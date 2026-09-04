# Fase 00 — Andamiaje, configuración y CLI

> **Ola:** 1 · **Depende de:** — · **Habilita:** 08, 09, 10

---

## 1. Objetivo

Al terminar esta fase el repositorio tiene la estructura de carpetas completa, un
archivo de configuración con todos los campos que el motor va a necesitar, y dos
módulos que permiten arrancar cualquier corrida: uno que lee y valida la
configuración, otro que interpreta los argumentos de línea de comandos. Todavía
no hay algoritmo genético, pero ya se puede invocar el programa con
`--gene_count=30` y obtener una configuración válida y verificada.

---

## 2. Archivos que produce

| Archivo | Qué es |
|---|---|
| `src/__init__.py` | Vacío. Marca `src` como paquete |
| `src/config.py` | Carga, valida y normaliza la configuración |
| `src/cli.py` | Interpreta los argumentos de línea de comandos |
| `config/conf.json` | Configuración por defecto, con todos los campos |
| `resources/.gitkeep` | Carpeta de la imagen objetivo y del PNG de overlay |
| `results/.gitkeep` | Carpeta de salida de CSV y `resumen.txt` |
| `img/.gitkeep` | Carpeta de salida de frames y GIF |
| `tests/.gitkeep` | Carpeta de la suite de tests (fase 11) |
| `analisis/.gitkeep` | Carpeta de scripts de experimentación (fase 12) |

Los subpaquetes de `src/` (`figuras/`, `seleccion/`, `cruza/`, `mutacion/`,
`supervivencia/`) los crea cada fase con su propio `__init__.py` vacío.

---

## 3. Qué hay que implementar

### `config/conf.json`

Un único objeto JSON con todos los campos de abajo. Todos son obligatorios: si
falta uno, la carga falla. Los valores de la columna "Por defecto" son un punto
de partida razonable, no un resultado experimental; se ajustan en la fase 12.

**Parámetros del problema**

| Campo | Por defecto | Qué es |
|---|---|---|
| `gene_count` | 100 | Cantidad de figuras de cada individuo |
| `file_input` | `resources/lebron.png` | Imagen a aproximar |
| `gene_type` | `triangle` | Figura que representa el gen |
| `overlay_source` | `resources/overlay.png` | Imagen que usa el gen de tipo `png` |
| `background_color` | 255, 255, 255, 255 | Color RGBA del lienzo. Entra en el fitness porque las figuras pueden ser translúcidas |
| `output_resolution_mult` | 0.5 | Multiplicador de resolución al renderizar y comparar |

**Métodos a usar**

| Campo | Por defecto | Qué es |
|---|---|---|
| `seleccion` | `torneo_deterministico` | Método de selección |
| `cruza` | `dos_puntos` | Método de cruza |
| `mutacion` | `multigen` | Método de mutación |
| `supervivencia` | `aditiva` | Estrategia de supervivencia |

**Hiperparámetros de población y selección**

| Campo | Por defecto | Qué es |
|---|---|---|
| `population_size` | 100 | Cantidad de individuos por generación |
| `selected_count` | 100 | Cantidad de individuos que se seleccionan como padres |
| `tournament_size` | 5 | Competidores por torneo determinístico |
| `tournament_threshold` | 0.75 | Umbral de torneo probabilístico |
| `temperature` | 1.0 | Temperatura de la selección de Boltzmann |

**Hiperparámetros de mutación**

| Campo | Por defecto | Qué es |
|---|---|---|
| `extra_gene_Pm` | 0.15 | Probabilidad de que un gen mute |
| `intra_gene_Pm` | 0.2 | Probabilidad de que mute cada parámetro dentro de un gen |
| `max_genes_to_mutate` | 5 | Cota de genes que mutan por individuo en multigen |
| `max_coord_delta` | 15.0 | Paso máximo de mutación en coordenadas |
| `max_color_delta` | 25 | Paso máximo de mutación en RGBA |
| `max_rotation_delta` | 0.05 | Paso máximo de mutación en rotación |
| `max_radius_delta` | 10.0 | Paso máximo de mutación en radios |
| `max_coord_overflow` | 10.0 | Cuánto puede salirse una coordenada del lienzo |

**Criterios de corte y reproducibilidad**

| Campo | Por defecto | Qué es |
|---|---|---|
| `max_generations` | 1000 | Corte por cantidad máxima de generaciones |
| `fitness_cutoff` | 0.99 | Corte al alcanzar este fitness |
| `stale_content_generation_cutoff` | 300 | Corte tras esta cantidad de generaciones sin mejorar el mejor fitness |
| `sesgo_color_inicial` | falso | Si la generación 0 toma el color de la zona de la imagen donde cae cada figura |
| `random_seed` | 42 | Semilla de la que derivan todos los sorteos |

