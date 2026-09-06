# Resumen Fase 02 — Fenotipo: renderizador y fitness

---

## Qué hace esta fase

Antes de esta fase existían las figuras (fase 01) y la configuración (fase 00),
pero no había forma de convertir un conjunto de figuras en una imagen ni de
decir qué tan buena era esa imagen. Ahora sí: dada una lista de figuras se
obtiene la imagen que producen, y dada esa imagen se obtiene un número entre 0 y
1 que dice cuánto se parece a la que queremos imitar. Es el puente entre el
genotipo, que es la tira de números que la cruza y la mutación manipulan, y la
aptitud, que es lo único que la selección sabe comparar. Todavía no hay
individuos ni generaciones: sólo se puede dibujar un conjunto de figuras y
medirle el error.

---

## Archivos

| Archivo | Qué hace |
|---|---|
| `src/renderizador.py` | Carga del disco las imágenes de la corrida y dibuja una lista de figuras sobre el lienzo |
| `src/fitness.py` | Mide la distancia entre el fenotipo y la imagen objetivo y la convierte en aptitud |

---

## Archivo por archivo

### `src/renderizador.py`

Es el único módulo de todo el proyecto que abre archivos de imagen, y el único
que sabe cómo se compone el lienzo. No tiene estado: fuera de la lectura inicial
del disco, todas sus funciones son puras.

| Función | Recibe | Devuelve | Qué hace |
|---|---|---|---|
| `cargar_objetivo(config)` | La configuración | La matriz del objetivo, su ancho y su alto | Abre `file_input`, lo deja opaco, le aplica el multiplicador de resolución |
| `cargar_recursos(config)` | La configuración | Un diccionario | Lee una sola vez lo que las figuras necesitan para dibujarse |
| `renderizar(figuras, ancho, alto, config, recursos)` | La lista de figuras y las dimensiones | La matriz del fenotipo | Dibuja las figuras en orden sobre el lienzo del color de fondo |

**`cargar_objetivo(config)`** — el ancho y el alto que devuelve son los de toda
la corrida: son las dimensiones del lienzo y del dominio contra el que las
figuras recortan sus coordenadas, y no tienen por qué coincidir con las del
archivo original. Hace tres cosas en este orden, que no es intercambiable: abre
la imagen, la aplana contra el color de fondo y recién después la redimensiona.
Redimensionar antes de aplanar interpolaría los píxeles transparentes contra los
opacos y dejaría un halo alrededor de la silueta.

**`_aplanar(imagen, color_de_fondo)`** — si la imagen trae transparencia con al
menos un píxel no opaco, la compone sobre un fondo del color configurado; si no,
la convierte a RGB y listo. El fondo se arma siempre opaco, usando sólo los tres
primeros componentes de `background_color`, porque el lienzo sobre el que se
compara también lo es. Ver la sección de decisiones: esto es un desvío
deliberado del documento de fase.

**`_tiene_transparencia(imagen)`** — no alcanza con mirar el modo de la imagen.
Un PNG con paleta guarda la transparencia en `info` y no en un canal, así que se
chequean las dos cosas. Y tener canal alfa no significa tener píxeles
transparentes: se mira el mínimo del canal, y si está todo opaco no se compone
nada.

**`cargar_recursos(config)`** — devuelve un diccionario vacío salvo que
`gene_type` sea `png`, en cuyo caso trae la imagen de overlay convertida a RGBA.
Existe para que ninguna figura abra archivos: el overlay lo comparten todas las
figuras de todos los individuos de todas las generaciones, así que se lee una
vez por corrida y viaja por parámetro hasta cada dibujado.

**`renderizar(...)`** — crea el lienzo, recorre la lista pidiéndole a cada figura
que se dibuje encima y devuelve el resultado como matriz. No sabe qué tipo de
figura le tocó: sólo usa el método de dibujado de la interfaz de la fase 01. El
orden del recorrido es información genética, porque las figuras son translúcidas
y se apilan: la de la posición cero queda debajo de todas.

**Reglas que si alguien las borra rompen algo.** El lienzo se crea en RGB, sin
canal alfa: es el único modo en el que Pillow compone la transparencia de la
figura en vez de pisar el píxel, y sin él todas las figuras se ven opacas sin
que se lance ningún error. La clave del overlay se importa de
`src/figuras/imagen_png.py` en vez de escribirse a mano, así que un cambio de
nombre allá rompe al importar y no en la primera corrida con genes PNG.

---

### `src/fitness.py`

Convierte una imagen generada en el número que la selección compara.

| Función | Recibe | Devuelve | Qué hace |
|---|---|---|---|
| `calcular_fitness(fenotipo, objetivo)` | Las dos matrices | Un número mayor que 0 y menor o igual a 1 | Mide el error cuadrático medio y lo transforma en aptitud |

**`calcular_fitness(fenotipo, objetivo)`** — la cuenta es

```
    ECM = promedio sobre todos los píxeles y los tres canales de (generado - objetivo)²
    aptitud = 1 / (1 + ECM)
```

