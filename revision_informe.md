Input:
"Revisa el informe (artículo científico). No debe referenciar al informe o texto anterior, se asume que este artículo es el único, ya que los anteriores no están publicados, y este es candidato a publicación. Debes ser meticuloso, como revisor académico. Busca qué partes podrían fallar, como que usen términos desconocidos, sin explicar; difícil de entender, demasiado complejas; incompletas o que omitan cosas.

No hagas cambios, solo diagnostica"

Output:
"El artículo todavía no se sostiene como publicación autónoma. La comparación está contada con cuidado, pero el texto sigue apoyado en documentos del curso, y el resultado principal —el algoritmo memético con el menor desvío en las tres instancias— queda sin la referencia clásica del problema y con un presupuesto que no es el de los otros tres métodos.

## 1. No se puede leer sin el curso

Estas frases remiten a textos que un lector externo no puede abrir:

- El encabezado de página dice «Informe de investigación».
- La introducción cita el informe previo del algoritmo genético con siembra NEH y el preproyecto de colonia de hormigas sobre Berlin52. En la bibliografía figuran como «Informe de curso» y «Preproyecto de curso».
- El sistema de colonia de hormigas se presenta como «el esquema usado en Berlin52».
- El reemplazo generacional se justifica porque «el enunciado pide» eso, frente al reemplazo \((\mu+\lambda)\) «del informe anterior».
- \(f_{BL}=10\) y \(\tau=1.4\) se atribuyen «al ejemplo de la sección 5 del enunciado». La misma frase está en el título de la tabla de parámetros.
- \(p_c\), \(p_m\), el presupuesto y el cambio de \(\alpha\) y \(\beta\) salen de «el ejemplo de ejecución» y de «el ejemplo del ACS».
- Las corridas están hechas «en el servidor Jupyter del curso».
- La comprobación de \(C_{\max}=1286\) en ta001 se hace contra «la implementación del informe anterior», sin decir cuál es la secuencia.
- Los resultados comparan con RPD medios de 0,61 %, 3,24 % y 1,23 % de ese informe, «con otra población y otra cantidad de generaciones», sin dar esos tamaños.

El párrafo que distingue «semilla» de «sembrar» existe para deshacer una confusión creada por ese informe anterior. La justificación de \(\alpha=0{,}1\) sí se sostiene sola: con \(\alpha=1\) cada actualización sustituye la feromona. Queda metida dentro de la frase del enunciado. \(q_0=0{,}9\) también se sostiene, porque además está en Dorigo y Gambardella.

## 2. Lo que un revisor rechazaría aunque se borren esas citas

**NEH se explica y no se ejecuta.** La introducción la presenta como la referencia clásica del flow shop. Las líneas de base que sí aparecen son SPT y 1 000 permutaciones al azar, ambas muy por encima de cualquier método del estudio. Con el mismo cálculo de \(C_{\max}\) del artículo, NEH obtiene:

| Instancia | NEH | RPD contra la UB del artículo | Media del AM |
|---|---:|---:|---:|
| ta001 | 1286 | 0,63 % | 1,38 % |
| ta041 | 3135 | 3,64 % | 3,57 % |
| ta071 | 5846 | 1,32 % | 1,38 % |

En ta071, 5846 coincide con el NEH publicado para esa instancia. En promedio, NEH queda por debajo de los cuatro métodos en ta001 y prácticamente empatado con el memético en las otras dos. El mejor memético sí lo supera (1278, 3070 y 5811). El resumen, que declara al memético con el menor desvío medio en todas las instancias, solo es cierto dentro de los cuatro métodos aleatorios. El 1286 de la comprobación con el informe anterior es, además, el makespan de NEH en ta001; la secuencia sigue sin identificarse.

**La cota de ta041 está vieja.** El artículo usa la cabecera de los archivos: 1278, 3025 y 5770, y dice que solo ta001 coincide con el óptimo. La tabla de mejores cotas del propio Taillard, con fecha 3 de junio de 2026, escribe un solo número cuando la cota inferior y la superior coinciden: ta041 queda en 2991 y ta071 en 5770. El 3025 de la cabecera está 34 unidades por encima de ese valor. El RPD medio del memético en ta041 pasa de 3,57 % a 4,75 % si el denominador es 2991; el mejor valor, 3070, pasa de 1,49 % a 2,64 %. El orden entre los cuatro métodos no cambia, porque en una misma instancia el denominador es común. Cambia el significado del porcentaje que abre el resumen. El artículo cita a Brunner y a Gmys justamente para decir que hay cotas posteriores mejores, y no da la cota vigente de las dos instancias en las que eso importa.

