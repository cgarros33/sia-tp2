"""Funciones auxiliares para la creación de individuos, poblaciones y generadores de prueba."""

import numpy as np

from src.figuras.triangulo import Triangulo
from src.individuo import Individuo
from src.poblacion import Poblacion

SEMILLA_TEST = 33333333


def generador_azar(seed=SEMILLA_TEST):
    """Devuelve un generador pseudoaleatorio de NumPy con la semilla dada."""
    return np.random.default_rng(seed)


def config_test(**overrides):
    """Devuelve un diccionario de configuración de prueba con valores razonables."""
    config = {
        "random_seed": SEMILLA_TEST,
        "population_size": 10,
        "selected_count": 4,
        "gene_count": 4,
        "gene_type": "triangle",
        "tournament_size": 3,
        "tournament_threshold": 0.75,
        "temperature": 1.0,
        "uniform_crossover_P": 0.5,
        "extra_gene_Pm": 0.5,
        "intra_gene_Pm": 0.5,
        "max_genes_to_mutate": 3,
        "max_coord_delta": 5.0,
        "max_color_delta": 10,
        "max_coord_overflow": 5.0,
    }
    config.update(overrides)
    return config


def crear_triangulo(marca=0, color=(100, 100, 100, 255)):
    """Devuelve un triángulo con geometría fija y una marca en la última coordenada."""
    return Triangulo((0.0, 0.0, 1.0, 1.0, 2.0, float(marca)), color)


def crear_individuo(fitness_val=None, cant_genes=4, marca=0):
    """Devuelve un individuo con la cantidad de triángulos indicada y su fitness opcionalmente cacheado."""
    genes = [crear_triangulo(marca=marca + i) for i in range(cant_genes)]
    individuo = Individuo(genes)
    if fitness_val is not None:
        individuo.fitness(lambda _: float(fitness_val))
    return individuo


def crear_poblacion_test(aptitudes, cant_genes=4, ancho=100, alto=100):
    """Devuelve una Población de prueba con los fitness indicados."""
    config = config_test(gene_count=cant_genes)
    individuos = [
        crear_individuo(fitness_val=fit, cant_genes=cant_genes, marca=i * 10)
        for i, fit in enumerate(aptitudes)
    ]
    rangos = Triangulo.rangos(config, ancho, alto)
    poblacion = Poblacion(individuos, rangos, generacion=0)
    poblacion.evaluar(lambda _: None)
    return poblacion
