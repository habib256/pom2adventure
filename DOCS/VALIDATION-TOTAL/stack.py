"""Banc POM2 : le creux maximal de la pile C de TOTAL.

La pile logicielle de cc65 part de $BF00 vers le bas et rien ne la surveille.
On remplit d'un motif tout ce qui est au-dessus du bout froid du programme
(ONCE est mort une fois main() lance), on fait travailler TOTAL -- arbre de
dossiers, image DHGR, visionneuses, editeur, copie recursive, tri -- et on
relit : le premier octet change donne le creux.

    python3 DOCS/VALIDATION-TOTAL/stack.py
"""
import sys, os, re, time, shutil, tempfile, subprocess, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]; os.chdir(ROOT)
sys.path.insert(0, 'SCOSWAMP.MORE/TOOLS')
import playtest as pt
labels = {n: int(a, 16) for a, n in re.findall(r'al ([0-9A-F]+) \.(\w+)', pathlib.Path('SCOSWAMP/SRC/total.lbl').read_text())}
TOOLS = ROOT / 'SCOSWAMP.MORE/TOOLS'
LO, HI = labels['__ONCE_RUN__'], labels['__HIMEM__']
with tempfile.TemporaryDirectory(prefix='total-stack-') as work:
    work = pathlib.Path(work); stage = work / 'vol'
    for d in ('TOTAL', 'DHGR', 'SUB/DEEP'): (stage / d).mkdir(parents=True)
    shutil.copy('SCOSWAMP/PRODOS.SYS', stage); shutil.copy('dist/.floppy/TOTAL.SYSTEM.SYS', stage)
    for f in ('TOTAL.CODE.BIN', 'TOTAL.HELP.TXT', 'FORMAT.SYS.SYS'): shutil.copy('SCOSWAMP/TOTAL/' + f, stage / 'TOTAL')
    shutil.copy('SCOSWAMP/DHGR/N000/N000.RLE.BIN', stage / 'PIC.RLE.BIN')
    (stage / 'NOTE.TXT').write_bytes(b'hello world\r' * 40)
    for i in range(30): (stage / 'SUB' / f'F{i:02d}.TXT').write_bytes(b'x\r')
    for i in range(20): (stage / 'SUB/DEEP' / f'G{i:02d}.TXT').write_bytes(b'y\r')
    subprocess.run([str(TOOLS / 'build/build_prodos_volume'), str(stage), str(TOOLS / 'prodos_boot.tmpl'), str(work / 'STACK.hdv'), 'STACK'], check=True, capture_output=True)
    p = pt.Pom2(str(work / 'STACK.hdv'), port=6562)
    def value(name, n=2): return int.from_bytes(p.peek(labels['_total_' + name], n), 'little')
    def rows(): return p.screen()
    def has(n): return any(n in r for r in rows())
    def wait(f, what, s=30):
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
    def low_water():
        d = p.peek(LO, HI - LO)
        for i, b in enumerate(d):
            if b != 0xEE: return LO + i
        return HI
    try:
        p.start(); wait(lambda: has('Type  Aux     Size'), 'boot', 60); p.stable()
        p.poke(LO, bytes([0xEE]) * (HI - LO))
        print('motif pose, creux initial $%04X' % low_water(), flush=True)
        # arbre, images, visionneuses, editeur, copie, tri, marquage
        select(0, 'SUB'); key(b'\r'); wait(lambda: has('/STACK/SUB'), 'sub'); p.stable()
        select(0, 'DEEP'); key(b'\r'); wait(lambda: has('/STACK/SUB/DEEP'), 'deep'); p.stable()
        print('apres descente : $%04X' % low_water(), flush=True)
        key(b'\x1b'); wait(lambda: has('/STACK/SUB '), 'up'); key(b'\x1b'); wait(lambda: has('/STACK  '), 'root'); p.stable()
        select(0, 'PIC.RLE'); key(b'\r'); wait(lambda: value('view', 1) == 1, 'image', 40); time.sleep(1); key(b'\x1b')
        wait(lambda: value('view', 1) == 0, 'back'); p.stable()
        print('apres image DHGR : $%04X' % low_water(), flush=True)
        select(0, 'NOTE'); key(b'\r'); wait(lambda: value('view', 1) == 2, 'texte'); key(b' '); key(b'\x1b'); wait(lambda: value('view', 1) == 0, 'back')
        key(b'H'); wait(lambda: value('view', 1) == 3, 'hexa'); key(b' '); key(b'\x1b'); wait(lambda: value('view', 1) == 0, 'back')
        key(b'?'); wait(lambda: value('view', 1) == 4, 'aide'); key(b' '); wait(lambda: value('view', 1) == 0, 'back'); p.stable()
        print('apres visionneuses : $%04X' % low_water(), flush=True)
        key(b'E'); wait(lambda: value('view', 1) == 5, 'editeur'); p.keys('ABC'); key(b'\x1b'); wait(lambda: has('Quit without saving'), 'menu'); key(b'Q'); wait(lambda: has('Discard'), 'discard'); key(b'Y'); wait(lambda: value('view', 1) == 0, 'sortie'); p.stable()
        print('apres editeur : $%04X' % low_water(), flush=True)
        # copie d un dossier entier (parcours recursif, le plus profond)
        key(b'\t'); p.stable(); print('panneau droit :', rows()[0][40:60], flush=True); key(b'\t')
        select(0, 'SUB'); key(b'C'); wait(lambda: has('copied') or has('failed'), 'copie dossier', 120); p.stable()
        print('apres copie recursive : $%04X' % low_water(), flush=True)
        key(b'S'); p.stable(); key(b'S'); p.stable(); key(b'*'); p.stable(); key(b'M'); p.stable()
        w = low_water()
        print('CREUX FINAL : $%04X  (pile utilisee : %d octets sous $BF00)' % (w, 0xBF00 - w), flush=True)
    finally:
        p.stop()
