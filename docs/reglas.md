# 01 — Reglas de trabajo del agente

Este documento es normativo. Ante cualquier duda entre "hacer algo útil" y
"cumplir una de estas reglas", gana la regla.

---

## 1. Git: leer sí, escribir nunca

**Prohibido sin excepción:**

```
git commit        git push         git merge
git rebase        git reset        git checkout <rama>
git stash         git tag          gh pr create
```

**Permitido siempre:** `git status`, `git diff`, `git log`, `git show`.

Cuando termines un bloque de trabajo, cerrá con un resumen así:

```
Listo. Archivos creados:
  src/modelo/tablero.py
  src/modelo/estado.py
Archivos modificados:
  main.py
Verificación: los 5 niveles siguen dando el costo esperado.

No commiteé nada. Revisalo y commiteá vos cuando quieras.
```
## 2. Autoría: el trabajo es del grupo

**Nunca** agregues, ni sugieras agregar, ninguna de estas líneas:

```
Co-Authored-By: Claude <noreply@anthropic.com>
🤖 Generated with Claude Code
Co-authored-by: Claude Code
```

Tampoco en comentarios de código, docstrings, encabezados de archivo, README,
CHANGELOG ni mensajes de commit sugeridos.

## 3. Checkpoint: parar antes de cualquier archivo que calcule

Antes de escribir un archivo que **decida, pondere, puntúe, estime, agregue o
compare numéricamente**, tenés que parar y explicar.
**Formato del checkpoint:**

```
CHECKPOINT — voy a escribir src/heuristicas/h3_matching.py

QUÉ CALCULA
  <en dos o tres oraciones, sin código>

POR QUÉ ASÍ
  <qué problema del enfoque anterior resuelve>

POR QUÉ ES ADMISIBLE
  <la demostración, en dos renglones, que va a ir en la presentación>

QUÉ SE DESCARTÓ
  <la alternativa evaluada y el motivo>

CÓMO SE VERIFICA
  <el test o la comparación que prueba que está bien>

¿Avanzo?
```

Después esperá respuesta. No escribas el archivo hasta que te digan que sí.

**Por qué.** Los profesores preguntan sobre cualquier parte, a cualquiera de los
cuatro. Un archivo que hace cuentas que el grupo no puede explicar es peor que
no tenerlo: es una pregunta que no se va a poder responder en el oral.

## 4. Resúmenes: uno por fase, en `docs/resumenes/`

Al terminar cada fase, escribí `docs/resumenes/FASE_N_RESUMEN.md` siguiendo
`docs/resumenes/_PLANTILLA.md`. Tiene que estar escrito para alguien que **no
vio el código**: los otros tres integrantes lo van a leer para entender qué
existe y por qué.

Regla dura: **todo archivo nuevo aparece en el resumen de su fase**, con una
línea sobre qué hace y un párrafo sobre por qué existe. Si un archivo no
justifica un párrafo, probablemente no debería existir.

## 5. Dependencias

Autorizadas en `src/`: sólo la biblioteca estándar de Python, más `numpy`,
`scipy` y `pillow`


**Prohibidas:** cualquier biblioteca que resuelva algoritmos genéticos

Si creés que hace falta algo más, preguntá antes de instalarlo.


## 6. El código va sin comentarios

El código se explica solo. Los nombres son largos y en castellano justamente
para eso, y quien lo lee ya sabe leer Python. 

Un comentario se justifica sólo en dos casos:

- **Una cuenta que no se lee del código.** Por qué una constante vale lo que
  vale, por qué una condición está en un bucle, qué se eligió cuando había dos
  opciones numéricas posibles.
- **Una regla que, si alguien la borra, rompe algo.** 

Todo lo demás sobra.


**Docstrings: uno de una línea** por módulo, clase y función, diciendo qué es.
Nada de secciones "QUÉ REPRESENTA", "LA DECISIÓN DE DISEÑO" o "QUÉ SE DESCARTÓ"
dentro de un archivo `.py`.


## 7. Cuando algo no cierra

Si una especificación te parece equivocada, incompleta o
contradictoria: **decilo antes de implementarla**.

## 8. Sincronización de configuración y `conf-example.json`

Cualquier cambio o agregado a la configuración (`config/conf.json` o
`src/config.py`) exige actualizar obligatoriamente `config/conf-example.json`
con todas las variables, todos sus valores posibles y una explicación concisa
de qué hace cada uno si no es autoexplicativo.