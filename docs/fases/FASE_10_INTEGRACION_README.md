# Fase 10 — Integración end-to-end y README

> **Ola:** 5 · **Depende de:** todas las anteriores · **Habilita:** 11, 12

---

## 1. Objetivo

Al terminar esta fase el programa corre entero desde la línea de comandos. Existe
el punto de entrada que une la configuración, la carga de la imagen, el motor y
las salidas, y existe el archivo que explica cómo ejecutarlo, que es uno de los
tres entregables que pide la consigna. Es la primera fase en la que se puede
mirar el GIF y ver si el motor efectivamente aproxima la imagen.

---

## 2. Archivos que produce

| Archivo | Qué es |
|---|---|
| `main.py` | Punto de entrada del programa |
| `README.md` | Cómo instalar y ejecutar |

Esta fase también puede corregir defectos de integración en archivos de fases
anteriores. Es la única que tiene esa licencia, y con dos condiciones: que el
defecto impida que el programa corra, y que el cambio quede anotado en el resumen
con el archivo tocado y el motivo.

---

## 3. Qué hay que implementar

### `main.py`

Un archivo corto. Su única responsabilidad es encadenar lo que ya existe en el
orden correcto y no contener lógica propia.

**El flujo:**

1. Se interpretan los argumentos de la línea de comandos.
2. Se carga y valida la configuración, con los overrides aplicados.
3. Se carga la imagen objetivo, que devuelve el ancho y el alto efectivos de toda
   la corrida.
4. Se cargan los recursos que las figuras necesitan para dibujarse.
5. Se crea el generador de azar a partir de la semilla de la configuración. Es el
   único de la corrida y de él derivan todos los sorteos.
6. Se preparan las carpetas de salida.
7. Se ejecuta el motor.
8. Se informa por pantalla dónde quedaron los resultados.

**Invariantes:**
- No hay lógica de algoritmo genético en este archivo.
- El generador de azar se crea una sola vez, acá.
- Un error de configuración corta con un mensaje entendible, no con un rastro de
  excepciones.

**Salida por pantalla durante la corrida.** Una corrida puede durar minutos sin
mostrar nada, y no hay forma de distinguir un programa trabajando de uno colgado.
Conviene informar el avance cada cierta cantidad de generaciones: número de
generación, mejor fitness y diversidad. Es lo mínimo para poder frenar a tiempo
una corrida que claramente no va a ningún lado.

---

### `README.md`

Escrito para alguien que clona el repositorio y no sabe nada del trabajo. Tiene
que contener:

- Qué hace el programa, en dos o tres oraciones.
- Qué versión de Python hace falta y cómo instalar las dependencias.
- El comando mínimo para correrlo.
- Cómo cambiar parámetros: el archivo de configuración, la forma de los overrides
  por línea de comandos y la diferencia entre los flags estructurales, que van
  con guión medio, y los overrides, que van con el nombre exacto del campo.
- La lista de campos de configuración con qué significa cada uno y qué valores
  admite.
- Qué archivos genera una corrida y dónde quedan.
- Un ejemplo completo de punta a punta.

---

## 4. Interfaces de otras fases

Esta fase consume todas las anteriores, cada una por su interfaz pública: los
argumentos y la configuración de la fase 00, la carga de imágenes de la fase 02,
la creación de carpetas de la fase 09 y la ejecución del motor de la fase 08.

Es también la fase donde se prueban por primera vez juntas, así que es esperable
que aparezcan desajustes entre lo que una fase creyó que devolvía y lo que la
siguiente esperaba recibir.

---

## 5. Decisiones ya tomadas

| Decisión | Motivo |
|---|---|
| El punto de entrada no contiene lógica de algoritmo | Todo lo que decida algo tiene que estar en un módulo que se pueda probar por separado |
| El generador de azar se crea acá y se pasa hacia abajo | Es lo que garantiza que dos corridas con la misma configuración den lo mismo. Si cada módulo creara el suyo, no habría reproducibilidad |
| El ancho y el alto salen de la carga de la imagen, no de la configuración | Dependen del multiplicador de resolución, y tiene que haber un solo par de valores en toda la corrida |
| Se informa el avance por pantalla | Una corrida silenciosa de varios minutos es indistinguible de una colgada |
| Esta fase puede tocar archivos de otras fases | Es la única que ve el sistema completo, y bloquear las correcciones de integración obligaría a coordinar cuatro personas para arreglar un desajuste de una línea |

---

## 6. Decisiones abiertas

