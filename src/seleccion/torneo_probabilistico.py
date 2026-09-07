"""Torneo probabilístico: de a dos, con un umbral que decide si gana el más apto."""

import numpy as np

from src.seleccion.comun import aptitudes


def seleccionar(individuos, cantidad, azar, config):
    """Enfrenta dos individuos por selección y aplica tournament_threshold."""
    valores = aptitudes(individuos)
    umbral = config["tournament_threshold"]
    elegidos = []
    for _ in range(cantidad):
        pareja = np.sort(azar.choice(len(individuos), 2, replace=False))
        if valores[pareja[0]] >= valores[pareja[1]]:
            mejor, peor = pareja[0], pareja[1]
        else:
            mejor, peor = pareja[1], pareja[0]
        elegidos.append(individuos[int(mejor if azar.random() < umbral else peor)])
    return elegidos
