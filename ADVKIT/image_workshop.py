#!/usr/bin/env python3
"""Local, recipe-based image workshop. Same HgrConvert code as POM2.

Masters are never overwritten. A preview token binds source, recipe and exact
output bytes. Apply consumes that result, rather than converting it again.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import secrets
import shutil
import signal
import struct
import subprocess
import tempfile
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

ROOT = Path(__file__).resolve().parents[1]
CONVERTER = ROOT / 'ADVKIT/TOOLS/build/scoswamp_dhgr'
DEFAULTS = dict(colourNoise=.30, brightness=1., contrast=1., gamma=1.,
                diffusion=.7, kernel=1, model=1, dither=False, stretch=False, crop=None)
RANGES = dict(colourNoise=(0,1), brightness=(.3,2), contrast=(.4,2.5),
              gamma=(.4,2.5), diffusion=(0,1), kernel=(0,1), model=(0,3))
LOCK = threading.Lock()
# Une seule generation codex a la fois : elle dure plusieurs minutes et coute.
REGEN = threading.Lock()
# Le generate_images.sh en cours : arreter l'atelier doit l'arreter AVEC codex.
RUNNING = {}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def project(game):
    if game not in ('SCOSWAMP', 'SPACETRIP'):
        raise ValueError('Projet inconnu')
    return json.loads((Path(__file__).parent / f'project.{game.lower()}.json').read_text())


def paths(game, asset):
    p = project(game)
    if not re.fullmatch(r'[NB][0-9]{3}', asset):
        raise ValueError('Identifiant image invalide')
    def resolve(template):
        bucket = f'N{int(asset[1:]) // (p["bucket"] or 50) * (p["bucket"] or 50):03d}'
        target = (ROOT / template.replace('{IMG}', asset).replace('{BUCKET}', bucket)).resolve()
        if not target.is_relative_to(ROOT):
            raise ValueError('Chemin hors projet')
        return target
    master = next(i for i in p['images'] if i['id']=='master')
    native = next(i for i in p['images'] if i['type'] in ('dhgr','hgr-brut'))
    previews = [i for i in p['images'] if i['id'].startswith('preview-')]
    composite = next(i for i in previews if i['id'] in ('preview-composite','preview-hgr'))
    chat = next((i for i in previews if i['id']=='preview-chatmauve'), composite)
    return dict(source=resolve(master['chemin']), output=resolve(native['chemin']),
                composite=resolve(composite['chemin']), chat=resolve(chat['chemin']),
                recipe=ROOT/f'{game}.MORE/IMAGE-RECIPES/{asset}.json',
                mode='dhgr' if native['type']=='dhgr' else 'hgr')


def dimensions(source):
    with source.open('rb') as f: header=f.read(24)
    if header[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError('Master PNG requis')
    return struct.unpack('>II', header[16:24])


def validate(recipe, width, height):
    if not isinstance(recipe, dict) or set(recipe)!=set(DEFAULTS):
        raise ValueError('Recette incomplète ou réglages inconnus')
    for key, (lo,hi) in RANGES.items():
        v=recipe[key]
        if type(v) not in (float,int) or not math.isfinite(v) or not lo<=v<=hi:
            raise ValueError(f'{key}: hors limites')
        if key in ('kernel','model') and int(v)!=v:
            raise ValueError(f'{key}: entier requis')
    for key in ('dither','stretch'):
        if type(recipe[key]) is not bool: raise ValueError(f'{key}: booléen requis')
    crop=recipe['crop']
    if crop is not None:
        if not isinstance(crop,list) or len(crop)!=4 or any(type(v)!=int for v in crop):
            raise ValueError('Cadrage: quatre coordonnées entières requises')
        x0,y0,x1,y1=crop
        if not (0<=x0<x1<=width and 0<=y0<y1<=height):
            raise ValueError('Cadrage hors image')
        if abs((x1-x0)/(y1-y0)-280/192)>2/min(x1-x0,y1-y0):
            raise ValueError('Le cadrage doit conserver le ratio 35:24')
    return recipe


def convert(source, mode, recipe, dest, resample='bilinear'):
    validate(recipe,*dimensions(source))
    opts={k:v for k,v in recipe.items() if k!='crop'}
    if recipe['crop']:
        opts.update(zip(('cropX0','cropY0','cropX1','cropY1'),recipe['crop']))
    settings=dest/'options.txt'
    settings.write_text(''.join(f'{k} {int(v) if isinstance(v,bool) else v}\n' for k,v in opts.items()))
    # bilinear reste la ligne de commande historique ; area ajoute l'option.
    extra=[] if resample=='bilinear' else ['--resample',resample]
    result=subprocess.run([str(CONVERTER),'import',*extra,str(source),mode,str(settings),
                           str(dest/'image.bin'),str(dest/'composite.png'),str(dest/'chat.png')],
                          capture_output=True,text=True,timeout=180)
    if result.returncode: raise ValueError(result.stderr[-2000:] or 'Échec de conversion native')


def atomic_write(path, data):
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,name=tempfile.mkstemp(dir=path.parent,prefix='.'+path.name)
    try:
        with os.fdopen(fd,'wb') as f: f.write(data)
        os.replace(name,path)
    finally:
        if os.path.exists(name): os.unlink(name)


def install(p, folder, recipe):
    # Roll back the group if a filesystem write fails. Each file is atomic.
    writes={p['recipe']:(json.dumps(recipe,indent=2)+'\n').encode(),
            p['output']:(folder/'image.bin').read_bytes(),
            p['composite']:(folder/'composite.png').read_bytes(),
            p['chat']:(folder/'chat.png').read_bytes()}
    previous={path:path.read_bytes() if path.exists() else None for path in writes}
    try:
        for path,data in writes.items(): atomic_write(path,data)
    except OSError:
        for path,data in previous.items():
            if data is None: path.unlink(missing_ok=True)
            else: atomic_write(path,data)
        raise


def replay(game, asset, resample='bilinear'):
    p=paths(game,asset)
    recipe=json.loads(p['recipe'].read_text())
    with tempfile.TemporaryDirectory(prefix='image-replay-') as tmp:
        dest=Path(tmp)
        convert(p['source'],p['mode'],recipe,dest,resample)
        install(p,dest,recipe)


def manifest_row(game, asset):
    """La ligne de manifeste de CETTE image : le prompt et les planches du lot.

    Elle sort de build_manifest.py --only, pas d'une copie du prompt ici : le
    bouton de l'atelier et generate_images.sh doivent demander la meme image."""
    if game != 'SCOSWAMP':
        raise ValueError('Régénération codex : SCOSWAMP seulement')
    paths(game, asset)
    with tempfile.TemporaryDirectory(prefix='image-prompt-') as tmp:
        out = Path(tmp)/'row.jsonl'
        result = subprocess.run(['python3', str(ROOT/'SCOSWAMP.MORE/TOOLS/build_manifest.py'),
                                 '--root', str(ROOT), '--only', asset, '--output', str(out)],
                                capture_output=True, text=True, timeout=120)
        if result.returncode:
            raise ValueError((result.stdout+result.stderr).strip()[-500:] or 'Manifeste introuvable')
        return json.loads(out.read_text(encoding='utf-8'))


