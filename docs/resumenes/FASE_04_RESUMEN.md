# Resumen Fase 04 — Selección

---

## Qué hace esta fase

Existen los siete métodos de selección que pide la consigna, todos
intercambiables entre sí. Cada uno recibe una lista de individuos ya evaluados y
devuelve la cantidad pedida de elegidos según su criterio. Es lo que fija la
presión de selección del motor: cuánto se favorece a los mejores contra cuánta
variedad se conserva. Todos comparten la misma firma, así que el motor los cambia
leyendo un campo de la configuración y la experimentación los compara sin tocar
código.

---

## Archivos

| Archivo | Qué hace |
|---|---|
| `src/seleccion/__init__.py` | Vacío |
| `src/seleccion/comun.py` | Lee las aptitudes, ordena y sortea sobre intervalos acumulados |
| `src/seleccion/elite.py` | Los mejores, repetidos según su posición |
| `src/seleccion/ruleta.py` | Probabilidad proporcional al fitness |
| `src/seleccion/universal.py` | Ruleta con los sorteos repartidos parejo |
| `src/seleccion/boltzmann.py` | Pseudo-aptitud exponencial con temperatura |
| `src/seleccion/torneo_deterministico.py` | Grupos al azar donde gana el mejor |
| `src/seleccion/torneo_probabilistico.py` | Duelos con umbral |
| `src/seleccion/ranking.py` | Peso por posición, no por valor |

---

## La firma que comparten los siete

```
seleccionar(individuos, cantidad, azar, config) -> lista de individuos
```

**Invariantes de los siete:**

- Devuelven exactamente la cantidad pedida.
- **Se permite repetición.** Un mismo individuo puede salir varias veces, y tiene
  que poder: sin repetición no hay presión de selección, porque los mejores no se
  reproducirían más que los peores.
- Devuelven **referencias**, no copias. Copiar tiraría el fitness cacheado y
  forzaría un renderizado que ya se pagó.
- No modifican la lista recibida ni los individuos.
- Sortean únicamente con el generador que llega por parámetro.
- **No evalúan.** Leen `fitness_cacheado` y cortan si alguno vale `None`.

---

## Archivo por archivo

### `src/seleccion/comun.py`

Lo que cuatro de los siete métodos hacen igual, en un solo lugar.

| Función | Recibe | Devuelve | Qué hace |
|---|---|---|---|
| `aptitudes(individuos)` | Los individuos | El vector de fitness | Lee el fitness cacheado de cada uno, una sola vez |
| `orden_por_fitness(valores)` | El vector de fitness | Los índices ordenados | De mayor a menor, estable ante empates |
| `seleccionar_por_pesos(individuos, pesos, numeros)` | Los individuos, sus pesos y los números al azar | Los elegidos | Normaliza, acumula y busca el intervalo de cada número |

**`aptitudes(...)`** — se llama una vez al principio de cada método y no dentro
del bucle. Además es lo que hace cumplir la invariante de que la selección no
evalúa: si algún individuo no tiene fitness cacheado corta con
`ErrorDeSeleccion`, en vez de disparar un renderizado por comparación.

**`seleccionar_por_pesos(...)`** — normaliza los pesos para que sumen uno, arma
las probabilidades acumuladas y, para cada número al azar, elige al individuo
cuyo intervalo lo contiene: el primero cuyo acumulado es mayor o igual al número.
La búsqueda es binaria sobre el acumulado, no un recorrido lineal.

Recibe los números **ya sorteados** en vez de sortearlos adentro porque es lo
único en lo que la ruleta y la universal se diferencian: la primera tira uno
independiente por selección, la segunda tira uno solo y deriva el resto. Todo lo
que sigue es idéntico.

**Regla que si alguien la borra rompe algo.** El índice se recorta al último
intervalo. La suma de las probabilidades acumuladas puede quedar apenas por
debajo de uno por redondeo, y sin el recorte un número sorteado más grande que
ese último acumulado se iría del rango.

