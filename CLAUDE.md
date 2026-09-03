# TP2 — Sistemas de Inteligencia Artificial (ITBA)

Aproximación a imágenes con polígonos mediante un motor de Algoritmos Genéticos

## Antes de tocar nada, leé estos documentos

- `docs/contexto.md` contexto del trabajo
- `docs/reglas.md` reglas obligatorias


## Reglas que no se negocian

1. **NUNCA ejecutes `git commit` ni `git push`.** Ni siquiera si parece obvio o
   conveniente. Podés usar `git status`, `git diff` y `git log` para leer.
   Cuando termines algo, decí qué archivos cambiaron y **esperá**. El usuario
   commitea a mano.
2. **NUNCA te agregues como co-autor.** Nada de `Co-Authored-By: Claude`,
   `Generated with Claude Code` ni firmas equivalentes en commits, mensajes,
   comentarios de código o documentación. 
3. **PARÁ y explicá antes de escribir cualquier archivo que calcule algo.**Ver el
   protocolo de checkpoint en `docs/reglas.md`.
6. **No agregues dependencias** más allá de las autorizadas en
   `docs/reglas.md` sin preguntar primero.


## Estilo de código

Python 3.11+, sin dependencias externas en `src/` salvo `numpy`,`scipy` y `pillow`

**El código va sin comentarios.** Se explica solo: si un comentario es necesario se agrega a mano

Se comenta sólo una cuenta que no se lee del código, o una regla que si alguien
la borra rompe algo. Los docstrings son de **una línea**. Nada de secciones
"QUÉ REPRESENTA" o "QUÉ SE DESCARTÓ" dentro del código.

El detalle y el porqué del cambio están en `docs/reglas.md`,
regla 8.
