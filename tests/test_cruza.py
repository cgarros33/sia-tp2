"""Tests exhaustivos para los métodos de cruza y sus rutinas comunes."""

import numpy as np
import pytest

from src.cruza import anular, comun, dos_puntos, un_punto, uniforme
from src.cruza.comun import ErrorDeCruza
from tests.helpers import (
    SEMILLA_TEST,
    config_test,
    crear_individuo,
    crear_triangulo,
    generador_azar,
)


def _genes_origen(padre, madre, hijo):
    """Devuelve 'P' si el gen proviene del padre o 'M' si proviene de la madre."""
    origen = []
    for locus in range(len(hijo)):
        param_h = hijo.gen(locus).parametros()
        param_p = padre.gen(locus).parametros()
        param_m = madre.gen(locus).parametros()
        if param_h == param_p:
            origen.append("P")
        elif param_h == param_m:
            origen.append("M")
        else:
            origen.append("?")
    return "".join(origen)


def test_comun_distinto_largo_lanza_error():
    """Verifica que largo_comun corte con ErrorDeCruza si los padres difieren en longitud."""
    padre = crear_individuo(cant_genes=4)
    madre = crear_individuo(cant_genes=5)
    with pytest.raises(ErrorDeCruza, match="misma cantidad de genes"):
        comun.largo_comun(padre, madre)


def test_comun_mascara_vacia_devuelve_copias_con_fitness():
    """Verifica que una máscara vacía devuelva copias con el fitness cacheado intacto."""
    padre = crear_individuo(fitness_val=0.8, cant_genes=3, marca=0)
    madre = crear_individuo(fitness_val=0.3, cant_genes=3, marca=100)
    mascara = np.zeros(3, dtype=bool)
    h1, h2 = comun.hijos_por_mascara(padre, madre, mascara)
    assert h1 is not padre and h2 is not madre
    assert h1.fitness_cacheado == 0.8 and not h1.esta_sucio
    assert h2.fitness_cacheado == 0.3 and not h2.esta_sucio


def test_comun_mascara_completa_devuelve_copias_cruzadas():
    """Verifica que una máscara completa devuelva copias cruzadas con fitness cacheado."""
    padre = crear_individuo(fitness_val=0.8, cant_genes=3, marca=0)
    madre = crear_individuo(fitness_val=0.3, cant_genes=3, marca=100)
    mascara = np.ones(3, dtype=bool)
    h1, h2 = comun.hijos_por_mascara(padre, madre, mascara)
    assert h1 is not madre and h2 is not padre
    assert h1.fitness_cacheado == 0.3 and not h1.esta_sucio
    assert h2.fitness_cacheado == 0.8 and not h2.esta_sucio


@pytest.mark.parametrize("metodo", [un_punto, dos_puntos, uniforme, anular])
def test_invariantes_cruza_hijos_nuevos_y_complementarios(metodo):
    """Verifica que todo método devuelva 2 hijos nuevos, del mismo largo y complementarios."""
    largo = 8
    padre = crear_individuo(cant_genes=largo, marca=0)
    madre = crear_individuo(cant_genes=largo, marca=100)
    azar = generador_azar()
    config = config_test()

    h1, h2 = metodo.cruzar(padre, madre, azar, config)

    assert h1 is not padre and h1 is not madre
    assert h2 is not padre and h2 is not madre
    assert len(h1) == largo and len(h2) == largo

    origen1 = _genes_origen(padre, madre, h1)
    origen2 = _genes_origen(padre, madre, h2)
    assert "?" not in origen1 and "?" not in origen2

    for locus in range(largo):
        assert {origen1[locus], origen2[locus]} == {"P", "M"}


def test_un_punto_corte_valido():
    """Verifica que cruce de un punto genere exactamente una transición de locus."""
    largo = 10
    padre = crear_individuo(cant_genes=largo, marca=0)
    madre = crear_individuo(cant_genes=largo, marca=100)
    azar = generador_azar()
    h1, h2 = un_punto.cruzar(padre, madre, azar, config_test())
    origen = _genes_origen(padre, madre, h1)
    assert "P" in origen and "M" in origen
    assert "MP" not in origen