---

### `src/seleccion/elite.py`

Ordena de mayor a menor y le da al individuo de la posición `i`, contada desde
cero, una cantidad de repeticiones

```
    n(i) = techo((cantidad_a_seleccionar - i) / cantidad_de_individuos)
```

Recorre las posiciones acumulando repeticiones y corta exactamente en la cantidad
pedida. Es el más agresivo de los siete: pidiendo menos o igual que el tamaño de
la población se queda literalmente con los mejores y descarta al resto; pidiendo
más, los primeros entran varias veces.

La parte entera hacia arriba de un número negativo es cero, así que las
posiciones sobrantes no aportan y no hay que tratarlas aparte.

**Regla que si alguien la borra rompe algo.** El corte final en la cantidad
pedida no es cosmético: los redondeos hacia arriba pueden sumar de más.

---

### `src/seleccion/ruleta.py` y `src/seleccion/universal.py`

La ruleta le da a cada individuo una probabilidad proporcional a su fitness y
sortea un número independiente por cada selección.

La universal usa los mismos intervalos pero sortea **un solo** número y deriva el
resto equiespaciados: al número sorteado se le suma la posición del sorteo y se
divide por la cantidad a seleccionar. Con eso la muestra queda repartida pareja
sobre el rango en vez de amontonarse por azar. Sobre una población de aptitudes
iguales, cada individuo sale exactamente una vez.

---

### `src/seleccion/boltzmann.py`

El peso de cada individuo es

```
    ExpVal(i) = e^(f(i)/T) / promedio sobre la población de e^(f(x)/T)
```

y con esos pesos se sortea como en la ruleta. La temperatura gobierna la presión:
alta acerca los pesos entre sí y la selección tiende al azar, baja amplifica las
diferencias y tiende a la élite.

**`valores_esperados(valores, temperatura)`** — antes de exponenciar le resta a
todas las aptitudes la mayor de ellas. Es lo que evita el desborde: con
temperaturas chicas, `e^(f/T)` se va al infinito, y restando el máximo el
exponente más grande es cero y la exponencial más grande es uno. **No cambia
ninguna selección**, porque multiplica todos los pesos por la misma constante y
la ruleta trabaja con proporciones, así que el factor se cancela al normalizar.
En el cociente con el promedio aparece arriba y abajo, y también se va.

La división por el promedio se calcula aunque la normalización posterior la
cancele, porque es la fórmula que define la consigna y la que hay que poder
mostrar.

---

### `src/seleccion/ranking.py`

Ordena por fitness y le asigna a cada individuo un peso que depende sólo de su
posición, no del valor:

```
    f'(i) = (cantidad_de_individuos - posición) / cantidad_de_individuos
```

**Las posiciones se cuentan desde cero.** Así el mejor recibe peso uno y el peor
recibe uno sobre la cantidad de individuos, que es el peso más chico posible sin
llegar a cero. Numerando desde uno, el peor recibiría peso cero y quedaría
excluido, que es exactamente lo contrario de lo que este método viene a resolver.

Resuelve el mismo problema que el torneo por otro camino, y en este trabajo
resuelve uno muy concreto: las aptitudes de la generación inicial valen alrededor
de 1e-4 y difieren en decimales de esa escala, así que la ruleta reparte
probabilidades casi idénticas y se comporta como un sorteo uniforme. Usando la
posición, la ventaja del primero sobre el último es siempre la misma.

---

### `src/seleccion/torneo_deterministico.py` y `torneo_probabilistico.py`

El determinístico sortea `tournament_size` competidores **sin repetir dentro del
mismo torneo** y se queda con el de mayor fitness. Repite el torneo, de forma
independiente, hasta juntar la cantidad pedida. Sin reposición porque si no un
individuo puede competir contra sí mismo y el tamaño de torneo miente.

El probabilístico enfrenta dos y sortea un número: si es menor que
`tournament_threshold` gana el más apto, si no gana el menos apto. El umbral
gradúa la presión: en uno equivale al torneo determinístico de a dos, en 0,5 es
un volado.

