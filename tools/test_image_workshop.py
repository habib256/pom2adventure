#!/usr/bin/env python3
"""Native conversion and disk-save regression tests, entirely in a temp project."""
import copy
import importlib.util
import json
from pathlib import Path
import struct
import tempfile
import unittest
import zlib

MODULE=Path(__file__).resolve().parents[1]/'SCOSWAMP.MORE/TOOLS/interpreter/image_workshop.py'
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

if __name__=='__main__':unittest.main()
