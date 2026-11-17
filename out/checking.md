# Comprobación de la simulación contra casos de resultado conocido

Modelos mínimos escritos en el mismo lenguaje y ejecutados con el mismo motor (`simulation.py`); 10 réplicas, semillas 1–10. Una fila está «dentro» si el valor analítico cae en el IC 95 % de la simulación.

| Caso | Semántica | Punto | Medida | Analítico | Simulado | IC 95 % | Dentro |
|---|---|---|---|---|---|---|---|
| M/M/1: p99 = ln(100)/(µ − λ), µ = 100/s | núcleo v2.0 | W = 50 | p99_latency (ms) | 92.10 | 91.75 | [89.85, 93.64] | Sí |
| M/M/1: p99 = ln(100)/(µ − λ), µ = 100/s | núcleo v2.0 | W = 80 | p99_latency (ms) | 230.26 | 224.57 | [205.36, 243.78] | Sí |
| M/M/1: p99 = ln(100)/(µ − λ), µ = 100/s | núcleo v2.0 | W = 90 | p99_latency (ms) | 460.52 | 457.59 | [406.59, 508.59] | Sí |
| Almacén ante una caída de 600 s: recuperación = λ·600/(µ − λ), λ = 40/s, µ = 120/s | núcleo v2.0 (Lab. 5, §4.5) | nominal | lost (events) | 0.00 | 0.00 | [0.00, 0.00] | Sí |
| Almacén ante una caída de 600 s: recuperación = λ·600/(µ − λ), λ = 40/s, µ = 120/s | núcleo v2.0 (Lab. 5, §4.5) | nominal | recovery (s) | 300.00 | 299.02 | [296.37, 301.68] | Sí |
| Prioridad no expulsiva M/M/1 de dos clases (Cobham), λ = 10 y 70/s, µ = 100/s | [E] discipline priority | clase High | latencia media (ms) | 18.89 | 18.90 | [18.75, 19.05] | Sí |
| Prioridad no expulsiva M/M/1 de dos clases (Cobham), λ = 10 y 70/s, µ = 100/s | [E] discipline priority | clase Low | latencia media (ms) | 54.44 | 53.49 | [51.79, 55.18] | Sí |
| Almacén finito de 880 trabajos, 900 llegadas Poisson esperadas: E[(A − 880)+] | [E] store buffer | nominal | lost (events) | 24.50 | 22.50 | [9.58, 35.42] | Sí |
| Detección y conmutación: sondeo de 2 s, 3 ausencias, conmutación de 2 s | [E] period, misses, standby | nominal | detection (s) | 6.00 | 6.00 | [6.00, 6.00] | Sí |
| Detección y conmutación: sondeo de 2 s, 3 ausencias, conmutación de 2 s | [E] period, misses, standby | nominal | restore (s) | 7.00 | 7.12 | [6.73, 7.51] | Sí |
| Detección y conmutación: sondeo de 2 s, 3 ausencias, conmutación de 2 s | [E] period, misses, standby | nominal | lost (events) | 0.00 | 0.00 | [0.00, 0.00] | Sí |
| Lote de 40 consultas a 2/s con respuesta de 2 s, con y sin reintento | [E] count, retry, delay | nominal | completion (s) | 41.50 | 41.50 | [41.50, 41.50] | Sí |
| Lote de 40 consultas a 2/s con respuesta de 2 s, con y sin reintento | [E] count, retry, delay | W.retry = 0 | completion (s) | 21.50 | 21.50 | [21.50, 21.50] | Sí |

Resultado: todos los valores analíticos caen dentro de los intervalos.
