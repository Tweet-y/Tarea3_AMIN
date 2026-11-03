"""Bateria comparativa: AG, AM, ACS y EO.

Uso: python main.py [--procesos N] [--semillas N]
Escribe resultados/experimentos.csv (trayectorias, en el orden de las tareas) y
resultados/resumen.csv (una fila por instancia y algoritmo, mas SPT y azar).
"""

import argparse
import csv
import os
from concurrent.futures import ProcessPoolExecutor
from random import Random
from statistics import mean, median, stdev

import numpy as np

import operadores as op
from acs import ejecutar_acs
from ag import ejecutar_ag
from eo import ejecutar_eo

INSTANCIAS = ("datos/tai20_5.txt", "datos/tai50_10.txt", "datos/tai100_10.txt")
ORDEN = ("AG", "AM", "ACS", "EO")

# Mismo presupuesto base: 50 x 200 = 10 000 evaluaciones. EO usa 10 000 iteraciones.
TAMANO, ITERACIONES = 50, 200
ITERACIONES_EO, TAU = 10000, 1.4
PC, PM, FREC_BL = 0.8, 0.1, 10
# beta = 1.0 y no 2.0 (ejemplo del enunciado): en tai20_5 con 5 semillas el RPD medio fue
# 3.19 % (beta=0), 2.90 % (beta=1), 3.35 % (beta=2) y 5.60 % (beta=5).
# alfa = 0.1: con alfa = 1.0 cada actualizacion borraria toda la feromona acumulada.
ALFA, BETA, Q0 = 0.1, 1.0, 0.9

CABECERA_RESUMEN = ["instancia", "algoritmo", "ub", "mejor_cmax", "media_cmax", "desv_cmax",
                    "media_rpd", "mediana_rpd", "min_rpd", "max_rpd", "n_ub", "evaluaciones",
                    "media_eval_hallazgo", "media_tiempo", "nota"]


def cpus_asignadas():
    """CPUs de este proceso. sched_getaffinity respeta la asignacion de Slurm."""
    if hasattr(os, "sched_getaffinity"):
        return len(os.sched_getaffinity(0))
    return os.cpu_count()


def construir_tareas(n_semillas):
    """Instancia, algoritmo y semilla, en el orden en que se escribe el CSV."""
    return [(algoritmo, instancia, semilla)
            for instancia in INSTANCIAS
            for algoritmo in ORDEN
            for semilla in range(1, n_semillas + 1)]


def correr(tarea):
    """Una corrida independiente. La semilla vive dentro del proceso."""
    algoritmo, instancia, semilla = tarea
    p, ub = op.leer_instancia(instancia)
    if algoritmo == "AG":
        return ejecutar_ag(p, ub, instancia, semilla, TAMANO, ITERACIONES, PC, PM)
    if algoritmo == "AM":
        return ejecutar_ag(p, ub, instancia, semilla, TAMANO, ITERACIONES, PC, PM, FREC_BL)
    if algoritmo == "ACS":
        return ejecutar_acs(p, ub, instancia, semilla, TAMANO, ITERACIONES, ALFA, BETA, Q0)
    if algoritmo == "EO":
        return ejecutar_eo(p, ub, instancia, semilla, ITERACIONES_EO, TAU)
    raise ValueError(f"algoritmo desconocido: {algoritmo}")


def _desvio(valores):
    return round(stdev(valores), 1) if len(valores) > 1 else 0


def resumir(instancia, algoritmo, ub, corridas):
    """Agrega las corridas de una instancia y un algoritmo."""
    finales = [filas[-1] for filas in corridas]
    cmaxs = [fila[5] for fila in finales]
    rpds = [fila[6] for fila in finales]

    def hallazgo(filas):
        final = filas[-1][5]
        return next(fila[8] for fila in filas if fila[5] == final)

    return [instancia, algoritmo, ub, min(cmaxs), round(mean(cmaxs), 1), _desvio(cmaxs),
            round(mean(rpds), 2), round(median(rpds), 2), round(min(rpds), 2), round(max(rpds), 2),
            sum(cmax <= ub for cmax in cmaxs), finales[0][8],
            round(mean(hallazgo(filas) for filas in corridas), 1),
            round(mean(fila[7] for fila in finales), 2), ""]


