# Resumen Fase 03 — Individuo y Población

---

## Qué hace esta fase

Antes existían las figuras sueltas. Ahora existe el **cromosoma** (una lista
ordenada de largo fijo de figuras, con su fitness cacheado) y la **generación**
(el conjunto de individuos, con sus métricas). Las dos clases son contenedores:
no sortean nada, no renderizan y no saben de qué tipo son sus figuras.

Lo único que hacen de fondo es evitar renderizados. El individuo guarda su
fitness y solo lo recalcula cuando lo mutan de verdad.

---

## Archivos

| Archivo | Qué hace |
|---|---|
| `src/individuo.py` | `Individuo`: la lista de genes más el caché de fitness |
| `src/poblacion.py` | `Poblacion`: los individuos de una generación, su fitness y su diversidad |

---

## `src/individuo.py`

El orden de los genes es información genética: es el orden de dibujado. Por eso
es una lista y el largo es fijo, así los cuatro operadores de cruza intercambian
siempre el mismo locus.

| Método | Recibe | Devuelve | Qué hace |
|---|---|---|---|
| `Individuo(genes)` | secuencia de figuras | — | Guarda el cromosoma; nace sucio |
| `genes` | — | tupla de figuras | Vista inmutable, para la cruza |
| `gen(locus)` | entero | figura | Un gen suelto |
| `establecer_gen(locus, gen)` | entero, figura | — | Lo reemplaza e invalida el caché |
| `__len__()` | — | entero | `gene_count` |
| `fitness(evaluador)` | invocable | flotante | El caché, o lo calcula si está sucio |
| `fitness_cacheado` | — | flotante o `None` | El valor sin forzar el cálculo |
| `esta_sucio` | — | booleano | Si hay que reevaluar |
| `copiar()` | — | `Individuo` | Copia profunda que conserva el caché |
| `vector_parametros()` | — | vector de `gene_count × P` | Genotipo aplanado |
| `nombres_parametros()` | — | tupla de nombres | `g0_x0, g0_y0, ...`, mismo orden |

**El evaluador.** `fitness` recibe un invocable de la fase 02 con la firma
`evaluador(genes) -> flotante en [0, 1]`, maximizante. Recibe la secuencia de
genes y no el individuo para que la fase 02 no tenga que importar esta.

**El caché.** El fenotipo depende solo del genotipo, y el genotipo solo cambia
por `establecer_gen`, que es el único método que escribe. Entonces caché limpio
implica mismo fitness. Esto depende de que las figuras nunca se modifiquen en el
lugar, invariante de la fase 01: si alguien lo rompe, el caché miente.

`establecer_gen` compara los parámetros antes de ensuciar: con `intra_gene_Pm`
en 0.2, uno de cada nueve genes mutados sale idéntico y renderizarlo de nuevo
sería gratis para nadie.

`copiar()` conserva el fitness porque una copia exacta tiene el mismo fenotipo.
Eso es lo que hace barata a la supervivencia aditiva. La copia es profunda
porque la fase 05 exige que ningún hijo comparta objetos con su padre.

---

## `src/poblacion.py`

Tamaño constante durante toda la corrida. Acá el orden no significa nada.

| Método | Recibe | Devuelve | Qué hace |
|---|---|---|---|
| `Poblacion(individuos, rangos, generacion=0)` | lista, rangos de un gen, entero | — | Valida y guarda |
| `individuos` / `rangos` / `generacion` | — | tupla, tupla, entero | Accesores |
| `__len__`, `__iter__`, `__getitem__` | — | — | Se recorre como una secuencia |
| `evaluar(evaluador)` | invocable | vector | Fitness de todos, respetando cada caché |
| `fitness` | — | vector | El vector ya calculado |
| `mejor()` | — | `Individuo` | El de fitness máximo; ante empate, el primero |
| `fitness_maximo` / `fitness_minimo` / `fitness_promedio` | — | flotante | Las tres columnas del CSV; el promedio lo usa Boltzmann |
| `diversidad()` | — | flotante | Ver abajo |
| `siguiente(individuos)` | lista | `Poblacion` | `generacion + 1`, mismos rangos, mismo tamaño |

**`evaluar` es el único lugar que llama al evaluador.** Las métricas leen el
vector ya calculado y fallan si se las pide antes. Así ninguna métrica dispara
cien renderizados sin que se note. Es también el único punto a tocar el día que
se paralelice.

