"""Pruebas de las cinco figuras: dominio, recorte de la mutación, copias y dibujado."""

import numpy as np
import pytest
from PIL import Image

from src.figuras.cuadrilatero import Cuadrilatero
from src.figuras.familias import FiguraElipsoidal, Poligono
from src.figuras.imagen_png import CLAVE_OVERLAY, ImagenPng
from src.figuras.ovalo import Ovalo
from src.figuras.pentagono import Pentagono
from src.figuras.triangulo import Triangulo
from tests.helpers import config_test, generador_azar

FIGURAS = (Triangulo, Cuadrilatero, Pentagono, Ovalo, ImagenPng)

ANCHO = 100
ALTO = 100
CONFIG = config_test(max_radius_delta=10.0, max_rotation_delta=0.05, intra_gene_Pm=0.5)
CONFIG_TODO_MUTA = config_test(
    max_radius_delta=10.0, max_rotation_delta=0.05, intra_gene_Pm=1.0
)
COORD_MINIMA = -CONFIG["max_coord_overflow"]
COORD_MAXIMA = ANCHO + CONFIG["max_coord_overflow"]
# Proporción con la que el color de la figura se mezcla sobre el overlay en imagen_png.
FACTOR_DE_TINTE = 0.45


def overlay_de_prueba(color=(200, 210, 220, 255), lado=16):
    """Devuelve el diccionario de recursos con una imagen de overlay generada en memoria."""
    return {CLAVE_OVERLAY: Image.new("RGBA", (lado, lado), color)}


def parametros_fuera_de_rango(figura, rangos):
    """Devuelve los parámetros de la figura que se escaparon de su rango válido."""
    nombres = type(figura).nombres_parametros()
    return [
        (nombre, valor, minimo, maximo)
        for nombre, valor, (minimo, maximo) in zip(nombres, figura.parametros(), rangos)
        if not minimo <= valor <= maximo
    ]


@pytest.mark.parametrize("clase", FIGURAS)
def test_la_creacion_al_azar_respeta_el_dominio(clase):
    """Verifica que ninguna figura nazca con un parámetro fuera de su rango."""
    azar = generador_azar()
    rangos = clase.rangos(CONFIG, ANCHO, ALTO)

    fallas = []
    for _ in range(2000):
        figura = clase.aleatoria(azar, CONFIG, ANCHO, ALTO)
        fallas += parametros_fuera_de_rango(figura, rangos)

    assert fallas == []


@pytest.mark.parametrize("clase", FIGURAS)
def test_las_secuencias_son_coherentes(clase):
    """Verifica que parámetros, nombres y rangos tengan el mismo largo, que es lo que asume la diversidad."""
    figura = clase.aleatoria(generador_azar(), CONFIG, ANCHO, ALTO)

    cantidad = len(figura.parametros())
    assert cantidad == len(clase.nombres_parametros())
    assert cantidad == len(clase.rangos(CONFIG, ANCHO, ALTO))


@pytest.mark.parametrize("clase", FIGURAS)
def test_mutar_no_modifica_el_original(clase):
    """Verifica que mutar devuelva una figura nueva y deje intacta la que recibió."""
    azar = generador_azar()
    figura = clase.aleatoria(azar, CONFIG, ANCHO, ALTO)
    antes = figura.parametros()

    mutada = figura.mutar(azar, CONFIG_TODO_MUTA, ANCHO, ALTO)

    assert figura.parametros() == antes
    assert mutada is not figura


@pytest.mark.parametrize("clase", FIGURAS)
def test_la_copia_es_independiente(clase):
    """Verifica que mutar una copia no toque a la figura original."""
    azar = generador_azar()
    figura = clase.aleatoria(azar, CONFIG, ANCHO, ALTO)
    antes = figura.parametros()

    copia = figura.copiar()
    copia.mutar(azar, CONFIG_TODO_MUTA, ANCHO, ALTO)

    assert copia is not figura
    assert copia.parametros() == antes
    assert figura.parametros() == antes


@pytest.mark.parametrize("clase", FIGURAS)
def test_la_misma_semilla_da_las_mismas_figuras(clase):
    """Verifica la reproducibilidad: sin esto no se puede comparar dos métodos en la fase 12."""
    uno, otro = generador_azar(), generador_azar()

    for _ in range(50):
        una = clase.aleatoria(uno, CONFIG, ANCHO, ALTO)
        otra = clase.aleatoria(otro, CONFIG, ANCHO, ALTO)
        assert una.parametros() == otra.parametros()
        assert (
            una.mutar(uno, CONFIG, ANCHO, ALTO).parametros()
            == otra.mutar(otro, CONFIG, ANCHO, ALTO).parametros()
        )


@pytest.mark.parametrize("clase", FIGURAS)
def test_con_color_conserva_la_geometria_y_la_transparencia(clase):
    """Verifica que el sesgo de color inicial solo toque los tres canales de color."""
    figura = clase.aleatoria(generador_azar(), CONFIG, ANCHO, ALTO)
    tenida = figura.con_color(10, 20, 30)

    assert tenida is not figura
    assert tenida.parametros()[:-4] == figura.parametros()[:-4]
    assert tenida.parametros()[-4:] == (10, 20, 30, figura.parametros()[-1])


