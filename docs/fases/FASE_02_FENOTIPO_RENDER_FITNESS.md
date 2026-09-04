# Fase 02 — Fenotipo: renderizador y fitness

> **Ola:** 2 · **Depende de:** 01 · **Habilita:** 03, 08, 09

---

## 1. Objetivo

Al terminar esta fase existe el fenotipo. Dada una lista de figuras se obtiene la
imagen que producen, y dada esa imagen se obtiene un número que dice qué tan
parecida es a la imagen objetivo. Es el puente entre el genotipo, que es lo que
los operadores manipulan, y la aptitud, que es lo que la selección compara.
Todavía no hay individuos ni generaciones, pero ya se puede dibujar un conjunto
de figuras y medir su error contra la imagen que se quiere aproximar.

---

## 2. Archivos que produce

| Archivo | Qué es |
|---|---|
| `src/renderizador.py` | Convierte una lista de figuras en una imagen, y carga las imágenes del disco |
| `src/fitness.py` | Mide la distancia entre una imagen generada y la imagen objetivo |

---

## 3. Qué hay que implementar

### `src/renderizador.py`

Es el único módulo que abre archivos de imagen y el único que sabe cómo se
compone el lienzo. No tiene estado: todas sus funciones son puras salvo la
lectura inicial del disco.

| Función | Recibe | Devuelve | Qué hace |
|---|---|---|---|
| `cargar_objetivo` | La configuración | La imagen objetivo como matriz de píxeles, más su ancho y su alto | Abre la imagen, le aplica el multiplicador de resolución y la deja lista para comparar |
| `cargar_recursos` | La configuración | Un diccionario de recursos | Carga una sola vez lo que las figuras necesitan para dibujarse |
| `renderizar` | La lista de figuras, el ancho, el alto, la configuración y los recursos | El fenotipo como matriz de píxeles | Dibuja las figuras sobre el lienzo y devuelve el resultado |

**Comportamiento de `cargar_objetivo`:**

1. Abre el archivo indicado en `file_input`. Si no existe, corta con un mensaje
   que diga qué path se intentó abrir.
2. Multiplica ancho y alto por `output_resolution_mult` y redimensiona. El ancho
   y el alto resultantes son los que va a usar todo el resto del programa: son
   las dimensiones del lienzo sobre el que se dibuja y sobre el que se recortan
   las coordenadas de las figuras.
3. Descarta el canal de transparencia de la imagen objetivo, si lo tiene. La
   comparación se hace solo sobre los tres canales de color.
4. Devuelve la matriz junto con el ancho y el alto efectivos.

**Comportamiento de `cargar_recursos`:**

Devuelve un diccionario con lo que las figuras piden al dibujarse. Hoy contiene
únicamente la imagen de overlay, bajo la clave `overlay`, y solo cuando
`gene_type` es el de tipo PNG. Si esa imagen no existe cuando hace falta, corta.
Se llama una sola vez por corrida: el punto del diccionario es que ninguna figura
abra archivos.

El nombre de la clave es un contrato con la fase 01: la figura PNG lo busca por
ese nombre exacto.

**Comportamiento de `renderizar`:**

1. Crea un lienzo del ancho y el alto recibidos, pintado del color indicado en
   `background_color`. **El lienzo se crea sin canal de transparencia**, en modo
   RGB, y por eso solo se usan los tres primeros componentes del color de fondo.
   Es el único modo en el que la biblioteca de imágenes mezcla la transparencia
   al dibujar: sobre un lienzo con canal alfa, el mismo llamado de dibujado pisa
   el píxel en vez de componerlo, y las figuras translúcidas dejan de serlo sin
   dar ningún error. Es coherente con que el lienzo sea opaco por construcción y
   con que la comparación use tres canales.
2. Recorre las figuras en el orden en que vienen en la lista y le pide a cada una
   que se dibuje sobre el lienzo, pasándole los recursos. El orden es información
   genética: la figura de la posición cero queda debajo de todas.
3. Devuelve el lienzo como matriz de píxeles, con los mismos canales y en el
   mismo formato que devuelve `cargar_objetivo`, para que la comparación sea
   directa.

**Invariantes:**
- Dos llamadas con la misma lista de figuras devuelven imágenes idénticas.
- La función no guarda estado entre llamadas ni modifica las figuras que recibe.
- El fenotipo y el objetivo tienen siempre la misma forma y el mismo tipo de
  dato. Si no la tienen, la comparación de `fitness.py` no tiene sentido.
