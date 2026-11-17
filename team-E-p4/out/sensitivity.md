# Análisis de sensibilidad

Cada parámetro se varía solo, con los demás en su valor nominal (10 réplicas, semillas 1–10, las mismas en todos los puntos). La fila del valor nominal es la de `verification.md`.

## Capacidad del Traductor (operaciones/s; supuesto A1 = 100)

| Propiedad | Iteración | Valor | Estimación | IC 95 % | Umbral | Outcome |
|---|---|---|---|---|---|---|
| P1a custodia p95 | it1 | 50 | 25.671 | [24.611, 26.732] | ≤ 30 s | Satisfied with margin |
| P1a custodia p95 | it1 | 60 | 11.494 | [10.897, 12.092] | ≤ 30 s | Satisfied with margin |
| P1a custodia p95 | it1 | 70 | 7.579 | [7.150, 8.008] | ≤ 30 s | Satisfied with margin |
| P1a custodia p95 | it1 | 80 | 4.641 | [4.306, 4.976] | ≤ 30 s | Satisfied with margin |
| P1a custodia p95 | it1 | 90 | 2.659 | [2.329, 2.990] | ≤ 30 s | Satisfied with margin |
| P1a custodia p95 | it1 | 100 | 1.169 | [0.884, 1.454] | ≤ 30 s | Satisfied with margin |
| P1a custodia p95 | it1 | 120 | 0.146 | [0.115, 0.177] | ≤ 30 s | Satisfied with margin |
| P1a custodia p95 | it2 | 50 | 0.221 | [0.216, 0.225] | ≤ 30 s | Satisfied with margin |
| P1a custodia p95 | it2 | 60 | 0.198 | [0.196, 0.201] | ≤ 30 s | Satisfied with margin |
| P1a custodia p95 | it2 | 70 | 0.183 | [0.181, 0.185] | ≤ 30 s | Satisfied with margin |
| P1a custodia p95 | it2 | 80 | 0.171 | [0.169, 0.173] | ≤ 30 s | Satisfied with margin |
| P1a custodia p95 | it2 | 90 | 0.163 | [0.161, 0.165] | ≤ 30 s | Satisfied with margin |
| P1a custodia p95 | it2 | 100 | 0.157 | [0.155, 0.159] | ≤ 30 s | Satisfied with margin |
| P1a custodia p95 | it2 | 120 | 0.147 | [0.146, 0.149] | ≤ 30 s | Satisfied with margin |
| P3f turno K4 p95 (sin falla) | it1 | 50 | 49.571 | [47.728, 51.415] | ≤ 5 s | Violated |
| P3f turno K4 p95 (sin falla) | it1 | 60 | 21.730 | [20.628, 22.832] | ≤ 5 s | Violated |
| P3f turno K4 p95 (sin falla) | it1 | 70 | 14.209 | [13.504, 14.914] | ≤ 5 s | Violated |
| P3f turno K4 p95 (sin falla) | it1 | 80 | 9.022 | [8.473, 9.572] | ≤ 5 s | Violated |
| P3f turno K4 p95 (sin falla) | it1 | 90 | 5.171 | [4.557, 5.785] | ≤ 5 s | Inconclusive |
| P3f turno K4 p95 (sin falla) | it1 | 100 | 2.277 | [1.623, 2.932] | ≤ 5 s | Satisfied with margin |
| P3f turno K4 p95 (sin falla) | it1 | 120 | 0.237 | [0.172, 0.303] | ≤ 5 s | Satisfied with margin |
| P3f turno K4 p95 (sin falla) | it2 | 50 | 22.428 | [20.223, 24.633] | ≤ 5 s | Violated |
| P3f turno K4 p95 (sin falla) | it2 | 60 | 1.258 | [0.920, 1.595] | ≤ 5 s | Satisfied with margin |
| P3f turno K4 p95 (sin falla) | it2 | 70 | 0.460 | [0.391, 0.530] | ≤ 5 s | Satisfied with margin |
| P3f turno K4 p95 (sin falla) | it2 | 80 | 0.282 | [0.252, 0.311] | ≤ 5 s | Satisfied with margin |
| P3f turno K4 p95 (sin falla) | it2 | 90 | 0.189 | [0.177, 0.201] | ≤ 5 s | Satisfied with margin |
| P3f turno K4 p95 (sin falla) | it2 | 100 | 0.143 | [0.134, 0.152] | ≤ 5 s | Satisfied with margin |
| P3f turno K4 p95 (sin falla) | it2 | 120 | 0.095 | [0.091, 0.100] | ≤ 5 s | Satisfied with margin |
| P2c posiciones nuevas p95 | it1 | 50 | 25.684 | [24.616, 26.753] | ≤ 15 s | Violated |
| P2c posiciones nuevas p95 | it1 | 60 | 11.486 | [10.923, 12.049] | ≤ 15 s | Satisfied with margin |
| P2c posiciones nuevas p95 | it1 | 70 | 7.543 | [7.207, 7.880] | ≤ 15 s | Satisfied with margin |
| P2c posiciones nuevas p95 | it1 | 80 | 4.636 | [4.332, 4.941] | ≤ 15 s | Satisfied with margin |
| P2c posiciones nuevas p95 | it1 | 90 | 2.656 | [2.354, 2.958] | ≤ 15 s | Satisfied with margin |
| P2c posiciones nuevas p95 | it1 | 100 | 1.158 | [0.841, 1.475] | ≤ 15 s | Satisfied with margin |
| P2c posiciones nuevas p95 | it1 | 120 | 0.115 | [0.084, 0.146] | ≤ 15 s | Satisfied with margin |
| P2c posiciones nuevas p95 | it2 | 50 | 11.609 | [10.405, 12.813] | ≤ 15 s | Satisfied with margin |
| P2c posiciones nuevas p95 | it2 | 60 | 0.675 | [0.507, 0.843] | ≤ 15 s | Satisfied with margin |
| P2c posiciones nuevas p95 | it2 | 70 | 0.266 | [0.232, 0.300] | ≤ 15 s | Satisfied with margin |
| P2c posiciones nuevas p95 | it2 | 80 | 0.169 | [0.158, 0.181] | ≤ 15 s | Satisfied with margin |
| P2c posiciones nuevas p95 | it2 | 90 | 0.119 | [0.112, 0.126] | ≤ 15 s | Satisfied with margin |
| P2c posiciones nuevas p95 | it2 | 100 | 0.100 | [0.094, 0.106] | ≤ 15 s | Satisfied with margin |
| P2c posiciones nuevas p95 | it2 | 120 | 0.072 | [0.069, 0.075] | ≤ 15 s | Satisfied with margin |

