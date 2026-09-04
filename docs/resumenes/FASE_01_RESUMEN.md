# Resumen Fase 01 — Genes: las cinco figuras

---

## Qué hace esta fase

Antes de esta fase el repositorio sabía leer una configuración y una línea de
comandos, pero no existía nada del problema. Ahora existe el **gen**: la figura.
Hay una interfaz común y cinco figuras que la implementan (triángulo,
cuadrilátero, pentágono, óvalo e imagen PNG), intercambiables entre sí. Cada una
sabe nacer al azar dentro de su dominio, mutarse sin salirse de él, copiarse,
dibujarse sobre un lienzo mezclando su transparencia con lo que ya está pintado,
y decir cuáles son sus parámetros, cómo se llaman y entre qué valores se mueve
cada uno.

Todavía no hay imagen renderizada, ni individuo, ni fitness. Lo que sí hay es la
garantía que el resto del motor necesita: **ningún operador puede sacar un
parámetro de su rango**, porque el recorte vive adentro de la figura y no en
quien la muta. Se puede crear una figura al azar, mutarla diez mil veces
seguidas y comprobar que sigue siendo dibujable.

Las cinco figuras no repiten código. Se agrupan en dos familias según cómo están
parametrizadas: la de polígonos (N vértices más color) y la elipsoidal (centro,
dos radios, rotación y color). La regla de mutación, el dominio y el recorte se
escriben una sola vez por familia. Los cinco archivos concretos sólo dicen
cuántos vértices tienen, o cómo se dibujan.

---

## Archivos

| Archivo | Qué hace |
|---|---|
| `src/figuras/__init__.py` | Vacío. Marca `figuras` como paquete de Python |
| `src/figuras/base.py` | La interfaz `Figura`: nueve métodos abstractos y nada más |
| `src/figuras/familias.py` | Las dos familias, `Poligono` y `FiguraElipsoidal`, con toda la lógica de creación, mutación, recorte y composición |
| `src/figuras/triangulo.py` | `Triangulo`: polígono de 3 vértices, 10 parámetros |
| `src/figuras/cuadrilatero.py` | `Cuadrilatero`: polígono de 4 vértices, 12 parámetros |
| `src/figuras/pentagono.py` | `Pentagono`: polígono de 5 vértices, 14 parámetros |
| `src/figuras/ovalo.py` | `Ovalo`: elipse rellena rotada, 9 parámetros |
| `src/figuras/imagen_png.py` | `ImagenPng`: overlay PNG reescalado, teñido y rotado, 9 parámetros |

---

## Archivo por archivo

### `src/figuras/base.py`

Existe para que el resto del motor trabaje con figuras sin saber de qué tipo son.
El renderizador de la fase 02 sólo llama a `dibujar`; la mutación de la fase 06
sólo llama a `mutar`; la cruza de la fase 05 sólo llama a `copiar`; la diversidad
de la fase 03 y los CSV de la fase 09 sólo llaman a `parametros`,
`nombres_parametros` y `rangos`. Ninguno de esos módulos menciona nunca un
triángulo. Gracias a eso, agregar un sexto tipo de figura no obliga a tocar
ninguna otra fase. No calcula nada: es sólo el contrato.

| Método | Recibe | Devuelve | Qué hace |
|---|---|---|---|
| `aleatoria` (de clase) | azar, config, ancho, alto | Una figura | La crea con todos sus parámetros al azar dentro del dominio válido |
| `mutar` | azar, config, ancho, alto | Una figura nueva | Muta los parámetros sin tocar la figura original |
| `copiar` | — | Una figura nueva | Copia independiente |
| `dibujar` | destino, recursos | Nada | Se pinta sobre el destino componiendo su color con lo ya dibujado |
| `parametros` | — | Tupla de valores | El genotipo de la figura, en orden fijo |
| `centro` | — | Par de coordenadas | El centro geométrico |
| `con_color` | rojo, verde, azul | Una figura nueva | Copia con otro color, misma geometría y mismo alfa |
| `nombres_parametros` (de clase) | — | Tupla de nombres | Mismo orden que `parametros` |
| `rangos` (de clase) | config, ancho, alto | Tupla de pares mínimo y máximo | Mismo orden que `parametros` |

Los métodos que reciben cosas las reciben siempre en el mismo orden: primero el
generador de azar, después la configuración, después el ancho y el alto. `rangos`
sigue ese orden salteando el generador, que no usa.

Tres reglas que valen para las cinco figuras y que, si alguien las rompe, rompen
una fase posterior:

