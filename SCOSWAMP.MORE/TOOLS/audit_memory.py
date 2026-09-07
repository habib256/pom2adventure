#!/usr/bin/env python3
"""Mesures reproductibles du lien SCOSWAMP et de ses objets, sans relier le jeu.

python3 SCOSWAMP.MORE/TOOLS/audit_memory.py --output DOCS/MEMOIRE-SCOSWAMP.json
Les tailles de fonctions proviennent de listings assembles par ca65, pas
 de comptages de lignes C. Les bornes end_exclusive evitent les ambiguites.
"""
import argparse
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / 'SCOSWAMP/SRC'


def read_map(path):
    modules, segments = {}, {}
    section, module = '', None
    for line in path.read_text().splitlines():
        if line == 'Modules list:':
            section = 'modules'
        elif line == 'Segment list:':
            section = 'segments'
        elif line.startswith('Exports list'):
            section = ''
        elif section == 'modules':
            if line.endswith(':'):
                module = line[:-1]
                modules[module] = {}
            m = re.match(r'\s+(\w+)\s+Offs=([0-9A-F]+)\s+Size=([0-9A-F]+)', line)
            if m:
                name, offset, size = m.groups()
                modules[module][name] = dict(offset=int(offset, 16), size=int(size, 16))
        elif section == 'segments':
            m = re.match(r'(\w+)\s+([0-9A-F]{6})\s+([0-9A-F]{6})\s+([0-9A-F]{6})', line)
            if m:
                name, start, end, size = m.groups()
                start, end, size = (int(v, 16) for v in (start, end, size))
                assert start + size == end + 1
                segments[name] = dict(start=start, end_exclusive=end+1, size=size)
    generated = {}
    for seg, info in segments.items():
        used = sum(v.get(seg, {}).get('size', 0) for v in modules.values())
        assert used <= info['size'], seg
        if used < info['size']:
            generated[seg] = dict(offset=used, size=info['size']-used)
    modules['[linker tables]'] = generated
    return modules, segments


def listing(path, module, placements, segments):
    functions, allocations = [], []
    segment, proc, label = 'CODE', None, ''
    constants = {}
    for line in path.read_text().splitlines():
        m = re.match(r'([0-9A-F]{6})r?\s+\d+\s', line)
        if not m:
            continue
        offset = int(m[1], 16)
        equ = re.search(r'\b(\w+)\s*=\s*(\$[0-9A-Fa-f]+|\d+)(?:\s|$)', line)
        if equ:
            constants[equ[1]] = int(equ[2][1:],16) if equ[2].startswith('$') else int(equ[2])
        sm = re.search(r'\.segment\s+"(\w+)"', line)
        if sm:
            segment = sm[1]
        shorthand = re.search(r'\.(bss|code|rodata|data)\s*(?:;.*)?$', line)
        if shorthand:
            segment = shorthand[1].upper()
        pm = re.search(r'\.proc\s+(\w+)', line)
        if pm:
            proc = dict(name=pm[1], module=module, segment=segment,
                        offset=offset, calls=[])
        if proc:
            cm = re.search(r'\b(?:jsr|jmp)\s+(_\w+)', line)
            if cm and cm[1] not in proc['calls']:
                proc['calls'].append(cm[1])
        if '.endproc' in line and proc:
            assert segment == proc['segment']
            proc['size'] = offset - proc['offset']
            functions.append(proc)
            proc = None
        lm = re.search(r'\s([A-Za-z_]\w*):(?:\s|$)', line)
        if lm:
            label = lm[1]
        rm = re.search(r'\.res\s+(\$[0-9A-Fa-f]+|\w+)(?:,|\s|$)', line)
        if rm:
            raw = rm[1]
            size = constants[raw] if raw in constants else int(raw[1:], 16) if raw.startswith('$') else int(raw)
            allocations.append(dict(name=(proc['name']+'::' if proc else '')+label,
                                    module=module, segment=segment, offset=offset, size=size))
    for item in functions + allocations:
        item['start'] = segments[item['segment']]['start'] + placements[item['segment']]['offset'] + item['offset']
        item['end_exclusive'] = item['start'] + item['size']
    for seg in ('BSS', 'LOWBSS', 'MAPBSS'):
        assert sum(a['size'] for a in allocations if a['segment']==seg) == placements.get(seg, {}).get('size', 0), (module, seg)
    return functions, allocations


