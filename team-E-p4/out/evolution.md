# Evolución de las propiedades en las cuatro iteraciones

Estimación [IC 95 %] y outcome de cada propiedad con los parámetros nominales. En las propiedades estructurales se listan los elementos que las violan. «No evaluada»: el escenario de esa propiedad entra en una iteración posterior.

| Propiedad | it1 | it2 | it3 | it4 |
|---|---|---|---|---|
| S1. Sin punto único de falla en la cadena de E-QS3 (disponibilidad del Traductor) | TRA — **Violated** | — — **Satisfied** | — — **Satisfied** | — — **Satisfied** |
| S2. Sin conector blocking en la cadena de custodia (clase 1, E-QS1) | — — **Satisfied** | — — **Satisfied** | — — **Satisfied** | — — **Satisfied** |
| S3. Todo servidor que la cadena de custodia comparte con intercambios blocking atiende por prioridad (E-QS1) | TRA — **Violated** | — — **Satisfied** | — — **Satisfied** | — — **Satisfied** |
| S4. El aviso de frontera de SoSQS1 alcanza por el broker a los servicios de su artefacto | CON — **Violated** | — — **Satisfied** | — — **Satisfied** | — — **Satisfied** |
| P1a custodia p95 (≤ 30 s) | 1.169 [0.884, 1.454] s — **Satisfied with margin** | 0.157 [0.155, 0.159] s — **Satisfied with margin** | 0.157 [0.155, 0.159] s — **Satisfied with margin** | 0.157 [0.155, 0.159] s — **Satisfied with margin** |
| P2c posiciones nuevas p95 (≤ 15 s) | 1.158 [0.841, 1.475] s — **Satisfied with margin** | 0.100 [0.094, 0.106] s — **Satisfied with margin** | 0.100 [0.094, 0.106] s — **Satisfied with margin** | 0.100 [0.094, 0.106] s — **Satisfied with margin** |
| P3f turno K4 p95 (sin falla) (≤ 5 s) | 2.277 [1.623, 2.932] s — **Satisfied with margin** | 0.143 [0.134, 0.152] s — **Satisfied with margin** | 0.143 [0.134, 0.152] s — **Satisfied with margin** | 0.143 [0.134, 0.152] s — **Satisfied with margin** |
| P5 reconciliación (consultas) (≤ 270 s) | 41.526 [41.513, 41.539] s — **Satisfied with margin** | 41.598 [41.467, 41.728] s — **Satisfied with margin** | 41.598 [41.467, 41.728] s — **Satisfied with margin** | 41.598 [41.467, 41.728] s — **Satisfied with margin** |
| P2a posiciones perdidas (≤ 0 events) | 898.1 [879.8, 916.4] events — **Violated** | 0.0 [0.0, 0.0] events — **Satisfied with margin** | 0.0 [0.0, 0.0] events — **Satisfied with margin** | 0.0 [0.0, 0.0] events — **Satisfied with margin** |
| P2b persistencia del rezago (≤ 60 s) | 0.000 [0.000, 0.000] s — **Satisfied with margin** | 20.982 [19.860, 22.104] s — **Satisfied with margin** | 20.982 [19.860, 22.104] s — **Satisfied with margin** | 20.850 [19.948, 21.751] s — **Satisfied with margin** |
| P4 detección del silencio (≤ 35 s) | 2000.000 [2000.000, 2000.000] s — **Violated** | 35.000 [35.000, 35.000] s — **Satisfied without margin** | 35.000 [35.000, 35.000] s — **Satisfied without margin** | 29.000 [29.000, 29.000] s — **Satisfied with margin** |
| P3a traducción restablecida (≤ 10 s) | No evaluada | No evaluada | 6.983 [6.516, 7.450] s — **Satisfied with margin** | 6.983 [6.516, 7.450] s — **Satisfied with margin** |
| P3b turno K4 99,9 % (≤ 15 s) | No evaluada | No evaluada | 6.579 [6.030, 7.127] s — **Satisfied with margin** | 7.289 [6.702, 7.876] s — **Satisfied with margin** |
| P3c retiro K28 99,9 % (≤ 15 s) | No evaluada | No evaluada | 1.830 [1.417, 2.242] s — **Satisfied with margin** | 7.763 [7.025, 8.502] s — **Satisfied with margin** |
| P3d turnos K4 perdidos (≤ 0 events) | No evaluada | No evaluada | 0.0 [0.0, 0.0] events — **Satisfied with margin** | 0.0 [0.0, 0.0] events — **Satisfied with margin** |
| P3e retiros K28 perdidos (≤ 0 events) | No evaluada | No evaluada | 36.7 [32.1, 41.3] events — **Violated** | 0.0 [0.0, 0.0] events — **Satisfied with margin** |
| P1b custodia perdida (≤ 0 events) | No evaluada | No evaluada | 0.0 [0.0, 0.0] events — **Satisfied with margin** | 0.0 [0.0, 0.0] events — **Satisfied with margin** |
