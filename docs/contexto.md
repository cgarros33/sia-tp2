Este es un trabajo práctico sobre algoritmos genéticos de la materia Sistemas de Inteligencia Artificial. El objetivo del trabajo es implementar un motor de Algoritmo Genético (AG) que se utilizará para en base a una imagen base intentar aproximar la misma imagen usando unicamente poligonos, en principio triangulos, de color homogeneo y con posibilidad de tener transparencia. Por cada ejecución, se va a establecer un número fijo de triángulos que se van a componer a la imagen. 

Con el objetivo de evaluar qué métodos serán los más aptos para resolver el problema, se generarán gráficos comparativos que muestren el desempeño de cada uno lado a lado. Hay que Para poder hacer esto, se van a implementar: 

## **Los siguientes métodos de selección (quiénes sobreviven hacia la próxima generación):** 

## **○ Elite** 

Consiste en tomar a los individuos con mejor aptitud. Teniendo que seleccionar selected_count individuos de un conjunto de tamaño population_size, los ordena según fitness y elije cada uno _n(i)_ veces, según la fórmula: _n(i)_ = (selected_count - i) / population_size (siendo⌈ ⌉ _i_ la posición en el ranking). 

## **○ Ruleta** 

Cada individuo tiene una probabilidad de ser elegido proporcional a su aptitud. Primero se transforma la aptitud de cada individuo en una probabilidad relativa _pi_ , normalizando para que todas sumen 1. Para poder elegir con un único número aleatorio se construyen probabilidades acumuladas _qi_ , que funcionan como los límites de los intervalos en [0, 1]. Esos _qi_ se obtienen sumando las probabilidades relativas hasta el índice _i_ . Después se generan selected_count números aleatorios uniformes _rj_ ∈ [0, 1]. Para cada _rj_ se selecciona el individuo cuyo intervalo acumulado lo contiene (es decir el _i_ tal que _qi-1_ < _rj_ ≤ _qi_ ). 

## **○ Universal** 

Es una variante de la ruleta que conserva la misma estructura de intervalos acumulados _qi_ pero cambia cómo se generan los selected_count números aleatorios. En vez de generarlos todos aleatoriamente, se genera un solo número aleatorio _r_ en [0, 1] y a partir de ahí se generan selected_count puntos igualmente espaciados: _rj =_ ( _r_ + _j_ )  selected_count; ∕ _j_ ∈ [0, (selected_count - 1)]. 

## **○ Boltzmann** 

En este método, en vez de usar el fitness directamente como peso de ruleta, se construye una pseudo-aptitud exponencial: a cada individuo se le asigna un peso proporcional a _e_<sup>_f(i)/temperature_</sup> _._ Después esos pesos se normalizan para que se comporten como probabilidades y con eso se selecciona como en el método de la ruleta. La función es la siguiente: _f_ ( _i_ ) / _temperature e ExpVal_ ( _i, g, temperature_ ) = _f_ ( _x_ ) / _temperature_ , siendo _⟨ e ⟩g_ 

- _i_ : Individuo 

- _⟨ ⟩g_ : Avg(population(g)) 

- _f(i)_ : fitness 

## **○ Torneos deterministicos** 

Funciona como una competencia repetida para elegir padres o sobrevivientes. En vez de asignar probabilidades globales como en ruleta, se toman subgrupos pequeños de la población: de una población total de tamaño population_size, se eligen tournament_size individuos al azar y se los hace "competir" comparando sus aptitudes. Como el torneo es determinístico, el ganador es simplemente el de mayor fitness dentro de ese grupo. Este procedimiento se repite de forma independiente hasta reunir la cantidad necesario de selected_count individuos. 

## **○ Torneos probabilísticos** 

Se desarrolla de la siguiente manera: 

1. Se elige un valor de tournament_threshold entre [0.5, 1] 

2. De la población de tamaño population_size, se eligen 2 individuos al azar. 

3. Se toma un valor r al azar uniformemente en [0, 1]. 

   - a. Si _r_ < tournament_threshold se selecciona el más apto. 

   - b. Caso contrario, se selecciona el menos apto. 

4. Se repite el proceso (1.) hasta conseguir los  individuos que se precisan. 

## **○ Ranking** 

