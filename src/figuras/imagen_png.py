"""Imagen PNG: overlay externo con la misma geometría que el óvalo."""

from PIL import Image, ImageChops

from src.figuras.familias import FiguraElipsoidal

CLAVE_OVERLAY = "overlay"


class ImagenPng(FiguraElipsoidal):
    """Overlay PNG reescalado al tamaño de la figura, teñido por su color y rotado."""

    __slots__ = ()

    def dibujar(self, destino, recursos, pincel=None):
        """Reescala el overlay, le aplica el filtro de color, lo rota y lo compone sobre el destino."""
        capa = recursos[CLAVE_OVERLAY].resize(self._caja(), Image.Resampling.BILINEAR)
        solido = Image.new("RGB", capa.size, self._color[:3])
        con_filtro = Image.blend(capa.convert("RGB"), solido, 0.45)
        alfa_combinado = ImageChops.multiply(
            capa.getchannel("A"), Image.new("L", capa.size, self._color[3])
        )
        con_filtro.putalpha(alfa_combinado)
        self._componer(destino, con_filtro)
