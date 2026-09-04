# Fase 04 — Selección

> **Ola:** 3 · **Depende de:** 03 · **Habilita:** 07, 08

---

## 1. Objetivo

Al terminar esta fase existen los siete métodos de selección que pide la
consigna, todos intercambiables entre sí. Dada una lista de individuos ya
evaluados, cualquiera de ellos devuelve la cantidad pedida de individuos elegidos
según su criterio. Es lo que determina la presión de selección del motor: cuánto
se favorece a los mejores frente a cuánta variedad se conserva.

---

## 2. Archivos que produce

| Archivo | Qué es |
|---|---|
| `src/seleccion/__init__.py` | Vacío |
| `src/seleccion/comun.py` | La rutina de ruleta compartida por los métodos que trabajan con pesos |
| `src/seleccion/elite.py` | Selección por élite |
| `src/seleccion/ruleta.py` | Selección proporcional a la aptitud |
| `src/seleccion/universal.py` | Variante de ruleta con muestreo equiespaciado |
| `src/seleccion/boltzmann.py` | Selección con pseudo-aptitud exponencial |
| `src/seleccion/torneo_deterministico.py` | Torneos donde siempre gana el mejor |
| `src/seleccion/torneo_probabilistico.py` | Torneos de a dos con umbral |
| `src/seleccion/ranking.py` | Selección por posición ordinal |

---

## 3. Qué hay que implementar

### La firma común

Los siete métodos exponen exactamente la misma interfaz, para que el motor pueda
intercambiarlos leyendo un campo de configuración.

| Recibe | Devuelve |
|---|---|
| La lista de individuos, cuántos hay que seleccionar, el generador de azar y la configuración | Una lista con exactamente esa cantidad de individuos |

**Invariantes que valen para los siete:**
- Devuelven exactamente la cantidad pedida, ni uno más ni uno menos.
- Se permite repetición: un mismo individuo puede salir seleccionado varias
  veces. Es lo esperado, porque los buenos tienen que reproducirse más.
- No modifican los individuos que reciben ni el orden de la lista original.
- Devuelven referencias a los individuos, no copias. Copiar es responsabilidad de
  la cruza, y copiar acá desperdiciaría el caché de aptitud.
- Usan únicamente el generador de azar que reciben por parámetro.
- Asumen que los individuos ya fueron evaluados. Ninguno dispara un renderizado.

---

### `src/seleccion/comun.py`

Cuatro de los siete métodos terminan haciendo lo mismo: convertir una lista de
pesos en probabilidades y sortear. Ese pedazo vive acá una sola vez.

| Función | Recibe | Devuelve | Qué hace |
|---|---|---|---|
| `seleccionar_por_pesos` | Los individuos, sus pesos, la lista de números al azar entre cero y uno, ya sorteados por quien llama | Los individuos elegidos | Normaliza los pesos, arma los intervalos acumulados y busca a qué intervalo cae cada número |

Recibe los números al azar ya sorteados en vez de sortearlos adentro, porque la
ruleta y la universal se diferencian justamente en cómo los generan: la primera
tira uno independiente por cada selección, la segunda tira uno solo y deriva el
resto equiespaciados. Todo lo que viene después es idéntico.

---

### `src/seleccion/elite.py`

Ordena la población por aptitud de mayor a menor y le asigna a cada uno una
cantidad de repeticiones que depende de su posición en ese orden. La cantidad de
veces que entra el individuo de la posición `i` es la parte entera hacia arriba
de la diferencia entre la cantidad a seleccionar y `i`, dividida por el tamaño de
la población. Se recorren las posiciones en orden y se van agregando
repeticiones hasta juntar la cantidad pedida.

Es el método más agresivo de los siete: si la cantidad a seleccionar es menor o
igual al tamaño de la población, se queda literalmente con los mejores y descarta
al resto.

---

### `src/seleccion/ruleta.py`

A cada individuo le corresponde una probabilidad proporcional a su aptitud. Se
sortean tantos números al azar entre cero y uno como individuos haya que
seleccionar, de forma independiente, y para cada uno se elige el individuo cuyo
intervalo acumulado lo contiene.

---

### `src/seleccion/universal.py`

Misma estructura de intervalos que la ruleta, pero cambia cómo se generan los
números. Se sortea uno solo entre cero y uno, y a partir de él se derivan los
demás equiespaciados: al número sorteado se le suma la posición del sorteo y se
divide todo por la cantidad a seleccionar. Con eso la muestra queda repartida
de forma más pareja sobre el rango, en vez de amontonarse por azar.

---

### `src/seleccion/boltzmann.py`

En lugar de usar la aptitud directamente como peso, la transforma
exponencialmente: el peso de cada individuo es la exponencial de su aptitud
dividida por la temperatura, y eso se divide por el promedio de esa misma
exponencial sobre toda la población. Con esos pesos se sortea igual que en la
ruleta.

