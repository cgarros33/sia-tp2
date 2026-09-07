# Resumen Fase 13 — Presentación y conclusiones

---

## Qué hace esta fase

Es la salida del trabajo hacia afuera: las 33 diapositivas con las que se defiende
el TP. Lo que tiene de particular es que **la presentación no se arma a mano, se
genera con código**. `docs/presentacion/generar_presentacion.py` la construye
entera y toma los gráficos y los GIF directamente de `results/analysis/`, que es
lo que deja la fase 12.

Esa decisión tiene una consecuencia práctica que vale más que la comodidad: si
alguien vuelve a correr los experimentos con otra semilla, otra imagen o más
generaciones, la presentación se regenera con los resultados nuevos en tres
segundos y ninguna diapositiva queda mostrando un gráfico viejo. Con un `.pptx`
editado a mano, cada vez que cambia un experimento hay que acordarse de pegar de
nuevo cada imagen, y tarde o temprano una queda sin actualizar.

El recorrido de las diapositivas sigue el hilo del trabajo: el problema, el
modelo genético, y después cinco etapas que van fijando una decisión por vez
(inicialización, selección, cruza, mutación, supervivencia y figura). Cada etapa
tiene una diapositiva de gráficos cuantitativos y otra de reconstrucción visual
con los GIF de cada variante, para que se vea el efecto además de medirlo.

---

## Archivos

| Archivo | Qué hace |
|---|---|
| `docs/presentacion/generar_presentacion.py` | Construye el `.pptx` completo: el sistema visual, las 33 diapositivas y el ajuste final de composición |
| `docs/presentacion/presentacion_tp2.pptx` | La presentación generada, lista para abrir o subir a Google Slides |

---

## Archivo por archivo

### `docs/presentacion/generar_presentacion.py`

Un solo módulo, sin estado, que se corre y deja el archivo. Está dividido en tres
capas: las constantes de color y medida, un puñado de funciones que arman piezas
reutilizables, y `crear_presentacion`, que es la lista de las 33 diapositivas.

**Las piezas reutilizables:**

| Función | Recibe | Devuelve | Qué hace |
|---|---|---|---|
| `crear_slide_base(prs, titulo, subtitulo)` | La presentación y los textos de cabecera | La diapositiva | Arma el fondo, la barra de acento, el título, el subtítulo y la línea divisoria |
| `agregar_card(slide, left, top, width, height, ...)` | Posición y tamaño | La tarjeta | Agrega el rectángulo redondeado que agrupa un bloque de contenido |
| `agregar_imagen_segura(slide, ruta, left, top, ...)` | La ruta de la imagen | La forma insertada | Inserta la imagen, convierte WebP a PNG, y si el archivo no existe deja un recuadro rojo diciendo cuál falta en vez de romper |
| `agregar_bullet_points(tf, puntos, font_size)` | El marco de texto y la lista | Nada | Escribe las viñetas con sangría francesa |

**El ajuste de composición.** Es lo que arregla el problema que tenía la
presentación: cada tarjeta se declaraba con una altura fija, elegida a ojo, y el
contenido casi nunca la llenaba. El resultado eran diapositivas con la mitad de
abajo en blanco. Ahora, después de armar las 33 diapositivas y antes de guardar,
`ajustar_composicion` recorre todo y lo acomoda:

| Función | Qué hace |
|---|---|
| `ajustar_composicion(prs)` | Recorre las diapositivas y aplica lo que corresponda a cada una |
| `_ajustar_tarjetas(contenido)` | Recorta cada tarjeta hasta la altura de lo que contiene y empareja las alturas de las tarjetas de una misma fila |
| `_alto_efectivo(forma)` | Devuelve lo que la forma ocupa de verdad |
| `_alto_del_texto(forma)` | Mide cuánto ocupa el texto de una caja |
| `_centrar_bloque(contenido)` | Baja el bloque para que quede centrado en la banda libre |
| `_centrar_portada(slide)` | Centra verticalmente el texto de las diapositivas a sangre |
| `_agregar_pie(slide, numero, total)` | Numera la diapositiva y deja la referencia del trabajo al pie |

