"""Óvalo: elipse con centro, dos radios, rotación y color RGBA."""

from PIL import Image, ImageDraw

from src.figuras.familias import FiguraElipsoidal


class Ovalo(FiguraElipsoidal):
    """Elipse rellena que se dibuja rotada sobre el destino."""

    __slots__ = ()

    def dibujar(self, destino, recursos):
        """Dibuja la elipse en una capa del tamaño de su caja, la rota y la compone sobre el destino."""
        ancho_caja, alto_caja = self._caja()
        # La capa nace del color de la figura con alfa cero: al rotarla se
        # interpola solo el alfa y el borde no queda con un halo oscuro.
        capa = Image.new("RGBA", (ancho_caja, alto_caja), self._color[:3] + (0,))
        ImageDraw.Draw(capa).ellipse(
            (0, 0, ancho_caja - 1, alto_caja - 1), fill=self._color
        )
        self._componer(destino, capa)
