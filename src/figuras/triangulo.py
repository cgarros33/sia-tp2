"""Triángulo: la figura estándar del problema."""

from src.figuras.familias import Poligono


class Triangulo(Poligono):
    """Polígono de tres vértices con color RGBA."""

    __slots__ = ()

    CANTIDAD_VERTICES = 3
