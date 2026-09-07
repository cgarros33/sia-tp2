"""Pruebas de la población: la métrica de diversidad, su normalización y las métricas de aptitud."""

import pytest

from src.figuras.triangulo import Triangulo
from src.individuo import Individuo
from src.poblacion import ErrorDePoblacion, Poblacion
from tests.helpers import config_test, crear_individuo, crear_poblacion_test

ANCHO = 100
ALTO = 100
CONFIG = config_test()
RANGOS = Triangulo.rangos(CONFIG, ANCHO, ALTO)
COORD_MINIMA = -CONFIG["max_coord_overflow"]
COORD_MAXIMA = ANCHO + CONFIG["max_coord_overflow"]
GRIS = (128, 128, 128, 255)


def triangulo(x0=0.0, color=GRIS):
    """Devuelve un triángulo que solo varía en su primera coordenada y en su color."""
    return Triangulo((x0, 0.0, 1.0, 1.0, 2.0, 3.0), color)


def poblacion_de(figuras):
    """Devuelve una población de individuos de un solo gen, uno por figura."""
    return Poblacion([Individuo([figura]) for figura in figuras], RANGOS)


def test_diversidad_nula_con_individuos_clonados():
    """Verifica que una población colapsada a un único genotipo dé diversidad exactamente cero."""
    poblacion = poblacion_de([triangulo(x0=7.0) for _ in range(5)])

    assert poblacion.diversidad() == 0.0


def test_diversidad_positiva_cuando_hay_variedad():
    """Verifica que la métrica suba apenas los individuos dejan de ser iguales."""
    poblacion = poblacion_de([triangulo(x0=0.0), triangulo(x0=50.0)])

    assert poblacion.diversidad() > 0.0


def test_diversidad_ordenada():
    """Verifica que una población más dispersa dé un valor mayor que una más concentrada."""
    concentrada = poblacion_de([triangulo(x0=0.0), triangulo(x0=5.0)])
    dispersa = poblacion_de([triangulo(x0=0.0), triangulo(x0=100.0)])

    assert dispersa.diversidad() > concentrada.diversidad()


def test_la_normalizacion_cancela_la_escala():
    """Verifica que la misma dispersión relativa dé la misma diversidad en geometría y en color."""
    por_geometria = poblacion_de(
        [triangulo(x0=COORD_MINIMA), triangulo(x0=COORD_MAXIMA)]
    )
    por_color = poblacion_de(
        [triangulo(color=(0, 128, 128, 255)), triangulo(color=(255, 128, 128, 255))]
    )

    cantidad_parametros = len(Triangulo.nombres_parametros())
    esperado = 0.5 / cantidad_parametros

    assert por_geometria.diversidad() == pytest.approx(esperado)
    assert por_color.diversidad() == pytest.approx(esperado)


def test_las_metricas_de_aptitud_son_coherentes():
    """Verifica que el máximo sea la aptitud del mejor y que el promedio quede entre el mínimo y el máximo."""
    poblacion = crear_poblacion_test([0.2, 0.9, 0.5, 0.1])

    assert poblacion.fitness_maximo == 0.9
    assert poblacion.fitness_minimo == 0.1
    assert poblacion.fitness_minimo <= poblacion.fitness_promedio <= poblacion.fitness_maximo
    assert poblacion.mejor().fitness_cacheado == poblacion.fitness_maximo


def test_mejor_desempata_por_el_de_menor_indice():
    """Verifica que dos individuos con la misma aptitud máxima resuelvan siempre igual."""
    poblacion = crear_poblacion_test([0.9, 0.9, 0.1])

    assert poblacion.mejor() is poblacion[0]


def test_pedir_el_fitness_sin_evaluar_falla():
    """Verifica que consultar métricas antes de evaluar corte en vez de devolver basura."""
    poblacion = poblacion_de([triangulo(), triangulo(x0=1.0)])

    with pytest.raises(ErrorDePoblacion):
        poblacion.fitness


def test_evaluar_respeta_el_cache_de_cada_individuo():
    """Verifica que evaluar dos veces seguidas no vuelva a renderizar a nadie."""
    individuos = [crear_individuo(cant_genes=2, marca=i * 10) for i in range(4)]
    poblacion = Poblacion(individuos, RANGOS)
    llamadas = []

    def evaluador(genes):
        llamadas.append(genes)
        return 0.5

    poblacion.evaluar(evaluador)
    poblacion.evaluar(evaluador)

    assert len(llamadas) == len(individuos)


def test_la_siguiente_generacion_conserva_tamano_rangos_y_numera():
    """Verifica que la transición entre generaciones mantenga el tamaño y avance el contador."""
    poblacion = poblacion_de([triangulo(x0=float(i)) for i in range(4)])

    siguiente = poblacion.siguiente([Individuo([triangulo(x0=9.0)]) for _ in range(4)])

    assert len(siguiente) == len(poblacion)
    assert siguiente.generacion == poblacion.generacion + 1
    assert siguiente.rangos == poblacion.rangos


def test_la_siguiente_generacion_rechaza_otro_tamano():
    """Verifica que la población no pueda cambiar de tamaño entre generaciones."""
    poblacion = poblacion_de([triangulo(x0=float(i)) for i in range(4)])

    with pytest.raises(ErrorDePoblacion):
        poblacion.siguiente([Individuo([triangulo()]) for _ in range(3)])


def test_no_admite_el_mismo_individuo_repetido_por_referencia():
    """Verifica que dos referencias al mismo individuo corten, porque mutarían juntas."""
    individuo = crear_individuo(cant_genes=2)

    with pytest.raises(ErrorDePoblacion):
        Poblacion([individuo, individuo], RANGOS)


def test_no_admite_cromosomas_de_distinto_largo():
    """Verifica que todos los individuos tengan la misma cantidad de genes."""
    with pytest.raises(ErrorDePoblacion):
        Poblacion(
            [Individuo([triangulo()]), Individuo([triangulo(), triangulo(x0=1.0)])],
            RANGOS,
        )
