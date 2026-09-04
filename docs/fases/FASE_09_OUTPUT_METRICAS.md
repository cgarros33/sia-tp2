# Fase 09 — Output y métricas de corrida

> **Ola:** 4 · **Depende de:** 03 · **Habilita:** 10, 12

---

## 1. Objetivo

Al terminar esta fase la corrida deja rastro. Existen los archivos que la
consigna pide como entregables (la imagen generada, la enumeración de figuras y
las métricas para defender la implementación) y el registro por generación sobre
el que se van a construir los gráficos comparativos. Es la fase que convierte una
ejecución en evidencia.

---

## 2. Archivos que produce

| Archivo | Qué es |
|---|---|
| `src/output.py` | Todas las escrituras a disco de una corrida |

---

## 3. Qué hay que implementar

### `src/output.py`

Es el único módulo que escribe archivos. No decide nada sobre el algoritmo: recibe
datos ya calculados y los guarda.

| Función | Recibe | Devuelve | Qué hace |
|---|---|---|---|
| `inicializar_output` | Los destinos de resultados e imágenes | Nada | Crea las carpetas si no existen y prepara los archivos de la corrida |
| `guardar_fila_generacion` | El destino, el número de generación y sus métricas | Nada | Agrega una fila al registro por generación |
| `guardar_frame` | El destino, el fenotipo del mejor individuo y el número de generación | Nada | Guarda la imagen de esa generación como cuadro del GIF |
| `compilar_gif` | El destino de imágenes | Nada | Arma el GIF con todos los cuadros guardados |
| `guardar_imagen_final` | El destino y el fenotipo del mejor individuo | Nada | Guarda la imagen generada de la corrida |
| `guardar_enumeracion_figuras` | El destino y el mejor individuo | Nada | Guarda la lista de figuras con todos sus parámetros |
| `guardar_genomas` | El destino, el número de generación y los individuos | Nada | Guarda todos los genomas de la generación. Solo se llama con el volcado completo activado |
| `guardar_resumen` | El destino y la metadata de la corrida | Nada | Escribe el resumen de la ejecución |

---

**El registro por generación.** Un archivo separado por comas, una fila por
generación, con al menos: número de generación, fitness máximo, mínimo y
promedio, diversidad, y tiempo transcurrido desde el inicio de la corrida. Es la
materia prima de todos los gráficos de la fase 12.

Se escribe fila por fila a medida que avanza la corrida, no todo junto al final.
Una corrida que se interrumpe a mitad de camino, por un corte o porque alguien la
frena, tiene que dejar utilizable todo lo que alcanzó a correr.

**La enumeración de figuras.** La consigna la pide explícitamente como salida:
posición, color y demás parámetros de cada figura del mejor individuo. Se guarda
como archivo separado por comas, una fila por figura, en el orden de dibujado, y
con una columna por parámetro.

Los encabezados salen de la propia figura, que sabe cómo se llaman sus
parámetros. Así el archivo se adapta solo a los cinco tipos de figura, que tienen
distinta cantidad de parámetros, sin que este módulo sepa cuál es cuál.

**El GIF de progreso.** Un cuadro por generación con el fenotipo del mejor
individuo, para ver cómo evoluciona la aproximación. En corridas largas son miles
de cuadros, así que conviene poder guardar uno cada tantas generaciones en vez de
todos.

**El resumen de la corrida.** Un archivo de texto con el fitness final, la
cantidad de generaciones, el tiempo de ejecución, el motivo de finalización y la
configuración completa que se usó. Es lo que permite, meses después, saber de
dónde salió un resultado.

**El volcado completo.** Todos los genomas de todos los individuos de todas las
generaciones, ordenados por generación. Solo se activa con el flag
correspondiente, porque el archivo crece muy rápido: cien individuos por cien
genes por diez parámetros por quinientas generaciones son cincuenta millones de
valores.

**Invariantes:**
- Ninguna función de este módulo calcula métricas. Todo llega calculado.
- El módulo no conoce ningún tipo de figura concreto: los nombres y los valores
  de los parámetros se los pide a la figura.
- Escribir en un destino que no existe no falla: las carpetas se crean.
- Dos corridas seguidas no mezclan resultados.

---

## 4. Interfaces de otras fases

**Los individuos** de la fase 03 exponen su lista de genes. **Las figuras** de la
fase 01 exponen sus parámetros y los nombres de esos parámetros, en el mismo
orden y con el mismo largo. Con esos dos métodos se arman tanto la enumeración de
figuras como el volcado completo, para cualquiera de los cinco tipos.

**El fenotipo** llega como la matriz de píxeles que devuelve el renderizador de
la fase 02. Este módulo la guarda como imagen pero no la produce.

**El motor** de la fase 08 llama a estas funciones. Le pasa las métricas de cada
generación ya calculadas, el fenotipo del mejor individuo, y al final la metadata
completa de la corrida.

**Los destinos** de resultados e imágenes llegan por parámetro, con sus valores
por defecto resueltos por la fase 00.