**`diversidad()`.** Desvío estándar normalizado promedio por locus. Se arma la
matriz de `population_size` filas por `gene_count × P` columnas con todos los
parámetros de todos los individuos, y se promedia el desvío de cada columna
dividido por el ancho del rango válido de ese parámetro:

```
D = promedio sobre las columnas de:  desvio(columna) / (maximo - minimo)
```

Los rangos son los que reporta `Figura.rangos`, o sea el mismo dominio donde
recorta la mutación. La normalización es obligatoria: una coordenada se mueve en
~520 unidades y un canal de color en 255, y sin dividir el promedio quedaría
dominado por la geometría. El desvío es poblacional (sin corrección de Bessel):
estos individuos son la población, no una muestra de otra más grande.

**`D` va de 0 a 0.5, no a 1.** Para una variable acotada de rango `R` el desvío
máximo es `R/2`, mitad de la población en cada extremo. `D = 0` significa que la
población colapsó a un solo genotipo.

Con óvalos y PNG la métrica sobreestima un poco: la rotación se envuelve en vez
de recortarse (fase 01), así que valores cerca de 0 y cerca de 1 describen
figuras casi iguales pero están lejos numéricamente. Es 1 de 9 parámetros.

**El constructor rechaza dos referencias al mismo individuo.** Elite puede
seleccionar al mismo varias veces y la aditiva arrastra referencias; si el mismo
objeto entra dos veces, mutar uno muta los dos y la diversidad real baja sin que
ninguna métrica lo diga. Quien reutiliza un individuo lo copia.

---

## Cómo comprobar que anda

```bash
python3 - <<'PY'
import numpy as np
from src.figuras.triangulo import Triangulo
from src.individuo import Individuo
from src.poblacion import Poblacion

config = {'max_coord_overflow': 10.0, 'max_coord_delta': 15.0, 'max_color_delta': 25,
          'intra_gene_Pm': 1.0}
azar = np.random.default_rng(42)
rangos = Triangulo.rangos(config, 200, 200)
llamadas = []
evaluador = lambda genes: llamadas.append(1) or 1.0

individuo = Individuo([Triangulo.aleatoria(azar, config, 200, 200) for _ in range(4)])
individuo.fitness(evaluador); individuo.fitness(evaluador)
individuo.establecer_gen(0, individuo.gen(0).copiar())
individuo.fitness(evaluador)
individuo.establecer_gen(0, individuo.gen(0).mutar(azar, config, 200, 200))
individuo.fitness(evaluador)
print('renderizados (esperado 2):', len(llamadas))

clones = Poblacion([individuo.copiar() for _ in range(5)], rangos)
print('diversidad de clones (esperado ~0):', round(clones.diversidad(), 12))

extremos = [Individuo([Triangulo(tuple(v[k] for v in rangos[:6]),
                                 tuple(int(v[k]) for v in rangos[6:])) for _ in range(4)])
            for k in (0, 1)]
print('diversidad maxima (esperado 0.5):', Poblacion(extremos, rangos).diversidad())
PY
```

Tienen que salir 2 renderizados, diversidad 0 y diversidad 0.5. Si salen 3
renderizados, `establecer_gen` está ensuciando el caché con un gen idéntico.

---

## Decisiones y pendientes

**Decisiones**

- **La mutación es en el lugar**, con marca de sucio, como pide el contexto. Que
  mutar devolviera un individuo nuevo haría innecesaria la marca, pero duplica
  objetos sin ganar nada porque las figuras ya son inmutables.
- **La generación 0 no se arma acá**: el muestreo aleatorio y
  `sesgo_color_inicial` van en `src/inicializacion.py` (fase 08).
- **La población guarda los rangos** y se los pasa a la generación siguiente, así
  el motor no tiene que acordarse de ellos en cada generación.
- **Diversidad por desvío normalizado y no por distancia entre pares**: la
  distancia promedio entre todos los pares mide lo mismo pero cuesta O(N²·L) en
  vez de O(N·L) y no tiene normalización natural. La entropía por locus obligaría
  a discretizar parámetros continuos, con el resultado dependiendo de los bins.

**Pendientes**

- **Evaluación secuencial.** Es paralelizable —cada individuo es
  independiente— pero implica serializar figuras e imagen objetivo hacia otros
  procesos y todavía no sabemos cuánto pesa. Se mide en la fase 12; el cambio
  toca solo `evaluar`.
- **La firma del evaluador está acordada pero no probada contra la fase 02.**
  Cuando exista `src/fitness.py` hay que confirmar que sea
  `evaluador(genes) -> [0, 1]` maximizante.
