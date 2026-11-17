"""Checking of the simulation against cases with a known result (Laboratory 5, §4.6), before any
result is accepted: one case for the core semantics and one for every extension of team E that
changes how jobs wait or are lost.

  python checking.py      ->  out/checking.md   (exit code 1 if an analytical value is outside)
"""
import math
import os
import sys

from metamodel import create_metamodel
from simulation import interval, run_scenario, simulate

HEAD = '''system Check
constituent X "Check" owner "Team E"
component A "Source" in X tier T3 kind software
component B "Buffer" in X tier T3 kind software {b}
component S "Server" in X tier T3 kind software {s}
component R "Standby" in X tier T3 kind software {r}
component D "Target" in X tier T3 kind software
connector K1 nature data_flow coupling sink carries "jobs" : A -> B -> S -> D
connector K2 nature data_flow coupling sink carries "jobs" : A -> S
connector K3 nature data_flow coupling sink carries "state" : S -> R
connector K4 nature dependency coupling blocking carries "query" : A -> D
'''


def model(scenario, b='', s='capacity 100', r=''):
    return create_metamodel().model_from_str(HEAD.format(b=b, s=s, r=r) + scenario).scenarios[0]


def rows_of(scenario, analytic):
    """One row per result of the scenario: analytic(parameter value, measure) is the known value."""
    rows = []
    for name, value, m, mean, low, high, _ in run_scenario(scenario):
        known = analytic(value, m)
        if known is not None:
            inside = low - 1e-6 <= known <= high + 1e-6
            rows.append((f'{name} = {value:g}' if name else 'nominal', m.metric, m.unit,
                         known, mean, low, high, inside))
    return rows


def mm1():
    """Core: M/M/1 queue, p99 of the response time = ln(100) / (mu - lambda)."""
    s = model('''scenario MM1 "M/M/1"
  workload W rate 50 : A -> S -> D
  vary W : 50, 80, 90
  measure p99_latency W <= 1000 ms
  run 600 warmup 30 replications 10
''')
    return [r for r in rows_of(s, lambda v, m: math.log(100) / (100 - v) * 1000 if v else None)]


def outage():
    """Core: store before a server that is down (Laboratory 5, scenario 4.5, at one tenth of its
    rates): recovery = lambda * outage / (mu - lambda)."""
    s = model('''scenario Outage "store and recovery"
  workload W rate 40 : A -> B -> S -> D
  fault S down at 60 for 600
  measure lost W <= 0 events
  measure recovery <= 300 s
  run 1100 warmup 0 replications 10
''', b='store', s='capacity 120')
    return rows_of(s, lambda v, m: 0 if m.metric == 'lost' else 40 * 600 / (120 - 40))


def priority():
    """[E] discipline priority: non-preemptive M/M/1 with two classes (Cobham), mean response
    time T1 = W0 / (1 - rho1) + 1/mu and T2 = W0 / ((1 - rho1)(1 - rho1 - rho2)) + 1/mu, with
    W0 = (lambda1 + lambda2) / mu**2."""
    s = model('''scenario Priority "priority queue"
  workload High rate 10 priority 1 : A -> S -> D
  workload Low rate 70 priority 2 : A -> S -> D
  measure p95_latency High <= 1000 ms
  run 600 warmup 30 replications 10
''', s='capacity 100 discipline priority')
    w0, rows = 80 / 100 ** 2, []
    known = {'High': w0 / 0.9 + 0.01, 'Low': w0 / (0.9 * 0.2) + 0.01}
    for name in known:
        means = []
        for seed in range(1, s.replications + 1):
            times = [j.t - j.start for j in simulate(s, seed).jobs
                     if j.workload == name and j.start >= s.warmup]
            means.append(sum(times) / len(times) * 1000)
        mean, low, high = interval(means)
        rows.append((f'clase {name}', 'latencia media', 'ms', known[name] * 1000, mean, low, high,
                     low <= known[name] * 1000 <= high))
    return rows