---

## 5. Decisiones ya tomadas

| Decisión | Motivo |
|---|---|
| El registro se escribe fila por fila y no al final | Una corrida interrumpida deja utilizable lo que alcanzó a correr, y las corridas largas son justamente las que más chances tienen de interrumpirse |
| La enumeración de figuras es un entregable propio | La consigna la pide explícitamente como salida, junto con la imagen generada |
| Los encabezados salen de la figura | Los cinco tipos tienen distinta cantidad de parámetros, y una tabla fija acá habría que actualizarla cada vez que se agrega un tipo |
| El volcado completo está detrás de un flag | El archivo crece a decenas de millones de valores en una corrida normal |
| Este módulo no calcula nada | Si calculara métricas, habría dos lugares donde se define lo mismo y en algún momento dejarían de coincidir |
| La configuración usada se guarda con los resultados | Es lo que hace que un resultado sea rastreable y reproducible |

---

## 6. Decisiones abiertas

- **Cada cuántas generaciones se guarda un cuadro del GIF.** Guardar todas
  produce archivos enormes y GIFs de miles de cuadros. Conviene un intervalo,
  pero el valor concreto queda a criterio de quien implementa. Si termina siendo
  un parámetro configurable, hay que avisar al grupo porque toca el archivo de
  configuración.
- **Qué hacer con los resultados de una corrida anterior.** Las opciones son
  sobrescribir, agregar a lo que hay, o guardar cada corrida en una carpeta con
  su fecha. La tercera es la que mejor sirve para la fase 12, donde se corren
  muchas configuraciones seguidas y hay que poder compararlas.

---

## 7. Checkpoints obligatorios

Ninguno: este módulo escribe archivos con datos que recibe ya calculados. No
decide, no pondera y no compara nada.

---

## 8. Cómo se verifica

| # | Qué se prueba | Entrada | Resultado esperado |
|---|---|---|---|
| 1 | Se crean las carpetas | Destinos que no existen | Se crean sin fallar |
| 2 | Una fila por generación | Una corrida de diez generaciones | El registro tiene diez filas más el encabezado |
| 3 | El registro es utilizable a mitad de camino | Leer el archivo con la corrida todavía en curso | Las filas escritas hasta ese momento se leen bien |
| 4 | Enumeración completa | Un individuo de cincuenta figuras | Cincuenta filas, en el orden de dibujado |
| 5 | Encabezados según el tipo | La enumeración para cada uno de los cinco tipos de figura | La cantidad de columnas coincide con la cantidad de parámetros de cada tipo |
| 6 | El GIF se arma | Una corrida corta | Existe el archivo y se abre |
| 7 | La imagen final | Una corrida corta | Existe y coincide con el fenotipo del mejor individuo |
| 8 | El resumen tiene todo | Una corrida corta | Incluye fitness final, generaciones, tiempo, motivo de corte y la configuración completa |
| 9 | El volcado está apagado por defecto | Una corrida sin el flag | No se generó el archivo de genomas |
| 10 | El volcado prendido | Una corrida de cinco generaciones con diez individuos y el flag activo | El archivo tiene cincuenta genomas, agrupados por generación |
| 11 | Dos corridas no se mezclan | Dos corridas seguidas sobre el mismo destino | Los resultados de la segunda no quedan pegados a los de la primera |

---

## 9. Errores probables

- **Acumular todo en memoria y escribir al final** → una corrida interrumpida no
  deja nada, y son las corridas largas las que más se interrumpen →
  verificación 3.
- **Encabezados fijos para los parámetros de las figuras** → funciona con
  triángulos y se rompe con óvalos, que tienen otros parámetros →
  verificación 5.
- **Abrir y cerrar el archivo en cada fila** → cientos de aperturas por corrida →
  conviene mantenerlo abierto o usar un modo de agregado.
- **Que la segunda corrida agregue filas a las de la primera** → el registro
  mezcla dos configuraciones distintas y los gráficos de la fase 12 salen mal →
  verificación 11.
- **Guardar un cuadro del GIF por generación en corridas largas** → miles de
  archivos y un GIF inmanejable → se guarda cada cierto intervalo.
- **Calcular alguna métrica acá** → queda definida en dos lugares y en algún
  momento dejan de coincidir → todo llega calculado desde la población.
- **Guardar el resumen sin la configuración** → el resultado deja de ser
  rastreable → verificación 8.
- **Escribir el fenotipo sin convertir el formato de color** → los canales quedan
  invertidos y las imágenes salen con los colores cambiados → verificación 7,
  comparando contra el fenotipo.

---

## 10. Cierre de la fase

- [ ] Todos los archivos de la sección 2 existen y se importan sin error
- [ ] Todas las verificaciones de la sección 8 pasan
- [ ] `docs/resumenes/FASE_09_RESUMEN.md` está escrito
- [ ] No se tocó ningún archivo fuera de la lista
- [ ] El agente no commiteó ni pusheó nada
