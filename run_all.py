"""Runs the whole verification of Delivery 4 and writes every report of out/.

  python run_all.py

  1. conformance: the models are accepted, the ill-formed ones are rejected (test_invalid.py)
  2. checking of the simulation against known results           -> out/checking.md
  3. the four iterations (verification.py)                       -> out/fts-itN/
  4. evolution of every property across the iterations           -> out/evolution.md, .png
  5. sensitivity to the uncertain parameters                     -> out/sensitivity.md, .png
  6. bottom-up row of the FTS for SoS-QS1 (M4)                   -> out/sos-qs1-fts.md
"""
import os
import subprocess
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import checking
from metamodel import create_metamodel
from simulation import DEFAULT_ATTR, outcome
from transformations import apply_transformations
from verification import number, verify

ITERATIONS = ['it1', 'it2', 'it3', 'it4']
COLOR = {'Satisfied with margin': '#009E73', 'Satisfied': '#009E73',
         'Satisfied without margin': '#F0E442', 'Inconclusive': '#E69F00',
         'Violated': '#D55E00', None: '#DDDDDD'}
SHORT = {'Satisfied with margin': 'Satisfied\nwith margin', 'Satisfied': 'Satisfied',
         'Satisfied without margin': 'Satisfied\nwithout margin', 'Inconclusive': 'Inconclusive',
         'Violated': 'Violated', None: 'No evaluada'}


def cell(mean, low, high, unit):
    return f'{number(mean, unit)} [{number(low, unit)}, {number(high, unit)}] {unit}'


def nominal(results, it):
    """Nominal rows of an iteration: {property: (scenario, measure, mean, low, high, outcome)}."""
    return {m.label: (s, m, mean, low, high, result)
            for s, rows in results[it][2] for name, _, m, mean, low, high, result in rows
            if name is None}


def sweep(results, it, parameter, label):
    """Points (value, mean, low, high, outcome) of one property against one varied parameter,
    with the nominal point at the value the model gives to the parameter."""
    points = []
    for s, rows in results[it][2]:
        for v in s.varies:
            attr = v.attr or DEFAULT_ATTR[v.target.__class__.__name__]
            if parameter != (v.target.name if not v.attr else f'{v.target.name}.{attr}'):
                continue
            base = getattr(v.target, attr)
            for name, value, m, mean, low, high, result in rows:
                if m.label == label and name in (None, parameter):
                    points.append((base if name is None else value, mean, low, high, result))
    return sorted(points)


# ─────────────────────────────────────────────
# Evolution of the properties across the iterations
# ─────────────────────────────────────────────
def evolution(results, out):
    table = {}                                          # property -> {iteration: (text, outcome)}
    for it in ITERATIONS:
        for p, found, result in results[it][1]:
            table.setdefault(p, {})[it] = (found if result == 'Violated' else '—', result)
        for label, (_, m, mean, low, high, result) in nominal(results, it).items():
            table.setdefault(f'{label} (≤ {m.threshold:g} {m.unit})', {})[it] = \
                (cell(mean, low, high, m.unit), result)
    lines = ['# Evolución de las propiedades en las cuatro iteraciones', '',
             'Estimación [IC 95 %] y outcome de cada propiedad con los parámetros nominales. '
             'En las propiedades estructurales se listan los elementos que las violan. '
             '«No evaluada»: el escenario de esa propiedad entra en una iteración posterior.', '',
             '| Propiedad | ' + ' | '.join(ITERATIONS) + ' |', '|---|' + '---|' * len(ITERATIONS)]
    for p, cells in table.items():
        row = [f'{cells[it][0]} — **{cells[it][1]}**' if it in cells else 'No evaluada'
               for it in ITERATIONS]
        lines.append(f'| {p} | ' + ' | '.join(row) + ' |')
    with open(os.path.join(out, 'evolution.md'), 'w') as f:
        f.write('\n'.join(lines) + '\n')

    fig, ax = plt.subplots(figsize=(11, 0.55 * len(table) + 1.2))
    for y, (p, cells) in enumerate(table.items()):
        for x, it in enumerate(ITERATIONS):
            text, result = cells.get(it, ('', None))
            ax.add_patch(plt.Rectangle((x, y), 1, 1, facecolor=COLOR[result], edgecolor='white', lw=2))
            value = text.split(' [')[0] if '[' in text else ''
            ax.text(x + 0.5, y + 0.5, (value + '\n' if value else '') + SHORT[result],
                    ha='center', va='center', fontsize=7)
    ax.set_xlim(0, len(ITERATIONS)); ax.set_ylim(len(table), 0)
    ax.set_xticks([x + 0.5 for x in range(len(ITERATIONS))], ITERATIONS)
    ax.set_yticks([y + 0.5 for y in range(len(table))], [p[:70] for p in table], fontsize=7)
    ax.xaxis.tick_top(); ax.tick_params(length=0)
    for side in ax.spines.values():
        side.set_visible(False)
    ax.set_title('Outcome de cada propiedad por iteración (estimación nominal)', fontsize=10, pad=24)
    fig.savefig(os.path.join(out, 'evolution.png'), dpi=130, bbox_inches='tight')
    plt.close(fig)
    return table


