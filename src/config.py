"""Carga, valida y normaliza la configuración de una corrida."""

import json
from pathlib import Path

CAMPOS = (
    "gene_count",
    "file_input",
    "gene_type",
    "overlay_source",
    "background_color",
    "output_resolution_mult",
    "seleccion",
    "cruza",
    "mutacion",
    "supervivencia",
    "population_size",
    "selected_count",
    "tournament_size",
    "tournament_threshold",
    "temperature",
    "uniform_crossover_P",
    "extra_gene_Pm",
    "intra_gene_Pm",
    "max_genes_to_mutate",
    "max_coord_delta",
    "max_color_delta",
    "max_rotation_delta",
    "max_radius_delta",
    "max_coord_overflow",
    "max_generations",
    "fitness_cutoff",
    "stale_content_generation_cutoff",
    "stale_content_epsilon",
    "sesgo_color_inicial",
    "tipo_sesgo_color",
    "save_best",
    "best_resolution_multiplier",
    "gif_gen_interval",
    "save_every_n_generations",
    "random_seed",
)

TIPOS_DE_FIGURA = ("triangle", "quad", "pentagon", "oval", "png")

METODOS_DE_SELECCION = (
    "elite",
    "ruleta",
    "universal",
    "boltzmann",
    "torneo_deterministico",
    "torneo_probabilistico",
    "ranking",
)

METODOS_DE_CRUZA = ("un_punto", "dos_puntos", "uniforme", "anular")

METODOS_DE_MUTACION = ("gen", "multigen", "uniforme", "no_uniforme")

ESTRATEGIAS_DE_SUPERVIVENCIA = ("aditiva", "exclusiva")

TIPOS_DE_SESGO_COLOR = ("bounding_box", "exact_match")

ENTEROS_POSITIVOS = (
    "gene_count",
    "population_size",
    "selected_count",
    "tournament_size",
    "max_genes_to_mutate",
    "max_generations",
    "stale_content_generation_cutoff",
    "gif_gen_interval",
)

ENTEROS_NO_NEGATIVOS = ("save_every_n_generations",)

PROBABILIDADES = (
    "uniform_crossover_P",
    "extra_gene_Pm",
    "intra_gene_Pm",
    "fitness_cutoff",
)

POSITIVOS_ESTRICTOS = (
    "temperature",
    "output_resolution_mult",
    "best_resolution_multiplier",
)

NO_NEGATIVOS = (
    "max_coord_delta",
    "max_color_delta",
    "max_rotation_delta",
    "max_radius_delta",
    "max_coord_overflow",
    "stale_content_epsilon",
)

PATHS = ("file_input", "overlay_source")


class ErrorDeConfiguracion(Exception):
    """Configuración inexistente, incompleta, mal tipada o fuera de rango."""


def cargar_config(path_config, overrides):
    """Lee el archivo de configuración, aplica los overrides en texto, valida y devuelve el resultado."""
    config = _leer_archivo(path_config)
    for nombre, texto in overrides.items():
        if nombre not in config:
            raise ErrorDeConfiguracion(
                f"override desconocido: '{nombre}'. "
                f"Los campos válidos son: {', '.join(sorted(config))}"
            )
        config[nombre] = _convertir(nombre, texto, config[nombre])
    _validar(config)
    return config


def _leer_archivo(path_config):
    """Devuelve el contenido del archivo de configuración sin las claves de notas."""
    ruta = Path(path_config)
    try:
        contenido = ruta.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise ErrorDeConfiguracion(
            f"no existe el archivo de configuración: {ruta}"
        ) from None
    except OSError as error:
        raise ErrorDeConfiguracion(
            f"no se pudo leer el archivo de configuración {ruta}: {error}"
        ) from None
    try:
        crudo = json.loads(contenido)
    except json.JSONDecodeError as error:
        raise ErrorDeConfiguracion(
            f"el archivo de configuración {ruta} no es JSON válido: {error}"
        ) from None
    if not isinstance(crudo, dict):
        raise ErrorDeConfiguracion(
            f"el archivo de configuración {ruta} tiene que ser un objeto JSON"
        )
    return {
        nombre: valor
        for nombre, valor in crudo.items()
        if not nombre.startswith("_")
    }