def test_dos_figuras_al_azar_no_comparten_estado():
    """Verifica que cada figura nazca con parámetros propios y no compartidos."""
    azar = generador_azar()
    figuras = [Triangulo.aleatoria(azar, CONFIG, ANCHO, ALTO) for _ in range(500)]
    parametros = [figura.parametros() for figura in figuras]

    assert len({id(figura) for figura in figuras}) == len(figuras)
    assert len({id(valores) for valores in parametros}) == len(figuras)
    assert len(set(parametros)) == len(figuras)


def test_el_recorte_aguanta_miles_de_mutaciones():
    """Verifica que ningún parámetro se escape del dominio por mucho que se mute."""
    azar = generador_azar()
    rangos = Triangulo.rangos(CONFIG_TODO_MUTA, ANCHO, ALTO)
    figura = Triangulo.aleatoria(azar, CONFIG_TODO_MUTA, ANCHO, ALTO)

    fallas = []
    for _ in range(2000):
        figura = figura.mutar(azar, CONFIG_TODO_MUTA, ANCHO, ALTO)
        fallas += parametros_fuera_de_rango(figura, rangos)

    assert fallas == []


def test_desde_el_extremo_la_coordenada_no_da_la_vuelta():
    """Verifica que una coordenada en el borde se quede en el borde o entre, pero nunca reaparezca del otro lado."""
    azar = generador_azar()
    delta = CONFIG_TODO_MUTA["max_coord_delta"]
    en_el_maximo = Triangulo((COORD_MAXIMA,) * 6, (10, 20, 30, 40))
    en_el_minimo = Triangulo((COORD_MINIMA,) * 6, (10, 20, 30, 40))

    se_movio = False
    for _ in range(500):
        desde_arriba = en_el_maximo.mutar(azar, CONFIG_TODO_MUTA, ANCHO, ALTO)
        desde_abajo = en_el_minimo.mutar(azar, CONFIG_TODO_MUTA, ANCHO, ALTO)

        for valor in desde_arriba.parametros()[:6]:
            assert COORD_MAXIMA - delta <= valor <= COORD_MAXIMA
            se_movio = se_movio or valor < COORD_MAXIMA
        for valor in desde_abajo.parametros()[:6]:
            assert COORD_MINIMA <= valor <= COORD_MINIMA + delta

    assert se_movio


def test_la_rotacion_envuelve_en_vez_de_recortarse():
    """Verifica que la rotación sea cíclica: pasarse de 1 reaparece cerca de 0, sin salirse del rango."""
    azar = generador_azar()
    cerca_de_una_vuelta = Ovalo((50.0, 50.0, 10.0, 10.0, 0.999), (10, 20, 30, 40))

    rotaciones = [
        cerca_de_una_vuelta.mutar(azar, CONFIG_TODO_MUTA, ANCHO, ALTO).parametros()[4]
        for _ in range(500)
    ]

    assert all(0.0 <= rotacion <= 1.0 for rotacion in rotaciones)
    assert any(rotacion < 0.05 for rotacion in rotaciones)


def test_los_radios_nunca_bajan_de_uno():
    """Verifica que la elipse no degenere a radio nulo, que rompe el dibujado."""
    azar = generador_azar()
    config = config_test(
        max_radius_delta=50.0, max_rotation_delta=0.05, intra_gene_Pm=1.0
    )
    figura = Ovalo((50.0, 50.0, 1.0, 1.0, 0.5), (10, 20, 30, 40))

    for _ in range(1000):
        figura = figura.mutar(azar, config, ANCHO, ALTO)
        radio_x, radio_y = figura.parametros()[2:4]
        assert radio_x >= 1.0 and radio_y >= 1.0
        assert max(radio_x, radio_y) <= max(ANCHO, ALTO) / 2


def test_el_centro_del_poligono_es_el_promedio_de_sus_vertices():
    """Verifica el centro que usa el sesgo de color inicial."""
    figura = Triangulo((0.0, 0.0, 30.0, 0.0, 0.0, 60.0), (1, 2, 3, 4))

    assert figura.centro() == (10.0, 20.0)


def test_el_centro_de_la_elipse_es_su_propio_centro():
    """Verifica que la familia elipsoidal devuelva el centro que ya tiene como parámetro."""
    figura = Ovalo((12.0, 34.0, 5.0, 6.0, 0.25), (1, 2, 3, 4))

    assert figura.centro() == (12.0, 34.0)


def test_el_triangulo_opaco_pinta_adentro_y_no_afuera():
    """Verifica el dibujado básico del polígono sobre el lienzo."""
    lienzo = Image.new("RGB", (100, 100), (255, 255, 255))

    Triangulo((10.0, 10.0, 90.0, 10.0, 50.0, 90.0), (255, 0, 0, 255)).dibujar(lienzo, {})

    assert lienzo.getpixel((50, 40)) == (255, 0, 0)
    assert lienzo.getpixel((2, 95)) == (255, 255, 255)