def filas_referencia(p, ub, instancia):
    """SPT y la media de 1000 permutaciones con Random(0). No dependen de la semilla del algoritmo."""
    spt = list(np.argsort(p.sum(axis=1), kind="stable"))
    cmax_spt = int(op.makespan(spt, p))
    rpd_spt = round(op.rpd(cmax_spt, ub), 2)
    fila_spt = [instancia, "SPT", ub, cmax_spt, cmax_spt, 0, rpd_spt, rpd_spt, rpd_spt, rpd_spt,
                int(cmax_spt <= ub), 1, 1, "",
                "permutacion SPT, argsort estable de la suma de tiempos"]

    rng = Random(0)
    n = len(p)
    cmaxs = [op.makespan(rng.sample(range(n), n), p) for _ in range(1000)]
    rpds = [op.rpd(cmax, ub) for cmax in cmaxs]
    fila_azar = [instancia, "aleatoria", ub, min(cmaxs), round(mean(cmaxs), 1), _desvio(cmaxs),
                 round(mean(rpds), 2), round(median(rpds), 2), round(min(rpds), 2), round(max(rpds), 2),
                 sum(cmax <= ub for cmax in cmaxs), 1000, "", "",
                 "media de 1000 permutaciones con Random(0)"]
    return [fila_spt, fila_azar]


def main(argv=None):
    parser = argparse.ArgumentParser(description="Experimentos AG, AM, ACS y EO para PFSP")
    parser.add_argument("--procesos", type=int, default=cpus_asignadas(),
                        help="procesos del pool; por defecto las CPUs asignadas")
    parser.add_argument("--semillas", type=int, default=30, help="semillas 1..N")
    args = parser.parse_args(argv)
    if args.procesos < 1 or args.semillas < 1:
        parser.error("procesos y semillas deben ser enteros mayores que cero")

    tareas = construir_tareas(args.semillas)
    datos = {instancia: op.leer_instancia(instancia) for instancia in INSTANCIAS}
    with ProcessPoolExecutor(max_workers=args.procesos) as ex:
        corridas = list(ex.map(correr, tareas))

    filas, resumen = [], []
    cursor = 0
    for instancia in INSTANCIAS:
        p, ub = datos[instancia]
        for algoritmo in ORDEN:
            grupo = [corrida[2] for corrida in corridas[cursor:cursor + args.semillas]]
            cursor += args.semillas
            for semilla, filas_corrida in zip(range(1, args.semillas + 1), grupo):
                print(f"{instancia:<22} {algoritmo:<4} semilla={semilla:<3} "
                      f"Cmax={filas_corrida[-1][5]:<6} tiempo={filas_corrida[-1][7]:.1f} s",
                      flush=True)
                filas += filas_corrida
            resumen.append(resumir(instancia, algoritmo, ub, grupo))
        resumen.extend(filas_referencia(p, ub, instancia))

    op.guardar_csv("resultados/experimentos.csv", filas)
    with open("resultados/resumen.csv", "w", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f)
        escritor.writerow(CABECERA_RESUMEN)
        escritor.writerows(resumen)

    print(f"\n{'instancia':<22} {'alg':<9} {'UB':>6} {'mejor':>6} {'media':>8} {'desv':>6} "
          f"{'RPD':>7} {'med':>7} {'min':>7} {'max':>7} {'nUB':>4} {'evals':>8} "
          f"{'hallazgo':>9} {'CPU':>7}")
    for fila in resumen:
        cpu = f"{fila[13]:>7}" if fila[13] != "" else f"{'':>7}"
        print(f"{fila[0]:<22} {fila[1]:<9} {fila[2]:>6} {fila[3]:>6} {fila[4]:>8} {fila[5]:>6} "
              f"{fila[6]:>7} {fila[7]:>7} {fila[8]:>7} {fila[9]:>7} {fila[10]:>4} {fila[11]:>8} "
              f"{str(fila[12]):>9} {cpu}")
    print(f"\n{len(tareas)} corridas. Resultados en resultados/experimentos.csv y resultados/resumen.csv")


if __name__ == "__main__":
    main()
