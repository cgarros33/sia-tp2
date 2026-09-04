# Fase NN — <Título>

> **Ola:** N · **Depende de:** <fases> · **Habilita:** <fases>

---

## 1. Objetivo

<Dos o tres oraciones sobre qué existe cuando esta fase termina y qué se puede
hacer que antes no se podía.>

---

## 2. Archivos que produce

Esta lista es el límite de la fase. No se toca nada que no esté acá.

| Archivo | Qué es |
|---|---|
| `src/...` | <una línea> |

---

## 3. Qué hay que implementar

Una subsección por archivo. Se describe qué tiene que exponer y cómo se tiene
que comportar, no cómo escribirlo: la codificación es del agente.

### `src/ejemplo.py`

<Una o dos oraciones sobre qué responsabilidad tiene este archivo.>

| Función | Recibe | Devuelve | Qué hace |
|---|---|---|---|
| `nombre` | | | <una línea> |

**Comportamiento de `nombre`:**
- <paso a paso, en castellano>

**Invariantes:**
- <lo que tiene que valer siempre, y que se pueda comprobar>

---

## 4. Interfaces de otras fases

Lo que esta fase usa pero no escribe: qué recibe de otros módulos, con qué forma
llega y qué puede asumir sobre eso. Está acá para no depender de otro documento
ni de que la otra fase esté terminada.

<Si no hay dependencias: "Ninguna: esta fase no usa código de otras fases.">

---

## 5. Decisiones ya tomadas

Lo que no se vuelve a discutir en esta fase, con el motivo.

| Decisión | Motivo |
|---|---|
| | |

---

## 6. Decisiones abiertas

<Lo que queda a criterio de quien implementa, o lo que hay que consultar antes de
avanzar. Si no hay ninguna, decirlo.>

---

## 7. Checkpoints obligatorios

Archivos de esta fase que disparan el protocolo de la regla 3 antes de
escribirse:

- `src/...` — porque <qué calcula>

<Si no hay ninguno: "Ninguno: esta fase no produce archivos que calculen.">

---

## 8. Cómo se verifica

Qué entra y qué tiene que salir. Comprobaciones chicas, que se corren a mano.

| # | Qué se prueba | Entrada | Resultado esperado |
|---|---|---|---|
| 1 | | | |

---

## 9. Errores probables

- <error> → <por qué pasa> → <cómo se detecta>

---

## 10. Cierre de la fase

- [ ] Todos los archivos de la sección 2 existen y se importan sin error
- [ ] Todas las verificaciones de la sección 8 pasan
- [ ] `docs/resumenes/FASE_NN_RESUMEN.md` está escrito
- [ ] No se tocó ningún archivo fuera de la lista
- [ ] El agente no commiteó ni pusheó nada
