# RESULTS — Entrega 4, equipo E (FTS): verificación arquitectónica

Insumo para el informe. Todos los números salen de `python run_all.py` y están copiados de `out/` (10 réplicas, semillas 1–10 en cada punto; la corrida es determinista). Los términos de outcome son los del curso: Satisfied with margin, Satisfied without margin, Inconclusive, Violated, Not verifiable.

## 1. Qué se hizo, en una página

| Paso (Lab. 5) | En esta entrega | Archivo |
|---|---|---|
| 1. Abstracción | Lenguaje de la Entrega 3 llevado al núcleo v2.0 (Lab. 4 + Lab. 5) y extendido con 14 construcciones `[E]`; C3 reforzada, C6 y C7 del Lab. 5, E1–E6 del equipo; chequeo de correspondencia con `sos.arch` | `arch.tx`, `metamodel.py`, `correspondence.py` |
| 2. Instanciación | Un modelo por iteración, con escenarios de calidad y tácticas como elementos | `models/fts-it1.arch` … `fts-it4.arch` |
| 3. Grafo | Grafo por tier y cuatro propiedades estructurales | `verification.py`, `out/fts-itN/graph.png` |
| 4. Simulación | Tres escenarios (`Recovery`, `Partition`, `Failover`), 13 medidas | `simulation.py` |
| 5. Reporte | Estimación, IC 95 %, umbral y outcome; evolución, sensibilidad, comprobación y fila de SoS-QS1 | `out/` |

Resultado final (`fts-it4.arch`): las 4 propiedades estructurales y las 13 simuladas quedan satisfechas con margen. En el camino la verificación encontró una violación que la Entrega 2 no vio (36,7 retiros SoS-K28 perdidos durante la conmutación del Traductor) y confirmó que la detección del silencio no tenía margen.

## 2. Lenguaje

### 2.1. Núcleo y extensiones

`arch.tx` declara el núcleo `core v2.0` = Laboratorio 4 (v1.0) + Laboratorio 5 (`capacity`, `store`, `scenario`, `workload`, `fault`, `vary`, `measure`; C6 y C7). Todo lo del equipo está marcado `[E]` y es opcional: `models/sos.arch` (lenguaje base) se acepta sin cambios.

Frente a la Entrega 3 se retiró lo que la simulación reemplaza: la métrica `detection` de los análisis y su atributo `misses` (ahora `misses` es del componente y la detección se simula), y la regla `Group` volvió a la forma del núcleo (`alternatives`, `beta` obligatorio).

| # | Construcción `[E]` | Sintaxis | Semántica en la simulación | Propiedad que la necesita | `arch.tx` |
|---|---|---|---|---|---|
| 1 | Búfer finito del almacén | `store buffer N` | El almacén retiene N trabajos como máximo; el resto se pierde | P2a (E-QS2: 0 posiciones perdidas, reserva ≥ 256 KiB) | 34 |
| 2 | Rol | `role broker` | Ninguna (lo usa E1) | E1, S4 | 35 |
| 3 | Disciplina de cola | `discipline priority` | Cola de prioridad no expulsiva, FIFO dentro de la clase | P1a, S3 (E-QS1: priorizar eventos) | 36 |
| 4 | Señal de vida o sondeo | `period P misses M` | El silencio se declara M periodos después de la última señal; fase aleatoria por réplica. En un almacén, `period` es el sondeo con el que nota que el enlace volvió | P3a (E-QS3), P4 (E-QS6), P2b (E-QS2) | 37–38 |
| 5 | Réplica pasiva | `standby C switch T` | Tras declararse el silencio de C, la réplica atiende su cola T ms después | P3a–P3e (E-QS3) | 39–40 |
| 6 | Escenario de calidad | `quality … attribute source stimulus artifact environment response measure` | Ninguna (trazabilidad; lo usan E5 y S4) | Enunciado §3.1 | 77–86 |
| 7 | Táctica o patrón | `tactic … for Q introduces … changes …` | Ninguna (trazabilidad; borde rojo en el grafo) | Enunciado §3.1 | 90–94 |
| 8 | Lote con limitador | `rate R count N at T retry p` | N trabajos liberados cada 1/R s desde T; cada primer intento necesita con probabilidad p su único reintento, que hace la misma cola del limitador | P5 (SoS-QS1 M4: 40 unidades, ≤ 2 intentos/s, máx. 1 reintento) | 110–111 |
| 9 | Workload disparado | `workload W on C : …` | Un trabajo cuando C se declara en silencio (el aviso que se propaga) | P4 (E-QS6) | 112 |
| 10 | Clase del trabajo | `priority n` | Clase en las colas con `discipline priority` (1 = más urgente) | P1a (E-QS1) | 113 |
| 11 | Conector de cada salto | `via K1, K2, …` | El salto tarda la `latency` del conector (presupuesto primitivo); una falla de conector afecta a los saltos que lo nombran | P1a, P2a, S2 | 115 |
| 12 | Tiempo de otro dueño | `delay D at C for T` | Cada visita a C tarda T ms en este escenario | P5 (respuesta de la frontera NCS ≤ 2 s) | 119–121 |
| 13 | Falla de conector | `fault K down at T for L` | Los saltos por K se caen; silencia al componente con `period` del que sale K | P2a, P2b, P4 (partición de E-K22) | 123–125 |
| 14 | Barrido de un atributo, varios barridos y medidas | `vary X.attr : …`; `p95_latency`, `p999_latency`, `drain`, `completion`, `detection`, `restore`; `of Q`, `as "…"` | Un parámetro a la vez; percentiles como en el Lab. 5; `drain` = fin de la falla → último trabajo retenido entregado; `completion` = inicio del lote → último trabajo; `detection` = última señal válida → aviso entregado; `restore` = falla → servicio restablecido | Todas las P; sensibilidad | 127–148 |

Semántica que se conserva del Laboratorio 5: servidor único por componente con `capacity`, servicio exponencial, llegadas Poisson, componente caído pierde lo que le llega salvo que el anterior en la ruta sea `store`, réplicas con semillas 1..N, IC 95 % con t de Student, y la clasificación con margen de 10 %. El Laboratorio 5 recorre los componentes en orden topológico y eso exige rutas acíclicas; las rutas del FTS pasan dos veces por el Traductor (solicitud y respuesta), así que la misma semántica se ejecuta con un motor de eventos discretos propio (`simulation.py`, 315 líneas, solo biblioteca estándar). Se comprobó contra el caso del Lab. 5 (§6).

### 2.2. Restricciones

