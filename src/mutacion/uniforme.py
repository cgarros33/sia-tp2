"""Mutación uniforme: cada gen del individuo se sortea por separado."""

import numpy as np

from src.mutacion.comun import mutar_loci, sorteados


def mutar(individuo, azar, config, ancho, alto):
    """Le da a cada gen del individuo una probabilidad extra_gene_Pm independiente de mutar."""
    loci = sorteados(np.arange(len(individuo)), azar, config["extra_gene_Pm"])
    return mutar_loci(individuo, loci, azar, config, ancho, alto)
