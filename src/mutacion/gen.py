"""Mutación por gen: se altera un único gen del individuo."""

from src.mutacion.comun import mutar_loci, sorteados


def mutar(individuo, azar, config, ancho, alto):
    """Sortea un solo gen del individuo y lo muta con probabilidad extra_gene_Pm."""
    candidatos = azar.integers(0, len(individuo), 1)
    loci = sorteados(candidatos, azar, config["extra_gene_Pm"])
    return mutar_loci(individuo, loci, azar, config, ancho, alto)
