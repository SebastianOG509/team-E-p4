import os
from textx import metamodel_from_file, get_location, TextXSemanticError

CORE_VERSION = '2.0'   # Laboratory 4 (C1-C5) + Laboratory 5 (C6, C7); E1-E6 are of team E


def _error(message, obj):
    raise TextXSemanticError(message, **get_location(obj))


def _is(obj, cls):
    return obj.__class__.__name__ == cls


def hops(path):
    return list(zip(path, path[1:]))


def _boundary(connector):
    """A connector is a boundary connector when one of its links joins two constituents."""
    return any(len({c.system.name for c in link.path}) > 1 for link in connector.links)


def check_model(model):
    components = [e for e in model.elements if _is(e, 'Component')]
    connectors = [e for e in model.elements if _is(e, 'Connector')]

    for k in connectors:
        # C1. Every link joins at least two components.
        for link in k.links:
            if len(link.path) < 2:
                _error(f'{k.name}: a link must join at least two components', k)
        # C2. A control command has a single source with authority over its targets.
        if 'control_command' in k.natures:
            sources = {link.path[0].name for link in k.links}
            if len(sources) > 1:
                _error(f'{k.name}: control command with several sources {sorted(sources)}', k)
        # C3. Every boundary connector is governed by an agreement among owners.
        if _boundary(k) and not k.agreement:
            _error(f'{k.name}: boundary connector without agreement', k)
        for link in k.links:
            for a, b in hops(link.path):
                # C3 [E, reinforced; proposed to the core]. Boundary confinement: a hop that
                # crosses constituents joins two T2 components.
                if a.system is not b.system and (a.tier != 'T2' or b.tier != 'T2'):
                    _error(f'{k.name}: {a.name} ({a.tier}) -> {b.name} ({b.tier}) crosses '
                           f'constituents outside T2', k)
                if 'event_notification' in k.natures:
                    # E1 [E]. Event-driven style (FTS, Delivery 1, section 5.2): inside a
                    # constituent, a T3 service receives events only from a broker, and
                    # publishes them only to a broker or to a data store (T4).
                    if a.system is b.system and b.tier == 'T3' and a.role != 'broker':
                        _error(f'{k.name}: event delivered to service {b.name} (T3) by {a.name} '
                               f'({a.tier}), which is not a broker', k)
                    if a.tier == 'T3' and b.role != 'broker' and b.tier != 'T4':
                        _error(f'{k.name}: {a.name} (T3) publishes an event directly to {b.name} '
                               f'({b.tier}), which is neither a broker nor a data store', k)
                # E2 [E]. Client-server style (FTS, Delivery 1, section 5.3): a client of T1
                # requests only from services of T3.
                if 'dependency' in k.natures and a.tier == 'T1' and b.tier != 'T3':
                    _error(f'{k.name}: client {a.name} (T1) requests from {b.name} ({b.tier}), '
                           f'which is not a T3 service', k)

    for c in components:
        # C4. A data store (T4) is accessed by dependency from a single component.
        if c.tier == 'T4':
            users = {link.path[-2].name
                     for k in connectors if 'dependency' in k.natures
                     for link in k.links if link.path[-1] is c}
            if len(users) > 1:
                _error(f'{c.name}: data store shared by {sorted(users)}', c)
        # E6 [E]. A standby replaces a server whose silence can be detected.
        p = c.standby
        if p and not (c.capacity and p.capacity and p.period and p.misses):
            _error(f'{c.name}: standby of {p.name} needs a capacity, and {p.name} needs '
                   f'capacity, period and misses', c)

    # C5. Every element in an analysis carries the property the analysis needs.
    for a in model.analyses:
        for f in a.factors:
            for r in (f.alternatives if _is(f, 'Group') else [f.ref]):
                if not getattr(r, a.metric):
                    _error(f'{a.name}: {r.name} has no {a.metric} property', a)

    # E4 [E]. A tactic introduces or changes at least one element of the model.
    for t in model.tactics:
        if not t.introduces and not t.changes:
            _error(f'{t.name}: tactic for {t.scenario.name} introduces or changes no element', t)

    joined = {}                                  # connector -> hops it offers, in either direction
    for k in connectors:
        joined[k] = {(a, b) for link in k.links for a, b in hops(link.path)}
        joined[k] |= {(b, a) for a, b in joined[k]}
    any_hop = set().union(*joined.values()) if joined else set()
    for s in model.scenarios:
        own = {w.name: w for w in s.workloads}
        for w in s.workloads:
            # C6. Every hop of a workload follows a connector of the model, in either direction.
            for a, b in hops(w.path):
                if (a, b) not in any_hop:
                    _error(f'{s.name}: {w.name} goes from {a.name} to {b.name} without a connector', w)
            # E3 [E]. When a workload names its connectors, there is one per hop and it joins it.
            if w.via:
                if len(w.via) != len(w.path) - 1:
                    _error(f'{s.name}: {w.name} names {len(w.via)} connectors for '
                           f'{len(w.path) - 1} hops', w)
                for (a, b), k in zip(hops(w.path), w.via):
                    if (a, b) not in joined[k]:
                        _error(f'{s.name}: {w.name} goes from {a.name} to {b.name} via {k.name}, '
                               f'which does not join them', w)
            # E6 [E]. A triggered workload needs a component whose silence can be detected.
            if w.trigger and not (w.trigger.period and w.trigger.misses):
                _error(f'{s.name}: {w.name} is triggered by {w.trigger.name}, which has no '
                       f'period and misses', w)
        # C7. A component that fails in a scenario has a capacity ([E]: a connector may fail too).
        for f in s.faults:
            if _is(f.target, 'Component') and not f.target.capacity:
                _error(f'{s.name}: fault on {f.target.name}, which has no capacity', f)
        # E5 [E]. A measure declared of a quality scenario observes its artifact.
        for m in s.measures:
            if m.workload and m.workload.name not in own:
                _error(f'{s.name}: measure on {m.workload.name}, which is not a workload of '
                       f'this scenario', m)
            if m.quality and m.workload:
                w = own[m.workload.name]
                if not (set(w.path) | set(w.via)) & set(m.quality.artifact):
                    _error(f'{s.name}: {m.metric} {w.name} is declared of {m.quality.name}, '
                           f'but {w.name} does not traverse its artifact', m)


def create_metamodel():
    grammar = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'arch.tx')
    mm = metamodel_from_file(grammar)
    mm.register_model_processor(lambda model, metamodel: check_model(model))
    return mm
