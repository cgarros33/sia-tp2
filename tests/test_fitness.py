"""Pruebas de la aptitud: rango, monotonía y qué canales entran en la comparación."""

import numpy as np
import pytest

from src.fitness import calcular_fitness

ERROR_MAXIMO = 255.0**2


def imagen(valor, alto=8, ancho=8, canales=3):
    """Devuelve una imagen uniforme del valor dado."""
    return np.full((alto, ancho, canales), valor, dtype=np.uint8)


def test_imagenes_identicas_dan_exactamente_uno():
    """Verifica que el fenotipo perfecto valga 1, que es la cota superior de la aptitud."""
    objetivo = imagen(123)
    assert calcular_fitness(objetivo.copy(), objetivo) == 1.0


def test_el_error_maximo_da_un_positivo_muy_chico():
    """Verifica que el peor caso posible siga siendo estrictamente mayor que cero."""
    aptitud = calcular_fitness(imagen(0), imagen(255))
    assert aptitud > 0.0
    assert aptitud == pytest.approx(1.0 / (1.0 + ERROR_MAXIMO))


def test_la_aptitud_preserva_el_orden_del_error():
    """Verifica que a menos error corresponda más aptitud, que es lo que hace que la selección signifique algo."""
    objetivo = imagen(200)
    aptitudes = [calcular_fitness(imagen(v), objetivo) for v in (100, 150, 190, 200)]
    assert aptitudes == sorted(aptitudes)
    assert len(set(aptitudes)) == len(aptitudes)
    assert aptitudes[-1] == 1.0


def test_el_canal_alfa_no_entra_en_la_comparacion():
    """Verifica que dos imágenes que solo difieren en transparencia den aptitud máxima."""
    objetivo = imagen(100, canales=4)
    fenotipo = objetivo.copy()
    fenotipo[..., 3] = 0
    assert calcular_fitness(fenotipo, objetivo) == 1.0


def test_las_diferencias_negativas_no_desbordan():
    """Verifica que restar colores sin signo no dé la vuelta: el error es simétrico."""
    claro, oscuro = imagen(200), imagen(50)
    assert calcular_fitness(claro, oscuro) == calcular_fitness(oscuro, claro)
    assert calcular_fitness(claro, oscuro) == pytest.approx(1.0 / (1.0 + 150.0**2))


def test_formas_distintas_cortan_con_error():
    """Verifica que comparar imágenes de distinto tamaño falle en vez de devolver un número sin sentido."""
    with pytest.raises(ValueError):
        calcular_fitness(imagen(0, alto=4), imagen(0, alto=8))


def test_no_modifica_las_matrices_que_recibe():
    """Verifica que la aptitud sea una función pura sobre las dos imágenes."""
    fenotipo, objetivo = imagen(10), imagen(240)
    copia_fenotipo, copia_objetivo = fenotipo.copy(), objetivo.copy()
    calcular_fitness(fenotipo, objetivo)
    assert np.array_equal(fenotipo, copia_fenotipo)
    assert np.array_equal(objetivo, copia_objetivo)
