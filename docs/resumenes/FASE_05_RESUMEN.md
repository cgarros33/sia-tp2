# Resumen Fase 05 — Cruza

---

## Qué hace esta fase

Existen los cuatro métodos de cruza que pide la consigna, todos intercambiables
entre sí. Cada uno recibe dos padres y devuelve dos hijos: recombina el material
genético de los padres para producir individuos nuevos. Es el paso que sigue a la
selección de la fase 04, que entrega los padres, y el que alimenta a la mutación
de la fase 06. Los cuatro comparten la misma firma, así que el motor los cambia
leyendo un campo de la configuración y la experimentación los compara sin tocar
código.

---

## Archivos

| Archivo | Qué hace |
|---|---|
| `src/cruza/__init__.py` | Vacío |
| `src/cruza/comun.py` | Verifica el largo de los padres y arma los dos hijos a partir de una máscara de loci |
| `src/cruza/un_punto.py` | Se intercambia el sufijo desde un corte |
| `src/cruza/dos_puntos.py` | Se intercambia el bloque entre dos cortes |
| `src/cruza/uniforme.py` | Se sortea locus por locus |
| `src/cruza/anular.py` | Se intercambia un segmento circular |

Además se agregó el campo `uniform_crossover_P` a `config/conf.json` y a
`src/config.py`, que son de la fase 00. Está explicado abajo, en Decisiones.

---

## La firma que comparten los cuatro

```
cruzar(padre, madre, azar, config) -> (hijo1, hijo2)
```

**Invariantes de los cuatro:**

- Devuelven **dos individuos nuevos**, nunca los padres. Es obligatorio:
  `Poblacion` rechaza dos referencias al mismo individuo, y la selección devuelve
  referencias repetidas, así que el mismo objeto puede llegar como padre y como
  madre.
- **Preservan el locus.** El gen del locus `i` de un padre sólo puede terminar en
  el locus `i` de un hijo. Es la consecuencia directa de que las figuras se
  dibujen en orden: la posición de un gen es información genética.
- Los dos hijos son **complementarios**: en cada locus, uno se queda el gen del
  padre y el otro el de la madre. Entre los dos no se pierde ni se duplica nada.
- **No tocan a los padres** ni comparten genes por referencia con ellos.
- Sortean únicamente con el generador que llega por parámetro.
- **No evalúan.** Un hijo nace sucio y su fitness lo calcula más tarde quien
  corresponda.
- Exigen que los dos padres tengan la misma cantidad de genes.

---

## El eje del diseño: una máscara de loci

Los cuatro métodos hacen lo mismo a nivel abstracto —elegir un subconjunto de
loci e intercambiarlo entre los dos padres— y se diferencian **sólo en cómo
eligen ese subconjunto**. Entonces cada método se reduce a producir un vector
booleano de largo `gene_count` que dice qué loci se intercambian, y el armado de
los hijos vive una sola vez, en `comun.py`.

```
hijo1[i] = madre.gen(i) si mascara[i], si no padre.gen(i)
hijo2[i] = padre.gen(i) si mascara[i], si no madre.gen(i)
```

Con eso cada archivo de método queda en seis líneas y toda la diferencia entre
los cuatro se lee de un vistazo. Es el mismo criterio con el que la fase 04 puso
la rutina de ruleta en `src/seleccion/comun.py`.

---

## Archivo por archivo

### `src/cruza/comun.py`

Lo que los cuatro métodos hacen igual, en un solo lugar.

| Función | Recibe | Devuelve | Qué hace |
|---|---|---|---|
| `largo_comun(padre, madre)` | Los dos padres | El largo del cromosoma | Corta con `ErrorDeCruza` si no miden lo mismo |
| `hijos_por_mascara(padre, madre, mascara)` | Los padres y el vector booleano | Los dos hijos | Arma los dos individuos complementarios |

**`hijos_por_mascara(...)`** — recorre los loci y en cada uno le da a un hijo el
gen del padre y al otro el de la madre, según la máscara. Los genes se copian con
`copiar()` antes de entrar a un hijo: las figuras hoy son inmutables, así que
compartir la referencia sería correcto, pero copiar cuesta nada al lado de un
renderizado y deja a la fase 06 libre de mutar como quiera sin que un hijo le
cambie los genes al padre.

**Regla que si alguien la borra rompe algo.** Cuando la máscara está toda en
falso o toda en verdadero, la función devuelve `padre.copiar()` y `madre.copiar()`
(cruzados en el segundo caso) en vez de rearmar los individuos gen por gen.
`Individuo.copiar()` conserva el fitness cacheado, y un hijo genéticamente
idéntico a un padre tiene el mismo fitness: rearmarlo lo dejaría sucio y
dispararía un renderizado que ya se pagó. Con las convenciones de corte de abajo
el caso sólo aparece en el cruce uniforme.

---

### `src/cruza/un_punto.py`

Sortea un corte `P` y marca todos los loci desde `P` hasta el final.

**El corte se sortea uniformemente entre 1 y `gene_count - 1`.** En 0 el sufijo
sería todo el cromosoma y en `gene_count` sería vacío: en los dos casos los hijos
saldrían clones de los padres y la cruza no aportaría genotipos nuevos. Es además
la convención de los libros.

---

### `src/cruza/dos_puntos.py`

Sortea dos cortes distintos `P1 < P2` y marca el bloque `[P1, P2)`.

**Los dos cortes se sortean entre 1 y `gene_count - 1`, sin repetición.** Con eso
el prefijo, el bloque del medio y el sufijo quedan siempre no vacíos, que es lo
que distingue a este método del de un punto. Hacen falta al menos tres genes para
que existan dos cortes así.

---