# ─────────────────────────────────────────────
# Sensitivity to the uncertain parameters
# ─────────────────────────────────────────────
SWEEPS = [   # (parameter, description, [(property, iterations)], logarithmic axis)
    ('TRA', 'Capacidad del Traductor (operaciones/s; supuesto A1 = 100)',
     [('P1a custodia p95', ['it1', 'it2']), ('P3f turno K4 p95 (sin falla)', ['it1', 'it2']),
      ('P2c posiciones nuevas p95', ['it1', 'it2'])], True),
    ('UAB.period', 'Periodo del latido de la Unidad a Bordo (ms; E-QS6: 10.000)',
     [('P4 detección del silencio', ['it2', 'it4'])], False),
    ('BUF.buffer', 'Reserva del búfer a bordo (posiciones de los 5 convoyes; H2: 1.280 = 5 × 256 KiB)',
     [('P2a posiciones perdidas', ['it2'])], False),
    ('Reconcile', 'Tasa acordada de SoS-K19a (intentos/s; P7 = 2) — dueño: acuerdo con Coordinación Nacional',
     [('P5 reconciliación (consultas)', ['it4'])], False),
    ('NcsResponse', 'Tiempo de respuesta de Coordinación Nacional (ms; H4 ≤ 2.000) — otro dueño',
     [('P5 reconciliación (consultas)', ['it4'])], False),
    ('Reconcile.retry', 'Probabilidad de que una consulta necesite su reintento (nominal 1, peor caso) — otro dueño',
     [('P5 reconciliación (consultas)', ['it4'])], False),
]


def sensitivity(results, out):
    lines = ['# Análisis de sensibilidad', '',
             'Cada parámetro se varía solo, con los demás en su valor nominal (10 réplicas, '
             'semillas 1–10, las mismas en todos los puntos). La fila del valor nominal es la de '
             '`verification.md`.']
    fig, axes = plt.subplots(2, 3, figsize=(16, 8.5))
    for ax, (parameter, title, properties, log) in zip(axes.flat, SWEEPS):
        lines += ['', f'## {title}', '', '| Propiedad | Iteración | Valor | Estimación | IC 95 % | Umbral | Outcome |',
                  '|---|---|---|---|---|---|---|']
        for i, (label, its) in enumerate(properties):
            for it in its:
                _, m, *_ = nominal(results, it)[label]
                points = sweep(results, it, parameter, label)
                for value, mean, low, high, result in points:
                    lines.append(f'| {label} | {it} | {value:g} | {number(mean, m.unit)} '
                                 f'| [{number(low, m.unit)}, {number(high, m.unit)}] '
                                 f'| ≤ {m.threshold:g} {m.unit} | {result} |')
                xs = [p[0] for p in points]
                ax.errorbar(xs, [p[1] for p in points],
                            yerr=[[p[1] - p[2] for p in points], [p[3] - p[1] for p in points]],
                            marker='os^'[i], ls='-' if it != 'it1' else '--', capsize=3,
                            label=f'{label} ({it})')
            ax.axhline(m.threshold, color='#D55E00', ls=':', lw=1)
            ax.annotate(f'umbral {m.threshold:g} {m.unit}', (xs[0], m.threshold), fontsize=7,
                        color='#D55E00', va='bottom')
        if log:
            ax.set_yscale('log')
        ax.set_title(title.split(' — ')[0], fontsize=8)
        ax.set_xlabel(parameter, fontsize=8); ax.set_ylabel(m.unit, fontsize=8)
        ax.tick_params(labelsize=7); ax.grid(alpha=0.3); ax.legend(fontsize=6)
    fig.suptitle('Sensibilidad de las propiedades a los parámetros inciertos (media e IC 95 %)', fontsize=11)
    fig.tight_layout()
    fig.savefig(os.path.join(out, 'sensitivity.png'), dpi=130)
    plt.close(fig)
    with open(os.path.join(out, 'sensitivity.md'), 'w') as f:
        f.write('\n'.join(lines) + '\n')