---

### `src/config.py`

Único punto donde se lee y se valida la configuración. Todo lo que sale de acá se
asume correcto: ningún módulo posterior vuelve a chequear nada.

| Función | Recibe | Devuelve | Qué hace |
|---|---|---|---|
| `cargar_config` | El path del archivo de configuración y un diccionario de overrides con valores en texto | Un diccionario con la configuración final, ya convertida a sus tipos | Lee el archivo, aplica los overrides, valida y devuelve |

**Comportamiento de `cargar_config`:**

1. Abre el archivo. Si no existe, corta con un mensaje que diga qué path se
   intentó abrir.
2. Ignora cualquier clave que empiece con guión bajo. Permite dejar bloques de
   notas dentro del archivo sin que se validen.
3. Para cada override: si el nombre no existe en el archivo base, corta y muestra
   el nombre recibido junto con los nombres válidos.
4. Convierte cada override del texto al tipo que ya tenía ese campo en el
   archivo. Los booleanos aceptan las palabras `true` y `false` sin distinguir
   mayúsculas y rechazan cualquier otra cosa. Las listas se interpretan como
   JSON.
5. Valida el resultado según la tabla de abajo. Ante cualquier incumplimiento
   corta nombrando el campo y la condición que no se cumplió.
6. Devuelve el diccionario.

**Validaciones:**

| Campo | Condición |
|---|---|
| `gene_count`, `population_size`, `selected_count`, `tournament_size`, `max_genes_to_mutate`, `max_generations`, `stale_content_generation_cutoff` | Entero mayor o igual a 1 |
| `selected_count` | Además, par |
| `tournament_size` | Además, menor o igual que `population_size` |
| `max_genes_to_mutate` | Además, menor o igual que `gene_count` |
| `tournament_threshold` | Entre 0.5 y 1, inclusive |
| `extra_gene_Pm`, `intra_gene_Pm`, `fitness_cutoff` | Entre 0 y 1, inclusive |
| `temperature`, `output_resolution_mult` | Mayor estricto que 0 |
| Los cinco `max_*_delta` y `max_coord_overflow` | Mayor o igual a 0 |
| `gene_type` | Uno de: triangle, quad, pentagon, oval, png |
| `seleccion` | Uno de: elite, ruleta, universal, boltzmann, torneo_deterministico, torneo_probabilistico, ranking |
| `cruza` | Uno de: un_punto, dos_puntos, uniforme, anular |
| `mutacion` | Uno de: gen, multigen, uniforme, no_uniforme |
| `supervivencia` | Uno de: aditiva, exclusiva |
| `background_color` | Cuatro enteros entre 0 y 255 |
| `sesgo_color_inicial` | Booleano |
| `random_seed` | Entero |
| — | No sobra ninguna clave desconocida |

`selected_count` tiene que ser par porque los padres se cruzan de a pares y cada
par produce dos hijos.

**Invariantes:**
- Si la función devuelve, la configuración es utilizable sin más chequeos.
- Ningún valor sale como texto salvo los que son texto por naturaleza.
- La función no lee los argumentos del programa ni toca el disco fuera del path
  que recibe.

---

### `src/cli.py`

Traduce los argumentos del programa a datos. No sabe qué campos de configuración
existen ni qué valores son válidos: eso es responsabilidad de `config.py`.

| Función | Recibe | Devuelve | Qué hace |
|---|---|---|---|
| `parsear_args` | La lista de argumentos, sin el nombre del programa | El path de configuración, el path de resultados, el path de imágenes, si está activo el volcado completo, y el diccionario de overrides en texto | Recorre los argumentos y los clasifica |

**Comportamiento de `parsear_args`:**

1. Reconoce cuatro flags estructurales, escritos con guión medio:
   `--config-path` (por defecto `config/conf.json`), `--result-path` (por
   defecto `results`), `--img-path` (por defecto `img`) y `--save-all`, que es
   booleano y no lleva valor.
2. Cualquier otro argumento con forma de nombre y valor se guarda como override,
   con el nombre tal cual vino y el valor sin convertir.
3. Cualquier argumento que no tenga ninguna de esas dos formas corta mostrando el
   argumento recibido y las formas aceptadas.