| ID | Restricción | Origen | `metamodel.py` | Modelo rechazado (`invalid/`) |
|---|---|---|---|---|
| C1, C2, C4, C5 | Sin cambios | Laboratorio 4 (núcleo) | 29–37, 65–71, 78–83 | — |
| C3 (reforzada, `[E]` propuesta al núcleo) | Todo conector de frontera tiene acuerdo **y todo salto que cruza constituyentes une dos componentes T2** | Retroalimentación de la Entrega 3, punto 2 | 38–47 | `c3-confinement.arch` |
| C6 | Cada salto de un workload sigue un conector, en cualquier sentido | Laboratorio 5 (núcleo v2.0) | 98–101 | `c6-workload.arch` |
| C7 | Un componente que falla tiene `capacity` (`[E]`: también puede fallar un conector) | Laboratorio 5 (núcleo v2.0) | 115–118 | `c7-fault.arch` |
| E1 (antes C6 de la Entrega 3; alcance corregido) | Dentro de un constituyente, un servicio T3 solo recibe `event_notification` de un componente `role broker`, y solo los publica a un broker o a un almacén T4 | Estilo orientado a eventos (Entrega 1, §5.2); retroalimentación, punto 3 | 48–57 | `e1-direct-event.arch`, `e1-publish.arch` |
| E2 (antes C7 de la Entrega 3) | Una `dependency` que sale de T1 termina en un servicio T3 | Estilo cliente-servidor (Entrega 1, §5.3) | 58–62 | `e2-client-server.arch` |
| E3 | Si un workload nombra sus conectores (`via`), hay uno por salto y une sus extremos | Trazabilidad escenario → conectores | 102–110 | `e3-via.arch` |
| E4 | Toda táctica introduce o cambia al menos un elemento | Enunciado §3.1 | 85–88 | `e4-tactic.arch` |
| E5 | Una medida declarada `of Q` observa un workload que atraviesa el artefacto de Q | Enunciado §3.1 | 119–129 | `e5-measure.arch` |
| E6 | Un `standby` tiene capacidad y su primario tiene `capacity`, `period` y `misses`; un workload `on C` exige `period` y `misses` en C | E-QS3, E-QS6 | 72–76, 111–114 | `e6-standby.arch` |
| Por referencia tipada | El artefacto de un escenario, el escenario de una táctica y lo que una táctica introduce existen en el modelo | Enunciado §3.1 | (gramática) | `q-artifact.arch`, `q-tactic-scenario.arch`, `q-tactic-element.arch` |
| Correspondencia | Ver §2.3 | Enunciado §3.1 | `correspondence.py` | `correspondence.arch` |

`python test_invalid.py` comprueba los 5 modelos válidos y los 14 inválidos contra `invalid/expected-rejections.txt`; pasa completo. Se retiraron `c5-period.arch` y `c5-misses.arch`, que probaban la métrica `detection` eliminada.

### 2.3. Chequeo de correspondencia (`correspondence.py`)

El constituyente de un modelo es el que lleva el nombre de su sistema (`system FTS`). El programa falla, con un mensaje por divergencia, si no se cumple:

1. Los constituyentes del modelo están en `sos.arch` con la misma etiqueta y dueño.
2. Todo componente de frontera de `sos.arch` que el modelo declara tiene la misma etiqueta, constituyente, tier, kind, `availability` y `latency`. Un componente de otro constituyente debe existir en `sos.arch` y no puede recibir propiedades de simulación; el dueño sí puede agregarlas a su propio gateway (`FGW … store` desde it3).
3. Todos los conectores globales de `sos.arch` en los que participa el constituyente están en el modelo (los 13 del FTS), y todo conector global del modelo coincide en extremos, naturaleza, acoplamiento, `carries`, `agreement`, `availability` y `latency`.
4. Un conector del modelo que cruza constituyentes es un conector global de `sos.arch`.

Los cuatro modelos corresponden. Caso inválido: `invalid/correspondence.arch` → `SoS_K19a: agreement is 'Contrato de estado consolidado (sin tasa)', but sos.arch says 'Contrato de estado consolidado; regla de acceso y tasa P7'`. `verification.py` ejecuta este chequeo antes de simular y aborta si hay divergencia. `models/sos.arch` no se modificó.

## 3. Correcciones a la retroalimentación de la Entrega 3

| Punto del profesor | Qué se corrigió | Dónde |
|---|---|---|
| 1. Extensión gramatical insuficiente; tiempos precalculados a mano | El lenguaje tiene ahora capacidad, tasa de arribo, almacén y búfer finito. Se eliminaron las tres constantes: la espera FIFO del Traductor (E-K26 = 1.660 ms), la cola de la respuesta (E-K33 = 5.200 ms; y los 40.000 ms de E-K32, que eran 80 intentos ÷ 2/s) y el vaciado del rezago (E-K58 = 18.000 ms). Ahora emergen: la espera, de `TRA capacity 100` y las tasas de los workloads; el tiempo de consultas, del limitador `rate 2 count 40 retry 1`; el vaciado, de `BUF capacity 50 store` con la partición de 1.800 s. También se eliminó la detección de reconexión (E-K22 = 10.000 ms), que sale del sondeo `BUF period` | `arch.tx:32–34, 107–115`; `simulation.py:157–232`; conectores sin `latency`: `models/fts-it1.arch:188, 207, 210` (E-K26, E-K32, E-K33) y `models/fts-it2.arch:180, 192, 212, 215, 291` (E-K22, E-K26, E-K32, E-K33, E-K58); parámetros primitivos en `tools/gen_models.py:43–65` |
| 2. Falta confinamiento de frontera en T2 | C3 exige además que los dos extremos de todo salto que cruza constituyentes sean T2 | `metamodel.py:43–47`; `invalid/c3-confinement.arch` |
| 3. Alcance de la restricción de estilo orientado a eventos | E1 ya no mira solo los eventos que nacen en T3: todo `event_notification` interno que llega a un servicio T3 debe venir de un broker. Los dos conectores que la violaban se reclasificaron (tabla siguiente) | `metamodel.py:48–57`; `tools/gen_models.py:37–41`; `invalid/e1-direct-event.arch` |

Revisión de los 17 conectores `event_notification` internos frente a E1 (estructura resultante):

| Conector | Origen → destino | Antes | Ahora | Por qué |
|---|---|---|---|---|
| E-K19 | Terminal de Muelle (T1) → Custodia (T3) | `event_notification`, sink | **`data_flow`**, sink | No es una publicación a suscriptores desconocidos: el Terminal entrega el registro del traspaso al único servicio que lo valida y lo persiste. El evento nace cuando Custodia publica al Broker (E-K21). Es el mismo patrón de E-K5, E-K17 y E-K20 (registros, `data_flow` sink) |
| E-K38 | App del Capitán (T1) → Seguimiento (T3) | `event_notification`, sink | **`data_flow`**, sink | Reporte punto a punto que Seguimiento registra; las novedades se publican después al Broker por E-K25, que ya las transporta |
| E-K21, E-K25, E-K48, E-K69 | T3 o T2 → Broker | — | Sin cambio | Publican al broker |
| E-K49, E-K50, E-K51 | Broker → Turnos, Programación, Consulta (T3) | — | Sin cambio | El origen es el broker |
| E-K26, E-K27, E-K28, E-K29, E-K47 | Entre T2, o Broker → Panel (T1) | — | Sin cambio | El destino no es un servicio T3 |
| E-K66, E-K67, E-K68 | Gateway, Custodia, Turnos → Auditoría (T4) | — | Sin cambio | El destino es un almacén T4 |

