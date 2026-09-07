"""Validate this binary's complete C-SP traces; fail rather than infer a peak."""
import gzip
import hashlib
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def analyze(raw, game):
    assert raw.count('[SCOS_CSP_READY] sp=BF00') == 1
    rows = [tuple(int(n, 16) for n in row) for row in re.findall(
        r'\[SCOS_CSP\] pc=(\w+) next=(\w+) before=(\w+) after=(\w+)', raw)]
    assert rows, 'No C stack trace'
    previous = 0xBF00
    for pc, next_pc, before, after in rows:
        assert before == previous, 'Unobserved SP change between instructions'
        previous = after
    # A raw minimum bounds all completed allocations. It is an attained peak
    # only if the instruction producing it completes a valid pointer update.
    peak = min(rows, key=lambda row: row[3])
    pc, next_pc, before, after = peak
    offset = 3072 + pc - 0x4000
    assert game[offset:offset + 3] == bytes.fromhex('c6 80 60'), 'Expected DEC sp; RTS'
    assert before & 255, 'Borrow would make this a split pointer update'
    assert after == before - 1 and next_pc == pc + 2
    assert 0x4000 <= after <= 0xBF00
    return dict(changes=len(rows), peak_bytes=0xBF00-after,
                peak_sp=f'{after:04X}', peak_pc=f'{pc:04X}',
                changed_pc_count=len({row[0] for row in rows}),
                high_byte_changes=sum((r[2] >> 8) != (r[3] >> 8) for r in rows))


if __name__ == '__main__':
    folder = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE
    provenance = json.loads((HERE / 'provenance.json').read_text())
    game = (ROOT / 'SCOSWAMP/SCOSWAMP.BIN').read_bytes()
    assert hashlib.sha256(game).hexdigest() == provenance['game_sha256']
    results = {}
    for name in ('demarrage', 'sac_combat', 'musique_aux', 'troc_alphonse', 'fin_transitions_175'):
        path = folder / (name + '.log')
        raw = path.read_text() if path.exists() else gzip.decompress(
            path.with_suffix('.log.gz').read_bytes()).decode()
        checks = json.loads((folder / (name + '.json')).read_text())
        assert not checks['failures']
        results[name] = analyze(raw, game)
    print(json.dumps(results, indent=2))
