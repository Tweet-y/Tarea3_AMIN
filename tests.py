"""Pruebas de los operadores PFSP. Ejecutar con: python tests.py."""

import os
import tempfile
from random import Random
from statistics import mean, median, stdev

import numpy as np

import acs
import ag
import eo
import graficar
import main
import operadores as op


def test_leer_instancia():
    for nombre, n, m, ub in [("tai20_5", 20, 5, 1278), ("tai50_10", 50, 10, 3025),
                             ("tai100_10", 100, 10, 5770)]:
        p, cota = op.leer_instancia(f"datos/{nombre}.txt")
        assert p.shape == (n, m)
        assert cota == ub

    # Filas del archivo = maquinas; filas de p = trabajos.
    p, _ = op.leer_instancia("datos/tai20_5.txt")
    assert p[0, 0] == 54 and p[1, 0] == 83 and p[0, 1] == 79


def test_leer_instancia_invalida():
    with tempfile.NamedTemporaryFile("w", suffix=".txt") as f:
        f.write("3 2 0 10 5\n1 2 3\n")  # Falta la fila de la segunda maquina.
        f.flush()
        try:
            op.leer_instancia(f.name)
        except ValueError:
            return
    raise AssertionError("una instancia incompleta debe lanzar ValueError")


def test_makespan_a_mano():
    p = np.array([[3, 2], [1, 4], [2, 1]])  # 3 trabajos x 2 maquinas.
    # M1: 3, 4, 6.  M2: 3+2=5, max(5,4)+4=9, max(9,6)+1=10.
    assert op.makespan([0, 1, 2], p) == 10
    # M1: 1, 4, 6.  M2: 1+4=5, max(5,4)+2=7, max(7,6)+1=8.
    assert op.makespan([1, 0, 2], p) == 8
    assert op.makespan([2], p) == 3


def test_makespan_taillard():
    p, _ = op.leer_instancia("datos/tai20_5.txt")
    # Secuencia y Cmax obtenidos con la implementacion independiente de la Tarea 1.
    secuencia = [2, 16, 8, 7, 14, 13, 10, 15, 12, 18, 5, 3, 4, 17, 0, 1, 9, 6, 19, 11]
    assert op.makespan(secuencia, p) == 1286

    # Cotas triviales: ninguna maquina ni trabajo termina antes de su carga total.
    cmax = op.makespan(list(range(20)), p)
    assert cmax >= p.sum(axis=0).max()
    assert cmax >= p.sum(axis=1).max()


def test_rpd():
    assert op.rpd(1278, 1278) == 0
    assert np.isclose(op.rpd(1286, 1278), 0.62597809)


P_CHICA = np.array([[3, 2], [1, 4], [2, 1]])  # Totales 5, 5, 3.


def test_visibilidad_spt():
    assert np.allclose(op.visibilidad_spt(P_CHICA), [1 / 5, 1 / 5, 1 / 3])


def test_inicializar_feromonas():
    tau, tau0 = op.inicializar_feromonas(P_CHICA)
    # SPT = [2, 0, 1]. M1: 2, 5, 6.  M2: 3, max(3,5)+2=7, max(7,6)+4=11.
    assert op.makespan([2, 0, 1], P_CHICA) == 11
    assert np.isclose(tau0, 1 / (3 * 11))
    assert tau.shape == (3, 3) and np.allclose(tau, tau0)


def test_siguiente_trabajo_explotacion():
    tau = np.ones((4, 4))
    eta = np.ones(4)
    tau[0, 1], eta[1] = 4, 0.5
    tau[0, 3] = 1000  # Trabajo ya programado: no es candidato.
    # beta=1: pesos 2 (trabajo 1) y 1 (trabajo 2). beta=3: pesos 0.5 y 1.
    assert op.siguiente_trabajo(0, [1, 2], tau, eta, 1, 1, Random(0)) == 1
    assert op.siguiente_trabajo(0, [1, 2], tau, eta, 3, 1, Random(0)) == 2
    assert op.siguiente_trabajo(0, [2], tau, eta, 2, 0, Random(0)) == 2


