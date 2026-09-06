"""Motor de Algoritmo Genético: orquesta el ciclo de evolución y los criterios de parada."""

import time
import numpy as np

from src.cruza import anular, dos_puntos, un_punto, uniforme as cruza_uniforme
from src.fitness import calcular_fitness
from src.inicializacion import inicializar_poblacion
from src.mutacion import gen, multigen, no_uniforme, uniforme as mutacion_uniforme
from src.registro import RegistroCorrida
from src.renderizador import cargar_objetivo, cargar_recursos, renderizar
from src.seleccion import (
    boltzmann,
    elite,
    ranking,
    ruleta,
    torneo_deterministico,
    torneo_probabilistico,
    universal,
)
from src.supervivencia import aditiva, exclusiva

SELECCIONES = {
    "elite": elite.seleccionar,
    "ruleta": ruleta.seleccionar,
    "universal": universal.seleccionar,
    "boltzmann": boltzmann.seleccionar,
    "torneo_deterministico": torneo_deterministico.seleccionar,
    "torneo_probabilistico": torneo_probabilistico.seleccionar,
    "ranking": ranking.seleccionar,
}

CRUZAS = {
    "un_punto": un_punto.cruzar,
    "dos_puntos": dos_puntos.cruzar,
    "uniforme": cruza_uniforme.cruzar,
    "anular": anular.cruzar,
}

MUTACIONES = {
    "gen": gen.mutar,
    "multigen": multigen.mutar,
    "uniforme": mutacion_uniforme.mutar,
    "no_uniforme": no_uniforme.mutar,
}

SUPERVIVENCIAS = {
    "aditiva": aditiva.sobrevivientes,
    "exclusiva": exclusiva.sobrevivientes,
}


def ejecutar_motor(
    config,
    save_all=False,
    callback_generacion=None,
    objetivo=None,
    ancho=None,
    alto=None,
    recursos=None,
):
    """Ejecuta el algoritmo genético hasta cumplir un criterio de parada y devuelve el registro y mejor individuo."""
    if objetivo is None or ancho is None or alto is None:
        objetivo, ancho, alto = cargar_objetivo(config)
    if recursos is None:
        recursos = cargar_recursos(config)

    azar = np.random.default_rng(config["random_seed"])
    evaluador = lambda genes: calcular_fitness(
        renderizar(genes, ancho, alto, config, recursos), objetivo
    )

    seleccionar = SELECCIONES[config["seleccion"]]
    cruzar = CRUZAS[config["cruza"]]
    mutar = MUTACIONES[config["mutacion"]]
    sobrevivir = SUPERVIVENCIAS[config["supervivencia"]]

    registro = RegistroCorrida(config, save_all=save_all)
    registro.iniciar()

    poblacion = inicializar_poblacion(config, objetivo, ancho, alto, azar)
    poblacion.evaluar(evaluador)

    mejor_fitness_historico = None
    generaciones_sin_mejora = 0

    try:
        while True:
            t_inicio = time.perf_counter()
            fit_max = poblacion.fitness_maximo
            fit_min = poblacion.fitness_minimo
            fit_prom = poblacion.fitness_promedio
            diversidad = poblacion.diversidad()
            mejor = poblacion.mejor()
            t_generacion = time.perf_counter() - t_inicio

            registro.registrar_generacion(
                poblacion.generacion,
                fit_max,
                fit_min,
                fit_prom,
                diversidad,
                mejor,
                t_generacion,
                poblacion.individuos,
            )

            if callback_generacion is not None:
                callback_generacion(poblacion, registro)

            if fit_max >= config["fitness_cutoff"]:
                registro.finalizar("fitness_cutoff")
                break

            if mejor_fitness_historico is None:
                mejor_fitness_historico = fit_max
            elif fit_max > mejor_fitness_historico + config["stale_content_epsilon"]:
                mejor_fitness_historico = fit_max
                generaciones_sin_mejora = 0
            else:
                generaciones_sin_mejora += 1
                if generaciones_sin_mejora >= config["stale_content_generation_cutoff"]:
                    registro.finalizar("stale_content_generation_cutoff")
                    break

            if poblacion.generacion >= config["max_generations"]:
                registro.finalizar("max_generations")
                break

            padres = list(
                seleccionar(poblacion.individuos, config["selected_count"], azar, config)
            )
            azar.shuffle(padres)

            hijos = []
            for indice in range(0, len(padres), 2):
                hijo1, hijo2 = cruzar(padres[indice], padres[indice + 1], azar, config)
                hijos.append(hijo1)
                hijos.append(hijo2)

            for hijo in hijos:
                mutar(hijo, azar, config, ancho, alto)
                hijo.fitness(evaluador)

            sobrevivientes = sobrevivir(
                poblacion.individuos,
                hijos,
                config["population_size"],
                seleccionar,
                azar,
                config,
            )

            poblacion = poblacion.siguiente(sobrevivientes)
            poblacion.evaluar(evaluador)
    except KeyboardInterrupt:
        registro.finalizar("interrupcion_usuario")

    return registro, registro.mejor_historico
