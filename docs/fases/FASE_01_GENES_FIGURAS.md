# Fase 01 — Genes: las cinco figuras

> **Ola:** 1 · **Depende de:** — · **Habilita:** 02, 03, 06, 08, 09

---

## 1. Objetivo

Al terminar esta fase existe el gen del problema: la figura. Hay una interfaz
común y cinco implementaciones intercambiables (triángulo, cuadrilátero,
pentágono, óvalo e imagen PNG). Cada una sabe crearse al azar, mutarse
respetando su dominio, copiarse, dibujarse sobre el lienzo y exponer sus
parámetros. Todavía no hay imagen renderizada ni fitness, pero ya se puede crear
una figura al azar, mutarla miles de veces y comprobar que ningún parámetro se
escapa de su rango.

---

## 2. Archivos que produce

| Archivo | Qué es |
|---|---|
| `src/figuras/__init__.py` | Vacío |
| `src/figuras/base.py` | Interfaz abstracta de figura |
| `src/figuras/triangulo.py` | Polígono de 3 vértices con RGBA |
| `src/figuras/cuadrilatero.py` | Polígono de 4 vértices con RGBA |
| `src/figuras/pentagono.py` | Polígono de 5 vértices con RGBA |
| `src/figuras/ovalo.py` | Elipse con centro, dos radios, rotación y RGBA |
| `src/figuras/imagen_png.py` | Overlay de un PNG externo, con la misma geometría que el óvalo |

---

## 3. Qué hay que implementar

### `src/figuras/base.py`

La interfaz abstracta que las cinco figuras implementan. Es lo que permite que el
resto del motor trabaje con figuras sin saber de qué tipo son.

| Método | Recibe | Devuelve | Qué hace |
|---|---|---|---|
| `aleatoria` | Generador de azar, ancho y alto del lienzo, configuración | Una figura nueva | Crea una figura con todos sus parámetros muestreados al azar dentro del dominio válido. Es de clase, no de instancia |
| `mutar` | Generador de azar, configuración, ancho y alto | Una figura nueva | Devuelve una figura con los parámetros mutados |
| `copiar` | — | Una figura nueva | Devuelve una copia independiente |
| `dibujar` | La superficie de destino y un diccionario de recursos | Nada | Pinta la figura sobre el destino, componiendo su color con lo que ya está dibujado |
| `parametros` | — | Los valores de la figura, en orden fijo | Expone el genotipo de la figura |
| `centro` | — | Un par de coordenadas | Devuelve el centro geométrico |
| `con_color` | Tres componentes de color | Una figura nueva | Devuelve una copia con otro color, conservando geometría y transparencia |
| `nombres_parametros` | — | Los nombres de los parámetros | Mismo orden que `parametros`. Es de clase |
| `rangos` | Ancho y alto del lienzo, configuración | El mínimo y el máximo de cada parámetro | Mismo orden que `parametros`. Es de clase |

Cada método existe porque una fase posterior lo necesita:

| Método | Quién lo usa |
|---|---|
| `aleatoria` | Fase 08, para armar la generación 0 |
| `mutar` | Fase 06, los cuatro métodos de mutación |
| `copiar` | Fase 05, para que los hijos no compartan genes con los padres |
| `dibujar` | Fase 02, el renderizador |
| `parametros` y `rangos` | Fase 03, la métrica de diversidad. Fase 09, el volcado de genomas |
| `nombres_parametros` | Fase 09, los encabezados de los CSV |
| `centro` y `con_color` | Fase 08, la variante de sesgo de color inicial |

**Invariantes de la interfaz:**
- `mutar`, `copiar` y `con_color` nunca modifican la figura sobre la que se
  llaman. Siempre devuelven una instancia nueva.
- `parametros`, `nombres_parametros` y `rangos` devuelven secuencias del mismo
  largo y en el mismo orden.
- Todas las implementaciones evitan el diccionario de instancia, según la
  consideración de rendimiento de `docs/contexto.md`.

---

### `src/figuras/triangulo.py`

La figura estándar del problema. Diez parámetros: seis de geometría (las
coordenadas de los tres vértices) y cuatro de color.

**Dominio de cada parámetro:**

| Parámetro | Rango válido |
|---|---|
| Las tres coordenadas horizontales | Desde menos `max_coord_overflow` hasta el ancho más `max_coord_overflow` |
| Las tres coordenadas verticales | Desde menos `max_coord_overflow` hasta el alto más `max_coord_overflow` |
| Los cuatro canales de color | Enteros de 0 a 255 |

**Creación al azar.** Cada parámetro se muestrea uniformemente dentro de su rango
válido. Es exactamente el mismo dominio que usa el recorte de la mutación: la
generación inicial y cualquier individuo mutado viven en el mismo espacio.

**Mutación.** Se recorren los diez parámetros y cada uno se muta de forma
independiente con probabilidad `intra_gene_Pm`. Cuando un parámetro muta, se le
suma un valor al azar tomado uniformemente entre menos y más su delta máximo
(`max_coord_delta` para las coordenadas, `max_color_delta` para el color), y el
resultado se recorta a los extremos de su rango válido. No hay wraparound: un
valor que se pasa del extremo se queda en el extremo.

