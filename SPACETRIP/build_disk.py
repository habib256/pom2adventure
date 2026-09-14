#!/usr/bin/env python3
"""Build SPACETRIP's engine, then its disk images in dist/.

    python3 SPACETRIP/build_disk.py

dist/SPACETRIP.hdv is the working image (POM2, the ADVKIT workshop);
dist/SPACETRIP.2mg carries the same ProDOS blocks behind a 2MG header, for
players and for emulators that will not guess a .hdv geometry.
"""
from pathlib import Path
import os
import shutil
import subprocess
import tempfile
ROOT=Path(__file__).resolve().parents[1]
subprocess.run(['sh','SPACETRIP/build.sh'],cwd=ROOT,check=True)
with tempfile.TemporaryDirectory(prefix='spacetrip-volume-') as temp:
    stage=Path(temp)/'SPACETRIP';stage.mkdir()
    for name in ('IMG','TXTFR','TXTEN'):
        shutil.copytree(ROOT/'SPACETRIP'/name,stage/name)
    for path in (ROOT/'SPACETRIP').iterdir():
        if path.suffix in ('.BIN','.SYS','.BAS','.TXT'): shutil.copy2(path,stage/path.name)
    out=Path(temp)/'SPACETRIP.hdv'
    subprocess.run([str(ROOT/'ADVKIT/TOOLS/build/build_prodos_volume'),str(stage),
                    str(ROOT/'ADVKIT/TOOLS/prodos_boot.tmpl'),str(out),'SPACETRIP'],check=True)
    # Same filesystem temporary destination for atomic replacement.
    (ROOT/'dist').mkdir(exist_ok=True)
    target=ROOT/'dist'/'SPACETRIP.hdv.tmp';shutil.copyfile(out,target);os.replace(target,ROOT/'dist'/'SPACETRIP.hdv')
subprocess.run(['python3',str(ROOT/'ADVKIT/TOOLS/wrap_2mg.py'),str(ROOT/'dist'/'SPACETRIP.hdv'),
                str(ROOT/'dist'/'SPACETRIP.2mg')],check=True)
