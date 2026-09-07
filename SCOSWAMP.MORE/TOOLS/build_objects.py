#!/usr/bin/env python3
"""Compatibility entry point; edit SCOSWAMP/JSON/OBJECTS.json for object data."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools'))
from compile_objects import write_catalogues


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    args = parser.parse_args()
    game = args.root / 'SCOSWAMP'
    write_catalogues(game / 'JSON' / 'OBJECTS.json', game, 16, localized=True)


if __name__ == '__main__':
    main()
