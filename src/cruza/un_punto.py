"""Cruce de un punto: se sortea un corte y se intercambia todo lo que va desde ahí hasta el final."""

import numpy as np

from src.cruza.comun import hijos_por_mascara, largo_comun


def cruzar(padre, madre, azar, config):
    """Intercambia el sufijo del cromosoma a partir de un corte sorteado."""
    largo = largo_comun(padre, madre)
    mascara = np.zeros(largo, dtype=bool)
    # El corte se sortea entre 1 y largo-1: en 0 el sufijo es todo el cromosoma y
    # en largo es vacío, y en los dos casos los hijos salen clones de los padres.
    if largo >= 2:
        mascara[azar.integers(1, largo):] = True
    return hijos_por_mascara(padre, madre, mascara)