- Ninguna figura abre un archivo. Todo lo que necesitan llega en los recursos.

---

### `src/fitness.py`

Convierte una imagen generada en un número que la selección puede comparar.

| Función | Recibe | Devuelve | Qué hace |
|---|---|---|---|
| `calcular_fitness` | El fenotipo y la imagen objetivo | Un número entre 0 y 1 | Mide el error entre las dos imágenes y lo transforma en aptitud |

**Comportamiento de `calcular_fitness`:**

1. Calcula el error cuadrático medio entre las dos imágenes: para cada píxel y
   cada uno de los tres canales de color, la diferencia entre el valor generado y
   el objetivo, elevada al cuadrado; después el promedio de todas esas
   diferencias.
2. Devuelve uno dividido por uno más ese error.

La transformación es necesaria porque el error es una magnitud a minimizar y la
selección trabaja maximizando. Dividir de esa forma da un valor que vale 1 cuando
las imágenes son idénticas, que baja cuando el error crece, que nunca es negativo
ni cero, y que preserva el orden: si una imagen tiene menos error que otra,
también tiene más aptitud. Que sea estrictamente positivo es un requisito de los
métodos de selección que reparten probabilidad proporcional a la aptitud.

Las dos alternativas que se descartaron: usar el error cambiado de signo, que da
valores negativos que la ruleta no puede usar como peso; y normalizar el error
contra un máximo teórico, que puede dar cero y que depende de una escala que
cambia con la imagen.

**Invariantes:**
- Dos imágenes idénticas dan exactamente 1.
- El resultado siempre está en el intervalo que va de 0 sin incluirlo hasta 1
  incluido.
- La función no modifica ninguna de las dos matrices que recibe.
- Solo se usan los tres canales de color. La transparencia del objetivo se
  ignora, y el lienzo del fenotipo es siempre opaco porque el fondo lo es.

---

## 4. Interfaces de otras fases

**Las figuras** llegan como una lista de objetos que implementan la interfaz de
la fase 01. El renderizador solo usa el método de dibujado: le pasa la superficie
de destino y el diccionario de recursos, y la figura se pinta sola componiendo su
color con lo que ya hay. El renderizador no sabe de qué tipo son ni cuántos
parámetros tienen.

**La configuración** llega como un diccionario ya validado por la fase 00. Las
claves que esta fase lee son `file_input`, `overlay_source`, `gene_type`,
`background_color` y `output_resolution_mult`.

**El ancho y el alto** que devuelve `cargar_objetivo` son la referencia para todo
el programa. Las figuras recortan sus coordenadas contra esos valores, no contra
el tamaño original del archivo.

---

## 5. Decisiones ya tomadas

| Decisión | Motivo |
|---|---|
| La aptitud se calcula como uno sobre uno más el error, y no como el error cambiado de signo | La ruleta y Boltzmann usan la aptitud como peso de probabilidad y necesitan que sea estrictamente positiva |
| La medida de error es el error cuadrático medio | Penaliza más las diferencias grandes de color que muchas diferencias chicas, que es lo que se quiere: una zona muy equivocada molesta más que un leve corrimiento general |
| La comparación usa solo los tres canales de color | El lienzo es opaco por construcción, así que el canal de transparencia del fenotipo no aporta información |
| El multiplicador de resolución se aplica al cargar y no al comparar | Si se aplicara al comparar, cada evaluación pagaría el costo de redimensionar. Aplicado al cargar se paga una sola vez por corrida |
| El renderizador es el único que abre archivos de imagen | Evita que cada figura lea el disco al dibujarse |
| El lienzo se crea sin canal de transparencia | Es el único modo en el que la biblioteca de imágenes compone la transparencia al dibujar en vez de pisar el píxel. Con canal alfa las figuras translúcidas dejarían de serlo, y sin ningún error de por medio |
| La imagen de overlay va bajo la clave `overlay` | La figura PNG de la fase 01 la busca por ese nombre exacto |
| El renderizador no compone capas del tamaño de la imagen | Una capa por figura implica una composición de imagen entera por gen, y el renderizado ya es la operación más cara del motor |

---

## 6. Decisiones abiertas

