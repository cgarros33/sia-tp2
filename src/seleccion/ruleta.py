"""Selección proporcional al fitness: cada individuo ocupa un intervalo de su tamaño."""

from src.seleccion.comun import aptitudes, seleccionar_por_pesos


def seleccionar(individuos, cantidad, azar, config):
    """Sortea un número independiente por cada selección y devuelve el dueño de ese intervalo."""
    return seleccionar_por_pesos(
        individuos, aptitudes(individuos), azar.random(cantidad)
    )
