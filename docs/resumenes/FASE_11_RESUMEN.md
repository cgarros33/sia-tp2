# Resumen Fase 11 — Verificación: suite de tests

---

## Qué hace esta fase

Antes de esta fase el proyecto se probaba corriéndolo: se lanzaba `main.py`, se
miraba el GIF y si la imagen se parecía a la original se daba por bueno. Eso
alcanza para ver que algo anda, pero no para ver que algo se rompió. Los errores
que importan en un algoritmo genético no lanzan ninguna excepción: si el caché de
aptitud no se invalida al mutar, el motor no falla, simplemente deja de converger
y nadie sabe por qué.

Ahora hay **145 pruebas automáticas que corren en menos de dos segundos** con un
solo comando. Cubren las cinco figuras, la aptitud, el individuo y su caché, la
población y su diversidad, los siete métodos de selección, los cuatro de cruza,
los cuatro de mutación, las dos estrategias de supervivencia y la corrida
completa de punta a punta.

Ninguna prueba toca el disco ni depende de una imagen del repositorio: las
imágenes objetivo y los overlays se generan en memoria. Ninguna depende del azar
sin fijar la semilla. Una prueba que a veces pasa y a veces no es peor que no
tenerla, porque enseña a ignorar los resultados.

---

## Archivos

| Archivo | Qué hace |
|---|---|
| `tests/__init__.py` | Vacío. Marca `tests` como paquete, para que `pytest` funcione igual invocado de cualquier forma |
| `tests/helpers.py` | Constructores de figuras, individuos, poblaciones y generadores de azar para las pruebas |
| `tests/test_figuras.py` | Las cinco figuras de la fase 01 |
| `tests/test_fitness.py` | La función de aptitud de la fase 02 |
| `tests/test_individuo.py` | El individuo y su caché, de la fase 03 |
| `tests/test_poblacion.py` | La población, sus métricas y la diversidad, de la fase 03 |
| `tests/test_seleccion.py` | Los siete métodos de selección de la fase 04 |
| `tests/test_cruza.py` | Los cuatro métodos de cruza de la fase 05 |
| `tests/test_mutacion.py` | Los cuatro métodos de mutación de la fase 06 |
| `tests/test_supervivencia.py` | Las dos estrategias de supervivencia de la fase 07 |
| `tests/test_reproducibilidad.py` | La corrida completa y los tres criterios de corte, de las fases 08 y 10 |

---

## Archivo por archivo

### `tests/helpers.py`

Existe para que ninguna prueba tenga que construir a mano un individuo válido.
Centraliza la configuración de prueba y los constructores, así que cambiar el
constructor de `Individuo` se arregla en un solo lugar y no en nueve archivos.

| Función | Qué hace |
|---|---|
| `generador_azar(seed)` | Devuelve un generador de numpy con la semilla fija de las pruebas |
| `config_test(**overrides)` | Devuelve una configuración de prueba completa, con los campos que consumen los operadores |
| `crear_triangulo(marca, color)` | Devuelve un triángulo de geometría fija con una marca reconocible en la última coordenada |
| `crear_individuo(fitness_val, cant_genes, marca)` | Devuelve un individuo, opcionalmente con la aptitud ya cacheada |
| `crear_poblacion_test(aptitudes)` | Devuelve una población ya evaluada, con las aptitudes que se le pidan |

La marca en la última coordenada del triángulo es lo que permite, después de una
cruza, saber de qué padre vino cada gen sin mirar adentro de la figura.

### `tests/test_figuras.py`

Cubre la fase 01. Diez de sus pruebas corren sobre las cinco figuras a la vez con
`parametrize`, así que agregar un sexto tipo de figura es agregarlo a una tupla.