def _convertir(nombre, texto, valor_base):
    """Convierte un override en texto al tipo que ese campo tiene en el archivo base."""
    if isinstance(valor_base, bool):
        normalizado = texto.strip().lower()
        if normalizado not in ("true", "false"):
            raise ErrorDeConfiguracion(
                f"'{nombre}' es booleano y solo acepta 'true' o 'false', "
                f"se recibió '{texto}'"
            )
        return normalizado == "true"
    if isinstance(valor_base, (list, dict)):
        try:
            return json.loads(texto)
        except json.JSONDecodeError:
            raise ErrorDeConfiguracion(
                f"'{nombre}' se interpreta como JSON y '{texto}' no lo es"
            ) from None
    if isinstance(valor_base, str):
        return texto
    try:
        return type(valor_base)(texto)
    except (TypeError, ValueError):
        raise ErrorDeConfiguracion(
            f"'{nombre}' es de tipo {type(valor_base).__name__} y no se puede "
            f"convertir '{texto}'"
        ) from None


def _validar(config):
    """Corta con ErrorDeConfiguracion ante el primer campo que no cumple su condición."""
    _validar_campos_presentes(config)

    for nombre in ENTEROS_POSITIVOS:
        _exigir_entero(config, nombre)
        if config[nombre] < 1:
            raise ErrorDeConfiguracion(
                f"'{nombre}' tiene que ser mayor o igual a 1, es {config[nombre]}"
            )

    for nombre in ENTEROS_NO_NEGATIVOS:
        _exigir_entero(config, nombre)
        if config[nombre] < 0:
            raise ErrorDeConfiguracion(
                f"'{nombre}' tiene que ser mayor o igual a 0, es {config[nombre]}"
            )

    if config["selected_count"] % 2 != 0:
        raise ErrorDeConfiguracion(
            f"'selected_count' tiene que ser par porque los padres se cruzan de "
            f"a pares, es {config['selected_count']}"
        )
    if config["tournament_size"] > config["population_size"]:
        raise ErrorDeConfiguracion(
            f"'tournament_size' tiene que ser menor o igual que "
            f"'population_size' ({config['population_size']}), es "
            f"{config['tournament_size']}"
        )
    if config["max_genes_to_mutate"] > config["gene_count"]:
        raise ErrorDeConfiguracion(
            f"'max_genes_to_mutate' tiene que ser menor o igual que "
            f"'gene_count' ({config['gene_count']}), es "
            f"{config['max_genes_to_mutate']}"
        )

    _exigir_rango(config, "tournament_threshold", 0.5, 1.0)
    for nombre in PROBABILIDADES:
        _exigir_rango(config, nombre, 0.0, 1.0)

    for nombre in POSITIVOS_ESTRICTOS:
        _exigir_numero(config, nombre)
        if config[nombre] <= 0:
            raise ErrorDeConfiguracion(
                f"'{nombre}' tiene que ser mayor que 0, es {config[nombre]}"
            )

    for nombre in NO_NEGATIVOS:
        _exigir_numero(config, nombre)
        if config[nombre] < 0:
            raise ErrorDeConfiguracion(
                f"'{nombre}' tiene que ser mayor o igual a 0, es {config[nombre]}"
            )

    _exigir_opcion(config, "gene_type", TIPOS_DE_FIGURA)
    _exigir_opcion(config, "seleccion", METODOS_DE_SELECCION)
    _exigir_opcion(config, "cruza", METODOS_DE_CRUZA)
    _exigir_opcion(config, "mutacion", METODOS_DE_MUTACION)
    _exigir_opcion(config, "supervivencia", ESTRATEGIAS_DE_SUPERVIVENCIA)
    _exigir_opcion(config, "tipo_sesgo_color", TIPOS_DE_SESGO_COLOR)

    _validar_color_de_fondo(config)

    for nombre in PATHS:
        if not isinstance(config[nombre], str) or not config[nombre].strip():
            raise ErrorDeConfiguracion(
                f"'{nombre}' tiene que ser un path no vacío, es {config[nombre]!r}"
            )

    if not isinstance(config["sesgo_color_inicial"], bool):
        raise ErrorDeConfiguracion(
            f"'sesgo_color_inicial' tiene que ser booleano, es "
            f"{config['sesgo_color_inicial']!r}"
        )

    if not isinstance(config["save_best"], bool):
        raise ErrorDeConfiguracion(
            f"'save_best' tiene que ser booleano, es "
            f"{config['save_best']!r}"
        )

    if isinstance(config["random_seed"], str):
        try:
            config["random_seed"] = int(config["random_seed"])
        except ValueError:
            import hashlib

            config["random_seed"] = int.from_bytes(
                hashlib.sha256(config["random_seed"].encode("utf-8")).digest()[:4],
                "big",
            )
    else:
        _exigir_entero(config, "random_seed")


