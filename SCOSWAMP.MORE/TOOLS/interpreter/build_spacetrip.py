#!/usr/bin/env python3
"""Build SPACETRIP's current standalone engine and stage only disk assets."""
from pathlib import Path
import os
import shutil
import subprocess
import tempfile
ROOT=Path(__file__).resolve().parents[3]
subprocess.run(['sh','SPACETRIP/build.sh'],cwd=ROOT,check=True)
with tempfile.TemporaryDirectory(prefix='spacetrip-volume-') as temp:
    stage=Path(temp)/'SPACETRIP';stage.mkdir()
    for name in ('IMG','TXTFR','TXTEN'):
        shutil.copytree(ROOT/'SPACETRIP'/name,stage/name)
    for path in (ROOT/'SPACETRIP').iterdir():
        if path.suffix in ('.BIN','.SYS','.BAS','.TXT'): shutil.copy2(path,stage/path.name)
    out=Path(temp)/'SPACETRIP.hdv'
    subprocess.run([str(ROOT/'SCOSWAMP.MORE/TOOLS/build/build_prodos_volume'),str(stage),
                    str(ROOT/'SCOSWAMP.MORE/TOOLS/prodos_boot.tmpl'),str(out),'SPACETRIP'],check=True)
    # Same filesystem temporary destination for atomic replacement.
    target=ROOT/'SPACETRIP.hdv.tmp';shutil.copyfile(out,target);os.replace(target,ROOT/'SPACETRIP.hdv')
