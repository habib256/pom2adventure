"""Banc POM2 : lancer un programme Applesoft depuis TOTAL.

X (ou Entree) sur un BAS charge BASIC.SYSTEM depuis la racine du volume et
lui passe le nom du programme en $2006, precede de sa longueur : c'est la
porte que tous ses lanceurs utilisent, Bitsy Bye compris, et BASIC.SYSTEM en
fait la commande "-NOM" a son demarrage. Le programme est range dans un
sous-dossier : le prefixe ProDOS doit donc partir sur ce dossier-la.

    python3 DOCS/VALIDATION-TOTAL/validate_basic.py
"""
import sys, os, re, time, shutil, tempfile, subprocess, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]; os.chdir(ROOT)
sys.path.insert(0, 'SCOSWAMP.MORE/TOOLS')
import playtest as pt
labels = {n: int(a, 16) for a, n in re.findall(r'al ([0-9A-F]+) \.(\w+)', pathlib.Path('SCOSWAMP/SRC/total.lbl').read_text())}
TOOLS = ROOT / 'SCOSWAMP.MORE/TOOLS'

def applesoft(lines):
    """lines : [(numero, bytes tokenises)] -> image memoire depuis $0801"""
    out = bytearray(); addr = 0x0801
    for num, toks in lines:
        body = bytes([num & 255, num >> 8]) + toks + b'\x00'
        addr += 2 + len(body)
        out += bytes([addr & 255, addr >> 8]) + body
    return bytes(out) + b'\x00\x00'

PRINT, HOME, END = 0xBA, 0x97, 0x80
prog = applesoft([(10, bytes([HOME])),
                  (20, bytes([PRINT]) + b'"TOTAL RUNS APPLESOFT"'),
                  (30, bytes([END]))])

with tempfile.TemporaryDirectory(prefix='total-bas-') as work:
    work = pathlib.Path(work); stage = work / 'vol'
    (stage / 'TOTAL').mkdir(parents=True); (stage / 'SUB').mkdir()
    shutil.copy('SCOSWAMP/PRODOS.SYS', stage); shutil.copy('dist/.floppy/TOTAL.SYSTEM.SYS', stage / 'A.TOTAL.SYSTEM.SYS')  # trie avant BASIC.SYSTEM : ProDOS amorce le premier .SYSTEM
    shutil.copy('SCOSWAMP/BASIC.SYSTEM.SYS', stage)
    for f in ('TOTAL.CODE.BIN', 'TOTAL.HELP.TXT', 'FORMAT.SYS.SYS'): shutil.copy('SCOSWAMP/TOTAL/' + f, stage / 'TOTAL')
    (stage / 'DHGR').mkdir()
    (stage / 'HELLO#FC0801').write_bytes(prog)
    (stage / 'SUB/DEEPHELLO#FC0801').write_bytes(prog)
    subprocess.run([str(TOOLS / 'build/build_prodos_volume'), str(stage), str(TOOLS / 'prodos_boot.tmpl'), str(work / 'BASTEST.hdv'), 'BASTEST'], check=True, capture_output=True)
    p = pt.Pom2(str(work / 'BASTEST.hdv'), port=6563)
    def rows(): return p.screen()
    def has(n): return any(n in r for r in rows())
    def wait(f, what, s=40):
        d = time.time() + s
        while time.time() < d:
            if f(): return
            time.sleep(.05)
        print('\n'.join(rows()), flush=True); raise AssertionError('timeout ' + what)
    def key(k): p.raw(k); time.sleep(.15)
    def cursor_row(x):
        main = p.peek(0x400, 1024); aux = p.peek(0x400, 1024, 'aux')
        for r in range(2, 20):
            base = 0x80*(r%8)+0x28*(r//8)
            if all(v < 0x80 for v in [aux[base+c//2] if c%2==0 else main[base+c//2] for c in range(x, x+16)]): return r
    def line(x):
        r = cursor_row(x); return rows()[r][x:x+38] if r is not None else ''
    def select(x, name):
        for _ in range(12): key(b'<')
        for _ in range(60):
            if line(x).startswith(name + ' '): return
            key(b'\x0a')
        raise AssertionError('cannot select ' + name)
    def ok(l, c, d=''):
        print(('PASS ' if c else 'FAIL ') + l, d, flush=True)
        if not c: raise AssertionError(l + ' ' + str(d))
    def rows40():
        m = p.peek(0x400, 1024); out = []
        for r in range(24):
            base = 0x80*(r%8)+0x28*(r//8)
            out.append(''.join(chr((b & 0x7f) if (b & 0x7f) >= 0x20 else 0x20) for b in m[base:base+40]))
        return out
    def has40(n): return any(n in r for r in rows40())
    try:
        p.start(); wait(lambda: has('Type  Aux     Size'), 'boot', 60); p.stable()
        ok('le volume demarre dans TOTAL', has('/BASTEST'))
        ok('HELLO est vu comme un BAS', any(r.startswith('HELLO ') and 'BAS' in r for r in rows()))
        select(0, 'SUB'); key(b'\r'); wait(lambda: has('/BASTEST/SUB'), 'sub'); p.stable()
        select(0, 'DEEPHELLO'); key(b'\r'); wait(lambda: has('Run DEEPHELLO?'), 'confirm')
        ok('Entree sur un BAS demande confirmation', has('Run DEEPHELLO?'), rows()[22].strip())
        key(b'Y'); wait(lambda: has40('TOTAL RUNS APPLESOFT'), 'applesoft', 60)
        ok('BASIC.SYSTEM lance le programme depuis un sous-dossier', has40('TOTAL RUNS APPLESOFT'))
        ok('Applesoft rend la main', any(r.startswith(']') for r in rows40()))
        print('--- ecran 40 col ---'); print('\n'.join(r.rstrip() for r in rows40() if r.strip()), flush=True)
    finally:
        p.stop()