## Periodo del latido de la Unidad a Bordo (ms; E-QS6: 10.000)

| Propiedad | Iteración | Valor | Estimación | IC 95 % | Umbral | Outcome |
|---|---|---|---|---|---|---|
| P4 detección del silencio | it2 | 6000 | 23.000 | [23.000, 23.000] | ≤ 35 s | Satisfied with margin |
| P4 detección del silencio | it2 | 8000 | 29.000 | [29.000, 29.000] | ≤ 35 s | Satisfied with margin |
| P4 detección del silencio | it2 | 9000 | 32.000 | [32.000, 32.000] | ≤ 35 s | Satisfied without margin |
| P4 detección del silencio | it2 | 10000 | 35.000 | [35.000, 35.000] | ≤ 35 s | Satisfied without margin |
| P4 detección del silencio | it2 | 12000 | 41.000 | [41.000, 41.000] | ≤ 35 s | Violated |
| P4 detección del silencio | it4 | 6000 | 23.000 | [23.000, 23.000] | ≤ 35 s | Satisfied with margin |
| P4 detección del silencio | it4 | 8000 | 29.000 | [29.000, 29.000] | ≤ 35 s | Satisfied with margin |
| P4 detección del silencio | it4 | 9000 | 32.000 | [32.000, 32.000] | ≤ 35 s | Satisfied without margin |
| P4 detección del silencio | it4 | 10000 | 35.000 | [35.000, 35.000] | ≤ 35 s | Satisfied without margin |
| P4 detección del silencio | it4 | 12000 | 41.000 | [41.000, 41.000] | ≤ 35 s | Violated |

## Reserva del búfer a bordo (posiciones de los 5 convoyes; H2: 1.280 = 5 × 256 KiB)

| Propiedad | Iteración | Valor | Estimación | IC 95 % | Umbral | Outcome |
|---|---|---|---|---|---|---|
| P2a posiciones perdidas | it2 | 600 | 301.3 | [283.5, 319.1] | ≤ 0 events | Violated |
| P2a posiciones perdidas | it2 | 900 | 10.7 | [2.9, 18.5] | ≤ 0 events | Violated |
| P2a posiciones perdidas | it2 | 1280 | 0.0 | [0.0, 0.0] | ≤ 0 events | Satisfied with margin |

## Tasa acordada de SoS-K19a (intentos/s; P7 = 2) — dueño: acuerdo con Coordinación Nacional

| Propiedad | Iteración | Valor | Estimación | IC 95 % | Umbral | Outcome |
|---|---|---|---|---|---|---|
| P5 reconciliación (consultas) | it4 | 0.25 | 318.020 | [318.011, 318.030] | ≤ 270 s | Violated |
| P5 reconciliación (consultas) | it4 | 0.5 | 160.021 | [160.013, 160.029] | ≤ 270 s | Satisfied with margin |
| P5 reconciliación (consultas) | it4 | 1 | 81.151 | [81.032, 81.269] | ≤ 270 s | Satisfied with margin |
| P5 reconciliación (consultas) | it4 | 2 | 41.598 | [41.467, 41.728] | ≤ 270 s | Satisfied with margin |

## Tiempo de respuesta de Coordinación Nacional (ms; H4 ≤ 2.000) — otro dueño

| Propiedad | Iteración | Valor | Estimación | IC 95 % | Umbral | Outcome |
|---|---|---|---|---|---|---|
| P5 reconciliación (consultas) | it4 | 1000 | 40.561 | [40.504, 40.619] | ≤ 270 s | Satisfied with margin |
| P5 reconciliación (consultas) | it4 | 2000 | 41.598 | [41.467, 41.728] | ≤ 270 s | Satisfied with margin |
| P5 reconciliación (consultas) | it4 | 5000 | 44.597 | [44.496, 44.699] | ≤ 270 s | Satisfied with margin |
| P5 reconciliación (consultas) | it4 | 30000 | 83.006 | [82.195, 83.817] | ≤ 270 s | Satisfied with margin |

## Probabilidad de que una consulta necesite su reintento (nominal 1, peor caso) — otro dueño

| Propiedad | Iteración | Valor | Estimación | IC 95 % | Umbral | Outcome |
|---|---|---|---|---|---|---|
| P5 reconciliación (consultas) | it4 | 0 | 23.778 | [22.823, 24.733] | ≤ 270 s | Satisfied with margin |
| P5 reconciliación (consultas) | it4 | 0.5 | 31.798 | [30.783, 32.813] | ≤ 270 s | Satisfied with margin |
| P5 reconciliación (consultas) | it4 | 1 | 41.598 | [41.467, 41.728] | ≤ 270 s | Satisfied with margin |