No hizo falta enrutar ninguno por el broker: en los dos casos el emisor conoce a su único receptor y este ya republica por el broker. La reclasificación vale desde `fts-it1.arch`, porque el modelo de partida no carga sin ella. El acoplamiento (sink) no cambió, así que S2 no se ve afectada.

## 4. Parámetros

Solo quedan en los modelos parámetros primitivos de la Entrega 2. Ninguno es una espera en cola.

| Parámetro | Valor | Fuente | En el modelo |
|---|---|---|---|
| Capacidad del Traductor (y del standby) | 100 operaciones/s | A1 | `TRA capacity 100`, `TRS capacity 100` |
| Custodia; posiciones; SoS-K4; SoS-K28; SoS-K31 | 10; 5; 10; 5; 5 por segundo | H1 | workloads `Custody`, `Positions`, `K4`, `K28`, `K31` (K4, K28 y K31 pasan dos veces por el Traductor: 109 op/s con el rezago y la reconciliación, como en la Entrega 2 §8) |
| Rezago de posiciones | 900 posiciones a 50/s | H2, H3 | `Backlog rate 50 count 900` (escenarios A y B); en `Partition` emerge de la falla y de `BUF capacity 50` |
| Reconciliación | 40 unidades, 2 intentos/s, 1 reintento por consulta (peor caso) | H4, P7 | `Reconcile rate 2 count 40 retry 1` |
| Respuesta de la frontera NCS | 2 s | H4 (otro dueño) | `delay NcsResponse at NCG for 2000` |
| Partición del enlace río–tierra | 1.800 s, 5 convoyes (0,5 posiciones/s) | H2 | `fault E_K22` y `fault E_K58 … for 1800`; `Affected rate 0.5` |
| Reserva a bordo | 256 KiB × 5 convoyes ÷ 1 KiB = 1.280 posiciones | H2 | `BUF store buffer 1280` |
| Latido y ausencias | 10 s, 3 (8 s en it4) | E-QS6 | `UAB period 10000 misses 3`; `BUF period` igual (reintenta con cada latido) |
| Sondeo de salud, ausencias, conmutación | 2 s, 3, 2 s | A3 | `TRA period 2000 misses 3`; `TRS standby TRA switch 2000` |
| Falla de la instancia | 300 s (recuperación manual si no hay standby) | Elegido | `fault TRA down at 600 for 300` |
| Disponibilidad de una instancia; β | 99,5 %; 0,10 | A4 | `availability 99.5`; `beta 0.10` |
| Corridas | `Recovery`: 150 s, calentamiento 60 s (la ventana medida son los 90 s posteriores a «restablecido»); `Partition`: 2.100 s; `Failover`: 3.600 s (ventana de 60 min de E-QS3); 10 réplicas | Elegido | `run … warmup … replications 10` |

Latencias que quedan (ms) y qué son:

| Elemento | it1 | it2–it4 | Qué es |
|---|---|---|---|
| E-K19, E-K21, E-K27 | 10 | 30 | Proceso de la etapa (10 ms, el mismo orden de A1) y, desde it2, escritura durable (20 ms, A2) |
| E-K55 | — | 20 | Escritura durable en la Cola Persistente (A2) |
| E-K59 | — | 2.000 | Presupuesto de persistencia y acuse duradero (E-QS2) |
| E-K29 | — | 5.000 | Presupuesto de propagación del aviso de vigencia Seguimiento → Panel (E-QS6), puesto en el último salto |
| CON | 30.000 | 30.000 | Presupuesto para aplicar los resultados de la reconciliación (Entrega 2 §5.2); no se simula |
| CGW, RGW, NCG, SoS-K5, SoS-K32 | — | — | Presupuestos de M4 copiados de `sos.arch` |

## 5. Propiedades

| ID | Propiedad | Escenario | Atributo | Clase | Técnica | Umbral |
|---|---|---|---|---|---|---|
| S1 | Sin punto único de falla en la cadena de traducción | E-QS3 | Disponibilidad | Estructural | Análisis del grafo (Lab. 5) | Ningún factor simple |
| S2 | Sin conector blocking en la cadena de custodia (conectores `via` del workload de clase 1) | E-QS1 | Rendimiento | Estructural | Análisis del grafo | Ninguno |
| S3 | Todo servidor que la cadena de custodia comparte con intercambios blocking atiende por prioridad | E-QS1 | Rendimiento | Estructural | Análisis del grafo | Ninguno |
| S4 | El aviso SoS-K35 alcanza, como eventos y por el broker, a los servicios del artefacto de SoS-QS1 | SoS-QS1 | Resiliencia | Estructural (alcanzabilidad) | Análisis del grafo | Todos alcanzables |
| P1a | p95 de la latencia de custodia E-K19 → E-K27 bajo la carga de recuperación (109 op/s) | E-QS1 | Rendimiento | Respuesta acotada | Simulación (`Recovery`) | ≤ 30 s |
| P1b | Eventos de custodia perdidos durante la falla del Traductor | E-QS1 | Rendimiento / confiabilidad | Seguridad (safety) | Simulación (`Failover`) | 0 |
| P2a | Posiciones perdidas en la partición de 1.800 s | E-QS2 | Confiabilidad (resiliencia) | Seguridad (safety) | Simulación (`Partition`) | 0 |
| P2b | Persistencia de todo el rezago tras reconectar | E-QS2 | Confiabilidad (recuperabilidad) | Respuesta acotada | Simulación (`Partition`) | ≤ 60 s |
| P2c | p95 de posiciones nuevas hasta el Gateway durante la recuperación | E-QS2 | Rendimiento | Respuesta acotada | Simulación (`Recovery`) | ≤ 15 s |
| P3a | Traducción restablecida desde la falla | E-QS3 | Disponibilidad | Respuesta acotada | Simulación (`Failover`) | ≤ 10 s |
| P3b, P3c | ≥ 99,9 % de las operaciones SoS-K4 y SoS-K28 completan su tramo local (percentil 99,9) | E-QS3 | Disponibilidad | Respuesta acotada | Simulación (`Failover`) | ≤ 15 s |
| P3d, P3e | Operaciones SoS-K4 y SoS-K28 aceptadas perdidas | E-QS3 | Disponibilidad | Seguridad (safety) | Simulación (`Failover`) | 0 |
| P3f | p95 del turno SoS-K4 sin falla, bajo la carga de recuperación (efecto lateral de las tácticas de E-QS1) | E-QS3 | Rendimiento | Respuesta acotada | Simulación (`Recovery`) | ≤ 5 s |
| P4 | Estado «no vigente» visible en el Panel desde el último latido válido | E-QS6 | Confiabilidad (tolerancia a fallos) | Respuesta acotada | Simulación (`Partition`); resultado determinista | ≤ 35 s |
| P5 | Contribución a SoS-QS1 (M4): consultas y reintentos de la reconciliación local | SoS-QS1, E-QS1 | Resiliencia | Respuesta acotada | Simulación (`Recovery`) | ≤ 270 s (+ 30 s de presupuesto para aplicar = 300 s) |