def _validar_campos_presentes(config):
    """Exige que estén todos los campos de CAMPOS y ninguno más."""
    faltantes = [nombre for nombre in CAMPOS if nombre not in config]
    if faltantes:
        raise ErrorDeConfiguracion(
            f"faltan campos en la configuración: {', '.join(faltantes)}"
        )
    sobrantes = [nombre for nombre in config if nombre not in CAMPOS]
    if sobrantes:
        raise ErrorDeConfiguracion(
            f"campos desconocidos en la configuración: {', '.join(sobrantes)}"
        )


def _validar_color_de_fondo(config):
    """Exige que background_color sean cuatro enteros entre 0 y 255."""
    color = config["background_color"]
    if not isinstance(color, list) or len(color) != 4:
        raise ErrorDeConfiguracion(
            f"'background_color' tiene que ser una lista de cuatro enteros, es "
            f"{color!r}"
        )
    for canal in color:
        if isinstance(canal, bool) or not isinstance(canal, int):
            raise ErrorDeConfiguracion(
                f"cada canal de 'background_color' tiene que ser un entero, se "
                f"recibió {canal!r}"
            )
        if not 0 <= canal <= 255:
            raise ErrorDeConfiguracion(
                f"cada canal de 'background_color' tiene que estar entre 0 y "
                f"255, se recibió {canal}"
            )


def _exigir_entero(config, nombre):
    """Exige que el campo sea un entero y no un booleano."""
    valor = config[nombre]
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise ErrorDeConfiguracion(
            f"'{nombre}' tiene que ser un entero, es {valor!r}"
        )


def _exigir_numero(config, nombre):
    """Exige que el campo sea un número y no un booleano."""
    valor = config[nombre]
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ErrorDeConfiguracion(
            f"'{nombre}' tiene que ser un número, es {valor!r}"
        )


def _exigir_rango(config, nombre, minimo, maximo):
    """Exige que el campo sea un número dentro del intervalo cerrado dado."""
    _exigir_numero(config, nombre)
    if not minimo <= config[nombre] <= maximo:
        raise ErrorDeConfiguracion(
            f"'{nombre}' tiene que estar entre {minimo} y {maximo}, es "
            f"{config[nombre]}"
        )


def _exigir_opcion(config, nombre, opciones):
    """Exige que el campo sea uno de los valores permitidos."""
    if config[nombre] not in opciones:
        raise ErrorDeConfiguracion(
            f"'{nombre}' tiene que ser uno de: {', '.join(opciones)}; se "
            f"recibió {config[nombre]!r}"
        )
