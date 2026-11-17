"""Correspondence check between the joint model (sos.arch) and the model of a constituent, so that
boundary components and global connectors cannot diverge.

  python correspondence.py models/sos.arch models/fts-it1.arch [more models]

The constituent of a model is the one named as its system (system FTS -> constituent FTS).
  1. Every constituent of the model is declared in sos.arch with the same label and owner.
  2. Every boundary component of sos.arch that the model declares has the same label, constituent,
     tier, kind, availability and latency. The owner may add simulation properties to its own
     boundary component; a component of another constituent must exist in sos.arch, unchanged.
  3. Every global connector of sos.arch in which the constituent takes part is in the model, and
     every global connector in the model has the same ends, nature, coupling, information,
     agreement, availability and latency as in sos.arch.
  4. A connector of the model that crosses constituents is a global connector of sos.arch.
"""
import sys

from metamodel import create_metamodel

EXTRA = ('capacity', 'store', 'role', 'discipline', 'period', 'standby')   # not in the joint model


def _split(model):
    components = {e.name: e for e in model.elements if e.__class__.__name__ == 'Component'}
    connectors = {e.name: e for e in model.elements if e.__class__.__name__ == 'Connector'}
    return components, connectors


def _component(c):
    return {'label': c.label, 'constituent': c.system.name, 'tier': c.tier, 'kind': c.kind,
            'availability': c.availability, 'latency': c.latency}


def _connector(k):
    return {'ends': [[c.name for c in link.path] for link in k.links], 'nature': list(k.natures),
            'coupling': k.coupling, 'carries': k.info, 'agreement': k.agreement,
            'availability': k.availability, 'latency': k.latency}


def _differences(name, mine, joint):
    return [f'{name}: {field} is {mine[field]!r}, but sos.arch says {joint[field]!r}'
            for field in joint if mine[field] != joint[field]]


def check(sos, model):
    """Divergences of the model from the joint model; an empty list means they correspond."""
    own, errors = model.name, []
    joint = {s.name: s for s in sos.constituents}
    for s in model.constituents:
        if s.name not in joint:
            errors.append(f'{s.name}: constituent that sos.arch does not declare')
        elif (s.label, s.owner) != (joint[s.name].label, joint[s.name].owner):
            errors.append(f'{s.name}: label or owner differs from sos.arch')
    sos_c, sos_k = _split(sos)
    my_c, my_k = _split(model)
    for name, c in my_c.items():
        if name in sos_c:
            errors += _differences(name, _component(c), _component(sos_c[name]))
        if c.system.name != own:
            if name not in sos_c:
                errors.append(f'{name}: component of {c.system.name} that sos.arch does not declare')
            errors += [f'{name}: belongs to {c.system.name}, so {own} cannot give it {p}'
                       for p in EXTRA if getattr(c, p)]
    for name, c in sos_c.items():
        if c.system.name == own and name not in my_c:
            errors.append(f'{name}: boundary component of {own} missing in the model')
    for name, k in sos_k.items():
        takes_part = any(c.system.name == own for link in k.links for c in link.path)
        if takes_part and name not in my_k:
            errors.append(f'{name}: global connector of {own} missing in the model')
    for name, k in my_k.items():
        if name in sos_k:
            errors += _differences(name, _connector(k), _connector(sos_k[name]))
        elif any(len({c.system.name for c in link.path}) > 1 for link in k.links):
            errors.append(f'{name}: crosses constituents, but it is not a global connector of sos.arch')
    return errors


if __name__ == '__main__':
    mm = create_metamodel()
    sos, failed = mm.model_from_file(sys.argv[1]), False
    for source in sys.argv[2:]:
        errors = check(sos, mm.model_from_file(source))
        print(f'{source}: ' + ('corresponds to ' + sys.argv[1] if not errors else
                               'DIVERGES: ' + '; '.join(errors)))
        failed = failed or bool(errors)
    sys.exit(1 if failed else 0)