Ignora la magnitud numérica directa del fitness, ordena a los individuos y les asigna una pseudo-aptitud lineal basada estrictamente en su posición ordinal según la función _f '_ ( _i_ ) = (population_size - rank(i)) / population_size, usando dicha ponderación para ejecutar una selección por ruleta estándar. 

## **Estas dos estrategias de supervivencia para crear nuevas generaciones** 

## **○ Supervivencia Aditiva** 

Los hijos no reemplazan automáticamente a los padres. En lugar de “tirar” a los padres y quedarse solo con los hijos, se construye un conjunto candidato más grande que incluye a todos los individuos actuales más los hijos. 

## **○ Supervivencia Exclusiva** 

En la medida de lo posible, la nueva generación se arma solo con hijos, o sea que el reemplazo de la población es mucho más “duro” que en la supervivencia aditiva. **K > N:** La nueva generación se genera seleccionando N de los K hijos exclusivamente. **K ≤ N:** La nueva generación se conformará por los K hijos generados + (N-K) individuos seleccionados de la generación actual. 

## **Estos métodos de cruza:** 

- Cruce de un punto 

Se toman dos padres representados como cadenas de genes y se elige al azar una posición de corte  (un locus). A partir de ese punto, se intercambia el resto de la cadena entre 𝑃 los padres. 

## **○ Cruce de dos puntos** 

Se eligen dos posiciones de corte 𝑃 1 y 𝑃 1 (con 𝑃 1≤ 𝑃 2). Eso divide el cromosoma en tres tramos: el prefijo antes de 𝑃 1, el bloque del medio entre 𝑃 1 y 𝑃 2, y el sufijo después de 𝑃 2. La recombinación consiste en intercambiar el tramo del medio entre los dos padres, manteniendo iguales los tramos de afuera. 

## **○ Cruce uniforme** 

Se decide gen por gen de qué padre hereda cada posición. Para cada locus se hace un sorteo con una probabilidad 𝑃 (típicamente 0.5): según el resultado, en esa posición se mantienen los alelos como estaban o se intercambian entre los padres. 

## **○ Cruce anular** 

El cromosoma se trata como si fuera circular, como un anillo. En vez de elegir dos puntos fijos como en el cruce de dos puntos, se elige un punto de inicio  y una longitud . A 𝑃 𝐿 partir de , se toma un segmento continuo de largo  y ese segmento se intercambia entre los 𝑃 𝐿 dos padres para generar los hijos. 

## **Estos métodos de mutación:** 

## **○ Gen** 

Se altera un solo gen con una probabilidad Pm. 

## **○ MultiGen** 

Se selecciona una cantidad [1,M] (azarosa) de genes para mutar, con probabilidad Pm 

## **○ Uniforme** 

Cada gen tiene una probabilidad Pm de ser mutado 

## **○ No Uniforme** 

Con una probabilidad Pm se mutan todos los genes del individuo, acorde a la función de mutación definida para cada gen 

# VARIABLES DE CONFIGURACIÓN 

gene_count: la cantidad de genes que poseerá cada individuo, es decir la cantidad de figuras que tendrá la imagen creada 

population_size: tamaño de la población inicial 

output_resolution_mult: multiplicador de resolución de la imagen original al momento de renderizar la imagen final y realizar las comparaciones - default 1 

file_input: path de la imagen a utilizar como referencia para el motor de AG 

gene_type: figura a ser representada por el gen, puede tomar el valor de “triangle”, “png”, “quad”, “pentagon”, “oval” 

max_genes_to_mutate:Cota superior de la cantidad de figuras que pueden mutar en un mismo individuo, cuando se usa mutación multigen limitada. En cada evento de mutación se sortea un valor uniformemente en el rango [1, max_genes_to_mutate]. intra_gene_Pm: probabilidad de mutar cada uno de los parámetros de una figura (gen) extra_gene_Pm: probabilidad de que un gen mute 

fitness_cutoff: valor de fitness a partir del cual se detiene la ejecución 

stale_content_generation_cutoff: Número de generaciones consecutivas sin una mejora del mejor fitness alcanzado max_coord_delta: delta maximo de mutacion en las coordenadas max_color_delta: delta maximo de mutacion en los valores de RGBA max_rotation_delta: delta maximo de mutacion en la rotacion max_radius_delta: delta maximo de mutacion en el radio 