def test_siguiente_trabajo_exploracion():
    tau = np.ones((3, 3))
    tau[0, 2] = 3
    rng = Random(0)
    # Pesos 1 y 3: la ruleta debe elegir el trabajo 2 cerca del 75 % de las veces.
    elegidos = [op.siguiente_trabajo(0, [1, 2], tau, np.ones(3), 2, 0, rng) for _ in range(4000)]
    assert set(elegidos) == {1, 2}
    assert abs(elegidos.count(2) / 4000 - 0.75) < 0.03


def test_actualizar_local():
    tau = np.full((3, 3), 2.0)
    op.actualizar_local(tau, 0, 1, alfa=0.25, tau0=0.5)
    assert tau[0, 1] == 0.75 * 2 + 0.25 * 0.5  # 1.625
    assert tau[1, 0] == 2  # Dirigida: 1 tras 0 no es lo mismo que 0 tras 1.
    assert (tau == 2).sum() == 8


def test_actualizar_global():
    tau = np.full((4, 4), 2.0)
    op.actualizar_global(tau, [2, 0, 3, 1], cmax=10, alfa=0.25)
    reforzadas = [(2, 0), (0, 3), (3, 1)]
    for i, j in reforzadas:
        assert np.isclose(tau[i, j], 0.75 * 2 + 0.25 / 10)  # 1.525
    assert tau[1, 2] == 2  # Sin arista de cierre: la secuencia no es un ciclo.
    assert (tau == 2).sum() == 16 - len(reforzadas)


def test_construir_secuencia():
    p, _ = op.leer_instancia("datos/tai20_5.txt")
    eta = op.visibilidad_spt(p)
    tau, tau0 = op.inicializar_feromonas(p)
    tau *= 2  # Asi la actualizacion local se nota: cada arista recorrida baja hacia tau0.
    secuencia = op.construir_secuencia(tau, eta, 2, 0.9, 0.1, tau0, Random(1))
    assert sorted(secuencia) == list(range(20))
    recorridas = list(zip(secuencia, secuencia[1:]))
    for i, j in recorridas:
        assert np.isclose(tau[i, j], 0.9 * 2 * tau0 + 0.1 * tau0)
    assert np.isclose(tau, 2 * tau0).sum() == 400 - len(recorridas)


def test_acs_reproducible_y_monotono():
    p, ub = op.leer_instancia("datos/tai20_5.txt")
    corrida1 = acs.ejecutar_acs(p, ub, "tai20_5", 7, 5, 15, 0.1, 2, 0.9)
    corrida2 = acs.ejecutar_acs(p, ub, "tai20_5", 7, 5, 15, 0.1, 2, 0.9)
    sec, cmax, filas = corrida1
    assert sec == corrida2[0] and cmax == corrida2[1]
    assert sorted(sec) == list(range(20)) and op.makespan(sec, p) == cmax
    historial = [fila[5] for fila in filas]
    assert len(filas) == 15 and historial[-1] == cmax
    assert all(a >= b for a, b in zip(historial, historial[1:]))  # Nunca empeora.


def test_poblacion_inicial():
    poblacion = op.poblacion_inicial(30, 8, Random(0))
    assert len(poblacion) == 30
    assert all(sorted(s) == list(range(8)) for s in poblacion)
    assert len({tuple(s) for s in poblacion}) > 1


def test_torneo():
    poblacion, cmax = [[0], [1], [2]], [30, 10, 20]
    rng = Random(0)
    ganadores = [op.torneo(poblacion, cmax, rng)[0] for _ in range(3000)]
    # k=3 con reposicion: P(mejor) = 1 - (2/3)^3 = 0.704; P(peor) = (1/3)^3 = 0.037.
    assert abs(ganadores.count(1) / 3000 - 0.704) < 0.03
    assert abs(ganadores.count(0) / 3000 - 0.037) < 0.015


