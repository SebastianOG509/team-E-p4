# Verificación de FTS

Modelo: `models/fts-it1.arch` (núcleo v2.0 con extensiones [E]); corresponde a `sos.arch`.

## Propiedades estructurales (análisis del grafo)

| Propiedad | Elementos encontrados | Outcome |
|---|---|---|
| S1. Sin punto único de falla en la cadena de E-QS3 (disponibilidad del Traductor) | TRA | Violated |
| S2. Sin conector blocking en la cadena de custodia (clase 1, E-QS1) | Ninguno | Satisfied |
| S3. Todo servidor que la cadena de custodia comparte con intercambios blocking atiende por prioridad (E-QS1) | TRA | Violated |
| S4. El aviso de frontera de SoSQS1 alcanza por el broker a los servicios de su artefacto | CON | Violated |

## Escenario E-QS1 (Recovery)

Corrida 150 s, calentamiento 60 s, 10 réplicas (semillas 1–10); parámetros variados, uno a la vez: TRA, NcsResponse, Reconcile.retry, Reconcile

| Parámetro | Valor | Propiedad | Medida | Estimación | IC 95 % | Umbral | Outcome |
|---|---|---|---|---|---|---|---|
| nominal | — | P1a custodia p95 | p95_latency Custody | 1.169 | [0.884, 1.454] | ≤ 30 s | Satisfied with margin |
| nominal | — | P2c posiciones nuevas p95 | p95_latency Positions | 1.158 | [0.841, 1.475] | ≤ 15 s | Satisfied with margin |
| nominal | — | P3f turno K4 p95 (sin falla) | p95_latency K4 | 2.277 | [1.623, 2.932] | ≤ 5 s | Satisfied with margin |
| nominal | — | P5 reconciliación (consultas) | completion Reconcile | 41.526 | [41.513, 41.539] | ≤ 270 s | Satisfied with margin |
| TRA | 50 | P1a custodia p95 | p95_latency Custody | 25.671 | [24.611, 26.732] | ≤ 30 s | Satisfied with margin |
| TRA | 50 | P2c posiciones nuevas p95 | p95_latency Positions | 25.684 | [24.616, 26.753] | ≤ 15 s | Violated |
| TRA | 50 | P3f turno K4 p95 (sin falla) | p95_latency K4 | 49.571 | [47.728, 51.415] | ≤ 5 s | Violated |
| TRA | 50 | P5 reconciliación (consultas) | completion Reconcile | 115.136 | [112.238, 118.034] | ≤ 270 s | Satisfied with margin |
| TRA | 60 | P1a custodia p95 | p95_latency Custody | 11.494 | [10.897, 12.092] | ≤ 30 s | Satisfied with margin |
| TRA | 60 | P2c posiciones nuevas p95 | p95_latency Positions | 11.486 | [10.923, 12.049] | ≤ 15 s | Satisfied with margin |
| TRA | 60 | P3f turno K4 p95 (sin falla) | p95_latency K4 | 21.730 | [20.628, 22.832] | ≤ 5 s | Violated |
| TRA | 60 | P5 reconciliación (consultas) | completion Reconcile | 65.910 | [64.048, 67.772] | ≤ 270 s | Satisfied with margin |
| TRA | 70 | P1a custodia p95 | p95_latency Custody | 7.579 | [7.150, 8.008] | ≤ 30 s | Satisfied with margin |
| TRA | 70 | P2c posiciones nuevas p95 | p95_latency Positions | 7.543 | [7.207, 7.880] | ≤ 15 s | Satisfied with margin |
| TRA | 70 | P3f turno K4 p95 (sin falla) | p95_latency K4 | 14.209 | [13.504, 14.914] | ≤ 5 s | Violated |
| TRA | 70 | P5 reconciliación (consultas) | completion Reconcile | 50.339 | [49.521, 51.157] | ≤ 270 s | Satisfied with margin |
| TRA | 80 | P1a custodia p95 | p95_latency Custody | 4.641 | [4.306, 4.976] | ≤ 30 s | Satisfied with margin |
| TRA | 80 | P2c posiciones nuevas p95 | p95_latency Positions | 4.636 | [4.332, 4.941] | ≤ 15 s | Satisfied with margin |
| TRA | 80 | P3f turno K4 p95 (sin falla) | p95_latency K4 | 9.022 | [8.473, 9.572] | ≤ 5 s | Violated |
| TRA | 80 | P5 reconciliación (consultas) | completion Reconcile | 42.414 | [42.015, 42.812] | ≤ 270 s | Satisfied with margin |
| TRA | 90 | P1a custodia p95 | p95_latency Custody | 2.659 | [2.329, 2.990] | ≤ 30 s | Satisfied with margin |
| TRA | 90 | P2c posiciones nuevas p95 | p95_latency Positions | 2.656 | [2.354, 2.958] | ≤ 15 s | Satisfied with margin |
| TRA | 90 | P3f turno K4 p95 (sin falla) | p95_latency K4 | 5.171 | [4.557, 5.785] | ≤ 5 s | Inconclusive |
| TRA | 90 | P5 reconciliación (consultas) | completion Reconcile | 41.545 | [41.524, 41.567] | ≤ 270 s | Satisfied with margin |
| TRA | 120 | P1a custodia p95 | p95_latency Custody | 0.146 | [0.115, 0.177] | ≤ 30 s | Satisfied with margin |
| TRA | 120 | P2c posiciones nuevas p95 | p95_latency Positions | 0.115 | [0.084, 0.146] | ≤ 15 s | Satisfied with margin |
| TRA | 120 | P3f turno K4 p95 (sin falla) | p95_latency K4 | 0.237 | [0.172, 0.303] | ≤ 5 s | Satisfied with margin |
| TRA | 120 | P5 reconciliación (consultas) | completion Reconcile | 41.519 | [41.508, 41.529] | ≤ 270 s | Satisfied with margin |
| NcsResponse | 1000 | P1a custodia p95 | p95_latency Custody | 1.258 | [0.955, 1.561] | ≤ 30 s | Satisfied with margin |
| NcsResponse | 1000 | P2c posiciones nuevas p95 | p95_latency Positions | 1.241 | [0.915, 1.567] | ≤ 15 s | Satisfied with margin |
| NcsResponse | 1000 | P3f turno K4 p95 (sin falla) | p95_latency K4 | 2.436 | [1.768, 3.103] | ≤ 5 s | Satisfied with margin |
| NcsResponse | 1000 | P5 reconciliación (consultas) | completion Reconcile | 40.524 | [40.509, 40.539] | ≤ 270 s | Satisfied with margin |
| NcsResponse | 5000 | P1a custodia p95 | p95_latency Custody | 1.122 | [0.802, 1.441] | ≤ 30 s | Satisfied with margin |
| NcsResponse | 5000 | P2c posiciones nuevas p95 | p95_latency Positions | 1.110 | [0.779, 1.440] | ≤ 15 s | Satisfied with margin |
| NcsResponse | 5000 | P3f turno K4 p95 (sin falla) | p95_latency K4 | 2.179 | [1.515, 2.843] | ≤ 5 s | Satisfied with margin |
| NcsResponse | 5000 | P5 reconciliación (consultas) | completion Reconcile | 44.544 | [44.519, 44.570] | ≤ 270 s | Satisfied with margin |
| NcsResponse | 30000 | P1a custodia p95 | p95_latency Custody | 1.028 | [0.700, 1.355] | ≤ 30 s | Satisfied with margin |
| NcsResponse | 30000 | P2c posiciones nuevas p95 | p95_latency Positions | 0.996 | [0.640, 1.352] | ≤ 15 s | Satisfied with margin |
| NcsResponse | 30000 | P3f turno K4 p95 (sin falla) | p95_latency K4 | 1.979 | [1.252, 2.707] | ≤ 5 s | Satisfied with margin |
| NcsResponse | 30000 | P5 reconciliación (consultas) | completion Reconcile | 80.857 | [80.537, 81.177] | ≤ 270 s | Satisfied with margin |
| Reconcile.retry | 0 | P1a custodia p95 | p95_latency Custody | 1.169 | [0.884, 1.454] | ≤ 30 s | Satisfied with margin |
| Reconcile.retry | 0 | P2c posiciones nuevas p95 | p95_latency Positions | 1.158 | [0.841, 1.475] | ≤ 15 s | Satisfied with margin |
| Reconcile.retry | 0 | P3f turno K4 p95 (sin falla) | p95_latency K4 | 2.277 | [1.623, 2.932] | ≤ 5 s | Satisfied with margin |
| Reconcile.retry | 0 | P5 reconciliación (consultas) | completion Reconcile | 22.344 | [21.912, 22.775] | ≤ 270 s | Satisfied with margin |
| Reconcile.retry | 0.5 | P1a custodia p95 | p95_latency Custody | 1.169 | [0.884, 1.454] | ≤ 30 s | Satisfied with margin |
| Reconcile.retry | 0.5 | P2c posiciones nuevas p95 | p95_latency Positions | 1.158 | [0.841, 1.475] | ≤ 15 s | Satisfied with margin |
| Reconcile.retry | 0.5 | P3f turno K4 p95 (sin falla) | p95_latency K4 | 2.277 | [1.623, 2.932] | ≤ 5 s | Satisfied with margin |
| Reconcile.retry | 0.5 | P5 reconciliación (consultas) | completion Reconcile | 32.305 | [31.079, 33.531] | ≤ 270 s | Satisfied with margin |
| Reconcile | 0.25 | P1a custodia p95 | p95_latency Custody | 0.858 | [0.687, 1.030] | ≤ 30 s | Satisfied with margin |
| Reconcile | 0.25 | P2c posiciones nuevas p95 | p95_latency Positions | 0.839 | [0.640, 1.038] | ≤ 15 s | Satisfied with margin |
| Reconcile | 0.25 | P3f turno K4 p95 (sin falla) | p95_latency K4 | 1.642 | [1.227, 2.057] | ≤ 5 s | Satisfied with margin |
| Reconcile | 0.25 | P5 reconciliación (consultas) | completion Reconcile | 318.020 | [318.011, 318.030] | ≤ 270 s | Violated |
| Reconcile | 0.5 | P1a custodia p95 | p95_latency Custody | 0.888 | [0.568, 1.207] | ≤ 30 s | Satisfied with margin |
| Reconcile | 0.5 | P2c posiciones nuevas p95 | p95_latency Positions | 0.867 | [0.539, 1.194] | ≤ 15 s | Satisfied with margin |
| Reconcile | 0.5 | P3f turno K4 p95 (sin falla) | p95_latency K4 | 1.703 | [1.020, 2.386] | ≤ 5 s | Satisfied with margin |
| Reconcile | 0.5 | P5 reconciliación (consultas) | completion Reconcile | 160.021 | [160.013, 160.029] | ≤ 270 s | Satisfied with margin |
| Reconcile | 1 | P1a custodia p95 | p95_latency Custody | 0.974 | [0.730, 1.218] | ≤ 30 s | Satisfied with margin |
| Reconcile | 1 | P2c posiciones nuevas p95 | p95_latency Positions | 0.950 | [0.680, 1.220] | ≤ 15 s | Satisfied with margin |
| Reconcile | 1 | P3f turno K4 p95 (sin falla) | p95_latency K4 | 1.873 | [1.320, 2.426] | ≤ 5 s | Satisfied with margin |
| Reconcile | 1 | P5 reconciliación (consultas) | completion Reconcile | 81.072 | [81.028, 81.116] | ≤ 270 s | Satisfied with margin |

## Escenario E-QS2 / E-QS6 (Partition)

Corrida 2100 s, calentamiento 0 s, 10 réplicas (semillas 1–10); parámetros variados, uno a la vez: —

| Parámetro | Valor | Propiedad | Medida | Estimación | IC 95 % | Umbral | Outcome |
|---|---|---|---|---|---|---|---|
| nominal | — | P2a posiciones perdidas | lost Affected | 898.1 | [879.8, 916.4] | ≤ 0 events | Violated |
| nominal | — | P2b persistencia del rezago | drain Affected | 0.000 | [0.000, 0.000] | ≤ 60 s | Satisfied with margin |
| nominal | — | P4 detección del silencio | detection | 2000.000 | [2000.000, 2000.000] | ≤ 35 s | Violated |
