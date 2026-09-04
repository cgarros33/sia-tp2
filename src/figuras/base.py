"""Interfaz que implementan las cinco figuras del problema."""

from abc import ABC, abstractmethod


class Figura(ABC):
    """Gen del problema: una figura que sabe crearse al azar, mutarse y dibujarse."""

    __slots__ = ()

    @classmethod
    @abstractmethod
    def aleatoria(cls, azar, config, ancho, alto):
        """Devuelve una figura con todos sus parámetros muestreados dentro del dominio válido."""

    @abstractmethod
    def mutar(self, azar, config, ancho, alto):
        """Devuelve una figura nueva con los parámetros mutados, sin tocar esta."""

    @abstractmethod
    def copiar(self):
        """Devuelve una copia independiente de esta figura."""

    @abstractmethod
    def dibujar(self, destino, recursos):
        """Pinta la figura sobre el destino componiendo su color con lo que ya está dibujado."""

    @abstractmethod
    def parametros(self):
        """Devuelve los valores de la figura en el orden fijo del genotipo."""

    @abstractmethod
    def centro(self):
        """Devuelve el centro geométrico de la figura."""

    @abstractmethod
    def con_color(self, rojo, verde, azul):
        """Devuelve una copia con otro color, conservando geometría y transparencia."""

    @classmethod
    @abstractmethod
    def nombres_parametros(cls):
        """Devuelve los nombres de los parámetros, en el mismo orden que parametros."""

    @classmethod
    @abstractmethod
    def rangos(cls, config, ancho, alto):
        """Devuelve el mínimo y el máximo de cada parámetro, en el mismo orden que parametros."""
