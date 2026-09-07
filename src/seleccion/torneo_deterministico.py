"""Torneo determinístico: gana siempre el más apto del grupo sorteado."""

import numpy as np

from src.seleccion.comun import aptitudes


def seleccionar(individuos, cantidad, azar, config):
    """Corre un torneo de tournament_size competidores por cada individuo a seleccionar."""
    valores = aptitudes(individuos)
    tamaño = min(config["tournament_size"], len(individuos))
    elegidos = []
    for _ in range(cantidad):
        # Ordenar el grupo hace que un empate lo gane el de menor índice en la
        # lista, y no el que salió primero en el sorteo.
        competidores = np.sort(azar.choice(len(individuos), tamaño, replace=False))
        elegidos.append(individuos[int(competidores[np.argmax(valores[competidores])])])
    return elegidos
