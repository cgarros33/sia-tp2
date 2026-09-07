"""Selección de Boltzmann: pseudo-aptitud exponencial gobernada por la temperatura."""

import numpy as np

from src.seleccion.comun import aptitudes, seleccionar_por_pesos


def seleccionar(individuos, cantidad, azar, config):
    """Pesa a cada individuo con su valor esperado de Boltzmann y sortea como la ruleta."""
    pesos = valores_esperados(aptitudes(individuos), config["temperature"])
    return seleccionar_por_pesos(individuos, pesos, azar.random(cantidad))


def valores_esperados(valores, temperatura):
    """Devuelve e^(f/T) dividido por su promedio en la población."""
    # Restar el máximo antes de exponenciar evita el desborde con temperaturas
    # chicas: es un factor común que se cancela en el cociente y no cambia nada.
    exponenciales = np.exp((valores - valores.max()) / temperatura)
    return exponenciales / exponenciales.mean()
