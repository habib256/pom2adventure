import sys,tempfile,pathlib,types,json,re,hashlib
sys.path.insert(0,'SCOSWAMP.MORE/TOOLS')
import playtest as pt
root=pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else pathlib.Path('DOCS/PROFIL-PILES-V2')
if any(root.glob('*.log*')):
 raise SystemExit('Choisir un dossier neuf pour conserver les mesures existantes')
root.mkdir(parents=True,exist_ok=True)
provenance=json.loads((pathlib.Path(__file__).parent/'provenance.json').read_text())
args=types.SimpleNamespace(verbose=False,hdv=pt.HDV_SRC,port=6526,speed=200000,pom2='/tmp/scoswamp-stack-pom2/build/pom2_playtest',keep=False)
sym=pt.Symbols(pt.SRCDIR)
assert hashlib.sha256(pathlib.Path(args.pom2).read_bytes()).hexdigest()==provenance['instrumented_emulator_sha256']
assert hashlib.sha256(pathlib.Path(args.hdv).read_bytes()).hexdigest()==provenance['hdv_sha256']
assert sym['_main']==0x80f3 and sym['_exit']==0x400c
assert hashlib.sha256(pathlib.Path('SCOSWAMP/SCOSWAMP.BIN').read_bytes()).hexdigest()==provenance['game_sha256']
for name in ['demarrage','sac_combat','musique_aux','troc_alphonse','fin_transitions_175']:
 spec=next(s for s in pt.SCENARIOS if s['name']==name)
 with tempfile.TemporaryDirectory(prefix='scos-stack-') as work:
  print(name,flush=True)
  b=pt.run_one(spec,args,sym,work)
  raw=(pathlib.Path(work)/'pom2.log').read_text(errors='replace')
  (root/(name+'.log')).write_text(raw)
  maxima={kind:max([int(n) for n in re.findall(r'\[SCOS_STACK\] '+kind+r' used=(\d+)',raw)],default=None) for kind in ['hardware','c_call']}
  result=dict(scenario=name,assertions=b.ok,failures=b.failures,seconds=b.seconds,maxima=maxima)
  (root/(name+'.json')).write_text(json.dumps(result,indent=2)+'\n');print(result,flush=True)
  if b.failures or None in maxima.values():raise SystemExit(1)
