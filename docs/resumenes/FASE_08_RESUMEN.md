# Resumen Fase 08 — Inicialización, registro y motor

---

## Qué hace esta fase

Antes existían todas las piezas genéticas por separado (figuras, renderizador,
fitness, individuo, población, selección, cruza, mutación y supervivencia).
Ahora existe el **motor** que las conecta en el ciclo evolutivo completo:
crea la población inicial (uniforme o con sesgo de color hacia el objetivo),
orquesta selección, cruza, mutación y supervivencia iteración a iteración,
recolecta métricas de fitness y diversidad por generación en memoria, y corta
la búsqueda ante cualquiera de los tres criterios de parada (generaciones
máximas, fitness objetivo o estancamiento con tolerancia epsilon).

---

## Archivos

| Archivo | Qué hace |
|---|---|
| `src/inicializacion.py` | Construye la población inicial (generación 0) con o sin sesgo de color |
| `src/registro.py` | `RegistroGeneracion` y `RegistroCorrida`: acumula métricas, tiempos y genomas |
| `src/motor.py` | `ejecutar_motor`: orquesta el ciclo generacional y los criterios de corte |

---

## Archivo por archivo

### `src/inicializacion.py`

Crea los `population_size` individuos iniciales respetando los rangos válidos del genotipo.

| Función | Recibe | Devuelve | Qué hace |
|---|---|---|---|
| `inicializar_poblacion(config, objetivo, ancho, alto, azar)` | Configuración, imagen objetivo, dimensiones y generador | `Poblacion` (generación 0) | Muestrea figuras al azar y aplica sesgo si está activo |
| `_aplicar_sesgo_color(figura, tipo_sesgo, objetivo, ancho, alto, azar)` | Figura, método de sesgo, objetivo y dimensiones | `Figura` | Modifica el RGB según la región y sortea alfa |
| `_color_bounding_box(figura, objetivo, ancho, alto)` | Figura, objetivo y dimensiones | Vector RGB float | Promedio de píxeles en la caja contenedora de la figura |
| `_color_exact_match(figura, objetivo, ancho, alto)` | Figura, objetivo y dimensiones | Vector RGB float | Promedio de píxeles sobre la máscara exacta de la figura |

**`inicializar_poblacion(...)`** — si `sesgo_color_inicial` es falso, cada figura
se muestrea uniformemente dentro de su dominio con `Figura.aleatoria`. Si es
verdadero, toma la geometría generada y computa el RGB promedio de la región
del objetivo que cubre: con `bounding_box` promedia la caja recortada al lienzo,
mientras que con `exact_match` rasteriza una máscara monocromática del polígono
u óvalo para promediar solo sus píxeles interiores. Si una figura queda fuera
del lienzo, toma el píxel más cercano. El canal alfa se sortea al azar entre 0
y 255 para mantener la exploración de transparencias.

---

### `src/registro.py`

Contenedores de datos en memoria para alimentar la salida de la fase 09.

| Clase / Método | Recibe | Devuelve | Qué hace |
|---|---|---|---|
| `RegistroGeneracion(...)` | Métricas de la generación | Instancia | Estructura inmutable con `__slots__` |
| `RegistroCorrida(config, save_all)` | Configuración y bandera de volcado | Instancia | Acumulador de generaciones e historial |
| `iniciar()` | — | — | Guarda la marca de tiempo inicial |
| `registrar_generacion(...)` | Métricas y lista de individuos | — | Añade la generación y actualiza el mejor histórico |
| `finalizar(motivo_fin)` | Motivo de corte | — | Guarda la marca de tiempo final y causa |

**`RegistroCorrida`** — almacena la lista de `RegistroGeneracion`, el mejor
individuo histórico (copiado profundamente para preservar su genotipo intacto)
y calcula el tiempo total de ejecución. Si `save_all=True`, extrae el vector de
parámetros de todos los individuos de cada generación para su exportación a CSV.

---

### `src/motor.py`

Coordina el flujo principal del algoritmo genético.

| Función | Recibe | Devuelve | Qué hace |
|---|---|---|---|
| `ejecutar_motor(config, save_all=False, callback_generacion=None, ...)` | Configuración y parámetros opcionales | `(registro, mejor_individuo)` | Corre el ciclo generacional completo |

