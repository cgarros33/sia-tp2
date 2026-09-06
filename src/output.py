"""Generación y persistencia de métricas, metadatos, imágenes y animaciones de salida."""

import csv
import json
from pathlib import Path
from PIL import Image

from src.figuras.familias import FiguraElipsoidal, Poligono
from src.renderizador import cargar_objetivo, cargar_recursos, renderizar


def guardar_salidas(registro, config, result_path, img_path, recursos=None):
    """Guarda los archivos CSV, el resumen de texto, el GIF evolutivo y la mejor imagen renderizada."""
    dir_results = Path(result_path)
    dir_img = Path(img_path)
    dir_results.mkdir(parents=True, exist_ok=True)
    dir_img.mkdir(parents=True, exist_ok=True)

    _, ancho, alto = cargar_objetivo(config)
    if recursos is None:
        recursos = cargar_recursos(config)

    nombre_base = Path(config["file_input"]).stem

    _guardar_metricas_csv(registro, dir_results / "metricas.csv")
    if registro.save_all:
        _guardar_genomas_csv(registro, dir_results / "genomas.csv")
    _guardar_resumen_txt(registro, config, dir_results / "resumen.txt")

    _guardar_gif_evolucion(
        registro, config, recursos, ancho, alto, dir_img / f"{nombre_base}.gif"
    )

    if config["save_best"] and registro.mejor_historico is not None:
        _guardar_mejor_png(
            registro.mejor_historico,
            config,
            recursos,
            ancho,
            alto,
            dir_img / f"best_{nombre_base}.png",
        )


def _guardar_metricas_csv(registro, path_archivo):
    """Escribe el historial de métricas generacionales en formato CSV."""
    with open(path_archivo, mode="w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(
            [
                "generacion",
                "fitness_maximo",
                "fitness_minimo",
                "fitness_promedio",
                "diversidad",
                "tiempo_generacion",
            ]
        )
        for gen in registro.historial:
            escritor.writerow(
                [
                    gen.generacion,
                    f"{gen.fitness_maximo:.10f}",
                    f"{gen.fitness_minimo:.10f}",
                    f"{gen.fitness_promedio:.10f}",
                    f"{gen.diversidad:.10f}",
                    f"{gen.tiempo_generacion:.6f}",
                ]
            )


def _guardar_genomas_csv(registro, path_archivo):
    """Escribe el genoma aplanado de cada individuo de cada generación en formato CSV."""
    with open(path_archivo, mode="w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        if registro.historial and registro.historial[0].genomas:
            primer_genoma = registro.historial[0].genomas[0]
            header = ["generacion", "individuo"] + [
                f"p_{i}" for i in range(len(primer_genoma))
            ]
            escritor.writerow(header)

        for gen in registro.historial:
            if gen.genomas is not None:
                for idx, genoma in enumerate(gen.genomas):
                    escritor.writerow([gen.generacion, idx] + list(genoma))


def _guardar_resumen_txt(registro, config, path_archivo):
    """Escribe los metadatos finales de la ejecución en resumen.txt."""
    lineas = [
        "============================================================",
        "              RESUMEN DE EJECUCION DEL MOTOR AG             ",
        "============================================================",
        f"Archivo objetivo:       {config['file_input']}",
        f"Tipo de figura:         {config['gene_type']}",
        f"Cantidad de genes:      {config['gene_count']}",
        f"Tamano poblacion:       {config['population_size']}",
        f"Generaciones totales:   {registro.cantidad_generaciones}",
        f"Tiempo total:           {registro.tiempo_total:.4f} s",
        f"Fitness final (max):    {registro.fitness_final}",
        f"Motivo de finalizacion: {registro.motivo_fin}",
        "------------------------------------------------------------",
        "Configuracion completa:",
        json.dumps(config, indent=2),
        "============================================================",
    ]
    path_archivo.write_text("\n".join(lineas) + "\n", encoding="utf-8")


def _guardar_gif_evolucion(registro, config, recursos, ancho, alto, path_archivo):
    """Renderiza los mejores individuos según el intervalo configurado y genera el GIF animado."""
    if not registro.historial:
        return

    intervalo = config["gif_gen_interval"]
    ultimo_indice = len(registro.historial) - 1
    frames = []

    for indice, gen in enumerate(registro.historial):
        if gen.generacion % intervalo == 0 or indice == ultimo_indice:
            if gen.mejor_individuo is not None:
                matriz = renderizar(
                    gen.mejor_individuo.genes, ancho, alto, config, recursos
                )
                frames.append(Image.fromarray(matriz))

    if frames:
        frames[0].save(
            path_archivo,
            save_all=True,
            append_images=frames[1:],
            duration=100,
            loop=0,
        )


def _guardar_mejor_png(mejor_individuo, config, recursos, ancho, alto, path_archivo):
    """Renderiza el mejor individuo histórico escalado por el multiplicador vectorial y lo guarda en PNG."""
    multiplicador = config["best_resolution_multiplier"]
    if multiplicador == 1.0:
        matriz = renderizar(mejor_individuo.genes, ancho, alto, config, recursos)
    else:
        figuras_escaladas = _escalar_figuras(mejor_individuo.genes, multiplicador)
        ancho_alto = max(1, round(ancho * multiplicador))
        alto_alto = max(1, round(alto * multiplicador))
        matriz = renderizar(
            figuras_escaladas, ancho_alto, alto_alto, config, recursos
        )

    Image.fromarray(matriz).save(path_archivo)


def _escalar_figuras(figuras, multiplicador):
    """Escala las coordenadas y dimensiones de las figuras para renderizado en alta resolución."""
    escaladas = []
    for figura in figuras:
        if isinstance(figura, Poligono):
            nuevos_puntos = tuple(p * multiplicador for p in figura._puntos)
            escaladas.append(type(figura)(nuevos_puntos, figura._color))
        elif isinstance(figura, FiguraElipsoidal):
            cx, cy, rx, ry, rot = figura._geometria
            nueva_geometria = (
                cx * multiplicador,
                cy * multiplicador,
                rx * multiplicador,
                ry * multiplicador,
                rot,
            )
            escaladas.append(type(figura)(nueva_geometria, figura._color))
        else:
            escaladas.append(figura)
    return escaladas
