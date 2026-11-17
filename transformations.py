import os

NATURE = {
    'data_flow': 'data flow',
    'control_command': 'control command',
    'dependency': 'dependency',
    'event_notification': 'event notification',
}


def _components(model):
    return [e for e in model.elements if e.__class__.__name__ == 'Component']


def _connectors(model):
    return [e for e in model.elements if e.__class__.__name__ == 'Connector']


def _crosses(link):
    return len({c.system.name for c in link.path}) > 1


def _boundary(connector):
    crossing = [link for link in connector.links if _crosses(link)]
    if not crossing:
        return 'No'
    if len(crossing) == len(connector.links):
        return 'Yes'
    return 'Yes (' + ', '.join(link.path[0].label for link in crossing) + ')'


# ─────────────────────────────────────────────
# Model-to-text: documentation
# ─────────────────────────────────────────────
def generate_connector_table(model, out):
    lines = [f'# Connectors of {model.name}', '',
             '| ID | Source → Target | Nature | Coupling | Information carried | Boundary |',
             '|----|-----------------|--------|----------|---------------------|----------|']
    for k in _connectors(model):
        paths = '; '.join(' → '.join(c.label for c in link.path) for link in k.links)
        natures = ', '.join(NATURE[n] for n in k.natures).capitalize()
        lines.append(f'| {k.name} | {paths} | {natures} | {k.coupling.capitalize()} '
                     f'| {k.info} | {_boundary(k)} |')
    with open(os.path.join(out, 'connectors.md'), 'w') as f:
        f.write('\n'.join(lines) + '\n')


# ─────────────────────────────────────────────
# Model-to-text: graphical representation
# ─────────────────────────────────────────────
def generate_view(model, out):
    lines = ['flowchart LR']
    for s in model.constituents:
        members = [c for c in _components(model) if c.system is s]
        if not members:
            continue
        lines.append(f'  subgraph {s.name}["{s.label}"]')
        for c in members:
            shape = f'[("{c.label} ({c.tier})")]' if c.tier == 'T4' else f'["{c.label} ({c.tier})"]'
            lines.append(f'    {c.name}{shape}')
        lines.append('  end')
    for k in _connectors(model):
        for link in k.links:
            for a, b in zip(link.path, link.path[1:]):
                lines.append(f'  {a.name} -->|{k.name}| {b.name}')
    with open(os.path.join(out, 'view.mmd'), 'w') as f:
        f.write('\n'.join(lines) + '\n')


# ─────────────────────────────────────────────
# Transformation to analysis: scenarios
# ─────────────────────────────────────────────
def _unavailability(factor):
    """Unavailability of a factor; a group of replicas uses the common-cause fraction beta
    (Laboratory 4): beta*U + ((1 - beta)*U)**n."""
    if factor.__class__.__name__ == 'Single':
        return 1 - factor.ref.availability / 100, factor.ref.name
    u = 1 - factor.alternatives[0].availability / 100
    b, n = factor.beta, len(factor.alternatives)
    name = ', '.join(r.name for r in factor.alternatives)
    return b * u + ((1 - b) * u) ** n, f'{name} (β = {b:g})'


def analyze(analysis):
    rows = []
    if analysis.metric == 'availability':
        terms = [_unavailability(f) for f in analysis.factors]
        total_u = sum(u for u, _ in terms)
        result = 1.0
        for u, _ in terms:
            result *= 1 - u
        result *= 100
        for u, name in terms:
            rows.append(f'| {name} | {u * 100:.4f} % | {u / total_u * 100:.0f} % |')
        header = ['| Factor | Unavailability | Share |', '|--------|----------------|-------|']
        hours = (100 - result) / 100 * 8760
        summary = f'Chain availability: **{result:.3f} %** ({hours:.1f} h/year)'
        met = round(result, 6) >= analysis.target
    else:
        result = sum(f.ref.latency for f in analysis.factors)
        for f in analysis.factors:
            rows.append(f'| {f.ref.name} | {f.ref.latency:g} ms |')
        header = ['| Stage | Budget |', '|-------|--------|']
        summary = f'Chain latency: **{result:g} ms**'
        met = round(result, 6) <= analysis.target
    verdict = 'met' if met else 'NOT met'
    return [f'## {analysis.name} (Scenario {analysis.scenario})', ''] + header + rows + \
           ['', f'{summary}; target {analysis.target:g}: **{verdict}**', '']


def generate_analysis(model, out):
    lines = [f'# Analysis of {model.name}', '']
    for a in model.analyses:
        lines += analyze(a)
    with open(os.path.join(out, 'analysis.md'), 'w') as f:
        f.write('\n'.join(lines))


# ─────────────────────────────────────────────
# Model-to-text [E]: quality scenarios and tactics, traced to the elements of the model
# ─────────────────────────────────────────────
def generate_scenarios(model, out):
    names = lambda elements: ', '.join(e.name for e in elements) or '—'
    lines = [f'# Quality scenarios and tactics of {model.name}', '',
             '| Scenario | Attribute | Source | Stimulus | Artifact | Environment | Response | Response measure |',
             '|----------|-----------|--------|----------|----------|-------------|----------|------------------|']
    for q in model.qualities:
        lines.append(f'| {q.name}: {q.label} | {q.attribute} | {q.source} | {q.stimulus} '
                     f'| {names(q.artifact)} | {q.environment} | {q.response} | {q.measure} |')
    lines += ['', '| Tactic or pattern | Scenario | Introduces | Changes |',
              '|-------------------|----------|------------|---------|']
    for t in model.tactics:
        lines.append(f'| {t.name}: {t.label} | {t.scenario.name} | {names(t.introduces)} '
                     f'| {names(t.changes)} |')
    with open(os.path.join(out, 'scenarios.md'), 'w') as f:
        f.write('\n'.join(lines) + '\n')


def apply_transformations(model, out):
    os.makedirs(out, exist_ok=True)
    generate_connector_table(model, out)
    generate_view(model, out)
    generate_analysis(model, out)
    if model.qualities:
        generate_scenarios(model, out)
