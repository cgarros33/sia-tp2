"""Interpreta los argumentos de línea de comandos y los clasifica."""

CONFIG_PATH_POR_DEFECTO = "config/conf.json"
RESULT_PATH_POR_DEFECTO = "results"
IMG_PATH_POR_DEFECTO = "img"

FLAGS_CONFIG_PATH = ("--config-path", "--config_path", "--config-file", "--config_file")
FLAGS_RESULT_PATH = ("--result-path", "--result_path")
FLAGS_IMG_PATH = ("--img-path", "--img_path")
FLAGS_SAVE_ALL = ("--save-all", "--save_all")

FORMAS_ACEPTADAS = (
    "--config-path=<path> (o --config_file), --result-path=<path>, "
    "--img-path=<path>, --save-all y --<nombre_de_campo>=<valor>"
)


class ErrorDeArgumentos(Exception):
    """Argumento de línea de comandos mal formado."""


def parsear_args(argumentos):
    """Separa los argumentos en los tres paths, el volcado completo y los overrides en texto."""
    config_path = CONFIG_PATH_POR_DEFECTO
    result_path = RESULT_PATH_POR_DEFECTO
    img_path = IMG_PATH_POR_DEFECTO
    save_all = False
    overrides = {}

    for argumento in argumentos:
        if argumento in FLAGS_SAVE_ALL:
            save_all = True
            continue

        nombre, separador, valor = argumento.partition("=")
        if not argumento.startswith("--") or not separador or nombre == "--":
            raise ErrorDeArgumentos(
                f"argumento no reconocido: '{argumento}'. Las formas aceptadas "
                f"son: {FORMAS_ACEPTADAS}"
            )

        if nombre in FLAGS_SAVE_ALL:
            raise ErrorDeArgumentos(f"'{nombre}' no lleva valor")
        if nombre in FLAGS_CONFIG_PATH:
            config_path = valor
        elif nombre in FLAGS_RESULT_PATH:
            result_path = valor
        elif nombre in FLAGS_IMG_PATH:
            img_path = valor
        else:
            clave = nombre[2:].replace("-", "_")
            overrides[clave] = valor

    return config_path, result_path, img_path, save_all, overrides
