# Fase 03 — Individuo y Población

> **Ola:** 2 · **Depende de:** 01, 02 · **Habilita:** 04, 05, 06, 07, 08, 09

---

## 1. Objetivo

Al terminar esta fase existen las dos estructuras sobre las que trabaja todo el
motor: el individuo, que es un cromosoma de largo fijo con su aptitud cacheada, y
la población, que es una generación completa y sabe calcular sus propias
métricas. Es la fase que fija la interfaz contra la que van a programar las
cuatro familias de operadores de la ola 3.

---

## 2. Archivos que produce

| Archivo | Qué es |
|---|---|
| `src/individuo.py` | Cromosoma de largo fijo con caché de aptitud |
| `src/poblacion.py` | Conjunto de individuos de una generación, con sus métricas |

---

## 3. Qué hay que implementar

### `src/individuo.py`

Un individuo es una lista ordenada de figuras. El orden es información genética,
porque las figuras se dibujan una sobre otra y el resultado depende de la
secuencia. El largo es fijo durante toda la corrida: siempre `gene_count` genes.

| Función | Recibe | Devuelve | Qué hace |
|---|---|---|---|
| Constructor | La lista de figuras | — | Arma el individuo y lo marca como no evaluado |
| `genes` | — | La lista de figuras | Da acceso al cromosoma para los operadores |
| `obtener_fitness` | La imagen objetivo, el ancho, el alto, la configuración y los recursos | La aptitud | Devuelve la aptitud cacheada, o la calcula si no la tiene |
| `invalidar_cache` | — | Nada | Marca la aptitud como vencida |
| `copiar` | — | Un individuo nuevo | Copia profunda: genes nuevos e independientes |

**Comportamiento de `obtener_fitness`:**

Si el individuo tiene aptitud vigente, la devuelve sin hacer nada más. Si no,
renderiza sus genes, calcula la aptitud contra el objetivo, la guarda, la marca
como vigente y la devuelve.

El caché existe porque con supervivencia aditiva un mismo individuo sobrevive
muchas generaciones, y renderizar es la operación más cara del motor. Sin caché,
un individuo que sobrevive doscientas generaciones se renderiza doscientas veces
para dar siempre el mismo número.

**Comportamiento de `invalidar_cache`:**

Marca la aptitud como vencida. Lo llama todo lo que modifique los genes. El
riesgo que cubre es el peor de esta fase: si un individuo muta y nadie invalida
su caché, sigue reportando la aptitud de antes de mutar, la selección ordena la
población con números falsos y el algoritmo entero deja de funcionar sin dar
ningún error.

**Invariantes:**
- La cantidad de genes nunca cambia después de construido.
- La aptitud no se recalcula mientras esté vigente.
- Un individuo recién construido no tiene aptitud vigente.
- La copia no comparte ninguna figura con el original, y nace sin aptitud
  vigente.

---

### `src/poblacion.py`

Una población es el conjunto de individuos de una generación. Su tamaño es
constante durante toda la corrida, porque las dos estrategias de supervivencia
están definidas como transiciones entre poblaciones del mismo tamaño. A
diferencia del individuo, acá el orden no significa nada.

| Función | Recibe | Devuelve | Qué hace |
|---|---|---|---|
| Constructor | La lista de individuos, la imagen objetivo, el ancho, el alto, la configuración, los recursos y el número de generación | — | Arma la generación |
| `individuos` | — | La lista de individuos | Da acceso a la población para los operadores |
| `evaluar` | — | Nada | Calcula la aptitud de todos los individuos, respetando el caché de cada uno |
| `mejor_individuo` | — | Un individuo | El de mayor aptitud |
| `fitness_maximo`, `fitness_minimo`, `fitness_promedio` | — | Un número | Las tres métricas de aptitud de la generación |
| `diversidad` | — | Un número | Cuánta variedad genética queda en la población |

El promedio de aptitud no es opcional: la selección de Boltzmann lo necesita para
normalizar sus pesos.