| Prueba | Qué verifica |
|---|---|
| `test_la_creacion_al_azar_respeta_el_dominio` | Dos mil figuras de cada tipo, ningún parámetro fuera de rango |
| `test_las_secuencias_son_coherentes` | Parámetros, nombres y rangos tienen el mismo largo, que es lo que asume la diversidad |
| `test_mutar_no_modifica_el_original` | Mutar devuelve una figura nueva y deja intacta la que recibió |
| `test_la_copia_es_independiente` | Mutar una copia no toca a la original |
| `test_la_misma_semilla_da_las_mismas_figuras` | Dos generadores con la misma semilla dan cien figuras idénticas |
| `test_con_color_conserva_la_geometria_y_la_transparencia` | El sesgo de color inicial solo toca los tres canales de color |
| `test_dos_figuras_al_azar_no_comparten_estado` | Quinientos triángulos, ninguno comparte objeto ni parámetros |
| `test_el_recorte_aguanta_miles_de_mutaciones` | Dos mil mutaciones seguidas sin salirse del dominio |
| `test_desde_el_extremo_la_coordenada_no_da_la_vuelta` | Una coordenada en el borde se queda o entra, nunca reaparece del otro lado |
| `test_la_rotacion_envuelve_en_vez_de_recortarse` | La rotación es cíclica: pasarse de 1 reaparece cerca de 0 |
| `test_los_radios_nunca_bajan_de_uno` | La elipse no degenera a radio nulo, que rompe el dibujado |
| `test_el_triangulo_translucido_compone_con_el_fondo` | La transparencia se mezcla en vez de pisar el píxel |
| `test_el_ovalo_rotado_no_deja_halo_oscuro` | La capa auxiliar nace del color de la figura y no de negro transparente |
| `test_el_color_tine_el_png_como_filtro` | El color de la figura se mezcla con el del overlay en la proporción del filtro |
| `test_las_familias_no_se_pueden_instanciar` | `Poligono` y `FiguraElipsoidal` cortan de entrada |

**`test_desde_el_extremo_la_coordenada_no_da_la_vuelta`** — arranca con las seis
coordenadas en el extremo del dominio y muta con probabilidad interna 1. Después
de cada mutación, ninguna coordenada puede estar a más de un `max_coord_delta`
del extremo. Si el recorte se aplicara antes de sumar el delta, o si hubiera
envoltura, esta prueba lo detecta enseguida.

**`test_el_color_tine_el_png_como_filtro`** — el color no multiplica al overlay:
se mezcla con él en un 45 %, según quedó implementado en `imagen_png.py`. La
proporción está escrita en el archivo de pruebas como constante, así que si
alguien la cambia en la figura, esta prueba avisa.

### `tests/test_fitness.py`

Siete pruebas sobre la fase 02. Es el archivo más chico y el que más protege: la
aptitud es lo que ordena a toda la población.

| Prueba | Qué verifica |
|---|---|
| `test_imagenes_identicas_dan_exactamente_uno` | El fenotipo perfecto vale 1, la cota superior |
| `test_el_error_maximo_da_un_positivo_muy_chico` | El peor caso sigue siendo estrictamente mayor que cero |
| `test_la_aptitud_preserva_el_orden_del_error` | A menos error, más aptitud, sin empates |
| `test_el_canal_alfa_no_entra_en_la_comparacion` | Dos imágenes que solo difieren en transparencia dan aptitud máxima |
| `test_las_diferencias_negativas_no_desbordan` | Restar colores sin signo no da la vuelta: el error es simétrico |
| `test_formas_distintas_cortan_con_error` | Comparar imágenes de distinto tamaño falla en vez de devolver un número sin sentido |
| `test_no_modifica_las_matrices_que_recibe` | La aptitud es una función pura |

**Por qué la tercera es la que más importa.** Si la aptitud no preservara el
orden del error, el motor seguiría corriendo, los gráficos seguirían saliendo y
todas las conclusiones de la fase 12 estarían comparando ruido. Que sea
estrictamente positiva tampoco es un detalle: la ruleta y Boltzmann la usan como
peso de probabilidad y un cero rompería el reparto.

### `tests/test_individuo.py`

Diez pruebas sobre el caché de aptitud, que es el mecanismo que más silenciosamente
puede arruinar una corrida.

| Prueba | Qué verifica |
|---|---|
| `test_el_cache_evita_recalcular` | Pedir dos veces la aptitud de un individuo que no cambió la calcula una sola vez |
| `test_cambiar_un_gen_invalida_el_cache` | Reemplazar un gen obliga a renderizar de nuevo |
| `test_reemplazar_por_un_gen_de_iguales_parametros_no_invalida` | El caché se invalida por cambio de parámetros, no por cambio de objeto |
| `test_la_copia_no_comparte_la_lista_de_genes` | Cambiarle un gen a la copia no toca al original |
| `test_la_copia_conserva_la_aptitud_porque_los_genes_no_cambian` | Sobrevivir de una generación a otra no obliga a recalcular |
| `test_la_copia_de_un_individuo_sucio_nace_sucia` | La copia arrastra el estado del caché y no inventa una aptitud vigente |
| `test_el_vector_de_parametros_concatena_los_genes_en_orden` | El vector que consume la diversidad respeta el orden de dibujado |
| `test_el_vector_de_parametros_se_recalcula_al_cambiar_un_gen` | El vector cacheado no queda viejo después de una mutación |
| `test_los_genes_se_devuelven_como_tupla_en_orden` | Exponer los genes no permite modificar la lista interna |
| `test_un_individuo_sin_genes_falla` | Un cromosoma vacío corta con un error del dominio |