def test_cruce_ox():
    padre1, padre2 = [0, 1, 2, 3, 4, 5, 6, 7], [7, 5, 3, 1, 6, 4, 2, 0]
    rng = Random(0)
    for _ in range(200):
        hijo = op.cruce_ox(padre1, padre2, rng)
        assert sorted(hijo) == list(range(8))
        # Debe existir un tramo copiado de padre1 en su lugar; el resto sigue el orden de padre2.
        assert any(hijo[a:b] == padre1[a:b]
                   and hijo[:a] + hijo[b:] == [t for t in padre2 if t not in padre1[a:b]]
                   for a in range(8) for b in range(a + 1, 9))
    assert op.cruce_ox(padre1, padre1, rng) == padre1


def test_mutacion_insercion():
    original = list(range(10))
    rng = Random(0)
    for _ in range(200):
        mutada = op.mutacion_insercion(original, rng)
        assert sorted(mutada) == original and mutada != original
        # Quitar el trabajo movido deja el resto en el mismo orden.
        assert any([t for t in mutada if t != x] == [t for t in original if t != x]
                   for x in original)
    assert original == list(range(10))  # No modifica la entrada.


def test_ag_reproducible_y_elitista():
    p, ub = op.leer_instancia("datos/tai20_5.txt")
    sec, cmax, filas = ag.ejecutar_ag(p, ub, "tai20_5", 7, 20, 30, 0.8, 0.1)
    sec2, cmax2, _ = ag.ejecutar_ag(p, ub, "tai20_5", 7, 20, 30, 0.8, 0.1)
    assert sec == sec2 and cmax == cmax2
    assert sorted(sec) == list(range(20)) and op.makespan(sec, p) == cmax
    historial = [fila[5] for fila in filas]
    assert len(filas) == 30 and historial[-1] == cmax
    assert all(a >= b for a, b in zip(historial, historial[1:]))  # Elitismo: nunca empeora.


def test_busqueda_local_insercion():
    # Con P_CHICA la secuencia [0, 1, 2] (Cmax 10) mejora moviendo el trabajo 0 al medio:
    # [1, 0, 2] da 8, el optimo de esta instancia.
    assert op.busqueda_local_insercion([0, 1, 2], P_CHICA) == ([1, 0, 2], 8)
    assert op.busqueda_local_insercion([1, 0, 2], P_CHICA) == ([1, 0, 2], 8)  # Ya optima.

    p, _ = op.leer_instancia("datos/tai20_5.txt")
    rng = Random(0)
    for _ in range(5):
        inicial = rng.sample(range(20), 20)
        mejorada, cmax = op.busqueda_local_insercion(inicial, p)
        assert sorted(mejorada) == list(range(20))
        assert cmax == op.makespan(mejorada, p) < op.makespan(inicial, p)


def test_evaluaciones_y_tiempo_cpu():
    """AG: tam evaluaciones por generacion. AM suma n^2+1 por busqueda local.
    ACS: una evaluacion por hormiga. El reloj es time.process_time (CPU)."""
    col_eval = op.CABECERA_CSV.index("evaluaciones")
    col_tiempo = op.CABECERA_CSV.index("tiempo")
    n = len(P_CHICA)
    costo_bl = n * n + 1

    _, _, ag_filas = ag.ejecutar_ag(P_CHICA, 8, "toy", 1, 4, 3, 0.8, 0.1)
    assert [fila[col_eval] for fila in ag_filas] == [4, 8, 12]

    _, _, am_filas = ag.ejecutar_ag(P_CHICA, 8, "toy", 1, 4, 3, 0.8, 0.1, frec_bl=2)
    assert [fila[col_eval] for fila in am_filas] == [4, 8 + costo_bl, 12 + costo_bl]

    _, _, acs_filas = acs.ejecutar_acs(P_CHICA, 8, "toy", 1, 3, 2, 0.1, 1.0, 0.9)
    assert [fila[col_eval] for fila in acs_filas] == [3, 6]

    marcas = iter([100.0, 100.25, 100.5])
    reloj = ag.process_time
    ag.process_time = lambda: next(marcas)
    try:
        _, _, filas = ag.ejecutar_ag(P_CHICA, 8, "toy", 1, 2, 2, 1.0, 0.0)
    finally:
        ag.process_time = reloj
    assert [fila[col_tiempo] for fila in filas] == [0.25, 0.5]


