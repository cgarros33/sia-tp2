"""Selección por élite: los mejores, repetidos según su posición en el ranking."""

import math

from src.seleccion.comun import aptitudes, orden_por_fitness


def seleccionar(individuos, cantidad, azar, config):
    """Devuelve los individuos de mayor fitness, repetidos según su posición en el ranking."""
    total = len(individuos)
    elegidos = []
    for posicion, indice in enumerate(orden_por_fitness(aptitudes(individuos))):
        # n(i) = techo((cantidad - i) / total), con i contado desde cero. Para
        # las posiciones sobrantes da cero o menos y ya no aporta nadie.
        repeticiones = math.ceil((cantidad - posicion) / total)
        if repeticiones <= 0:
            break
        elegidos.extend([individuos[int(indice)]] * repeticiones)
        if len(elegidos) >= cantidad:
            break
    return elegidos[:cantidad]
