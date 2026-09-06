# Resumen Fase 09 — Output y métricas de corrida

---

## Qué hace esta fase

Antes el motor calculaba las generaciones y acumulaba los datos únicamente en
memoria dentro de `RegistroCorrida`. Ahora existe el módulo de **output** que
toma ese registro y vuelca todo a disco: genera el archivo `metricas.csv` con las
estadísticas por generación, `resumen.txt` con la metadata de la corrida,
`genomas.csv` con los parámetros completos de todos los individuos si se pidió
`--save-all`, el GIF animado con la evolución generacional del mejor fenotipo
y el PNG en alta resolución del mejor individuo histórico.

---

## Archivos

| Archivo | Qué hace |
|---|---|
| `src/output.py` | Exporta métricas a CSV, metadata a TXT, y renderiza el GIF animado y el mejor PNG |

---

## Archivo por archivo

### `src/output.py`

Persistencia de resultados y renderizado final de la corrida.

| Función | Recibe | Devuelve | Qué hace |
|---|---|---|---|
| `guardar_salidas(registro, config, result_path, img_path, recursos=None)` | Registro, configuración, rutas de salida y recursos | — | Orquesta el guardado de todos los archivos de salida |
| `_guardar_metricas_csv(registro, path)` | Registro y ruta del archivo | — | Escribe las columnas de métricas por generación |
| `_guardar_genomas_csv(registro, path)` | Registro y ruta del archivo | — | Escribe los genomas de todos los individuos si save_all está activo |
| `_guardar_resumen_txt(registro, config, path)` | Registro, configuración y ruta | — | Escribe los metadatos de corrida y JSON de configuración |
| `_guardar_gif_evolucion(...)` | Registro, config, recursos, dimensiones y ruta | — | Arma y guarda el GIF animado según `gif_gen_interval` |
| `_guardar_mejor_png(...)` | Mejor individuo, config, recursos, dimensiones y ruta | — | Renderiza y guarda el PNG escalado según `best_resolution_multiplier` |
| `_escalar_figuras(figuras, multiplicador)` | Lista de figuras y factor de escala | Lista de figuras | Escala las coordenadas vectoriales de polígonos y elipses |

**`guardar_salidas(...)`** — crea las carpetas de destino si no existen y
construye los nombres de imagen en base al nombre del archivo objetivo
(`Path(config['file_input']).stem`). Escribe `metricas.csv` con precisión de
10 decimales en fitness y diversidad. En el GIF solo incluye los frames que
coinciden con `gif_gen_interval` o el frame final, evitando generar archivos
excesivamente pesados.

**`_guardar_mejor_png(...)`** — como las figuras son vectoriales, aprovecha que
el fenotipo se puede renderizar a mayor escala sin pixelación: multiplica las
coordenadas de vértices, centros y radios por `best_resolution_multiplier`
(por defecto 2.0) y genera una imagen en alta resolución de la mejor
aproximación alcanzada.

---

## Cómo comprobar que anda

```bash
python3 -c "
from pathlib import Path
from src.config import cargar_config
from src.motor import ejecutar_motor
from src.output import guardar_salidas

config = cargar_config('config/conf.json', {
    'max_generations': '5',
    'population_size': '10',
    'selected_count': '10',
    'gene_count': '15',
    'tournament_size': '3',
    'max_genes_to_mutate': '5',
})
registro, _ = ejecutar_motor(config, save_all=True)
guardar_salidas(registro, config, 'results', 'img')

assert Path('results/metricas.csv').exists()
assert Path('results/genomas.csv').exists()
assert Path('results/resumen.txt').exists()
assert Path('img/bron500.gif').exists()
assert Path('img/best_bron500.png').exists()
print('Fase 09 verificada correctamente')
"
```

Tiene que imprimir `Fase 09 verificada correctamente` y crear los cinco archivos
en `results/` e `img/`.

---

## Decisiones y pendientes

**Decisiones**
- **Nombres basados en el archivo de entrada.** El GIF y la mejor imagen se
  nombran `<nombre_base>.gif` y `best_<nombre_base>.png` respetando el nombre
  del archivo objetivo en lugar de nombres fijos genéricos.
- **Escalado vectorial de alta resolución.** Se implementó `_escalar_figuras`
  para que el mejor individuo se renderice nítidamente al tamaño definido por
  `best_resolution_multiplier` sin interpolar píxeles sobre la matriz chica.
- **Muestreo configurable del GIF.** Se utiliza `gif_gen_interval` para poder
  espaciar los frames del GIF en corridas de miles de generaciones sin degradar
  la velocidad del renderizado final.