- **Ventana de progreso en vivo.** Mostrar el mejor individuo de cada generación
  en una ventana mientras corre ayuda mucho a entender qué está haciendo el
  motor. La biblioteca que suele usarse para eso no está entre las autorizadas,
  así que hay que consultarlo con el grupo antes. Como alternativa sin
  dependencias nuevas, se puede escribir el fenotipo actual en un archivo fijo y
  mirarlo con cualquier visor que recargue solo.

---

## 7. Checkpoints obligatorios

Ninguno: el punto de entrada encadena módulos y no calcula nada.

---

## 8. Cómo se verifica

| # | Qué se prueba | Entrada | Resultado esperado |
|---|---|---|---|
| 1 | Corrida mínima | El programa sin argumentos, con la configuración por defecto y pocas generaciones | Termina sin errores y genera todas las salidas |
| 2 | Overrides | Un override de la cantidad de genes por línea de comandos | La corrida usa ese valor, y el resumen lo registra |
| 3 | Archivo de configuración alternativo | El flag de ruta de configuración apuntando a otro archivo | Se usa ese archivo |
| 4 | Destinos alternativos | Los flags de resultados e imágenes apuntando a otras carpetas | Las salidas quedan ahí |
| 5 | Volcado completo | El flag correspondiente | Se genera el archivo de genomas |
| 6 | Error de configuración | Un valor fuera de rango | Corta con un mensaje entendible, sin rastro de excepciones |
| 7 | Imagen inexistente | Una configuración que apunta a una imagen que no está | Corta con un mensaje que incluye el path |
| 8 | Reproducibilidad | Dos corridas con la misma semilla | El registro por generación es idéntico |
| 9 | Semillas distintas | Dos corridas con semillas distintas | Los resultados difieren |
| 10 | Los cinco tipos de figura | Una corrida corta con cada tipo | Las cinco terminan sin errores |
| 11 | Las catorce combinaciones | Los siete métodos de selección por las dos estrategias de supervivencia | Todas terminan sin errores |
| 12 | El motor aproxima | Una corrida larga sobre una imagen simple | El fitness sube de forma sostenida y el GIF muestra la imagen formándose |

La verificación 12 es la más importante de toda la fase, y la única que no es
binaria. Es el momento en que se comprueba que el algoritmo hace lo que tiene que
hacer y no solamente que no se rompe. Conviene correrla sobre una imagen simple,
de pocos colores planos y bordes rectos: sobre una cara el progreso tarda mucho
más en volverse visible y es difícil distinguir un motor lento de uno roto.

---

## 9. Errores probables

- **Crear más de un generador de azar** → se pierde la reproducibilidad y con
  ella toda posibilidad de comparar métodos, porque no se sabe si una diferencia
  viene del cambio o del azar → verificación 8.
- **Usar el ancho y el alto del archivo original en vez de los de la imagen ya
  redimensionada** → las figuras se recortan contra un tamaño y se dibujan sobre
  otro → se detecta cuando el multiplicador de resolución no es uno.
- **Dejar que las excepciones salgan crudas** → un valor mal escrito en la
  configuración devuelve un rastro de excepciones en vez de decir qué campo está
  mal → verificación 6.
- **Meter lógica en el punto de entrada** → queda código que ninguna prueba
  alcanza, porque probar el punto de entrada es correr el programa entero.
- **Que el fitness suba unas generaciones y se estanque enseguida** → suele ser
  presión de selección insuficiente. Con aptitudes muy chicas y parecidas, los
  métodos proporcionales al valor reparten casi la misma probabilidad a todos y
  el motor se comporta como una búsqueda al azar. Los métodos que miran la
  posición y no el valor no tienen ese problema → verificación 12.
- **Que el fitness no suba nunca** → puede ser el caché de aptitud que no se
  invalida al mutar, con lo cual la selección ordena con números vencidos. Es lo
  primero que conviene descartar → se comprueba corriendo las verificaciones de
  la fase 03.
- **Un README que asume contexto** → el entregable pide explicar cómo ejecutar el
  programa, y lo tiene que poder seguir alguien que no participó del trabajo.

---

## 10. Cierre de la fase

- [ ] Todos los archivos de la sección 2 existen y el programa corre
- [ ] Todas las verificaciones de la sección 8 pasan
- [ ] `docs/resumenes/FASE_10_RESUMEN.md` está escrito, incluyendo los arreglos de integración a archivos de otras fases
- [ ] El agente no commiteó ni pusheó nada
