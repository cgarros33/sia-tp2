# Fase 07 — Supervivencia

> **Ola:** 3 · **Depende de:** 03, 04 · **Habilita:** 08

---

## 1. Objetivo

Al terminar esta fase existen las dos estrategias de supervivencia que pide la
consigna. Dadas la población actual y los hijos recién generados, cada una decide
quiénes componen la generación siguiente, manteniendo el tamaño de la población
constante. Es lo que determina cuánto sobrevive de una generación a la otra: si
los padres compiten con los hijos o si los hijos los reemplazan.

---

## 2. Archivos que produce

| Archivo | Qué es |
|---|---|
| `src/supervivencia/__init__.py` | Vacío |
| `src/supervivencia/aditiva.py` | Padres e hijos compiten juntos |
| `src/supervivencia/exclusiva.py` | Los hijos reemplazan a los padres |

---

## 3. Qué hay que implementar

### La firma común

| Recibe | Devuelve |
|---|---|
| La lista de individuos de la población actual, la lista de hijos, el tamaño que tiene que tener la generación siguiente, el método de selección a usar, el generador de azar y la configuración | Una lista con exactamente ese tamaño |

El método de selección llega como parámetro, no se elige acá. Es cualquiera de
los siete de la fase 04, y esta fase lo trata como una caja negra: le pasa una
lista de candidatos y una cantidad, y recibe los elegidos.

**Invariantes que valen para las dos:**
- Devuelven exactamente el tamaño pedido.
- No modifican los individuos que reciben ni sus genes.
- Devuelven referencias, no copias: los individuos que sobreviven conservan su
  aptitud cacheada, que es justamente lo que hace que sobrevivir sea barato.
- Asumen que tanto los padres como los hijos ya fueron evaluados.

---

### `src/supervivencia/aditiva.py`

Se arma un único conjunto de candidatos con todos los individuos de la población
actual más todos los hijos, y de ese conjunto se seleccionan tantos como indique
el tamaño de la nueva generación, usando el método de selección recibido.

Los hijos no reemplazan automáticamente a los padres: compiten con ellos. Un
padre que sigue siendo mejor que todos los hijos permanece en la población tantas
generaciones como haga falta. Lo que prima es la aptitud, no la generación de
origen.

Tiene una consecuencia importante: como los individuos sobreviven muchas
generaciones, el caché de aptitud de la fase 03 se vuelve determinante. Sin él,
un individuo que sobrevive doscientas generaciones se renderizaría doscientas
veces para dar siempre el mismo número.

---

### `src/supervivencia/exclusiva.py`

El reemplazo es más duro: en la medida de lo posible, la nueva generación se arma
solo con hijos.

- Si hay más hijos que el tamaño de la nueva generación, se seleccionan de entre
  los hijos exclusivamente, y ningún padre sobrevive.
- Si hay menos hijos que ese tamaño, o la misma cantidad, entran todos los hijos
  y las posiciones que faltan se completan seleccionando entre los individuos de
  la población actual.

Con la configuración por defecto, donde la cantidad de padres seleccionados es
igual al tamaño de la población y cada pareja produce dos hijos, la cantidad de
hijos coincide con el tamaño de la población y se cae en el segundo caso justo en
el límite: la nueva generación son todos hijos y no sobrevive ningún padre.

---

## 4. Interfaces de otras fases

**Los individuos** de la fase 03 exponen su aptitud cacheada. Esta fase no toca
sus genes.

**Los métodos de selección** de la fase 04 comparten una firma única: reciben una
lista de individuos, una cantidad, el generador de azar y la configuración, y
devuelven esa cantidad de individuos elegidos, con repetición permitida. Esta
fase los invoca sin saber cuál le tocó.

Hay un punto de contacto que importa: las fórmulas de élite y de ranking usan el
tamaño de la lista de candidatos que reciben, no el campo `population_size` de la
configuración. La supervivencia aditiva llama a la selección con una lista más
larga que ese campo, porque junta padres e hijos, y si el método usara el campo
las cuentas saldrían mal.

**El generador de azar** llega por parámetro y es el único de la corrida.

---

## 5. Decisiones ya tomadas

| Decisión | Motivo |
|---|---|
| El tamaño de la población es constante | Las dos estrategias están definidas como transiciones entre poblaciones del mismo tamaño |
| El método de selección llega por parámetro | Cualquiera de los siete tiene que poder combinarse con cualquiera de las dos estrategias, y eso da los catorce pares que la fase 12 va a comparar |
| Se devuelven referencias y no copias | Un individuo que sobrevive conserva su aptitud cacheada; copiarlo la tiraría y forzaría un renderizado que ya se pagó |
| La repetición que permite la selección se acepta tal cual | Un individuo muy apto puede quedar duplicado en la nueva generación. Es consecuencia esperada de la presión de selección, y la métrica de diversidad de la fase 03 está justamente para detectar cuándo eso se vuelve un problema |