max_coord_overflow: valor maximo en que una coordenada puede irse del canvas overlay_source: suministra la imagen para el tipo png **selected_count:** cantidad de individuos a seleccionar en los metodos de selección **tournament_size:** cantidad de individuos que compiten en los torneos determinísticos **tournament_threshold:** el umbral de probabilidad para torneos probabilísticos - debe pertenecer al intervalo [0.5, 1] 

temperature: parámetro para la selección de Boltzmann 

random_seed: la semilla para ejecutar las funciones random 

Se definen a continuación los conceptos de gen, individuo y población para el trabajo: 

# GEN: 

Dado que la imagen es aproximada mediante un conjunto de figuras se considera a la figura como el gen en el problema. El gen deberá implementar una interfaz Figura con métodos para renderizar y mutar, de manera que se puedan implementar diferentes tipos de figuras que se utilicen de manera intercambiable para la generación de imágenes. 

1. 

La figura estándar del problema es un triángulo (gene_type = “triangle”), compuesto por las posiciones x e y de cada uno de sus vértices y sus valores RGBA de color y transparencia (de 8 bits sin signo). 

a. 

La función de mutación del triángulo implicará recorrer cada uno de los parámetros del triángulo y con probabilidad intra_gene_Pm se mutará cada uno individualmente de la siguiente manera: 

- b. - Para las posiciones x e y de cada esquina del polígono se calculará un delta
como random [-max_coord_delta, max_coord_delta]. No hay wraparound: si el
resultado se escapa del dominio válido, la coordenada se recorta al extremo
del dominio en lugar de dar la vuelta.

El dominio válido es el canvas ampliado por max_coord_overflow en los cuatro
lados:

    x ∈ [-max_coord_overflow, ancho + max_coord_overflow]
    y ∈ [-max_coord_overflow, alto  + max_coord_overflow]

Concretamente, para x:

    si x + delta < -max_coord_overflow
        la nueva x es -max_coord_overflow
    si x + delta > ancho + max_coord_overflow
        la nueva x es ancho + max_coord_overflow
    en cualquier otro caso
        la nueva x es x + delta

Para y vale lo mismo, reemplazando ancho por alto.

Se permite ese margen de overflow para que una figura pueda quedar
parcialmente fuera del canvas y así cubrir un borde con un solo vértice
adentro, en vez de estar obligada a tener todos sus vértices dentro de la
imagen. max_coord_delta controla cuánto se mueve un vértice por mutación;
max_coord_overflow controla hasta dónde puede llegar. Son independientes. 

- Para los valores de RGBA se tomará el mismo comportamiento con el valor nuevo = valor original + rand[-max_color_delta, max_color_delta], nuevamente sin underflow ni overflow, el valor siempre debe permanecer entre 0 y 255. 

Se deben implementar también otras figuras, a saber: 

2. Cuadrilátero (gene_type = “quad”) 

   - a. Funcionamiento idéntico al triángulo pero con 4 coordenadas de posición 

3. Pentágono (gene_type=”pentagon”) 

   - a. De nuevo funcionamiento idéntico al triángulo pero esta vez con 5 coordenadas de posición 

4. Ovalo (gene_type=”oval”) 

   - a. Se compone de (x, y, radiusX, radiusY, rotation) coordenadas y RGBA (de 8 bits). Rotation entre 0 y 1. La funcion de mutacion tiene el mismo funcionamiento general, solo que utiliza max_radius_delta para calcular el delta del radio en x y en y y el max_rotation_delta para calcular el delta de rotación, nuevamente como delta = rand[-max, max], además de no considerar el max_coord_overflow 

5. Imagen PNG (gene_type=”png”) 

   - a. Por último se presenta la figura de una imagen png, con los mismos comportamientos y variables que el óvalo, solo que al momento de renderizar lo que será reescalado en una imagen png seteada en el archivo de configuración como overlay_source 

