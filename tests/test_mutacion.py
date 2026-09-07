"""Tests exhaustivos para los métodos de mutación y sus rutinas comunes."""

import numpy as np
import pytest

from src.figuras.familias import COLOR_MAXIMO
from src.mutacion import comun, gen, multigen, no_uniforme, uniforme
from tests.helpers import (
    SEMILLA_TEST,
    config_test,
    crear_individuo,
    generador_azar,
)


def _contar_genes_mutados(original, mutado):
    """Devuelve cuántos genes difieren en sus parámetros entre los dos individuos."""
    return sum(
        1
        for g_orig, g_mut in zip(original.genes, mutado.genes)
        if g_orig.parametros() != g_mut.parametros()
    )


@pytest.mark.parametrize("metodo", [gen, multigen, uniforme, no_uniforme])
def test_invariantes_mutacion_en_el_lugar(metodo):
    """Verifica que los cuatro métodos muten in-place y preserven la longitud."""
    largo = 6
    ind = crear_individuo(cant_genes=largo)
    ret = metodo.mutar(ind, generador_azar(), config_test(), 100, 100)
    assert ret is ind
    assert len(ind) == largo


@pytest.mark.parametrize("metodo", [gen, multigen, uniforme, no_uniforme])
def test_mutacion_probabilidad_cero_no_modifica_nada(metodo):
    """Verifica que con extra_gene_Pm en cero ningún gen cambie y el fitness cacheado sobreviva."""
    ind = crear_individuo(fitness_val=0.75, cant_genes=5)
    config = config_test(extra_gene_Pm=0.0)
    metodo.mutar(ind, generador_azar(), config, 100, 100)
    assert not ind.esta_sucio
    assert ind.fitness_cacheado == 0.75


def test_mutacion_invalida_cache_si_cambia():
    """Verifica que al modificarse parámetros el fitness cacheado se invalide y pase a sucio."""
    ind = crear_individuo(fitness_val=0.75, cant_genes=5)
    config = config_test(extra_gene_Pm=1.0, intra_gene_Pm=1.0)
    gen.mutar(ind, generador_azar(), config, 100, 100)
    assert ind.esta_sucio
    assert ind.fitness_cacheado is None


def test_gen_muta_como_maximo_un_gen():
    """Verifica que mutación por gen altere exactamente un gen con Pm=1 y como máximo uno con Pm menor."""
    config_seguro = config_test(extra_gene_Pm=1.0, intra_gene_Pm=1.0)
    ind = crear_individuo(cant_genes=8)
    clon = ind.copiar()
    gen.mutar(clon, generador_azar(), config_seguro, 100, 100)
    assert _contar_genes_mutados(ind, clon) == 1

    config_azar = config_test(extra_gene_Pm=0.5, intra_gene_Pm=1.0)
    for seed in range(20):
        clon_azar = ind.copiar()
        gen.mutar(clon_azar, generador_azar(seed), config_azar, 100, 100)
        assert _contar_genes_mutados(ind, clon_azar) in (0, 1)


def test_multigen_acotado_por_max_genes():
    """Verifica que multigen mute entre 1 y max_genes_to_mutate genes con Pm=1."""
    max_genes = 3
    largo = 8
    config = config_test(
        max_genes_to_mutate=max_genes, extra_gene_Pm=1.0, intra_gene_Pm=1.0
    )
    ind = crear_individuo(cant_genes=largo)

    for seed in range(20):
        clon = ind.copiar()
        multigen.mutar(clon, generador_azar(seed), config, 100, 100)
        mutados = _contar_genes_mutados(ind, clon)
        assert 1 <= mutados <= min(max_genes, largo)


def test_uniforme_muta_todos_con_probabilidad_uno():
    """Verifica que mutación uniforme mute la totalidad de los genes si Pm e intra son uno."""
    largo = 6
    config = config_test(extra_gene_Pm=1.0, intra_gene_Pm=1.0)
    ind = crear_individuo(cant_genes=largo)
    clon = ind.copiar()
    uniforme.mutar(clon, generador_azar(), config, 100, 100)
    assert _contar_genes_mutados(ind, clon) == largo


def test_no_uniforme_todo_o_nada():
    """Verifica que mutación no uniforme mute todos los genes o ninguno, sin valores intermedios."""
    largo = 7
    config = config_test(extra_gene_Pm=0.5, intra_gene_Pm=1.0)
    ind = crear_individuo(cant_genes=largo)

    mutados_historial = set()
    for seed in range(30):
        clon = ind.copiar()
        no_uniforme.mutar(clon, generador_azar(seed), config, 100, 100)
        cant = _contar_genes_mutados(ind, clon)
        assert cant in (0, largo)
        mutados_historial.add(cant)

    assert 0 in mutados_historial and largo in mutados_historial


def test_mutacion_respeta_limites_canvas():
    """Verifica que las coordenadas y colores mutados queden dentro del dominio admisible."""
    ancho, alto = 100, 80
    overflow = 10.0
    config = config_test(
        extra_gene_Pm=1.0,
        intra_gene_Pm=1.0,
        max_coord_overflow=overflow,
        max_coord_delta=500.0,
        max_color_delta=500,
    )
    ind = crear_individuo(cant_genes=5)
    uniforme.mutar(ind, generador_azar(), config, ancho, alto)

    for gen_actual in ind.genes:
        params = gen_actual.parametros()
        puntos = params[:6]
        color = params[6:]
        for x in puntos[0::2]:
            assert -overflow <= x <= ancho + overflow
        for y in puntos[1::2]:
            assert -overflow <= y <= alto + overflow
        for c in color:
            assert 0 <= c <= COLOR_MAXIMO


def test_mutacion_reproducibilidad_con_semilla():
    """Verifica que con la misma semilla los métodos de mutación produzcan exactamente los mismos cambios."""
    ind = crear_individuo(cant_genes=6)
    config = config_test(extra_gene_Pm=0.8, intra_gene_Pm=0.8)

    for metodo in (gen, multigen, uniforme, no_uniforme):
        clon_a = ind.copiar()
        clon_b = ind.copiar()
        metodo.mutar(clon_a, generador_azar(SEMILLA_TEST), config, 100, 100)
        metodo.mutar(clon_b, generador_azar(SEMILLA_TEST), config, 100, 100)
        assert clon_a.vector_parametros().tolist() == clon_b.vector_parametros().tolist()
