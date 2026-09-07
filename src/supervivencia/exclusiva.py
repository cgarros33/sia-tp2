"""Supervivencia exclusiva: la generación siguiente se arma con hijos en la medida de lo posible."""

from src.supervivencia.comun import sin_repetir_referencias


def sobrevivientes(actuales, hijos, cantidad, seleccionar, azar, config):
    """Se queda con los hijos y sólo completa con individuos de la generación actual si faltan."""
    if len(hijos) > cantidad:
        elegidos = seleccionar(list(hijos), cantidad, azar, config)
    else:
        elegidos = list(hijos)
        faltan = cantidad - len(elegidos)
        if faltan:
            elegidos += seleccionar(list(actuales), faltan, azar, config)
    return sin_repetir_referencias(elegidos)