La temperatura controla la presión de selección. Con temperatura alta los pesos
se parecen entre sí y la selección se acerca al azar puro; con temperatura baja
las diferencias se amplifican y se parece a la élite.

**Riesgo numérico.** La exponencial de un número grande desborda. Como la aptitud
está acotada entre cero y uno, el problema solo aparece con temperaturas muy
chicas. Restarle a todas las aptitudes la mayor de ellas antes de exponenciar
evita el desborde y no cambia el resultado, porque la ruleta trabaja con
proporciones entre pesos y esa resta es un factor común que se cancela al
normalizar.

---

### `src/seleccion/torneo_deterministico.py`

Se eligen al azar tantos individuos como indique `tournament_size` y gana el de
mayor aptitud. Se repite de forma independiente hasta juntar la cantidad pedida.

A diferencia de la ruleta, no mira el valor de la aptitud sino solo cuál es
mayor. Eso lo hace inmune al problema de las aptitudes casi iguales: cuando todos
los individuos valen aproximadamente lo mismo, la ruleta reparte probabilidades
casi idénticas y se comporta como un sorteo al azar, mientras que el torneo sigue
eligiendo siempre al mejor del grupo.

---

### `src/seleccion/torneo_probabilistico.py`

Se eligen dos individuos al azar y se sortea un número entre cero y uno. Si ese
número es menor que `tournament_threshold`, gana el más apto; si no, gana el
menos apto. Se repite hasta juntar la cantidad pedida.

El umbral gradúa la presión: en uno es equivalente al torneo determinístico de a
dos, y en medio es un sorteo al azar entre los dos competidores.

---

### `src/seleccion/ranking.py`

Ordena la población por aptitud y le asigna a cada individuo un peso que depende
solo de su posición en ese orden, no del valor de su aptitud: la diferencia entre
el tamaño de la población y la posición, dividida por el tamaño de la población.
Con esos pesos se sortea igual que en la ruleta.

Las posiciones se numeran desde cero, de modo que el mejor recibe peso uno y el
peor recibe el peso más chico posible sin llegar a cero. Que el último conserve
alguna probabilidad es justamente el punto del método: nadie queda descartado de
entrada.

Resuelve el mismo problema que el torneo pero por otro camino. Con una población
inicial al azar todos los individuos son igual de malos y sus aptitudes difieren
en decimales, así que la ruleta pierde toda capacidad de discriminar. Al usar la
posición en vez del valor, la ventaja del primero sobre el último es siempre la
misma, sin importar si sus aptitudes difieren en una milésima o en quinientos.

---

## 4. Interfaces de otras fases

**Los individuos** de la fase 03 exponen su aptitud a través del método que la
devuelve cacheada. Los métodos de selección solo necesitan comparar y ordenar por
ese número. No tocan los genes ni saben qué hay adentro del individuo.

**La configuración** de la fase 00 llega ya validada. Las claves que esta fase lee
son `tournament_size`, `tournament_threshold` y `temperature`. Se puede asumir
que el umbral está entre 0.5 y 1, que la temperatura es positiva y que el tamaño
de torneo no supera al de la población.

**El generador de azar** llega por parámetro y es el único de la corrida.

**El tamaño de la población** que aparece en las fórmulas de élite y de ranking es
la cantidad de individuos de la lista recibida, no el campo de configuración. Son
lo mismo cuando el motor selecciona padres, pero no cuando la supervivencia
aditiva de la fase 07 llama a estos métodos con la lista de padres más hijos, que
es más larga.

---

## 5. Decisiones ya tomadas

| Decisión | Motivo |
|---|---|
| Los siete comparten la misma firma | Es lo que permite que el motor los intercambie leyendo un campo de configuración, y que la fase 12 los compare sin tocar código |
| Se devuelven referencias y no copias | El individuo trae su aptitud cacheada; copiarlo la tiraría y forzaría un renderizado |
| Se permite seleccionar al mismo individuo varias veces | Sin repetición no hay presión de selección: los mejores tienen que reproducirse más que los peores |
| La rutina de ruleta vive en un archivo aparte | Cuatro de los siete métodos la usan, y tenerla cuatro veces significa cuatro lugares donde corregir el mismo error |
| Las posiciones del ranking se numeran desde cero | Numerando desde uno, el peor individuo recibe peso cero y queda excluido, que es exactamente lo que el método viene a evitar |
| El tamaño de población de las fórmulas es el largo de la lista recibida | La supervivencia aditiva llama a estos métodos con padres más hijos, y usar el campo de configuración daría cuentas mal hechas |
| Boltzmann resta el máximo antes de exponenciar | Evita el desborde numérico con temperaturas chicas y no cambia el resultado, porque es un factor común que se cancela al normalizar |

