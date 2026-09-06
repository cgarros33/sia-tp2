"""Lo que comparten los cuatro métodos de cruza: el largo del cromosoma y el armado de los hijos."""

from src.individuo import Individuo


class ErrorDeCruza(Exception):
    """Cruza pedida sobre padres de distinto largo."""


def largo_comun(padre, madre):
    """Devuelve el largo del cromosoma, exigiendo que los dos padres midan lo mismo."""
    if len(padre) != len(madre):
        raise ErrorDeCruza(
            f"los dos padres tienen que tener la misma cantidad de genes: "
            f"llegaron uno de {len(padre)} y otro de {len(madre)}"
        )
    return len(padre)


def hijos_por_mascara(padre, madre, mascara):
    """Devuelve los dos hijos complementarios que resultan de intercambiar los loci marcados."""
    # Copiar al padre entero en vez de rearmarlo gen por gen conserva su fitness
    # cacheado y ahorra un renderizado que ya se pagó.
    if not mascara.any():
        return padre.copiar(), madre.copiar()
    if mascara.all():
        return madre.copiar(), padre.copiar()

    primero, segundo = [], []
    for locus, intercambia in enumerate(mascara):
        origen, alterno = (madre, padre) if intercambia else (padre, madre)
        primero.append(origen.gen(locus).copiar())
        segundo.append(alterno.gen(locus).copiar())
    return Individuo(primero), Individuo(segundo)