El error cuadrático medio y no el absoluto porque penaliza más una zona muy
equivocada que un corrimiento leve repartido por toda la imagen, que es el
comportamiento que se busca. La transformación es necesaria porque el error es
una magnitud a minimizar y la selección maximiza, pero además la ruleta,
Boltzmann, universal y ranking usan la aptitud directamente como peso de una
probabilidad, y un peso negativo o cero rompe el reparto de intervalos. Esta
fórmula vale exactamente 1 cuando las dos imágenes son idénticas, nunca llega a
0, y es estrictamente decreciente en el error, así que menos error es siempre más
aptitud. Su cota inferior es 1/(1+255²) = 1,537e-5, el caso de negro contra
blanco.

Sólo se comparan los tres canales de color: el lienzo es opaco por construcción,
así que el canal de transparencia no aporta información.

**Regla que si alguien la borra rompe algo.** La resta se hace en enteros de 32
bits con signo. En los 8 bits sin signo que traen las dos matrices, una
diferencia negativa da la vuelta y el error queda enorme y al revés; en 16 bits
la diferencia entra, pero su cuadrado llega a 65.025 contra un máximo de 32.767 y
también da la vuelta. Ninguno de los dos casos lanza una excepción.

---

## Cómo comprobar que anda

```bash
python -c "
import numpy as np
from src.config import cargar_config
from src.renderizador import cargar_objetivo, renderizar
from src.fitness import calcular_fitness
from src.figuras.triangulo import Triangulo

config = cargar_config('config/conf.json', {})
objetivo, ancho, alto = cargar_objetivo(config)
azar = np.random.default_rng(config['random_seed'])
figuras = [Triangulo.aleatoria(azar, config, ancho, alto) for _ in range(100)]
print(calcular_fitness(objetivo, objetivo))
print(calcular_fitness(renderizar([], ancho, alto, config, {}), objetivo))
print(calcular_fitness(renderizar(figuras, ancho, alto, config, {}), objetivo))
"
```

Tiene que imprimir `1.0` en la primera línea, porque el objetivo contra sí mismo
es aptitud máxima. Las otras dos tienen que dar números chiquitos y positivos, y
el lienzo vacío tiene que dar **más** que los cien triángulos al azar: sobre esta
imagen objetivo, cien triángulos de colores random son peores que no dibujar
nada.

---

## Decisiones y pendientes

**El objetivo se compone sobre el color de fondo, en vez de descartar el alfa a
secas.** Es un desvío del documento de la fase, que dice sólo "descartá el canal
de transparencia si lo tiene". `resources/bron500.png` tiene 109.205 de sus
168.000 píxeles totalmente transparentes, el 65%, y en ellos el RGB es
prácticamente negro. Descartar el alfa convertía el objetivo en LeBron sobre
fondo negro, así que el motor habría gastado la mayoría de sus cien triángulos
pintando de negro un fondo que sólo es negro por un accidente del archivo. Se
compone únicamente si hay píxeles no opacos, así que una imagen sin
transparencia pasa intacta.

**El filtro de reescalado del objetivo es LANCZOS**, y no el bilineal que usan
las figuras: se paga una sola vez por corrida y da mejor calidad al achicar.

**Las dos matrices salen en enteros de 8 bits sin signo**, que es lo que una
imagen es, y el casteo a 32 bits lo hace `calcular_fitness` al restar. Ver la
regla de la subsección de fitness.

**Formas incompatibles cortan con `ValueError`** en vez de devolver un número.
Sin el chequeo, numpy puede difundir formas distintas en silencio y dar un
resultado que parece válido.

**`cargar_objetivo` y `cargar_recursos` cortan con `ErrorDeImagen`**, definida en
el mismo módulo, con el path en el mensaje. No se reusó `ErrorDeConfiguracion`
para no acoplar los dos módulos; `main.py` va a atrapar las dos en la fase 10.

### Pendientes y cosas que las próximas fases tienen que saber

- **Comparar en un espacio de color perceptual** sigue abierto para la fase 12,
  tal como lo dejó el documento de la fase. Encarece cada evaluación y conviene
  medir primero cuánto cambia el resultado.
- **El `fitness_cutoff` de 0,99 del `conf.json` es inalcanzable.** Equivale a un
  ECM de 0,01, imposible aproximando una foto con cien polígonos. Toda corrida va
  a terminar por `max_generations` o por estancamiento, y conviene saberlo antes
  de leer el motivo de finalización en `resumen.txt`.
- **La `temperature` de 1,0 deja a Boltzmann sin presión selectiva.** Las
  aptitudes del problema viven en el orden de 1e-4, así que e^(f/T) vale ≈1,0001
  para todos y la selección se vuelve azar puro. Medido sobre treinta individuos
  aleatorios: la ruleta común le da al mejor 1,2251 veces la probabilidad
  uniforme, y Boltzmann le da 1,0000. Es un dato para la fase 04, que implementa
  el método, y para la 12, que tiene que barrer ese parámetro. Ninguna de las dos
  cosas se cambió acá: `config/conf.json` lo toca sólo la fase 00.
