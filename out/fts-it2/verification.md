# Verificación de FTS

Modelo: `models/fts-it2.arch` (núcleo v2.0 con extensiones [E]); corresponde a `sos.arch`.

## Propiedades estructurales (análisis del grafo)

| Propiedad | Elementos encontrados | Outcome |
|---|---|---|
| S1. Sin punto único de falla en la cadena de E-QS3 (disponibilidad del Traductor) | Ninguno | Satisfied |
| S2. Sin conector blocking en la cadena de custodia (clase 1, E-QS1) | Ninguno | Satisfied |
| S3. Todo servidor que la cadena de custodia comparte con intercambios blocking atiende por prioridad (E-QS1) | Ninguno | Satisfied |
| S4. El aviso de frontera de SoSQS1 alcanza por el broker a los servicios de su artefacto | Ninguno | Satisfied |

## Escenario E-QS1 (Recovery)

Corrida 150 s, calentamiento 60 s, 10 réplicas (semillas 1–10); parámetros variados, uno a la vez: TRA, NcsResponse, Reconcile.retry, Reconcile

| Parámetro | Valor | Propiedad | Medida | Estimación | IC 95 % | Umbral | Outcome |
|---|---|---|---|---|---|---|---|
| nominal | — | P1a custodia p95 | p95_latency Custody | 0.157 | [0.155, 0.159] | ≤ 30 s | Satisfied with margin |
| nominal | — | P2c posiciones nuevas p95 | p95_latency Positions | 0.100 | [0.094, 0.106] | ≤ 15 s | Satisfied with margin |
| nominal | — | P3f turno K4 p95 (sin falla) | p95_latency K4 | 0.143 | [0.134, 0.152] | ≤ 5 s | Satisfied with margin |
| nominal | — | P5 reconciliación (consultas) | completion Reconcile | 41.598 | [41.467, 41.728] | ≤ 270 s | Satisfied with margin |
| TRA | 50 | P1a custodia p95 | p95_latency Custody | 0.221 | [0.216, 0.225] | ≤ 30 s | Satisfied with margin |
| TRA | 50 | P2c posiciones nuevas p95 | p95_latency Positions | 11.609 | [10.405, 12.813] | ≤ 15 s | Satisfied with margin |
| TRA | 50 | P3f turno K4 p95 (sin falla) | p95_latency K4 | 22.428 | [20.223, 24.633] | ≤ 5 s | Violated |
| TRA | 50 | P5 reconciliación (consultas) | completion Reconcile | 145.461 | [143.888, 147.033] | ≤ 270 s | Satisfied with margin |
| TRA | 60 | P1a custodia p95 | p95_latency Custody | 0.198 | [0.196, 0.201] | ≤ 30 s | Satisfied with margin |
| TRA | 60 | P2c posiciones nuevas p95 | p95_latency Positions | 0.675 | [0.507, 0.843] | ≤ 15 s | Satisfied with margin |
| TRA | 60 | P3f turno K4 p95 (sin falla) | p95_latency K4 | 1.258 | [0.920, 1.595] | ≤ 5 s | Satisfied with margin |
| TRA | 60 | P5 reconciliación (consultas) | completion Reconcile | 118.836 | [117.055, 120.617] | ≤ 270 s | Satisfied with margin |
| TRA | 70 | P1a custodia p95 | p95_latency Custody | 0.183 | [0.181, 0.185] | ≤ 30 s | Satisfied with margin |
| TRA | 70 | P2c posiciones nuevas p95 | p95_latency Positions | 0.266 | [0.232, 0.300] | ≤ 15 s | Satisfied with margin |
| TRA | 70 | P3f turno K4 p95 (sin falla) | p95_latency K4 | 0.460 | [0.391, 0.530] | ≤ 5 s | Satisfied with margin |
| TRA | 70 | P5 reconciliación (consultas) | completion Reconcile | 82.340 | [77.061, 87.618] | ≤ 270 s | Satisfied with margin |
| TRA | 80 | P1a custodia p95 | p95_latency Custody | 0.171 | [0.169, 0.173] | ≤ 30 s | Satisfied with margin |
| TRA | 80 | P2c posiciones nuevas p95 | p95_latency Positions | 0.169 | [0.158, 0.181] | ≤ 15 s | Satisfied with margin |
| TRA | 80 | P3f turno K4 p95 (sin falla) | p95_latency K4 | 0.282 | [0.252, 0.311] | ≤ 5 s | Satisfied with margin |
| TRA | 80 | P5 reconciliación (consultas) | completion Reconcile | 52.165 | [49.854, 54.476] | ≤ 270 s | Satisfied with margin |
| TRA | 90 | P1a custodia p95 | p95_latency Custody | 0.163 | [0.161, 0.165] | ≤ 30 s | Satisfied with margin |
| TRA | 90 | P2c posiciones nuevas p95 | p95_latency Positions | 0.119 | [0.112, 0.126] | ≤ 15 s | Satisfied with margin |
| TRA | 90 | P3f turno K4 p95 (sin falla) | p95_latency K4 | 0.189 | [0.177, 0.201] | ≤ 5 s | Satisfied with margin |
| TRA | 90 | P5 reconciliación (consultas) | completion Reconcile | 41.694 | [41.433, 41.956] | ≤ 270 s | Satisfied with margin |
| TRA | 120 | P1a custodia p95 | p95_latency Custody | 0.147 | [0.146, 0.149] | ≤ 30 s | Satisfied with margin |
| TRA | 120 | P2c posiciones nuevas p95 | p95_latency Positions | 0.072 | [0.069, 0.075] | ≤ 15 s | Satisfied with margin |
| TRA | 120 | P3f turno K4 p95 (sin falla) | p95_latency K4 | 0.095 | [0.091, 0.100] | ≤ 5 s | Satisfied with margin |
| TRA | 120 | P5 reconciliación (consultas) | completion Reconcile | 41.537 | [41.504, 41.570] | ≤ 270 s | Satisfied with margin |
| NcsResponse | 1000 | P1a custodia p95 | p95_latency Custody | 0.157 | [0.155, 0.158] | ≤ 30 s | Satisfied with margin |
| NcsResponse | 1000 | P2c posiciones nuevas p95 | p95_latency Positions | 0.099 | [0.093, 0.104] | ≤ 15 s | Satisfied with margin |
| NcsResponse | 1000 | P3f turno K4 p95 (sin falla) | p95_latency K4 | 0.144 | [0.136, 0.153] | ≤ 5 s | Satisfied with margin |
| NcsResponse | 1000 | P5 reconciliación (consultas) | completion Reconcile | 40.561 | [40.504, 40.619] | ≤ 270 s | Satisfied with margin |
| NcsResponse | 5000 | P1a custodia p95 | p95_latency Custody | 0.157 | [0.155, 0.159] | ≤ 30 s | Satisfied with margin |
| NcsResponse | 5000 | P2c posiciones nuevas p95 | p95_latency Positions | 0.100 | [0.096, 0.104] | ≤ 15 s | Satisfied with margin |
| NcsResponse | 5000 | P3f turno K4 p95 (sin falla) | p95_latency K4 | 0.146 | [0.135, 0.158] | ≤ 5 s | Satisfied with margin |
| NcsResponse | 5000 | P5 reconciliación (consultas) | completion Reconcile | 44.597 | [44.496, 44.699] | ≤ 270 s | Satisfied with margin |
| NcsResponse | 30000 | P1a custodia p95 | p95_latency Custody | 0.156 | [0.155, 0.158] | ≤ 30 s | Satisfied with margin |
| NcsResponse | 30000 | P2c posiciones nuevas p95 | p95_latency Positions | 0.100 | [0.096, 0.104] | ≤ 15 s | Satisfied with margin |
| NcsResponse | 30000 | P3f turno K4 p95 (sin falla) | p95_latency K4 | 0.140 | [0.131, 0.149] | ≤ 5 s | Satisfied with margin |
| NcsResponse | 30000 | P5 reconciliación (consultas) | completion Reconcile | 83.006 | [82.195, 83.817] | ≤ 270 s | Satisfied with margin |
| Reconcile.retry | 0 | P1a custodia p95 | p95_latency Custody | 0.157 | [0.155, 0.159] | ≤ 30 s | Satisfied with margin |
| Reconcile.retry | 0 | P2c posiciones nuevas p95 | p95_latency Positions | 0.099 | [0.093, 0.106] | ≤ 15 s | Satisfied with margin |
| Reconcile.retry | 0 | P3f turno K4 p95 (sin falla) | p95_latency K4 | 0.139 | [0.127, 0.151] | ≤ 5 s | Satisfied with margin |
| Reconcile.retry | 0 | P5 reconciliación (consultas) | completion Reconcile | 23.778 | [22.823, 24.733] | ≤ 270 s | Satisfied with margin |
| Reconcile.retry | 0.5 | P1a custodia p95 | p95_latency Custody | 0.156 | [0.155, 0.158] | ≤ 30 s | Satisfied with margin |
| Reconcile.retry | 0.5 | P2c posiciones nuevas p95 | p95_latency Positions | 0.097 | [0.090, 0.104] | ≤ 15 s | Satisfied with margin |
| Reconcile.retry | 0.5 | P3f turno K4 p95 (sin falla) | p95_latency K4 | 0.136 | [0.125, 0.148] | ≤ 5 s | Satisfied with margin |
| Reconcile.retry | 0.5 | P5 reconciliación (consultas) | completion Reconcile | 31.798 | [30.783, 32.813] | ≤ 270 s | Satisfied with margin |
| Reconcile | 0.25 | P1a custodia p95 | p95_latency Custody | 0.157 | [0.155, 0.159] | ≤ 30 s | Satisfied with margin |
| Reconcile | 0.25 | P2c posiciones nuevas p95 | p95_latency Positions | 0.097 | [0.091, 0.104] | ≤ 15 s | Satisfied with margin |
| Reconcile | 0.25 | P3f turno K4 p95 (sin falla) | p95_latency K4 | 0.144 | [0.134, 0.153] | ≤ 5 s | Satisfied with margin |
| Reconcile | 0.25 | P5 reconciliación (consultas) | completion Reconcile | 318.020 | [318.011, 318.030] | ≤ 270 s | Violated |
| Reconcile | 0.5 | P1a custodia p95 | p95_latency Custody | 0.157 | [0.155, 0.158] | ≤ 30 s | Satisfied with margin |
| Reconcile | 0.5 | P2c posiciones nuevas p95 | p95_latency Positions | 0.098 | [0.092, 0.103] | ≤ 15 s | Satisfied with margin |
| Reconcile | 0.5 | P3f turno K4 p95 (sin falla) | p95_latency K4 | 0.139 | [0.132, 0.147] | ≤ 5 s | Satisfied with margin |
| Reconcile | 0.5 | P5 reconciliación (consultas) | completion Reconcile | 160.021 | [160.013, 160.029] | ≤ 270 s | Satisfied with margin |
| Reconcile | 1 | P1a custodia p95 | p95_latency Custody | 0.156 | [0.154, 0.159] | ≤ 30 s | Satisfied with margin |
| Reconcile | 1 | P2c posiciones nuevas p95 | p95_latency Positions | 0.101 | [0.096, 0.107] | ≤ 15 s | Satisfied with margin |
| Reconcile | 1 | P3f turno K4 p95 (sin falla) | p95_latency K4 | 0.140 | [0.128, 0.152] | ≤ 5 s | Satisfied with margin |
| Reconcile | 1 | P5 reconciliación (consultas) | completion Reconcile | 81.151 | [81.032, 81.269] | ≤ 270 s | Satisfied with margin |

