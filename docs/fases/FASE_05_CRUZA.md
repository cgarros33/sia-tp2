# Fase 05 — Cruza

> **Ola:** 3 · **Depende de:** 03 · **Habilita:** 08

---

## 1. Objetivo

Al terminar esta fase existen los cuatro métodos de cruza que pide la consigna,
todos intercambiables. Dados dos padres, cualquiera de ellos devuelve dos hijos
que combinan sus cromosomas preservando las posiciones. Es el operador que
recombina material genético existente, en contraposición a la mutación, que
introduce material nuevo.

---

## 2. Archivos que produce

| Archivo | Qué es |
|---|---|
| `src/cruza/__init__.py` | Vacío |
| `src/cruza/un_punto.py` | Un corte, se intercambian las colas |
| `src/cruza/dos_puntos.py` | Dos cortes, se intercambia el tramo del medio |
| `src/cruza/uniforme.py` | Se decide posición por posición |
| `src/cruza/anular.py` | El cromosoma se trata como un anillo |

---

## 3. Qué hay que implementar

### La firma común

| Recibe | Devuelve |
|---|---|
| Los dos padres y el generador de azar | Dos individuos nuevos |

**Invariantes que valen para los cuatro:**
- Los hijos tienen exactamente la misma cantidad de genes que los padres.
- El gen que estaba en una posición de un padre va a esa misma posición en el
  hijo. Nunca cambia de locus.
- Los padres no se modifican.
- Ningún hijo comparte una figura con un padre ni con el otro hijo: las figuras
  se copian siempre.
- Los hijos nacen sin aptitud vigente.
- Se usa únicamente el generador de azar que llega por parámetro.

Que el largo sea fijo y que las posiciones se preserven no es un detalle de
implementación: es lo que permite usar los cuatro operadores tal como se los vio
en clase, sin ninguna adaptación. Y preservar el locus es obligatorio porque en
este problema la posición determina el orden de dibujado, así que es información
genética en sí misma.

---

### `src/cruza/un_punto.py`

Se sortea una posición de corte. El primer hijo se arma con los genes del primer
padre hasta esa posición y los del segundo padre desde ahí en adelante. El
segundo hijo se arma al revés.

---

### `src/cruza/dos_puntos.py`

Se sortean dos posiciones de corte y se ordenan. El cromosoma queda partido en
tres tramos. Los hijos conservan el primero y el tercero de su propio padre e
intercambian el tramo del medio.

---

### `src/cruza/uniforme.py`

Para cada posición se sortea de forma independiente, con probabilidad un medio,
si los genes de esa posición se intercambian entre los dos hijos o se mantienen
como estaban.

Es el que más mezcla y el que menos respeta la contigüidad: un bloque de figuras
que juntas funcionaban bien tiene muy pocas chances de sobrevivir entero. En este
problema eso puede importar, porque figuras vecinas en el cromosoma se dibujan
una encima de otra y su efecto combinado depende de que estén juntas.

---

### `src/cruza/anular.py`

El cromosoma se trata como circular. Se sortea una posición de inicio y una
longitud de segmento. Desde esa posición se toma un tramo continuo de esa
longitud, dando la vuelta al final del cromosoma si hace falta, y ese tramo se
intercambia entre los dos hijos.

Es equivalente a la cruza de dos puntos salvo por un caso: cuando el segmento
cruza el final del cromosoma, el tramo intercambiado es el que la cruza de dos
puntos dejaría afuera. Eso le da a las posiciones de los extremos las mismas
chances de quedar en un tramo intercambiado que a las del medio, cosa que con la
cruza de dos puntos no pasa.

---

## 4. Interfaces de otras fases

**Los individuos** de la fase 03 exponen su lista de genes y saben copiarse. Los
métodos de cruza leen los genes de los dos padres, arman dos listas nuevas
copiando cada figura, y con eso construyen dos individuos.

**Las figuras** de la fase 01 saben copiarse en profundidad. La cruza nunca mira
adentro de una figura: no sabe cuántos parámetros tiene ni de qué tipo es. Solo
las mueve de una lista a otra.

**El generador de azar** llega por parámetro y es el único de la corrida.

---

## 5. Decisiones ya tomadas

