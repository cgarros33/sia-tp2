"""Cruce anular: el cromosoma se trata como un anillo y se intercambia un segmento circular."""

import numpy as np

from src.cruza.comun import hijos_por_mascara, largo_comun


def cruzar(padre, madre, azar, config):
    """Intercambia un segmento circular de inicio y largo sorteados."""
    largo = largo_comun(padre, madre)
    mascara = np.zeros(largo, dtype=bool)
    if largo >= 2:
        inicio = azar.integers(0, largo)
        # El largo llega hasta la mitad del anillo: un segmento de largo k desde
        # el inicio intercambia los mismos loci que uno de largo largo-k desde
        # inicio+k, así que pasada la mitad se repiten intercambios.
        tramo = azar.integers(1, largo // 2 + 1)
        mascara[(inicio + np.arange(tramo)) % largo] = True
    return hijos_por_mascara(padre, madre, mascara)