- **Comparar en un espacio de color perceptual.** El error cuadrático medio sobre
  los canales crudos no coincide del todo con lo que el ojo percibe como
  parecido. Cambiar de espacio de color es una mejora posible, pero encarece cada
  evaluación y conviene medir primero cuánto cambia el resultado. Queda para la
  fase 12.

---

## 7. Checkpoints obligatorios

- `src/fitness.py` — porque define la función de aptitud, que es lo que ordena a
  toda la población y lo que la consigna pide justificar explícitamente.
- `src/renderizador.py` — porque decide cómo se componen las figuras
  translúcidas, y esa composición determina el fenotipo sobre el que se calcula
  todo lo demás.

---

## 8. Cómo se verifica

| # | Qué se prueba | Entrada | Resultado esperado |
|---|---|---|---|
| 1 | Aptitud máxima | La misma matriz contra sí misma | Exactamente 1 |
| 2 | Aptitud mínima | Una matriz toda en negro contra una toda en blanco | Un valor positivo muy chico, cerca de la cota inferior |
| 3 | Monotonía | Tres imágenes cada vez más parecidas al objetivo | La aptitud crece en el mismo orden |
| 4 | Formas compatibles | El fenotipo y el objetivo | Misma cantidad de filas, columnas y canales |
| 5 | Lienzo vacío | Renderizar una lista sin figuras | Una imagen enteramente del color de fondo configurado |
| 6 | Orden de dibujado | Dos triángulos opacos superpuestos, y después la misma lista al revés | Las dos imágenes son distintas, y en cada una queda arriba el último de la lista |
| 7 | Composición translúcida | Un triángulo rojo con la transparencia a la mitad sobre fondo blanco | Los píxeles de adentro quedan rosados, no rojos puros |
| 8 | Determinismo | Renderizar dos veces la misma lista | Las dos matrices son idénticas |
| 9 | Multiplicador de resolución | Una imagen de 400 por 400 con el multiplicador en 0.5 | El ancho y el alto devueltos son 200 |
| 10 | El renderizado no modifica las figuras | Leer los parámetros de las figuras antes y después de renderizar | No cambiaron |
| 11 | Archivo faltante | Una configuración que apunta a una imagen que no existe | Corta con un mensaje que incluye el path |

---

## 9. Errores probables

- **Comparar imágenes de distinto tamaño o distinto tipo de dato** → el error da
  un número sin sentido o la resta falla → verificación 4. El fenotipo se
  construye siempre con el ancho y el alto que devolvió la carga del objetivo.
- **Restar valores de color sin convertirlos a un tipo con signo** → las
  diferencias negativas dan la vuelta y el error queda enorme y equivocado → se
  detecta con la verificación 3, donde el orden de las aptitudes sale mal.
- **Dibujar las figuras en orden inverso** → el fenotipo no corresponde al
  genotipo y el orden dentro del individuo deja de significar lo que dice
  `docs/contexto.md` → verificación 6.
- **Cargar la imagen de overlay dentro del bucle de renderizado** → una lectura
  de disco por figura y por individuo → se carga una sola vez en los recursos.
- **Aplicar el multiplicador de resolución al objetivo pero no al lienzo** → las
  dos imágenes tienen distinto tamaño y no se pueden comparar → hay un solo par
  de valores de ancho y alto en toda la corrida, el que devuelve la carga.
- **Incluir el canal de transparencia en el error** → se suma una diferencia
  constante que no aporta nada y ensucia la escala de la aptitud → solo se
  comparan los tres canales de color.
- **Crear el lienzo con canal de transparencia** → el dibujado deja de componer y
  pasa a pisar el píxel, así que todas las figuras se ven opacas por más que su
  canal alfa diga otra cosa. No da ningún error: simplemente el motor pierde la
  translucidez, que es una de las cosas que la consigna pide → verificación 7.
- **Usar una clave distinta a `overlay`** → la figura PNG no encuentra su imagen
  y falla en la primera corrida con ese tipo de gen.

---

## 10. Cierre de la fase

- [ ] Todos los archivos de la sección 2 existen y se importan sin error
- [ ] Todas las verificaciones de la sección 8 pasan
- [ ] `docs/resumenes/FASE_02_RESUMEN.md` está escrito
- [ ] No se tocó ningún archivo fuera de la lista
- [ ] El agente no commiteó ni pusheó nada