**Dibujado.** Pinta el polígono relleno sobre la superficie que recibe,
componiendo su color con lo que ya hay dibujado según su canal de transparencia.
No crea capas intermedias del tamaño de la imagen: la biblioteca de imágenes
permite dibujar con mezcla de transparencia directamente sobre el destino, y
crear una capa por figura convertiría el renderizado en el cuello de botella del
motor.

**Centro.** El promedio de los tres vértices.

**Invariantes:**
- Después de cualquier cantidad de mutaciones, todos los parámetros siguen dentro
  de los rangos de la tabla.
- Los cuatro canales de color se guardan y se devuelven como enteros.

---

### `src/figuras/cuadrilatero.py` y `src/figuras/pentagono.py`

Idénticos al triángulo, con cuatro y cinco vértices respectivamente. Mismo
dominio, misma regla de mutación, mismo recorte. Tienen doce y catorce
parámetros.

---

### `src/figuras/ovalo.py`

Nueve parámetros: centro, dos radios, rotación y los cuatro canales de color.

**Dominio de cada parámetro:**

| Parámetro | Rango válido | Delta de mutación |
|---|---|---|
| Coordenada horizontal del centro | De 0 al ancho | `max_coord_delta` |
| Coordenada vertical del centro | De 0 al alto | `max_coord_delta` |
| Los dos radios | De 1 a la mitad del lado mayor del lienzo | `max_radius_delta` |
| Rotación | De 0 a 1 | `max_rotation_delta` |
| Los cuatro canales de color | Enteros de 0 a 255 | `max_color_delta` |

El óvalo no usa `max_coord_overflow`: su centro se queda siempre dentro del
lienzo.

La rotación está normalizada: 0 es sin rotar y 1 es una vuelta completa. Al
dibujar se lleva a grados.

**Dibujado.** La biblioteca de imágenes no dibuja elipses rotadas directamente.
La elipse se dibuja sin rotar en una capa auxiliar del tamaño de su caja
contenedora, esa capa se rota, y recién ahí se compone sobre el destino en la
posición que corresponde. La capa auxiliar es del tamaño de la figura, no de la
imagen.

---

### `src/figuras/imagen_png.py`

Los mismos nueve parámetros del óvalo, con los mismos dominios y la misma regla
de mutación.

**Dibujado.** Toma la imagen de overlay que llega en los recursos, la reescala al
doble de cada radio, la rota según su rotación, aplica el color como tinte y el
canal de transparencia como multiplicador del suyo propio, y la pega centrada en
su posición.

El PNG se lee del disco una sola vez, en el renderizador de la fase 02, y llega
ya cargado en los recursos. La figura nunca abre un archivo: si cada gen leyera
el PNG, una generación de cien individuos con cien genes haría diez mil lecturas
de disco.

---

## 4. Interfaces de otras fases

**La configuración** llega como un diccionario ya validado por la fase 00. Se
asume correcto y no se vuelve a chequear. Las claves que esta fase lee son
`intra_gene_Pm`, `max_coord_delta`, `max_color_delta`, `max_rotation_delta`,
`max_radius_delta` y `max_coord_overflow`.

**El generador de azar** llega siempre por parámetro. Es un único generador de
numpy creado a partir de `random_seed` al arrancar la corrida. Ninguna figura
crea su propio generador ni usa el módulo de azar de la biblioteca estándar: si
lo hiciera, se rompería la reproducibilidad por semilla.

**El ancho y el alto del lienzo** llegan por parámetro, no por configuración,
porque salen de la imagen objetivo y esa la carga la fase 10.

---

## 5. Decisiones ya tomadas

| Decisión | Motivo |
|---|---|
| El gen es la figura completa, no un parámetro suelto | Mezclar parámetros de figuras distintas produce figuras incoherentes, no recombinación útil. La cruza opera a nivel de figura |
| La mutación aplica un delta al valor en vez de reasignarlo al azar | Un delta chico mantiene el fitness localmente suave: una figura bien ubicada se ajusta en lugar de destruirse. Reasignar al azar convierte la mutación en ruido |
| Recorte estricto, sin wraparound | Con wraparound una figura del borde derecho salta al izquierdo ante un delta mínimo, y eso es un cambio enorme de fenotipo ante un cambio mínimo de genotipo |
| La mutación recibe el ancho y el alto explícitamente | El recorte de coordenadas depende del tamaño del lienzo, que no está en la configuración porque sale de la imagen objetivo |
| La figura compone su propio color sobre el destino, sin capas del tamaño de la imagen | Una capa por figura implica una composición de la imagen completa por gen. Con cien genes, cien individuos y cientos de generaciones son millones de composiciones de imagen entera, y el renderizado ya es la operación más cara del motor |
| El radio del óvalo se recorta entre 1 y la mitad del lado mayor | El mínimo evita radios nulos o negativos, que rompen el dibujado. El máximo es el radio que ya cubre el lienzo entero: más grande no aporta fenotipo nuevo |