Las pruebas del caché no leen variables internas del individuo para contar
renderizados: le pasan un evaluador de mentira que cuenta cuántas veces lo
llamaron. Así la prueba verifica comportamiento y no implementación, y sobrevive
a cualquier refactor de adentro de la clase.

### `tests/test_poblacion.py`

Doce pruebas sobre las métricas de la generación, con foco en la diversidad.

| Prueba | Qué verifica |
|---|---|
| `test_diversidad_nula_con_individuos_clonados` | Una población colapsada da exactamente cero |
| `test_diversidad_positiva_cuando_hay_variedad` | La métrica sube apenas los individuos dejan de ser iguales |
| `test_diversidad_ordenada` | Una población más dispersa da un valor mayor que una concentrada |
| `test_la_normalizacion_cancela_la_escala` | La misma dispersión relativa da la misma diversidad en geometría y en color |
| `test_las_metricas_de_aptitud_son_coherentes` | El máximo es la aptitud del mejor y el promedio queda entre el mínimo y el máximo |
| `test_mejor_desempata_por_el_de_menor_indice` | Dos individuos con la misma aptitud máxima resuelven siempre igual |
| `test_pedir_el_fitness_sin_evaluar_falla` | Consultar métricas antes de evaluar corta en vez de devolver basura |
| `test_evaluar_respeta_el_cache_de_cada_individuo` | Evaluar dos veces seguidas no vuelve a renderizar a nadie |
| `test_la_siguiente_generacion_conserva_tamano_rangos_y_numera` | La transición mantiene el tamaño y avanza el contador |
| `test_la_siguiente_generacion_rechaza_otro_tamano` | La población no puede cambiar de tamaño entre generaciones |
| `test_no_admite_el_mismo_individuo_repetido_por_referencia` | Dos referencias al mismo individuo cortan, porque mutarían juntas |
| `test_no_admite_cromosomas_de_distinto_largo` | Todos los individuos tienen la misma cantidad de genes |

**`test_la_normalizacion_cancela_la_escala`** — es la prueba que justifica que la
diversidad signifique algo. Arma dos poblaciones de dos individuos cada una. En
la primera, los dos individuos difieren solo en una coordenada, y difieren de
extremo a extremo de su rango. En la segunda difieren solo en el canal rojo,
también de extremo a extremo. En crudo esos desvíos son distintos, 55 contra
127.5, porque las escalas son distintas. Divididos por el ancho de su rango los
dos dan 0.5, y la diversidad de las dos poblaciones tiene que dar exactamente lo
mismo. Si alguien saca la normalización, la geometría se come la métrica y el
color deja de contar.

### `tests/test_seleccion.py`

Veintitrés pruebas sobre los siete métodos de la fase 04, más la maquinaria
compartida. Verifica de cada método el largo del resultado, que devuelva
referencias a individuos de la población y su comportamiento característico: que
elite tome exactamente a los mejores y repita cuando hace falta, que la ruleta
sea proporcional a la aptitud, que universal con población homogénea reparta
exacto, que Boltzmann siga la fórmula esperada y aguante el desborde de la
exponencial, que el torneo determinístico con tamaño igual a la población siempre
gane el mejor, que el probabilístico con umbral 0 gane el peor y con umbral 1 el
mejor, y que ranking sea invariante a la escala del fitness.

### `tests/test_cruza.py`

Doce pruebas sobre los cuatro métodos de la fase 05. Verifica que los dos hijos
sean individuos nuevos, del mismo largo que los padres y complementarios entre sí
(lo que un hijo hereda del padre, el otro lo hereda de la madre, locus por
locus), más el comportamiento propio de cada método: el punto de corte válido en
un punto, los tres bloques en dos puntos, el segmento circular que desborda en
anular, y la máscara en uniforme.

### `tests/test_mutacion.py`

Nueve pruebas sobre los cuatro métodos de la fase 06. Verifica que la mutación
por gen altere exactamente un gen con probabilidad 1, que multigen esté acotada
por `max_genes_to_mutate`, que la uniforme mute todos los genes con probabilidad
1 y ninguno con probabilidad 0, que la no uniforme sea todo o nada, que ninguna
saque un parámetro del dominio del lienzo, que la misma semilla dé el mismo
resultado y que mutar invalide el caché de aptitud del individuo.

### `tests/test_supervivencia.py`

Ocho pruebas sobre las dos estrategias de la fase 07. Verifica que la aditiva
seleccione del pozo combinado de padres e hijos, que la exclusiva resuelva los
tres casos de la consigna (más hijos que lugares, exactamente los mismos, y menos
hijos que lugares, completando con padres) y que la generación resultante tenga
siempre el tamaño de la población.