Atributos distintos verificados por simulación: rendimiento (P1a, P2c, P3f), confiabilidad (P2a, P2b, P4), disponibilidad (P3a–P3e) y resiliencia del todo (P5). La disponibilidad anual de la traducción (99,5 % → 99,948 % con β = 0,10) sigue siendo analítica (`out/fts-itN/analysis.md`), como en el Laboratorio 4.

### No verificables con este modelo

| Escenario o medida | Por qué | Qué haría falta |
|---|---|---|
| E-QS4 (seguridad): 0 falsificaciones aceptadas, rechazo p95 ≤ 2 s | El metamodelo no tiene atacante, identidad, firma ni frontera de confianza. El escenario y su táctica están en el modelo solo como elementos trazables | Modelo de amenazas con fronteras de confianza; model checking del protocolo de verificación y correlación; ensayo adversarial |
| E-QS5 (evolutividad): ≤ 16 horas-persona, 1 componente | Atributo de tiempo de diseño: no hay entidades canónicas por conector ni esfuerzo | Entidades del modelo canónico como elementos y análisis de impacto de cambio sobre el grafo de dependencias |
| 0 duplicados lógicos (E-QS2) y 0 efectos duplicados (E-QS3) | Un trabajo no tiene identidad ni puede reenviarse dos veces; la deduplicación es comportamiento | Modelo de comportamiento (entrega al menos una vez + receptor idempotente) y model checking |
| Falsas alarmas de desconexión (E-QS6) | No se modela la pérdida de latidos; es un evento raro (≈ 10⁻⁶ por ventana) que 10 réplicas no estiman | Probabilidad de pérdida en el conector y simulación de eventos raros o modelo analítico. Cifra analítica de la Entrega 2: 0,018/h con latido de 10 s; con 8 s, 0,0225/h |
| Restablecer la vigencia en ≤ 15 s y 0 latidos históricos aceptados como actuales (E-QS6) | No se simuló el retorno de la señal ni la edad de un mensaje | Medida de recuperación de la vigencia; edad del dato como concepto |
| 100 % de registros conservan la hora de captura; reserva en KiB | Los trabajos no llevan datos; la reserva se modela en posiciones suponiendo 1 KiB por posición | Atributos de datos en los trabajos |
| p95 ≤ 5 s por ruta **incluyendo la transición** (E-QS3) | Se midió el percentil 99,9 con falla y el p95 sin falla (P3f); el p95 de 60 min con una falla de segundos no cambia (≈ 0,5 % de las operaciones afectadas) | Bastaría agregar la medida; no se agregó |
| SoS-QS1 M1 (0 cancelaciones, regla P5) | Regla de negocio, no estructura ni tiempo | Modelo de la política de despacho |
| SoS-QS1 M2 (error de ETA) y M3 (peaje ≤ 60 s) | Dependen del estimador de Coordinación Nacional y de Carretera; el FTS no participa | Verificación de sus dueños |
| Respuesta de la frontera NCS ≤ 2 s por consulta | Es un parámetro de otro dueño; entra como supuesto (`delay`) y se reporta su sensibilidad | Medida verificada de Coordinación Nacional |

## 6. Comprobación de la simulación (`out/checking.md`)

Modelos mínimos en el mismo lenguaje y con el mismo motor. Los 13 valores analíticos caen dentro de su IC 95 %.

| Caso | Semántica | Punto | Analítico | Simulado | IC 95 % | Dentro |
|---|---|---|---|---|---|---|
| M/M/1, p99 = ln(100)/(µ − λ), µ = 100/s | Núcleo | λ = 50/s | 92,10 ms | 91,75 | [89,85; 93,64] | Sí |
| | | λ = 80/s | 230,26 ms | 224,57 | [205,36; 243,78] | Sí |
| | | λ = 90/s | 460,52 ms | 457,59 | [406,59; 508,59] | Sí |
| Almacén ante una caída de 600 s (Lab. 5 §4.5 a un décimo de sus tasas): recuperación = λ·600/(µ − λ) | Núcleo | λ = 40, µ = 120 | 300,00 s | 299,02 | [296,37; 301,68] | Sí |
| | | perdidos | 0 | 0 | [0; 0] | Sí |
| Prioridad no expulsiva de dos clases (Cobham), λ = 10 y 70/s, µ = 100/s: latencia media | `discipline priority` | clase alta | 18,89 ms | 18,90 | [18,75; 19,05] | Sí |
| | | clase baja | 54,44 ms | 53,49 | [51,79; 55,18] | Sí |
| Almacén finito de 880 con 900 llegadas Poisson esperadas: E[(A − 880)⁺] | `store buffer` | perdidos | 24,50 | 22,50 | [9,58; 35,42] | Sí |
| Detección y conmutación: sondeo 2 s, 3 ausencias, conmutación 2 s | `period`, `misses`, `standby` | detección = 3 × 2 | 6,00 s | 6,00 | [6,00; 6,00] | Sí |
| | | restablecimiento = 2,5 × 2 + 2 | 7,00 s | 7,12 | [6,73; 7,51] | Sí |
| | | perdidos | 0 | 0 | [0; 0] | Sí |
| Lote de 40 consultas a 2/s con respuesta de 2 s: (N(1 + p) − 1)/r + d | `count`, `retry`, `delay` | p = 1 | 41,50 s | 41,50 | [41,50; 41,50] | Sí |
| | | p = 0 | 21,50 s | 21,50 | [21,50; 21,50] | Sí |

La comprobación sirvió: en su primera corrida el caso del almacén dio 30,4 s en vez de 300 s y descubrió un error en la medida `recovery` (contaba como recuperado el primer trabajo liberado por el almacén). Se corrigió antes de aceptar ningún resultado; `recovery` no la usa ninguna propiedad del FTS.

## 7. Iteraciones

### Iteración 1 — estructura de partida, escenario A (E-QS1)

Modelo: `models/fts-it1.arch` (19 componentes del FTS, 46 conectores internos). Cambios frente a `fts-e1.arch` de la Entrega 3: E-K19 y E-K38 reclasificados (E1); `TRA capacity 100`; se quitaron las latencias precalculadas; se agregaron los 7 escenarios de calidad y los escenarios de simulación `Recovery` y `Partition`. Grafo: `out/fts-it1/graph.png`.

| Propiedad | Estimación | IC 95 % | Umbral | Outcome |
|---|---|---|---|---|
| S1 sin punto único de falla | TRA | — | — | Violated |
| S2 sin blocking en la cadena de custodia | Ninguno | — | — | Satisfied |
| S3 servidor compartido atiende por prioridad | TRA | — | — | Violated |
| S4 el aviso SoS-K35 alcanza a los servicios | CON | — | — | Violated |
| P1a custodia p95 | 1,169 s | [0,884; 1,454] | ≤ 30 s | Satisfied with margin |
| P2c posiciones nuevas p95 | 1,158 s | [0,841; 1,475] | ≤ 15 s | Satisfied with margin |
| P3f turno K4 p95 (sin falla) | 2,277 s | [1,623; 2,932] | ≤ 5 s | Satisfied with margin |
| P5 reconciliación (consultas) | 41,526 s | [41,513; 41,539] | ≤ 270 s | Satisfied with margin |
| P2a posiciones perdidas | 898,1 | [879,8; 916,4] | 0 | Violated |
| P2b persistencia del rezago | 0,000 s | [0; 0] | ≤ 60 s | Satisfied with margin (no hay rezago: se perdió) |
| P4 detección del silencio | 2.000 s (sin cota: fin de la corrida) | — | ≤ 35 s | Violated |

