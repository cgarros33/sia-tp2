"""Individuo: el cromosoma, una lista de largo fijo de figuras con su fitness cacheado."""

import numpy as np


class ErrorDeIndividuo(Exception):
    """Individuo mal construido o accedido fuera de rango."""


class Individuo:
    """Lista ordenada de gene_count figuras que sabe cachear su fitness."""

    __slots__ = ("_genes", "_fitness", "_sucio", "_vector_parametros")

    def __init__(self, genes):
        """Recibe la secuencia ordenada de figuras que forman el cromosoma."""
        self._genes = list(genes)
        if not self._genes:
            raise ErrorDeIndividuo("un individuo necesita al menos un gen")
        self._fitness = None
        self._sucio = True
        self._vector_parametros = None

    @property
    def genes(self):
        """Devuelve los genes como tupla, en orden de dibujado."""
        return tuple(self._genes)

    def gen(self, locus):
        """Devuelve el gen que está en ese locus."""
        return self._genes[locus]

    def establecer_gen(self, locus, gen):
        """Reemplaza el gen del locus e invalida el fitness solo si los parámetros cambiaron."""
        if gen.parametros() != self._genes[locus].parametros():
            self._sucio = True
            self._fitness = None
            self._vector_parametros = None
        self._genes[locus] = gen

    def __len__(self):
        """Devuelve gene_count."""
        return len(self._genes)

    def fitness(self, evaluador):
        """Devuelve el fitness cacheado, o lo calcula con el evaluador si el individuo está sucio."""
        if self._sucio:
            self._fitness = evaluador(self.genes)
            self._sucio = False
        return self._fitness

    @property
    def fitness_cacheado(self):
        """Devuelve el último fitness calculado, o None si nunca se calculó."""
        return self._fitness

    @property
    def esta_sucio(self):
        """Indica si el fitness hay que volver a calcularlo."""
        return self._sucio

    def copiar(self):
        """Devuelve un individuo con una copia de la lista de genes y el mismo fitness."""
        copia = Individuo(self._genes)
        copia._fitness = self._fitness
        copia._sucio = self._sucio
        copia._vector_parametros = self._vector_parametros
        return copia

    def vector_parametros(self):
        """Devuelve todos los parámetros de todos los genes concatenados en un vector."""
        if self._vector_parametros is None:
            lista = []
            for gen in self._genes:
                lista.extend(gen.parametros())
            self._vector_parametros = np.asarray(lista, dtype=float)
        return self._vector_parametros

    def nombres_parametros(self):
        """Devuelve los nombres del vector de parámetros, prefijados por el locus del gen."""
        nombres = type(self._genes[0]).nombres_parametros()
        return tuple(
            f"g{locus}_{nombre}"
            for locus in range(len(self._genes))
            for nombre in nombres
        )