**`_alto_del_texto`** — es la parte que no se lee del código. Una caja de texto
declara la altura que le dieron al crearla, no la que ocupa el texto que tiene
adentro: una caja de 4.7 pulgadas con tres renglones sigue midiendo 4.7. Para
recortar la tarjeta hace falta saber cuánto ocupa el texto de verdad, así que la
función lo mide: carga Arial en el cuerpo de cada párrafo, va acumulando palabras
hasta pasarse del ancho útil de la caja para contar en cuántas líneas cae, y suma
las alturas de línea más los espacios entre párrafos. Al total le agrega un 6 %,
porque la medición de la fuente y lo que termina componiendo PowerPoint no
coinciden exactamente y quedarse corto significa cortar el texto.

**Por qué el ajuste va al final y no en cada diapositiva.** Las 33 diapositivas
se escriben con posiciones explícitas, que es lo más simple de leer y de tocar.
Si además cada una tuviera que calcular su propia altura, el archivo se volvería
ilegible. Separando las dos cosas, agregar una diapositiva nueva sigue siendo
poner tres cajas con sus coordenadas, y el ajuste la acomoda sola.

**El sistema visual.** Fondo gris muy claro, tarjetas blancas con borde fino y
sin sombra, azul marino para los títulos, gris para el texto, y un azul de acento
que aparece en la barra vertical junto al título y en la primera serie de todos
los gráficos. Las diapositivas de apertura y de cierre invierten el esquema:
fondo azul marino y texto blanco.

---

## Cómo comprobar que anda

```bash
python analyze.py
python docs/presentacion/generar_presentacion.py
```

El primer comando tarda unos tres minutos y deja los gráficos en
`results/analysis/`. El segundo tarda segundos y reescribe
`docs/presentacion/presentacion_tp2.pptx`.

Tres cosas para mirar al abrir el archivo:

1. **Ninguna diapositiva tiene un recuadro rojo** que diga "Archivo no
   encontrado". Si aparece alguno, falta correr `analyze.py` o falló el
   experimento que produce esa imagen.
2. **Ninguna tarjeta corta el texto** por abajo ni deja media diapositiva vacía.
3. Las 33 diapositivas están numeradas al pie, salvo la portada y el cierre.

---

## Decisiones y pendientes

**Decisiones**

- **La presentación se genera con código y no se edita a mano.** Cualquier
  cambio hecho directamente sobre el `.pptx` se pierde en la próxima generación:
  hay que tocar el generador. A cambio, los gráficos nunca quedan
  desactualizados respecto de los experimentos.
- **El estilo de los gráficos no vive acá.** Está en `configurar_estilo_graficos`
  de `analyze.py`, como parámetros globales de matplotlib. Es el único lugar
  donde se define la tipografía, la paleta y la grilla de las 18 figuras, así que
  cambiar el look de todos los gráficos es cambiar un diccionario.
- **El título de cada figura queda chico y gris.** La diapositiva ya pone su
  propio título arriba de la tarjeta; si los dos compiten se leen como repetidos.
  Se mantiene el de la figura, en tono menor, para que el PNG siga siendo legible
  fuera de la presentación.
- **Si falta una imagen, no se rompe.** El generador deja un recuadro que dice
  qué archivo faltó. Es a propósito: permite armar la presentación con los
  experimentos a medio correr y ver qué queda pendiente.
- **La portada muestra la imagen objetivo.** Es el problema del trabajo en una
  imagen, y evita la portada de puro texto sobre fondo liso.

**Pendientes**

- **Faltan los nombres del grupo en la portada.** Es lo único que hay que
  agregar a mano antes de presentar, y va en la diapositiva 1 del generador.
- **Los números que se citan en las conclusiones salen de una corrida
  concreta.** Frases como "acelera 5x la convergencia temprana" están escritas en
  el texto de la diapositiva, no calculadas desde los CSV. Si se vuelven a correr
  los experimentos con otros parámetros, hay que revisarlas a mano.
- **Los GIF no se reproducen en PowerPoint en modo edición.** Se ven como imagen
  fija hasta que se pasa a presentación. En Google Slides se animan directamente.
