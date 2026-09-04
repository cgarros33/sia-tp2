# Mapa de fases — TP2 Algoritmos Genéticos

Índice del trabajo. Cada fase tiene su propio `.md` en esta carpeta y produce un
resumen en `docs/resumenes/`.

Orden de lectura para arrancar una fase:

1. `CLAUDE.md`
2. `docs/reglas.md`
3. `docs/contexto.md`
4. este documento
5. `docs/fases/FASE_NN_<nombre>.md` — solo la fase que corresponda

Cada documento de fase es autocontenido: lleva adentro las firmas que produce y
también las de otras fases que necesita usar.

---

## Reglas que valen para todas las fases

Se repiten en cada documento de fase porque el agente arranca con contexto limpio
cada vez. No son negociables.

1. **El agente no escribe en git.** Nada de `commit`, `push`, `merge`, `rebase`,
   `reset`, `checkout <rama>`, `stash`, `tag`, `gh pr create`. Puede leer con
   `status`, `diff`, `log`, `show`. Commitea siempre una persona, a mano.
2. **El agente no se firma.** Ni `Co-Authored-By: Claude`, ni
   `Generated with Claude Code`, ni equivalentes: en commits, código, docstrings,
   README o documentación. El trabajo es del grupo.
3. **Checkpoint antes de todo archivo que calcule.** Si el archivo decide,
   pondera, puntúa, estima, agrega o compara numéricamente, el agente para y
   explica con el formato de la regla 3 de `docs/reglas.md`, y espera respuesta.
4. **Dependencias.** En `src/`: solo stdlib de Python, `numpy`, `scipy` y
   `pillow`. Prohibida cualquier biblioteca que resuelva algoritmos genéticos.
   Cualquier otra cosa se consulta antes.
5. **Código sin comentarios.** Se comenta solo una cuenta que no se lee del
   código o una regla que si alguien la borra rompe algo. Docstrings de una
   línea.
6. **Nadie toca archivos fuera de su fase.** La sección "Archivos que produce" de
   cada documento es el límite. Si hace falta tocar algo de otra fase, se avisa
   antes.
7. **Toda fase termina con su resumen** en `docs/resumenes/`, siguiendo
   `docs/resumenes/_PLANTILLA.md`.

---

## Tabla de fases

| Ola | Fase | Nombre | Archivos que produce | Depende de | Dueño |
|:---:|:---:|---|---|---|---|
| 1 | 00 | Andamiaje, configuración y CLI | `src/config.py`, `src/cli.py`, `config/conf.json`, estructura de carpetas | — | Matías |
| 1 | 01 | Genes: las cinco figuras | `src/figuras/base.py`, `triangulo.py`, `cuadrilatero.py`, `pentagono.py`, `ovalo.py`, `imagen_png.py` | — | Matías |
| 2 | 02 | Fenotipo: renderizador y fitness | `src/renderizador.py`, `src/fitness.py` | 01 | Celestino |
| 2 | 03 | Individuo y Población | `src/individuo.py`, `src/poblacion.py` | 01, 02 | Leo |
| 3 | 04 | Selección (7 métodos) | `src/seleccion/*.py` | 03 | Matías |
| 3 | 05 | Cruza (4 métodos) | `src/cruza/*.py` | 03 | Federico |
| 3 | 06 | Mutación (4 métodos) | `src/mutacion/*.py` | 01, 03 | Leo |
| 3 | 07 | Supervivencia (2 estrategias) | `src/supervivencia/*.py` | 03, 04 | Celestino |
| 4 | 08 | Inicialización, registro y motor | `src/inicializacion.py`, `src/registro.py`, `src/motor.py` | 00–07 | Celestino |
| 4 | 09 | Output y métricas de corrida | `src/output.py` | 03 | Federico |
| 5 | 10 | Integración end-to-end y README | `main.py`, `README.md` | todas | Matías |
| 5 | 11 | Verificación: suite de tests | `tests/*.py` | todas | Leo |
| 6 | 12 | Experimentación y gráficos | `analisis/*.py`, `results/` | 10 | Federico |
| 6 | 13 | Presentación y conclusiones | `docs/presentacion/` | 12 | todos |

Dentro de una misma ola las fases son independientes y se hacen en paralelo.
Entre olas hay que esperar.

---

## Por qué las olas están armadas así

**Ola 1.** Ni la configuración ni las figuras dependen de nada. Son los dos
puntos de entrada.

**Ola 2.** El renderizador necesita que existan las figuras, el fitness necesita
el renderizador, e Individuo y Población necesitan los dos. Aun así las dos fases
van en paralelo: el documento de la fase 03 incluye la firma de
`calcular_fitness`, así que se programa contra esa firma sin esperar a que la 02
esté terminada.

**Ola 3.** Cuatro familias de operadores sin solapamiento entre sí. Las cuatro
dependen solamente de la interfaz de `Individuo`, que queda fija en la ola 2.
Supervivencia además usa un método de selección, pero lo recibe como parámetro,
así que tampoco necesita que la fase 04 esté terminada.

**Ola 4.** El motor es lo primero que necesita que todo lo anterior exista de
verdad, no solo su firma. El output es independiente y va en paralelo.

**Ola 5.** Recién acá el programa corre entero. Los tests van después de la
integración para cubrir también el end-to-end.

**Ola 6.** Los experimentos necesitan un motor que funcione, y la presentación
necesita los experimentos.

---

## Cómo se trabaja una fase

1. **Rama propia.** `git checkout -b fase-NN-<nombre>`, hecho por la persona, no
   por el agente.
2. **Al agente se le pasa el documento de la fase** junto con `CLAUDE.md`,
   `docs/reglas.md` y `docs/contexto.md`. El prompt lo arma cada integrante, pero
   tiene que dejar claro: que implemente solo esa fase, que no toque archivos
   fuera de la lista de la sección 2, que no commitee ni pushee, que no se firme
   como coautor y que haga el checkpoint antes de cada archivo que calcule.
3. **El agente explica antes de escribir.** Primero dice qué entendió y qué dudas
   tiene; recién después arranca.
4. **Checkpoints.** Cada archivo que calcula dispara uno.
5. **Verificación.** Se corren las comprobaciones de la sección "Cómo se
   verifica" antes de dar la fase por terminada.
6. **Resumen.** Se escribe `docs/resumenes/FASE_NN_RESUMEN.md` siguiendo la
   plantilla.
7. **La persona commitea y pushea.** El agente avisa qué archivos tocó y espera.

---

## Riesgo del trabajo en paralelo

Cuatro personas sobre el mismo repo con agentes distintos chocan si alguien se
sale de su lista de archivos. Dos medidas:

- **Los documentos de fase no se editan por cuenta propia.** Si al implementar
  aparece que una firma tiene que cambiar, se avisa y se cambia una sola vez en
  los documentos afectados. Esas firmas son lo que hace posible el paralelismo.
- **`config/conf.json` lo toca solo la fase 00.** Cualquier campo nuevo que una
  fase necesite se pide, no se agrega por cuenta propia.
