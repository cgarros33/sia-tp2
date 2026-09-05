"""La rutina de ruleta que comparten los métodos de selección que trabajan con pesos."""

import numpy as np


class ErrorDeSeleccion(Exception):
    """Selección pedida sobre individuos sin evaluar o con pesos inservibles."""


def aptitudes(individuos):
    """Devuelve el vector de fitness cacheado de los individuos, leído una sola vez."""
    valores = [individuo.fitness_cacheado for individuo in individuos]
    if any(valor is None for valor in valores):
        raise ErrorDeSeleccion(
            "hay individuos sin fitness cacheado: la selección no evalúa, hay "
            "que llamar a Poblacion.evaluar antes de seleccionar"
        )
    return np.array(valores, dtype=float)


def orden_por_fitness(valores):
    """Devuelve los índices ordenados de mayor a menor fitness, estable ante empates."""
    return np.argsort(-valores, kind="stable")


def seleccionar_por_pesos(individuos, pesos, numeros):
    """Devuelve un individuo por cada número al azar, según los intervalos acumulados de los pesos."""
    total = pesos.sum()
    if not total > 0:
        raise ErrorDeSeleccion(
            f"los pesos de selección tienen que sumar más que cero, suman {total}"
        )
    acumuladas = np.cumsum(pesos / total)
    # El último acumulado puede quedar apenas por debajo de uno por redondeo, y
    # un número sorteado mayor caería fuera de todos los intervalos.
    indices = np.clip(
        np.searchsorted(acumuladas, numeros, side="left"), 0, len(individuos) - 1
    )
    return [individuos[int(indice)] for indice in indices]
