# Resumen Fase 07 — Supervivencia

---

## Qué hace esta fase

Existen las dos estrategias de supervivencia de la consigna. Cada una recibe la
población actual y los hijos recién generados, y devuelve los individuos que
forman la generación siguiente. No comparan aptitudes: eso lo hace el método de
selección, que llega **como parámetro** en vez de leerse de la configuración, así
que el motor decide con cuál elegir y esta fase no depende de la 04.

---

## Archivos

| Archivo | Qué hace |
|---|---|
| `src/supervivencia/__init__.py` | Vacío |
| `src/supervivencia/comun.py` | Copia los individuos que aparecen más de una vez |
| `src/supervivencia/aditiva.py` | Padres e hijos compiten juntos |
| `src/supervivencia/exclusiva.py` | La generación se arma con hijos, y se completa si faltan |

---

## La firma que comparten las dos

```
sobrevivientes(actuales, hijos, cantidad, seleccionar, azar, config) -> lista
```

Con N = `cantidad` (el tamaño de la población) y K = `len(hijos)`:

| Estrategia | Caso | Nueva generación |
|---|---|---|
| `aditiva` | — | N elegidos de `actuales + hijos` (N+K candidatos) |
| `exclusiva` | K > N | N elegidos entre los K hijos, sin ningún padre |
| `exclusiva` | K ≤ N | los K hijos enteros + (N−K) elegidos de la generación actual |

**Invariantes:** devuelven exactamente `cantidad` individuos, no modifican las
listas que reciben, sortean sólo con el generador que llega por parámetro y no
evalúan. En el caso K = N `exclusiva` no llama a la selección: no hace falta.

---

## Lo único que no es obvio: los repetidos se copian

La selección devuelve **referencias repetidas** —un mismo objeto puede salir
varias veces— y `Poblacion._validar` las rechaza. `sin_repetir_referencias`
recorre la lista final y, del segundo uso en adelante de un mismo individuo, mete
un `Individuo.copiar()`.

**Regla que si alguien la borra rompe algo.** Sin eso, `Poblacion` no construye,
y peor: como la mutación de la fase 06 es **en el lugar**, dos referencias al
mismo individuo se mutarían juntas y bajarían la diversidad real sin que ninguna
métrica lo muestre.

Sólo se copian los repetidos. Los demás sobrevivientes pasan como el **mismo
objeto**, que es lo que conserva su fitness cacheado y evita re-renderizarlos: es
justo el ahorro que hace valiosa a la supervivencia aditiva. `copiar()` también
se lleva el fitness, así que ni las copias cuestan un renderizado.

---

## Cómo comprobar que anda

```bash
PYTHONPATH=. python3 -c "
import numpy as np
from src.individuo import Individuo
from src.figuras.triangulo import Triangulo
from src.seleccion import elite
from src.supervivencia import aditiva, exclusiva

def poblar(marca, cantidad, desde):
    gente = []
    for i in range(cantidad):
        ind = Individuo([Triangulo((0.,0.,1.,1.,2.,2.), (marca, i, 0, 255))])
        ind.fitness(lambda genes, v=desde + i: v)
        gente.append(ind)
    return gente

for estrategia in (aditiva, exclusiva):
    for k in (6, 10, 16):
        salida = estrategia.sobrevivientes(poblar(10, 10, 0), poblar(20, k, 5), 10,
                                           elite.seleccionar, np.random.default_rng(1), {})
        padres = sum(1 for i in salida if i.gen(0).parametros()[6] == 10)
        print(estrategia.__name__, 'K =', k, '-> total', len(salida), 'padres', padres)
"
```

Las seis líneas tienen que dar **total 10**, con **5, 3 y 0 padres** en `aditiva`
y **4, 0 y 0** en `exclusiva`. Los dos ceros de `exclusiva` son la estrategia: con
K ≥ N ningún padre sobrevive, pase lo que pase con las aptitudes. El cero de
`aditiva` con K = 16 no lo es: ahí los hijos del ejemplo son más aptos y se quedan
con todo, pero podrían no serlo. Esa es la diferencia entre las dos.

Comprobado además: con élite, `aditiva` se queda exactamente con los diez mejores
del pozo mezclado; ningún individuo aparece dos veces por referencia con élite,
ruleta ni torneo, y `Poblacion.siguiente(...)` acepta el resultado; los
sobrevivientes no repetidos conservan su fitness cacheado y las copias también.

---

## Decisiones y pendientes

- **El método de selección llega por parámetro**, no de `config["seleccion"]`.
  Es lo que pide el mapa de fases y lo que permite probar esta fase sin la 04.
- **En el caso K ≤ N los (N−K) salen de la generación actual**, no del pozo
  mezclado: es literal al `docs/contexto.md` y es lo que hace el reemplazo más
  duro que el aditivo.
- **Con `config/conf.json` como está** (`population_size` = 100,
  `selected_count` = 100) resulta K = N, así que **`exclusiva` reemplaza la
  población entera por hijos y ningún padre sobrevive nunca**. Es correcto según
  la consigna, pero hay que tenerlo en cuenta al leer los gráficos.
- **Hay un solo campo `seleccion`**, así que el motor va a usar el mismo método
  para elegir padres y sobrevivientes. Es habitual que sean dos distintos: si el
  grupo lo quiere, es un campo nuevo de configuración.