Lectura. La propiedad del escenario A se cumple con margen en la estructura de partida: con A1 = 100 op/s la cola FIFO del Traductor crece durante los 18 s del rezago y el p95 de custodia queda en 1,17 s, 25 veces por debajo del umbral. La Entrega 2 había estimado ≈ 1,7 s a mano (la espera máxima, no el p95 de la ventana); la simulación lo confirma en orden de magnitud. Lo que la estructura no tiene es aislamiento (S3) ni margen frente a A1 para las operaciones (ver §8: P3f es inconclusa con 90 op/s y violada con 80). P2b es un caso de «una medida satisfecha esconde una violada»: no hay rezago que persistir porque las 898 posiciones se perdieron.

Decisión: aplicar las tácticas de la Entrega 2. Para E-QS1 no las justifica el umbral de custodia sino el aislamiento frente a la carga compartida (S3) y la sensibilidad a A1; para E-QS2, E-QS3 y E-QS6 las justifican P2a, S1 y P4.

### Iteración 2 — estructura resultante, escenario A de nuevo y efectos laterales

Modelo: `models/fts-it2.arch` (23 componentes, 69 conectores internos). Cambios: los 4 elementos y 23 conectores de la Entrega 2; `TRA discipline priority`; `BRO store` (durable por la Cola Persistente) y las rutas de eventos pasan por `COL` (E-K55, E-K56); `BUF capacity 50 store buffer 1280 period 10000`; `UAB period 10000 misses 3`; las 7 tácticas como elementos. Clases: 1 custodia; 2 posiciones nuevas y operaciones K4, K28 y K31; 3 rezago y reconciliación. Grafo: `out/fts-it2/graph.png`.

| Propiedad | Estimación | IC 95 % | Umbral | Outcome | Frente a it1 |
|---|---|---|---|---|---|
| S1, S2, S3, S4 | Ninguno | — | — | Satisfied | S1, S3 y S4 pasan de Violated a Satisfied |
| P1a custodia p95 | 0,157 s | [0,155; 0,159] | ≤ 30 s | Satisfied with margin | 7,4 veces menor |
| P2c posiciones nuevas p95 | 0,100 s | [0,094; 0,106] | ≤ 15 s | Satisfied with margin | 11,6 veces menor |
| P3f turno K4 p95 (sin falla) | 0,143 s | [0,134; 0,152] | ≤ 5 s | Satisfied with margin | 15,9 veces menor |
| P5 reconciliación (consultas) | 41,598 s | [41,467; 41,728] | ≤ 270 s | Satisfied with margin | + 0,07 s |
| P2a posiciones perdidas | 0,0 | [0; 0] | 0 | Satisfied with margin | De 898 a 0 |
| P2b persistencia del rezago | 20,982 s | [19,860; 22,104] | ≤ 60 s | Satisfied with margin | Ahora hay rezago y se persiste |
| P4 detección del silencio | 35,000 s | [35,000; 35,000] | ≤ 35 s | Satisfied without margin | De sin cota a 35 s |

Lectura. Las tácticas entregan lo que la Entrega 2 esperaba donde se aplicaron: custodia p95 0,157 s (Entrega 2: ≤ 0,2 s; cálculo 0,15 s), 0 posiciones perdidas, rezago persistido en 21,0 s (Entrega 2: 30 s, que tomaba el peor caso de 10 s para detectar la reconexión; en la simulación el sondeo espera en promedio 5 s, el vaciado de 18 s emerge de los 50/s del búfer y se suman 2 s de acuse). Efectos laterales: la prioridad también mejora a las clases 2 (posiciones nuevas y turnos), porque el rezago pasa a la clase 3; quien paga es la clase 3: sin reintentos, la reconciliación tarda 23,8 s [22,8; 24,7] en it2 frente a 22,3 s [21,9; 22,8] en it1 (barrido `Reconcile.retry = 0` de `out/fts-itN/verification.md`), y con el Traductor a 60 op/s sube a 118,8 s [117,1; 120,6] frente a 65,9 s [64,0; 67,8] en it1, todavía dentro de 270 s. P4 queda exactamente en el umbral: el resultado es determinista (3 × 10 s + 5 s de presupuesto de propagación; en la ruta Seguimiento → Broker → Panel no hay cola) y coincide con el «margen 0» de las Entregas 2 y 3.

Decisión: se conserva la estructura resultante; P4 pasa a la iteración 4 por no tener margen; el escenario B se elige para E-QS3, donde la Entrega 2 afirmó «0 operaciones perdidas» con un cálculo que no recorre las rutas.

### Iteración 3 — estructura resultante, escenario B (E-QS3, disponibilidad)

Modelo: `models/fts-it3.arch` = it2 más lo que el escenario B necesita y la Entrega 2 solo tenía en prosa (A3 y §8.1.3): `TRA period 2000 misses 3` (sondeo E-K62), `TRS capacity 100 standby TRA switch 2000`, `FGW store` («el Gateway retiene lo que llega») y el escenario `Failover`: una instancia cae 300 s en t = 600 s, bajo H1 y con el rezago H3 coincidiendo con la falla, en una ventana de 60 min. Grafo: `out/fts-it3/graph.png`. Las demás propiedades no cambian frente a it2.

| Propiedad | Estimación | IC 95 % | Umbral | Outcome |
|---|---|---|---|---|
| P3a traducción restablecida | 6,983 s | [6,516; 7,450] | ≤ 10 s | Satisfied with margin |
| P3b turno K4, percentil 99,9 | 6,579 s | [6,030; 7,127] | ≤ 15 s | Satisfied with margin |
| P3c retiro K28, percentil 99,9 | 1,830 s | [1,417; 2,242] | ≤ 15 s | Satisfied with margin (sobre las que no se perdieron) |
| P3d turnos K4 perdidos | 0,0 | [0; 0] | 0 | Satisfied with margin |
| **P3e retiros K28 perdidos** | **36,7** | **[32,1; 41,3]** | **0** | **Violated** |
| P1b custodia perdida | 0,0 | [0; 0] | 0 | Satisfied with margin |

Lectura. La conmutación funciona: 6,98 s en promedio (la Entrega 2 dio 8 s, que es el máximo: 3 sondeos × 2 s + 2 s; el instante de la falla cae al azar dentro del periodo de sondeo, así que la detección está entre 4 y 6 s). La custodia no se pierde (la retiene el Broker con la Cola Persistente) y los turnos SoS-K4 tampoco (los retiene el Gateway). **Pero se pierden 36,7 solicitudes de retiro SoS-K28 por falla**, y eso contradice la Entrega 2 §8.1.3, que contaba «20 transacciones/s × 8 s = 160 solicitudes» retenidas por el Gateway: las solicitudes de retiro no entran por el Gateway, nacen en el Servicio de Turnos y van directo al Traductor (E-K39), y Turnos no retiene nada (la Entrega 2 §8.2 le da un timeout de 0,3 s con 1 reintento, 0,6 s frente a 7–8 s de conmutación). 5 solicitudes/s × 7 s ≈ 35, que es lo que la simulación encuentra. El mismo hueco existe para todo lo que nace dentro y va al Traductor: el retorno de SoS-K4 y SoS-K31 (Turnos y Programación → Traductor), las solicitudes de atraque (E-K8) y las consultas de reconciliación (E-K31). P3c es otra medida satisfecha que esconde una violada: su percentil se calcula sobre las solicitudes que sobrevivieron.

