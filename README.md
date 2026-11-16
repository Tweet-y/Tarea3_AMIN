# Proyecto 3: PFSP con AG, AM, ACS y EO

Algoritmos Metaheurísticos Inspirados en la Naturaleza (AMIN), UCSC.

Comparación de cuatro metaheurísticas sobre el *Permutation Flow Shop Scheduling Problem*
(PFSP), minimizando el makespan $C_{max}$ en instancias de Taillard:

- **AG**: Algoritmo Genético.
- **AM**: Algoritmo Memético (AG + búsqueda local por inserción).
- **ACS**: Ant Colony System.
- **EO**: Extremal Optimization con selección $\tau$ (tau-EO).

## Requisitos

Python 3.10 o superior, con numpy y matplotlib (este último solo para `graficar.py`).

```bash
pip install -r requirements.txt
```

## Estructura

```
ag.py            AG: bucle del algoritmo y CLI (con frec_bl > 0 es el AM)
am.py            AM: CLI que reutiliza ag.py con búsqueda local
acs.py           ACS: bucle del algoritmo y CLI
eo.py            tau-EO: bucle del algoritmo y CLI
main.py          Batería: 4 algoritmos x 3 instancias x N semillas, en paralelo
operadores.py    Lectura, Cmax, ocio, RPD, CSV y operadores
tests.py         Pruebas de operadores, AG, AM, ACS, EO, resumen y gráficos
graficar.py      Convergencia (evaluaciones, escala log) y boxplots
slurm.sh         Job opcional de Slurm para la batería completa
requirements.txt Dependencias: numpy y matplotlib
datos/           Instancias de Taillard: tai20_5, tai50_10, tai100_10
resultados/      CSV de corridas y resumen
graficos/        Convergencia y dispersión por instancia (PNG)
```

Los scripts de cada algoritmo describen **qué** hace. `operadores.py` describe **cómo**.

## Uso

Cada algoritmo recibe sus parámetros en orden fijo:

```bash
python ag.py  instancia semilla poblacion iteraciones pc pm salida.csv
python am.py  instancia semilla poblacion iteraciones pc pm frec_bl salida.csv
python acs.py instancia semilla hormigas iteraciones alfa beta q0 salida.csv
python eo.py  instancia semilla iteraciones tau salida.csv
```

Ejemplos con los parámetros de la batería:

```bash
python ag.py  datos/tai20_5.txt 12345 50 200 0.8 0.1 resultados/res_ag.csv
python am.py  datos/tai20_5.txt 12345 50 200 0.8 0.1 10 resultados/res_am.csv
python acs.py datos/tai20_5.txt 12345 50 200 0.1 1.0 0.9 resultados/res_acs.csv
python eo.py  datos/tai20_5.txt 12345 10000 1.4 resultados/res_eo.csv
```

| Parámetro | Significado | Rango |
| :--- | :--- | :--- |
| `instancia` | Archivo Taillard: `n m semilla UB LB` y luego m filas de n tiempos | archivo existente |
| `semilla` | Semilla del generador aleatorio | entero |
| `poblacion` / `hormigas` | Individuos por generación / hormigas por iteración | ≥ 1 |
| `iteraciones` | Generaciones (AG, AM), ciclos de la colonia (ACS) o pasos de EO | ≥ 1 |
| `pc`, `pm` | Probabilidad de cruce y de mutación | [0, 1] |
| `frec_bl` | Búsqueda local sobre el mejor individuo cada `frec_bl` generaciones | ≥ 1 |
| `alfa` | Evaporación de feromona, en la actualización local y en la global | (0, 1] |
| `beta` | Peso de la visibilidad η | ≥ 0 |
| `q0` | Probabilidad de explotación en la regla de transición | [0, 1] |
| `tau` | Exponente de $P(k) \propto k^{-\tau}$. k = 1 es la posición de mayor ocio | > 0 |

Cada ejecución muestra el progreso cada 10 % de las iteraciones y al final la mejor
secuencia, el makespan, el RPD y el tiempo de CPU. Si un parámetro no es válido, el
script termina con un mensaje que indica cuál y por qué.

