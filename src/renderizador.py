"""Carga las imágenes de la corrida y convierte una lista de figuras en el fenotipo."""

import numpy as np
from PIL import Image

from src.figuras.imagen_png import CLAVE_OVERLAY

TIPO_DE_GEN_CON_OVERLAY = "png"
MODOS_CON_ALFA = ("RGBA", "LA", "PA")
CLAVE_TRANSPARENCIA = "transparency"
OPACO = 255


class ErrorDeImagen(Exception):
    """Imagen inexistente o ilegible."""


def cargar_objetivo(config):
    """Abre la imagen objetivo, la deja opaca y redimensionada, y la devuelve con su ancho y su alto."""
    imagen = _abrir(config["file_input"])
    imagen = _aplanar(imagen, config["background_color"])
    imagen = _redimensionar(imagen, config["output_resolution_mult"])
    return np.asarray(imagen, dtype=np.uint8), imagen.width, imagen.height


def cargar_recursos(config):
    """Devuelve lo que las figuras necesitan para dibujarse, leído una sola vez por corrida."""
    if config["gene_type"] != TIPO_DE_GEN_CON_OVERLAY:
        return {}
    return {CLAVE_OVERLAY: _abrir(config["overlay_source"]).convert("RGBA")}


def renderizar(figuras, ancho, alto, config, recursos):
    """Dibuja las figuras en orden sobre el lienzo del color de fondo y devuelve el fenotipo."""
    # El lienzo va sin canal alfa: es el único modo en el que Pillow compone la
    # transparencia de la figura en vez de pisar el píxel.
    lienzo = Image.new("RGB", (ancho, alto), tuple(config["background_color"][:3]))
    for figura in figuras:
        figura.dibujar(lienzo, recursos)
    return np.asarray(lienzo, dtype=np.uint8)


def _abrir(path_imagen):
    """Abre una imagen del disco, cortando con un mensaje que incluye el path."""
    try:
        imagen = Image.open(path_imagen)
        imagen.load()
    except FileNotFoundError:
        raise ErrorDeImagen(f"no existe la imagen: {path_imagen}") from None
    except OSError as error:
        raise ErrorDeImagen(
            f"no se pudo leer la imagen {path_imagen}: {error}"
        ) from None
    return imagen


def _aplanar(imagen, color_de_fondo):
    """Compone la imagen sobre el color de fondo si tiene píxeles no opacos y la devuelve en RGB."""
    if not _tiene_transparencia(imagen):
        return imagen.convert("RGB")
    imagen = imagen.convert("RGBA")
    fondo = Image.new("RGBA", imagen.size, tuple(color_de_fondo[:3]) + (OPACO,))
    return Image.alpha_composite(fondo, imagen).convert("RGB")


def _tiene_transparencia(imagen):
    """Dice si la imagen trae transparencia con al menos un píxel no opaco."""
    if CLAVE_TRANSPARENCIA in imagen.info:
        return True
    if imagen.mode not in MODOS_CON_ALFA:
        return False
    minimo, _ = imagen.getchannel("A").getextrema()
    return minimo < OPACO


def _redimensionar(imagen, multiplicador):
    """Escala la imagen por el multiplicador de resolución, sin bajar de un píxel."""
    ancho = max(1, round(imagen.width * multiplicador))
    alto = max(1, round(imagen.height * multiplicador))
    if (ancho, alto) == imagen.size:
        return imagen
    return imagen.resize((ancho, alto), Image.Resampling.LANCZOS)
