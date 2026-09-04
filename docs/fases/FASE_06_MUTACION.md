# Fase 06 — Mutación

> **Ola:** 3 · **Depende de:** 01, 03 · **Habilita:** 08

---

## 1. Objetivo

Al terminar esta fase existen los cuatro métodos de mutación que pide la
consigna, todos intercambiables. Cada uno decide **cuántos y cuáles genes de un
individuo se mutan**; qué le pasa a un gen cuando le toca mutar ya lo definió la
fase 01, dentro de cada figura. Es el operador que introduce material genético
nuevo y el que evita que la población colapse a un único genotipo.

---

## 2. Archivos que produce

| Archivo | Qué es |
|---|---|
| `src/mutacion/__init__.py` | Vacío |
| `src/mutacion/gen.py` | Muta un solo gen |
| `src/mutacion/multigen.py` | Muta una cantidad acotada de genes |
| `src/mutacion/uniforme.py` | Decide gen por gen, de forma independiente |
| `src/mutacion/no_uniforme.py` | O muta todos los genes, o ninguno |

---

## 3. Qué hay que implementar

### La firma común

| Recibe | Devuelve |
|---|---|
| El individuo, el generador de azar, la configuración, el ancho y el alto del lienzo | Un individuo nuevo |

**Invariantes que valen para los cuatro:**
- El individuo que llega no se modifica nunca.
- El individuo devuelto tiene la misma cantidad de genes.
- Los genes que no mutaron son copias independientes, no las mismas figuras del
  original.
- Si mutó al menos un gen, el individuo devuelto no tiene aptitud vigente.
- La mutación de un gen concreto se delega en la figura: estos módulos no saben
  qué parámetros tiene ni cómo se recortan.
- Se usa únicamente el generador de azar que llega por parámetro.

**La división de responsabilidades.** Hay dos niveles de probabilidad y conviene
no confundirlos. `extra_gene_Pm` es de esta fase: gobierna cuántos genes del
individuo se eligen para mutar. `intra_gene_Pm` es de la fase 01: gobierna, una
vez que un gen fue elegido, cuáles de sus parámetros cambian. Un gen elegido para
mutar puede terminar sin ningún cambio, si ninguno de sus parámetros salió
sorteado.

---

### `src/mutacion/gen.py`

Con probabilidad `extra_gene_Pm` ocurre un evento de mutación. Si ocurre, se
elige un gen al azar y se lo muta. Si no ocurre, el individuo queda como estaba.

Es el más conservador de los cuatro.

---

### `src/mutacion/multigen.py`

Con probabilidad `extra_gene_Pm` ocurre un evento de mutación. Si ocurre, se
sortea uniformemente una cantidad entre uno y `max_genes_to_mutate`, se eligen
esa cantidad de genes distintos al azar y se los muta.

Los genes elegidos tienen que ser distintos entre sí: si se sortearan con
repetición, la cantidad efectiva de genes mutados sería menor que la sorteada.

Es la variante limitada, y la que la configuración trae por defecto: introduce
variedad en varios lugares del cromosoma a la vez sin llegar a destruir al
individuo entero.

---

### `src/mutacion/uniforme.py`

No hay evento único. Cada gen se evalúa por separado y muta con probabilidad
`extra_gene_Pm`, de forma independiente del resto.

La cantidad esperada de genes mutados es la cantidad de genes por esa
probabilidad. Con cien genes y una probabilidad de 0.15 son quince genes por
individuo en promedio, todas las veces. La diferencia con multigen no está tanto
en el promedio como en la varianza: multigen a veces no muta nada y a veces muta
un puñado, mientras que uniforme muta una cantidad parecida siempre.

---

### `src/mutacion/no_uniforme.py`

Con probabilidad `extra_gene_Pm` ocurre un evento de mutación. Si ocurre, se
mutan **todos** los genes del individuo. Si no ocurre, no muta ninguno.

Es la definición que fija `docs/contexto.md` para este trabajo. Conviene tenerlo
presente porque en la bibliografía el nombre "no uniforme" suele designar otra
cosa: una mutación cuya intensidad decrece con las generaciones. Acá no es eso.

Es el más destructivo de los cuatro. Cuando se dispara, el individuo cambia
entero, y con probabilidades altas la población pierde todo lo acumulado.

---

## 4. Interfaces de otras fases

**Las figuras** de la fase 01 saben mutarse y saben copiarse, y en los dos casos
devuelven una figura nueva sin tocar la original. El método de mutación le pasa a
la figura el generador de azar, la configuración, el ancho y el alto, y recibe la
figura mutada. Nunca mira adentro.

**Los individuos** de la fase 03 exponen su lista de genes, saben copiarse y
saben invalidar su caché de aptitud.

**La configuración** de la fase 00 llega ya validada. Las claves que esta fase lee
son `extra_gene_Pm` y `max_genes_to_mutate`, y se puede asumir que la
probabilidad está entre cero y uno y que la cota de genes no supera la cantidad
de genes del individuo.

**El ancho y el alto** llegan por parámetro y se pasan tal cual a la figura, que
los necesita para recortar sus coordenadas.

---

## 5. Decisiones ya tomadas