def test_un_punto_largo_uno():
    """Verifica el comportamiento de cruce de un punto en cromosoma de longitud 1."""
    padre = crear_individuo(fitness_val=0.5, cant_genes=1, marca=0)
    madre = crear_individuo(fitness_val=0.7, cant_genes=1, marca=100)
    h1, h2 = un_punto.cruzar(padre, madre, generador_azar(), config_test())
    assert h1 is not padre and h2 is not madre
    assert h1.fitness_cacheado == 0.5
    assert h2.fitness_cacheado == 0.7


def test_dos_puntos_tres_bloques():
    """Verifica que cruce de dos puntos intercambie un bloque central dejando prefijo y sufijo."""
    largo = 12
    padre = crear_individuo(cant_genes=largo, marca=0)
    madre = crear_individuo(cant_genes=largo, marca=100)
    azar = generador_azar()
    h1, h2 = dos_puntos.cruzar(padre, madre, azar, config_test())
    origen = _genes_origen(padre, madre, h1)
    assert origen.startswith("P") and origen.endswith("P")
    assert "M" in origen


def test_dos_puntos_largo_menor_a_tres():
    """Verifica que con menos de 3 genes dos_puntos devuelva copias sin romper."""
    padre = crear_individuo(fitness_val=0.5, cant_genes=2, marca=0)
    madre = crear_individuo(fitness_val=0.7, cant_genes=2, marca=100)
    h1, h2 = dos_puntos.cruzar(padre, madre, generador_azar(), config_test())
    assert h1.fitness_cacheado == 0.5
    assert h2.fitness_cacheado == 0.7


def test_uniforme_probabilidades_extremas():
    """Verifica que cruce uniforme con P=0 devuelva padres y con P=1 intercambiados."""
    padre = crear_individuo(fitness_val=0.6, cant_genes=4, marca=0)
    madre = crear_individuo(fitness_val=0.9, cant_genes=4, marca=100)

    h1_p0, h2_p0 = uniforme.cruzar(
        padre, madre, generador_azar(), config_test(uniform_crossover_P=0.0)
    )
    assert _genes_origen(padre, madre, h1_p0) == "PPPP"
    assert h1_p0.fitness_cacheado == 0.6

    h1_p1, h2_p1 = uniforme.cruzar(
        padre, madre, generador_azar(), config_test(uniform_crossover_P=1.0)
    )
    assert _genes_origen(padre, madre, h1_p1) == "MMMM"
    assert h1_p1.fitness_cacheado == 0.9


def test_anular_segmento_interior():
    """Verifica que cruce anular intercambie un segmento continuo acotado a la mitad del largo."""
    largo = 10
    padre = crear_individuo(cant_genes=largo, marca=0)
    madre = crear_individuo(cant_genes=largo, marca=100)
    azar = generador_azar()
    h1, _ = anular.cruzar(padre, madre, azar, config_test())
    origen = _genes_origen(padre, madre, h1)
    cant_m = origen.count("M")
    assert 1 <= cant_m <= largo // 2


def test_anular_segmento_circular_desborda():
    """Verifica que cruce anular cuando desborda el anillo afecte a los extremos simultáneamente."""
    largo = 6
    padre = crear_individuo(cant_genes=largo, marca=0)
    madre = crear_individuo(cant_genes=largo, marca=100)

    for seed in range(50):
        azar = generador_azar(seed)
        h1, _ = anular.cruzar(padre, madre, azar, config_test())
        origen = _genes_origen(padre, madre, h1)
        if origen.startswith("M") and origen.endswith("M") and "P" in origen:
            break
    else:
        pytest.fail("No se encontró ningún caso de desborde en el anillo")


def test_cruza_reproducibilidad_con_semilla():
    """Verifica que con la misma semilla los métodos de cruza den resultados idénticos."""
    padre = crear_individuo(cant_genes=8, marca=0)
    madre = crear_individuo(cant_genes=8, marca=100)

    for metodo in (un_punto, dos_puntos, uniforme, anular):
        h1_a, h2_a = metodo.cruzar(
            padre, madre, generador_azar(SEMILLA_TEST), config_test()
        )
        h1_b, h2_b = metodo.cruzar(
            padre, madre, generador_azar(SEMILLA_TEST), config_test()
        )
        assert _genes_origen(padre, madre, h1_a) == _genes_origen(padre, madre, h1_b)
        assert _genes_origen(padre, madre, h2_a) == _genes_origen(padre, madre, h2_b)
