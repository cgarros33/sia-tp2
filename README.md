# TP2 — Sistemas de Inteligencia Artificial (ITBA)

Aproximación a imágenes con figuras geométricas translúcidas mediante un motor de Algoritmos Genéticos.

---

## Requisitos

- Python 3.11+
- Dependencias: `numpy`, `scipy`, `pillow`

Instalación:
```bash
pip install numpy scipy pillow
```

---

## Ejecución

El programa principal se ejecuta con `main.py`:

```bash
python3 main.py
```

Por defecto lee la configuración desde `config/conf.json`.

### Flags de línea de comandos

- `--config-path=<path>` o `--config_file=<path>`: Ruta a un archivo JSON de configuración alternativo (por defecto: `config/conf.json`).
- `--result-path=<path>`: Carpeta de destino para las métricas y reportes (por defecto: `results/`).
- `--img-path=<path>`: Carpeta de destino para las imágenes y animaciones (por defecto: `img/`).
- `--save-all`: Exporta el registro completo de todos los genomas de todos los individuos de todas las generaciones en `genomas.csv`.
- `--<nombre_parametro>=<valor>`: Permite sobreescribir cualquier variable de configuración puntualmente, tanto con guiones medios (`--max-generations=200`) como con guiones bajos (`--max_generations=200`).

### Ejemplos de uso

Ejecución rápida con overrides directos:
```bash
python3 main.py --max-generations=50 --population-size=30 --gene-count=50 --sesgo-color-inicial=true
```

Ejecutar con otro archivo de configuración y volcado completo:
```bash
python3 main.py --config_file=config/conf-example.json --save-all
```

Probar con otra figura (por ejemplo, óvalos o cuadriláteros):
```bash
python3 main.py --gene-type=oval --gene-count=40 --max-generations=100
```

---

## Opciones de Configuración

Todas las variables de configuración se detallan con ejemplos en `config/conf-example.json`.

- **Figuras disponibles (`gene_type`):**
  - `triangle`: Triángulos (figura estándar).
  - `quad`: Cuadriláteros de 4 vértices.
  - `pentagon`: Pentágonos de 5 vértices.
  - `oval`: Óvalos / elipses con centro, radios y rotación.
  - `png`: Imagen PNG externa reescalada, teñida y rotada.
- **Métodos de selección (`seleccion`):**
  - `elite`, `ruleta`, `universal`, `boltzmann`, `torneo_deterministico`, `torneo_probabilistico`, `ranking`.
- **Métodos de cruza (`cruza`):**
  - `un_punto`, `dos_puntos`, `uniforme`, `anular`.
- **Métodos de mutación (`mutacion`):**
  - `gen`, `multigen`, `uniforme`, `no_uniforme`.
- **Estrategias de supervivencia (`supervivencia`):**
  - `aditiva`: Los padres compiten junto con los hijos para la siguiente generación.
  - `exclusiva`: La siguiente generación se forma exclusivamente con los hijos (completando con padres solo si faltan).
- **Criterios de corte:**
  - `max_generations`: Cantidad máxima de generaciones.
  - `fitness_cutoff`: Nivel de fitness para terminar por óptimo.
  - `stale_content_generation_cutoff`: Generaciones consecutivas sin una mejora mayor a `stale_content_epsilon` en el mejor fitness histórico.
- **Sesgo de color inicial:**
  - `sesgo_color_inicial` (`true`/`false`): Inicializa el color de las figuras promediando la región correspondiente de la imagen objetivo.
  - `tipo_sesgo_color`: `bounding_box` (caja contenedora, muy rápido) o `exact_match` (máscara de píxeles exacta de la figura).
- **Visualización y renderizado:**
  - `gif_gen_interval`: Intervalo de generaciones para incluir frames en el GIF animado.
  - `save_best`: Guarda en PNG la mejor aproximación al finalizar la corrida.
  - `best_resolution_multiplier`: Multiplicador vectorial para exportar la imagen final en mayor resolución.

---

## Archivos de Salida

Tras la corrida, el programa genera automáticamente:

1. En la carpeta de resultados (`results/`):
   - `metricas.csv`: Tabla con `generacion`, `fitness_maximo`, `fitness_minimo`, `fitness_promedio`, `diversidad` y `tiempo_generacion`.
   - `resumen.txt`: Reporte con metadatos de la corrida (tiempos, fitness final, motivo de corte y configuración completa).
   - `genomas.csv` (solo si se pasa `--save-all`): Parámetros numéricos de cada individuo generación por generación.
2. En la carpeta de imágenes (`img/`):
   - `<imagen>.gif`: GIF animado mostrando la evolución del mejor fenotipo generación a generación.
   - `best_<imagen>.png`: PNG renderizado en alta resolución del mejor individuo obtenido en la corrida.

---

## Interrupción de la Simulación

Si se desea detener la simulación antes de que cumpla los criterios de parada, se puede presionar `Ctrl + C`. El motor atrapará la señal de forma limpia y generará todos los reportes, el GIF y la imagen del mejor individuo hasta la generación alcanzada, indicando `interrupcion_usuario` como motivo de finalización.