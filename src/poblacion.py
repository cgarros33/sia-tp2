"""Población: los individuos de una generación, con sus métricas de fitness y de diversidad."""

import numpy as np


class ErrorDePoblacion(Exception):
    """Población mal construida o consultada antes de evaluarse."""


class Poblacion:
    """Conjunto de tamaño constante de individuos que conforman una generación."""

    __slots__ = ("_individuos", "_rangos", "_generacion", "_fitness")

    def __init__(self, individuos, rangos, generacion=0):
        """Recibe los individuos, los rangos válidos de un gen y el número de generación."""
        self._individuos = tuple(individuos)
        self._validar()
        self._rangos = tuple(rangos)
        self._generacion = generacion
        self._fitness = None

    @property
    def individuos(self):
        """Devuelve los individuos de la generación."""
        return self._individuos

    @property
    def rangos(self):
        """Devuelve el mínimo y el máximo de cada parámetro de un gen."""
        return self._rangos

    @property
    def generacion(self):
        """Devuelve el número de generación."""
        return self._generacion

    def __len__(self):
        """Devuelve population_size."""
        return len(self._individuos)

    def __iter__(self):
        """Recorre los individuos."""
        return iter(self._individuos)

    def __getitem__(self, indice):
        """Devuelve el individuo de esa posición."""
        return self._individuos[indice]

    def evaluar(self, evaluador):
        """Devuelve el vector de fitness de la generación, calculando solo el de los individuos sucios."""
        self._fitness = np.array(
            [individuo.fitness(evaluador) for individuo in self._individuos], dtype=float
        )
        return self._fitness

    @property
    def fitness(self):
        """Devuelve el vector de fitness ya calculado."""
        if self._fitness is None:
            raise ErrorDePoblacion(
                "hay que llamar a evaluar antes de pedir el fitness de la población"
            )
        return self._fitness

    def mejor(self):
        """Devuelve el individuo de mayor fitness, el de menor índice ante un empate."""
        return self._individuos[int(np.argmax(self.fitness))]

    @property
    def fitness_maximo(self):
        """Devuelve el mayor fitness de la generación."""
        return float(self.fitness.max())

    @property
    def fitness_minimo(self):
        """Devuelve el menor fitness de la generación."""
        return float(self.fitness.min())

    @property
    def fitness_promedio(self):
        """Devuelve el fitness promedio de la generación, que además usa la selección de Boltzmann."""
        return float(self.fitness.mean())

    def diversidad(self):
        """Devuelve el desvío estándar promedio de los parámetros, normalizado por el rango de cada uno."""
        minimos, maximos = np.array(self._rangos).T
        anchos = np.tile(maximos - minimos, len(self._individuos[0]))
        matriz = np.empty((len(self._individuos), len(anchos)), dtype=float)
        for indice, individuo in enumerate(self._individuos):
            matriz[indice] = [param for gen in individuo.genes for param in gen.parametros()]
        return float(np.mean(matriz.std(axis=0) / anchos))

    def siguiente(self, individuos):
        """Devuelve la generación que sigue, con el mismo tamaño y los mismos rangos."""
        if len(individuos) != len(self._individuos):
            raise ErrorDePoblacion(
                f"la población tiene que mantener su tamaño: se esperaban "
                f"{len(self._individuos)} individuos y llegaron {len(individuos)}"
            )
        return Poblacion(individuos, self._rangos, self._generacion + 1)

    def _validar(self):
        """Exige población no vacía, cromosomas del mismo largo y ningún individuo repetido por referencia."""
        if not self._individuos:
            raise ErrorDePoblacion("una población necesita al menos un individuo")
        largos = {len(individuo) for individuo in self._individuos}
        if len(largos) != 1:
            raise ErrorDePoblacion(
                f"todos los individuos tienen que tener la misma cantidad de "
                f"genes, se encontraron los largos {sorted(largos)}"
            )
        # Dos referencias al mismo individuo se mutarían juntas y bajarían la
        # diversidad real sin que ninguna métrica lo muestre.
        if len({id(individuo) for individuo in self._individuos}) != len(self._individuos):
            raise ErrorDePoblacion(
                "hay un mismo individuo repetido por referencia en la población: "
                "quien lo reutiliza tiene que copiarlo"
            )
