"""Checks that every model of models/ is accepted and corresponds to sos.arch, and that every model
of invalid/ is rejected with the message of invalid/expected-rejections.txt.

  python test_invalid.py
"""
import glob
import sys

from textx import TextXError

from correspondence import check
from metamodel import create_metamodel


def rejection(mm, sos, source):
    """Message with which a model is rejected, or None when it is accepted."""
    try:
        errors = check(sos, mm.model_from_file(source))
    except TextXError as e:
        return e.message
    return '; '.join(errors) or None


if __name__ == '__main__':
    mm = create_metamodel()
    sos = mm.model_from_file('models/sos.arch')
    failed = 0
    for source in sorted(glob.glob('models/*.arch')):
        message = rejection(mm, sos, source)
        print(f'{"ok  " if message is None else "FAIL"} {source}: accepted' if message is None
              else f'FAIL {source}: {message}')
        failed += message is not None
    for line in open('invalid/expected-rejections.txt', encoding='utf-8'):
        if line.strip() and not line.startswith('#'):
            name, constraint, expected = (part.strip() for part in line.split('|'))
            message = rejection(mm, sos, f'invalid/{name}')
            ok = message is not None and expected in message
            print(f'{"ok  " if ok else "FAIL"} invalid/{name} [{constraint}]: {message or "ACCEPTED"}')
            failed += not ok
    listed = {l.split('|')[0].strip() for l in open('invalid/expected-rejections.txt', encoding='utf-8')}
    missing = [f for f in sorted(glob.glob('invalid/*.arch')) if f.split('/')[-1] not in listed]
    if missing:
        print('FAIL without expected rejection:', missing)
    sys.exit(1 if failed or missing else 0)