Ninguno de los dos mira el **valor** del fitness, sólo cuál es mayor. Eso los
vuelve inmunes al problema que arruina a la ruleta en este trabajo: aunque las
aptitudes difieran en la quinta cifra decimal, el torneo sigue eligiendo al mejor
de cada grupo.

El grupo sorteado se ordena antes de buscar el máximo para que un empate lo gane
el de menor índice en la lista y no el que salió primero en el sorteo.

---

## Cómo comprobar que anda

```bash
python -c "
import numpy as np
from src.seleccion import elite, ruleta, ranking

class Falso:
    def __init__(self, etiqueta, fitness): self.etiqueta, self.fitness_cacheado = etiqueta, fitness

gente = [Falso(i, f) for i, f in enumerate([0.1, 0.9, 0.5, 0.7, 0.3])]
config = {'tournament_size': 3, 'tournament_threshold': 0.75, 'temperature': 1.0}
print([i.etiqueta for i in elite.seleccionar(gente, 3, np.random.default_rng(42), config)])
print(len(ruleta.seleccionar(gente, 12, np.random.default_rng(42), config)))
print([i.etiqueta for i in ranking.seleccionar(gente, 5, np.random.default_rng(1), config)])
"
```

La primera línea tiene que dar `[1, 3, 2]`: los tres de mayor fitness, en orden.
La segunda tiene que dar `12`, aunque haya sólo cinco individuos, porque la
repetición está permitida. La tercera tiene que dar cinco etiquetas cualesquiera,
y repetir la orden con la misma semilla tiene que dar exactamente la misma lista.

---

## Decisiones y pendientes

**Decisiones**

- **El tamaño de población de las fórmulas de élite y ranking es el largo de la
  lista recibida**, no `population_size`. Son lo mismo cuando el motor selecciona
  padres, pero no cuando la supervivencia aditiva llame con padres más hijos, que
  es una lista más larga. Usar el campo de configuración daría cuentas mal
  hechas justo en el caso menos obvio.
- **El orden es estable ante empates.** Dos individuos con el mismo fitness
  quedan siempre en el mismo orden relativo, que es el que traían. Con un orden
  inestable, dos corridas con la misma semilla podrían diferir.
- **Boltzmann resta el máximo antes de exponenciar**, por el desborde.
- **La rutina de ruleta vive en `comun.py`.** Cuatro de los siete la usan;
  tenerla cuatro veces son cuatro lugares donde corregir el mismo error.

**Pendientes y cosas que las próximas fases tienen que saber**

- **La selección devuelve referencias repetidas, y `Poblacion` las rechaza.** El
  validador de la fase 03 corta si el mismo individuo aparece dos veces por
  referencia, con el mensaje "quien lo reutiliza tiene que copiarlo". Está bien
  que sea así, pero significa que **la fase 07 no puede pasarle directamente a
  `Poblacion` lo que le devuelve un método de selección**: tiene que copiar los
  repetidos. Comprobado: seleccionando 6 de 6 con ruleta salieron 2 repetidos y
  la construcción de la población cortó.
- **Con `temperature` en 1,0 Boltzmann no ejerce ninguna presión.** Medido sobre
  aptitudes en el rango real del problema, 6,5e-5 a 9,7e-5: Boltzmann le da al
  mejor 1,0000 veces la probabilidad uniforme y la ruleta 1,1975. Con aptitudes
  de ese orden, `e^(f/T)` vale ≈1 para todos. La temperatura tiene que ser del
  orden de las aptitudes para que el método haga algo. No se cambió
  `config/conf.json`: ese archivo es de la fase 00.
- **Temperatura variable.** El método se usa habitualmente con una temperatura
  que baja a lo largo de la corrida, para explorar al principio y explotar al
  final. Acá es un valor fijo. Si en la experimentación aparece que conviene
  bajarla, hay que agregar campos de configuración y avisar al grupo.
