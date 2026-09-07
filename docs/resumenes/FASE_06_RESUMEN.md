# Resumen Fase 06 — Mutación

---

## Qué hace esta fase

Existen los cuatro métodos de mutación de la consigna, intercambiables entre sí.
Cada uno decide **qué genes de un individuo mutan** y le pide a cada uno de esos
genes que se mute. No toca los parámetros de las figuras: eso ya lo hace
`Figura.mutar`, que recorre cada parámetro con probabilidad `intra_gene_Pm` y lo
recorta a su rango. La fase 06 es dueña de `extra_gene_Pm`, "la probabilidad de
que un gen mute".

---

## Archivos

| Archivo | Qué hace |
|---|---|
| `src/mutacion/__init__.py` | Vacío |
| `src/mutacion/comun.py` | Filtra los loci candidatos por su sorteo y los muta |
| `src/mutacion/gen.py` | Un solo gen sorteado |
| `src/mutacion/multigen.py` | Entre 1 y `max_genes_to_mutate` genes sorteados |
| `src/mutacion/uniforme.py` | Los `gene_count` genes, cada uno por su cuenta |
| `src/mutacion/no_uniforme.py` | Los `gene_count` genes, con un único sorteo |

---

## La firma que comparten los cuatro

```
mutar(individuo, azar, config, ancho, alto) -> el mismo individuo
```

`ancho` y `alto` son los del canvas, que `Figura.mutar` necesita para recortar.

**Invariantes:**

- **Mutan el individuo en el lugar** y devuelven ese mismo objeto, no una copia.
  Quien no quiera perder el original lo copia antes.
- Van por `Individuo.establecer_gen`, que invalida el caché de fitness **sólo si
  los parámetros cambiaron de verdad**. Si una figura muta pero ningún parámetro
  pasa `intra_gene_Pm`, el fitness cacheado sobrevive y se ahorra un renderizado.
- Sortean únicamente con el generador que llega por parámetro.
- No evalúan ni copian genes.

---

## Los cuatro, en una tabla

Todos usan `extra_gene_Pm` como Pm. Sólo cambian los candidatos y cuántos
sorteos se tiran.

| Método | Candidatos | Sorteos de Pm | Genes que mutan |
|---|---|---|---|
| `gen` | un locus sorteado | 1 | 0 o 1 |
| `multigen` | k loci sorteados sin repetir, k uniforme en `[1, max_genes_to_mutate]` | uno por candidato | 0 a k |
| `uniforme` | los `gene_count` loci | uno por candidato | 0 a `gene_count` |
| `no_uniforme` | los `gene_count` loci | **1, que decide por todos** | 0 o `gene_count` |

La diferencia entre `uniforme` y `no_uniforme` es la única sutil: los dos mutan
`gene_count · Pm` genes en promedio, pero el uniforme reparte (binomial) y el no
uniforme es **todo o nada**. Medido sobre 1000 corridas con Pm = 0,5 y 20 genes:
el no uniforme dio siempre 0 o 20, el uniforme dio entre 2 y 17, nunca los
extremos.

---

## Cómo comprobar que anda

```bash
PYTHONPATH=. python3 -c "
import numpy as np
from src.individuo import Individuo
from src.figuras.triangulo import Triangulo
from src.mutacion import gen, multigen, uniforme, no_uniforme

config = {'extra_gene_Pm': 1.0, 'intra_gene_Pm': 1.0, 'max_genes_to_mutate': 5,
          'max_coord_delta': 15.0, 'max_color_delta': 25, 'max_coord_overflow': 10.0}
azar = np.random.default_rng(1)
for metodo in (gen, multigen, uniforme, no_uniforme):
    original = Individuo([Triangulo.aleatoria(np.random.default_rng(0), config, 100, 100) for _ in range(20)])
    copia = original.copiar()
    metodo.mutar(copia, azar, config, 100, 100)
    print(metodo.__name__, sum(1 for a, b in zip(original.genes, copia.genes)
                               if a.parametros() != b.parametros()))
"
```

Con `extra_gene_Pm` e `intra_gene_Pm` en 1, la cantidad de genes cambiados tiene
que ser: 1 para `gen`, entre 1 y 5 para `multigen`, y 20 para `uniforme` y
`no_uniforme`. Con `extra_gene_Pm` en 0 los cuatro tienen que dar 0 y dejar el
fitness cacheado intacto. Repetir con la misma semilla tiene que dar lo mismo.

---

## Decisiones y pendientes

- **En `multigen`, Pm se sortea una vez por gen elegido**, no una vez por evento.
  Así `gen` es el caso k = 1 y `uniforme` el caso k = `gene_count`: los tres son
  la misma familia con distinto conjunto de candidatos, y `no_uniforme` es el
  único con sorteo único. Mutan k · Pm genes en promedio.
- **La mutación es en el lugar.** `Individuo.establecer_gen` está hecho para eso
  y ya resuelve la invalidación del caché. Devolver individuos nuevos tiraría el
  ahorro de renderizado descrito arriba.
- **Los rangos y el envoltorio de la rotación son de la figura**, no de acá:
  duplicarlos serían dos lugares donde corregir el mismo error.
- **El motor (fase 08) tiene que mutar sólo a los hijos.** Como la mutación es en
  el lugar, mutar un padre que sobrevive por supervivencia aditiva lo cambiaría
  dentro de la población.
- **`no_uniforme` no es la mutación no uniforme de la literatura**, donde lo que
  decrece con las generaciones es la magnitud del delta. Acá se implementa lo que
  define el `docs/contexto.md`: un sorteo que muta el individuo entero.