def regenerate(game, asset, job):
    """Remplace le master par une generation codex, dans un fil a part.

    generate_images.sh fait tout le reste, comme pour un lot : FORCE=1 copie
    d'abord l'ancien master dans GENERATED/.rejets/<id>.avant-*.png, le controle
    qualite refuse et relance, le moins mauvais revient si rien ne passe. Le DHGR
    du disque n'est PAS touche : on l'enregistre ensuite depuis l'atelier."""
    source = before = None
    try:
        row = manifest_row(game, asset)
        source = ROOT/row['source_png']
        before = digest(source) if source.exists() else None
        with tempfile.TemporaryDirectory(prefix='image-regen-') as tmp:
            manifest = Path(tmp)/'manifest.jsonl'
            manifest.write_text(json.dumps(row, ensure_ascii=False)+'\n', encoding='utf-8')
            # Son propre groupe de processus : un delai depasse ou l'arret de
            # l'atelier tue bash ET le codex qu'il a lance, qui sinon ecrirait
            # le master plus tard, sans que personne ne le sache.
            proc = subprocess.Popen(['bash', str(ROOT/'SCOSWAMP.MORE/TOOLS/generate_images.sh'), str(manifest), '1', '1'],
                                    cwd=ROOT, env={**os.environ, 'FORCE': '1'}, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, text=True, start_new_session=True)
            RUNNING.update(proc=proc, source=source, before=before)
            try:
                out, _ = proc.communicate(timeout=3600)
            except subprocess.TimeoutExpired:
                kill_group(proc)
                raise
            finally:
                RUNNING.clear()
        result = subprocess.CompletedProcess(proc.args, proc.returncode, out, '')
        log = (result.stdout+result.stderr).strip()
        job['log'] = log[-3000:]
        restore_master(source, before)
        lines = log.splitlines()
        after = digest(source) if source.exists() else None
        if result.returncode or after is None or after == before or any(l.startswith('ECHEC') for l in lines):
            job['state'] = 'failed'
            job['error'] = 'Aucun nouveau master : ' + (lines[-1] if lines else 'generate_images.sh muet')
        else:
            job['state'] = 'done'
            job['warning'] = next((l for l in lines if l.startswith('HORS')), None)
    except (ValueError, OSError, KeyError, subprocess.TimeoutExpired) as e:
        if source is not None: restore_master(source, before)
        job.update(state='failed', error=str(e))
    finally:
        job['finished'] = time.time()
        REGEN.release()