**El presupuesto común de la introducción es el presupuesto base.** En \(100\times10\), una pasada de búsqueda local cuesta \(n^2+1=10\,001\) evaluaciones: más que las 10 000 de todo el genético, la colonia o la optimización extremal. Esa pasada ocurre en la generación 10, cuando el genético lleva 500 evaluaciones. El memético entra en 10 501 y después hace otras 19 pasadas. El total, 210 020, es 21 veces el presupuesto base. En \(20\times5\) el total es 1,8 veces; en \(50\times10\), 6 veces. La ventaja media del memético sobre el genético crece en el mismo sentido: 0,17, 2,19 y 3,45 puntos de RPD. La conclusión dice que no se puede separar el mecanismo del costo, y eso está bien dicho. Falta la cuenta que hace visible el problema: la ventaja más grande aparece donde una sola pasada ya agota el presupuesto de los demás. El tramo con el mismo presupuesto sí se puede leer. En ta041 y ta071, el peor RPD del genético queda por debajo del mejor de la colonia y de la optimización extremal.

**La literatura del flow shop se cita y no se usa.** Reeves, Stützle y Rajendran aparecen en la introducción. El experimento no dice en qué se diferencia esta colonia de esas colonias para el flow shop, ni qué haría un genético publicado en estas tres instancias. El método de hormigas queda anclado al preproyecto de Berlin52. Iterated greedy, la referencia habitual junto a NEH, no aparece.

**Tres instancias, la primera de cada tamaño.** El título habla del permutation flow shop. Taillard publica diez instancias por grupo. Con ta001, ta041 y ta071 se puede concluir sobre esas tres, que es lo que hace la sección final, y no sobre el problema.

**\(\beta\) se eligió en ta001.** El texto lo declara: cinco semillas, y esa instancia después entra en los resultados. No dice cuáles semillas. \(\alpha\) se cambió por una razón analítica; \(\beta\) es el único parámetro ajustado con datos del experimento. En la corrida completa el RPD medio de la colonia en ta001 es 3,28 %, peor que el 2,90 % del ensayo.

## 3. Contradicción, términos opacos y pasos que no se pueden rehacer

**La feromona local se explica de dos maneras.** En el marco teórico, cada arista recorrida «pierde parte de su feromona» para que las hormigas siguientes prueben otras. En la metodología, la actualización es una combinación con \(\tau_0\): baja si el valor era mayor, queda igual si era \(\tau_0\) y sube si era menor. Al empezar, toda la matriz vale \(\tau_0\), así que la actualización local no hace nada hasta que el refuerzo global separe algunos valores. El párrafo de la metodología es el claro. El del marco teórico cuenta el mecanismo contrario.

**\(\alpha\) no es el \(\alpha\) del artículo citado.** En Dorigo y Gambardella el exponente de la feromona es \(\alpha\) y la evaporación es \(\rho\). Aquí \(\alpha\) es el coeficiente de las dos actualizaciones, y en la regla de transición la feromona entra con exponente 1, sin decirlo. Quien abra la cita no encuentra la fórmula del artículo.

**La búsqueda local admite dos algoritmos con el mismo costo.** «Prueba cada trabajo en todas las posiciones y lo deja en la mejor» puede ser una pasada secuencial, en la que cada trabajo se reubica y el siguiente ve la secuencia ya cambiada, o un único movimiento: se evalúan las \(n^2\) inserciones y se aplica solo la mejor. Las dos cuestan \(n^2+1\) evaluaciones y dan resultados distintos. Tampoco se dice el orden en que se recorren los trabajos.