- **`mutar`, `copiar` y `con_color` nunca modifican la figura sobre la que se
  llaman.** Si mutaran en el lugar, el padre cambiaría cuando muta el hijo y el
  caché de fitness del padre (fase 03) quedaría mintiendo.
- **`parametros`, `nombres_parametros` y `rangos` tienen el mismo largo y el
  mismo orden.** La diversidad de la fase 03 recorre los tres en paralelo.
- **El generador de azar llega siempre por parámetro.** Ninguna figura crea el
  suyo ni usa `random` de la biblioteca estándar ni el generador global de numpy:
  eso rompería la reproducibilidad por semilla, que es lo que permite comparar
  dos métodos sabiendo que la diferencia no vino del azar.

---

### `src/figuras/familias.py`

Es el archivo donde están las cuentas. Existe porque las cinco figuras se agrupan
en dos familias, y sin él la regla de mutación y recorte de los polígonos estaría
escrita tres veces y la de la familia elipsoidal dos: corregir un error en una
copia dejaría las otras mal. Poniéndolo en la interfaz se mezclaría el contrato
con las cuentas, y poniéndolo en un archivo concreto el cuadrilátero tendría que
importar del triángulo. Acá los cinco archivos concretos importan de un solo
lugar, y ninguno importa de otro concreto.

#### `Poligono` — triángulo, cuadrilátero y pentágono

`2N` parámetros de geometría (las coordenadas de los N vértices, intercaladas
`x0, y0, x1, y1, ...`) más los cuatro canales de color. Guarda dos tuplas: una de
coordenadas en punto flotante y otra de cuatro enteros.

| Método | Recibe | Devuelve | Qué hace |
|---|---|---|---|
| `aleatoria` | azar, config, ancho, alto | Un polígono | Muestrea cada coordenada y cada canal uniformemente en su rango |
| `mutar` | azar, config, ancho, alto | Un polígono nuevo | Suma un delta a los parámetros que mutan y recorta el resultado |
| `copiar` | — | Un polígono nuevo | Instancia nueva con los mismos parámetros |
| `dibujar` | destino, recursos | Nada | Pinta el polígono relleno mezclando su alfa con el destino |
| `parametros` | — | `2N + 4` valores | Coordenadas y después color |
| `centro` | — | Par de coordenadas | El promedio de los N vértices |
| `con_color` | rojo, verde, azul | Un polígono nuevo | Misma geometría, mismo alfa, otro color |
| `nombres_parametros` | — | `2N + 4` nombres | `x0, y0, ... , rojo, verde, azul, alfa` |
| `rangos` | config, ancho, alto | `2N + 4` pares | Los extremos de cada parámetro |
| `_limites` | config, ancho, alto | Dos vectores | Los mínimos y los máximos, que usan a la vez el muestreo, el recorte y `rangos` |

**El dominio.** Cada coordenada horizontal va de `-max_coord_overflow` a
`ancho + max_coord_overflow`, cada vertical lo mismo con el alto, y cada canal de
color de 0 a 255. Ese margen de desborde existe para que una figura pueda quedar
parcialmente afuera y cubrir un borde con un solo vértice adentro, en lugar de
estar obligada a tener los tres vértices dentro de la imagen.

**`mutar`.** Se sortea, para cada uno de los `2N + 4` parámetros por separado, si
muta o no con probabilidad `intra_gene_Pm`. Al que muta se le suma un delta
uniforme en `[-max, +max]` (`max_coord_delta` para geometría, `max_color_delta`
para color) y recién ahí el resultado se recorta a los extremos de su rango. El
orden importa: **primero sumar y después recortar**. Si se recortara antes de
sumar, el valor se escaparía del rango. No hay envoltura: un vértice que se pasa
del borde derecho se queda en el borde derecho, no reaparece por la izquierda,
porque eso sería un salto enorme de fenotipo ante un cambio mínimo de genotipo.

La mutación suma un delta en lugar de reasignar el parámetro al azar porque un
delta chico mantiene el fitness localmente suave: una figura bien ubicada se
ajusta en vez de destruirse. Y el delta es simétrico alrededor de cero, así que
la mutación no empuja en ninguna dirección; el único lugar donde empuja es el
borde, hacia adentro, que es lo que se quiere.

Los tres sorteos de una mutación (la máscara de qué muta, los deltas de
geometría, los deltas de color) son tres llamadas vectorizadas al generador, no
`2N + 4` llamadas sueltas. Con cien genes por individuo y cien individuos por
generación esa diferencia se paga en cada mutación. **La cantidad de números que
se le piden al generador es fija y no depende de cuántos parámetros terminen
mutando**: si alguien la hace variable, dos corridas con la misma semilla dejan
de dar lo mismo.

