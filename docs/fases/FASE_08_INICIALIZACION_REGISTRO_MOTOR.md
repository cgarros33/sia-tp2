# Fase 08 — Inicialización, registro y motor

> **Ola:** 4 · **Depende de:** 00, 01, 02, 03, 04, 05, 06, 07 · **Habilita:** 10

---

## 1. Objetivo

Al terminar esta fase el algoritmo genético funciona. Existe la generación cero,
existe la tabla que traduce los nombres de la configuración en los operadores que
corresponden, y existe el ciclo evolutivo que los encadena hasta que se cumple un
criterio de corte. Es la primera fase que necesita que todo lo anterior exista de
verdad y no solo su descripción.

---

## 2. Archivos que produce

| Archivo | Qué es |
|---|---|
| `src/inicializacion.py` | Construye la generación cero |
| `src/registro.py` | Traduce los nombres de la configuración en operadores |
| `src/motor.py` | El ciclo evolutivo |

---

## 3. Qué hay que implementar

### `src/registro.py`

Una tabla que asocia cada nombre válido de la configuración con el operador que
le corresponde. Existe para que el motor no tenga una cadena de condicionales por
cada familia de operadores, y para que agregar un método nuevo sea tocar un solo
archivo.

| Función | Recibe | Devuelve | Qué hace |
|---|---|---|---|
| `obtener_tipo_figura` | El nombre del tipo de gen | La clase de figura | Traduce el valor de `gene_type` |
| `obtener_seleccion` | El nombre del método | El operador de selección | Traduce el valor de `seleccion` |
| `obtener_cruza` | El nombre del método | El operador de cruza | Traduce el valor de `cruza` |
| `obtener_mutacion` | El nombre del método | El operador de mutación | Traduce el valor de `mutacion` |
| `obtener_supervivencia` | El nombre de la estrategia | La estrategia de supervivencia | Traduce el valor de `supervivencia` |

Los nombres válidos son exactamente los que valida la fase 00. Como la
configuración ya está validada cuando llega acá, un nombre desconocido significa
que la tabla y la validación se desincronizaron, y eso tiene que fallar con un
mensaje claro en vez de devolver nada.

**Invariante:** todo valor que la fase 00 acepta tiene una entrada acá. Si la
fase 12 quiere comparar los siete métodos de selección, tiene que poder pedir los
siete por nombre.

---

### `src/inicializacion.py`

| Función | Recibe | Devuelve | Qué hace |
|---|---|---|---|
| `crear_poblacion_inicial` | La configuración, el generador de azar, la imagen objetivo, el ancho, el alto y los recursos | La población de la generación cero | Construye los individuos del primer ciclo |

**Comportamiento:**

1. Construye tantos individuos como indique `population_size`.
2. Cada individuo se arma con tantas figuras como indique `gene_count`, todas del
   tipo que indique `gene_type`.
3. Cada figura se crea al azar dentro de su dominio válido, que es el mismo que
   usa el recorte de la mutación. Así la generación cero y cualquier individuo
   mutado viven en el mismo espacio de búsqueda.
4. Si `sesgo_color_inicial` está activo, después de crear cada figura se le
   cambia el color por el promedio de la zona de la imagen objetivo donde cae, y
   se conserva su transparencia.
5. Devuelve la población, con el número de generación en cero y sin evaluar.

**La variante con sesgo de color.** Cada figura nace con un color muestreado al
azar, lo que significa que la generación cero es ruido de colores arbitrarios
sobre el lienzo, y las primeras decenas de generaciones se gastan solo en
corregir colores. Tomar el color de la zona donde cae la figura ahorra esas
generaciones, a costa de reducir la variedad inicial: si todas las figuras nacen
con el color aproximadamente correcto, hay menos material distinto sobre el que
la evolución pueda trabajar. Está como bandera de configuración justamente para
poder medir las dos alternativas en la fase 12, no para elegir una de antemano.