**Regla de nombres.** Los flags estructurales usan guión medio. Los overrides de
configuración usan exactamente el nombre del campo, con guión bajo:
`--output_resolution_mult=0.25`, no `--output-resolution-mult=0.25`. Sin esta
regla no hay forma de distinguir un flag estructural de un override sin que
`cli.py` conozca el esquema.

**Invariantes:**
- No importa `config.py` ni ningún otro módulo del proyecto.
- No convierte tipos: todos los valores de override salen como texto.

---

## 4. Interfaces de otras fases

Ninguna: esta fase no usa código de otras fases.

---

## 5. Decisiones ya tomadas

| Decisión | Motivo |
|---|---|
| El color del lienzo es configurable en vez de blanco fijo | Con figuras translúcidas el fondo entra directamente en el fitness, y comparar fondo blanco contra otro color es un experimento barato para la presentación |
| `max_generations` existe como campo propio | La consigna pide corte por cantidad máxima de generaciones y no había ningún campo que lo cubriera |
| Toda la validación vive en `config.py` | Un solo lugar donde la configuración puede fallar. Los módulos del motor asumen que lo que reciben es válido |
| Los tipos se deducen del archivo base y no de una tabla aparte | Una tabla de tipos duplicada se desincroniza cada vez que se agrega un campo |
| Flags estructurales con guión medio, overrides con guión bajo | Es la única forma de distinguirlos sin una lista blanca en `cli.py` |
| `cli.py` no valida nombres de override | Separa interpretación de validación |

---

## 6. Decisiones abiertas

- **Imagen de prueba además de la definitiva.** La configuración apunta a
  `resources/lebron.png`, que es la imagen de los resultados finales. Conviene
  dejar además una imagen simple, con pocos colores planos y bordes rectos, para
  las pruebas de integración: sobre una cara el motor tarda muchas generaciones
  en mostrar progreso visible, y eso hace lento detectar si algo está mal.

---

## 7. Checkpoints obligatorios

Ninguno: esta fase no produce archivos que calculen. `config.py` compara valores
contra rangos, pero no pondera, estima ni puntúa nada.

---

## 8. Cómo se verifica

| # | Qué se prueba | Entrada | Resultado esperado |
|---|---|---|---|
| 1 | Carga limpia | El archivo por defecto, sin overrides | Devuelve todos los campos, cada uno en su tipo |
| 2 | Override numérico | `gene_count` con el texto 30 | Queda como el entero 30 |
| 3 | Override booleano | `sesgo_color_inicial` con el texto `false` | Queda como falso, no como texto ni como verdadero |
| 4 | Override desconocido | Un campo mal escrito | Corta, y el mensaje incluye el nombre recibido |
| 5 | Rango inválido | `tournament_threshold` en 0.2 | Corta nombrando el campo |
| 6 | Valor de lista cerrada inválido | `seleccion` con un valor inexistente | Corta listando los valores válidos |
| 7 | Paridad | `selected_count` impar | Corta |
| 8 | Campo faltante | Un archivo al que se le borró `temperature` | Corta nombrando `temperature` |
| 9 | Clasificación de argumentos | Un path de configuración, el flag de volcado completo y un override | Devuelve el path, los dos paths por defecto, verdadero, y el override sin convertir |
| 10 | Argumento mal formado | Un argumento con un solo guión | Corta |
| 11 | Clave de notas | Un archivo con una clave que empieza con guión bajo | Se ignora y no rompe la validación |

---

## 9. Errores probables

- **Convertir un texto a booleano con la conversión genérica por tipo** → tanto
  `true` como `false` dan verdadero, porque cualquier texto no vacío es verdadero
  → se detecta con la verificación 3.
- **Validar rangos antes de convertir tipos** → se comparan textos contra
  números → el orden es siempre convertir primero, validar después.
- **Que `config.py` y `cli.py` se importen entre sí** → dependencia circular y
  responsabilidades mezcladas → los une `main.py` en la fase 10, no se conocen
  entre ellos.
- **Aceptar los overrides también con guión medio** → hay dos formas de escribir
  el mismo parámetro y una falla en silencio → los overrides usan exclusivamente
  el nombre exacto del campo.
- **Carpetas vacías que git no versiona** → `results/` e `img/` desaparecen al
  clonar y el motor falla al escribir → van con `.gitkeep`.

---

## 10. Cierre de la fase

- [ ] Todos los archivos de la sección 2 existen y se importan sin error
- [ ] Todas las verificaciones de la sección 8 pasan
- [ ] `docs/resumenes/FASE_00_RESUMEN.md` está escrito
- [ ] No se tocó ningún archivo fuera de la lista
- [ ] El agente no commiteó ni pusheó nada
