"""Supervivencia aditiva: los hijos compiten contra la población entera por un lugar."""

from src.supervivencia.comun import sin_repetir_referencias


def sobrevivientes(actuales, hijos, cantidad, seleccionar, azar, config):
    """Elige la generación siguiente del conjunto que junta a todos los individuos actuales con los hijos."""
    candidatos = list(actuales) + list(hijos)
    return sin_repetir_referencias(seleccionar(candidatos, cantidad, azar, config))
