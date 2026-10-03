#!/usr/bin/env python3
"""Native conversion and disk-save regression tests, entirely in a temp project."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import struct
import threading
import time
import tempfile
import unittest
import zlib

MODULE=Path(__file__).resolve().parents[1]/'image_workshop.py'
spec=importlib.util.spec_from_file_location('workshop',MODULE)
w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)

def png(path,width,height,pixel):
    def chunk(tag,data):return struct.pack('>I',len(data))+tag+data+struct.pack('>I',zlib.crc32(tag+data))
    raw=b''.join(b'\0'+b''.join(bytes(pixel(x,y)) for x in range(width)) for y in range(height))
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',width,height,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b''))

def unpack(blob):
    assert blob[:8]==b'DHRR\x01\0\0@'
    out=bytearray();i=8
    while i<len(blob):
        t=blob[i];i+=1
        if t&128:out.extend([blob[i]]*((t&127)+3));i+=1
        else:out.extend(blob[i:i+t+1]);i+=t+1
    assert i==len(blob) and len(out)==16384
    return out

def bbox(raw):
    points=[]
    for y in range(192):
        base=((y&7)<<10)+((y&56)<<4)+(y//64)*40
        for x in range(560):
            if raw[base+((x//7)&1)*8192+x//14]&(1<<(x%7)):points.append((x,y))
    return (min(x for x,y in points),min(y for x,y in points),max(x for x,y in points)+1,max(y for x,y in points)+1)

class WorkshopTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name).resolve()
        self.original=w.ROOT;w.ROOT=self.root
        self.p=w.paths('SCOSWAMP','N001')
        png(self.p['source'],280,192,lambda x,y:(255,255,255) if 90<=x<190 and 46<=y<146 else (0,0,0))
        self.dest=self.root/'preview';self.dest.mkdir()
        self.recipe=copy.deepcopy(w.DEFAULTS);self.recipe['dither']=False
    def tearDown(self):w.ROOT=self.original;self.temp.cleanup()
    def test_fit_keeps_visual_square(self):
        w.convert(self.p['source'],'dhgr',self.recipe,self.dest)
        x0,y0,x1,y1=bbox(unpack((self.dest/'image.bin').read_bytes()))
        self.assertAlmostEqual((x1-x0)/2,y1-y0,delta=3)
        self.assertAlmostEqual((x0+x1)/4,140,delta=2)
    def test_all_dhgr_models_produce_complete_streams(self):
        for model in range(4):
            with self.subTest(model=model):
                self.recipe['model']=model
                w.convert(self.p['source'],'dhgr',self.recipe,self.dest)
                unpack((self.dest/'image.bin').read_bytes())
                self.assertEqual(w.dimensions(self.dest/'composite.png'),(560,192))
    def test_crop_zoom_and_hgr_output(self):
        self.recipe['crop']=[70,48,210,144]
        w.convert(self.p['source'],'dhgr',self.recipe,self.dest)
        x0,y0,x1,y1=bbox(unpack((self.dest/'image.bin').read_bytes()))
        self.assertGreater(x1-x0,380)
        w.convert(self.p['source'],'hgr',self.recipe,self.dest)
        self.assertEqual((self.dest/'image.bin').stat().st_size,8192)
        self.assertEqual(w.dimensions(self.dest/'composite.png'),(280,192))
    def test_save_replay_is_identical_and_preserves_master(self):
        self.recipe['crop']=[70,48,210,144];self.recipe['brightness']=1.23
        original=w.digest(self.p['source'])
        w.convert(self.p['source'],'dhgr',self.recipe,self.dest)
        expected=(self.dest/'image.bin').read_bytes()
        w.install(self.p,self.dest,self.recipe)
        self.assertEqual(self.p['output'].read_bytes(),expected)
        self.assertEqual(json.loads(self.p['recipe'].read_text()),self.recipe)
        w.replay('SCOSWAMP','N001')
        self.assertEqual(self.p['output'].read_bytes(),expected)
        self.assertEqual(w.digest(self.p['source']),original)
        self.assertGreaterEqual(self.p['output'].stat().st_mtime_ns,self.p['recipe'].stat().st_mtime_ns)
    def test_refuses_invalid_recipes_and_paths(self):
        for key,value in [('brightness',float('nan')),('gamma',8),('model',1.5),('dither',1),('crop',[-1,0,139,96]),('crop',[0,0,20,180])]:
            with self.subTest(key=key):
                recipe={**self.recipe,key:value}
                with self.assertRaises(ValueError):w.validate(recipe,280,192)
        with self.assertRaises(ValueError):w.paths('SCOSWAMP','../../N000')
        with self.assertRaises(ValueError):w.paths('OTHER','N000')
    def test_literal_boundaries_on_noise(self):
        png(self.p['source'],280,192,lambda x,y:((x*73+y*37)%256,(x*17+y*53)%256,(x*97+y*11)%256))
        self.recipe.update(stretch=True,dither=True)
        w.convert(self.p['source'],'dhgr',self.recipe,self.dest)
        unpack((self.dest/'image.bin').read_bytes())

class RegenerateTests(unittest.TestCase):
    """Le bouton de l'atelier : generate_images.sh reel, codex remplace par GEN_COMMAND."""
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name).resolve()
        self.original=(w.ROOT,w.manifest_row);w.ROOT=self.root
        tools=self.root/'SCOSWAMP.MORE/TOOLS';tools.mkdir(parents=True)
        shutil.copy(self.original[0]/'SCOSWAMP.MORE/TOOLS/generate_images.sh',tools)
        self.master=self.root/'SCOSWAMP.MORE/GENERATED/N421.png'
        png(self.master,280,192,lambda x,y:(0,0,0))
        self.fresh=self.root/'fresh.png';png(self.fresh,280,192,lambda x,y:(255,255,255))
        w.manifest_row=lambda game,asset:dict(scene=asset,prompt='un sentier',refs=[],
                                              source_png=f'SCOSWAMP.MORE/GENERATED/{asset}.png')
        self.env=os.environ.get('GEN_COMMAND')
    def tearDown(self):
        w.ROOT,w.manifest_row=self.original
        if self.env is None:os.environ.pop('GEN_COMMAND',None)
        else:os.environ['GEN_COMMAND']=self.env
        self.temp.cleanup()
    def run_job(self,command):
        os.environ['GEN_COMMAND']=command
        job=dict(state='running');self.assertTrue(w.REGEN.acquire(blocking=False))
        w.regenerate('SCOSWAMP','N421',job)
        self.assertTrue(w.REGEN.acquire(blocking=False),'le verrou doit etre rendu');w.REGEN.release()
        return job
    def test_new_master_replaces_old_which_is_kept(self):
        old=self.master.read_bytes()
        job=self.run_job(f'cat > /dev/null; cp "{self.fresh}" "$GEN_DEST"')
        self.assertEqual(job['state'],'done',job)
        self.assertEqual(self.master.read_bytes(),self.fresh.read_bytes())
        kept=list((self.master.parent/'.rejets').glob('N421.avant-*.png'))
        self.assertEqual([k.read_bytes() for k in kept],[old])
    def test_nothing_written_is_a_failure_and_master_survives(self):
        old=self.master.read_bytes()
        job=self.run_job('cat > /dev/null')
        self.assertEqual(job['state'],'failed',job)
        self.assertEqual(self.master.read_bytes(),old)
    def test_master_lost_mid_run_is_restored(self):
        # Comme un essai refuse deplace dans .rejets/ puis un codex tue : plus de master.
        old=self.master.read_bytes()
        job=self.run_job('cat > /dev/null; rm -f "$GEN_DEST"')
        self.assertEqual(job['state'],'failed',job)
        self.assertEqual(self.master.read_bytes(),old)
    def test_stopping_the_workshop_kills_codex_and_restores_master(self):
        old=self.master.read_bytes()
        # Le faux codex efface le master puis ecrirait le nouveau bien plus tard.
        os.environ['GEN_COMMAND']=f'cat > /dev/null; rm -f "$GEN_DEST"; sleep 3; cp "{self.fresh}" "$GEN_DEST"'
        job=dict(state='running');self.assertTrue(w.REGEN.acquire(blocking=False))
        worker=threading.Thread(target=w.regenerate,args=('SCOSWAMP','N421',job));worker.start()
        for _ in range(100):
            if w.RUNNING.get('proc') and not self.master.exists():break
            time.sleep(.05)
        self.assertFalse(self.master.exists(),'le faux codex devait avoir efface le master')
        t=time.time();w.stop_regeneration();worker.join(10)
        self.assertLess(time.time()-t,5);self.assertFalse(worker.is_alive())
        time.sleep(4)   # le codex tue ne doit plus rien ecrire
        self.assertEqual(self.master.read_bytes(),old)
        self.assertEqual(job['state'],'failed')
    def test_master_shown_during_its_regeneration(self):
        server=type('S',(),{})();p=w.paths('SCOSWAMP','N421')
        server.job=dict(game='SCOSWAMP',asset='N421',state='running')
        self.assertEqual(w.master_for(server,'SCOSWAMP','N421',p),self.master)
        backup=self.master.parent/'.rejets/N421.avant-20260101-000000.png';backup.parent.mkdir()
        shutil.copy(self.master,backup);self.master.unlink()
        self.assertEqual(w.master_for(server,'SCOSWAMP','N421',p),backup)
        server.job['state']='done'
        self.assertEqual(w.master_for(server,'SCOSWAMP','N421',p),self.master)
    def test_only_scoswamp_has_a_manifest(self):
        w.manifest_row=self.original[1]
        with self.assertRaises(ValueError):w.manifest_row('SPACETRIP','N001')

class PromptTests(unittest.TestCase):
    def test_prompt_is_the_batch_prompt(self):
        row=w.manifest_row('SCOSWAMP','N421')
        self.assertEqual(row['scene'],'N421')
        self.assertIn('T 421 Le sentier sur les Sables',row['prompt'])
        self.assertEqual(row['source_png'],'SCOSWAMP.MORE/GENERATED/N421.png')
        with self.assertRaises(ValueError):w.manifest_row('SCOSWAMP','B013')

if __name__=='__main__':unittest.main()
