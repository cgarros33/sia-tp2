# Resumen Fase 00 — Andamiaje, configuración y CLI

---

## Qué hace esta fase

Antes de esta fase el repositorio tenía documentación y una imagen. Ahora tiene
la estructura de carpetas completa (`src/`, `config/`, `results/`, `img/`,
`tests/`, `analisis/`), un archivo de configuración con los 28 parámetros que el
motor va a necesitar, y los dos módulos que permiten arrancar una corrida: uno
que lee y valida la configuración y otro que interpreta los argumentos de línea
de comandos. Todavía no hay nada de algoritmo genético: no hay figuras, ni
renderizado, ni fitness. Lo que sí hay es la garantía de que cualquier fase
posterior recibe una configuración completa, con cada valor en su tipo y dentro
de su rango, sin tener que volver a chequear nada.

La división entre los dos módulos es a propósito y es lo que hace que no se
pisen. `cli.py` sólo separa el texto de la línea de comandos en categorías: no
sabe qué campos de configuración existen ni qué valores son aceptables.
`config.py` sólo valida: no sabe que existe una línea de comandos. Ninguno de
los dos importa al otro; los une `main.py` en la fase 10.

---

## Archivos

| Archivo | Qué hace |
|---|---|
| `src/__init__.py` | Vacío. Marca `src` como paquete de Python |
| `src/config.py` | Carga el JSON de configuración, aplica los overrides, valida todo y devuelve el diccionario |
| `src/cli.py` | Separa `argv` en tres paths, el flag de volcado completo y los overrides sin convertir |
| `config/conf.json` | Los 28 parámetros por defecto de una corrida |
| `resources/.gitkeep` | Sostiene la carpeta de la imagen objetivo y del PNG de overlay |
| `results/.gitkeep` | Sostiene la carpeta de salida de CSV y `resumen.txt` |
| `img/.gitkeep` | Sostiene la carpeta de salida de frames y GIF |
| `tests/.gitkeep` | Sostiene la carpeta de la suite de tests de la fase 11 |
| `analisis/.gitkeep` | Sostiene la carpeta de scripts de experimentación de la fase 12 |

Los `.gitkeep` existen porque git no versiona carpetas vacías: sin ellos, al
clonar el repositorio `results/` e `img/` no aparecen y el motor falla al
intentar escribir su salida.

---

## Archivo por archivo

### `config/conf.json`

Un único objeto JSON, sin anidamiento, con los 28 campos que consume el motor.
Todos son obligatorios: no hay valores implícitos en el código, si un campo falta
la carga corta. Los valores que están puestos son un punto de partida razonable,
no un resultado experimental; se ajustan en la fase 12.

Los campos se agrupan así:

- **Problema:** `gene_count`, `file_input`, `gene_type`, `overlay_source`,
  `background_color`, `output_resolution_mult`.
- **Métodos a usar:** `seleccion`, `cruza`, `mutacion`, `supervivencia`.
- **Población y selección:** `population_size`, `selected_count`,
  `tournament_size`, `tournament_threshold`, `temperature`.
- **Mutación:** `extra_gene_Pm`, `intra_gene_Pm`, `max_genes_to_mutate`,
  `max_coord_delta`, `max_color_delta`, `max_rotation_delta`,
  `max_radius_delta`, `max_coord_overflow`.
- **Corte y reproducibilidad:** `max_generations`, `fitness_cutoff`,
  `stale_content_generation_cutoff`, `sesgo_color_inicial`, `random_seed`.

Cualquier clave que empiece con guión bajo se descarta al cargar. Sirve para
dejar bloques de notas dentro del archivo, ya que JSON no tiene comentarios.

**Este archivo lo toca solamente la fase 00.** Si una fase posterior necesita un
campo nuevo, lo pide; no lo agrega por su cuenta. Es la regla que evita que
cuatro personas trabajando en paralelo se pisen el archivo de configuración.

---

### `src/config.py`

Es el único lugar del proyecto donde la configuración puede fallar. Si
`cargar_config` devuelve, lo que devolvió es usable tal cual: ningún módulo
posterior vuelve a chequear tipos ni rangos.

| Función | Recibe | Devuelve | Qué hace |
|---|---|---|---|
| `cargar_config(path_config, overrides)` | El path del archivo y un diccionario `{nombre: texto}` | La configuración final, cada valor en su tipo | Lee, aplica overrides, valida y devuelve |
| `_leer_archivo(path_config)` | El path del archivo | El JSON como diccionario, sin las claves de notas | Abre, parsea y filtra las claves que empiezan con guión bajo |
| `_convertir(nombre, texto, valor_base)` | Nombre del campo, el override en texto y el valor que ese campo tiene en el archivo | El valor convertido | Deduce el tipo del valor del archivo y convierte el texto a ese tipo |
| `_validar(config)` | La configuración ya convertida | Nada | Corta ante el primer campo que no cumple su condición |
| `_validar_campos_presentes(config)` | La configuración | Nada | Exige que estén los 28 campos y ninguno más |
| `_validar_color_de_fondo(config)` | La configuración | Nada | Exige cuatro enteros entre 0 y 255 |
| `_exigir_entero`, `_exigir_numero`, `_exigir_rango`, `_exigir_opcion` | La configuración y el nombre del campo | Nada | Chequeos elementales reutilizados por `_validar` |

