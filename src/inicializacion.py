"""Inicialización de la población inicial de individuos para el motor genético."""

import numpy as np
from PIL import Image, ImageDraw

from src.figuras.cuadrilatero import Cuadrilatero
from src.figuras.familias import FiguraElipsoidal, Poligono
from src.figuras.imagen_png import ImagenPng
from src.figuras.ovalo import Ovalo
from src.figuras.pentagono import Pentagono
from src.figuras.triangulo import Triangulo
from src.individuo import Individuo
from src.poblacion import Poblacion

FIGURAS = {
    "triangle": Triangulo,
    "quad": Cuadrilatero,
    "pentagon": Pentagono,
    "oval": Ovalo,
    "png": ImagenPng,
}


def inicializar_poblacion(config, objetivo, ancho, alto, azar):
    """Crea la población inicial de la generación cero con o sin sesgo de color."""
    figura_cls = FIGURAS[config["gene_type"]]
    rangos = figura_cls.rangos(config, ancho, alto)
    sesgo = config["sesgo_color_inicial"]
    tipo_sesgo = config["tipo_sesgo_color"]
    gene_count = config["gene_count"]
    population_size = config["population_size"]

    individuos = []
    for _ in range(population_size):
        genes = []
        for _ in range(gene_count):
            figura = figura_cls.aleatoria(azar, config, ancho, alto)
            if sesgo:
                figura = _aplicar_sesgo_color(
                    figura, tipo_sesgo, objetivo, ancho, alto, azar
                )
            genes.append(figura)
        individuos.append(Individuo(genes))

    return Poblacion(individuos, rangos, generacion=0)


def _aplicar_sesgo_color(figura, tipo_sesgo, objetivo, ancho, alto, azar):
    """Calcula el color promedio de la figura sobre la imagen objetivo y devuelve una copia con ese color."""
    if tipo_sesgo == "bounding_box":
        rgb = _color_bounding_box(figura, objetivo, ancho, alto)
    else:
        rgb = _color_exact_match(figura, objetivo, ancho, alto)

    alfa = int(azar.integers(0, 256))
    return _con_color_y_alfa(figura, rgb[0], rgb[1], rgb[2], alfa)


def _con_color_y_alfa(figura, rojo, verde, azul, alfa):
    """Devuelve una figura nueva con la misma geometría y el color RGBA especificado."""
    color = (int(round(rojo)), int(round(verde)), int(round(azul)), int(alfa))
    if isinstance(figura, Poligono):
        return type(figura)(figura._puntos, color)
    return type(figura)(figura._geometria, color)


def _color_bounding_box(figura, objetivo, ancho, alto):
    """Obtiene el color promedio de la caja contenedora de la figura recortada al lienzo."""
    if isinstance(figura, Poligono):
        xs = figura._puntos[0::2]
        ys = figura._puntos[1::2]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
    else:
        cx, cy, rx, ry, _ = figura._geometria
        min_x, max_x = cx - rx, cx + rx
        min_y, max_y = cy - ry, cy + ry

    x0 = max(0, min(ancho, int(np.floor(min_x))))
    x1 = max(0, min(ancho, int(np.ceil(max_x))))
    y0 = max(0, min(alto, int(np.floor(min_y))))
    y1 = max(0, min(alto, int(np.ceil(max_y))))

    if x1 <= x0 or y1 <= y0:
        cx, cy = figura.centro()
        px = max(0, min(ancho - 1, int(round(cx))))
        py = max(0, min(alto - 1, int(round(cy))))
        return objetivo[py, px, :3].astype(float)

    return objetivo[y0:y1, x0:x1, :3].mean(axis=(0, 1))


def _color_exact_match(figura, objetivo, ancho, alto):
    """Obtiene el color promedio de los píxeles interiores exactos de la figura en el lienzo."""
    mascara = Image.new("L", (ancho, alto), 0)
    if isinstance(figura, Poligono):
        ImageDraw.Draw(mascara).polygon(figura._puntos, fill=255)
    else:
        w_caja, h_caja = figura._caja()
        capa = Image.new("L", (w_caja, h_caja), 0)
        ImageDraw.Draw(capa).ellipse((0, 0, w_caja - 1, h_caja - 1), fill=255)
        rotada = capa.rotate(
            figura._geometria[4] * 360,
            resample=Image.Resampling.BILINEAR,
            expand=True,
        )
        esquina_x = round(figura._geometria[0] - rotada.width / 2)
        esquina_y = round(figura._geometria[1] - rotada.height / 2)
        mascara.paste(rotada, (esquina_x, esquina_y), rotada)

    pixeles = np.asarray(mascara) > 0
    if not np.any(pixeles):
        cx, cy = figura.centro()
        px = max(0, min(ancho - 1, int(round(cx))))
        py = max(0, min(alto - 1, int(round(cy))))
        return objetivo[py, px, :3].astype(float)

    return objetivo[pixeles, :3].mean(axis=0)