Decisión: la redundancia primary-standby no basta sin retención en todos los emisores del Traductor; se rediseña en la iteración 4.

### Iteración 4 — estructura rediseñada, todas las propiedades

Modelo: `models/fts-it4.arch`. Dos cambios, cada uno como táctica enlazada a su escenario (`models/fts-it4.arch:414–417`):

| Táctica | Para | Cambia | Motivo (iteración) | En el modelo |
|---|---|---|---|---|
| `CallerRetention`: retención y reintento idempotente en el emisor mientras el Traductor conmuta | E-QS3 | Turnos, Programación, Consulta | P3e Violated (it3) | `TUR store`, `PRO store`, `CON store` (líneas 25, 26 y 29). Reemplaza el timeout de 0,3 s con 1 reintento por reintentos con el mismo id hasta el plazo de la operación (15 s) |
| `FasterHeartbeat`: latido cada 8 s | E-QS6 | Unidad a Bordo, Búfer, E-K22 | P4 Satisfied without margin (it2, it3) | `UAB period 8000 misses 3`, `BUF … period 8000` (líneas 36 y 41). El valor sale del barrido de it2: 8 s es el periodo más largo de los probados que deja margen |

No se agregan componentes ni conectores. Grafo: `out/fts-it4/graph.png`.

| Propiedad | Estimación | IC 95 % | Umbral | Outcome | Frente a it3 |
|---|---|---|---|---|---|
| S1, S2, S3, S4 | Ninguno | — | — | Satisfied | Igual |
| P1a custodia p95 | 0,157 s | [0,155; 0,159] | ≤ 30 s | Satisfied with margin | Igual |
| P1b custodia perdida | 0,0 | [0; 0] | 0 | Satisfied with margin | Igual |
| P2a posiciones perdidas | 0,0 | [0; 0] | 0 | Satisfied with margin | Igual |
| P2b persistencia del rezago | 20,850 s | [19,948; 21,751] | ≤ 60 s | Satisfied with margin | − 0,13 s (sondeo cada 8 s) |
| P2c posiciones nuevas p95 | 0,100 s | [0,094; 0,106] | ≤ 15 s | Satisfied with margin | Igual |
| P3a traducción restablecida | 6,983 s | [6,516; 7,450] | ≤ 10 s | Satisfied with margin | Igual |
| P3b turno K4, percentil 99,9 | 7,289 s | [6,702; 7,876] | ≤ 15 s | Satisfied with margin | + 0,71 s |
| P3c retiro K28, percentil 99,9 | 7,763 s | [7,025; 8,502] | ≤ 15 s | Satisfied with margin | + 5,93 s |
| P3d turnos K4 perdidos | 0,0 | [0; 0] | 0 | Satisfied with margin | Igual |
| P3e retiros K28 perdidos | 0,0 | [0; 0] | 0 | Satisfied with margin | De 36,7 a 0 |
| P3f turno K4 p95 (sin falla) | 0,143 s | [0,134; 0,152] | ≤ 5 s | Satisfied with margin | Igual |
| P4 detección del silencio | 29,000 s | [29,000; 29,000] | ≤ 35 s | Satisfied with margin | De 35 a 29 s |
| P5 reconciliación (consultas) | 41,598 s | [41,467; 41,728] | ≤ 270 s | Satisfied with margin | Igual |

Lectura y costos. La retención en el emisor cambia pérdida por espera: los retiros ya no se pierden y su percentil 99,9 sube de 1,8 a 7,8 s, y el de los turnos de 6,6 a 7,3 s porque los retiros retenidos entran a la misma cola al restablecerse el servicio; los dos siguen por debajo de 13,5 s (90 % del umbral). El latido de 8 s da 6 s de margen a la detección y cuesta 25 % más latidos (6,25/s en vez de 5/s para 50 convoyes) y, según la fórmula de la Entrega 2, más falsas alarmas esperadas (0,0225/h frente a 0,018/h; analítico, no simulado). La otra salida, exigir 4 ausencias con latido de 6 s (24 s + 5 s = 29 s, y ≈ 0,0003 falsas alarmas/h), duplica casi el tráfico de latidos; queda como alternativa si las falsas alarmas resultan molestas en operación.

Decisión: se adopta `fts-it4.arch` como arquitectura verificada del FTS.

## 8. Sensibilidad (`out/sensitivity.md`, `out/sensitivity.png`)

Un parámetro a la vez, mismas semillas en todos los puntos.

**Capacidad del Traductor (A1, incierta; la Entrega 2 §8.3 pide medirla).** Estimación en segundos [IC 95 %]:

| op/s | P1a custodia, it1 | P1a, it2 | P3f turno K4, it1 | P3f, it2 | P2c posiciones, it1 | P2c, it2 |
|---|---|---|---|---|---|---|
| 50 | 25,671 [24,611; 26,732] with margin | 0,221 [0,216; 0,225] | 49,571 **Violated** | 22,428 **Violated** | 25,684 **Violated** | 11,609 [10,405; 12,813] with margin |
| 60 | 11,494 [10,897; 12,092] | 0,198 | 21,730 **Violated** | 1,258 [0,920; 1,595] | 11,486 | 0,675 |
| 70 | 7,579 [7,150; 8,008] | 0,183 | 14,209 **Violated** | 0,460 | 7,543 | 0,266 |
| 80 | 4,641 [4,306; 4,976] | 0,171 | 9,022 [8,473; 9,572] **Violated** | 0,282 | 4,636 | 0,169 |
| 90 | 2,659 [2,329; 2,990] | 0,163 | 5,171 [4,557; 5,785] **Inconclusive** | 0,189 | 2,656 | 0,119 |
| 100 (nominal) | 1,169 [0,884; 1,454] | 0,157 | 2,277 [1,623; 2,932] | 0,143 | 1,158 | 0,100 |
| 120 | 0,146 | 0,147 | 0,237 | 0,095 | 0,115 | 0,072 |

(Sin etiqueta: Satisfied with margin.) Conclusiones: (1) la custodia nunca viola 30 s en el rango probado, ni siquiera en la estructura de partida con 50 op/s (25,7 s; la Entrega 2 había calculado 21 s para ese caso); (2) la propiedad sensible a A1 en la estructura de partida es el turno SoS-K4 (p95 ≤ 5 s): con 10 % menos de capacidad queda inconclusa y con 20 % menos, violada; (3) con prioridad (it2 en adelante) la custodia es insensible a A1 (0,15–0,22 s) y los turnos aguantan hasta 60 op/s; con 50 op/s, por debajo de las 55 op/s de las clases 1 y 2, la clase 2 se queda sin servicio y P3f se viola: la prioridad protege la custodia, no reemplaza la capacidad.

