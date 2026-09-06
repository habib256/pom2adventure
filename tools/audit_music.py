#!/usr/bin/env python3
"""Measure MB1 resident streams and validate the bytes consumed by the IRQ reader."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path


def inspect_stream(raw):
    if len(raw) < 9 or raw[:4] != b'MB1\0' or raw[4] != 50:
        raise ValueError('invalid MB1 header or tick rate')
    start = int.from_bytes(raw[6:8], 'little')
    if start != 8 or raw[5] not in (0, 1):
        raise ValueError('unsupported loop header')
    counts = Counter()
    cursor, ticks, burst, peak = start, 0, 0, 0
    while cursor < len(raw):
        op = raw[cursor]
        cursor += 1
        if 1 <= op <= 127:
            counts['delay'] += 1
            ticks += op
            peak = max(peak, burst)
            burst = 0
            continue
        burst += 1
        kind, voice = op & 0xf0, op & 0x0f
        if op == 0xe0:
            if cursor != len(raw):
                raise ValueError('bytes after END')
            counts['end'] += 1
            return {'bytes': len(raw), 'ticks': ticks, 'seconds': ticks / 50,
                    'loop': bool(raw[5]), 'commands': dict(counts),
                    'peak_commands_per_tick': max(peak, burst),
                    'sha256': hashlib.sha256(raw).hexdigest()}
        if op == 0xf0:
            counts['fade'] += 1
            continue
        if kind not in (0x80, 0x90, 0xa0, 0xb0) or voice >= 6:
            raise ValueError(f'invalid opcode {op:02x} at {cursor - 1}')
        counts[{0x80: 'note', 0x90: 'off', 0xa0: 'volume', 0xb0: 'noise'}[kind]] += 1
        if kind != 0x90:
            if cursor >= len(raw):
                raise ValueError('truncated operand')
            value = raw[cursor]
            cursor += 1
            if value > {0x80: 59, 0xa0: 15, 0xb0: 31}[kind]:
                raise ValueError('operand outside AY/table limits')
    raise ValueError('missing END')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--music-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    streams, errors = {}, []
    for path in sorted(args.music_dir.glob('*.MB.BIN')):
        try:
            streams[path.name] = inspect_stream(path.read_bytes())
        except ValueError as exc:
            errors.append(f'{path}: {exc}')
    if not streams:
        errors.append('no valid streams')
    result = {'format': 'MB1', 'streams': streams, 'errors': errors,
              'largest': sorted(streams, key=lambda n: streams[n]['bytes'], reverse=True)[:10],
              'total_disk_bytes': sum(s['bytes'] for s in streams.values())}
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(f'{len(streams)} streams, {len(errors)} errors, {result["total_disk_bytes"]} disk bytes')
    for name in result['largest']:
        print(name, streams[name]['bytes'], 'bytes,', streams[name]['peak_commands_per_tick'], 'commands/tick max')
    for error in errors:
        print(error)
    return bool(errors)


if __name__ == '__main__':
    raise SystemExit(main())
