"""Selección universal: la ruleta, pero con los sorteos repartidos parejo sobre el intervalo."""

import numpy as np

from src.seleccion.comun import aptitudes, seleccionar_por_pesos


def seleccionar(individuos, cantidad, azar, config):
    """Sortea un solo número y deriva el resto equiespaciados."""
    numeros = (azar.random() + np.arange(cantidad)) / cantidad
    return seleccionar_por_pesos(individuos, aptitudes(individuos), numeros)