# ─────────────────────────────────────────────
# Contribution of the FTS to SoS-QS1 (M4): bottom-up row
# ─────────────────────────────────────────────
def sos_qs1(results, out):
    label = 'P5 reconciliación (consultas)'
    model = results['it4'][0]
    con = next(e for e in model.elements if e.name == 'CON')
    budget = next(a for a in model.analyses if a.name == 'SoSQS1M4').factors[-1].ref.latency / 1000
    apply = con.latency / 1000
    lines = ['# SoS-QS1 (M4): fila bottom-up del Sistema de Transporte Fluvial', '',
             f'Presupuesto asignado al FTS por el acuerdo conjunto: reconciliación local ≤ {budget:g} s '
             f'desde el aviso «restablecido» (SoS-K35), repartido por el equipo en ≤ {budget - apply:g} s '
             f'para consultas y reintentos y ≤ {apply:g} s para aplicar los resultados (Entrega 2, §5.2).',
             '', 'Estímulo verificado (escenario `Recovery`): 40 unidades pendientes, 1 consulta por '
             'unidad por SoS-K19a/b detrás de un limitador de 2 intentos/s (P7), cada consulta necesita '
             'su único reintento (80 intentos, peor caso de H4), respuesta de la frontera NCS de 2 s, '
             'con la carga de recuperación H1 + H3 sobre el Traductor compartido.', '',
             '| Iteración | Consultas y reintentos: estimación [IC 95 %] | Aplicar resultados (presupuesto, no simulado) '
             '| Reconciliación local | Presupuesto | Outcome |', '|---|---|---|---|---|---|']
    for it in ITERATIONS:
        _, m, mean, low, high, _ = nominal(results, it)[label]
        lines.append(f'| {it} | {cell(mean, low, high, "s")} | {apply:g} s | {mean + apply:.1f} s '
                     f'[{low + apply:.1f}, {high + apply:.1f}] | ≤ {budget:g} s '
                     f'| {outcome(low + apply, high + apply, budget)} |')
    _, m, mean, low, high, result = nominal(results, 'it4')[label]
    s4 = {it: next((r for p, _, r in results[it][1] if p.startswith('S4')), '—') for it in ITERATIONS}
    lines += ['', '## Fila para la tabla conjunta (modelo final, `fts-it4.arch`)', '',
              '| Constituyente o conector | Presupuesto | Medida verificada | Técnica | Outcome |',
              '|---|---|---|---|---|',
              f'| FTS: reconciliación local (M4) | ≤ {budget:g} s | {mean + apply:.1f} s '
              f'[{low + apply:.1f}, {high + apply:.1f}] ({number(mean, "s")} s simulados + {apply:g} s de presupuesto) '
              f'| Simulación, 10 réplicas, IC 95 % | {outcome(low + apply, high + apply, budget)} |',
              f'| FTS: consultas por SoS-K19a | ≤ 2 intentos/s y ≤ 80 intentos (P7, H4) | 2 intentos/s y 80 intentos '
              f'| Por construcción: limitador del escenario (`rate 2 count 40 retry 1`) | Satisfied |',
              f'| FTS: recepción del aviso SoS-K35 por los servicios (S4) | Alcanzable por el broker '
              f'| it1: {s4["it1"]}; it2–it4: {s4["it4"]} | Análisis del grafo | {s4["it4"]} |',
              '| SoS-K19a/b: respuesta de la frontera NCS | ≤ 2 s por consulta | No verificada por el FTS: '
              'es un parámetro de Coordinación Nacional (entra como `delay NcsResponse`) | — | Not verifiable (otro dueño) |',
              '', '## Sensibilidad a parámetros de otros dueños (modelo final)', '',
              '| Parámetro | Dueño | Valor | Consultas: estimación [IC 95 %] | Reconciliación local | Outcome frente a 300 s |',
              '|---|---|---|---|---|---|']
    owners = [('Reconcile', 'Tasa acordada P7 (intentos/s)', 'Acuerdo FTS–Coordinación Nacional'),
              ('NcsResponse', 'Respuesta de la frontera NCS (ms)', 'Coordinación Nacional'),
              ('Reconcile.retry', 'Probabilidad de reintento', 'Coordinación Nacional y red')]
    for parameter, name, owner in owners:
        for value, mean, low, high, _ in sweep(results, 'it4', parameter, label):
            lines.append(f'| {name} | {owner} | {value:g} | {cell(mean, low, high, "s")} '
                         f'| {mean + apply:.1f} s | {outcome(low + apply, high + apply, budget)} |')
    with open(os.path.join(out, 'sos-qs1-fts.md'), 'w') as f:
        f.write('\n'.join(lines) + '\n')


if __name__ == '__main__':
    out = 'out'
    os.makedirs(out, exist_ok=True)
    if subprocess.call([sys.executable, 'test_invalid.py']):                # 1
        sys.exit('conformance checking failed')
    if not checking.check(out):                                             # 2
        sys.exit('the simulation does not reproduce the known results: see out/checking.md')
    print('out/checking.md: the analytical values fall inside the confidence intervals')
    apply_transformations(create_metamodel().model_from_file('models/sos.arch'), 'out/sos')
    results = {it: verify(f'models/fts-{it}.arch') for it in ITERATIONS}    # 3
    evolution(results, out)                                                 # 4
    sensitivity(results, out)                                               # 5
    sos_qs1(results, out)                                                   # 6
    print('out/evolution.md, out/sensitivity.md and out/sos-qs1-fts.md written')
