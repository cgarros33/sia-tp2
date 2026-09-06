"""Tests exhaustivos para los métodos de selección y sus rutinas comunes."""

import math
import numpy as np
import pytest

from src.seleccion import (
    boltzmann,
    comun,
    elite,
    ranking,
    ruleta,
    torneo_deterministico,
    torneo_probabilistico,
    universal,
)
from src.seleccion.comun import ErrorDeSeleccion
from tests.helpers import (
    SEMILLA_TEST,
    config_test,
    crear_individuo,
    generador_azar,
)


def test_comun_aptitudes_requiere_fitness_cacheado():
    """Verifica que aptitudes corte con ErrorDeSeleccion si hay individuos sin evaluar."""
    individuos = [crear_individuo(fitness_val=1.0), crear_individuo(fitness_val=None)]
    with pytest.raises(ErrorDeSeleccion, match="sin fitness cacheado"):
        comun.aptitudes(individuos)


def test_comun_orden_por_fitness_estable():
    """Verifica que orden_por_fitness sea descendente y estable ante empates."""
    valores = np.array([0.2, 0.8, 0.5, 0.8, 0.1])
    indices = comun.orden_por_fitness(valores)
    assert list(indices) == [1, 3, 2, 0, 4]


def test_comun_pesos_no_positivos():
    """Verifica que seleccionar_por_pesos corte si la suma de pesos no es mayor a cero."""
    individuos = [crear_individuo(fitness_val=0.0)]
    with pytest.raises(ErrorDeSeleccion, match="sumar más que cero"):
        comun.seleccionar_por_pesos(individuos, np.array([0.0]), np.array([0.5]))


def test_comun_seleccionar_por_pesos_acorta_al_limite():
    """Verifica que sorteos cercanos a uno caigan en el último índice sin salirse del rango."""
    individuos = [crear_individuo(fitness_val=1.0, marca=i) for i in range(3)]
    pesos = np.array([1.0, 1.0, 1.0])
    elegidos = comun.seleccionar_por_pesos(individuos, pesos, np.array([0.999999999]))
    assert elegidos[0] is individuos[2]


def test_elite_selecciona_mejores_exactos():
    """Verifica que élite seleccione estrictamente a los mejores cuando K <= N."""
    individuos = [
        crear_individuo(fitness_val=0.1, marca=0),
        crear_individuo(fitness_val=0.9, marca=1),
        crear_individuo(fitness_val=0.4, marca=2),
        crear_individuo(fitness_val=0.7, marca=3),
    ]
    azar = generador_azar()
    config = config_test()
    elegidos = elite.seleccionar(individuos, 2, azar, config)
    assert len(elegidos) == 2
    assert elegidos[0] is individuos[1]
    assert elegidos[1] is individuos[3]


def test_elite_repeticiones_cuando_k_mayor_n():
    """Verifica que las repeticiones sigan la fórmula techo((K - i) / N)."""
    individuos = [
        crear_individuo(fitness_val=0.1, marca=0),
        crear_individuo(fitness_val=0.9, marca=1),
        crear_individuo(fitness_val=0.5, marca=2),
    ]
    azar = generador_azar()
    config = config_test()
    elegidos = elite.seleccionar(individuos, 7, azar, config)
    assert len(elegidos) == 7
    total = len(individuos)
    cuenta = {ind: elegidos.count(ind) for ind in individuos}
    assert cuenta[individuos[1]] == math.ceil((7 - 0) / total)
    assert cuenta[individuos[2]] == math.ceil((7 - 1) / total)
    assert cuenta[individuos[0]] == math.ceil((7 - 2) / total)


def test_elite_estabilidad_empates():
    """Verifica que ante igual fitness se respete el orden original de aparición."""
    individuos = [
        crear_individuo(fitness_val=0.5, marca=1),
        crear_individuo(fitness_val=0.5, marca=2),
    ]
    elegidos = elite.seleccionar(individuos, 2, generador_azar(), config_test())
    assert elegidos[0] is individuos[0]
    assert elegidos[1] is individuos[1]