**Periodo del latido (E-QS6).** P4 en it2: 6 s → 23 s (with margin); 8 s → 29 s (with margin); 9 s → 32 s (without margin); 10 s → 35 s (without margin); 12 s → 41 s (Violated). Es lineal (3 × periodo + 5 s) y determinista; de aquí sale el periodo de 8 s de la iteración 4.

**Reserva del búfer a bordo (E-QS2).** P2a en it2: 600 posiciones → 301,3 perdidas [283,5; 319,1] (Violated); 900 → 10,7 [2,9; 18,5] (Violated); 1.280 → 0 (Satisfied with margin). Una reserva igual al rezago esperado (900 = 180 KiB por convoy) no basta cuando las llegadas varían; los 256 KiB de H2 dan 42 % de holgura.

**Parámetros de otros dueños sobre P5** (modelo final): ver §10.

## 9. Evolución (`out/evolution.md`, `out/evolution.png`)

| Propiedad | it1 | it2 | it3 | it4 |
|---|---|---|---|---|
| S1 sin punto único de falla (E-QS3) | Violated (TRA) | Satisfied | Satisfied | Satisfied |
| S2 sin blocking en custodia (E-QS1) | Satisfied | Satisfied | Satisfied | Satisfied |
| S3 servidor compartido con prioridad (E-QS1) | Violated (TRA) | Satisfied | Satisfied | Satisfied |
| S4 aviso SoS-K35 alcanza a los servicios (SoS-QS1) | Violated (CON) | Satisfied | Satisfied | Satisfied |
| P1a custodia p95 ≤ 30 s | 1,169 [0,884; 1,454] — with margin | 0,157 [0,155; 0,159] — with margin | 0,157 — with margin | 0,157 — with margin |
| P2c posiciones nuevas p95 ≤ 15 s | 1,158 [0,841; 1,475] — with margin | 0,100 [0,094; 0,106] — with margin | 0,100 — with margin | 0,100 — with margin |
| P3f turno K4 p95 sin falla ≤ 5 s | 2,277 [1,623; 2,932] — with margin | 0,143 [0,134; 0,152] — with margin | 0,143 — with margin | 0,143 — with margin |
| P5 reconciliación (consultas) ≤ 270 s | 41,526 [41,513; 41,539] — with margin | 41,598 [41,467; 41,728] — with margin | 41,598 — with margin | 41,598 — with margin |
| P2a posiciones perdidas = 0 | 898,1 [879,8; 916,4] — **Violated** | 0 — with margin | 0 — with margin | 0 — with margin |
| P2b persistencia del rezago ≤ 60 s | 0 (sin rezago) — with margin | 20,982 [19,860; 22,104] — with margin | 20,982 — with margin | 20,850 [19,948; 21,751] — with margin |
| P4 detección del silencio ≤ 35 s | sin cota — **Violated** | 35,000 — **without margin** | 35,000 — **without margin** | 29,000 — with margin |
| P3a traducción restablecida ≤ 10 s | No evaluada | No evaluada | 6,983 [6,516; 7,450] — with margin | 6,983 — with margin |
| P3b turno K4 percentil 99,9 ≤ 15 s | No evaluada | No evaluada | 6,579 [6,030; 7,127] — with margin | 7,289 [6,702; 7,876] — with margin |
| P3c retiro K28 percentil 99,9 ≤ 15 s | No evaluada | No evaluada | 1,830 [1,417; 2,242] — with margin | 7,763 [7,025; 8,502] — with margin |
| P3d turnos K4 perdidos = 0 | No evaluada | No evaluada | 0 — with margin | 0 — with margin |
| P3e retiros K28 perdidos = 0 | No evaluada | No evaluada | 36,7 [32,1; 41,3] — **Violated** | 0 — with margin |
| P1b custodia perdida = 0 | No evaluada | No evaluada | 0 — with margin | 0 — with margin |

«No evaluada»: el escenario B (`Failover`) entra en la iteración 3, como pide el enunciado; para E-QS3 la línea de base de las iteraciones 1 y 2 es S1.

## 10. Contribución a SoS-QS1 (M4) (`out/sos-qs1-fts.md`)

Presupuesto del FTS en el acuerdo conjunto: reconciliación local ≤ 300 s desde «restablecido» (SoS-K35); el equipo lo reparte en ≤ 270 s para consultas y reintentos y ≤ 30 s para aplicar resultados.

| Constituyente o conector | Presupuesto | Medida verificada (modelo final) | Técnica | Outcome |
|---|---|---|---|---|
| FTS: reconciliación local (M4) | ≤ 300 s | 71,6 s [71,5; 71,7] = 41,598 s simulados de consultas + 30 s de presupuesto para aplicar | Simulación, 10 réplicas, IC 95 % | Satisfied with margin |
| FTS: consultas por SoS-K19a | ≤ 2 intentos/s y ≤ 80 intentos | 2 intentos/s, 80 intentos | Por construcción (limitador del escenario) | Satisfied |
| FTS: recepción del aviso SoS-K35 (S4) | Alcanza a los servicios por el broker | it1: Violated (CON); it2–it4: Satisfied | Análisis del grafo | Satisfied |
| SoS-K19a/b: respuesta de la frontera NCS | ≤ 2 s por consulta | Supuesto del escenario; no la verifica el FTS | — | Not verifiable (otro dueño) |

La medida es la misma en las cuatro iteraciones (71,5 a 71,6 s): la domina la tasa acordada, no la estructura del FTS. Coincide con la Entrega 2 (72 s). Sensibilidad a parámetros que no son del FTS (reconciliación local = consultas + 30 s):

| Parámetro | Dueño | Valor | Consultas [IC 95 %] | Reconciliación local | Outcome frente a 300 s |
|---|---|---|---|---|---|
| Tasa acordada P7 (intentos/s) | Acuerdo FTS–Coordinación Nacional | 0,25 | 318,020 [318,011; 318,030] s | 348,0 s | **Violated** |
| | | 0,5 | 160,021 [160,013; 160,029] s | 190,0 s | Satisfied with margin |
| | | 1 | 81,151 [81,032; 81,269] s | 111,2 s | Satisfied with margin |
| | | 2 (nominal) | 41,598 [41,467; 41,728] s | 71,6 s | Satisfied with margin |
| Respuesta de la frontera NCS | Coordinación Nacional | 1 s | 40,561 [40,504; 40,619] s | 70,6 s | Satisfied with margin |
| | | 2 s (nominal) | 41,598 s | 71,6 s | Satisfied with margin |
| | | 5 s | 44,597 [44,496; 44,699] s | 74,6 s | Satisfied with margin |
| | | 30 s | 83,006 [82,195; 83,817] s | 113,0 s | Satisfied with margin |
| Probabilidad de reintento | Coordinación Nacional y red | 0 | 23,778 [22,823; 24,733] s | 53,8 s | Satisfied with margin |
| | | 0,5 | 31,798 [30,783; 32,813] s | 61,8 s | Satisfied with margin |
| | | 1 (nominal, peor caso) | 41,598 s | 71,6 s | Satisfied with margin |