**Reproducibilidad:** cada ejecución usa su propio `random.Random(semilla)`. Con la
misma instancia, semilla y parámetros se obtienen el mismo makespan y la misma
secuencia final. El tiempo puede variar.

### Formato del CSV de salida

AG, AM y ACS escriben una fila por iteración. EO escribe una cada 50 iteraciones
(200 filas en una corrida de 10 000) y también la última si el total no es múltiplo de 50.

| Columna | Contenido |
| :--- | :--- |
| `algoritmo` | AG, AM, ACS o EO |
| `instancia`, `semilla`, `parametros` | Configuración de la corrida |
| `iteracion` | Generación, ciclo o iteración de EO en la que se registró la fila |
| `mejor_cmax` | Mejor makespan encontrado hasta esa fila |
| `rpd` | $100 \cdot (C_{max} - UB) / UB$. UB es la mejor cota publicada (`COTAS` en `operadores.py`: 1278, 2991 y 5770), no la cabecera del archivo de tai50_10 (3025) |
| `tiempo` | Segundos de CPU (`time.process_time`) desde el inicio |
| `evaluaciones` | Makespans acumulados. AG: 50 por generación. AM: eso más $n^2+1$ por búsqueda local. ACS: una por hormiga. EO: una por iteración |
| `mejor_secuencia` | Trabajos separados por `-`, numerados desde 0 |

La población inicial del AG y el makespan SPT que fija $\tau_0$ no entran en `evaluaciones`.
Así 50 × 200 y las 10 000 iteraciones de EO cuentan el mismo presupuesto base.

## Pruebas, batería y gráficos

```bash
python tests.py
python main.py --semillas 1 --procesos 1
python graficar.py resultados/experimentos.csv
```

`python main.py --semillas 1` es una prueba corta: 4 algoritmos × 3 instancias × 1 semilla.
Reemplaza `resultados/experimentos.csv` y `resultados/resumen.csv`. La corrida completa
es la de `slurm.sh` (30 semillas, 360 corridas).

- `main.py --semillas N` usa las semillas 1 a N (por defecto 30) y un
  `ProcessPoolExecutor`. `--procesos` vale, por defecto, las CPUs asignadas al proceso
  (`sched_getaffinity` si existe; si no, `os.cpu_count()`).
- `resultados/resumen.csv` trae, por instancia y algoritmo, mejor $C_{max}$, media,
  desviación, RPD medio, mediano, mínimo y máximo, corridas que alcanzan la UB,
  evaluaciones, evaluación media del hallazgo y CPU media. Agrega una fila SPT
  (argsort estable de la suma de tiempos) y una fila aleatoria (media de 1000
  permutaciones con `Random(0)`).
- `graficar.py` crea dos figuras por instancia y exige la columna `evaluaciones`:
  - `graficos/convergencia_<instancia>.png`: media del mejor $C_{max}$ contra evaluaciones, en escala log.
  - `graficos/dispersion_<instancia>.png`: boxplot del $C_{max}$ final, con una caja por algoritmo.

  Con un CSV de una sola corrida sobrescribe las figuras de esa instancia.
  El `experimentos.csv` anterior al Proyecto 3 no tiene `evaluaciones` y no se puede graficar.

Hay que lanzar `main.py` desde la terminal (`python main.py` o `!python main.py` en una
celda). No como código dentro del notebook: el pool necesita funciones importables y el
guard `if __name__ == "__main__"`.

## Servidor (Jupyter con Slurm)

En una terminal del servidor, antes de la corrida:

```bash
echo $SLURM_JOB_ID $SLURM_CPUS_PER_TASK
nproc
which sbatch
python -c "import numpy, matplotlib"
```

Los perfiles del Jupyter (Básico, Estándar, Intensivo y Debug) asignan las CPUs de la
sesión. `os.cpu_count()` ve el nodo entero; `main.py` usa las CPUs asignadas para no
crear más procesos que CPUs.

