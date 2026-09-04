# Fase 11 — Verificación: suite de tests

> **Ola:** 5 · **Depende de:** todas las anteriores · **Habilita:** 12

---

## 1. Objetivo

Al terminar esta fase las verificaciones que cada fase describió en su documento
existen como pruebas automáticas que se corren con un solo comando. Deja de
depender de que cada uno haya comprobado a mano lo suyo. Es también la red que
permite tocar hiperparámetros y hacer experimentos en la fase 12 sabiendo si algo
se rompió.

---

## 2. Archivos que produce

| Archivo | Qué cubre |
|---|---|
| `tests/__init__.py` | Vacío |
| `tests/test_config.py` | Fase 00 |
| `tests/test_figuras.py` | Fase 01 |
| `tests/test_renderizador.py` | Fase 02, el renderizador |
| `tests/test_fitness.py` | Fase 02, la aptitud |
| `tests/test_individuo.py` | Fase 03, el individuo y su caché |
| `tests/test_poblacion.py` | Fase 03, las métricas y la diversidad |
| `tests/test_seleccion.py` | Fase 04 |
| `tests/test_cruza.py` | Fase 05 |
| `tests/test_mutacion.py` | Fase 06 |
| `tests/test_supervivencia.py` | Fase 07 |
| `tests/test_motor.py` | Fase 08 |
| `tests/test_output.py` | Fase 09 |
| `tests/test_integracion.py` | Fase 10, la corrida completa |

Esta fase puede corregir defectos que las pruebas destapen en archivos de otras
fases. Todo arreglo queda anotado en el resumen, con el archivo tocado y qué
prueba lo descubrió.

---

## 3. Qué hay que implementar

### Punto de partida

Cada documento de fase tiene una sección "Cómo se verifica" con una tabla de
comprobaciones. Esa tabla es la especificación de las pruebas: cada fila se
convierte en al menos una prueba automática. No hay que inventar qué probar, hay
que traducir esas tablas.

Además, cada documento tiene una sección "Errores probables". Los errores más
graves de esa lista merecen una prueba que los detecte explícitamente, aunque la
tabla de verificación no los cubra fila por fila.

### Herramienta

Se usa el módulo de pruebas de la biblioteca estándar de Python. No se instala
nada: la regla 5 solo autoriza la biblioteca estándar más las tres bibliotecas de
cálculo e imágenes, y agregar una herramienta de pruebas externa requeriría
consultarlo con el grupo sin ganar nada que haga falta acá.

Toda la suite se tiene que poder correr con un solo comando, y también fase por
fase.

### Qué tiene que cumplir cada prueba

- **Ser determinista.** Toda prueba que involucre azar fija la semilla. Una
  prueba que a veces pasa y a veces no es peor que no tenerla, porque enseña a
  ignorar los resultados.
- **Ser rápida.** La suite entera tiene que correr en menos de un minuto. Las
  pruebas del motor y de integración usan poblaciones de diez individuos, cinco
  genes y tres generaciones sobre una imagen chica generada en memoria. Probar
  que el ciclo funciona no requiere una corrida real.
- **No depender del disco cuando no hace falta.** Las que sí escriben archivos
  usan un directorio temporal y lo limpian.
- **No depender de `resources/`.** Las imágenes de prueba se generan en memoria.
  Una suite que necesita un archivo puntual del repositorio se rompe cuando
  alguien lo mueve.
- **Fallar con un mensaje que diga qué se esperaba.** Una prueba que falla y solo
  informa que dos valores no coinciden obliga a leer el código de la prueba para
  entender qué pasó.

### Las tres pruebas que más importan

Estas cubren los errores que no dan ninguna excepción y que arruinan el
algoritmo en silencio. Si el tiempo no alcanza para todo, estas van primero.

**El caché se invalida al mutar.** Un individuo que muta y sigue reportando la
aptitud anterior hace que la selección ordene la población con números falsos. El
motor no falla: simplemente no converge. Se prueba mutando un individuo ya
evaluado y comprobando que pedirle la aptitud dispara un cálculo nuevo.

**Los hijos no comparten figuras con los padres.** Si la cruza o la mutación
copian la lista de genes pero no las figuras, mutar a un hijo muta a su padre, y
el caché del padre queda mintiendo. Se prueba mutando un gen del hijo y
comprobando que el padre no cambió.

**La corrida es reproducible.** Dos corridas con la misma configuración y la
misma semilla tienen que dar métricas idénticas en todas las generaciones. Sin
esto, ninguna comparación de la fase 12 significa nada, porque no se puede
distinguir si una diferencia viene del método o del azar.

---

## 4. Interfaces de otras fases

Las pruebas usan las interfaces públicas de todos los módulos, tal como las
describe cada documento de fase. No acceden a estado interno: una prueba que se
apoya en cómo está implementado algo se rompe con cualquier refactor y deja de
verificar comportamiento.