def experiments(output):
    source = (SRC/'scoswamp.c').read_text()
    flags = ['-t', 'apple2enh', '-O', '-Oirs', '-Cl', '--codesize', '100']
    variants = {
        'baseline_u8': (flags, source),
        'stone_arrays_enum16': (flags, source.replace('unsigned char shown[STONE_COUNT]', 'Stone shown[STONE_COUNT]').replace('unsigned char allowed[STONE_COUNT]', 'Stone allowed[STONE_COUNT]')),
        'codesize120': (flags[:-1]+['120'], source),
        'codesize150': (flags[:-1]+['150'], source),
        'codesize200': (flags[:-1]+['200'], source),
        'no_static_locals': ([x for x in flags if x != '-Cl'], source),
    }
    results = {}
    with tempfile.TemporaryDirectory(prefix='scoswamp-experiments-') as tmp:
        for name, (options, content) in variants.items():
            c = Path(tmp)/(name+'.c'); c.write_text(content)
            asm = c.with_suffix('.s'); obj = c.with_suffix('.o')
            subprocess.run(['cc65', *options, '-I', str(SRC), '-o', str(asm), str(c)], check=True)
            subprocess.run(['ca65', '-t', 'apple2enh', '-o', str(obj), str(asm)], check=True)
            dump = subprocess.check_output(['od65', '--dump-segments', str(obj)], text=True)
            results[name] = {n:int(v) for n,v in re.findall(r'Name:\s+"(\w+)".*?Size:\s+(\d+)', dump, re.S)}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(dict(source_sha256=hashlib.sha256(source.encode()).hexdigest(), variants=results), indent=2)+'\n')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--experiments', type=Path, help='compiler des variantes en fichiers temporaires')
    args = ap.parse_args()
    modules, segments = read_map(SRC / 'build.map')
    functions, allocations = [], []
    with tempfile.TemporaryDirectory(prefix='scoswamp-audit-') as tmp:
        for module, placements in modules.items():
            if '/' in module or module.startswith('['):
                continue
            source = SRC / (Path(module).stem + '.s')
            if not source.exists():  # iobuf archive extracted by the Makefile
                continue
            target = Path(tmp) / (source.stem + '.lst')
            subprocess.run(['ca65', '-t', 'apple2enh', '-l', str(target), '-o',
                            str(Path(tmp) / module), str(source)], check=True)
            f, a = listing(target, module, placements, segments)
            functions.extend(f)
            allocations.extend(a)
    bss = segments['BSS']
    symbols = {}
    for line in (SRC/'build.lbl').read_text().splitlines():
        m = re.match(r'al ([0-9A-Fa-f]+) \.([\w]+)$', line)
        if m:
            symbols[m[2]] = int(m[1],16)
    make = (SRC/'Makefile').read_text()
    himem = int(re.search(r'^HIMEM\s*=\s*(0x\w+)', make, re.M)[1],16)
    stack = int(re.search(r'^STACK\s*=\s*(0x\w+)', make, re.M)[1],16)
    binary = (SRC.parent/'SCOSWAMP.BIN').read_bytes()
    load_segments = ('STARTUP','LOWCODE','CODE','RODATA','DATA','INIT','ONCE','LC')
    lc_prefix = 3072 if 'crt0.o' in modules else 0
    lc_padding = lc_prefix - segments['LC']['size'] if lc_prefix else 0
    assert lc_padding >= 0
    assert sum(segments[s]['size'] for s in load_segments) + lc_padding == len(binary)
    graph = {f['name']: f['calls'] for f in functions if f['module'] in
             ('scoswamp.o','rules.o','dice.o','paths.o','messages.o','memory_swap.o')}
    cycles = set()
    def visit(name, path):
        if name in path:
            cycles.add(tuple(path[path.index(name):]+[name])); return
        for target in graph.get(name, []):
            if target in graph:
                visit(target, path+[name])
    for name in graph:
        visit(name, [])
    data = dict(lc_prefix_bytes=lc_prefix, main_load_start=0x4000,
                main_load_end_exclusive=0x4000 + len(binary)-lc_prefix,
                main_load_free_bytes=himem-(0x4000+len(binary)-lc_prefix),
                binary_bytes=len(binary), binary_sha256=hashlib.sha256(binary).hexdigest(),
                hdv_sha256=hashlib.sha256((ROOT/'dist/SCOSWAMP.HDV').read_bytes()).hexdigest(),
                compiler=subprocess.run(['cc65','--version'],capture_output=True,text=True).stderr.strip(),
                himem=himem, c_stack_reserved=stack, heap_start=bss['end_exclusive'],
                heap_end_exclusive=himem-stack, heap_bytes=himem-stack-bss['end_exclusive'],
                segments=segments, modules=modules,
                functions=sorted(functions,key=lambda f:f['size'],reverse=True),
                allocations=sorted(allocations,key=lambda a:a['size'],reverse=True),
                c_direct_call_cycles=sorted(cycles), exported_symbols=symbols)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(data,indent=2)+'\n')
    if args.experiments:
        experiments(args.experiments)
    print('Binaire:', len(binary),'octets ; tas:',data['heap_bytes'],'octets')
    print('Fonctions:', len(functions), '; allocations:', len(allocations), '; cycles C directs:',len(cycles))
    for f in data['functions'][:15]:
        print('%5d %-8s %s' % (f['size'],f['segment'],f['name']))


if __name__ == '__main__':
    main()