def kill_group(proc):
    try:
        os.killpg(proc.pid, signal.SIGTERM)
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL); proc.wait()
    except ProcessLookupError:
        pass


def stop_regeneration():
    """A l'arret de l'atelier : tuer la generation et rendre son master."""
    # Copie d'abord : une fois codex tue, le fil de generation vide RUNNING.
    running = dict(RUNNING)
    proc = running.get('proc')
    if proc and proc.poll() is None:
        kill_group(proc)
        restore_master(running['source'], running['before'])


def regenerating(server, game, asset):
    job = server.job
    return bool(job and job['state'] == 'running' and job['game'] == game and job['asset'] == asset)


def master_for(server, game, asset, p):
    """Le master a montrer. Pendant sa regeneration il peut manquer un instant
    (un essai refuse part dans .rejets/ avant le suivant) : on montre alors la
    copie de l'ancien que FORCE=1 a prise au depart."""
    if p['source'].exists() or not regenerating(server, game, asset):
        return p['source']
    kept = sorted((p['source'].parent/'.rejets').glob(f'{asset}.avant-*.png'))
    return kept[-1] if kept else p['source']


def restore_master(source, before):
    """generate_images.sh deplace un essai refuse dans .rejets/ AVANT d'en
    redemander un : interrompu la (delai depasse, codex tue), il laisse le jeu
    sans master. On remet alors la copie FORCE=1 de l'ancien."""
    if before is None or source.exists():
        return
    for kept in sorted((source.parent/'.rejets').glob(f'{source.stem}.avant-*.png'), reverse=True):
        if digest(kept) == before:
            shutil.copy2(kept, source)
            return