- **Debug** (1 CPU): `python main.py --semillas 1 --procesos 1`.
- **Estándar** (8 CPUs): `sbatch slurm.sh`, o `python main.py` en la terminal de esa sesión.
- **Básico** (2 CPUs): la misma batería, con el valor por defecto de `--procesos`.

`slurm.sh` pide 8 CPUs, 1 hora y 8 GB, y ejecuta `python main.py --procesos $SLURM_CPUS_PER_TASK`.
En esta Mac no hay `sbatch`; el script solo se envía en el servidor.

## Diseño de los algoritmos

Presupuesto base: 50 individuos u hormigas × 200 iteraciones = 10 000 evaluaciones.
EO usa 10 000 iteraciones, con $\tau = 1.4$. AG/AM: pc = 0.8, pm = 0.1, frec_bl = 10.
ACS: $\alpha$ = 0.1, $\beta$ = 1.0, q0 = 0.9.

**AG:**
- Población aleatoria de permutaciones.
- Selección por torneo de tamaño 3.
- Cruce OX: un tramo de padre1 conserva su lugar y el resto se completa en el orden de padre2.
- Mutación por inserción.
- Reemplazo generacional con elitismo: el mejor histórico reemplaza al peor hijo.

**AM:** el mismo AG. Cada `frec_bl` generaciones, después del elitismo, aplica al mejor
individuo una pasada secuencial de inserción. Los trabajos se recorren en el orden de
la secuencia de entrada. Cada uno se prueba en todas las posiciones de la secuencia ya
modificada por los anteriores y se deja en la de menor $C_{max}$ solo si ese valor baja.

**ACS:**
- **Grafo:** trabajo → trabajo. $\tau_{ij}$ es la deseabilidad de programar $j$
  inmediatamente después de $i$. Es dirigida: $\tau_{ij} \neq \tau_{ji}$.
- **Visibilidad SPT:** $\eta_j = 1 / \sum_k p_{j,k}$. Prefiere los trabajos de menor
  tiempo total.
- **Feromona inicial:** $\tau_0 = 1 / (n \cdot C_{max}^{SPT})$.
- **Construcción:** cada hormiga parte en un trabajo al azar.
  - Con probabilidad $q_0$ elige el máximo $\tau_{ij}\,\eta_j^{\beta}$.
  - Si no, sortea con probabilidad proporcional a ese valor (ruleta).
- **Actualización local**, en cada arista recorrida: $\tau_{ij} \leftarrow (1-\alpha)\tau_{ij} + \alpha\tau_0$.
- **Actualización global**, solo en las aristas de la mejor secuencia global:
  $\tau_{ij} \leftarrow (1-\alpha)\tau_{ij} + \alpha / C_{max}^{mejor}$.

**EO:**
- Estado inicial: una permutación aleatoria.
- El fitness de la posición $i$ es el ocio que induce,
  $o_i = \sum_{j=2}^{m} \max(0,\, C(i,j-1) - C(i-1,j))$, calculado en la misma pasada que $C_{max}$.
- Se ordenan las posiciones de mayor a menor ocio. El rango k = 1 es el peor. Los empates se rompen al azar.
- Se elige una posición con $P(k) \propto k^{-\tau}$ y ese trabajo se inserta en otra posición.
- El nuevo estado se acepta siempre. Se guardan $\pi^*$ y $C_{max}^*$.

**Por qué estas opciones:**
- **Torneo k=3, no ruleta:** la ruleta exige transformar el Cmax, y como los Cmax de una
  población son muy parecidos, las probabilidades quedan casi uniformes. El torneo solo
  compara. k=3 da una presión moderada.
- **OX, no PMX:** el Cmax depende del orden relativo de los trabajos, y OX lo conserva.
- **Inserción, no intercambio:** mueve un solo trabajo y es el vecindario estándar del PFSP.
  La búsqueda local del AM y el paso de EO usan el mismo vecindario.
- **BL una pasada, solo al mejor:** cada pasada cuesta $n^2+1$ evaluaciones; aplicarla a toda
  la población multiplicaría ese costo por 50.
