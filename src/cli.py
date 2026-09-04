"""Interpreta los argumentos de línea de comandos y los clasifica."""

CONFIG_PATH_POR_DEFECTO = "config/conf.json"
RESULT_PATH_POR_DEFECTO = "results"
IMG_PATH_POR_DEFECTO = "img"

FLAG_CONFIG_PATH = "--config-path"
FLAG_RESULT_PATH = "--result-path"
FLAG_IMG_PATH = "--img-path"
FLAG_SAVE_ALL = "--save-all"

FORMAS_ACEPTADAS = (
    f"{FLAG_CONFIG_PATH}=<path>, {FLAG_RESULT_PATH}=<path>, "
    f"{FLAG_IMG_PATH}=<path>, {FLAG_SAVE_ALL} y --<nombre_de_campo>=<valor>"
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
        if argumento == FLAG_SAVE_ALL:
            save_all = True
            continue

        nombre, separador, valor = argumento.partition("=")
        if not argumento.startswith("--") or not separador or nombre == "--":
            raise ErrorDeArgumentos(
                f"argumento no reconocido: '{argumento}'. Las formas aceptadas "
                f"son: {FORMAS_ACEPTADAS}"
            )

        if nombre == FLAG_SAVE_ALL:
            raise ErrorDeArgumentos(f"'{FLAG_SAVE_ALL}' no lleva valor")
        if nombre == FLAG_CONFIG_PATH:
            config_path = valor
        elif nombre == FLAG_RESULT_PATH:
            result_path = valor
        elif nombre == FLAG_IMG_PATH:
            img_path = valor
        elif "-" in nombre[2:]:
            raise ErrorDeArgumentos(
                f"'{nombre}' no es un flag estructural, y los overrides de "
                f"configuración se escriben con guión bajo: "
                f"--{nombre[2:].replace('-', '_')}={valor}"
            )
        else:
            overrides[nombre[2:]] = valor

    return config_path, result_path, img_path, save_all, overrides
