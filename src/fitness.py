"""Convierte un fenotipo en la aptitud que compara la selección."""

import numpy as np

CANALES_DE_COLOR = 3


def calcular_fitness(fenotipo, objetivo):
    """Devuelve la aptitud del fenotipo contra el objetivo, entre 0 sin incluirlo y 1."""
    if fenotipo.shape != objetivo.shape:
        raise ValueError(
            f"el fenotipo y el objetivo tienen que tener la misma forma para "
            f"poder compararse: {fenotipo.shape} contra {objetivo.shape}"
        )
    # En 32 bits con signo la resta y su cuadrado son exactos, y numpy promedia
    # enteros acumulando en flotante de 64 bits, así que la suma no desborda.
    diferencia = np.subtract(
        fenotipo[..., :CANALES_DE_COLOR],
        objetivo[..., :CANALES_DE_COLOR],
        dtype=np.int32,
    )
    error = np.mean(diferencia * diferencia)
    return float(1.0 / (1.0 + error))