**Otros huecos para repetir el experimento.** El cruce OX no dice de dónde salen los dos cortes. El torneo de 3 no dice si el sorteo es con reposición ni si los dos padres pueden ser el mismo individuo. La mutación no fija la distribución de la posición de destino. SPT desempatan, según el texto, con un «argsort estable»: es una función de NumPy, no una regla. El generador es «una semilla»; el de la línea de base sí se nombra, `Random(0)`, y el de los algoritmos no. Los tiempos van al centésimo de segundo y no hay modelo de CPU, versión de Python ni forma de obtener el código. `ProcessPoolExecutor` y Slurm no aportan eso.

**La optimización extremal es el tramo más difícil, y el menos justificado.** Bak y Sneppen entran con especies, equilibrio puntuado y estado crítico; nada de eso vuelve a usarse. «Mal ubicado» se define mucho después como el ocio de la posición. La fórmula es correcta para la espera de las máquinas 2 a \(m\), y el ejemplo \((3,0,0)\) también lo es, pero está en el párrafo de pruebas, separado de la ecuación y sin la aritmética. Falta decir por qué la máquina 1 no entra: con los trabajos disponibles en el instante 0, esa máquina no espera. También falta el otro lado del \(\max\): si el trabajo espera a la máquina, ese término vale 0, así que una posición bloqueada puede parecer buena. La regla \(\tau\approx 1+1/\ln n\) está bien calculada (1,33, 1,26 y 1,22), y no se dice que subir \(\tau\) concentra la probabilidad en la peor posición. Con \(\tau=1{,}4\) el método es más ávido que esa regla, sobre todo en \(n=100\). En el pseudocódigo, \(\pi^{*}\) se copia sin inicializar su \(C_{\max}\), y el movimiento de la última iteración queda fuera del archivo porque la comparación ocurre antes de mover.

**Términos que el lector tiene que adivinar.** «Segmento» y «vértice» aparecen en el pseudocódigo de la colonia; el texto decía «arista» y el grafo no se define. «Randómicamente» y «es encontrada una mejor solución» no son formulaciones reconocibles; «for un tamaño predeterminado de población» obliga a traducir el pseudocódigo desde el párrafo anterior. «Presión selectiva» se nombra y no se usa. «Certificado», en «no es un certificado», pide la palabra optimalidad. «Escala log» no dice que el logaritmo es el del eje de evaluaciones; el de \(C_{\max}\) es lineal. En las cajas, el texto define el rango intercuartil y los puntos, y omite la línea de la mediana y los bigotes. Esos bigotes, en el gráfico, llegan a 1,5 veces el rango intercuartil, así que no son el mínimo y el máximo; los extremos están en los puntos. Solo el primer gráfico de convergencia dice que la línea horizontal es la cota. Los otros cinco también la tienen y el pie no lo dice. «Hallazgo» está definido, y su nota se queda corta: en el memético el contador salta \(n^2+1\) de una fila a la siguiente, así que en \(100\times10\) el instante registrado puede adelantarse hasta una pasada entera, unas 10 000 evaluaciones.

**El resumen en inglés.** *Above* en «the ACS and the EO stay above the AG» se puede leer como mejor calidad o como una curva más alta. En el cuerpo, más alto es peor. El resumen tampoco dice que la cota de referencia puede no ser el óptimo.

## 4. Lo que ya funciona

La definición de \(C_{\max}\), el RPD, el torneo, OX, el elitismo, la visibilidad SPT y la combinación de la feromona están escritos para quien no vio el curso. El caso de tres trabajos y dos máquinas cierra: \((0,1,2)\) da 10 y ocios \((3,0,0)\); \((1,0,2)\) da 8. Las 18 020, 60 020 y 210 020 evaluaciones coinciden con \(10\,000+20(n^2+1)\). La sección de resultados separa lo observado de la lectura, y usa el cruce de mínimos y máximos donde una prueba estadística habría hecho ese trabajo. El solapamiento de ta001 y ta041, y la separación completa en ta071, están bien contados."

Notas (mías):
Opino que falta justificar algunas cosas. Por ejemplo en los algoritmos, podrían justificarse las decisiones. Así como "por qué de esta forma y no otra".

Revisa @local/Analisis_correcciones_Metaheuristicos.pdf, que contiene el feedback del último informe, ya que varias de estas cosas ya estaban ahí especificadas. Es muy importante aplicar la retroalimentación que se nos entregó con tal de generar un mejor artículo.