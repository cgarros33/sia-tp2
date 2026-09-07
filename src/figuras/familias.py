"""Las dos familias de figuras: polígonos de N vértices y figuras elipsoidales."""

import numpy as np
from PIL import Image, ImageDraw

from src.figuras.base import Figura

CANALES_DE_COLOR = ("rojo", "verde", "azul", "alfa")
COLOR_MAXIMO = 255


class Poligono(Figura):
    """Familia de los polígonos de color homogéneo: triángulo, cuadrilátero y pentágono."""

    __slots__ = ("_puntos", "_color")

    CANTIDAD_VERTICES = None

    def __init__(self, puntos, color):
        """Recibe las coordenadas planas de los vértices y los cuatro canales de color."""
        if self.CANTIDAD_VERTICES is None:
            raise TypeError(
                "Poligono es una familia, no una figura: instanciá Triangulo, "
                "Cuadrilatero, Pentagono o una subclase que defina "
                "CANTIDAD_VERTICES"
            )
        self._puntos = puntos
        self._color = color

    @classmethod
    def aleatoria(cls, azar, config, ancho, alto):
        """Muestrea cada vértice y cada canal de color uniformemente dentro del dominio válido."""
        minimos, maximos = cls._limites(config, ancho, alto)
        cantidad = 2 * cls.CANTIDAD_VERTICES
        puntos = azar.uniform(minimos[:cantidad], maximos[:cantidad])
        color = azar.integers(0, COLOR_MAXIMO + 1, len(CANALES_DE_COLOR))
        return cls(tuple(puntos.tolist()), tuple(color.tolist()))

    def mutar(self, azar, config, ancho, alto):
        """Devuelve un polígono nuevo con cada parámetro mutado por un delta y recortado a su rango."""
        minimos, maximos = self._limites(config, ancho, alto)
        cantidad = 2 * self.CANTIDAD_VERTICES
        total = cantidad + len(CANALES_DE_COLOR)

        aleatorios = azar.random(2 * total)
        muta = aleatorios[:total] < config["intra_gene_Pm"]
        if not np.any(muta):
            return self

        delta_coord = config["max_coord_delta"]
        deltas_coord = (
            aleatorios[total : total + cantidad] * (2 * delta_coord)
        ) - delta_coord
        puntos = np.asarray(self._puntos) + deltas_coord * muta[:cantidad]
        puntos = np.clip(puntos, minimos[:cantidad], maximos[:cantidad])

        delta_color = int(config["max_color_delta"])
        deltas_color = (
            np.floor(
                aleatorios[total + cantidad :] * (2 * delta_color + 1)
            ).astype(int)
            - delta_color
        )
        color = np.asarray(self._color) + deltas_color * muta[cantidad:]
        color = tuple(np.clip(color, 0, COLOR_MAXIMO).tolist())

        return type(self)(tuple(puntos.tolist()), color)

    def copiar(self):
        """Devuelve un polígono nuevo con los mismos parámetros."""
        return type(self)(self._puntos, self._color)

    def dibujar(self, destino, recursos, pincel=None):
        """Pinta el polígono relleno sobre el destino, mezclando su alfa con lo ya dibujado."""
        if pincel is None:
            pincel = ImageDraw.Draw(destino, "RGBA")
        pincel.polygon(self._puntos, fill=self._color)

    def parametros(self):
        """Devuelve las coordenadas de los vértices seguidas de los cuatro canales de color."""
        return self._puntos + self._color

    def centro(self):
        """Devuelve el promedio de los vértices."""
        horizontales = self._puntos[0::2]
        verticales = self._puntos[1::2]
        return (
            sum(horizontales) / len(horizontales),
            sum(verticales) / len(verticales),
        )

    def con_color(self, rojo, verde, azul):
        """Devuelve un polígono nuevo con la misma geometría, el mismo alfa y otro color."""
        color = (_a_entero(rojo), _a_entero(verde), _a_entero(azul), self._color[3])
        return type(self)(self._puntos, color)

    @classmethod
    def nombres_parametros(cls):
        """Devuelve x0, y0, x1, y1, ... seguidos de los nombres de los cuatro canales."""
        nombres = []
        for indice in range(cls.CANTIDAD_VERTICES):
            nombres.append(f"x{indice}")
            nombres.append(f"y{indice}")
        return tuple(nombres) + CANALES_DE_COLOR

    @classmethod
    def rangos(cls, config, ancho, alto):
        """Devuelve el par mínimo y máximo de cada parámetro."""
        minimos, maximos = cls._limites(config, ancho, alto)
        return tuple(zip(minimos.tolist(), maximos.tolist()))

    @classmethod
    def _limites(cls, config, ancho, alto):
        """Devuelve los mínimos y los máximos de todos los parámetros como dos vectores."""
        desborde = config["max_coord_overflow"]
        cantidad = 2 * cls.CANTIDAD_VERTICES
        minimos = np.empty(cantidad + len(CANALES_DE_COLOR))
        maximos = np.empty(cantidad + len(CANALES_DE_COLOR))
        minimos[:cantidad] = -desborde
        maximos[0:cantidad:2] = ancho + desborde
        maximos[1:cantidad:2] = alto + desborde
        minimos[cantidad:] = 0
        maximos[cantidad:] = COLOR_MAXIMO
        return minimos, maximos