---

## 6. Decisiones abiertas

- **Temperatura variable en Boltzmann.** El método se usa habitualmente con una
  temperatura que baja a lo largo de la corrida, para explorar al principio y
  explotar al final. Acá la temperatura es un valor fijo de configuración. Si en
  la fase 12 aparece que conviene bajarla, hay que agregar los campos
  correspondientes y avisar al grupo, porque toca el archivo de configuración.

---

## 7. Checkpoints obligatorios

- `src/seleccion/elite.py` — por la fórmula de repeticiones por posición.
- `src/seleccion/boltzmann.py` — por la transformación exponencial y el manejo
  del desborde numérico.
- `src/seleccion/ranking.py` — por la pseudo-aptitud por posición y la decisión
  de numerar desde cero.
- `src/seleccion/comun.py` junto con `ruleta.py` y `universal.py` — un solo
  checkpoint para los tres, porque comparten la construcción de intervalos
  acumulados y solo se diferencian en cómo se sortean los números.
- `torneo_deterministico.py` y `torneo_probabilistico.py` — un solo checkpoint
  para los dos.

---

## 8. Cómo se verifica

| # | Qué se prueba | Entrada | Resultado esperado |
|---|---|---|---|
| 1 | Cantidad devuelta | Los siete métodos, pidiendo distintas cantidades | Siempre devuelven exactamente lo pedido |
| 2 | No modifican la entrada | Los siete métodos | La lista original conserva su orden y sus individuos |
| 3 | Élite se queda con los mejores | Una población con aptitudes distintas, pidiendo menos individuos que el tamaño de la población | Los seleccionados son exactamente los de mayor aptitud |
| 4 | Los pesos suman uno | Ruleta, universal, Boltzmann y ranking | Las probabilidades normalizadas suman uno |
| 5 | La ruleta favorece a los mejores | Una población donde un individuo tiene aptitud mucho mayor, con muchas selecciones | Ese individuo sale elegido bastante más seguido que el resto |
| 6 | La universal reparte parejo | Una población de aptitudes iguales, seleccionando tantos como individuos hay | Cada individuo sale aproximadamente una vez |
| 7 | El torneo determinístico ignora la magnitud | Dos poblaciones con el mismo orden de aptitudes pero magnitudes muy distintas, con la misma semilla | La selección es idéntica en las dos |
| 8 | El umbral del torneo probabilístico | Umbral en uno, muchas repeticiones | Nunca gana el menos apto |
| 9 | Ranking no excluye al peor | Una población grande, con muchas selecciones | El peor individuo sale elegido alguna vez |
| 10 | Boltzmann con temperatura chica | Temperatura muy baja | No desborda, y la selección se concentra en los mejores |
| 11 | Reproducibilidad | El mismo método dos veces con la misma semilla | La selección es idéntica |
| 12 | No se dispara renderizado | Cualquier método sobre una población ya evaluada | No se renderiza ninguna vez |

---

## 9. Errores probables

- **Usar el tamaño de población de la configuración en vez del largo de la lista
  recibida** → cuando la supervivencia aditiva llama con padres más hijos, las
  fórmulas de élite y ranking dan cuentas mal hechas → se detecta seleccionando
  sobre una lista más larga que `population_size`.
- **Devolver copias de los individuos** → se pierde el caché de aptitud y cada
  generación paga renderizados de más → verificación 12.
- **Numerar las posiciones del ranking desde uno** → el peor individuo recibe
  peso cero y queda excluido, que es lo contrario de lo que el método busca →
  verificación 9.
- **Ordenar de menor a mayor** → la élite se queda con los peores y nadie se da
  cuenta hasta ver que el motor empeora → verificación 3.
- **Comparar aptitudes de individuos no evaluados** → se comparan valores
  vencidos o inexistentes → los métodos asumen población evaluada; evaluar es
  responsabilidad de quien llama.
- **Sortear con el generador global en vez del que llega por parámetro** → se
  rompe la reproducibilidad → verificación 11.
- **Recalcular la aptitud dentro del bucle de selección** → se llama al método que
  devuelve la aptitud una vez por comparación en vez de una vez por individuo →
  conviene leer todas las aptitudes una sola vez al principio.
- **Devolver menos individuos de los pedidos en la élite** → la parte entera hacia
  arriba puede sumar más o menos que la cantidad pedida según los redondeos → hay
  que cortar exactamente en la cantidad pedida.

---

## 10. Cierre de la fase

- [ ] Todos los archivos de la sección 2 existen y se importan sin error
- [ ] Todas las verificaciones de la sección 8 pasan
- [ ] `docs/resumenes/FASE_04_RESUMEN.md` está escrito
- [ ] No se tocó ningún archivo fuera de la lista
- [ ] El agente no commiteó ni pusheó nada
