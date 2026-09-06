"""Script central para ejecutar experimentos, benchmarks aislados y generar gráficos comparativos."""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src.config import cargar_config
from src.cruza import anular, dos_puntos, un_punto, uniforme as cruza_uniforme
from src.figuras.cuadrilatero import Cuadrilatero
from src.figuras.ovalo import Ovalo
from src.figuras.pentagono import Pentagono
from src.figuras.triangulo import Triangulo
from src.individuo import Individuo
from src.mutacion import gen, multigen, no_uniforme, uniforme as mutacion_uniforme
from src.poblacion import Poblacion
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

TABLA_SELECCIONES = {
    "elite": elite.seleccionar,
    "ruleta": ruleta.seleccionar,
    "universal": universal.seleccionar,
    "boltzmann": boltzmann.seleccionar,
    "torneo_deterministico": torneo_deterministico.seleccionar,
    "torneo_probabilistico": torneo_probabilistico.seleccionar,
    "ranking": ranking.seleccionar,
}

TABLA_CRUZAS = {
    "un_punto": un_punto.cruzar,
    "dos_puntos": dos_puntos.cruzar,
    "uniforme": cruza_uniforme.cruzar,
    "anular": anular.cruzar,
}

TABLA_MUTACIONES = {
    "gen": gen.mutar,
    "multigen": multigen.mutar,
    "uniforme": mutacion_uniforme.mutar,
    "no_uniforme": no_uniforme.mutar,
}

TABLA_SUPERVIVENCIAS = {
    "aditiva": aditiva.sobrevivientes,
    "exclusiva": exclusiva.sobrevivientes,
}

TABLA_FIGURAS = {
    "triangle": Triangulo,
    "quad": Cuadrilatero,
    "pentagon": Pentagono,
    "oval": Ovalo,
}


def parsear_argumentos_cli(args):
    """Interpreta flags de línea de comandos para filtrar la ejecución del análisis."""
    opciones = {
        "config": "analyze-conf.json",
        "experiment": None,
        "type": None,
        "output_dir": None,
        "random_seed": False,
        "dry_run": False,
    }
    for argumento in args:
        if argumento.startswith("--config="):
            opciones["config"] = argumento.partition("=")[2]
        elif argumento.startswith("--experiment="):
            opciones["experiment"] = argumento.partition("=")[2]
        elif argumento.startswith("--type="):
            opciones["type"] = argumento.partition("=")[2]
        elif argumento.startswith("--output-dir="):
            opciones["output_dir"] = argumento.partition("=")[2]
        elif argumento == "--random-seed":
            opciones["random_seed"] = True
        elif argumento == "--dry-run":
            opciones["dry_run"] = True
    return opciones


def cargar_configuracion_analisis(ruta_archivo):
    """Carga y valida el archivo JSON de configuración de análisis."""
    ruta = Path(ruta_archivo)
    if not ruta.exists():
        print(f"Error: no existe el archivo {ruta}", file=sys.stderr)
        sys.exit(1)
    with open(ruta, "r", encoding="utf-8") as archivo:
        return json.load(archivo)


def resolver_semilla(config_analisis, opciones_cli):
    """Determina la semilla pseudoaleatoria respetando la preferencia estocástica configurada."""
    if opciones_cli["random_seed"] or config_analisis.get("use_random_seed", False):
        return int(np.random.randint(1, 2_000_000_000))
    return int(config_analisis.get("default_seed", 33333333))


def configurar_estilo_graficos():
    """Aplica parámetros globales de matplotlib para obtener figuras sobrias y legibles."""
    plt.rcParams["font.sans-serif"] = "DejaVu Sans"
    plt.rcParams["axes.edgecolor"] = "#333333"
    plt.rcParams["axes.linewidth"] = 0.8
    plt.rcParams["grid.color"] = "#cccccc"
    plt.rcParams["grid.linestyle"] = "--"
    plt.rcParams["grid.linewidth"] = 0.5