def test_ruleta_largo_y_referencias():
    """Verifica que ruleta devuelva la cantidad solicitada con referencias a la población original."""
    individuos = [crear_individuo(fitness_val=0.2 + 0.1 * i, marca=i) for i in range(5)]
    azar = generador_azar()
    elegidos = ruleta.seleccionar(individuos, 8, azar, config_test())
    assert len(elegidos) == 8
    for ind in elegidos:
        assert any(ind is original for original in individuos)


def test_ruleta_proporcionalidad_sesgo_extremo():
    """Verifica que un individuo con fitness desproporcionadamente alto sea el casi exclusivo."""
    individuos = [
        crear_individuo(fitness_val=1000.0, marca=0),
        crear_individuo(fitness_val=0.001, marca=1),
        crear_individuo(fitness_val=0.001, marca=2),
    ]
    azar = generador_azar()
    elegidos = ruleta.seleccionar(individuos, 20, azar, config_test())
    assert elegidos.count(individuos[0]) >= 19


def test_ruleta_reproducibilidad_con_semilla():
    """Verifica que dos corridas de ruleta con la misma semilla den resultados idénticos."""
    individuos = [crear_individuo(fitness_val=0.1 * i, marca=i) for i in range(1, 6)]
    res1 = ruleta.seleccionar(individuos, 5, generador_azar(SEMILLA_TEST), config_test())
    res2 = ruleta.seleccionar(individuos, 5, generador_azar(SEMILLA_TEST), config_test())
    assert [id(x) for x in res1] == [id(x) for x in res2]


def test_universal_largo_y_referencias():
    """Verifica cantidad y pertenencia de referencias en selección universal."""
    individuos = [crear_individuo(fitness_val=0.1 * i, marca=i) for i in range(1, 5)]
    azar = generador_azar()
    elegidos = universal.seleccionar(individuos, 6, azar, config_test())
    assert len(elegidos) == 6
    for ind in elegidos:
        assert any(ind is orig for orig in individuos)


def test_universal_poblacion_homogenea_seleccion_exacta():
    """Verifica que sobre población homogénea y K=N cada individuo salga exactamente una vez."""
    individuos = [crear_individuo(fitness_val=0.5, marca=i) for i in range(6)]
    azar = generador_azar()
    elegidos = universal.seleccionar(individuos, 6, azar, config_test())
    assert len(elegidos) == 6
    for ind in individuos:
        assert elegidos.count(ind) == 1


def test_boltzmann_valores_esperados_formula():
    """Verifica que los valores esperados de Boltzmann coincidan con la fórmula matemática."""
    valores = np.array([0.2, 0.4, 0.6])
    temperatura = 0.5
    esperados = boltzmann.valores_esperados(valores, temperatura)
    exps = np.exp((valores - valores.max()) / temperatura)
    teorico = exps / exps.mean()
    assert np.allclose(esperados, teorico)


def test_boltzmann_temperatura_baja_favorece_mejor():
    """Verifica que con temperatura tendiendo a cero Boltzmann seleccione casi siempre al mejor."""
    individuos = [
        crear_individuo(fitness_val=0.2, marca=0),
        crear_individuo(fitness_val=0.8, marca=1),
    ]
    config = config_test(temperature=0.01)
    azar = generador_azar()
    elegidos = boltzmann.seleccionar(individuos, 15, azar, config)
    assert elegidos.count(individuos[1]) == 15


def test_boltzmann_inmunidad_a_desborde():
    """Verifica que la resta del máximo impida división por cero o desbordes numéricos."""
    valores = np.array([1000.0, 100.0, 50.0])
    pesos = boltzmann.valores_esperados(valores, temperatura=0.001)
    assert not np.any(np.isnan(pesos))
    assert not np.any(np.isinf(pesos))
    assert pesos[0] > 0.0