**`cargar_config(path_config, overrides)`** — el orden de los cuatro pasos
importa y no es intercambiable. Primero lee el archivo y descarta las claves de
notas, porque el archivo ya filtrado es lo que define qué nombres de override son
legítimos. Segundo, para cada override chequea que el nombre exista en el archivo
y lo convierte al tipo que ese campo ya tenía. Tercero valida. Cuarto devuelve.
Convertir antes de validar es obligatorio: si se validara primero, se estarían
comparando textos contra números y todos los rangos darían cualquier cosa.

**`_convertir(nombre, texto, valor_base)`** — no hay una tabla de tipos: el tipo
sale del valor que el campo tiene en el archivo base. Una tabla duplicada se
desincroniza la primera vez que alguien agrega un campo. Los booleanos se tratan
aparte y sólo aceptan las palabras `true` y `false` sin distinguir mayúsculas,
porque la conversión genérica `bool("false")` da verdadero y el override quedaría
silenciosamente al revés. Las listas y objetos se interpretan como JSON, así que
`--background_color=[0,0,0,255]` funciona. El texto se pasa tal cual. El resto
usa el constructor del tipo del valor base.

**`_validar(config)`** — implementa la tabla de validaciones del documento de
fase. Enteros mayores o iguales a 1 para las siete cantidades;
`selected_count` además par, porque los padres se cruzan de a pares y cada par
produce dos hijos, así que un número impar dejaría un padre sin pareja;
`tournament_size` no puede superar a `population_size` porque no se puede armar
un torneo con más competidores que individuos hay; `max_genes_to_mutate` no puede
superar a `gene_count` por la misma razón. `tournament_threshold` entre 0.5 y 1
inclusive, que es el intervalo donde el torneo probabilístico favorece al más
apto. Las tres probabilidades entre 0 y 1. `temperature` y
`output_resolution_mult` estrictamente mayores que 0, porque una temperatura de 0
divide por cero en Boltzmann y un multiplicador de 0 da una imagen sin píxeles.
Los cuatro `max_*_delta` y `max_coord_overflow`, mayores o iguales a 0: en 0 el
parámetro queda desactivado, que es un experimento válido. Los cinco campos de
lista cerrada contra sus valores permitidos. `background_color`, cuatro enteros
entre 0 y 255. `file_input` y `overlay_source`, texto no vacío.

**Cuatro cosas que conviene saber de este archivo:**

- **`config.py` no toca el disco fuera del path que recibe.** No verifica que
  `file_input` ni `overlay_source` existan. Que la imagen objetivo esté o no está
  es un problema del renderizador, en la fase 02, no de la validación.
- **La tupla `CAMPOS` es la lista de los 28 nombres esperados** y se usa para dos
  cosas: detectar campos faltantes y detectar campos sobrantes. Es la única
  duplicación respecto del archivo JSON, y es inevitable: sin una lista de
  nombres no hay forma de saber que a un archivo le falta `temperature`.
- **En Python `bool` es subclase de `int`.** Por eso `_exigir_entero` y
  `_exigir_numero` rechazan booleanos explícitamente; sin ese rechazo,
  `"random_seed": true` pasaría la validación como si fuera el entero 1. Y por eso
  en `_convertir` el caso booleano va antes que todo: si se probara `int` primero,
  un campo booleano se convertiría con el constructor equivocado.
- **Los errores son excepciones, no `sys.exit`.** `ErrorDeConfiguracion` lleva un
  mensaje que nombra siempre el campo y la condición que no se cumplió. Quien la
  atrapa, la imprime y sale con código distinto de cero es `main.py`, en la fase
  10. Se eligió así para que la fase 11 pueda testear los fallos.

---

### `src/cli.py`

Traduce los argumentos del programa a datos y nada más. No conoce el esquema de
configuración: no sabe qué campos existen ni qué valores son válidos.

| Función | Recibe | Devuelve | Qué hace |
|---|---|---|---|
| `parsear_args(argumentos)` | La lista de argumentos sin el nombre del programa | `(config_path, result_path, img_path, save_all, overrides)` | Clasifica cada argumento en flag estructural, volcado completo u override |

