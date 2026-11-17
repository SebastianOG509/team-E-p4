"""Verification of a model in the five steps of Laboratory 5: abstraction and instantiation (the
model is read and checked against the metamodel and against sos.arch), graphing (graph by tier
and structural properties), simulation (scenarios with replications) and reporting.

  python verification.py models/fts-it1.arch      ->  out/fts-it1/
"""
import os
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import networkx as nx

from correspondence import check as check_correspondence
from metamodel import CORE_VERSION, create_metamodel, hops
from simulation import run_scenario
from transformations import apply_transformations

TIER_COLOR = {'T1': 'lightblue', 'T2': 'khaki', 'T3': 'lightgreen', 'T4': 'orange', 'T5': 'salmon'}


def _components(model):
    return [e for e in model.elements if e.__class__.__name__ == 'Component']


def _connectors(model):
    return [e for e in model.elements if e.__class__.__name__ == 'Connector']


# ─────────────────────────────────────────────
# Step 3. Graphing
# ─────────────────────────────────────────────
def draw_graph(model, out):
    """Graph of the model by tier (Laboratory 5). Several connectors between the same two
    components share one edge; the elements introduced by a tactic have a red border."""
    graph = nx.DiGraph()
    order = {s.name: i for i, s in enumerate(model.constituents)}
    for c in sorted(_components(model), key=lambda c: order[c.system.name]):
        graph.add_node(c.name, tier=c.tier, layer=-int(c.tier[1]))
    labels = {}
    for k in _connectors(model):
        for link in k.links:
            for a, b in hops(link.path):
                graph.add_edge(a.name, b.name)
                labels.setdefault((a.name, b.name), []).append(k.name.replace('E_K', 'K'))
    new = {e.name for t in model.tactics for e in t.introduces}
    plt.figure(figsize=(22, 13))
    pos = nx.multipartite_layout(graph, subset_key='layer', align='horizontal')
    arc = 'arc3,rad=0.15'
    nx.draw(graph, pos, with_labels=True, node_size=1500, font_size=7, arrows=True,
            connectionstyle=arc, edge_color='gray', linewidths=2,
            node_color=[TIER_COLOR[graph.nodes[n]['tier']] for n in graph.nodes],
            edgecolors=['red' if n in new else 'gray' for n in graph.nodes])
    text = {e: ks[0] if len(ks) == 1 else f'{ks[0]} +{len(ks) - 1}' for e, ks in labels.items()}
    nx.draw_networkx_edge_labels(graph, pos, text, connectionstyle=arc, font_size=5)
    plt.title(f'{model.name} — C&C graph by tier (T1 top, T5 bottom; red border: introduced by a tactic)')
    plt.savefig(os.path.join(out, 'graph.png'), dpi=110, bbox_inches='tight')
    plt.close()
    return graph


# ─────────────────────────────────────────────
# Structural properties, checked on the graph of the model
# ─────────────────────────────────────────────
def check_structure(model):
    """Rows (property, elements found, outcome). S1 and S2 are those of Laboratory 5; S2 uses the
    connectors that the class-1 workloads name, S3 and S4 are of team E."""
    rows, own = [], model.name
    for a in model.analyses:                                # S1, as in Laboratory 5
        if a.metric == 'availability':
            single = [f.ref.name for f in a.factors if f.__class__.__name__ == 'Single']
            rows.append((f'S1. Sin punto único de falla en la cadena de {a.scenario}',
                         ', '.join(single) or 'Ninguno', 'Violated' if single else 'Satisfied'))
    urgent = [w for s in model.scenarios for w in s.workloads if w.priority == 1 and w.via]
    if urgent:
        blocking = sorted({k.name for w in urgent for k in w.via if k.coupling == 'blocking'})
        rows.append(('S2. Sin conector blocking en la cadena de custodia (clase 1, E-QS1)',
                     ', '.join(blocking) or 'Ninguno', 'Violated' if blocking else 'Satisfied'))
        # S3. A server that the custody chain shares with blocking exchanges serves by priority.
        shared = {c for k in _connectors(model) if k.coupling == 'blocking'
                  for link in k.links for c in link.path}
        fifo = sorted({c.name for w in urgent for c in w.path
                       if c.capacity and c in shared and c.discipline != 'priority'})
        rows.append(('S3. Todo servidor que la cadena de custodia comparte con intercambios '
                     'blocking atiende por prioridad (E-QS1)',
                     ', '.join(fifo) or 'Ninguno', 'Violated' if fifo else 'Satisfied'))
    # S4. A notice that enters by the boundary reaches, as events and through a broker, every
    # service of the artifact of its scenario.
    events = nx.DiGraph()
    events.add_nodes_from(c.name for c in _components(model))
    for k in _connectors(model):
        if 'event_notification' in k.natures:
            events.add_edges_from((a.name, b.name) for link in k.links for a, b in hops(link.path))
    brokers = [c.name for c in _components(model) if c.role == 'broker']
    for q in model.qualities:
        entries = [link.path[-1].name for k in q.artifact
                   if k.__class__.__name__ == 'Connector' and 'event_notification' in k.natures
                   for link in k.links
                   if link.path[0].system.name != own and link.path[-1].system.name == own]
        services = [c.name for c in q.artifact if c.__class__.__name__ == 'Component'
                    and c.tier == 'T3' and c.system.name == own]
        if entries and services:
            cut = sorted(c for c in services if not any(
                nx.has_path(events, e, b) and nx.has_path(events, b, c)
                for e in entries for b in brokers))
            rows.append((f'S4. El aviso de frontera de {q.name} alcanza por el broker a los '
                         f'servicios de su artefacto', ', '.join(cut) or 'Ninguno',
                         'Violated' if cut else 'Satisfied'))
    return rows


