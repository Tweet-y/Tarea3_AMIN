"""Extremal Optimization (tau-EO) para PFSP.

Uso: python eo.py instancia semilla iteraciones tau salida.csv
"""

import argparse
import os
from random import Random
from time import process_time

import operadores as op


def ejecutar_eo(p, ub, instancia, semilla, iteraciones, tau, mostrar_progreso=False):
    """Ejecuta tau-EO y devuelve (mejor_secuencia, mejor_cmax, filas).

    Cada iteracion evalua el estado actual (1 makespan) y lo reemplaza sin condicion.
    # ponytail: una fila cada 50 iteraciones, la misma granularidad que una generacion de AG.
    """
    inicio = process_time()
    rng = Random(semilla)
    parametros = f"tau={tau}"
    acum = op.pesos_potencia(len(p), tau)
    secuencia = rng.sample(range(len(p)), len(p))
    mejor_sec, mejor_cmax = None, float("inf")
    filas = []

    for iteracion in range(1, iteraciones + 1):
        cmax, ocio = op.ocio_por_posicion(secuencia, p)
        if cmax < mejor_cmax:
            mejor_sec, mejor_cmax = list(secuencia), cmax
        secuencia = op.paso_eo(secuencia, ocio, acum, rng)
        if mostrar_progreso and iteracion % max(1, iteraciones // 10) == 0:
            print(f"  Iteracion {iteracion:>5}/{iteraciones}  mejor Cmax = {mejor_cmax}")
        if iteracion % 50 == 0 or iteracion == iteraciones:
            tiempo = process_time() - inicio
            filas.append(["EO", instancia, semilla, parametros, iteracion, mejor_cmax,
                          round(op.rpd(mejor_cmax, ub), 4), round(tiempo, 4), iteracion,
                          "-".join(map(str, mejor_sec))])

    return mejor_sec, mejor_cmax, filas


def main():
    parser = argparse.ArgumentParser(description="Extremal Optimization para PFSP")
    parser.add_argument("instancia")
    parser.add_argument("semilla", type=int)
    parser.add_argument("iteraciones", type=int)
    parser.add_argument("tau", type=float, help="exponente de la ley de potencia, > 0")
    parser.add_argument("salida", metavar="salida.csv")
    args = parser.parse_args()

    if not os.path.isfile(args.instancia):
        parser.error(f"no existe el archivo de instancia '{args.instancia}'")
    if args.iteraciones < 1:
        parser.error("iteraciones debe ser un entero mayor que cero")
    if args.tau <= 0:
        parser.error("tau debe ser mayor que cero")
    try:
        p, ub = op.leer_instancia(args.instancia)
    except ValueError as error:
        parser.error(str(error))

    print(f"EO | {args.instancia} | {p.shape[0]} trabajos x {p.shape[1]} maquinas | UB = {ub}")
    print(f"Parametros: semilla={args.semilla} iteraciones={args.iteraciones} tau={args.tau}")
    secuencia, cmax, filas = ejecutar_eo(
        p, ub, args.instancia, args.semilla, args.iteraciones, args.tau, mostrar_progreso=True,
    )
    op.guardar_csv(args.salida, filas)

    print(f"Mejor secuencia: {secuencia}")
    print(f"Makespan: {cmax} | RPD: {op.rpd(cmax, ub):.2f} % | Tiempo: {filas[-1][7]:.2f} s")
    print(f"Resultados guardados en {args.salida}")


if __name__ == "__main__":
    main()
