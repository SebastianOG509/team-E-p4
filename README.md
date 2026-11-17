# team-E-p4 — Verificación arquitectónica del Sistema de Transporte Fluvial (FTS)

Entrega 4 de LSSA 2026-II, equipo E. El lenguaje y los modelos de la Entrega 3 se extienden con lo que la verificación necesita (núcleo v2.0 = Laboratorios 4 y 5, más las extensiones `[E]` del equipo), y la arquitectura del FTS se verifica en cuatro iteraciones contra las propiedades derivadas de los escenarios de la Entrega 2. Los resultados, con todos los números, están en [`RESULTS.md`](RESULTS.md).

## Ejecución

Con Docker, desde la carpeta del proyecto:

```
docker build -t lssa-team-e-p4 .
docker run --rm -v "$PWD:/app" lssa-team-e-p4 models/fts-it1.arch                 # una iteración -> out/fts-it1/
docker run --rm -v "$PWD:/app" --entrypoint python lssa-team-e-p4 run_all.py      # todo (unos 3 minutos)
```

En Windows cambia `"$PWD:/app"` por `"%cd%:/app"` (CMD) o `"${PWD}:/app"` (PowerShell).

Sin Docker (Python 3.11 o superior):

```
python3 -m venv .venv
.venv/bin/python -m pip install textX==4.3.0 networkx==3.4.2 matplotlib==3.9.2
.venv/bin/python run_all.py
```

`run_all.py` hace, en orden: (1) comprueba que los modelos de `models/` se aceptan y corresponden con `sos.arch` y que los de `invalid/` se rechazan con el mensaje esperado; (2) comprueba la simulación contra casos de resultado conocido; (3) verifica las cuatro iteraciones; (4) escribe la evolución, (5) la sensibilidad y (6) la fila del FTS para SoS-QS1. La corrida es determinista: las semillas son 1 a 10 en cada punto y dos ejecuciones producen los mismos reportes.

Otros comandos:

| Comando | Qué hace |
|---|---|
| `python verification.py models/fts-it3.arch` | Los cinco pasos del Laboratorio 5 sobre un modelo |
| `python test_invalid.py` | Conformidad: modelos válidos aceptados, inválidos rechazados con su mensaje |
| `python correspondence.py models/sos.arch models/fts-it4.arch` | Chequeo de correspondencia con el modelo conjunto |
| `python checking.py` | Simulación contra casos de resultado conocido |
| `python generation.py` | Transformaciones del Laboratorio 4 sobre todos los modelos de `models/` |
| `python tools/gen_models.py` | Vuelve a escribir los cuatro modelos y `invalid/correspondence.arch` |

## Estructura

| Archivo | Contenido |
|---|---|
| `arch.tx` | Gramática (M2): núcleo v2.0 (Laboratorios 4 y 5) y extensiones del equipo, marcadas `[E]` |
| `metamodel.py` | Restricciones C1–C7 del núcleo (C3 reforzada) y E1–E6 del equipo |
| `correspondence.py` | Chequeo de correspondencia entre `sos.arch` y el modelo del constituyente |
| `simulation.py` | Motor de eventos discretos con la semántica del Laboratorio 5 y las extensiones `[E]` |
| `verification.py` | Grafo por tier, propiedades estructurales S1–S4, simulación y reporte de un modelo |
| `checking.py` | Seis casos de resultado conocido (M/M/1, almacén, prioridad, búfer finito, conmutación, lote) |
| `run_all.py` | Corrida completa: conformidad, comprobación, cuatro iteraciones, evolución, sensibilidad, SoS-QS1 |
| `transformations.py`, `generation.py` | Transformaciones del Laboratorio 4 (tabla de conectores, vista, análisis) y tabla de escenarios y tácticas |
| `models/` | `sos.arch` (conjunto, sin cambios) y `fts-it1.arch` a `fts-it4.arch`, uno por iteración |
| `invalid/` | Un modelo rechazado por cada restricción nueva o cambiada, y `expected-rejections.txt` |
| `tools/` | `gen_models.py` escribe los modelos desde las tablas de la Entrega 2 (`fts_data.json`) y desde `sos.arch` |
| `out/` | Reportes y gráficas generados |

## Reportes generados (`out/`)

| Archivo | Contenido |
|---|---|
| `fts-itN/verification.md` | Propiedades estructurales y, por escenario, propiedad, estimación, IC 95 %, umbral y outcome (nominal y barridos) |
| `fts-itN/graph.png` | Grafo del modelo por tier; borde rojo: elementos introducidos por una táctica |
| `fts-itN/connectors.md`, `view.mmd`, `analysis.md`, `scenarios.md` | Tabla de conectores, vista C&C (Mermaid), análisis analíticos, y escenarios de calidad y tácticas |
| `checking.md` | Comparación de la simulación con seis resultados analíticos |
| `sensitivity.md`, `sensitivity.png` | Sensibilidad a seis parámetros inciertos |
| `evolution.md`, `evolution.png` | Outcome de cada propiedad en las cuatro iteraciones |
| `sos-qs1-fts.md` | Fila bottom-up del FTS para SoS-QS1 (M4) y su sensibilidad a parámetros de otros dueños |

## Modelos

| Modelo | Estructura | Componentes | Conectores | Escenarios simulados |
|---|---|---|---|---|
| `fts-it1.arch` | De partida (Entrega 1 con los parámetros de la Entrega 2) | 19 del FTS + 5 gateways | 46 internos + 15 globales | `Recovery`, `Partition` |
| `fts-it2.arch` | Resultante de la Entrega 2 | 23 + 5 | 69 + 15 | `Recovery`, `Partition` |
| `fts-it3.arch` | Resultante + lo que el escenario B necesita (sondeo, conmutación, retención en el Gateway) | 23 + 5 | 69 + 15 | `Recovery`, `Partition`, `Failover` |
| `fts-it4.arch` | Rediseñada (retención en el emisor; latido cada 8 s) | 23 + 5 | 69 + 15 | `Recovery`, `Partition`, `Failover` |

Los siete escenarios de calidad (E-QS1 a E-QS6 y la contribución a SoS-QS1) están en los cuatro modelos como elementos `quality` con sus seis partes; las tácticas (`tactic`) aparecen desde `fts-it2.arch`.

## Convenciones

- Identificadores: `SoS-K5` se escribe `SoS_K5` y `E-K1`, `E_K1`.
- Los componentes de frontera de los otros constituyentes y los conectores globales se copian de `sos.arch` sin cambios; `correspondence.py` lo comprueba. El FTS solo agrega propiedades de simulación a su propio gateway (`FGW ... store`).
- Latencias en ms, capacidades en trabajos por segundo, tiempos de los escenarios en segundos. Una latencia es un presupuesto o un tiempo de servicio primitivo, nunca una espera en cola: las esperas salen de la simulación.
- Los nombres de los workloads son únicos en un modelo; los del escenario `Failover` llevan el prefijo `F`.
- Los outcome usan los términos del curso: Satisfied with margin (todo el IC ≤ 90 % del umbral), Satisfied without margin (IC ≤ umbral), Inconclusive (el IC contiene el umbral), Violated (IC por encima).
