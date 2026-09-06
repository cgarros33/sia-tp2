"""Selección por ranking: el peso depende de la posición y no del valor del fitness."""

import numpy as np

from src.seleccion.comun import aptitudes, orden_por_fitness, seleccionar_por_pesos


def seleccionar(individuos, cantidad, azar, config):
    """Pesa a cada individuo por su posición en el ranking y sortea como la ruleta."""
    ordenados, pesos = pesos_por_ranking(individuos)
    return seleccionar_por_pesos(ordenados, pesos, azar.random(cantidad))


def pesos_por_ranking(individuos):
    """Devuelve los individuos de mejor a peor junto con su peso (N - posición) / N."""
    total = len(individuos)
    orden = orden_por_fitness(aptitudes(individuos))
    # Las posiciones se cuentan desde cero: numerando desde uno el peor recibiría
    # peso cero y quedaría excluido, que es justo lo que este método evita.
    pesos = (total - np.arange(total)) / total
    return [individuos[int(indice)] for indice in orden], pesos
