"""Mutación no uniforme: un solo sorteo decide si muta el individuo entero."""

import numpy as np

from src.mutacion.comun import mutar_loci


def mutar(individuo, azar, config, ancho, alto):
    """Con probabilidad extra_gene_Pm muta todos los genes del individuo, y si no ninguno."""
    if azar.random() >= config["extra_gene_Pm"]:
        return individuo
    return mutar_loci(individuo, np.arange(len(individuo)), azar, config, ancho, alto)