La única excepción razonable es contar cuántas veces se renderiza, que hace falta
para probar el caché. Se resuelve envolviendo el renderizador con un contador en
la prueba, no leyendo variables internas del individuo.

---

## 5. Decisiones ya tomadas

| Decisión | Motivo |
|---|---|
| Se usa el módulo de pruebas de la biblioteca estándar | La regla 5 no autoriza herramientas externas, y para lo que hace falta acá no aportan nada |
| Un archivo de pruebas por fase | Cada uno puede correr las suyas mientras trabaja, y cuando algo falla se sabe de inmediato qué fase revisar |
| Las tablas de verificación de cada fase son la especificación de las pruebas | Las comprobaciones ya están pensadas y acordadas; escribir pruebas distintas sería decidir dos veces lo mismo |
| Toda prueba con azar fija la semilla | Una prueba intermitente enseña a ignorar los resultados de la suite |
| Las imágenes de prueba se generan en memoria | Una suite que depende de un archivo del repositorio se rompe cuando alguien lo mueve o lo cambia |
| Las pruebas del motor usan corridas mínimas | Probar que el ciclo funciona no requiere una corrida real, y una suite lenta se deja de correr |
| Esta fase puede corregir archivos de otras fases | Encontrar un error y no poder arreglarlo obligaría a coordinar a cuatro personas por cada defecto |

---

## 6. Decisiones abiertas

- **Cobertura de las combinaciones.** Probar los siete métodos de selección por
  las dos estrategias de supervivencia por los cuatro de cruza por los cuatro de
  mutación por los cinco tipos de figura son mil ciento veinte corridas. Hay que
  elegir un subconjunto: probar cada operador contra una configuración base, más
  unas pocas combinaciones completas, cubre lo importante sin volver lenta la
  suite. El criterio concreto queda a criterio de quien implementa y se escribe
  en el resumen.

---

## 7. Checkpoints obligatorios

Ninguno: las pruebas comprueban resultados, no calculan nada del algoritmo.

---

## 8. Cómo se verifica

| # | Qué se prueba | Entrada | Resultado esperado |
|---|---|---|---|
| 1 | La suite corre entera | El comando único | Todas las pruebas pasan |
| 2 | La suite corre por fase | El comando sobre un solo archivo | Corren solo esas pruebas |
| 3 | Duración | La suite entera | Menos de un minuto |
| 4 | Determinismo | La suite entera, tres veces seguidas | El mismo resultado las tres veces |
| 5 | Cobertura de las tablas | Cada fila de cada sección "Cómo se verifica" de las fases 00 a 10 | Le corresponde al menos una prueba |
| 6 | Las pruebas detectan de verdad | Romper a propósito la invalidación del caché | La prueba correspondiente falla |
| 7 | Ídem con las figuras compartidas | Hacer que la cruza comparta figuras en vez de copiarlas | La prueba correspondiente falla |
| 8 | Ídem con la reproducibilidad | Crear un segundo generador de azar dentro del motor | La prueba correspondiente falla |
| 9 | Sin dependencias del repositorio | La suite sobre una copia sin la carpeta de recursos | Pasa igual |
| 10 | Sin restos en disco | La suite entera | No quedan archivos ni carpetas creados por las pruebas |

Las verificaciones 6, 7 y 8 son la parte más importante de esta fase. Una prueba
que pasa siempre, incluso cuando el código está roto, da una falsa sensación de
seguridad que es peor que no tener la prueba. Romper el código a propósito y
comprobar que la prueba se da cuenta es la única forma de saber que sirve.

---

## 9. Errores probables

- **Pruebas que pasan aunque el código esté roto** → la suite da seguridad falsa,
  que es peor que no tenerla → verificaciones 6, 7 y 8.
- **Pruebas intermitentes por no fijar la semilla** → el grupo aprende a
  ignorarlas y la suite deja de servir → verificación 4.
- **Una suite lenta** → se deja de correr, y una suite que no se corre no existe
  → verificación 3.
- **Probar estado interno en vez de comportamiento** → cualquier refactor rompe
  pruebas que en realidad no estaban verificando nada.
- **Pruebas que dependen de archivos del repositorio** → se rompen cuando alguien
  mueve o cambia la imagen objetivo → verificación 9.
- **Pruebas que dejan archivos dados vuelta** → ensucian el repositorio y en algún
  momento alguien los commitea → verificación 10.
- **Traducir las tablas de verificación de forma incompleta** → quedan huecos
  justo en las fases que menos se revisaron a mano → verificación 5, recorriendo
  las tablas fila por fila.

---

## 10. Cierre de la fase

- [ ] Todos los archivos de la sección 2 existen y la suite corre entera
- [ ] Todas las verificaciones de la sección 8 pasan
- [ ] `docs/resumenes/FASE_11_RESUMEN.md` está escrito, incluyendo los arreglos a archivos de otras fases y qué prueba destapó cada uno
- [ ] El agente no commiteó ni pusheó nada
