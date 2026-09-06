"""Punto de entrada principal para ejecutar el motor de algoritmos genéticos."""

import sys
import time
from pathlib import Path

from PIL import Image

from src.cli import ErrorDeArgumentos, parsear_args
from src.config import ErrorDeConfiguracion, cargar_config
from src.motor import ejecutar_motor
from src.output import guardar_salidas
from src.renderizador import (
    ErrorDeImagen,
    cargar_objetivo,
    cargar_recursos,
    renderizar,
)


def main():
    """Coordina la lectura de argumentos, ejecución del motor y persistencia de resultados."""
    try:
        config_path, result_path, img_path, save_all, overrides = parsear_args(
            sys.argv[1:]
        )
        config = cargar_config(config_path, overrides)
    except (ErrorDeArgumentos, ErrorDeConfiguracion) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)

    max_gen = config["max_generations"]
    stale_max = config["stale_content_generation_cutoff"]
    epsilon = config["stale_content_epsilon"]
    intervalo_guardado = config["save_every_n_generations"]
    nombre_base = Path(config["file_input"]).stem
    dir_img = Path(img_path)

    try:
        objetivo, ancho, alto = cargar_objetivo(config)
        recursos = cargar_recursos(config)
    except ErrorDeImagen as error:
        print(f"Error de imagen: {error}", file=sys.stderr)
        sys.exit(1)

    if intervalo_guardado > 0:
        dir_img.mkdir(parents=True, exist_ok=True)

    estado = {
        "anterior": None,
        "mejor_historico": None,
        "sin_mejora": 0,
        "inicio": time.perf_counter(),
    }

    def callback_progreso(poblacion, registro):
        gen = poblacion.generacion
        fit = poblacion.fitness_maximo

        if estado["anterior"] is None:
            delta_str = "=0.000000"
        else:
            delta = fit - estado["anterior"]
            if delta > 0:
                delta_str = f"+{delta:.6f}"
            elif delta < 0:
                delta_str = f"{delta:.6f}"
            else:
                delta_str = "=0.000000"
        estado["anterior"] = fit

        if (
            estado["mejor_historico"] is None
            or fit > estado["mejor_historico"] + epsilon
        ):
            estado["mejor_historico"] = fit
            estado["sin_mejora"] = 0
        else:
            estado["sin_mejora"] += 1

        transcurrido = time.perf_counter() - estado["inicio"]
        vel = (gen + 1) / transcurrido if transcurrido > 0 else 0.0

        linea = (
            f"\r[Gen {gen:04d}/{max_gen:04d}] "
            f"Mejor: {fit:.6f} (Δ {delta_str}) | "
            f"Sin mejora: {estado['sin_mejora']:03d}/{stale_max:03d} | "
            f"{vel:.1f} gen/s"
        )
        sys.stdout.write(linea)
        sys.stdout.flush()

        if intervalo_guardado > 0 and gen % intervalo_guardado == 0:
            ind = registro.mejor_historico or poblacion.mejor()
            matriz = renderizar(ind.genes, ancho, alto, config, recursos)
            Image.fromarray(matriz).save(dir_img / f"current_{nombre_base}.png")

    registro, mejor = ejecutar_motor(
        config,
        save_all=save_all,
        callback_generacion=callback_progreso,
        objetivo=objetivo,
        ancho=ancho,
        alto=alto,
        recursos=recursos,
    )

    sys.stdout.write("\n")
    sys.stdout.flush()

    vel_prom = (
        registro.cantidad_generaciones / registro.tiempo_total
        if registro.tiempo_total > 0
        else 0.0
    )

    print("------------------------------------------------------------")
    print("Simulación finalizada.")
    print(f"Motivo de parada:      {registro.motivo_fin}")
    print(f"Generaciones totales:  {registro.cantidad_generaciones}")
    print(f"Tiempo de corrida:     {registro.tiempo_total:.2f} s ({vel_prom:.1f} gen/s)")
    print(f"Fitness final (mejor): {registro.fitness_final}")
    print("------------------------------------------------------------")
    print("Guardando archivos de salida...")

    estado_img = {
        "inicio": time.perf_counter(),
        "activo": False,
    }

    def callback_progreso_imagen(actual, total, gen):
        estado_img["activo"] = True
        transcurrido = time.perf_counter() - estado_img["inicio"]
        vel = actual / transcurrido if transcurrido > 0 else 0.0
        pct = (actual / total) * 100 if total > 0 else 100.0
        ancho_num = max(4, len(str(total)))
        linea = (
            f"\r[Frame {actual:0{ancho_num}d}/{total:0{ancho_num}d}] "
            f"Gen: {gen:04d} | "
            f"{pct:5.1f}% | "
            f"{vel:.1f} frame/s"
        )
        sys.stdout.write(linea)
        sys.stdout.flush()

    guardar_salidas(
        registro,
        config,
        result_path,
        img_path,
        recursos=recursos,
        callback_progreso=callback_progreso_imagen,
    )

    if estado_img["activo"]:
        sys.stdout.write("\n")
        sys.stdout.flush()

    print(f"Resultados guardados:")
    print(f"  - {result_path}/metricas.csv")
    print(f"  - {result_path}/resumen.txt")
    if save_all:
        print(f"  - {result_path}/genomas.csv")
    print(f"Imágenes guardadas:")
    print(f"  - {img_path}/{nombre_base}.gif")
    if config["save_best"]:
        print(f"  - {img_path}/best_{nombre_base}.png")
    if config["save_every_n_generations"] > 0:
        print(f"  - {img_path}/current_{nombre_base}.png")
    print("------------------------------------------------------------")


if __name__ == "__main__":
    main()