Para determinar la zona se usa el centro de la figura y una ventana cuadrada
alrededor. El centro puede caer fuera del lienzo, porque las coordenadas admiten
un margen de desborde, así que hay que recortar la ventana a los límites de la
imagen antes de promediar.

**Invariantes:**
- La población devuelta tiene exactamente `population_size` individuos y cada uno
  exactamente `gene_count` genes.
- Todos los parámetros de todas las figuras están dentro de su dominio válido.
- Todos los sorteos derivan del generador que llega por parámetro.
- Ningún individuo comparte figuras con otro.

---

### `src/motor.py`

| Función | Recibe | Devuelve | Qué hace |
|---|---|---|---|
| `ejecutar` | La configuración, el generador de azar, la imagen objetivo, el ancho, el alto, los recursos y los destinos de salida | La metadata de la corrida | Corre el ciclo evolutivo hasta que se cumple un criterio de corte |

**El ciclo, paso a paso:**

1. Se resuelven los cuatro operadores contra el registro, una sola vez antes de
   empezar.
2. Se crea la generación cero y se la evalúa.
3. Se registran las métricas de la generación cero y se guarda el fenotipo de su
   mejor individuo.
4. En cada generación:
   - Se seleccionan `selected_count` padres de la población actual.
   - Se los mezcla al azar y se los agrupa de a pares.
   - Cada par se cruza y produce dos hijos.
   - Cada hijo se muta.
   - Se evalúan los hijos.
   - La estrategia de supervivencia arma la generación siguiente a partir de la
     población actual y de los hijos.
   - Se evalúa la nueva población, se registran sus métricas y se guarda el
     fenotipo de su mejor individuo.
   - Se evalúan los criterios de corte.
5. Al terminar, se compila el GIF, se guarda la imagen final, se guarda la
   enumeración de figuras del mejor individuo y se escribe el resumen de la
   corrida.

**Por qué se mezclan los padres antes de aparearlos.** La lista de seleccionados
puede venir ordenada por aptitud, sobre todo con élite y con ranking. Si se
aparean tal cual llegan, el mejor se cruza siempre con el segundo mejor y el peor
con el anteúltimo, lo que acelera la pérdida de variedad sin que nadie lo haya
pedido. Mezclar primero desacopla el apareamiento del orden en que la selección
devolvió los individuos.

**Criterios de corte.** Se evalúan los tres y alcanza con que se cumpla uno. La
metadata tiene que registrar cuál fue el que disparó, porque en el análisis
importa distinguir una corrida que alcanzó el objetivo de una que se quedó sin
generaciones o de una que se estancó.

| Criterio | Se cumple cuando |
|---|---|
| Contenido alcanzado | El mejor fitness llega a `fitness_cutoff` |
| Estancamiento | Pasan `stale_content_generation_cutoff` generaciones consecutivas sin que el mejor fitness histórico mejore |
| Generaciones agotadas | Se llega a `max_generations` |

El contador de estancamiento se compara contra el mejor fitness histórico de toda
la corrida, no contra el de la generación anterior. Con supervivencia exclusiva
el mejor de una generación puede ser peor que el de la anterior, y usar la
generación previa como referencia haría que el contador se reinicie con cualquier
oscilación.

**La metadata de la corrida** incluye el fitness final alcanzado, la cantidad de
generaciones corridas, el tiempo de ejecución, el motivo de finalización y la
configuración completa que se usó. Esto último es lo que hace que una corrida sea
reproducible después: sin la configuración guardada junto al resultado, un CSV
suelto no dice de dónde salió.

**Invariantes:**
- Toda la corrida usa un único generador de azar, creado a partir de
  `random_seed`. Dos corridas con la misma configuración dan resultados
  idénticos.
- El tamaño de la población es constante en todas las generaciones.
- Ningún individuo se evalúa dos veces sin haber cambiado.
- El motor no abre archivos de imagen ni escribe archivos directamente: lo
  primero es de la fase 02, lo segundo de la fase 09.

---