class FiguraElipsoidal(Figura):
    """Familia de las figuras con centro, dos radios y rotación: óvalo e imagen PNG."""

    __slots__ = ("_geometria", "_color")

    NOMBRES_GEOMETRIA = ("x", "y", "radio_x", "radio_y", "rotacion")

    def __init__(self, geometria, color):
        """Recibe el centro, los dos radios y la rotación en una tupla, y los cuatro canales de color."""
        self._geometria = geometria
        self._color = color

    @classmethod
    def aleatoria(cls, azar, config, ancho, alto):
        """Muestrea la geometría y el color uniformemente dentro del dominio válido."""
        minimos, maximos = cls._limites(config, ancho, alto)
        cantidad = len(cls.NOMBRES_GEOMETRIA)
        geometria = azar.uniform(minimos[:cantidad], maximos[:cantidad])
        color = azar.integers(0, COLOR_MAXIMO + 1, len(CANALES_DE_COLOR))
        return cls(tuple(geometria.tolist()), tuple(color.tolist()))

    def mutar(self, azar, config, ancho, alto):
        """Devuelve una figura nueva con la geometría recortada, la rotación envuelta y el color recortado."""
        minimos, maximos = self._limites(config, ancho, alto)
        cantidad = len(self.NOMBRES_GEOMETRIA)
        total = cantidad + len(CANALES_DE_COLOR)

        aleatorios = azar.random(2 * total)
        muta = aleatorios[:total] < config["intra_gene_Pm"]
        if not np.any(muta):
            return self

        deltas = np.array(
            (
                config["max_coord_delta"],
                config["max_coord_delta"],
                config["max_radius_delta"],
                config["max_radius_delta"],
                config["max_rotation_delta"],
            )
        )
        deltas_geom = (aleatorios[total : total + cantidad] * 2.0 - 1.0) * deltas
        geometria = np.asarray(self._geometria) + deltas_geom * muta[:cantidad]
        geometria[:-1] = np.clip(
            geometria[:-1], minimos[: cantidad - 1], maximos[: cantidad - 1]
        )
        # El módulo de Python devuelve siempre un valor no negativo: con fmod,
        # una rotación apenas negativa quedaría fuera de rango sin fallar.
        geometria[-1] %= 1.0

        delta_color = int(config["max_color_delta"])
        deltas_color = (
            np.floor(
                aleatorios[total + cantidad :] * (2 * delta_color + 1)
            ).astype(int)
            - delta_color
        )
        color = np.asarray(self._color) + deltas_color * muta[cantidad:]
        color = tuple(np.clip(color, 0, COLOR_MAXIMO).tolist())

        return type(self)(tuple(geometria.tolist()), color)

    def copiar(self):
        """Devuelve una figura nueva con los mismos parámetros."""
        return type(self)(self._geometria, self._color)

    def parametros(self):
        """Devuelve el centro, los radios y la rotación seguidos de los cuatro canales de color."""
        return self._geometria + self._color

    def centro(self):
        """Devuelve el centro de la figura."""
        return (self._geometria[0], self._geometria[1])

    def con_color(self, rojo, verde, azul):
        """Devuelve una figura nueva con la misma geometría, el mismo alfa y otro color."""
        color = (_a_entero(rojo), _a_entero(verde), _a_entero(azul), self._color[3])
        return type(self)(self._geometria, color)

    @classmethod
    def nombres_parametros(cls):
        """Devuelve los nombres de la geometría seguidos de los de los cuatro canales."""
        return cls.NOMBRES_GEOMETRIA + CANALES_DE_COLOR

    @classmethod
    def rangos(cls, config, ancho, alto):
        """Devuelve el par mínimo y máximo de cada parámetro."""
        minimos, maximos = cls._limites(config, ancho, alto)
        return tuple(zip(minimos.tolist(), maximos.tolist()))

    @classmethod
    def _limites(cls, config, ancho, alto):
        """Devuelve los mínimos y los máximos de todos los parámetros como dos vectores."""
        radio_maximo = max(1.0, max(ancho, alto) / 2)
        minimos = np.array([0.0, 0.0, 1.0, 1.0, 0.0] + [0.0] * len(CANALES_DE_COLOR))
        maximos = np.array(
            [float(ancho), float(alto), radio_maximo, radio_maximo, 1.0]
            + [float(COLOR_MAXIMO)] * len(CANALES_DE_COLOR)
        )
        return minimos, maximos

    def _caja(self):
        """Devuelve el tamaño en píxeles de la caja contenedora de la figura."""
        radio_x, radio_y = self._geometria[2], self._geometria[3]
        return (max(1, round(2 * radio_x)), max(1, round(2 * radio_y)))

    def _componer(self, destino, capa):
        """Rota la capa auxiliar y la pega centrada en el destino usando su alfa como máscara."""
        rotada = capa.rotate(
            self._geometria[4] * 360,
            expand=True,
            resample=Image.Resampling.BILINEAR,
        )
        posicion = (
            round(self._geometria[0] - rotada.width / 2),
            round(self._geometria[1] - rotada.height / 2),
        )
        destino.paste(rotada, posicion, rotada)




def _a_entero(valor):
    """Redondea un valor de color al entero más cercano."""
    return int(round(float(valor)))
