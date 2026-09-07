# Resumen Fase 12 — Experimentación y gráficos

---

## Qué hace esta fase

Antes existía el motor completo con `main.py` y la suite de tests unitarios, pero
no había una herramienta para automatizar corridas comparativas de operadores ni
para graficar resultados de manera reproducible. Ahora existe `analyze.py`, un
orquestador único que lee `analyze-conf.json`, ejecuta pruebas aisladas de
operadores genéticos o simulaciones evolutivas completas a escala de 100 genes,
calcula estadísticas de rendimiento y genera gráficos comparativos concisos y
prolijos con matplotlib en `./results/analysis/`.

---

## Archivos

| Archivo | Qué hace |
|---|---|
| `analyze.py` | CLI de análisis: ejecuta benchmarks de operadores y corridas completas generando gráficos comparativos |
| `analyze-conf.json` | Configuración activa con la suite de pruebas del hilo conductor (operadores aislados y corridas evolutivas) |
| `analyze-conf.example.json` | Plantilla documentada con la estructura y opciones de configuración de análisis |

---

## Archivo por archivo

### `analyze.py`

Punto de entrada único para la experimentación, benchmarks y generación de gráficos.

| Función | Recibe | Devuelve | Qué hace |
|---|---|---|---|
| `parsear_argumentos_cli(args)` | Argumentos de línea de comandos | Diccionario | Extrae opciones de configuración, experimento, tipo y semilla |
| `cargar_configuracion_analisis(ruta_archivo)` | Ruta al JSON | Diccionario | Carga y valida el archivo de análisis |
| `resolver_semilla(config_analisis, opciones_cli)` | Configuración y opciones | Entero | Devuelve la semilla fija o genera una aleatoria si se solicitó |
| `configurar_estilo_graficos()` | — | — | Aplica estilos globales sobrios en matplotlib |
| `ejecutar_benchmark_seleccion(...)` | Experimento, ruta de salida, semilla y base | — | Evalúa frecuencias de selección empíricas sobre población sintética fija |
| `ejecutar_benchmark_cruza(...)` | Experimento, ruta de salida, semilla y base | — | Evalúa cantidad de loci transferidos y probabilidad de cruce por posición |
| `ejecutar_benchmark_mutacion(...)` | Experimento, ruta de salida, semilla y base | — | Evalúa cantidad y distribución de genes mutados por individuo |
| `ejecutar_benchmark_supervivencia(...)` | Experimento, ruta de salida, semilla y base | — | Evalúa preservación de padres vs hijos bajo aditiva y exclusiva |
| `ejecutar_benchmark_render(...)` | Experimento, ruta de salida, semilla y base | — | Mide tiempo de renderizado y FPS para 100 figuras de cada tipo |
| `ejecutar_experimento_completo(...)` | Experimento, ruta de salida, semilla y base | — | Ejecuta `main.py` por subproceso para cada variante del experimento |
| `generar_graficos_completos(...)` | Métricas de variantes, ruta y salidas | — | Grafica fitness, diversidad y tiempos de la simulación evolutiva |
| `main()` | — | — | Orquesta la lectura de opciones, ejecución de pruebas y reporte final |

**`ejecutar_benchmark_seleccion(...)`** — crea una población sintética de 100
individuos con aptitudes distribuidas entre 1e-4 y 1e-3, corre cada método de
selección 1000 veces y calcula la frecuencia relativa con la que cada ranking es
elegido. Permite visualizar con claridad la presión selectiva de cada método.

**`ejecutar_experimento_completo(...)`** — corre cada variante llamando a
`main.py` mediante un subproceso aislado con sus parámetros de CLI propios. Evita
fugas de memoria o colisiones de procesos de multiprocessing entre corridas
sucesivas.

### `analyze-conf.json`

Define la suite completa de pruebas organizada según el hilo conductor de 6
etapas en escala de 100 genes, incluyendo pruebas aisladas de operadores (rápidas
por defecto) y pruebas evolutivas completas de 30 generaciones.

### `analyze-conf.example.json`

Documenta la sintaxis permitida para definir experimentos arbitrarios,
especificando tipo (`operator` o `full`), parámetros base, variantes a contrastar,
semilla fija o aleatoria (`use_random_seed`) y tipos de gráficos a generar.

---

## Cómo comprobar que anda

```bash
python3 analyze.py --type=operator
```

Tiene que ejecutar los 5 benchmarks aislados de operadores en pocos segundos y
generar en `results/analysis/` las carpetas `op_01_seleccion` a `op_05_figuras_render`
con sus respectivos gráficos PNG, CSVs y archivos `resumen.json`.

Para correr una prueba evolutiva completa de 30 generaciones a 100 genes:

```bash
python3 analyze.py --experiment=full_01_inicializacion
```

Tiene que correr las 3 variantes (aleatoria, bounding box y exact match) por
subproceso y generar los gráficos comparativos de convergencia y tiempos.

---

## Decisiones y pendientes

**Decisiones**
- **Aislamiento por subproceso en corridas completas.** Las pruebas completas
  invocan a `main.py` por subproceso para garantizar que la memoria y los pools
  de multiprocessing de cada variante queden completamente limpios.
- **Gráficos sobrios sin overlay de texto ni em dashes.** Se configuró un estilo
  conciso en matplotlib con títulos descriptivos directos, ejes limpios y grilla
  tenue, sin textos intrusivos.
- **Soporte de semilla fija o estocástica.** Se incluye la opción `use_random_seed`
  en `analyze-conf.json` y el flag `--random-seed` por CLI para alternar entre
  reproducibilidad determinística y corridas aleatorias.
- **Valores por defecto rápidos.** La suite se dimensionó en escala de 100 genes
  con `output_resolution_mult: 0.3` para iterar en segundos.