**`parsear_args(argumentos)`** — reconoce cuatro flags estructurales:
`--config-path=<path>` (por defecto `config/conf.json`), `--result-path=<path>`
(por defecto `results`), `--img-path=<path>` (por defecto `img`) y `--save-all`,
que es booleano y no lleva valor. Todo lo demás con forma `--nombre=valor` se
acumula como override, con el nombre tal cual vino y el valor **sin convertir**,
como texto. Que un nombre de override exista o no es problema de `config.py`.
Cualquier otra forma corta con `ErrorDeArgumentos`, mostrando el argumento
recibido y las formas aceptadas.

**La regla de nombres es lo que hace posible todo esto:** los flags estructurales
se escriben con guión medio y los overrides de configuración con el nombre exacto
del campo, con guión bajo. `--output_resolution_mult=0.25`, nunca
`--output-resolution-mult=0.25`. Sin esa regla no hay forma de distinguir un flag
estructural de un override sin meter una lista blanca de campos dentro de
`cli.py`, que es exactamente la dependencia que se quiere evitar. Si alguien
escribe un override con guión medio, corta y le muestra cómo se escribe.

---

## Cómo comprobar que anda

```bash
python -c "import sys; sys.path.insert(0,'.'); from src.config import cargar_config; c=cargar_config('config/conf.json',{}); print(len(c), c['gene_count'], c['sesgo_color_inicial'])"
python -c "import sys; sys.path.insert(0,'.'); from src.cli import parsear_args; print(parsear_args(['--config-path=config/conf.json','--save-all','--gene_count=30']))"
python -c "import sys; sys.path.insert(0,'.'); from src.config import cargar_config; cargar_config('config/conf.json',{'selected_count':'99'})"
```

Lo que tiene que pasar:

1. La primera imprime `28 100 False`: los 28 campos, `gene_count` como entero y
   `sesgo_color_inicial` como booleano, no como texto.
2. La segunda imprime
   `('config/conf.json', 'results', 'img', True, {'gene_count': '30'})`: los dos
   paths que no se pasaron quedan en su valor por defecto y el override sale
   como texto.
3. La tercera corta con `ErrorDeConfiguracion` nombrando `selected_count` y
   diciendo que tiene que ser par.

Las once verificaciones de la sección 8 del documento de fase se corrieron una
por una y pasan todas.

---

## Decisiones y pendientes

**Decisiones**

- **`--result-path`, no `--resultpath`.** `docs/contexto.md` escribe
  `--resultpath`; se usa `--result-path` para que los cuatro flags estructurales
  sigan la misma regla de guión medio.
- **`output_resolution_mult` arranca en 0.5, no en 1.** `contexto.md` dice 1 y el
  documento de fase dice 0.5. Se usó 0.5, que es lo que dice el documento de
  fase; renderizar a media resolución es varias veces más rápido y esta constante
  se ajusta en la fase 12 de todos modos.
- **Excepciones propias en cada módulo.** `ErrorDeConfiguracion` en `config.py` y
  `ErrorDeArgumentos` en `cli.py`. No hay un módulo de excepciones compartido
  porque `cli.py` no puede importar nada del proyecto sin romper su aislamiento.
- **La lista de nombres `CAMPOS` vive en `config.py`.** Es la única forma de
  detectar un campo faltante. Los tipos, en cambio, se siguen deduciendo del
  archivo.
- **Un override no puede cambiar el tipo de un campo.** `--max_color_delta=25.5`
  corta, porque en el archivo ese campo es entero. Si en algún momento hace falta
  que sea fraccionario, se cambia el valor del archivo a `25.0` y el override
  empieza a aceptar decimales solo.
- **`--save-all=true` es un error, no un sinónimo de `--save-all`.** El flag no
  lleva valor; aceptar las dos formas es una manera silenciosa de que alguien
  escriba `--save-all=false` y termine con el volcado activado.

**Pendientes**

- **`resources/overlay.png` no existe todavía.** `conf.json` lo apunta por
  defecto, pero como `gene_type` por defecto es `triangle` nunca se usa, y
  `config.py` no mira el disco, así que no rompe nada en esta fase. Lo va a
  necesitar la fase 01 cuando implemente el gen de tipo `png`.
- **Falta una imagen de prueba simple.** Es la decisión abierta de la sección 6
  del documento de fase. Sobre la cara de `lebron.png` el motor tarda muchas
  generaciones en mostrar progreso visible, y eso hace lento detectar si algo
  está mal en la integración. Conviene dejar en `resources/` una imagen con pocos
  colores planos y bordes rectos para las pruebas de la fase 10. Es un archivo
  binario, no se agregó en esta fase.
- **Los valores por defecto no están calibrados.** Son un punto de partida. La
  fase 12 los ajusta con experimentos.