# ─────────────────────────────────────────────
# Step 5. Reporting
# ─────────────────────────────────────────────
def number(value, unit):
    return f'{value:.1f}' if unit in ('events', 'ms') else f'{value:.3f}'


def measure_name(m):
    return f'{m.metric} {m.workload.name}' if m.workload else m.metric


def report(model, source, structure, simulations, out):
    lines = [f'# Verificación de {model.name}', '', f'Modelo: `{source}` (núcleo v{CORE_VERSION} '
             f'con extensiones [E]); corresponde a `sos.arch`.', '',
             '## Propiedades estructurales (análisis del grafo)', '',
             '| Propiedad | Elementos encontrados | Outcome |', '|---|---|---|']
    lines += [f'| {p} | {e} | {o} |' for p, e, o in structure]
    for s, results in simulations:
        varied = ', '.join(dict.fromkeys(r[0] for r in results if r[0])) or '—'
        lines += ['', f'## Escenario {s.label} ({s.name})', '',
                  f'Corrida {s.duration:g} s, calentamiento {s.warmup:g} s, {s.replications} réplicas '
                  f'(semillas 1–{s.replications}); parámetros variados, uno a la vez: {varied}', '',
                  '| Parámetro | Valor | Propiedad | Medida | Estimación | IC 95 % | Umbral | Outcome |',
                  '|---|---|---|---|---|---|---|---|']
        for name, value, m, mean, low, high, result in results:
            u = m.unit
            lines.append(f'| {name or "nominal"} | {"—" if value is None else f"{value:g}"} '
                         f'| {m.label or "—"} | {measure_name(m)} | {number(mean, u)} '
                         f'| [{number(low, u)}, {number(high, u)}] | ≤ {m.threshold:g} {u} | {result} |')
    with open(os.path.join(out, 'verification.md'), 'w') as f:
        f.write('\n'.join(lines) + '\n')


def verify(source):
    """Runs the five steps on one model and returns (model, structure, simulations)."""
    mm = create_metamodel()
    model = mm.model_from_file(source)                                      # Steps 1 and 2
    sos = os.path.join(os.path.dirname(os.path.abspath(source)), 'sos.arch')
    if model.name != 'SoS' and os.path.exists(sos):
        errors = check_correspondence(mm.model_from_file(sos), model)
        if errors:
            sys.exit(f'{source}: DIVERGES from sos.arch: ' + '; '.join(errors))
    out = os.path.join('out', os.path.splitext(os.path.basename(source))[0])
    apply_transformations(model, out)                   # connectors.md, view.mmd, analysis.md
    draw_graph(model, out)                                                  # Step 3
    structure = check_structure(model)
    simulations = [(s, run_scenario(s)) for s in model.scenarios]           # Step 4
    report(model, source, structure, simulations, out)                      # Step 5
    print(f'{source}: verification report written to {out}/verification.md')
    return model, structure, simulations


if __name__ == '__main__':
    for source in sys.argv[1:] or ['models/fts-it1.arch']:
        verify(source)