def finite_store():
    """[E] store buffer N: with A ~ Poisson(lambda * outage) arrivals during the outage, the jobs
    lost are (A - N)+, whose mean is the sum of (a - N) P(A = a)."""
    s = model('''scenario Buffer "finite store"
  workload W rate 0.5 : A -> B -> S -> D
  fault S down at 100 for 1800
  measure lost W <= 0 events
  run 2000 warmup 0 replications 10
''', b='store buffer 880')
    mu = 0.5 * 1800
    known = sum((a - 880) * math.exp(a * math.log(mu) - mu - math.lgamma(a + 1))
                for a in range(881, 1400))
    return rows_of(s, lambda v, m: known)


def switchover():
    """[E] period, misses, standby: the silence is declared `misses` periods after the last
    signal, whose age at the fault is uniform in [0, period): detection = misses * period, and
    restore has mean (misses - 1/2) * period + switch."""
    s = model('''scenario Switch "detection and switchover"
  workload W rate 50 : A -> B -> S -> D
  fault S down at 100 for 300
  measure detection <= 10 s
  measure restore <= 10 s
  measure lost W <= 0 events
  run 500 warmup 0 replications 10
''', b='store', s='capacity 100 period 2000 misses 3', r='capacity 100 standby S switch 2000')
    known = {'detection': 3 * 2.0, 'restore': 2.5 * 2.0 + 2.0, 'lost': 0}
    return rows_of(s, lambda v, m: known[m.metric])


def batch():
    """[E] count, retry, delay: N attempts behind a limiter of rate r, each answered after d;
    completion = (N (1 + p) - 1) / r + d when every attempt (p = 1) or none (p = 0) is retried."""
    s = model('''scenario Batch "rate limiter with retries"
  workload W rate 2 count 40 at 10 retry 1 : A -> D -> A
  delay Answer at D for 2000
  vary W.retry : 0
  measure completion W <= 300 s
  run 100 warmup 0 replications 10
''')
    return rows_of(s, lambda v, m: (40 * (1 + (1 if v is None else v)) - 1) / 2 + 2)


CASES = [('M/M/1: p99 = ln(100)/(µ − λ), µ = 100/s', 'núcleo v2.0', mm1),
         ('Almacén ante una caída de 600 s: recuperación = λ·600/(µ − λ), λ = 40/s, µ = 120/s',
          'núcleo v2.0 (Lab. 5, §4.5)', outage),
         ('Prioridad no expulsiva M/M/1 de dos clases (Cobham), λ = 10 y 70/s, µ = 100/s',
          '[E] discipline priority', priority),
         ('Almacén finito de 880 trabajos, 900 llegadas Poisson esperadas: E[(A − 880)+]',
          '[E] store buffer', finite_store),
         ('Detección y conmutación: sondeo de 2 s, 3 ausencias, conmutación de 2 s',
          '[E] period, misses, standby', switchover),
         ('Lote de 40 consultas a 2/s con respuesta de 2 s, con y sin reintento',
          '[E] count, retry, delay', batch)]


def check(out='out'):
    lines = ['# Comprobación de la simulación contra casos de resultado conocido', '',
             'Modelos mínimos escritos en el mismo lenguaje y ejecutados con el mismo motor '
             '(`simulation.py`); 10 réplicas, semillas 1–10. Una fila está «dentro» si el valor '
             'analítico cae en el IC 95 % de la simulación.', '',
             '| Caso | Semántica | Punto | Medida | Analítico | Simulado | IC 95 % | Dentro |',
             '|---|---|---|---|---|---|---|---|']
    ok = True
    for title, semantics, case in CASES:
        for point, metric, unit, known, mean, low, high, inside in case():
            ok = ok and inside
            lines.append(f'| {title} | {semantics} | {point} | {metric} ({unit}) | {known:.2f} '
                         f'| {mean:.2f} | [{low:.2f}, {high:.2f}] | {"Sí" if inside else "NO"} |')
    lines += ['', 'Resultado: ' + ('todos los valores analíticos caen dentro de los intervalos.'
                                   if ok else 'HAY VALORES ANALÍTICOS FUERA DE SU INTERVALO.')]
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, 'checking.md'), 'w') as f:
        f.write('\n'.join(lines) + '\n')
    return ok


if __name__ == '__main__':
    ok = check()
    print(open('out/checking.md').read())
    sys.exit(0 if ok else 1)