**Comportamiento de `diversidad`:**

Mide qué tan parecidos son entre sí los individuos, mirando el genotipo y no el
fenotipo. Para cada locus del cromosoma y cada parámetro de la figura que ocupa
ese locus, se toma el valor que tiene en cada uno de los individuos de la
población y se calcula su desvío estándar. Ese desvío se divide por el ancho del
rango válido de ese parámetro. Después se promedian todos los valores
normalizados.

La normalización es imprescindible. Las coordenadas van de cero al ancho de la
imagen, la rotación va de cero a uno y los canales de color van de cero a
doscientos cincuenta y cinco. Sin dividir por el rango, el promedio quedaría
dominado por la geometría y la métrica no diría nada sobre el color.

El resultado tiende a cero cuando la población colapsó a un único genotipo. Sirve
para diagnosticar convergencia prematura: si la diversidad se derrumba mientras
la aptitud sigue mediocre, el problema es de presión de selección o de mutación,
no de cantidad de generaciones.

Los rangos válidos de cada parámetro los provee la figura. La población no sabe
qué tipo de figura contiene ni cuántos parámetros tiene: los pide y los promedia.

**Comportamiento de `evaluar`:**

Le pide la aptitud a cada individuo. Como cada uno respeta su propio caché, los
que no cambiaron desde la generación anterior no se vuelven a renderizar. Cada
individuo se evalúa de forma independiente, así que esta función es el punto
natural para paralelizar si más adelante hace falta.

**Invariantes:**
- El tamaño de la población es siempre `population_size`.
- Las métricas se calculan sobre aptitudes ya evaluadas. Pedir una métrica antes
  de evaluar es un error.
- Ninguna función de esta clase modifica los genes de sus individuos.

---

## 4. Interfaces de otras fases

**Las figuras** de la fase 01 exponen sus parámetros y los rangos válidos de cada
uno, en el mismo orden y con el mismo largo. La métrica de diversidad se apoya
exactamente en eso, y funciona igual para cualquiera de los cinco tipos sin
saber cuál es.

**El renderizador y la aptitud** de la fase 02: el individuo le pasa su lista de
figuras al renderizador junto con el ancho, el alto, la configuración y los
recursos, recibe el fenotipo, y se lo pasa al cálculo de aptitud junto con la
imagen objetivo. Recibe un número entre cero y uno, donde más alto es mejor. Esta
fase se puede escribir y probar contra esa descripción sin esperar a que la fase
02 esté terminada.

**La imagen objetivo, el ancho, el alto y los recursos** se cargan una sola vez
al arrancar la corrida y se pasan de mano en mano. Ni el individuo ni la
población los cargan.

---

## 5. Decisiones ya tomadas

| Decisión | Motivo |
|---|---|
| El individuo es una lista y no un conjunto | Las figuras translúcidas se dibujan una sobre otra, así que la posición de un gen es información genética en sí misma |
| El largo del cromosoma es fijo | Permite usar los cuatro operadores de cruza vistos en clase sin ninguna adaptación, porque todos intercambian información entre posiciones iguales |
| La aptitud se cachea con una marca de vencimiento | Con supervivencia aditiva un individuo sobrevive muchas generaciones, y renderizar es lo más caro del motor |
| El caché se invalida al mutar, no al copiar el individuo a otra generación | Sobrevivir no cambia los genes. Solo la mutación los cambia |
| La diversidad se mide sobre el genotipo y no sobre el fenotipo | Comparar las imágenes de todos contra todos es cuadrático en el tamaño de la población y cuesta un renderizado por comparación |
| El desvío se normaliza por el rango válido de cada parámetro | Sin normalizar, las coordenadas dominan numéricamente sobre el color y la rotación, y la métrica deja de reflejar la variedad real |
| La población pide los rangos a la figura en vez de conocerlos | Permite agregar tipos de figura sin tocar la población |

---