**`ejecutar_motor(...)`** — ciclo generacional:
1. Inicializa generador pseudoaleatorio, carga imagen objetivo y recursos, y define el evaluador de fitness contra el fenotipo renderizado.
2. Despacha por nombre los módulos de selección, cruza, mutación y supervivencia configurados.
3. Inicializa la generación 0 y evalúa a sus individuos.
4. En cada iteración: registra métricas (fitness máx/mín/prom y diversidad normalizada), ejecuta el callback si existe, y verifica los tres criterios de parada:
   - `fit_max >= fitness_cutoff`
   - `fit_max <= mejor_historico + stale_content_epsilon` durante `stale_content_generation_cutoff` generaciones consecutivas.
   - `generacion >= max_generations`
5. Si no corta: selecciona `selected_count` padres, los mezcla aleatoriamente con `azar.shuffle`, los cruza de a pares generando `selected_count` hijos, muta a los hijos en el lugar, los evalúa con el evaluador, y aplica la estrategia de supervivencia (`aditiva` o `exclusiva`) para obtener `population_size` sobrevivientes.
6. Construye `poblacion.siguiente(sobrevivientes)` y reevalúa (donde los sobrevivientes no mutados conservan su fitness cacheado sin re-renderizar).

**Regla que si alguien la borra rompe algo.** Los hijos recién mutados se
evalúan con `hijo.fitness(evaluador)` antes de llamar a la supervivencia. La
selección exige que todos los candidatos tengan fitness cacheado y no evalúa;
sin este paso, la supervivencia aditiva falla al intentar ranquear al pozo de
padres e hijos mezclados.

---

## Cómo comprobar que anda

```bash
python3 -c "
from PIL import Image
from src.config import cargar_config
from src.motor import ejecutar_motor
from src.renderizador import cargar_objetivo, renderizar, cargar_recursos

config = cargar_config('config/conf.json', {
    'max_generations': '20',
    'population_size': '20',
    'selected_count': '20',
    'gene_count': '30',
    'tournament_size': '3',
    'max_genes_to_mutate': '5',
    'sesgo_color_inicial': 'true',
})

registro, mejor = ejecutar_motor(config)
assert registro.motivo_fin == 'max_generations'
assert registro.cantidad_generaciones == 21

objetivo, w, h = cargar_objetivo(config)
recursos = cargar_recursos(config)
matriz = renderizar(mejor.genes, w, h, config, recursos)
Image.fromarray(matriz).save('img/prueba_fase_08.png')
print('Verificación exitosa: 20 generaciones completadas y figura guardada en img/prueba_fase_08.png')
"
```

Tiene que imprimir `Verificación exitosa...`, terminar en menos de 2 segundos,
y generar `img/prueba_fase_08.png` donde se observa cómo los triángulos ya
toman los tonos y la forma aproximada de la imagen objetivo.

---

## Decisiones y pendientes

**Decisiones**
- **Apareamiento con mezcla previa de padres.** Los padres seleccionados se
  mezclan con `azar.shuffle` antes de cruzarse de a pares. Evita que métodos
  como élite o ranking emparejen siempre a los mejores entre sí.
- **Evaluación previa a la supervivencia.** Los hijos se evalúan justo después de
  mutar. Permite que la supervivencia aditiva use cualquier método de selección
  sin violar la invariante de que la selección solo lee aptitudes ya cacheadas.
- **Soporte de dos modalidades de sesgo.** Se implementó `bounding_box`
  (ultrarrápido, promediando la caja contenedora de la figura) y `exact_match`
  (promediando solo los píxeles interiores reales mediante máscara).
- **Parámetro `stale_content_epsilon`.** Se agregó a la configuración con
  valor por defecto 0.0 para poder definir una tolerancia mínima de mejora en
  el criterio de estancamiento.
- **`conf-example.json` y regla 8.** Se documentaron todas las variables del
  sistema con sus valores posibles y notas concisas, fijando en `docs/reglas.md`
  que cualquier cambio en la configuración exige actualizar el ejemplo.

**Pendientes**
- La fase 09 (`src/output.py`) consumirá el `RegistroCorrida` para generar los
  CSVs en `results/`, el GIF animado y las imágenes por generación en `img/`, y
  el `resumen.txt`.