def ejecutar_benchmark_seleccion(experimento, dir_salida, semilla, config_base):
    """Ejecuta una evaluación aislada de frecuencias de selección sobre una población fija."""
    iteraciones = experimento.get("iterations", 1000)
    poblacion_tamano = experimento.get("population_size", 100)
    seleccion_cant = experimento.get("selected_count", 20)
    azar = np.random.default_rng(semilla)

    fitnesses = [
        1e-4 + (i / poblacion_tamano) * (1e-3 - 1e-4)
        for i in range(poblacion_tamano)
    ]
    individuos = []
    for i, fit in enumerate(fitnesses):
        ind = Individuo([Triangulo((0.0, 0.0, 1.0, 1.0, 2.0, float(i)), (100, 100, 100, 255))])
        ind.fitness(lambda _, v=fit: v)
        individuos.append(ind)

    conteos = {}
    for variante in experimento["variants"]:
        var_id = variante["id"]
        cfg = dict(config_base)
        cfg.update(variante.get("overrides", {}))
        metodo = TABLA_SELECCIONES[cfg["seleccion"]]
        frecuencias = np.zeros(poblacion_tamano, dtype=int)
        for _ in range(iteraciones):
            elegidos = metodo(individuos, seleccion_cant, azar, cfg)
            for elegido in elegidos:
                idx = int(elegido.genes[0]._puntos[5])
                frecuencias[idx] += 1
        conteos[var_id] = {
            "nombre": variante["name"],
            "frecuencias": (frecuencias / (iteraciones * seleccion_cant)).tolist(),
        }

    csv_path = dir_salida / "frecuencias_seleccion.csv"
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("ranking," + ",".join(v["nombre"] for v in conteos.values()) + "\n")
        for rank in range(poblacion_tamano):
            fila = [str(rank)] + [f"{conteos[vid]['frecuencias'][rank]:.6f}" for vid in conteos]
            f.write(",".join(fila) + "\n")

    fig, ax = plt.subplots(figsize=(8, 5))
    for vid, datos in conteos.items():
        ax.plot(range(poblacion_tamano), datos["frecuencias"], label=datos["nombre"], linewidth=1.5)
    ax.set_title("Frecuencia de seleccion vs Ranking")
    ax.set_xlabel("Ranking del individuo (0 = peor, 99 = mejor)")
    ax.set_ylabel("Frecuencia relativa de seleccion")
    ax.grid(True, alpha=0.3)
    ax.legend(frameon=True)
    fig.savefig(dir_salida / "frecuencia_seleccion.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    with open(dir_salida / "resumen.json", "w", encoding="utf-8") as f:
        json.dump(conteos, f, indent=2)


def ejecutar_benchmark_cruza(experimento, dir_salida, semilla, config_base):
    """Ejecuta una evaluación aislada de transferencia y disrupción de loci para métodos de cruza."""
    iteraciones = experimento.get("iterations", 1000)
    gene_count = experimento.get("gene_count", 100)
    azar = np.random.default_rng(semilla)

    p1 = Individuo([Triangulo((0.0, 0.0, 1.0, 1.0, 2.0, 0.0), (0, 0, 0, 255)) for _ in range(gene_count)])
    p2 = Individuo([Triangulo((0.0, 0.0, 1.0, 1.0, 2.0, 1.0), (255, 255, 255, 255)) for _ in range(gene_count)])

    resultados = {}
    frecuencias_locus = {}

    for variante in experimento["variants"]:
        var_id = variante["id"]
        cfg = dict(config_base)
        cfg.update(variante.get("overrides", {}))
        metodo = TABLA_CRUZAS[cfg["cruza"]]
        genes_transferidos = []
        locus_conteo = np.zeros(gene_count, dtype=int)

        for _ in range(iteraciones):
            h1, h2 = metodo(p1, p2, azar, cfg)
            mascara = [h1.genes[i]._puntos[5] == 1.0 for i in range(gene_count)]
            genes_transferidos.append(int(sum(mascara)))
            for idx, val in enumerate(mascara):
                if val:
                    locus_conteo[idx] += 1

        resultados[var_id] = {
            "nombre": variante["name"],
            "promedio_transferido": float(np.mean(genes_transferidos)),
            "desvio_transferido": float(np.std(genes_transferidos)),
            "datos": genes_transferidos,
        }
        frecuencias_locus[var_id] = (locus_conteo / iteraciones).tolist()

    csv_path = dir_salida / "intercambio_cruza.csv"
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("variante,promedio_transferido,desvio_transferido\n")
        for vid, res in resultados.items():
            f.write(f"{res['nombre']},{res['promedio_transferido']:.2f},{res['desvio_transferido']:.2f}\n")

    fig, ax = plt.subplots(figsize=(8, 5))
    nombres = [res["nombre"] for res in resultados.values()]
    datos = [res["datos"] for res in resultados.values()]
    ax.boxplot(datos, tick_labels=nombres, patch_artist=True, boxprops=dict(facecolor="#d0e1f9"))
    ax.set_title("Cantidad de genes intercambiados por cruza")
    ax.set_ylabel("Cantidad de genes (de 100)")
    ax.grid(True, alpha=0.3)
    fig.savefig(dir_salida / "genes_intercambiados.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    for vid, vals in frecuencias_locus.items():
        ax.plot(range(gene_count), vals, label=resultados[vid]["nombre"], linewidth=1.5)
    ax.set_title("Frecuencia de intercambio por locus")
    ax.set_xlabel("Posicion del locus (0 a 99)")
    ax.set_ylabel("Probabilidad de intercambio")
    ax.grid(True, alpha=0.3)
    ax.legend(frameon=True)
    fig.savefig(dir_salida / "frecuencia_locus.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    resumen_json = {
        vid: {
            "nombre": res["nombre"],
            "promedio": res["promedio_transferido"],
            "desvio": res["desvio_transferido"],
        }
        for vid, res in resultados.items()
    }
    with open(dir_salida / "resumen.json", "w", encoding="utf-8") as f:
        json.dump(resumen_json, f, indent=2)


def ejecutar_benchmark_mutacion(experimento, dir_salida, semilla, config_base):
    """Ejecuta una evaluación aislada de la cantidad de genes alterados por método de mutación."""
    iteraciones = experimento.get("iterations", 1000)
    gene_count = experimento.get("gene_count", 100)
    azar = np.random.default_rng(semilla)

    resultados = {}
    for variante in experimento["variants"]:
        var_id = variante["id"]
        cfg = dict(config_base)
        cfg.update(variante.get("overrides", {}))
        cfg["gene_count"] = gene_count
        metodo = TABLA_MUTACIONES[cfg["mutacion"]]
        mutados_lista = []

        for _ in range(iteraciones):
            original = Individuo([
                Triangulo.aleatoria(azar, cfg, 100, 100) for _ in range(gene_count)
            ])
            copia = original.copiar()
            metodo(copia, azar, cfg, 100, 100)
            cant_mutados = sum(
                1 for a, b in zip(original.genes, copia.genes)
                if a.parametros() != b.parametros()
            )
            mutados_lista.append(cant_mutados)

        resultados[var_id] = {
            "nombre": variante["name"],
            "promedio_mutados": float(np.mean(mutados_lista)),
            "desvio_mutados": float(np.std(mutados_lista)),
            "maximo_mutados": int(np.max(mutados_lista)),
            "datos": mutados_lista,
        }

    csv_path = dir_salida / "genes_mutados.csv"
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("variante,promedio_mutados,desvio_mutados,maximo_mutados\n")
        for vid, res in resultados.items():
            f.write(f"{res['nombre']},{res['promedio_mutados']:.2f},{res['desvio_mutados']:.2f},{res['maximo_mutados']}\n")

    fig, ax = plt.subplots(figsize=(8, 5))
    nombres = [res["nombre"] for res in resultados.values()]
    promedios = np.array([res["promedio_mutados"] for res in resultados.values()])
    desvios = np.array([res["desvio_mutados"] for res in resultados.values()])
    desvios_inferiores = np.minimum(promedios, desvios)
    desvios_superiores = np.minimum(gene_count - promedios, desvios)
    x = np.arange(len(nombres))
    ax.bar(
        x,
        promedios,
        yerr=[desvios_inferiores, desvios_superiores],
        capsize=4,
        color="#4b86b4",
        edgecolor="#2a4d69",
    )
    ax.set_xticks(x)
    ax.set_xticklabels(nombres, rotation=15, ha="right")
    ax.set_title("Cantidad promedio de genes mutados")
    ax.set_ylabel("Genes mutados (de 100)")
    ax.set_ylim(bottom=0)
    ax.grid(True, alpha=0.3, axis="y")
    fig.savefig(dir_salida / "genes_mutados.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    resumen_json = {
        vid: {
            "nombre": res["nombre"],
            "promedio": res["promedio_mutados"],
            "desvio": res["desvio_mutados"],
            "maximo": res["maximo_mutados"],
        }
        for vid, res in resultados.items()
    }
    with open(dir_salida / "resumen.json", "w", encoding="utf-8") as f:
        json.dump(resumen_json, f, indent=2)


def ejecutar_benchmark_supervivencia(experimento, dir_salida, semilla, config_base):
    """Evalúa de forma aislada la tasa de preservación de padres bajo distintas supervivencias."""
    iteraciones = experimento.get("iterations", 100)
    poblacion_tamano = experimento.get("population_size", 100)
    azar = np.random.default_rng(semilla)

    resultados = {}
    for variante in experimento["variants"]:
        var_id = variante["id"]
        cfg = dict(config_base)
        cfg.update(variante.get("overrides", {}))
        k = cfg.get("selected_count", 20)
        metodo = TABLA_SUPERVIVENCIAS[cfg["supervivencia"]]
        metodo_sel = TABLA_SELECCIONES[cfg.get("seleccion", "torneo_deterministico")]

        padres_sobrevivientes = []
        for _ in range(iteraciones):
            actuales = [
                Individuo([Triangulo((0.0, 0.0, 1.0, 1.0, 2.0, 0.0), (0, 0, 0, 255))])
                for _ in range(poblacion_tamano)
            ]
            for idx, ind in enumerate(actuales):
                fit = 0.0001 + (idx / poblacion_tamano) * 0.0005
                ind.fitness(lambda _, v=fit: v)

            hijos = [
                Individuo([Triangulo((0.0, 0.0, 1.0, 1.0, 2.0, 1.0), (255, 255, 255, 255))])
                for _ in range(k)
            ]
            for idx, ind in enumerate(hijos):
                fit = 0.0001 + (idx / k) * 0.0006
                ind.fitness(lambda _, v=fit: v)

            sobrevivientes = metodo(
                actuales, hijos, poblacion_tamano, metodo_sel, azar, cfg
            )
            conteo_padres = sum(1 for s in sobrevivientes if s.genes[0]._puntos[5] == 0.0)
            padres_sobrevivientes.append(conteo_padres)

        resultados[var_id] = {
            "nombre": variante["name"],
            "promedio_padres": float(np.mean(padres_sobrevivientes)),
            "desvio_padres": float(np.std(padres_sobrevivientes)),
            "datos": padres_sobrevivientes,
        }

    csv_path = dir_salida / "supervivencia.csv"
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("variante,promedio_padres,desvio_padres\n")
        for vid, res in resultados.items():
            f.write(f"{res['nombre']},{res['promedio_padres']:.2f},{res['desvio_padres']:.2f}\n")

    fig, ax = plt.subplots(figsize=(8, 5))
    nombres = [res["nombre"] for res in resultados.values()]
    promedios = [res["promedio_padres"] for res in resultados.values()]
    x = np.arange(len(nombres))
    ax.bar(x, promedios, color="#57bc90", edgecolor="#015249")
    ax.set_xticks(x)
    ax.set_xticklabels(nombres, rotation=15, ha="right")
    ax.set_title("Padres sobrevivientes en la nueva generacion")
    ax.set_ylabel("Cantidad de padres (de 100)")
    ax.set_ylim(bottom=0)
    ax.grid(True, alpha=0.3, axis="y")
    fig.savefig(dir_salida / "supervivencia_padres.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    resumen_json = {
        vid: {
            "nombre": res["nombre"],
            "promedio_padres": res["promedio_padres"],
            "desvio_padres": res["desvio_padres"],
        }
        for vid, res in resultados.items()
    }
    with open(dir_salida / "resumen.json", "w", encoding="utf-8") as f:
        json.dump(resumen_json, f, indent=2)


def ejecutar_benchmark_render(experimento, dir_salida, semilla, config_base):
    """Mide de forma aislada el tiempo de renderizado de 100 figuras de cada tipo."""
    iteraciones = experimento.get("iterations", 50)
    gene_count = experimento.get("gene_count", 100)
    azar = np.random.default_rng(semilla)

    ancho, alto = 150, 150
    recursos = cargar_recursos(config_base)

    resultados = {}
    for variante in experimento["variants"]:
        var_id = variante["id"]
        cfg = dict(config_base)
        cfg.update(variante.get("overrides", {}))
        tipo_figura = cfg["gene_type"]
        clase_figura = TABLA_FIGURAS[tipo_figura]

        figuras = [
            clase_figura.aleatoria(azar, cfg, ancho, alto) for _ in range(gene_count)
        ]

        renderizar(figuras, ancho, alto, cfg, recursos)

        tiempos = []
        for _ in range(iteraciones):
            t0 = time.perf_counter()
            renderizar(figuras, ancho, alto, cfg, recursos)
            tiempos.append((time.perf_counter() - t0) * 1000.0)

        resultados[var_id] = {
            "nombre": variante["name"],
            "tiempo_medio_ms": float(np.mean(tiempos)),
            "desvio_ms": float(np.std(tiempos)),
            "fps": float(1000.0 / np.mean(tiempos)) if np.mean(tiempos) > 0 else 0.0,
        }

    csv_path = dir_salida / "tiempo_render.csv"
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("figura,tiempo_medio_ms,desvio_ms,fps\n")
        for vid, res in resultados.items():
            f.write(f"{res['nombre']},{res['tiempo_medio_ms']:.3f},{res['desvio_ms']:.3f},{res['fps']:.1f}\n")

    fig, ax = plt.subplots(figsize=(8, 5))
    nombres = [res["nombre"] for res in resultados.values()]
    medios = np.array([res["tiempo_medio_ms"] for res in resultados.values()])
    desvios = np.array([res["desvio_ms"] for res in resultados.values()])
    desvios_inf = np.minimum(medios, desvios)
    x = np.arange(len(nombres))
    ax.bar(
        x,
        medios,
        yerr=[desvios_inf, desvios],
        capsize=4,
        color="#e0876a",
        edgecolor="#d9534f",
    )
    ax.set_xticks(x)
    ax.set_xticklabels(nombres)
    ax.set_title("Tiempo de renderizado para 100 figuras")
    ax.set_ylabel("Tiempo por frame (ms)")
    ax.set_ylim(bottom=0)
    ax.grid(True, alpha=0.3, axis="y")
    fig.savefig(dir_salida / "tiempo_render.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    with open(dir_salida / "resumen.json", "w", encoding="utf-8") as f:
        json.dump(resultados, f, indent=2)


def ejecutar_experimento_completo(experimento, dir_salida, semilla, config_base):
    """Ejecuta main.py de punta a punta para cada variante del experimento y genera gráficos comparativos."""
    base_overrides = experimento.get("base_overrides", {})
    variantes = experimento["variants"]
    outputs = experimento.get("outputs", {})

    resultados_variantes = {}

    for variante in variantes:
        var_id = variante["id"]
        var_nombre = variante["name"]
        var_overrides = variante.get("overrides", {})

        cfg = dict(config_base)
        cfg.update(base_overrides)
        cfg.update(var_overrides)
        cfg["random_seed"] = semilla

        dir_var_results = dir_salida / var_id
        dir_var_img = dir_var_results / "img"
        dir_var_results.mkdir(parents=True, exist_ok=True)
        dir_var_img.mkdir(parents=True, exist_ok=True)

        config_tmp_path = dir_var_results / "config.json"
        with open(config_tmp_path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)

        cmd = [
            sys.executable,
            "main.py",
            f"--config-path={config_tmp_path}",
            f"--result-path={dir_var_results}",
            f"--img-path={dir_var_img}",
        ]

        print(f"  -> Ejecutando variante: {var_nombre}...")
        proceso = subprocess.run(cmd, capture_output=True, text=True)
        if proceso.returncode != 0:
            print(f"Error al ejecutar variante {var_id}:\n{proceso.stderr}", file=sys.stderr)
            continue

        metricas_csv = dir_var_results / "metricas.csv"
        if metricas_csv.exists():
            datos_metricas = []
            with open(metricas_csv, "r", encoding="utf-8") as f:
                lineas = f.read().strip().split("\n")
                encabezados = lineas[0].split(",")
                for linea in lineas[1:]:
                    if linea.strip():
                        partes = linea.split(",")
                        datos_metricas.append({
                            encabezados[i]: float(partes[i]) for i in range(len(encabezados))
                        })
            resultados_variantes[var_id] = {
                "nombre": var_nombre,
                "metricas": datos_metricas,
                "salida_dir": dir_var_results,
            }

    if not resultados_variantes:
        print(f"Advertencia: no se recolectaron metricas para {experimento['id']}")
        return

    generar_graficos_completos(resultados_variantes, dir_salida, outputs)


def generar_graficos_completos(resultados_variantes, dir_salida, outputs):
    """Genera las curvas de convergencia, diversidad y rendimiento para un experimento evolutivo."""
    graficos_solicitados = outputs.get("plots", [])

    if "fitness_maximo" in graficos_solicitados:
        fig, ax = plt.subplots(figsize=(8, 5))
        for vid, datos in resultados_variantes.items():
            metricas = datos["metricas"]
            gens = [m["generacion"] for m in metricas]
            fit_max = [m["fitness_maximo"] for m in metricas]
            ax.plot(gens, fit_max, label=datos["nombre"], linewidth=1.5)
        ax.set_title("Fitness maximo vs Generacion")
        ax.set_xlabel("Generacion")
        ax.set_ylabel("Fitness maximo")
        ax.grid(True, alpha=0.3)
        ax.legend(frameon=True)
        fig.savefig(dir_salida / "fitness_maximo.png", dpi=300, bbox_inches="tight")
        plt.close(fig)

    if "fitness_promedio" in graficos_solicitados:
        fig, ax = plt.subplots(figsize=(8, 5))
        for vid, datos in resultados_variantes.items():
            metricas = datos["metricas"]
            gens = [m["generacion"] for m in metricas]
            fit_prom = [m["fitness_promedio"] for m in metricas]
            ax.plot(gens, fit_prom, label=datos["nombre"], linewidth=1.5)
        ax.set_title("Fitness promedio vs Generacion")
        ax.set_xlabel("Generacion")
        ax.set_ylabel("Fitness promedio")
        ax.grid(True, alpha=0.3)
        ax.legend(frameon=True)
        fig.savefig(dir_salida / "fitness_promedio.png", dpi=300, bbox_inches="tight")
        plt.close(fig)

    if "diversidad" in graficos_solicitados:
        fig, ax = plt.subplots(figsize=(8, 5))
        for vid, datos in resultados_variantes.items():
            metricas = datos["metricas"]
            gens = [m["generacion"] for m in metricas]
            div = [m["diversidad"] for m in metricas]
            ax.plot(gens, div, label=datos["nombre"], linewidth=1.5)
        ax.set_title("Diversidad genetica vs Generacion")
        ax.set_xlabel("Generacion")
        ax.set_ylabel("Diversidad normalizada")
        ax.grid(True, alpha=0.3)
        ax.legend(frameon=True)
        fig.savefig(dir_salida / "diversidad.png", dpi=300, bbox_inches="tight")
        plt.close(fig)

    if "tiempo_generacion" in graficos_solicitados:
        fig, ax = plt.subplots(figsize=(8, 5))
        for vid, datos in resultados_variantes.items():
            metricas = datos["metricas"]
            gens = [m["generacion"] for m in metricas]
            tiempos = [m["tiempo_generacion"] for m in metricas]
            ax.plot(gens, tiempos, label=datos["nombre"], linewidth=1.2, alpha=0.8)
        ax.set_title("Tiempo por generacion")
        ax.set_xlabel("Generacion")
        ax.set_ylabel("Tiempo (s)")
        ax.grid(True, alpha=0.3)
        ax.legend(frameon=True)
        fig.savefig(dir_salida / "tiempo_generacion.png", dpi=300, bbox_inches="tight")
        plt.close(fig)

    if "fitness_vs_tiempo" in graficos_solicitados:
        fig, ax = plt.subplots(figsize=(8, 5))
        for vid, datos in resultados_variantes.items():
            metricas = datos["metricas"]
            tiempos_acumulados = np.cumsum([m["tiempo_generacion"] for m in metricas])
            fit_max = [m["fitness_maximo"] for m in metricas]
            ax.plot(tiempos_acumulados, fit_max, label=datos["nombre"], linewidth=1.5)
        ax.set_title("Fitness maximo vs Tiempo acumulado")
        ax.set_xlabel("Tiempo transcurrido (s)")
        ax.set_ylabel("Fitness maximo")
        ax.grid(True, alpha=0.3)
        ax.legend(frameon=True)
        fig.savefig(dir_salida / "fitness_vs_tiempo.png", dpi=300, bbox_inches="tight")
        plt.close(fig)

    resumen_variantes = {}
    for vid, datos in resultados_variantes.items():
        metricas = datos["metricas"]
        if metricas:
            resumen_variantes[vid] = {
                "nombre": datos["nombre"],
                "generaciones": len(metricas),
                "fitness_final_max": metricas[-1]["fitness_maximo"],
                "fitness_final_prom": metricas[-1]["fitness_promedio"],
                "tiempo_total_s": sum(m["tiempo_generacion"] for m in metricas),
                "tiempo_prom_gen_s": np.mean([m["tiempo_generacion"] for m in metricas]),
            }

    with open(dir_salida / "resumen.json", "w", encoding="utf-8") as f:
        json.dump(resumen_variantes, f, indent=2)


def main():
    """Coordina la lectura de configuración, despacho de pruebas y generación de gráficos."""
    configurar_estilo_graficos()
    opciones = parsear_argumentos_cli(sys.argv[1:])
    config_analisis = cargar_configuracion_analisis(opciones["config"])

    dir_salida_base = Path(
        opciones["output_dir"] or config_analisis.get("output_dir", "results/analysis")
    )
    dir_salida_base.mkdir(parents=True, exist_ok=True)

    ruta_base = config_analisis.get("base_config_path", "config/conf.json")
    with open(ruta_base, "r", encoding="utf-8") as f:
        config_base = json.load(f)

    experimentos = config_analisis.get("experiments", [])
    semilla = resolver_semilla(config_analisis, opciones)

    print("============================================================")
    print("           SUITE DE EXPERIMENTACION Y ANALISIS AG           ")
    print("============================================================")
    print(f"Archivo de config:    {opciones['config']}")
    print(f"Directorio de salida: {dir_salida_base}")
    print(f"Semilla de analisis:  {semilla}")
    print(f"Experimentos totales: {len(experimentos)}")
    print("============================================================")

    for idx, exp in enumerate(experimentos, start=1):
        if not exp.get("enabled", True):
            continue
        if opciones["experiment"] and exp["id"] != opciones["experiment"]:
            continue
        if opciones["type"] and exp.get("type", "operator") != opciones["type"]:
            continue

        exp_id = exp["id"]
        exp_tipo = exp.get("type", "operator")
        dir_exp = dir_salida_base / exp_id
        dir_exp.mkdir(parents=True, exist_ok=True)

        print(f"\n[{idx}/{len(experimentos)}] Ejecutando: {exp.get('name', exp_id)} (tipo: {exp_tipo})")

        if opciones["dry_run"]:
            print("  [DRY-RUN] Omitiendo ejecucion real.")
            continue

        if exp_tipo == "operator":
            target = exp.get("operator_target", "seleccion")
            if target == "seleccion":
                ejecutar_benchmark_seleccion(exp, dir_exp, semilla, config_base)
            elif target == "cruza":
                ejecutar_benchmark_cruza(exp, dir_exp, semilla, config_base)
            elif target == "mutacion":
                ejecutar_benchmark_mutacion(exp, dir_exp, semilla, config_base)
            elif target == "supervivencia":
                ejecutar_benchmark_supervivencia(exp, dir_exp, semilla, config_base)
            elif target == "render":
                ejecutar_benchmark_render(exp, dir_exp, semilla, config_base)
            else:
                print(f"Error: target de operador desconocido '{target}'", file=sys.stderr)
        elif exp_tipo == "full":
            ejecutar_experimento_completo(exp, dir_exp, semilla, config_base)
        else:
            print(f"Error: tipo de experimento desconocido '{exp_tipo}'", file=sys.stderr)

    print("\n============================================================")
    print(f"Analisis completado. Resultados en: {dir_salida_base}")
    print("============================================================")


if __name__ == "__main__":
    main()