| Decisión | Motivo |
|---|---|
| La cruza opera a nivel de figura, no de parámetro | Mezclar parámetros de figuras distintas produce figuras incoherentes, no recombinación útil: el hijo hereda tres vértices de un triángulo y el color de otro que estaba en otra parte de la imagen |
| Las figuras se copian siempre, nunca se comparten | Si el hijo comparte una figura con el padre, mutar al hijo muta al padre, y el caché de aptitud del padre queda mintiendo |
| Los cuatro devuelven dos hijos, no uno | Es lo que hace que la cantidad de hijos por generación sea igual a la cantidad de padres seleccionados, y por eso la fase 00 exige que esa cantidad sea par |
| Toda pareja seleccionada se cruza | No hay probabilidad de cruza configurable: la variedad que aportaría se consigue por la vía de la mutación, y agregar el parámetro sumaría un eje más a los experimentos de la fase 12 sin mucho a cambio |
| Los hijos nacen sin aptitud vigente | Tienen genes distintos a los de sus padres; heredar la aptitud del padre daría un número falso |

---

## 6. Decisiones abiertas

- **Rango de la longitud del segmento anular.** Puede ir de uno hasta el largo
  del cromosoma, o acotarse a la mitad para que el intercambio nunca sea tan
  grande que equivalga a intercambiar los individuos enteros. Queda a criterio de
  quien implementa, pero la decisión tiene que quedar escrita en el resumen
  porque cambia cuánto mezcla el operador.

---

## 7. Checkpoints obligatorios

- `src/cruza/anular.py` — porque hay que decidir de qué rango se sortea la
  longitud del segmento, y esa decisión determina cuánto material se intercambia.

Los otros tres no llevan checkpoint: sortean posiciones de corte y reordenan
listas, no ponderan ni puntúan nada.

---

## 8. Cómo se verifica

| # | Qué se prueba | Entrada | Resultado esperado |
|---|---|---|---|
| 1 | Largo preservado | Los cuatro métodos | Los dos hijos tienen la misma cantidad de genes que los padres |
| 2 | Padres intactos | Los cuatro métodos | Los genes de los padres no cambiaron |
| 3 | Sin figuras compartidas | Los cuatro métodos | Ninguna figura de un hijo es el mismo objeto que una de un padre o del otro hijo |
| 4 | Aislamiento real | Mutar un gen de un hijo | Ni los padres ni el otro hijo cambian |
| 5 | Conservación del material | Un punto, dos puntos y anular | Para cada posición, el par de genes de los dos hijos es el mismo par que tenían los padres en esa posición |
| 6 | Corte en el extremo | Un punto, con el corte en la primera y en la última posición | Los hijos son copias de los padres, o de los padres intercambiados, pero siguen siendo individuos válidos |
| 7 | Uniforme reparte | Muchas cruzas de dos padres bien distintos | Aproximadamente la mitad de las posiciones quedaron intercambiadas |
| 8 | Anular da la vuelta | Una posición de inicio cerca del final y una longitud que la excede | El segmento intercambiado incluye posiciones del principio del cromosoma |
| 9 | Aptitud invalidada | Los cuatro métodos | Pedirle la aptitud a un hijo dispara un cálculo nuevo |
| 10 | Reproducibilidad | El mismo método dos veces con la misma semilla | Los hijos son idénticos |

---

## 9. Errores probables

- **Copiar la lista de genes pero no las figuras** → padre e hijo comparten
  figuras y mutar a uno muta al otro. Es el error más silencioso de esta fase,
  porque todo parece funcionar hasta que las aptitudes empiezan a no tener
  sentido → verificaciones 3 y 4.
- **Reordenar los genes al armar el hijo** → una figura cambia de locus, cambia
  el orden de dibujado y el fenotipo no corresponde a lo que se recombinó → las
  posiciones se preservan siempre.
- **Sortear los dos puntos sin ordenarlos** → si el segundo es menor que el
  primero, el tramo del medio queda vacío o negativo → hay que ordenarlos.
- **Que el hijo herede la aptitud del padre** → arranca con un número que no
  corresponde a sus genes → verificación 9.
- **Perder material genético** → un gen queda en los dos hijos y otro en ninguno
  → verificación 5.
- **Que la cruza anular no dé la vuelta** → se convierte en una cruza de dos
  puntos con otro nombre y los experimentos de la fase 12 comparan lo mismo dos
  veces → verificación 8.
- **Devolver un solo hijo** → la cantidad de hijos por generación deja de ser la
  esperada y la supervivencia exclusiva reparte mal → los cuatro devuelven dos.

---

## 10. Cierre de la fase

- [ ] Todos los archivos de la sección 2 existen y se importan sin error
- [ ] Todas las verificaciones de la sección 8 pasan
- [ ] `docs/resumenes/FASE_05_RESUMEN.md` está escrito
- [ ] No se tocó ningún archivo fuera de la lista
- [ ] El agente no commiteó ni pusheó nada