def test_torneo_deterministico_largo_y_referencias():
    """Verifica cantidad y pertenencia de referencias en torneo determinístico."""
    individuos = [crear_individuo(fitness_val=0.1 * i, marca=i) for i in range(1, 6)]
    azar = generador_azar()
    elegidos = torneo_deterministico.seleccionar(
        individuos, 4, azar, config_test(tournament_size=2)
    )
    assert len(elegidos) == 4
    for ind in elegidos:
        assert any(ind is orig for orig in individuos)


def test_torneo_deterministico_tamano_poblacion_gana_siempre_mejor():
    """Verifica que si tournament_size es mayor o igual a la población gane siempre el mejor."""
    individuos = [
        crear_individuo(fitness_val=0.2, marca=0),
        crear_individuo(fitness_val=0.9, marca=1),
        crear_individuo(fitness_val=0.4, marca=2),
    ]
    config = config_test(tournament_size=10)
    azar = generador_azar()
    elegidos = torneo_deterministico.seleccionar(individuos, 5, azar, config)
    assert all(ind is individuos[1] for ind in elegidos)


def test_torneo_deterministico_desempate():
    """Verifica que un empate en fitness lo gane el de menor índice en la lista original."""
    individuos = [
        crear_individuo(fitness_val=0.5, marca=0),
        crear_individuo(fitness_val=0.5, marca=1),
    ]
    config = config_test(tournament_size=2)
    azar = generador_azar()
    elegidos = torneo_deterministico.seleccionar(individuos, 4, azar, config)
    assert all(ind is individuos[0] for ind in elegidos)


def test_torneo_probabilistico_largo_y_referencias():
    """Verifica cantidad y pertenencia de referencias en torneo probabilístico."""
    individuos = [crear_individuo(fitness_val=0.2 * i, marca=i) for i in range(1, 5)]
    azar = generador_azar()
    elegidos = torneo_probabilistico.seleccionar(individuos, 4, azar, config_test())
    assert len(elegidos) == 4
    for ind in elegidos:
        assert any(ind is orig for orig in individuos)


def test_torneo_probabilistico_umbral_uno_gana_mejor():
    """Verifica que con tournament_threshold en uno siempre gane el más apto de la pareja sorteada."""
    individuos = [
        crear_individuo(fitness_val=0.1, marca=0),
        crear_individuo(fitness_val=0.9, marca=1),
    ]
    config = config_test(tournament_threshold=1.0)
    azar = generador_azar()
    elegidos = torneo_probabilistico.seleccionar(individuos, 10, azar, config)
    assert all(ind is individuos[1] for ind in elegidos)


def test_torneo_probabilistico_umbral_cero_gana_peor():
    """Verifica que con tournament_threshold en cero siempre gane el menos apto de la pareja sorteada."""
    individuos = [
        crear_individuo(fitness_val=0.1, marca=0),
        crear_individuo(fitness_val=0.9, marca=1),
    ]
    config = config_test(tournament_threshold=0.0)
    azar = generador_azar()
    elegidos = torneo_probabilistico.seleccionar(individuos, 10, azar, config)
    assert all(ind is individuos[0] for ind in elegidos)


def test_ranking_pesos_lineales_formula():
    """Verifica que pesos_por_ranking asigne (N - posicion) / N con posicion desde cero."""
    individuos = [
        crear_individuo(fitness_val=0.1, marca=0),
        crear_individuo(fitness_val=0.9, marca=1),
        crear_individuo(fitness_val=0.5, marca=2),
    ]
    ordenados, pesos = ranking.pesos_por_ranking(individuos)
    assert ordenados == [individuos[1], individuos[2], individuos[0]]
    assert np.allclose(pesos, np.array([3 / 3, 2 / 3, 1 / 3]))


def test_ranking_invarianza_de_escala():
    """Verifica que multiplicar y desplazar los fitness no altere los pesos de ranking."""
    ind1 = [crear_individuo(fitness_val=0.0001 * i, marca=i) for i in range(4)]
    ind2 = [crear_individuo(fitness_val=1000.0 * i + 50.0, marca=i) for i in range(4)]
    _, pesos1 = ranking.pesos_por_ranking(ind1)
    _, pesos2 = ranking.pesos_por_ranking(ind2)
    assert np.allclose(pesos1, pesos2)
