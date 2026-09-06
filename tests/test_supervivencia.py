"""Tests exhaustivos para las estrategias de supervivencia y sus rutinas comunes."""

import pytest

from src.poblacion import ErrorDePoblacion
from src.seleccion import elite, ruleta
from src.supervivencia import aditiva, comun, exclusiva
from tests.helpers import (
    config_test,
    crear_individuo,
    crear_poblacion_test,
    generador_azar,
)


def test_comun_sin_repetir_referencias_elimina_duplicados():
    """Verifica que sin_repetir_referencias reemplace instancias repetidas por copias."""
    ind1 = crear_individuo(fitness_val=0.5, marca=1)
    ind2 = crear_individuo(fitness_val=0.8, marca=2)
    repetidos = [ind1, ind2, ind1, ind1, ind2]

    limpios = comun.sin_repetir_referencias(repetidos)

    assert len(limpios) == 5
    assert len({id(ind) for ind in limpios}) == 5
    assert limpios[0] is ind1 and limpios[1] is ind2
    assert limpios[2] is not ind1 and limpios[3] is not ind1
    assert limpios[4] is not ind2
    assert all(ind.fitness_cacheado is not None for ind in limpios)


@pytest.mark.parametrize("estrategia", [aditiva, exclusiva])
def test_invariantes_supervivencia_largo_y_no_mutacion(estrategia):
    """Verifica que la salida tenga el largo pedido y no altere las listas de entrada."""
    actuales = [crear_individuo(fitness_val=0.1 * i, marca=i) for i in range(5)]
    hijos = [crear_individuo(fitness_val=0.2 * i, marca=10 + i) for i in range(4)]
    actuales_orig = list(actuales)
    hijos_orig = list(hijos)

    salida = estrategia.sobrevivientes(
        actuales, hijos, 5, elite.seleccionar, generador_azar(), config_test()
    )

    assert len(salida) == 5
    assert len({id(ind) for ind in salida}) == 5
    assert actuales == actuales_orig
    assert hijos == hijos_orig


def test_aditiva_selecciona_mejores_del_pozo_combinado():
    """Verifica que con élite supervivencia aditiva conserve los mejores de padres e hijos."""
    actuales = [
        crear_individuo(fitness_val=0.1, marca=0),
        crear_individuo(fitness_val=0.9, marca=1),
    ]
    hijos = [
        crear_individuo(fitness_val=0.4, marca=2),
        crear_individuo(fitness_val=0.8, marca=3),
    ]
    salida = aditiva.sobrevivientes(
        actuales, hijos, 2, elite.seleccionar, generador_azar(), config_test()
    )

    assert len(salida) == 2
    assert salida[0] is actuales[1]
    assert salida[1] is hijos[1]


def test_aditiva_todos_hijos_superan_a_padres():
    """Verifica que si todos los hijos son superiores reemplacen totalmente a los padres en aditiva."""
    actuales = [crear_individuo(fitness_val=0.1, marca=i) for i in range(3)]
    hijos = [crear_individuo(fitness_val=0.8 + 0.05 * i, marca=10 + i) for i in range(3)]

    salida = aditiva.sobrevivientes(
        actuales, hijos, 3, elite.seleccionar, generador_azar(), config_test()
    )
    for ind in salida:
        assert ind in hijos


def test_exclusiva_caso_k_mayor_que_n():
    """Verifica que con K > N solo sobrevivan hijos y ningún padre, usando selección."""
    actuales = [crear_individuo(fitness_val=0.99, marca=i) for i in range(3)]
    hijos = [
        crear_individuo(fitness_val=0.1, marca=10),
        crear_individuo(fitness_val=0.8, marca=11),
        crear_individuo(fitness_val=0.5, marca=12),
        crear_individuo(fitness_val=0.2, marca=13),
    ]
    salida = exclusiva.sobrevivientes(
        actuales, hijos, 2, elite.seleccionar, generador_azar(), config_test()
    )

    assert len(salida) == 2
    assert salida[0] is hijos[1]
    assert salida[1] is hijos[2]
    assert all(ind not in actuales for ind in salida)


def test_exclusiva_caso_k_igual_n():
    """Verifica que con K = N la nueva generación esté formada íntegramente por los hijos."""
    actuales = [crear_individuo(fitness_val=0.9, marca=i) for i in range(3)]
    hijos = [crear_individuo(fitness_val=0.2, marca=10 + i) for i in range(3)]

    salida = exclusiva.sobrevivientes(
        actuales, hijos, 3, None, generador_azar(), config_test()
    )
    assert salida == hijos
    assert all(ind not in actuales for ind in salida)


def test_exclusiva_caso_k_menor_que_n():
    """Verifica que con K < N entren todos los hijos y se complete con padres seleccionados."""
    actuales = [
        crear_individuo(fitness_val=0.2, marca=0),
        crear_individuo(fitness_val=0.9, marca=1),
        crear_individuo(fitness_val=0.4, marca=2),
    ]
    hijos = [crear_individuo(fitness_val=0.1, marca=10)]

    salida = exclusiva.sobrevivientes(
        actuales, hijos, 3, elite.seleccionar, generador_azar(), config_test()
    )

    assert len(salida) == 3
    assert salida[0] is hijos[0]
    assert salida[1] is actuales[1]
    assert salida[2] is actuales[2]


def test_supervivencia_resultado_valido_en_poblacion():
    """Verifica que la generación devuelta sea directamente aceptada por Poblacion.siguiente."""
    poblacion = crear_poblacion_test([0.2, 0.5, 0.8, 0.3])
    hijos = [crear_individuo(fitness_val=0.6, cant_genes=4, marca=20 + i) for i in range(4)]

    for estrategia in (aditiva, exclusiva):
        sobrevivientes = estrategia.sobrevivientes(
            poblacion.individuos,
            hijos,
            len(poblacion),
            ruleta.seleccionar,
            generador_azar(),
            config_test(),
        )
        siguiente = poblacion.siguiente(sobrevivientes)
        assert len(siguiente) == len(poblacion)
        assert siguiente.generacion == poblacion.generacion + 1
        assert siguiente.diversidad() >= 0.0