## Escenario E-QS2 / E-QS6 (Partition)

Corrida 2100 s, calentamiento 0 s, 10 réplicas (semillas 1–10); parámetros variados, uno a la vez: BUF.buffer, UAB.period

| Parámetro | Valor | Propiedad | Medida | Estimación | IC 95 % | Umbral | Outcome |
|---|---|---|---|---|---|---|---|
| nominal | — | P2a posiciones perdidas | lost Affected | 0.0 | [0.0, 0.0] | ≤ 0 events | Satisfied with margin |
| nominal | — | P2b persistencia del rezago | drain Affected | 20.982 | [19.860, 22.104] | ≤ 60 s | Satisfied with margin |
| nominal | — | P4 detección del silencio | detection | 35.000 | [35.000, 35.000] | ≤ 35 s | Satisfied without margin |
| BUF.buffer | 600 | P2a posiciones perdidas | lost Affected | 301.3 | [283.5, 319.1] | ≤ 0 events | Violated |
| BUF.buffer | 600 | P2b persistencia del rezago | drain Affected | 20.570 | [18.293, 22.847] | ≤ 60 s | Satisfied with margin |
| BUF.buffer | 600 | P4 detección del silencio | detection | 35.000 | [35.000, 35.000] | ≤ 35 s | Satisfied without margin |
| BUF.buffer | 900 | P2a posiciones perdidas | lost Affected | 10.7 | [2.9, 18.5] | ≤ 0 events | Violated |
| BUF.buffer | 900 | P2b persistencia del rezago | drain Affected | 23.895 | [20.880, 26.909] | ≤ 60 s | Satisfied with margin |
| BUF.buffer | 900 | P4 detección del silencio | detection | 35.000 | [35.000, 35.000] | ≤ 35 s | Satisfied without margin |
| UAB.period | 6000 | P2a posiciones perdidas | lost Affected | 0.0 | [0.0, 0.0] | ≤ 0 events | Satisfied with margin |
| UAB.period | 6000 | P2b persistencia del rezago | drain Affected | 20.982 | [19.860, 22.104] | ≤ 60 s | Satisfied with margin |
| UAB.period | 6000 | P4 detección del silencio | detection | 23.000 | [23.000, 23.000] | ≤ 35 s | Satisfied with margin |
| UAB.period | 8000 | P2a posiciones perdidas | lost Affected | 0.0 | [0.0, 0.0] | ≤ 0 events | Satisfied with margin |
| UAB.period | 8000 | P2b persistencia del rezago | drain Affected | 20.982 | [19.860, 22.104] | ≤ 60 s | Satisfied with margin |
| UAB.period | 8000 | P4 detección del silencio | detection | 29.000 | [29.000, 29.000] | ≤ 35 s | Satisfied with margin |
| UAB.period | 9000 | P2a posiciones perdidas | lost Affected | 0.0 | [0.0, 0.0] | ≤ 0 events | Satisfied with margin |
| UAB.period | 9000 | P2b persistencia del rezago | drain Affected | 20.982 | [19.860, 22.104] | ≤ 60 s | Satisfied with margin |
| UAB.period | 9000 | P4 detección del silencio | detection | 32.000 | [32.000, 32.000] | ≤ 35 s | Satisfied without margin |
| UAB.period | 12000 | P2a posiciones perdidas | lost Affected | 0.0 | [0.0, 0.0] | ≤ 0 events | Satisfied with margin |
| UAB.period | 12000 | P2b persistencia del rezago | drain Affected | 20.982 | [19.860, 22.104] | ≤ 60 s | Satisfied with margin |
| UAB.period | 12000 | P4 detección del silencio | detection | 41.000 | [41.000, 41.000] | ≤ 35 s | Violated |