**`dibujar`.** Pinta el polígono directamente sobre el destino con mezcla de
transparencia, sin crear ninguna capa del tamaño de la imagen. Una capa por
figura significaría una composición de imagen entera por gen, y el renderizado ya
es lo más caro del motor. **El destino tiene que ser una imagen de Pillow en modo
RGB**: es el único modo en el que la biblioteca mezcla el alfa al dibujar. Sobre
un destino con canal alfa, el mismo llamado pisa el píxel en vez de componerlo y
las figuras translúcidas dejan de serlo, sin dar ningún error.

#### `FiguraElipsoidal` — óvalo e imagen PNG

Nueve parámetros: `x`, `y`, `radio_x`, `radio_y`, `rotacion` y los cuatro canales
de color. Mismos métodos que `Poligono`, más dos auxiliares de dibujado. No
implementa `dibujar`: eso es lo único que distingue al óvalo del PNG y vive en
cada archivo concreto.

| Método | Recibe | Devuelve | Qué hace |
|---|---|---|---|
| `aleatoria` | azar, config, ancho, alto | Una figura | Muestrea los nueve parámetros en su rango |
| `mutar` | azar, config, ancho, alto | Una figura nueva | Delta y recorte, con la rotación envuelta en vez de recortada |
| `centro` | — | Par de coordenadas | El centro de la elipse, que ya es un parámetro |
| `_caja` | — | Ancho y alto en píxeles | El tamaño de la caja contenedora, el doble de cada radio |
| `_componer` | destino, capa | Nada | Rota la capa auxiliar y la pega centrada usando su alfa como máscara |

**El dominio.** El centro va de 0 al ancho y de 0 al alto: a diferencia de los
polígonos, **el óvalo no usa `max_coord_overflow`** y su centro se queda siempre
adentro. Los dos radios van de 1 a la mitad del lado mayor del lienzo. El mínimo
de 1 evita el radio nulo o negativo, que rompe el dibujado. El máximo acota
cuánto puede abarcar una sola figura, para que ninguna se convierta en un fondo
de color que tape todo lo que se dibujó antes. La rotación va de 0 a 1, donde 0
es sin rotar y 1 es una vuelta completa; al dibujar se multiplica por 360.

**La rotación se envuelve, no se recorta.** Es la única excepción a la regla del
recorte estricto, y es porque es un parámetro cíclico: 0.99 y 0.01 describen
prácticamente la misma figura, así que un valor que se pasa de un extremo tiene
que volver a entrar por el otro. Recortarla pondría dos paredes donde la mutación
se frenaría sin ningún motivo geométrico. El argumento que justifica el recorte
en las coordenadas no aplica acá, porque allá los dos extremos del rango sí son
puntos lejanos entre sí. Se envuelve con el operador de módulo de Python, que
devuelve siempre un valor no negativo: con `fmod`, que conserva el signo, una
rotación apenas negativa quedaría fuera de rango sin que nada fallara.

El período es una vuelta entera y no media, aunque una elipse rotada media vuelta
sea idéntica a sí misma, porque la figura PNG comparte esta familia y una imagen
rotada media vuelta no es la misma imagen.

**Esto tiene un costo conocido y aceptado.** La métrica de diversidad de la fase
03 divide el desvío estándar de cada parámetro por el ancho de su rango. Con la
rotación envuelta, una población concentrada cerca de cero va a tener valores
cerca de 0 y valores cerca de 1, que están lejos numéricamente aunque describan
figuras casi iguales, y el desvío de ese parámetro va a salir más alto que la
diversidad real. Es uno de nueve parámetros y sólo en dos de los cinco tipos de
figura, así que se acepta, pero hay que tenerlo presente al leer la curva de
diversidad de una corrida con óvalos o con PNG.

---

### `src/figuras/triangulo.py`, `src/figuras/cuadrilatero.py` y `src/figuras/pentagono.py`

Los tres archivos son iguales y tienen tres líneas útiles: heredan de `Poligono`,
declaran `__slots__` vacío y declaran cuántos vértices tienen (3, 4 y 5). De ahí
salen solos su cantidad de parámetros (10, 12 y 14), sus nombres y sus rangos.

Existen como archivos separados, y no como una sola clase con la cantidad de
vértices en la configuración, porque `gene_type` elige un **tipo** de figura y la
fase 08 traduce ese nombre a una clase concreta. Tener tres clases hace que esa
tabla sea directa y que agregar un hexágono sea un archivo nuevo de tres líneas,
sin tocar nada más.