def test_am_reproducible_y_mejora():
    p, ub = op.leer_instancia("datos/tai20_5.txt")
    sec, cmax, filas = ag.ejecutar_ag(p, ub, "tai20_5", 7, 20, 30, 0.8, 0.1, frec_bl=5)
    sec2, cmax2, _ = ag.ejecutar_ag(p, ub, "tai20_5", 7, 20, 30, 0.8, 0.1, frec_bl=5)
    assert sec == sec2 and cmax == cmax2
    assert sorted(sec) == list(range(20)) and op.makespan(sec, p) == cmax
    assert filas[0][0] == "AM" and "frec_bl=5" in filas[0][3]
    historial = [fila[5] for fila in filas]
    assert all(a >= b for a, b in zip(historial, historial[1:]))


def test_ocio_por_posicion():
    # 3x2. Secuencia [0, 1, 2]:
    # pos0: M1=2, ocio=max(0,2-0)=2, M2=3.
    # pos1: M1=12, ocio=max(0,12-3)=9, M2=13.
    # pos2: M1=13, ocio=max(0,13-13)=0, M2=16.
    p = np.array([[2, 1], [10, 1], [1, 3]])
    cmax, ocio = op.ocio_por_posicion([0, 1, 2], p)
    assert cmax == 16 and ocio == [2, 9, 0]
    assert cmax == op.makespan([0, 1, 2], p)

    # 3x3, para que el ocio sume mas de una maquina.
    # pos0: ocios 1+3. pos1: 2+0. pos2: 0+4. Cmax=12.
    p3 = np.array([[1, 2, 3], [4, 1, 1], [1, 5, 1]])
    cmax3, ocio3 = op.ocio_por_posicion([0, 1, 2], p3)
    assert cmax3 == 12 and ocio3 == [4, 2, 4]
    assert cmax3 == op.makespan([0, 1, 2], p3)


def test_pesos_potencia():
    # k^{-1} para k=1,2,3: 1, 1/2, 1/3.
    assert np.allclose(op.pesos_potencia(3, 1), [1, 1.5, 1.5 + 1 / 3])


def test_paso_eo_es_permutacion():
    secuencia = [0, 1, 2, 3]
    ocio = [1, 5, 0, 5]
    acum = op.pesos_potencia(4, 1.4)
    rng = Random(0)
    for _ in range(30):
        nueva = op.paso_eo(secuencia, ocio, acum, rng)
        assert sorted(nueva) == secuencia and nueva != secuencia


def test_eo_reproducible_y_monotono():
    p, ub = op.leer_instancia("datos/tai20_5.txt")
    sec, cmax, filas = eo.ejecutar_eo(p, ub, "tai20_5", 7, 100, 1.4)
    sec2, cmax2, filas2 = eo.ejecutar_eo(p, ub, "tai20_5", 7, 100, 1.4)
    assert sec == sec2 and cmax == cmax2
    assert [fila[9] for fila in filas] == [fila[9] for fila in filas2]
    assert sorted(sec) == list(range(20)) and op.makespan(sec, p) == cmax
    assert [fila[0] for fila in filas] == ["EO", "EO"]
    assert [fila[4] for fila in filas] == [50, 100]
    assert [fila[8] for fila in filas] == [50, 100]
    assert "tau=1.4" in filas[0][3]
    historial = [fila[5] for fila in filas]
    assert historial[-1] == cmax
    assert all(a >= b for a, b in zip(historial, historial[1:]))


def _campo(fila, nombre):
    return fila[main.CABECERA_RESUMEN.index(nombre)]


def test_tareas_incluyen_eo():
    tareas = main.construir_tareas(2)
    assert len(tareas) == 4 * 3 * 2
    assert tareas[0] == ("AG", "datos/tai20_5.txt", 1)
    assert {alg for alg, _, _ in tareas} == {"AG", "AM", "ACS", "EO"}
    assert {semilla for _, _, semilla in tareas} == {1, 2}