### `tests/test_reproducibilidad.py`

Siete pruebas que corren el motor entero sobre una imagen de 24 por 24 generada
en memoria, con seis individuos de seis genes y sin procesos aparte.

| Prueba | Qué verifica |
|---|---|
| `test_dos_corridas_con_la_misma_semilla_dan_las_mismas_metricas` | Las métricas de todas las generaciones coinciden exactamente |
| `test_dos_corridas_con_la_misma_semilla_dan_el_mismo_mejor_genotipo` | La reproducibilidad llega hasta los parámetros del mejor individuo |
| `test_dos_semillas_distintas_dan_resultados_distintos` | La semilla realmente manda |
| `test_la_corrida_termina_por_generaciones_agotadas` | El corte por cantidad de generaciones y lo que queda registrado |
| `test_la_corrida_termina_por_fitness_alcanzado` | El corte por aptitud se evalúa antes que el de generaciones |
| `test_la_corrida_termina_por_estancamiento` | El motor corta cuando el mejor deja de mejorar |
| `test_el_registro_guarda_la_configuracion_de_la_corrida` | El resultado es rastreable: queda con qué configuración se produjo |

La configuración de estas pruebas sale de `config/conf.json` pasando por
`cargar_config`, y recién después se achica para que la corrida sea mínima. Como
efecto secundario, la suite falla si alguien deja el archivo de configuración por
defecto en un estado inválido.

Las dos primeras pruebas son las que sostienen todo el trabajo experimental: sin
reproducibilidad, cualquier diferencia entre dos métodos en la fase 12 puede ser
azar y no hay forma de demostrar lo contrario.

---

## Cómo comprobar que anda

```bash
python -m pytest tests -q
```

Tienen que pasar las 145 pruebas en menos de dos segundos. Para ver qué cubre
cada una:

```bash
python -m pytest tests -v
```

Y para correr una sola parte:

```bash
python -m pytest tests/test_poblacion.py -q
python -m pytest tests -q -k diversidad
```

---

## Decisiones y pendientes

**Decisiones**

- **Se usa `pytest` y no `unittest`.** Es una dependencia más, pero solo de
  desarrollo: no la importa nada de `src/`, así que el motor sigue corriendo con
  numpy y pillow solamente. A cambio, `parametrize` permite correr la misma
  prueba sobre las cinco figuras o los siete métodos de selección sin repetir
  código, que es lo que mantiene la suite en un tamaño legible.
- **Existe `tests/__init__.py`.** Sin él, `from tests.helpers import ...` depende
  de cómo se invoque pytest: anda con `python -m pytest` y falla con `pytest` a
  secas. Con el archivo, las dos formas funcionan.
- **Las pruebas verifican lo que el código hace hoy, no lo que decía la
  especificación.** Dos casos concretos: la copia de un individuo conserva su
  aptitud cacheada, en vez de nacer sin ella, y el color del PNG se mezcla con el
  overlay en un 45 % en vez de multiplicarlo. Las dos son decisiones deliberadas
  que se tomaron implementando, y las pruebas las fijan como comportamiento
  esperado.
- **Ninguna prueba lee del disco ni de `resources/`.** Las imágenes objetivo y
  los overlays se generan en memoria. Una suite que necesita un archivo puntual
  del repositorio se rompe cuando alguien lo mueve, y además tarda.
- **Las pruebas del caché cuentan llamadas a un evaluador de mentira** en lugar
  de leer atributos internos del individuo. Así verifican comportamiento y no
  implementación.

**Pendientes**

Quedan sin cubrir cuatro módulos, en orden de lo que más conviene atacar:

- **`src/output.py`** (fase 09): que el CSV tenga una fila por generación, que
  los encabezados se adapten a los cinco tipos de figura, que el GIF se arme y
  que dos corridas seguidas no se pisen. Escribe en disco, así que necesita
  directorio temporal.
- **`src/renderizador.py`** (fase 02): que el orden de dibujado importe, que dos
  renders de la misma lista den lo mismo y que el multiplicador de resolución se
  aplique. Hoy está cubierto de refilón por las pruebas de dibujado de las
  figuras y por las de reproducibilidad, que renderizan de verdad.
- **`src/config.py`** (fase 00): que cada campo mal tipado o fuera de rango corte
  con mensaje claro. La validación ya es defensiva y falla ruidosamente, así que
  el riesgo es bajo.
- **La línea de comandos** (fase 10): overrides, archivo de configuración
  alternativo y mensajes de error. Es la única parte que pide pruebas de
  integración de verdad y la que menos aporta por prueba escrita.
