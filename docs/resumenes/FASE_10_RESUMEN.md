# Resumen Fase 10 — Integración end-to-end y README

---

## Qué hace esta fase

Antes existían los módulos del motor, la configuración y el output como piezas
independientes. Ahora existe **`main.py`**, el punto de entrada oficial para
ejecutar la aplicación completa desde la línea de comandos, con feedback en vivo
de una sola línea (`\r`), captura limpia de interrupción de usuario (`Ctrl+C`),
y persistencia automática de reportes y figuras. Se incluye además el
`README.md` del repositorio con la documentación integral de uso.

---

## Archivos

| Archivo | Qué hace |
|---|---|
| `main.py` | CLI principal: parsea argumentos, ejecuta el motor con barra de progreso y guarda salidas |
| `README.md` | Documentación general del proyecto: instalación, ejecución, configuración y salidas |

---

## Archivo por archivo

### `main.py`

Punto de entrada de la aplicación.

| Función | Recibe | Devuelve | Qué hace |
|---|---|---|---|
| `main()` | — | — | Orquesta la lectura de CLI, corrida del motor y generación de salidas |
| `callback_progreso(poblacion, registro)` | Población y registro de la generación | — | Actualiza la línea de progreso en la consola con `\r` |

**`main()`** — lee `sys.argv[1:]`, valida la configuración combinando el archivo
base con cualquier override por parámetro (soportando `--config_file`,
`--save-all` y nombres con guiones medios o bajos indistintamente). Instala el
callback de progreso en vivo y ejecuta el motor. Al finalizar (o ante un `Ctrl+C`),
imprime el resumen en la terminal e invoca a `guardar_salidas(...)` de la fase 09.

**`callback_progreso(...)`** — diseñado para no ralentizar el bucle de simulación:
calcula el delta de fitness frente a la generación previa, el contador de
estancamiento y las generaciones por segundo, refrescando una única línea en la
pantalla con `sys.stdout.write` y retorno de carro `\r`.

---

## Cómo comprobar que anda

```bash
python3 main.py --max-generations=20 --population-size=20 --selected-count=20 --gene-count=25 --tournament-size=3 --max-genes-to-mutate=5 --sesgo-color-inicial=true
```

Tiene que correr mostrando la barra de progreso en vivo en una sola línea,
terminar reportando las estadísticas generales, y dejar los archivos en `results/`
e `img/`.

---

## Decisiones y pendientes

**Decisiones**
- **Soporte de guiones medios y bajos.** En `src/cli.py` se normalizan los
  nombres de override reemplazando `-` por `_`, de forma que `--max-generations`
  y `--max_generations` funcionen de manera equivalente.
- **Interrupción limpia con `Ctrl+C`.** Si el usuario interrumpe la simulación,
  se atrapa `KeyboardInterrupt`, se finaliza el motor con motivo
  `interrupcion_usuario` y se procede al guardado de todos los archivos
  generados hasta ese instante sin perder datos.
- **Progreso no invasivo.** El callback actualiza en la misma línea con `\r` sin
  hacer saltos de línea continuos ni llamadas costosas a renderizado en cada frame.
