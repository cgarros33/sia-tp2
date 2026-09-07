"""Prueba de punta a punta: la misma semilla tiene que dar exactamente la misma corrida."""

from pathlib import Path

import numpy as np

from src.config import cargar_config
from src.motor import ejecutar_motor

RUTA_CONFIG = Path(__file__).resolve().parents[1] / "config" / "conf.json"
ANCHO = 24
ALTO = 24


def objetivo_de_prueba():
    """Devuelve una imagen objetivo chica generada en memoria, con dos zonas de color."""
    imagen = np.zeros((ALTO, ANCHO, 3), dtype=np.uint8)
    imagen[:, : ANCHO // 2] = (200, 40, 40)
    imagen[:, ANCHO // 2 :] = (40, 40, 200)
    return imagen


def config_de_corrida(**overrides):
    """Devuelve la configuración real del proyecto ajustada a una corrida mínima y sin procesos aparte."""
    config = cargar_config(str(RUTA_CONFIG), {})
    config.update(
        {
            "gene_count": 6,
            "population_size": 6,
            "selected_count": 4,
            "max_genes_to_mutate": 3,
            "max_generations": 4,
            "fitness_cutoff": 1.0,
            "stale_content_generation_cutoff": 100,
            "stale_content_epsilon": 0.0,
            "sesgo_color_inicial": False,
            "workers": 1,
            "random_seed": 12345,
        }
    )
    config.update(overrides)
    return config


def correr(config):
    """Corre el motor sobre la imagen de prueba, sin tocar el disco."""
    registro, _ = ejecutar_motor(
        config,
        objetivo=objetivo_de_prueba(),
        ancho=ANCHO,
        alto=ALTO,
        recursos={},
    )
    return registro


def metricas(registro):
    """Devuelve las métricas de todas las generaciones, sin los tiempos, que no son deterministas."""
    return [
        (
            generacion.generacion,
            generacion.fitness_maximo,
            generacion.fitness_minimo,
            generacion.fitness_promedio,
            generacion.diversidad,
        )
        for generacion in registro.historial
    ]


def test_dos_corridas_con_la_misma_semilla_dan_las_mismas_metricas():
    """Verifica la reproducibilidad de la corrida entera: sin esto ninguna comparación entre métodos significa nada."""
    una = correr(config_de_corrida())
    otra = correr(config_de_corrida())

    assert metricas(una) == metricas(otra)
    assert una.motivo_fin == otra.motivo_fin


def test_dos_corridas_con_la_misma_semilla_dan_el_mismo_mejor_genotipo():
    """Verifica que la reproducibilidad llegue hasta los parámetros del mejor individuo."""
    una = correr(config_de_corrida())
    otra = correr(config_de_corrida())

    assert np.array_equal(
        una.mejor_historico.vector_parametros(),
        otra.mejor_historico.vector_parametros(),
    )


def test_dos_semillas_distintas_dan_resultados_distintos():
    """Verifica que la semilla realmente mande: si no, la reproducibilidad sería un espejismo."""
    una = correr(config_de_corrida(random_seed=1))
    otra = correr(config_de_corrida(random_seed=2))

    assert metricas(una) != metricas(otra)


def test_la_corrida_termina_por_generaciones_agotadas():
    """Verifica el criterio de corte por cantidad de generaciones y lo que queda registrado."""
    registro = correr(config_de_corrida(max_generations=3))

    assert registro.motivo_fin == "max_generations"
    assert registro.cantidad_generaciones == 4
    assert [generacion.generacion for generacion in registro.historial] == [0, 1, 2, 3]


def test_la_corrida_termina_por_fitness_alcanzado():
    """Verifica que el corte por aptitud se evalúe antes que el de generaciones."""
    registro = correr(config_de_corrida(fitness_cutoff=0.0))

    assert registro.motivo_fin == "fitness_cutoff"
    assert registro.cantidad_generaciones == 1


def test_la_corrida_termina_por_estancamiento():
    """Verifica que el motor corte cuando el mejor deja de mejorar, sin agotar las generaciones."""
    registro = correr(
        config_de_corrida(
            max_generations=50,
            stale_content_generation_cutoff=2,
            stale_content_epsilon=1.0,
        )
    )

    assert registro.motivo_fin == "stale_content_generation_cutoff"
    assert registro.cantidad_generaciones == 3


def test_el_registro_guarda_la_configuracion_de_la_corrida():
    """Verifica que el resultado sea rastreable: el registro conserva con qué configuración se produjo."""
    config = config_de_corrida()
    registro = correr(config)

    assert registro.config["random_seed"] == config["random_seed"]
    assert registro.config["population_size"] == config["population_size"]
    assert registro.fitness_final == registro.historial[-1].fitness_maximo