| Decisión | Motivo |
|---|---|
| Esta fase decide qué genes mutan, la figura decide qué le pasa a un gen | Permite agregar tipos de figura sin tocar ninguno de los cuatro métodos, y agregar métodos de mutación sin tocar ninguna figura |
| Los cuatro devuelven un individuo nuevo | Si mutaran sobre el original, un individuo que sobrevivió de la generación anterior cambiaría sin que nadie lo pida, y su aptitud cacheada quedaría mintiendo |
| Los genes no mutados también se copian | Si se compartieran, el individuo mutado y el original tendrían figuras en común, y mutar a uno más adelante afectaría al otro |
| El caché se invalida solo si algo cambió | Invalidar siempre obliga a renderizar de nuevo individuos que quedaron idénticos, y el renderizado es lo más caro del motor |
| En multigen los genes se eligen sin repetición | Con repetición, la cantidad efectiva de genes mutados sería menor que la sorteada, y el parámetro dejaría de significar lo que dice |
| "No uniforme" se implementa como lo define `docs/contexto.md` | Es la definición que dio la cátedra para este trabajo, aunque el nombre se use en la bibliografía para otra cosa |

---

## 6. Decisiones abiertas

Ninguna.

---

## 7. Checkpoints obligatorios

- `src/mutacion/multigen.py` — porque sortea una cantidad de genes dentro de un
  rango y después elige cuáles, y ese sorteo determina la intensidad efectiva de
  la mutación.

Los otros tres no llevan checkpoint: aplican una probabilidad directa sobre uno,
sobre cada uno o sobre todos los genes, sin ninguna cuenta intermedia.

---

## 8. Cómo se verifica

| # | Qué se prueba | Entrada | Resultado esperado |
|---|---|---|---|
| 1 | El original no cambia | Los cuatro métodos | Los genes del individuo recibido quedan idénticos |
| 2 | Largo preservado | Los cuatro métodos | El individuo devuelto tiene la misma cantidad de genes |
| 3 | Sin figuras compartidas | Los cuatro métodos | Ninguna figura del individuo devuelto es el mismo objeto que una del original |
| 4 | Caché invalidado | Un individuo evaluado, mutado con probabilidad uno | Pedirle la aptitud al resultado dispara un cálculo nuevo |
| 5 | Probabilidad cero | Los cuatro métodos con `extra_gene_Pm` en cero | Ningún gen cambia |
| 6 | Un solo gen | El método de gen único, con probabilidad uno y muchas repeticiones | Nunca cambia más de un gen |
| 7 | Cota de multigen | Multigen con probabilidad uno y muchas repeticiones | La cantidad de genes cambiados nunca supera `max_genes_to_mutate` |
| 8 | Multigen sin repetición | Multigen con la cota igual a la cantidad de genes y probabilidad uno | Cuando sortea la cantidad máxima, cambian todos los genes |
| 9 | Uniforme en promedio | Uniforme con probabilidad conocida, muchas repeticiones | La cantidad promedio de genes mutados se acerca a la cantidad de genes por la probabilidad |
| 10 | No uniforme es todo o nada | No uniforme, muchas repeticiones | En cada corrida cambian todos los genes o ninguno, nunca una parte |
| 11 | Dominio respetado | Cualquier método aplicado mil veces seguidas | Ningún parámetro de ninguna figura queda fuera de su rango válido |
| 12 | Reproducibilidad | El mismo método dos veces con la misma semilla | El resultado es idéntico |

---

## 9. Errores probables

- **Mutar el individuo recibido en vez de devolver uno nuevo** → un individuo que
  sobrevivió de la generación anterior cambia sin que nadie lo pida, y su caché
  de aptitud queda mintiendo. Es el error más grave de esta fase y no da ninguna
  excepción → verificación 1.
- **Copiar la lista de genes sin copiar las figuras que no mutaron** → el
  individuo nuevo comparte figuras con el original y las mutaciones futuras se
  propagan hacia atrás → verificación 3.
- **No invalidar el caché** → el individuo mutado reporta la aptitud que tenía
  antes de mutar y la selección ordena la población con números falsos →
  verificación 4.
- **Confundir los dos niveles de probabilidad** → se aplica `intra_gene_Pm` para
  elegir genes o `extra_gene_Pm` para elegir parámetros, y la intensidad efectiva
  de la mutación no es la configurada → se detecta con las verificaciones 6, 7
  y 9, que miden cuántos genes cambian.
- **Sortear los genes de multigen con repetición** → mutan menos genes que los
  sorteados → verificación 8.
- **Implementar "no uniforme" como una mutación gen por gen** → queda idéntico a
  uniforme y los experimentos de la fase 12 comparan dos veces lo mismo →
  verificación 10.
- **Recortar el dominio en el método de mutación en vez de en la figura** → cada
  método de mutación tiene que conocer los parámetros de cada tipo de figura →
  el recorte vive en la figura, acá solo se elige a quién mutar.

---

## 10. Cierre de la fase

- [ ] Todos los archivos de la sección 2 existen y se importan sin error
- [ ] Todas las verificaciones de la sección 8 pasan
- [ ] `docs/resumenes/FASE_06_RESUMEN.md` está escrito
- [ ] No se tocó ningún archivo fuera de la lista
- [ ] El agente no commiteó ni pusheó nada