def test_referencias_spt_y_azar():
    filas = main.filas_referencia(P_CHICA, 8, "toy")
    assert [_campo(f, "algoritmo") for f in filas] == ["SPT", "aleatoria"]
    spt = list(np.argsort(P_CHICA.sum(axis=1), kind="stable"))
    assert _campo(filas[0], "mejor_cmax") == op.makespan(spt, P_CHICA)
    assert _campo(filas[0], "evaluaciones") == 1
    assert "argsort" in _campo(filas[0], "nota")
    rng = Random(0)
    muestra = [op.makespan(rng.sample(range(3), 3), P_CHICA) for _ in range(1000)]
    assert _campo(filas[1], "media_cmax") == round(mean(muestra), 1)
    assert _campo(filas[1], "evaluaciones") == 1000
    assert "Random(0)" in _campo(filas[1], "nota")


def test_resumen_de_corridas():
    filas1 = [
        ["AG", "toy", 1, "p", 1, 12, 50.0, 0.1, 50, "a"],
        ["AG", "toy", 1, "p", 2, 10, 25.0, 0.2, 100, "b"],
    ]
    filas2 = [
        ["AG", "toy", 2, "p", 1, 9, 12.5, 0.3, 50, "c"],
        ["AG", "toy", 2, "p", 2, 8, 0.0, 0.4, 100, "d"],
    ]
    fila = main.resumir("toy", "AG", 8, [filas1, filas2])
    assert _campo(fila, "mejor_cmax") == 8
    assert _campo(fila, "media_cmax") == 9
    assert _campo(fila, "desv_cmax") == round(stdev([10, 8]), 1)
    assert _campo(fila, "media_rpd") == 12.5
    assert _campo(fila, "mediana_rpd") == round(median([25.0, 0.0]), 2)
    assert _campo(fila, "min_rpd") == 0 and _campo(fila, "max_rpd") == 25
    assert _campo(fila, "n_ub") == 1
    assert _campo(fila, "evaluaciones") == 100
    assert _campo(fila, "media_eval_hallazgo") == 100
    assert _campo(fila, "media_tiempo") == 0.3


def test_graficos_evaluaciones_log_y_eo():
    assert set(graficar.ESTILOS) == {"AG", "AM", "ACS", "EO"}
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as f:
        f.write("algoritmo,instancia,semilla,parametros,iteracion,mejor_cmax,rpd,"
                "tiempo,evaluaciones,mejor_secuencia\n")
        f.write("AG,datos/tai20_5.txt,1,p,1,10,0,0.1,50,0\n")
        f.write("EO,datos/tai20_5.txt,1,p,50,12,0,0.1,50,0\n")
        ruta = f.name
    curvas = graficar.leer_curvas(ruta)
    os.unlink(ruta)
    assert list(curvas["datos/tai20_5.txt"]["AG"]) == [50]
    assert list(curvas["datos/tai20_5.txt"]["EO"]) == [50]

    capturado = {}

    def savefig(self, *args, **kwargs):
        ax = self.axes[0]
        if ax.get_xscale() == "log":
            capturado["xscale"] = ax.get_xscale()
            capturado["xlabel"] = ax.get_xlabel()
            capturado["labels"] = [linea.get_label() for linea in ax.get_lines()]
        capturado["xticks"] = [tick.get_text() for tick in ax.get_xticklabels()]

    original = graficar.plt.Figure.savefig
    graficar.plt.Figure.savefig = savefig
    try:
        graficar.graficar_instancia(
            "datos/tai20_5.txt",
            {"AG": {50: [10], 500: [9]}, "EO": {50: [12], 500: [8]}},
            8, "salida.png")
        graficar.graficar_dispersion(
            "datos/tai20_5.txt",
            {algoritmo: {50: [10, 11], 100: [9, 10]} for algoritmo in ("AG", "AM", "ACS", "EO")},
            8, "salida.png")
    finally:
        graficar.plt.Figure.savefig = original
    assert capturado["xscale"] == "log"
    assert capturado["xlabel"] == "Evaluaciones"
    assert "EO" in capturado["labels"]
    assert capturado["xticks"] == ["AG", "AM", "ACS", "EO"]


if __name__ == "__main__":
    pruebas = [f for nombre, f in list(globals().items()) if nombre.startswith("test_")]
    for prueba in pruebas:
        prueba()
    print(f"Todas las pruebas pasaron correctamente ({len(pruebas)}/{len(pruebas)}).")