INDIVIDUO: Conjunto de gene_count genes, donde gene_count es cantidad de figuras, que es un parámetro del problema (no un hiperparámetro). Tres definiciones necesarias: 1) El orden importa. Como las figuras pueden ser translúcidas, se renderizan una sobre otra en el orden en el que aparecen en el individuo, y el resultado depende de ese orden (un triángulo opaco al final por ejemplo tapa todo lo anterior). Entonces, el individuo es una lista en lugar de un conjunto y la consecuencia de esto es que la posición de un gen dentro del individuo es información genética en sí misma y por ende los operadores de cruza tienen que preservar posiciones (o sea, el gen en el locus i de un padre va al locus i del hijo). 2) Longitud fija. Todos los individuos tienen exactamente gene_count genes, durante toda la corrida para que así podamos usar los distintos operadores de cruza que vimos en clase (un punto, dos puntos, anular, y uniforme) sin necesitar ningún tipo de adaptación 

pues el cromosoma es un vector de longitud constante y los operadores de cruzamiento (como el de un punto o el uniforme) solo intercambian información que está en la misma posición. 

- 3) Fenotipo. Es la imagen que se obtiene al renderizar los count_gene genes en un orden sobre un canvas de color de fondo fijo. El genotipo es un vector de gene_count genes donde cada gen es una figura y encapsula un determinado número de parámetros según la figura utilizada y el locus es la posición de la figura dentro del vector que además determina el orden de dibujado, mientras que el fenotipo son los píxeles de la imagen. La cruza y mutación operan sobre el genotipo mientras que el fitness se calcula sobre el fenotipo. 

Caché de fitness. El individuo almacena su fitness junto con una marca de “sucio”. El fitness se calcula por demanda y se invalida solo cuando el individuo muta. Esto es necesario porque con supervivencia aditiva un mismo individuo sobrevive varias generaciones y se lo evaluaría repetidamente, y el renderizado es una operación MUY costosa en el algoritmo. 

Población: Conjunto de population_size individuos que conforman una generación. Su tamaño se mantiene constante durante toda la corrida, porque las dos estrategias de supervivencia vistas en clase están definidas como una transición entre poblaciones del mismo tamaño. A diferencia del individuo, acá el orden no es información genética. 

Población inicial (generación 0). Se generan population_size individuos con todos los parámetros de cada una de sus figuras muestreados uniformemente al azar dentro del mismo dominio válido que usa el recorte de la mutación (coordenadas con max_coord_overflow, RGBA entre 0 y 255, rotación entre 0 y 1). Se contempla como variante opcional un sesgo en la inicialización, en el que el color inicial de cada figura se muestrea del color promedio de la región de la imagen objetivo donde cae, en lugar de al azar. Reduce la cantidad de generaciones necesarias, a costa de reducir la diversidad inicial. Se implementa como bandera de configuración para poder medir el efecto de las dos alternativas. 

Restricción de tamaño respecto de gene_count. Hay que dimensionar population_size teniendo en cuenta que el largo del cromosoma es gene_count. Una población chica (20 individuos) explora una fracción despreciable del espacio y es una causa directa de convergencia prematura, según las causas listadas en la clase. Como criterio de partida se propone population_size en el orden de 50 a 200, y evaluar el efecto experimentalmente. 

Responsabilidades de la clase Población. Además de contener a los individuos, expone lo que necesita el motor y lo que necesitan las métricas: 

Evaluación de fitness de todos sus individuos, respetando el caché (paralelizable, ya que cada individuo se evalúa de forma independiente). 

Acceso al mejor individuo, al fitness promedio de la generación (requerido por Boltzmann) y al número de generación. 

Una medida de diversidad, necesaria para diagnosticar convergencia prematura y para el criterio de corte por estructura. Se propone el desvío estándar normalizado promedio por locus: para cada parámetro se calcula el desvío entre los population_size individuos, se lo divide por su rango válido y se promedian los resultados. La normalización es necesaria porque las coordenadas y los canales de color están en escalas distintas y, sin ella, el promedio quedaría 

dominado por la geometría. Un valor que tiende a cero indica que la población colapsó a un único genotipo. 

Reproducibilidad. Todos los sorteos, incluida la generación inicial, derivan de un único generador inicializado con random_seed, de modo que dos corridas con la misma configuración den resultados idénticos. Es un requisito para comparar métodos: sin semilla controlada no se puede distinguir si una diferencia proviene del cambio introducido o del azar de la corrida. 

# Consideraciones de rendimiento: 

- Se deben definir los objetos  con (__slots__) para evitar la creacion del diccionario y bajar el overhead, ya se conoce la estructura de los datos a usar 

- 