## 4. Interfaces de otras fases

**La configuración** llega ya validada por la fase 00, y con ella los cuatro
nombres de operadores y todos los hiperparámetros.

**Las figuras** de la fase 01 saben crearse al azar, dan su centro y saben
devolver una copia con otro color. La inicialización usa esos tres métodos y
nada más.

**El renderizador y la aptitud** de la fase 02 los usa el individuo, no el motor.
El motor solo pide evaluar la población.

**La población** de la fase 03 sabe evaluarse respetando el caché de cada
individuo, y expone su mejor individuo, sus tres métricas de aptitud y su
diversidad.

**Los operadores** de las fases 04 a 07 comparten cada uno su firma común, y el
motor los invoca sin saber cuál le tocó. La supervivencia recibe el operador de
selección como parámetro, así que el motor se lo pasa.

**El output** de la fase 09 recibe las métricas de cada generación, los fenotipos
de los mejores individuos y la metadata final. El motor lo llama pero no sabe qué
formato produce.

---

## 5. Decisiones ya tomadas

| Decisión | Motivo |
|---|---|
| Los operadores se resuelven una sola vez, antes del ciclo | Resolverlos en cada generación es buscar en una tabla cientos de veces para obtener siempre lo mismo |
| Los padres se mezclan antes de aparearse | Sin mezclar, con élite o ranking el apareamiento queda ordenado por aptitud y se pierde variedad más rápido de lo que ningún parámetro indica |
| El contador de estancamiento se compara contra el mejor histórico | Con supervivencia exclusiva el mejor puede empeorar de una generación a la otra, y comparar contra la anterior reiniciaría el contador ante cualquier oscilación |
| Los tres criterios de corte conviven y se registra cuál disparó | En el análisis no es lo mismo una corrida que alcanzó el objetivo que una que se estancó o que se quedó sin generaciones |
| La configuración completa se guarda junto con los resultados | Un CSV sin la configuración que lo produjo no sirve para comparar nada |
| El registro vive en un archivo aparte y no adentro del motor | Agregar un método de selección es tocar un archivo, no el ciclo evolutivo |
| La cantidad de hijos por generación es igual a `selected_count` | Cada par produce dos hijos, y por eso la fase 00 exige que ese valor sea par |

---

## 6. Decisiones abiertas

- **Cómo se define la zona para el sesgo de color.** Se propone una ventana
  cuadrada alrededor del centro de la figura, pero el tamaño de esa ventana queda
  a criterio de quien implementa. Muy chica y el color es el de un píxel, con
  todo el ruido que eso trae; muy grande y todas las figuras terminan con el
  color promedio de la imagen entera. La decisión tiene que quedar escrita en el
  resumen.
- **Qué significa "mejora" en el criterio de estancamiento.** Se implementa como
  mejora estricta: cualquier aumento del mejor fitness reinicia el contador. La
  alternativa es exigir una mejora mínima, para que mejoras insignificantes no
  mantengan viva una corrida estancada. Conviene medirlo en la fase 12 antes de
  cambiarlo, porque agregar un umbral suma un campo de configuración.
- **Paralelizar la evaluación de la población.** Cada individuo se evalúa
  independientemente. Antes de hacerlo hay que verificar que no rompa la
  reproducibilidad por semilla.

---

## 7. Checkpoints obligatorios

- `src/motor.py` — porque decide cuándo termina la corrida y en qué orden se
  aplican los operadores, que es el corazón del trabajo.
- `src/inicializacion.py` — por el muestreo de la generación cero y por el
  cálculo del color promedio de la zona en la variante con sesgo.

`src/registro.py` no lleva checkpoint: es una tabla de correspondencias.

---

## 8. Cómo se verifica

