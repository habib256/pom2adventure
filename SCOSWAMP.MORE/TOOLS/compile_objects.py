#!/usr/bin/env python3
"""Compile editable objects, with explicit stable bits, to Apple II catalogues."""
import argparse
import json
import re
from pathlib import Path


def compile_objects(data, capacity):
    if data.get('schema') != 1:
        raise ValueError('unsupported object schema')
    rows = data.get('objects')
    if not isinstance(rows, list) or not 1 <= len(rows) <= capacity <= 32:
        raise ValueError('object catalogue exceeds backend capacity or is empty')
    ids, bits = set(), set()
    for row in rows:
        key, bit = row.get('id'), row.get('bit')
        if not isinstance(key, str) or not re.fullmatch(r'\.?[A-Z][A-Z0-9_]*', key):
            raise ValueError('invalid object id')
        if key in ids or type(bit) is not int or bit in bits or not 0 <= bit < len(rows):
            raise ValueError('duplicate id or non-contiguous bit positions')
        ids.add(key)
        bits.add(bit)
        if type(row.get('hidden')) is not bool or row['hidden'] != key.startswith('.'):
            raise ValueError('hidden flag must match object id prefix')
        labels = row.get('labels', {})
        for lang in ('FR', 'EN'):
            label = labels.get(lang)
            if not isinstance(label, str) or any(not 32 <= ord(c) <= 126 for c in label):
                raise ValueError('labels must contain printable ASCII')
            if label != label.strip() or (not row['hidden'] and not label):
                raise ValueError('visible objects require nonempty trimmed labels')
    ordered = sorted(rows, key=lambda row: row['bit'])
    hidden = False
    for row in ordered:
        if hidden and not row['hidden']:
            raise ValueError('visible objects must precede hidden flags')
        hidden |= row['hidden']
    return {lang: ''.join(f"{r['id']} {r['labels'][lang]}".rstrip() + '\n'
                         for r in ordered) for lang in ('FR', 'EN')}


def write_catalogues(source, output_dir, capacity, localized=False):
    result = compile_objects(json.loads(source.read_text()), capacity)
    for lang, content in result.items():
        path = (output_dir / f'TEXT{lang}' if localized else output_dir) / f'OBJ{lang}.TXT'
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists() or path.read_text() != content:
            path.write_text(content, encoding='ascii')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--capacity', type=int, required=True)
    parser.add_argument('--localized', action='store_true', help='Write catalogues under TEXTFR/TEXTEN')
    args = parser.parse_args()
    write_catalogues(args.source, args.output_dir, args.capacity, args.localized)


if __name__ == '__main__':
    main()
