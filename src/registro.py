"""Registro de la corrida: acumula métricas, tiempos e historial de generaciones."""

import time


class RegistroGeneracion:
    """Métricas y estado de una generación particular."""

    __slots__ = (
        "generacion",
        "fitness_maximo",
        "fitness_minimo",
        "fitness_promedio",
        "diversidad",
        "mejor_individuo",
        "tiempo_generacion",
        "genomas",
    )

    def __init__(
        self,
        generacion,
        fitness_maximo,
        fitness_minimo,
        fitness_promedio,
        diversidad,
        mejor_individuo,
        tiempo_generacion,
        genomas=None,
    ):
        """Guarda las métricas calculadas de la generación y opcionalmente los genomas."""
        self.generacion = generacion
        self.fitness_maximo = fitness_maximo
        self.fitness_minimo = fitness_minimo
        self.fitness_promedio = fitness_promedio
        self.diversidad = diversidad
        self.mejor_individuo = mejor_individuo
        self.tiempo_generacion = tiempo_generacion
        self.genomas = genomas


class RegistroCorrida:
    """Historial completo de la ejecución del motor genético."""

    __slots__ = (
        "config",
        "save_all",
        "historial",
        "tiempo_inicio",
        "tiempo_fin",
        "motivo_fin",
        "mejor_historico",
    )

    def __init__(self, config, save_all=False):
        """Inicializa el registro para una corrida con su configuración y modo de guardado."""
        self.config = config
        self.save_all = save_all
        self.historial = []
        self.tiempo_inicio = None
        self.tiempo_fin = None
        self.motivo_fin = None
        self.mejor_historico = None

    def iniciar(self):
        """Registra el instante de inicio de la corrida."""
        self.tiempo_inicio = time.perf_counter()

    def registrar_generacion(
        self,
        generacion,
        fitness_maximo,
        fitness_minimo,
        fitness_promedio,
        diversidad,
        mejor_individuo,
        tiempo_generacion,
        individuos=None,
    ):
        """Agrega el registro de una generación y actualiza el mejor individuo histórico."""
        genomas = None
        if self.save_all and individuos is not None:
            genomas = tuple(ind.vector_parametros() for ind in individuos)

        registro = RegistroGeneracion(
            generacion=generacion,
            fitness_maximo=fitness_maximo,
            fitness_minimo=fitness_minimo,
            fitness_promedio=fitness_promedio,
            diversidad=diversidad,
            mejor_individuo=mejor_individuo,
            tiempo_generacion=tiempo_generacion,
            genomas=genomas,
        )
        self.historial.append(registro)

        if (
            self.mejor_historico is None
            or fitness_maximo > self.mejor_historico.fitness_cacheado
        ):
            self.mejor_historico = mejor_individuo.copiar()

    def finalizar(self, motivo_fin):
        """Registra el instante de finalización y el motivo de corte."""
        self.tiempo_fin = time.perf_counter()
        self.motivo_fin = motivo_fin

    @property
    def tiempo_total(self):
        """Devuelve la duración total de la corrida en segundos."""
        if self.tiempo_inicio is None:
            return 0.0
        fin = self.tiempo_fin if self.tiempo_fin is not None else time.perf_counter()
        return fin - self.tiempo_inicio

    @property
    def fitness_final(self):
        """Devuelve el mejor fitness alcanzado en la última generación registrada."""
        if not self.historial:
            return None
        return self.historial[-1].fitness_maximo

    @property
    def cantidad_generaciones(self):
        """Devuelve la cantidad de generaciones registradas."""
        return len(self.historial)