El aporte del FTS a M4 es robusto a la respuesta de Coordinación Nacional (15 veces más lenta: 113 s) y a los reintentos, y sensible a la tasa P7: si se acordara por debajo de ≈ 0,3 intentos/s (80 intentos ÷ 270 s) el presupuesto se rompe. El FTS usa 71,6 de sus 300 s: 228 s de holgura para la composición top-down, que hacen los seis equipos.

## 11. Hallazgos frente a las Entregas 2 y 3

| # | Entrega 2 / 3 | Verificación | Tipo |
|---|---|---|---|
| 1 | E-QS3: «0 operaciones aceptadas perdidas»; el Gateway retiene 160 solicitudes durante 8 s | 36,7 retiros SoS-K28 perdidos [32,1; 41,3] por falla: nacen en Turnos, no pasan por el Gateway y nadie los retiene | **Contradice.** Corregido en it4 |
| 2 | E-QS6: 35 s ≤ 35 s, margen 0 | 35,000 s, Satisfied without margin | Confirma. Corregido en it4 (29 s) |
| 3 | E-QS1 antes: p95 ≈ 1,7 s; «con 50 op/s, 21 s» | 1,169 s [0,884; 1,454]; con 50 op/s, 25,7 s [24,6; 26,7] | Matiza: la custodia cumple 30 s sin tácticas en todo el rango; la propiedad en riesgo en la estructura de partida es el turno SoS-K4 (p95 ≤ 5 s), que la Entrega 2 no evaluó bajo la carga de recuperación |
| 4 | E-QS1 después: p95 ≤ 0,2 s (0,15 s) | 0,157 s [0,155; 0,159] | Confirma |
| 5 | E-QS2: persistido en ≈ 30 s (10 + 18 + 2) | 20,982 s [19,860; 22,104]; el vaciado de 18 s emerge de 900 posiciones y 50/s | Confirma con más margen: 30 s era el peor caso de la detección de reconexión |
| 6 | E-QS3: conmutación 8 s | 6,983 s [6,516; 7,450] | Confirma: 8 s es el máximo, no el valor esperado |
| 7 | E-QS3: «100 % completa en ≤ 15 s» con 41 op/s libres | Percentil 99,9 de SoS-K4: 6,6 s (it3) y 7,3 s (it4), aun con el rezago H3 coincidiendo con la falla | Confirma, gracias a la prioridad: el rezago queda detrás de las operaciones |
| 8 | SoS-QS1: reconciliación ≈ 72 s (≈ 75 s antes) | 71,6 s en las cuatro estructuras | Confirma; la diferencia «antes/después» de 3 s no aparece: cuando llegan las últimas consultas la cola ya se vació |
| 9 | E-QS2: reserva de 256 KiB «con margen de 76 KiB» | Con reserva justa de 900 posiciones se pierden 10,7 [2,9; 18,5] | Matiza: el margen no es un lujo; con llegadas variables es necesario |
| 10 | Entrega 3: C6 solo restringía eventos que salen de T3; E-K19 y E-K38 «no la violan» | Con el alcance corregido la violaban; reclasificados a `data_flow` | Corrige |

## 12. Amenazas a la validez

- **Modelo de colas.** Servicio exponencial y un servidor por componente (Lab. 5). Las posiciones y los latidos reales son periódicos; modelarlos como Poisson exagera la variabilidad (afecta sobre todo al barrido del búfer: 900 llegadas exactas no se desbordarían en 900).
- **Capacidades conocidas.** Solo el Traductor (A1) y el Búfer (H3, A2) tienen capacidad; Gateway, Broker, servicios, Gateway IoT y Cola Persistente no toman tiempo porque la Entrega 2 no les da cifra. Si la escritura durable de la Cola (20 ms, A2) fuera serial serían 50 escrituras/s frente a 65 eventos/s en la recuperación: no se modeló y es un riesgo por medir.
- **Parámetros ilustrativos.** Los de la Entrega 2; la falla de 300 s y las ventanas son elegidas. El p95 de custodia depende de la ventana de 90 s.
- **P4 es determinista.** No es una estimación estadística: es 3 × periodo más el presupuesto de propagación de 5 s. No hay cola en la ruta del aviso; si la hubiera, o si el filtro de vigencia revisara por barrido y no por temporizador (H6), el resultado cambiaría.
- **Medias frente a máximos.** E-QS3 pide el plazo «en cada inyección»; P3a clasifica la media de 10 réplicas (6,98 s). El máximo analítico es 8 s, también ≤ 10 s.
- **Conmutación ideal.** La réplica tiene la misma capacidad y hereda la cola completa (réplica de estado E-K61 perfecta); el trabajo en servicio al fallar termina (como en el Lab. 5).
- **Retención ideal.** Un `store` retiene sin límite de tiempo; el plazo de 15 s del reintento de `CallerRetention` no se modela como vencimiento (la conmutación dura como máximo 8 s).
- **Agregación.** Los 5 convoyes afectados son un solo búfer de 1.280 posiciones; en la realidad son 5 de 256.
- **Reintento.** El reintento siempre resuelve la consulta; no se modela un segundo fallo.
- **Peor caso elegido.** El rezago H3 se hace coincidir con la falla del Traductor; otros desfases no se probaron.
- **Línea de base de B.** `Failover` no se corrió sobre la estructura de partida (el enunciado lo ubica en la iteración 3); sin standby el resultado es trivial (restablecimiento = 300 s).
- **Correspondencia con el sistema.** La conformidad y la correspondencia con `sos.arch` las comprueba la herramienta; que el modelo corresponda al FTS real, no.

## 13. Riesgos residuales (modelo final)

| Riesgo | Evidencia | Estado |
|---|---|---|
| El Fluvial Gateway es único en todas las cadenas | Fuera del ambiente de E-QS3 («Gateway… permanecen disponibles»); S1 solo mira los factores del análisis de disponibilidad | Declarado, no cubierto |
| La causa común domina la disponibilidad del Traductor (99,948 % con β = 0,10; 99,898 % con β = 0,20) | Analítico (`analysis.md`, Entrega 2 §8.2) | Depende del despliegue |
| Capacidad del Traductor por debajo de 55–60 op/s | P3f Violated con 50 op/s aun con prioridad | Medir A1 |
| La clase 3 paga la prioridad | Reconciliación sin reintentos: 23,8 s frente a 22,3 s; con el Traductor a 60 op/s, 118,8 s frente a 65,9 s | Aceptado (dentro de 270 s) |
| La retención en el emisor agrega espera | P3c: 1,8 → 7,8 s | Aceptado (≤ 13,5 s) |
| Tasa P7 por debajo de ≈ 0,3 intentos/s | P5 Violated con 0,25 | Depende del acuerdo con Coordinación Nacional |
| Falsas alarmas de desconexión con latido de 8 s | No verificado (0,0225/h analítico) | Por ensayo |
| Seguridad, evolutividad, duplicados | No verificables con este modelo (§5) | Por otra técnica |