### `src/cruza/uniforme.py`

Cada locus se sortea por separado y se intercambia con probabilidad
`uniform_crossover_P`. Es el único de los cuatro que usa `config`, y el único que
puede producir un hijo idéntico a un padre: con `gene_count` = 100 y probabilidad
0,5 eso ocurre con probabilidad `2 · 0,5^100`, o sea nunca, pero el caso está
contemplado en `comun.py`.

Es el más disruptivo de los cuatro: rompe los bloques contiguos de genes en vez
de conservarlos, así que mezcla mucho más pero destruye esquemas de orden alto.

---

### `src/cruza/anular.py`

Trata al cromosoma como un anillo: sortea un inicio `P` uniforme entre 0 y
`gene_count - 1` y un largo `M`, y marca el segmento circular de largo `M` que
arranca en `P`.

**El largo se sortea entre 1 y `gene_count // 2`.** Un segmento circular de largo
`k` que arranca en `P` intercambia exactamente los mismos loci que uno de largo
`gene_count - k` que arranca en `P + k`, con los papeles de padre y madre dados
vuelta. Pasada la mitad del anillo no aparecen intercambios nuevos: sólo se
repiten los de la otra mitad. Acotarlo a la mitad muestrea cada intercambio una
sola vez.

Comparado con el de dos puntos, este método puede intercambiar un bloque que
cruza el final del cromosoma y vuelve al principio, que es justamente lo que el
de dos puntos no alcanza.

---

## Cómo comprobar que anda

```bash
PYTHONPATH=. python3 -c "
import numpy as np
from src.individuo import Individuo
from src.figuras.triangulo import Triangulo
from src.cruza import un_punto, dos_puntos, uniforme, anular

def individuo(marca, largo=8):
    return Individuo([Triangulo((0.,0.,1.,1.,2.,2.), (marca, i, 0, 255)) for i in range(largo)])

config = {'uniform_crossover_P': 0.5}
for metodo in (un_punto, dos_puntos, uniforme, anular):
    padre, madre = individuo(10), individuo(20)
    h1, h2 = metodo.cruzar(padre, madre, np.random.default_rng(7), config)
    print(metodo.__name__,
          [g.parametros()[6] for g in h1.genes],
          [g.parametros()[6] for g in h2.genes])
"
```

Cada individuo tiene los ocho genes marcados con el mismo número, 10 el padre y
20 la madre, así que la lista de marcas de un hijo dice de dónde vino cada gen.
Lo que tiene que pasar:

1. **Las dos listas de cada línea son complementarias**: donde una tiene 10 la
   otra tiene 20. Si en algún locus las dos coincidieran, se habría perdido o
   duplicado material genético.
2. **La forma de cada línea delata al método**: `un_punto` tiene exactamente un
   cambio de valor a lo largo de la lista; `dos_puntos`, exactamente dos, con la
   primera y la última marca iguales; `anular`, un bloque contiguo leyendo la
   lista como circular; `uniforme`, cualquier patrón.
3. **Repetir el comando da idénticas las cuatro líneas**, porque el único azar
   sale del generador que se pasa por parámetro.

Comprobado además sobre 5000 cruzas de cromosomas de 12 genes: `un_punto`
intercambia siempre entre 1 y 11 genes, `dos_puntos` entre 1 y 10 dejando prefijo
y sufijo, y `anular` entre 1 y 6 en un bloque siempre contiguo sobre el anillo.
Ninguno devolvió nunca un hijo clon de un padre.

---

## Decisiones y pendientes

**Decisiones**

- **El largo del cromosoma sale de los padres**, no de `config["gene_count"]`.
  Los métodos no leen la configuración para nada que ya esté en el dato que
  reciben, y así la cruza se puede probar sin armar una configuración entera.
- **Sin cortes degenerados en un punto, dos puntos y anular.** Los rangos de
  sorteo están elegidos para que el bloque intercambiado nunca sea vacío ni
  total: cada cruza aporta genotipos nuevos y ninguna generación desperdicia
  lugares en clones.
- **El largo del segmento anular llega hasta la mitad**, por la redundancia
  explicada arriba.
- **Los genes se copian al armar un hijo**, aunque hoy las figuras sean
  inmutables, para que la fase 06 no tenga que preocuparse por el aliasing.
- **No hay tabla de despacho.** Los nombres de módulo coinciden con los valores
  de `METODOS_DE_CRUZA` en `src/config.py`, así que el motor de la fase 08
  despacha por nombre. La fase 04 tampoco agregó registro.

**Pendientes y cosas que las próximas fases tienen que saber**

- **Se agregó `uniform_crossover_P` a `config/conf.json` y a `src/config.py`,
  que son archivos de la fase 00.** El `docs/contexto.md` dice que el cruce
  uniforme usa "una probabilidad P (típicamente 0.5)" pero no la incluye en la
  lista de variables de configuración, y la experimentación de la fase 12 la va a
  querer barrer sin editar código. Entró en `CAMPOS` y en `PROBABILIDADES`, que
  ya obliga al rango [0, 1]. **Hay que confirmarlo con el dueño de la fase 00.**
- **El apareamiento de los padres es del motor, fase 08.** La cruza recibe dos
  individuos y no opina sobre quién se cruza con quién. `src/config.py` ya exige
  que `selected_count` sea par por ese motivo.
- **No hay probabilidad de cruza.** Los cuatro métodos cruzan siempre. Si el
  motor quiere que un par pase de largo sin recombinarse, es una decisión suya:
  no hay campo de configuración para eso y el `docs/contexto.md` no lo pide.
- **La cruza no muta ni evalúa.** Los hijos salen sucios y la fase 06 los muta
  antes de que alguien les pida el fitness.