- **Elitismo de 1:** es lo mínimo para que el mejor Cmax del AG nunca empeore.
- **SPT, no NEH reducida:** con NEH no se distinguiría su aporte del de la colonia.
- **Refuerzo con la mejor global:** es la forma original del ACS (Dorigo y Gambardella, 1997).
- **$\tau = 1.4$:** un solo exponente para las tres instancias. $1 + 1/\ln n$ da cerca de
  1.33, 1.26 y 1.22 para $n = 20$, 50 y 100; 1.4 es más ávido. No se barrió $\tau$.

## Resultados

Cifras de `resultados/resumen.csv`: 30 semillas, cuatro algoritmos, cotas 1278, 2991 y 5770.
El RPD de tai50_10 usa 2991, no el 3025 de la cabecera del archivo.

| Instancia | Alg | Mejor | Media ± desv | RPD medio | Tiempo medio |
| :--- | :---: | ---: | ---: | ---: | ---: |
| tai20_5 (1278) | AG | 1297 | 1297.8 ± 4.6 | 1.55 % | 1.16 s |
| | AM | 1278 | 1295.7 ± 6.2 | 1.38 % | 1.82 s |
| | ACS | 1297 | 1320.0 ± 12.5 | 3.28 % | 9.00 s |
| | EO | 1303 | 1324.1 ± 10.9 | 3.60 % | 1.67 s |
| tai50_10 (2991) | AG | 3122 | 3199.1 ± 28.5 | 6.96 % | 3.92 s |
| | AM | 3070 | 3133.1 ± 27.2 | 4.75 % | 21.18 s |
| | ACS | 3362 | 3453.0 ± 35.2 | 15.45 % | 27.70 s |
| | EO | 3378 | 3445.2 ± 33.7 | 15.19 % | 7.52 s |
| tai100_10 (5770) | AG | 5967 | 6048.9 ± 53.2 | 4.83 % | 8.01 s |
| | AM | 5811 | 5849.8 ± 28.4 | 1.38 % | 147.58 s |
| | ACS | 6277 | 6337.7 ± 29.5 | 9.84 % | 60.07 s |
| | EO | 6339 | 6418.3 ± 43.8 | 11.24 % | 13.89 s |

- Entre los cuatro métodos, el AM tiene el menor RPD medio en las tres instancias. En
  tai20_5 iguala 1278 en 2 de 30 semillas. También es el que más evalúa: en tai100_10
  hace 210 020 evaluaciones y tarda 147.58 s; el AG hace 10 000 y tarda 8.01 s. Una pasada
  de búsqueda local en ese tamaño cuesta 10 001 evaluaciones, más que el presupuesto base.
  La mejor calidad y el costo extra se observan juntos; no se separó cuánto viene de cada uno.
- ACS y EO, con las mismas 10 000 evaluaciones que el AG, quedan por encima en RPD.
  SPT queda en 15.18 %, 26.41 % y 18.25 %, cerca de la media de 1 000 permutaciones
  al azar (18.64 %, 28.26 % y 20.00 %).

**Parámetros.** El presupuesto 50×200, pc = 0.8, pm = 0.1, frec_bl = 10, q0 = 0.9 y
α = 0.1 se fijaron a priori y no se calibraron de forma sistemática. q0 = 0.9 es también
el valor de Dorigo y Gambardella. pc = 0.8 deja la mayor parte de los hijos al cruce;
pm = 0.1 mueve cerca de un hijo de cada diez. Con α = 1 cada actualización reemplazaría
la feromona de la arista.

β = 1.0 se eligió en tai20_5 con cinco semillas; el listado no quedó archivado. El RPD
medio de ese ensayo fue:

| β | 0 | 1 | 2 | 5 |
| :--- | :---: | :---: | :---: | :---: |
| RPD medio | 3.19 % | 2.90 % | 3.35 % | 5.60 % |

En las 30 semillas el ACS de tai20_5 queda en 3.28 %, peor que el 2.90 % del ensayo.
Elegir β en una instancia que después se reporta favorece levemente al ACS en 20×5.