| # | Qué se prueba | Entrada | Resultado esperado |
|---|---|---|---|
| 1 | Tabla completa | Todos los nombres que acepta la fase 00 | Cada uno devuelve un operador |
| 2 | Nombre desconocido | Un nombre que no existe | Falla con un mensaje claro |
| 3 | Tamaño de la generación cero | Una configuración cualquiera | Tantos individuos como dice la configuración, cada uno con tantos genes como dice |
| 4 | Dominio de la generación cero | Diez mil figuras de la generación cero | Ningún parámetro fuera de su rango |
| 5 | Sesgo de color | Una imagen objetivo de un solo color, con el sesgo activo | Todas las figuras nacen aproximadamente de ese color |
| 6 | Sesgo desactivado | La misma imagen, con el sesgo apagado | Los colores están repartidos por todo el rango |
| 7 | Centro fuera del lienzo | Una figura cuyo centro cae en el margen de desborde | No falla, y el color sale de la parte de la ventana que sí está dentro de la imagen |
| 8 | Corrida corta | Una corrida de cinco generaciones con una población chica | Termina sin errores y devuelve metadata completa |
| 9 | Tamaño constante | Una corrida de veinte generaciones | Todas las generaciones tienen el mismo tamaño |
| 10 | Corte por generaciones | El máximo de generaciones en cinco | Termina en cinco y la metadata dice que fue por generaciones agotadas |
| 11 | Corte por contenido | El umbral de fitness en un valor muy bajo | Termina en la primera generación que lo supera y la metadata lo dice |
| 12 | Corte por estancamiento | El umbral de estancamiento en tres, sin mutación | Termina poco después de que el mejor deja de mejorar |
| 13 | Reproducibilidad | Dos corridas con la misma configuración y la misma semilla | Las métricas de todas las generaciones coinciden exactamente |
| 14 | Todas las combinaciones | Los siete métodos de selección por las dos estrategias de supervivencia, corridas de tres generaciones | Las catorce terminan sin errores |
| 15 | El caché sirve | Una corrida con supervivencia aditiva, contando renderizados | Bastante menos renderizados que individuos por generación |

---

## 9. Errores probables

- **Aparear los padres en el orden en que los devolvió la selección** → con élite
  o ranking el apareamiento queda ordenado por aptitud y la variedad cae mucho
  más rápido de lo que indican los parámetros → se detecta comparando la
  diversidad de una corrida con élite contra una con torneo.
- **Evaluar la población entera después de cada operador** → se renderiza varias
  veces por generación lo mismo → verificación 15.
- **No evaluar los hijos antes de la supervivencia** → la estrategia de
  supervivencia compara aptitudes inexistentes o vencidas → se detecta porque las
  métricas de la generación no cierran.
- **Comparar el estancamiento contra la generación anterior** → con supervivencia
  exclusiva el contador se reinicia con cualquier oscilación y la corrida no
  termina nunca → verificación 12.
- **Crear un generador de azar nuevo en algún punto del ciclo** → se rompe la
  reproducibilidad y las comparaciones de la fase 12 dejan de tener sentido →
  verificación 13.
- **Resolver los operadores dentro del ciclo** → cientos de búsquedas en una
  tabla para obtener siempre lo mismo.
- **No registrar el motivo de finalización** → al analizar los resultados no se
  distingue una corrida exitosa de una que se quedó sin generaciones →
  verificaciones 10, 11 y 12.
- **Que la ventana del sesgo de color se salga de la imagen** → se leen píxeles
  inexistentes o se da la vuelta al índice y el color sale del lado opuesto de la
  imagen → verificación 7.
- **Perder el mejor individuo** → con métodos de selección probabilísticos el
  mejor puede no ser elegido y desaparecer → se detecta mirando si el mejor
  fitness retrocede entre generaciones con supervivencia aditiva.

---

## 10. Cierre de la fase

- [ ] Todos los archivos de la sección 2 existen y se importan sin error
- [ ] Todas las verificaciones de la sección 8 pasan
- [ ] `docs/resumenes/FASE_08_RESUMEN.md` está escrito
- [ ] No se tocó ningún archivo fuera de la lista
- [ ] El agente no commiteó ni pusheó nada
