"""Mutación multigen limitada: se sortea un puñado de genes acotado por max_genes_to_mutate."""

from src.mutacion.comun import mutar_loci, sorteados


def mutar(individuo, azar, config, ancho, alto):
    """Sortea entre 1 y max_genes_to_mutate genes y muta cada uno con probabilidad extra_gene_Pm."""
    cota = min(config["max_genes_to_mutate"], len(individuo))
    candidatos = azar.choice(len(individuo), azar.integers(1, cota + 1), replace=False)
    loci = sorteados(candidatos, azar, config["extra_gene_Pm"])
    return mutar_loci(individuo, loci, azar, config, ancho, alto)