class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs): super().__init__(*args,directory=str(ROOT),**kwargs)
    def end_headers(self):
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        super().end_headers()
    def reply(self,data,status=200):
        blob=json.dumps(data).encode()
        self.send_response(status); self.send_header('Content-Type','application/json')
        self.send_header('Content-Length',str(len(blob))); self.end_headers(); self.wfile.write(blob)
    def do_GET(self):
        url=urlparse(self.path)
        if url.path=='/api/images':
            try:
                game=parse_qs(url.query).get('game',['SCOSWAMP'])[0]
                probe=paths(game,'N000'); assets=[]
                ids={s.stem for s in probe['source'].parent.glob('*.png')}
                if self.server.job and self.server.job['state']=='running' and self.server.job['game']==game:
                    ids.add(self.server.job['asset'])
                for asset in sorted(ids):
                    if not re.fullmatch(r'[NB][0-9]{3}',asset): continue
                    p=paths(game,asset);source=master_for(self.server,game,asset,p)
                    if not source.exists(): continue
                    assets.append(dict(id=asset,source='/'+str(source.relative_to(ROOT)),
                                       corrected=p['recipe'].exists()))
                self.reply(dict(assets=assets,defaults=DEFAULTS,mode=probe['mode'],csrf=self.server.csrf,
                                regenerable=game=='SCOSWAMP',job=self.server.job))
            except (ValueError,OSError) as e: self.reply(dict(error=str(e)),400)
        elif url.path=='/api/recipe':
            try:
                q=parse_qs(url.query); p=paths(q['game'][0],q['asset'][0])
                recipe=json.loads(p['recipe'].read_text()) if p['recipe'].exists() else DEFAULTS.copy()
                width,height=dimensions(master_for(self.server,q['game'][0],q['asset'][0],p));warning=None
                # Un master regenere n'a plus la composition que visait le cadrage.
                try: validate(recipe,width,height)
                except ValueError:
                    if recipe.get('crop') is None: raise
                    recipe={**recipe,'crop':None};validate(recipe,width,height)
                    warning='Cadrage enregistré hors du master actuel : retiré.'
                self.reply(dict(recipe=recipe,width=width,height=height,warning=warning))
            except (ValueError,OSError,KeyError) as e: self.reply(dict(error=str(e)),400)
        elif url.path=='/api/prompt':
            try:
                q=parse_qs(url.query);row=manifest_row(q['game'][0],q['asset'][0])
                self.reply(dict(prompt=row['prompt'],refs=row.get('refs',[])))
            except (ValueError,OSError,KeyError,subprocess.TimeoutExpired) as e: self.reply(dict(error=str(e)),400)
        elif url.path=='/api/regenerate':
            self.reply(dict(job=self.server.job))
        elif url.path.startswith('/api/preview/'):
            parts=url.path.split('/')
            if len(parts)!=5 or parts[3] not in self.server.previews or parts[4] not in ('composite.png','chat.png'):
                self.send_error(404); return
            data=(self.server.previews[parts[3]]['folder']/parts[4]).read_bytes()
            self.send_response(200); self.send_header('Content-Type','image/png')
            self.send_header('Content-Length',str(len(data))); self.end_headers(); self.wfile.write(data)
        else: super().do_GET()
    def do_POST(self):
        if self.headers.get('X-Workshop-Token')!=self.server.csrf:
            self.reply(dict(error='Session atelier invalide. Rechargez la page.'),403); return
        try:
            length=int(self.headers.get('Content-Length','0'))
            if not 0<length<=16384: raise ValueError('Requête trop grande ou vide')
            body=json.loads(self.rfile.read(length))
            if self.path in ('/api/convert','/api/apply'):
                # Pendant sa regeneration, le master de cette image change sous nos pieds.
                item=self.server.previews.get(body.get('token')) or {}
                game,asset=(body['game'],body['asset']) if self.path=='/api/convert' else (item.get('game'),item.get('asset'))
                if game and regenerating(self.server,game,asset):
                    raise ValueError(f'{asset} : régénération en cours, attendez le nouveau master')
            if self.path=='/api/convert':
                p=paths(body['game'],body['asset']); recipe=validate(body['recipe'],*dimensions(p['source']))
                # Bound CPU/memory use; UI queues one conversion at a time.
                with LOCK:
                    source_hash=digest(p['source'])
                    token=secrets.token_hex(16); dest=Path(self.server.cache.name)/token; dest.mkdir()
                    convert(p['source'],p['mode'],recipe,dest)
                    if digest(p['source'])!=source_hash: raise ValueError('Master modifié pendant la conversion')
                    self.server.previews[token]=dict(folder=dest,paths=p,recipe=recipe,source_hash=source_hash,
                                                    game=body['game'],asset=body['asset'],
                                                    previous=digest(p['output']) if p['output'].exists() else None)
                    while len(self.server.previews)>48:
                        old=next(iter(self.server.previews)); shutil.rmtree(self.server.previews.pop(old)['folder'])
                self.reply(dict(token=token,bytes=(dest/'image.bin').stat().st_size,
                                sha256=digest(dest/'image.bin'),composite=f'/api/preview/{token}/composite.png',
                                chat=f'/api/preview/{token}/chat.png'))
            elif self.path=='/api/apply':
                with LOCK:
                    item=self.server.previews.get(body['token'])
                    if item is None: raise ValueError('Aperçu expiré: relancez la conversion')
                    p=item['paths']
                    if digest(p['source'])!=item['source_hash']: raise ValueError('Master modifié: refaites un aperçu')
                    current=digest(p['output']) if p['output'].exists() else None
                    if current!=item['previous']: raise ValueError('Image modifiée ailleurs: refaites un aperçu')
                    install(p,item['folder'],item['recipe']); item['previous']=digest(p['output'])
                self.reply(dict(saved=str(p['output'].relative_to(ROOT)),sha256=item['previous']))
            elif self.path=='/api/regenerate':
                game,asset=body['game'],body['asset'];manifest_row(game,asset)
                if not REGEN.acquire(blocking=False):
                    raise ValueError(f"Une régénération est déjà en cours ({(self.server.job or {}).get('asset','?')})")
                # Toutes les cles des maintenant : le fil ne fait ensuite que changer
                # des valeurs, jamais la taille du dict qu'un GET est en train de lire.
                job=dict(game=game,asset=asset,state='running',started=time.time(),finished=None,log='',error=None,warning=None)
                self.server.job=job
                threading.Thread(target=regenerate,args=(game,asset,job),daemon=True).start()
                self.reply(dict(job=job))
            elif self.path=='/api/build':
                game=body['game']; project(game)
                command=['make','-C','SCOSWAMP/SRC','hdv'] if game=='SCOSWAMP' else ['python3','SPACETRIP/build_disk.py']
                with LOCK:
                    result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,timeout=240)
                if result.returncode: raise ValueError((result.stdout+result.stderr)[-3000:])
                self.reply(dict(volume='/dist/SCOSWAMP.HDV' if game=='SCOSWAMP' else '/dist/SPACETRIP.hdv'))
            else: self.reply(dict(error='Action inconnue'),404)
        except (ValueError,KeyError,OSError,subprocess.TimeoutExpired) as e:
            self.reply(dict(error=str(e)),400)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--port',type=int,default=8765)
    parser.add_argument('--replay',nargs=2,metavar=('GAME','ASSET'))
    parser.add_argument('--resample',choices=('bilinear','area'),default='bilinear')
    args=parser.parse_args()
    if args.replay: replay(*args.replay,args.resample); return
    server=ThreadingHTTPServer(('127.0.0.1',args.port),Handler)
    server.csrf=secrets.token_hex(24); server.previews={}; server.job=None
    with tempfile.TemporaryDirectory(prefix='image-workshop-') as cache:
        # Keep the path, not a second temporary directory owner.
        class Cache: name=cache
        server.cache=Cache()
        print(f'Atelier: http://127.0.0.1:{args.port}/ADVKIT/',flush=True)
        # kill (SIGTERM) passe par le meme chemin que Ctrl-C.
        signal.signal(signal.SIGTERM, lambda *_: (_ for _ in ()).throw(KeyboardInterrupt()))
        try: server.serve_forever()
        except KeyboardInterrupt: pass
        finally: stop_regeneration()

if __name__=='__main__': main()
