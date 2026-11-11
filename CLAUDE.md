# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Proyecto

Proyecto 3 de AMIN (UCSC): compara AG, AM, ACS y EO (tau-EO) sobre el PFSP (minimizar makespan) con instancias de Taillard. Código y documentación en español. El README.md tiene el detalle de parámetros, formato CSV y decisiones de diseño.

## Comandos

```bash
pip install -r requirements.txt                 # numpy, matplotlib
python tests.py                                 # todas las pruebas (sin pytest)
python -c "import tests; tests.test_eo_reproducible_y_monotono()"   # una prueba
python main.py --semillas 1 --procesos 1        # batería corta (4 alg x 3 inst x 1 semilla)
python graficar.py resultados/experimentos.csv  # exige columna `evaluaciones`
sbatch slurm.sh                                 # batería completa (30 semillas) en el servidor
```

CLIs individuales (parámetros posicionales, orden fijo):

```bash
python ag.py  instancia semilla poblacion iteraciones pc pm salida.csv
python am.py  instancia semilla poblacion iteraciones pc pm frec_bl salida.csv
python acs.py instancia semilla hormigas iteraciones alfa beta q0 salida.csv
python eo.py  instancia semilla iteraciones tau salida.csv
```

No hay linter ni build. `main.py` debe lanzarse desde terminal (usa `ProcessPoolExecutor`; requiere el guard `__main__`).

## Arquitectura

- **Algoritmo = qué, `operadores.py` = cómo.** Cada `ag.py`/`acs.py`/`eo.py` contiene el bucle, la CLI y el CSV; todas las funciones puras (lectura, `makespan`, ocio, RPD, torneo, OX, mutación, búsqueda local, feromonas, `paso_eo`) viven en `operadores.py`. Mantener esta separación y la simplicidad (sin wrappers/abstracciones sobre stdlib/NumPy).
- **AM no tiene bucle propio:** `am.py` es solo CLI sobre `ejecutar_ag(..., frec_bl>0)`. `frec_bl=0` es el AG.
- Cada `ejecutar_*` devuelve `(mejor_secuencia, mejor_cmax, filas)`; `filas` son las filas del CSV por iteración (EO: cada 50 iteraciones + la última). `main.py` importa estas funciones, define la batería (constantes de parámetros arriba del archivo), las reparte en un pool y escribe `resultados/experimentos.csv` y `resultados/resumen.csv` (incluye filas de referencia SPT y azar).
- **Presupuesto común:** 50 × 200 = 10 000 evaluaciones; EO usa 10 000 iteraciones. La columna `evaluaciones` es el eje X de los gráficos (escala log), así que cualquier cambio en cómo un algoritmo cuenta evaluaciones afecta `graficar.py` y los tests. La población inicial del AG y el SPT de `tau0` no se cuentan.
- **Reproducibilidad:** cada corrida usa su propio `random.Random(semilla)`; mismos parámetros -> misma secuencia y makespan (el tiempo varía).
- Instancias en `datos/` (formato Taillard: `n m semilla UB LB` + m filas de n tiempos; `p` queda como matriz trabajos × máquinas).
- `tests.py` importa `acs, ag, eo, graficar, main, operadores`; es un script de funciones `test_*` ejecutadas en orden, no pytest.
- `preproyecto_berlin52/` (ACS sobre TSP) está borrado en el working tree pero aún tracked en git.
- `local/`, `.claude/`, `.serena/` y `*.pdf` están en `.gitignore`. `local/` tiene enunciado, `RULES.md`, `plan.md` y notas.

## Flujo de trabajo (de `local/RULES.md`)

- KISS estricto: 1–2 archivos nucleares, sin abstracciones vacías.
- Pasos incrementales: implementar un paso, verificarlo (tests/consola), **recomendar** el comando y mensaje de commit (Conventional Commits: `feat:`, `fix:`, `test:`, `docs:`, `chore:`), resumir el siguiente paso y esperar confirmación. **Nunca ejecutar `git commit` ni `git push`** sin que el usuario lo pida.
- Mantener `local/plan.md` (rúbrica -> estado) al día.