def test_el_triangulo_translucido_compone_con_el_fondo():
    """Verifica que la transparencia se mezcle en vez de pisar el píxel: adentro tiene que quedar rosado."""
    lienzo = Image.new("RGB", (100, 100), (255, 255, 255))

    Triangulo((10.0, 10.0, 90.0, 10.0, 50.0, 90.0), (255, 0, 0, 128)).dibujar(lienzo, {})

    rojo, verde, azul = lienzo.getpixel((50, 40))
    assert rojo == 255
    assert verde == azul
    assert 100 < verde < 160
    assert lienzo.getpixel((2, 95)) == (255, 255, 255)


def test_el_ovalo_rotado_no_deja_halo_oscuro():
    """Verifica que la capa auxiliar nazca del color de la figura: si naciera negra, el borde se ensuciaría."""
    lienzo = Image.new("RGB", (100, 100), (255, 255, 255))

    Ovalo((50.0, 50.0, 35.0, 12.0, 0.125), (255, 0, 0, 255)).dibujar(lienzo, {})

    canal_rojo = np.asarray(lienzo)[:, :, 0]
    assert set(np.unique(canal_rojo).tolist()) == {255}


def test_la_rotacion_del_ovalo_cambia_el_fenotipo():
    """Verifica que la rotación llegue al dibujado y no quede como un parámetro decorativo."""
    sin_rotar = Image.new("RGB", (100, 100), (255, 255, 255))
    rotado = Image.new("RGB", (100, 100), (255, 255, 255))

    Ovalo((50.0, 50.0, 40.0, 10.0, 0.0), (255, 0, 0, 255)).dibujar(sin_rotar, {})
    Ovalo((50.0, 50.0, 40.0, 10.0, 0.25), (255, 0, 0, 255)).dibujar(rotado, {})

    assert not np.array_equal(np.asarray(sin_rotar), np.asarray(rotado))
    assert rotado.getpixel((50, 20)) == (255, 0, 0)
    assert sin_rotar.getpixel((50, 20)) == (255, 255, 255)


def test_el_color_tine_el_png_como_filtro():
    """Verifica que el color de la figura se mezcle con el del overlay en la proporción del filtro."""
    lienzo = Image.new("RGB", (100, 100), (255, 255, 255))
    overlay = (200, 210, 220)
    tinte = (255, 0, 0)
    recursos = overlay_de_prueba(color=overlay + (255,))

    ImagenPng((50.0, 50.0, 20.0, 20.0, 0.0), tinte + (255,)).dibujar(lienzo, recursos)

    esperado = [
        canal * (1 - FACTOR_DE_TINTE) + color * FACTOR_DE_TINTE
        for canal, color in zip(overlay, tinte)
    ]
    assert lienzo.getpixel((50, 50)) == pytest.approx(esperado, abs=1)


def test_la_transparencia_de_la_figura_multiplica_a_la_del_png():
    """Verifica que un overlay opaco con la figura a media transparencia quede compuesto con el fondo."""
    lienzo = Image.new("RGB", (100, 100), (0, 0, 0))
    recursos = overlay_de_prueba(color=(200, 200, 200, 255))

    ImagenPng((50.0, 50.0, 20.0, 20.0, 0.0), (200, 200, 200, 128)).dibujar(
        lienzo, recursos
    )

    opaco = Image.new("RGB", (100, 100), (0, 0, 0))
    ImagenPng((50.0, 50.0, 20.0, 20.0, 0.0), (200, 200, 200, 255)).dibujar(
        opaco, recursos
    )

    medio = lienzo.getpixel((50, 50))[0]
    entero = opaco.getpixel((50, 50))[0]
    assert 0 < medio < entero
    assert medio == pytest.approx(entero / 2, abs=2)


def test_el_png_conserva_sus_zonas_transparentes():
    """Verifica que un overlay enteramente transparente no pinte nada sobre el lienzo."""
    lienzo = Image.new("RGB", (60, 60), (255, 255, 255))
    recursos = overlay_de_prueba(color=(10, 20, 30, 0))

    ImagenPng((30.0, 30.0, 15.0, 15.0, 0.0), (255, 0, 0, 255)).dibujar(lienzo, recursos)

    assert set(np.unique(np.asarray(lienzo)).tolist()) == {255}


def test_el_png_nunca_abre_un_archivo():
    """Verifica que la figura dibuje con lo que llega en los recursos y no lea el disco."""
    lienzo = Image.new("RGB", (40, 40), (255, 255, 255))
    figura = ImagenPng((20.0, 20.0, 8.0, 8.0, 0.0), (255, 255, 255, 255))

    with pytest.raises(KeyError):
        figura.dibujar(lienzo, {})


@pytest.mark.parametrize("familia", (Poligono, FiguraElipsoidal))
def test_las_familias_no_se_pueden_instanciar(familia):
    """Verifica que las clases de familia fallen de entrada y no más adelante con un error sin sentido."""
    with pytest.raises(TypeError):
        familia((0.0, 0.0, 1.0, 1.0, 2.0, 3.0), (1, 2, 3, 4))