# CONSIDERACIONES DE EJECUCIÓN: 

1. El programa se ejecuta por defecto con la configuración ubicada en ./config/conf.json 

2. Se pueden modificar parámetros puntuales con --<nombre-parametro>=<valor> (falla si no esta dentro de los contemplados 

3. Se puede modificar el archivo de configuración usado con --config-path=<path> 

4. El motor debe generar distintos archivos csv en ./results (cambiable con --resultpath=<path>). En cada generación se deben guardar los datos de fitness máximo, mínimo y promedio, además de cualquier otro dato  extraido de la generación (la medida de la diversidad por ejemplo) y en resumen.txt la metadata de la ejecucion: fitness final, tiempo de ejecucion, generaciones, configuracion usada, motivo de finalizacion y cualquier otro que se calcule en el proyecto 

5. Con la opción --save-all se guarda en el directorio de csvs el registro completo de todos los genomas de todas los individuos de todas las generaciones, ordenado por generacion 

6. Se debe guardar en ./img (cambiable con --img-path=<path>) un gif del individuo con mejor fitness en cada generación, de manera de observar el progreso del motor. 

# CONSIDERACIONES ESTRUCTURALES 

1. codigo en <project-root>/src 

2. recursos (imagen a imitar y para la figura) en <project-root>/resources 

3. documentacion (spec, contexto, etc) en <project-root>/docs 

4. configuracion en <project-root>/config/conf.json 

5. resultados en <project-root>/results 

6. output de imagenes en <project-root>/img 

Definiciones 

especificas 

de la 

catedra: 

- **Población** : conjunto de soluciones candidatas (“individuos”) que el algoritmo evalúa y mejora en cada ciclo. Para evitar estancamiento, la diversidad genética suele ser clave. 

- **Genotipo** : la forma en que se codifican las soluciones dentro del cromosoma (pueden ser cadenas de bits, vectores de números reales, permutaciones o árboles). Determina cómo interactúan los operadores de cruza y mutación. 

- **Locus** : posición/índice dentro del cromosoma donde se guarda un “gen” (un atributo o parte de la solución). 

- **Cromosoma** : la representación completa de una solución candidata (por ejemplo, una cadena de bits). 

- **Fenotipo** : la solución “interpretada” en el dominio real; las características observables que resultan del cromosoma. 

- **Alelos** : los valores posibles que puede tomar un locus (por ejemplo, 0/1 o combinaciones que codifican color/forma). 

- **Función de fitness** : evaluación de qué tan adaptado o qué tan buena es una solución candidata respecto al problema planteado. A mayor fitness, mayor es la adaptación del individuo. Fitness relativo es el rendimiento de un individuo respecto al resto de la población. 

- **Selección** : proceso por el cual se decide qué individuos pasan a la siguiente generación o se eligen para reproducirse. Su objetivo es equilibrar la presión de favorecer las mejores soluciones (explotación) sin perder la variedad necesaria para seguir explorando el espacio de búsqueda (exploración) y así poder llegar a las mejores soluciones. 

- **Cruza** : operador que toma a 2 individuos seleccionados como “padres” y recombina sus genes para generar nuevos “hijos”. 

- **Mutación** : Consiste en introducir pequeñas variaciones o cambios aleatorios en la información genética de los cromosomas. Su función principal es asegurar y enriquecer la diversidad genética para impedir la convergencia prematura, que ocurre cuando la población se vuelve homogénea y se estanca en soluciones subóptimas (máximos locales) antes de alcanzar un rendimiento óptimo real. 

- **Supervivencia** : Es el mecanismo que determina qué soluciones (entre la población actual y los descendientes generados) continuarán en la siguiente generación para mantener un tamaño de población constante. 

- **Brecha generacional** : Es un parámetro que determina de manera exacta qué proporción de la población es renovada en cada generación. 

- **Esquema** : Es un patrón parcial que describe un conjunto de cromosomas que comparten ciertos genes en posiciones específicas, dejando el resto de las posiciones como comodines. El Teorema de los Esquemas demuestra que aquellos patrones de orden bajo y con una aptitud superior a la media de la población verán incrementada su presencia de forma exponencial en las siguientes generaciones. 

- **Criterios de corte** : Son las condiciones que dictan cuándo detener las iteraciones del algoritmo 

