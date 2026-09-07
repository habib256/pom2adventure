"""Banc POM2 : une image DHGR detruit des blocs de /RAM, et lesquels.

Le disque virtuel de ProDOS vit en RAM auxiliaire ; la moitie auxiliaire
d'une page DHGR ($2000-$3FFF, banque AUX) lui appartient. Le banc ecrit un
fichier de 40 blocs sur /RAM, chaque bloc rempli de sa propre marque, releve
ou chaque marque atterrit en RAM auxiliaire, affiche une image DHGR, et
releve a nouveau. Les marques disparues sont les blocs perdus.

    python3 DOCS/VALIDATION-TOTAL/ram_dhgr.py
"""
import sys, os, re, time, shutil, tempfile, subprocess, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]; os.chdir(ROOT)
sys.path.insert(0, 'SCOSWAMP.MORE/TOOLS')
import playtest as pt
labels = {n: int(a, 16) for a, n in re.findall(r'al ([0-9A-F]+) \.(\w+)', pathlib.Path('SCOSWAMP/SRC/total.lbl').read_text())}
TOOLS = ROOT / 'SCOSWAMP.MORE/TOOLS'
NBLK = 40
MARKS = [('PAT%03d;' % i).encode() for i in range(NBLK)]

def ok(label, cond, detail=''):
    print(('PASS ' if cond else 'FAIL ') + label, detail, flush=True)
    if not cond: raise AssertionError(label + ' ' + str(detail))

with tempfile.TemporaryDirectory(prefix='total-ram-') as work:
    work = pathlib.Path(work); stage = work / 'vol'
    (stage / 'TOTAL').mkdir(parents=True)
    shutil.copy('SCOSWAMP/PRODOS.SYS', stage); shutil.copy('dist/.floppy/TOTAL.SYSTEM.SYS', stage)
    for f in ('TOTAL.CODE.BIN', 'TOTAL.HELP.TXT', 'FORMAT.SYS.SYS'): shutil.copy('SCOSWAMP/TOTAL/' + f, stage / 'TOTAL')
    (stage / 'PATTERN.BIN').write_bytes(b''.join((m * 64)[:512] for m in MARKS))
    shutil.copy('SCOSWAMP/DHGR/N000/N000.RLE.BIN', stage / 'PIC.RLE.BIN')
    shutil.copy('SPACETRIP/IMG/N001.HGR.BIN', stage / 'SIMPLE.BIN')   # page HGR brute : banque principale seule
    subprocess.run([str(TOOLS / 'build/build_prodos_volume'), str(stage), str(TOOLS / 'prodos_boot.tmpl'), str(work / 'DHGRRAM.hdv'), 'DHGRRAM'], check=True, capture_output=True)
    p = pt.Pom2(str(work / 'DHGRRAM.hdv'), port=6561)
    def value(name, n=2): return int.from_bytes(p.peek(labels['_total_' + name], n), 'little')
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
    def where():
        # peek() avance l'adresse de la taille DEMANDEE : lire page par page
        # et verifier, sinon un octet manquant decale tout le releve.
        d = bytearray(0xC000)
        for a in range(0x0200, 0xBF00, 0x100):
            b = p.peek(a, 0x100, 'aux')
            assert len(b) == 0x100, (hex(a), len(b))
            d[a:a+0x100] = b
        return {i: (d.find(m, 0x0200) if d.find(m, 0x0200) >= 0 else None) for i, m in enumerate(MARKS)}
    try:
        p.start(); wait(lambda: has('Type  Aux     Size'), 'boot', 60); p.stable()
        key(b'\t'); key(b'/'); wait(lambda: has('[Volumes]'), 'volumes'); select(40, '/RAM')
        key(b'\r'); wait(lambda: rows()[0][40:].startswith('/RAM '), 'ram'); key(b'\t'); p.stable()
        select(0, 'PATTERN'); key(b'C'); wait(lambda: has('copied') or has('failed'), 'copie', 120); p.stable()
        ok('les 40 blocs sont copies sur /RAM', has('1 file copied'), rows()[22].strip())
        before = {i: a for i, a in where().items() if a is not None}
        ok('les blocs se retrouvent en RAM auxiliaire', len(before) >= 36, '%d / %d' % (len(before), NBLK))
        page = sorted(i for i, a in before.items() if 0x2000 <= a < 0x4000)
        ok('une partie tombe dans la page DHGR auxiliaire $2000-$3FFF', len(page) > 8,
           '%d blocs, du %d au %d' % (len(page), page[0], page[-1]))
        select(0, 'PIC.RLE'); key(b'\r'); wait(lambda: value('view', 1) == 1, 'image', 40); time.sleep(1)
        key(b'\x1b'); wait(lambda: value('view', 1) == 0, 'retour', 30); p.stable()
        after = where()
        lost = sorted(i for i in before if after[i] is None)
        ok("l'affichage DHGR a detruit ces blocs de /RAM", len(lost) > 8, str(lost))
        ok('et seulement ceux de la page auxiliaire', set(lost) <= set(page), str(sorted(set(lost) - set(page))))
        print('%d blocs perdus (%d octets) ; HGR simple, qui n ecrit qu en banque '
              'principale, les laisserait intacts' % (len(lost), 512 * len(lost)), flush=True)
        # ... et TOTAL refait le volume a neuf en revenant, plutot que de
        # laisser un /RAM a moitie faux ou la prochaine ecriture derailerait.
        ok('TOTAL annonce avoir refait /RAM', has('/RAM was rebuilt empty'), rows()[22].strip())
        # Le pilote /RAM vit dans la banque 1 de la carte langage : l'appel
        # doit rendre a TOTAL sa banque 2, ou vivent l'aide, les
        # visionneuses et les saisies. Une touche qui y saute le prouve.
        key(b'?'); wait(lambda: value('view', 1) == 4, 'aide apres reformatage', 20)
        ok("l'aide s'ouvre encore : la carte langage est bien rendue", has('APPLE IIe TOTAL COMMANDER'))
        key(b' '); wait(lambda: value('view', 1) == 0, 'retour aide')
        p.stable()
        key(b'\t'); key(b'/'); wait(lambda: has('[Volumes]'), 'volumes'); p.stable()
        ram = [r[40:] for r in rows() if r[40:].startswith('/RAM ')]
        ok('/RAM est de nouveau un volume valide et vide', ram and '119/  127' in ram[0], ram[0] if ram else 'absent')
        select(40, '/RAM'); key(b'\r'); wait(lambda: rows()[0][40:].startswith('/RAM '), 'ram')
        p.stable()
        ok('et PATTERN n y est plus', not any('PATTERN' in r[40:] for r in rows()))
        # Une image HGR simple n'ecrit qu'en banque principale : elle ne doit
        # rien detruire, et donc ne rien refaire.
        key(b'\t'); select(0, 'PATTERN'); key(b'C'); wait(lambda: has('copied') or has('failed'), 'recopie', 120); p.stable()
        select(0, 'SIMPLE'); key(b'\r'); wait(lambda: value('view', 1) == 1, 'image HGR', 40); time.sleep(1)
        key(b'\x1b'); wait(lambda: value('view', 1) == 0, 'retour', 30); p.stable()
        ok('une image HGR simple ne touche pas a /RAM', not has('rebuilt'), rows()[22].strip())
        ok('le fichier de /RAM est intact', any(r[40:].startswith('PATTERN ') for r in rows()))
    finally:
        p.stop()
