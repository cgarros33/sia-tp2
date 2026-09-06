"""Cruce uniforme: cada locus se sortea por separado."""

from src.cruza.comun import hijos_por_mascara, largo_comun


def cruzar(padre, madre, azar, config):
    """Intercambia cada gen de forma independiente con probabilidad uniform_crossover_P."""
    largo = largo_comun(padre, madre)
    mascara = azar.random(largo) < config["uniform_crossover_P"]
    return hijos_por_mascara(padre, madre, mascara)
