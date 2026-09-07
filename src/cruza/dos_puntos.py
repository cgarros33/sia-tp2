"""Cruce de dos puntos: se sortean dos cortes y se intercambia el bloque que queda en el medio."""

import numpy as np

from src.cruza.comun import hijos_por_mascara, largo_comun


def cruzar(padre, madre, azar, config):
    """Intercambia los genes que quedan entre dos cortes sorteados."""
    largo = largo_comun(padre, madre)
    mascara = np.zeros(largo, dtype=bool)
    # Dos cortes distintos entre 1 y largo-1 dejan siempre prefijo, medio y sufijo
    # no vacíos, y para que existan hacen falta al menos tres genes.
    if largo >= 3:
        primero, segundo = np.sort(
            azar.choice(np.arange(1, largo), 2, replace=False)
        )
        mascara[primero:segundo] = True
    return hijos_por_mascara(padre, madre, mascara)
