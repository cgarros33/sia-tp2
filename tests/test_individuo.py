"""Pruebas del individuo: el caché de aptitud, su invalidación y la independencia de la copia."""

import pytest

from src.individuo import ErrorDeIndividuo, Individuo
from tests.helpers import crear_individuo, crear_triangulo


class EvaluadorContador:
    """Evaluador de mentira que cuenta cuántas veces lo llamaron."""

    def __init__(self, valor=0.5):
        """Guarda la aptitud que va a devolver siempre."""
        self.valor = valor
        self.llamadas = 0

    def __call__(self, genes):
        """Cuenta la llamada y devuelve la aptitud fija."""
        self.llamadas += 1
        return self.valor


def test_el_cache_evita_recalcular():
    """Verifica que pedir dos veces la aptitud de un individuo que no cambió la calcule una sola vez."""
    individuo = crear_individuo(cant_genes=3)
    evaluador = EvaluadorContador(0.7)

    assert individuo.fitness(evaluador) == 0.7
    assert individuo.fitness(evaluador) == 0.7
    assert evaluador.llamadas == 1


def test_cambiar_un_gen_invalida_el_cache():
    """Verifica que reemplazar un gen por otro distinto obligue a renderizar de nuevo."""
    individuo = crear_individuo(cant_genes=3)
    evaluador = EvaluadorContador(0.7)
    individuo.fitness(evaluador)

    individuo.establecer_gen(1, crear_triangulo(marca=999))

    assert individuo.esta_sucio
    assert individuo.fitness_cacheado is None
    assert individuo.fitness(evaluador) == 0.7
    assert evaluador.llamadas == 2


def test_reemplazar_por_un_gen_de_iguales_parametros_no_invalida():
    """Verifica que el caché se invalide por cambio de parámetros y no por cambio de objeto."""
    individuo = crear_individuo(cant_genes=3)
    evaluador = EvaluadorContador(0.7)
    individuo.fitness(evaluador)

    mismo = crear_triangulo(marca=1)
    assert mismo is not individuo.gen(1)
    assert mismo.parametros() == individuo.gen(1).parametros()

    individuo.establecer_gen(1, mismo)

    assert not individuo.esta_sucio
    assert individuo.fitness(evaluador) == 0.7
    assert evaluador.llamadas == 1


def test_la_copia_no_comparte_la_lista_de_genes():
    """Verifica que cambiarle un gen a la copia no toque al original."""
    original = crear_individuo(cant_genes=4)
    parametros_antes = [gen.parametros() for gen in original.genes]

    copia = original.copiar()
    copia.establecer_gen(0, crear_triangulo(marca=999))

    assert copia is not original
    assert [gen.parametros() for gen in original.genes] == parametros_antes
    assert original.gen(0).parametros() != copia.gen(0).parametros()


def test_la_copia_conserva_la_aptitud_porque_los_genes_no_cambian():
    """Verifica que copiar no invalide el caché: sobrevivir de una generación a otra no cambia el genotipo."""
    original = crear_individuo(cant_genes=3)
    evaluador = EvaluadorContador(0.42)
    original.fitness(evaluador)

    copia = original.copiar()

    assert not copia.esta_sucio
    assert copia.fitness_cacheado == 0.42
    assert copia.fitness(evaluador) == 0.42
    assert evaluador.llamadas == 1


def test_la_copia_de_un_individuo_sucio_nace_sucia():
    """Verifica que la copia arrastre el estado del caché y no invente una aptitud vigente."""
    original = crear_individuo(cant_genes=3)
    copia = original.copiar()

    assert copia.esta_sucio
    assert copia.fitness_cacheado is None


def test_el_vector_de_parametros_concatena_los_genes_en_orden():
    """Verifica que el vector que consume la diversidad respete el orden de dibujado."""
    individuo = crear_individuo(cant_genes=3)
    esperado = [valor for gen in individuo.genes for valor in gen.parametros()]

    assert list(individuo.vector_parametros()) == esperado
    assert len(individuo.nombres_parametros()) == len(individuo.vector_parametros())


def test_el_vector_de_parametros_se_recalcula_al_cambiar_un_gen():
    """Verifica que el vector cacheado no quede viejo después de una mutación."""
    individuo = crear_individuo(cant_genes=2)
    individuo.vector_parametros()

    individuo.establecer_gen(0, crear_triangulo(marca=777))

    esperado = [valor for gen in individuo.genes for valor in gen.parametros()]
    assert list(individuo.vector_parametros()) == esperado


def test_los_genes_se_devuelven_como_tupla_en_orden():
    """Verifica que exponer los genes no permita modificar la lista interna."""
    individuo = crear_individuo(cant_genes=3)
    genes = individuo.genes

    assert isinstance(genes, tuple)
    assert len(genes) == len(individuo) == 3
    assert all(genes[i] is individuo.gen(i) for i in range(3))


def test_un_individuo_sin_genes_falla():
    """Verifica que un cromosoma vacío corte con un error del dominio y no más adelante."""
    with pytest.raises(ErrorDeIndividuo):
        Individuo([])
