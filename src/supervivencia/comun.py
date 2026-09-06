"""Lo que comparten las dos estrategias de supervivencia: dejar la generación sin referencias repetidas."""


def sin_repetir_referencias(individuos):
    """Devuelve la lista con una copia de cada individuo que ya haya aparecido antes."""
    vistos = set()
    generacion = []
    for individuo in individuos:
        if id(individuo) in vistos:
            individuo = individuo.copiar()
        vistos.add(id(individuo))
        generacion.append(individuo)
    return generacion