---

## 6. Decisiones abiertas

- **Elitismo explícito.** La supervivencia aditiva garantiza que el mejor
  individuo sobreviva solo si el método de selección lo elige, y los métodos
  probabilísticos podrían no hacerlo. Reservar una o dos posiciones para los
  mejores, sin sorteo, es un agregado chico que evita perder el mejor por mala
  suerte. No se implementa acá porque no está en la consigna, pero si la fase 12
  muestra que el mejor fitness retrocede entre generaciones, es lo primero que
  hay que agregar. Requiere avisar al grupo, porque suma un campo de
  configuración.

---

## 7. Checkpoints obligatorios

- `src/supervivencia/aditiva.py` — porque decide qué individuos pasan a la
  generación siguiente combinando dos poblaciones.
- `src/supervivencia/exclusiva.py` — por el reparto entre hijos y padres según
  las dos ramas del caso.

---

## 8. Cómo se verifica

| # | Qué se prueba | Entrada | Resultado esperado |
|---|---|---|---|
| 1 | Tamaño constante | Las dos estrategias, con distintas cantidades de hijos | Siempre devuelven exactamente el tamaño pedido |
| 2 | Entradas intactas | Las dos estrategias | Las listas de padres e hijos conservan su contenido |
| 3 | Aditiva considera a todos | Aditiva con selección por élite, y un padre con la aptitud más alta de todo el conjunto | Ese padre está en la nueva generación |
| 4 | Aditiva no privilegia a los hijos | Aditiva con selección por élite y padres mejores que todos los hijos | La nueva generación son todos padres |
| 5 | Exclusiva con más hijos que lugares | Más hijos que el tamaño pedido | Ningún padre aparece en la nueva generación |
| 6 | Exclusiva con menos hijos que lugares | Menos hijos que el tamaño pedido | Están todos los hijos, y el resto son padres |
| 7 | Exclusiva en el límite | Tantos hijos como el tamaño pedido | La nueva generación son todos hijos |
| 8 | Sin renderizados de más | Padres e hijos ya evaluados | No se dispara ningún cálculo de aptitud |
| 9 | Se preserva el caché | Un padre evaluado que sobrevive | Pedirle la aptitud no dispara un cálculo nuevo |
| 10 | Compatibilidad con los siete métodos | Las dos estrategias con cada uno de los siete | Todas las combinaciones devuelven el tamaño correcto |
| 11 | Reproducibilidad | La misma estrategia dos veces con la misma semilla | El resultado es idéntico |

---

## 9. Errores probables

- **Copiar los individuos que sobreviven** → se pierde el caché de aptitud y cada
  generación paga de nuevo los renderizados de todos los sobrevivientes, que es
  exactamente lo que la supervivencia aditiva viene a aprovechar →
  verificaciones 8 y 9.
- **Que el método de selección use `population_size` de la configuración en vez
  del largo de la lista recibida** → en la aditiva la lista es más larga que ese
  campo y las fórmulas de élite y ranking dan cuentas mal hechas → verificación 3
  con una lista de candidatos más larga que el tamaño de la población.
- **Invertir las ramas de la exclusiva** → cuando sobran hijos se meten padres, o
  al revés → verificaciones 5 y 6.
- **Devolver más o menos individuos que el tamaño pedido** → la población deja de
  ser constante y todo lo que depende de su tamaño empieza a desviarse →
  verificación 1.
- **Cortar en el caso límite de la exclusiva** → con exactamente tantos hijos
  como lugares, un error de comparación deja la generación un individuo corta o
  mete un padre de más → verificación 7.
- **Evaluar la aptitud dentro de la estrategia** → se renderiza en un lugar que
  no corresponde y se duplica trabajo que ya hizo el motor → esta fase asume que
  todo llega evaluado.
- **Asumir que la cantidad de hijos siempre es igual al tamaño de la población**
  → la exclusiva funciona con la configuración por defecto y se rompe apenas se
  cambia la cantidad de padres seleccionados → las dos ramas tienen que estar
  implementadas y probadas.

---

## 10. Cierre de la fase

- [ ] Todos los archivos de la sección 2 existen y se importan sin error
- [ ] Todas las verificaciones de la sección 8 pasan
- [ ] `docs/resumenes/FASE_07_RESUMEN.md` está escrito
- [ ] No se tocó ningún archivo fuera de la lista
- [ ] El agente no commiteó ni pusheó nada