---

## 6. Decisiones abiertas

- **Transparencia mínima.** Con el canal de transparencia uniforme en todo su
  rango, una parte de las figuras nace casi invisible y ocupa un locus sin
  aportar fenotipo. Se podría acotar el mínimo, pero conviene medirlo en la fase
  12 antes de tocarlo.
- **Tinte del PNG.** Queda a criterio de quien implementa si el color tiñe la
  imagen de overlay o si solo se usa el canal de transparencia. Se resuelve al
  ver cómo queda el resultado.

---

## 7. Checkpoints obligatorios

- `src/figuras/triangulo.py` — porque define el esquema de mutación por delta y
  el recorte de dominio que después repiten el cuadrilátero y el pentágono.
- `src/figuras/ovalo.py` — porque tiene tres dominios que el triángulo no tiene
  (radios, rotación normalizada, centro sin overflow) y una regla de recorte
  propia.

`cuadrilatero.py` y `pentagono.py` no llevan checkpoint: repiten el esquema ya
aprobado en el triángulo con más vértices. `imagen_png.py` repite el del óvalo.

---

## 8. Cómo se verifica

| # | Qué se prueba | Entrada | Resultado esperado |
|---|---|---|---|
| 1 | Dominio inicial | Diez mil triángulos al azar sobre un lienzo de 200 por 200 | Ningún parámetro fuera de su rango |
| 2 | Recorte tras mutar | Un triángulo mutado diez mil veces seguidas | Ningún parámetro fuera de su rango, en particular ninguna coordenada más allá del margen de overflow |
| 3 | Recorte extremo | Un triángulo con todas las coordenadas en el máximo, mutado con probabilidad interna 1 | Las coordenadas se quedan en el máximo y no dan la vuelta |
| 4 | La mutación no modifica el original | Leer los parámetros, mutar, volver a leer | La lectura original no cambió |
| 5 | Independencia de la copia | Copiar y mutar la copia | El original no cambió |
| 6 | Coherencia de las secuencias | Las cinco figuras | Los parámetros, sus nombres y sus rangos tienen el mismo largo |
| 7 | Reproducibilidad | Dos generadores con la misma semilla, cien figuras cada uno | Las cien coinciden parámetro por parámetro |
| 8 | Rotación normalizada | Un óvalo mutado diez mil veces | La rotación siempre entre 0 y 1 |
| 9 | Radios | Un óvalo mutado diez mil veces | Ningún radio menor a 1 |
| 10 | Dibujado opaco | Un triángulo rojo opaco sobre un lienzo blanco de 100 por 100 | Hay píxeles rojos dentro del triángulo y blancos fuera |
| 11 | Dibujado translúcido | Un triángulo rojo con la transparencia a la mitad sobre un lienzo blanco | Los píxeles de adentro quedan rosados, no rojos puros: el color se compuso con el fondo |
| 12 | Sin estado compartido | Mil triángulos al azar | Ninguno comparte identidad de objeto con otro |

---

## 9. Errores probables

- **Recortar antes de sumar el delta** → el valor se escapa del rango → se
  detecta con la verificación 3, que arranca desde el extremo.
- **Guardar los colores como flotantes** → el renderizador falla o los colores
  quedan corridos → los cuatro canales se guardan como enteros.
- **Mutar sobre la misma instancia y devolverla** → el padre cambia cuando muta
  el hijo, y el caché de fitness del padre queda mintiendo → verificación 4.
- **Copiar en superficie** → la copia comparte estado con el original →
  verificación 5.
- **Usar el módulo de azar de la biblioteca estándar o el generador global de
  numpy** → se rompe la reproducibilidad por semilla → verificación 7. El
  generador siempre llega por parámetro.
- **Abrir el PNG dentro del dibujado** → miles de lecturas de disco por
  generación → el PNG llega ya cargado en los recursos.
- **Declarar el ahorro de diccionario solo en la clase base** → las clases hijas
  lo crean igual y se pierde el beneficio → las cinco lo declaran.
- **Componer la figura sobre el lienzo dentro del dibujado** → el orden de
  dibujado y la translucidez dejan de ser responsabilidad del renderizador y el
  resultado pasa a depender de quién llama → la figura solo pinta sobre el
  destino que recibe, en el momento en que la llaman.
- **Dibujar sin mezclar la transparencia** → el color de la figura reemplaza al
  del fondo en vez de componerse, y las figuras translúcidas dejan de serlo →
  verificación 11.

---

## 10. Cierre de la fase

- [ ] Todos los archivos de la sección 2 existen y se importan sin error
- [ ] Todas las verificaciones de la sección 8 pasan
- [ ] `docs/resumenes/FASE_01_RESUMEN.md` está escrito
- [ ] No se tocó ningún archivo fuera de la lista
- [ ] El agente no commiteó ni pusheó nada