## 6. Decisiones abiertas

- **Paralelizar la evaluación.** Cada individuo se evalúa independientemente, así
  que la evaluación es paralelizable. No se implementa en esta fase: hay que
  medir primero cuánto se gana, y hay que verificar que no rompa la
  reproducibilidad por semilla. Queda como posible optimización de la fase 12.

---

## 7. Checkpoints obligatorios

- `src/poblacion.py` — porque la métrica de diversidad es una cuenta que agrega y
  compara valores de toda la población, y es uno de los números que se van a
  presentar y defender.

`src/individuo.py` no lleva checkpoint: administra un caché y delega el cálculo
en la fase 02, no calcula nada propio.

---

## 8. Cómo se verifica

| # | Qué se prueba | Entrada | Resultado esperado |
|---|---|---|---|
| 1 | El caché evita recalcular | Pedir la aptitud dos veces al mismo individuo, contando cuántas veces se renderiza | Se renderiza una sola vez |
| 2 | El caché se invalida | Pedir la aptitud, invalidar, volver a pedirla | Se renderiza de nuevo |
| 3 | El largo no cambia | Un individuo recién construido | Tiene exactamente `gene_count` genes |
| 4 | Independencia de la copia | Copiar un individuo y mutar un gen de la copia | El original no cambió |
| 5 | La copia nace sin aptitud vigente | Evaluar un individuo y después copiarlo | La copia recalcula al pedirle la aptitud |
| 6 | Diversidad nula | Una población de copias idénticas del mismo individuo | Diversidad exactamente cero |
| 7 | Diversidad positiva | Una población generada al azar | Un valor claramente mayor que cero |
| 8 | Diversidad ordenada | Una población al azar y otra donde todos los individuos se parecen mucho | La primera da un valor mayor que la segunda |
| 9 | Normalización | Dos poblaciones que difieren solo en color, una sobre una imagen chica y otra sobre una grande | Diversidades parecidas, porque la normalización cancela la escala |
| 10 | Coherencia de las métricas | Una población evaluada | El máximo es la aptitud del mejor individuo, y el promedio queda entre el mínimo y el máximo |
| 11 | Tamaño constante | La población en cualquier momento | Siempre `population_size` individuos |

---

## 9. Errores probables

- **No invalidar el caché al mutar** → el individuo reporta la aptitud que tenía
  antes de mutar, la selección ordena con números falsos y el motor deja de
  converger sin dar ningún error → verificación 2. Es el error más peligroso de
  esta fase, porque no se manifiesta como una excepción sino como un algoritmo
  que simplemente no mejora.
- **Copiar la lista de genes sin copiar las figuras** → padre e hijo comparten
  figuras, y mutar al hijo muta al padre → verificación 4.
- **Que la copia herede la aptitud vigente** → si después se muta, arrastra un
  número que ya no corresponde → verificación 5.
- **Calcular la diversidad sin normalizar por el rango** → las coordenadas, que
  van hasta el ancho de la imagen, tapan por completo al color y a la rotación →
  verificación 9.
- **Pedir métricas antes de evaluar** → se leen aptitudes inexistentes o
  vencidas → `evaluar` se llama siempre antes de consultar cualquier métrica.
- **Que la población conozca los parámetros de un tipo de figura concreto** →
  agregar un tipo nuevo obliga a tocar la población → los rangos y los
  parámetros se le piden a la figura.
- **Recalcular las métricas en cada consulta** → el motor las pide varias veces
  por generación y cada consulta recorre la población entera → conviene
  calcularlas una vez por generación.

---

## 10. Cierre de la fase

- [ ] Todos los archivos de la sección 2 existen y se importan sin error
- [ ] Todas las verificaciones de la sección 8 pasan
- [ ] `docs/resumenes/FASE_03_RESUMEN.md` está escrito
- [ ] No se tocó ningún archivo fuera de la lista
- [ ] El agente no commiteó ni pusheó nada
