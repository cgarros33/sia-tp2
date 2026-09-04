"""Imagen PNG: overlay externo con la misma geometría que el óvalo."""

from PIL import Image, ImageChops

from src.figuras.familias import FiguraElipsoidal

CLAVE_OVERLAY = "overlay"


class ImagenPng(FiguraElipsoidal):
    """Overlay PNG reescalado al tamaño de la figura, teñido por su color y rotado."""

    __slots__ = ()

    def dibujar(self, destino, recursos):
        """Reescala el overlay, lo tiñe con el color de la figura, lo rota y lo compone sobre el destino."""
        capa = recursos[CLAVE_OVERLAY].resize(self._caja(), Image.Resampling.BILINEAR)
        tinte = Image.new("RGBA", capa.size, self._color)
        self._componer(destino, ImageChops.multiply(capa, tinte))