Cada uno declara su propio `__slots__` vacío. Si sólo lo declarara la clase base,
las hijas crearían igual su diccionario de instancia y se perdería el ahorro de
memoria que pide `docs/contexto.md`: con cien genes por individuo y cien
individuos, son diez mil objetos vivos por generación.

---

### `src/figuras/ovalo.py`

La elipse rellena. Hereda todo de `FiguraElipsoidal` y sólo define `dibujar`.

Existe separado del PNG porque el dibujado es lo único que los distingue, y son
dos formas de dibujar completamente distintas: una genera la figura, la otra
transforma una imagen que ya existe.

**`dibujar`.** Pillow no dibuja elipses rotadas. Entonces la elipse se dibuja sin
rotar en una capa auxiliar del tamaño de su caja contenedora, esa capa se rota, y
recién ahí se pega sobre el destino usando su propio alfa como máscara, que es lo
que hace que se componga con lo que ya estaba pintado.

**Esa capa no es necesariamente chica.** La caja mide el doble de cada radio y el
radio máximo es medio lado mayor del lienzo, así que una elipse grande llega a
tener una capa tan grande como el lado mayor de la imagen, y después de rotarla
con expansión, bastante más. O sea que el costo de dibujar un óvalo crece con el
tamaño de la figura, y lo mismo vale para la imagen PNG, que usa el mismo
mecanismo. **Los polígonos no pagan nada de esto**, porque pintan directo sobre
el destino sin capa intermedia. Es una diferencia de costo entre los tipos de
gen, no entre implementaciones mejores y peores, y hay que tenerla en cuenta al
comparar el tiempo por generación de las cinco figuras en la fase 12.

Dos detalles del dibujado que no se leen del código y que conviene no tocar sin
entenderlos:

- **La capa auxiliar se crea con el color de la figura y alfa cero**, no con
  negro transparente. Al rotar, Pillow interpola los píxeles del borde; si el
  fondo de la capa fuera negro, esa interpolación mezclaría el color de la figura
  con negro y **todas las elipses aparecerían con un halo oscuro en el borde**, un
  artefacto que después nadie habría sabido de dónde salía. Creando la capa del
  color de la figura, lo único que interpola es el alfa.
- **La capa se rota con expansión.** Sin eso, la caja de destino de la rotación
  seguiría siendo la caja original y la elipse rotada quedaría recortada en las
  esquinas.

---

### `src/figuras/imagen_png.py`

El overlay externo: una imagen PNG que se usa como figura. Misma geometría, mismo
dominio y misma mutación que el óvalo; sólo cambia el dibujado.

Existe porque es uno de los cinco tipos de gen que pide la consigna, y es el
único cuyo fenotipo no se genera sino que se lee de un archivo. Eso obliga a una
regla: **la figura nunca abre el archivo**. El PNG lo lee el renderizador de la
fase 02, una sola vez por corrida, y llega ya cargado en el diccionario de
recursos bajo la clave `overlay`. Si cada gen leyera el disco, una generación de
cien individuos con cien genes haría diez mil lecturas.

**`dibujar`.** Toma el overlay de los recursos, lo reescala al doble de cada
radio, lo multiplica canal por canal por el color de la figura y después lo rota
y lo compone igual que el óvalo. Esa multiplicación hace las dos cosas a la vez:
el color tiñe la imagen y el alfa de la figura multiplica al alfa propio del PNG,
así que un PNG con zonas transparentes las conserva. Se hace con una
multiplicación de imágenes de Pillow, que corre en C, y no píxel por píxel.

**El overlay tiene que llegar en modo RGBA.** La multiplicación exige que las dos
imágenes tengan el mismo modo y el mismo tamaño; si la fase 02 lo carga en RGB,
esto falla.

**El tinte multiplicativo sólo puede oscurecer, nunca aclarar**: cada canal se
multiplica por un valor entre 0 y 1. Como los colores nacen muestreados
uniformemente, el factor promedio es la mitad, así que los overlays van a tender
a salir más oscuros que la imagen original. Queda así a propósito, es lo que pide
la consigna cuando dice que el color tiñe, pero si en la fase 12 las corridas con
`gene_type` en `png` salen sistemáticamente oscuras, la causa es esta y no el
motor.

---

## Cómo comprobar que anda

Las doce verificaciones de la sección 8 del documento de la fase pasan, más cinco
extra de dibujado del óvalo y del PNG. La suite formal es de la fase 11; mientras
tanto, esto comprueba lo esencial desde la raíz del repositorio:

```bash
python -c "
import numpy as np
from PIL import Image
from src.figuras.triangulo import Triangulo
from src.figuras.ovalo import Ovalo

config = {'max_coord_overflow': 10.0, 'max_coord_delta': 15.0, 'max_color_delta': 25,
          'max_radius_delta': 10.0, 'max_rotation_delta': 0.05, 'intra_gene_Pm': 1.0}
azar = np.random.default_rng(42)

figura = Triangulo.aleatoria(azar, config, 200, 200)
for _ in range(10000):
    figura = figura.mutar(azar, config, 200, 200)
rangos = Triangulo.rangos(config, 200, 200)
print('dominio:', all(a <= v <= b for v, (a, b) in zip(figura.parametros(), rangos)))

ovalo = Ovalo.aleatoria(azar, config, 200, 200)
for _ in range(10000):
    ovalo = ovalo.mutar(azar, config, 200, 200)
x, y, radio_x, radio_y, rotacion = ovalo.parametros()[:5]
print('rotacion y radios:', 0.0 <= rotacion <= 1.0 and radio_x >= 1.0 and radio_y >= 1.0)

lienzo = Image.new('RGB', (100, 100), (255, 255, 255))
Triangulo((10., 10., 90., 10., 50., 90.), (255, 0, 0, 128)).dibujar(lienzo, {})
print('translucido:', lienzo.getpixel((50, 40)), 'fondo:', lienzo.getpixel((2, 95)))
"
```

Tienen que salir las dos primeras líneas en `True`, el píxel de adentro rosado
—`(255, 127, 127)` o parecido, nunca `(255, 0, 0)`— y el de afuera blanco. Si el
de adentro sale rojo puro, el destino no estaba en modo RGB y la mezcla de alfa
no ocurrió.

---

## Decisiones y pendientes

**Decisiones**

- **La lógica compartida vive en `familias.py`.** En la interfaz mezclaría
  contrato con cuentas; en un archivo concreto obligaría al cuadrilátero a
  importar del triángulo.
- **Las coordenadas, los radios y la rotación son flotantes; los cuatro canales
  de color son enteros.** El delta de color se sortea directamente como entero,
  así no hay que decidir cómo redondear los empates. Si `max_color_delta` viniera
  con decimales, se trunca.
- **El recorte vive adentro de la figura, no en quien la muta.** Los cuatro
  métodos de mutación de la fase 06 eligen a quién mutar y nada más: no conocen
  los parámetros de ningún tipo de figura.
- **`rangos` y el recorte salen de la misma tabla.** El muestreo inicial, el
  recorte de la mutación y el rango que la figura reporta a la fase 03 salen del
  mismo lugar, así que la generación 0 y cualquier individuo mutado viven
  exactamente en el mismo espacio de búsqueda y no pueden desincronizarse.
- **El destino de dibujado llega en modo RGB y el overlay en RGBA**, los dos de
  la fase 02. Están anotados en el documento de esa fase.

**Optimización disponible, deliberadamente no aprovechada**

Las figuras son de hecho inmutables: los parámetros se guardan en tuplas y
`mutar`, `copiar` y `con_color` siempre construyen una instancia nueva. Nadie
puede modificar una figura existente. Eso significa que **compartir la misma
figura entre dos individuos sería seguro** y que la cruza de la fase 05 podría no
copiar nada, ahorrándose una copia por gen y por hijo en cada generación.

No se aprovecha ahora porque la fase 05 ya está escrita y su verificación 3
comprueba exactamente lo contrario: que ningún hijo comparta un objeto con su
padre. Para aprovecharlo habría que, en este orden: cambiar esa verificación;
sacar las copias de los cuatro métodos de cruza y de la copia profunda del
individuo de la fase 03, que pasarían a compartir referencias; y dejar escrito
como invariante que ninguna figura se modifica en el lugar, porque a partir de
ahí el aislamiento entre individuos depende de eso y no de la copia. No conviene
hacerlo hasta que la fase 12 muestre que la copia de genes pesa en el perfil de
tiempos: hoy el costo dominante es el renderizado.

**Pendientes**

- **Transparencia mínima.** Con el alfa uniforme en todo su rango, una parte de
  las figuras nace casi invisible y ocupa un locus sin aportar fenotipo. Se
  podría acotar el mínimo; conviene medirlo en la fase 12 antes de tocarlo.
- **`resources/overlay.png` no existe todavía.** `config/conf.json` ya lo nombra,
  así que una corrida con `gene_type` en `png` va a fallar al cargar los recursos
  hasta que alguien ponga el archivo.
