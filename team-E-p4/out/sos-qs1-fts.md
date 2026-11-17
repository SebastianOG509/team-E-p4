# SoS-QS1 (M4): fila bottom-up del Sistema de Transporte Fluvial

Presupuesto asignado al FTS por el acuerdo conjunto: reconciliación local ≤ 300 s desde el aviso «restablecido» (SoS-K35), repartido por el equipo en ≤ 270 s para consultas y reintentos y ≤ 30 s para aplicar los resultados (Entrega 2, §5.2).

Estímulo verificado (escenario `Recovery`): 40 unidades pendientes, 1 consulta por unidad por SoS-K19a/b detrás de un limitador de 2 intentos/s (P7), cada consulta necesita su único reintento (80 intentos, peor caso de H4), respuesta de la frontera NCS de 2 s, con la carga de recuperación H1 + H3 sobre el Traductor compartido.

| Iteración | Consultas y reintentos: estimación [IC 95 %] | Aplicar resultados (presupuesto, no simulado) | Reconciliación local | Presupuesto | Outcome |
|---|---|---|---|---|---|
| it1 | 41.526 [41.513, 41.539] s | 30 s | 71.5 s [71.5, 71.5] | ≤ 300 s | Satisfied with margin |
| it2 | 41.598 [41.467, 41.728] s | 30 s | 71.6 s [71.5, 71.7] | ≤ 300 s | Satisfied with margin |
| it3 | 41.598 [41.467, 41.728] s | 30 s | 71.6 s [71.5, 71.7] | ≤ 300 s | Satisfied with margin |
| it4 | 41.598 [41.467, 41.728] s | 30 s | 71.6 s [71.5, 71.7] | ≤ 300 s | Satisfied with margin |

## Fila para la tabla conjunta (modelo final, `fts-it4.arch`)

| Constituyente o conector | Presupuesto | Medida verificada | Técnica | Outcome |
|---|---|---|---|---|
| FTS: reconciliación local (M4) | ≤ 300 s | 71.6 s [71.5, 71.7] (41.598 s simulados + 30 s de presupuesto) | Simulación, 10 réplicas, IC 95 % | Satisfied with margin |
| FTS: consultas por SoS-K19a | ≤ 2 intentos/s y ≤ 80 intentos (P7, H4) | 2 intentos/s y 80 intentos | Por construcción: limitador del escenario (`rate 2 count 40 retry 1`) | Satisfied |
| FTS: recepción del aviso SoS-K35 por los servicios (S4) | Alcanzable por el broker | it1: Violated; it2–it4: Satisfied | Análisis del grafo | Satisfied |
| SoS-K19a/b: respuesta de la frontera NCS | ≤ 2 s por consulta | No verificada por el FTS: es un parámetro de Coordinación Nacional (entra como `delay NcsResponse`) | — | Not verifiable (otro dueño) |

## Sensibilidad a parámetros de otros dueños (modelo final)

| Parámetro | Dueño | Valor | Consultas: estimación [IC 95 %] | Reconciliación local | Outcome frente a 300 s |
|---|---|---|---|---|---|
| Tasa acordada P7 (intentos/s) | Acuerdo FTS–Coordinación Nacional | 0.25 | 318.020 [318.011, 318.030] s | 348.0 s | Violated |
| Tasa acordada P7 (intentos/s) | Acuerdo FTS–Coordinación Nacional | 0.5 | 160.021 [160.013, 160.029] s | 190.0 s | Satisfied with margin |
| Tasa acordada P7 (intentos/s) | Acuerdo FTS–Coordinación Nacional | 1 | 81.151 [81.032, 81.269] s | 111.2 s | Satisfied with margin |
| Tasa acordada P7 (intentos/s) | Acuerdo FTS–Coordinación Nacional | 2 | 41.598 [41.467, 41.728] s | 71.6 s | Satisfied with margin |
| Respuesta de la frontera NCS (ms) | Coordinación Nacional | 1000 | 40.561 [40.504, 40.619] s | 70.6 s | Satisfied with margin |
| Respuesta de la frontera NCS (ms) | Coordinación Nacional | 2000 | 41.598 [41.467, 41.728] s | 71.6 s | Satisfied with margin |
| Respuesta de la frontera NCS (ms) | Coordinación Nacional | 5000 | 44.597 [44.496, 44.699] s | 74.6 s | Satisfied with margin |
| Respuesta de la frontera NCS (ms) | Coordinación Nacional | 30000 | 83.006 [82.195, 83.817] s | 113.0 s | Satisfied with margin |
| Probabilidad de reintento | Coordinación Nacional y red | 0 | 23.778 [22.823, 24.733] s | 53.8 s | Satisfied with margin |
| Probabilidad de reintento | Coordinación Nacional y red | 0.5 | 31.798 [30.783, 32.813] s | 61.8 s | Satisfied with margin |
| Probabilidad de reintento | Coordinación Nacional y red | 1 | 41.598 [41.467, 41.728] s | 71.6 s | Satisfied with margin |
