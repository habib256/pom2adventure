"""Decisions, masters and actual ProDOS packaging, using a temporary project."""
import base64
import io
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

from test_image_workshop import w, png


class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.original=w.ROOT
        w.ROOT=self.root=Path(self.temp.name).resolve()
        self.p=w.paths('SCOSWAMP','N001')
        png(self.p['source'],280,192,lambda x,y:(0,0,0))
        self.p['output'].parent.mkdir(parents=True)
        self.p['output'].write_bytes(b'original output')

    def tearDown(self):
        w.ROOT=self.original
        self.temp.cleanup()

    def decision(self,**extra):
        return dict(state='accepted',notes='Garder le cadrage',selected=True,
                    fingerprint=w.fingerprint(self.p),**extra)

    def post(self,path,body,previews=None):
        handler=object.__new__(w.Handler)
        data=json.dumps(body).encode()
        handler.path=path;handler.headers={'X-Workshop-Token':'test','Content-Length':str(len(data))}
        handler.rfile=io.BytesIO(data)
        handler.server=SimpleNamespace(csrf='test',previews=previews or {},job=None)
        response=[];handler.reply=lambda data,status=200:response.append((status,data))
        handler.do_POST()
        return response[0]

    def test_http_acceptance_requires_saved_candidate_for_this_image(self):
        body=dict(game='SCOSWAMP',asset='N001',**self.decision())
        self.assertEqual(self.post('/api/review',body)[0],400)
        preview=self.root/'preview';preview.mkdir();(preview/'image.bin').write_bytes(self.p['output'].read_bytes())
        item=dict(game='SCOSWAMP',asset='N001',source_hash=w.digest(self.p['source']),folder=preview)
        status,data=self.post('/api/review',dict(body,token='t'),{'t':item})
        self.assertEqual(status,200,data)
        (preview/'image.bin').write_bytes(b'unsaved proposal')
        self.assertEqual(self.post('/api/review',dict(body,token='t'),{'t':item})[0],400)
        item['asset']='N002'
        self.assertEqual(self.post('/api/review',dict(body,token='t'),{'t':item})[0],400)

    def test_decision_persists_and_changes_invalidate_acceptance(self):
        before=w.save_review('SCOSWAMP','N001',self.decision())
        detail=w.review_details('SCOSWAMP','N001')
        self.assertEqual(detail['state'],'accepted')
        self.assertEqual(detail['record']['notes'],'Garder le cadrage')
        self.assertEqual(base64.b64decode(detail['saved']),b'original output')
        self.p['output'].write_bytes(b'new output')
        self.assertEqual(w.review_details('SCOSWAMP','N001')['state'],'changed')
        self.assertEqual(w.review_records('SCOSWAMP')['N001'],before)
        self.p['output'].write_bytes(b'original output')
        self.p['recipe'].parent.mkdir(parents=True)
        self.p['recipe'].write_text('{}')
        self.assertEqual(w.review_details('SCOSWAMP','N001')['state'],'changed')

    def test_stale_decision_does_not_overwrite_another_review(self):
        body=self.decision()
        w.save_review('SCOSWAMP','N001',body)
        before=(self.root/'SCOSWAMP.MORE/IMAGE-REVIEW.json').read_bytes()
        self.p['source'].write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'modifiés ailleurs'):
            w.save_review('SCOSWAMP','N001',body)
        self.assertEqual((self.root/'SCOSWAMP.MORE/IMAGE-REVIEW.json').read_bytes(),before)

    def test_restore_master_keeps_replaced_variant_and_output(self):
        previous=self.p['source'].parent/'.rejets/N001.avant-20260101-000000.png'
        png(previous,280,192,lambda x,y:(255,255,255))
        old=self.p['source'].read_bytes()
        output=self.p['output'].read_bytes()
        w.restore_previous_master('SCOSWAMP','N001',w.fingerprint(self.p),'/'+str(previous.relative_to(self.root)))
        self.assertEqual(self.p['source'].read_bytes(),previous.read_bytes())
        self.assertEqual(self.p['output'].read_bytes(),output)
        self.assertTrue(any(p.read_bytes()==old for p in previous.parent.glob('*.png')))
        self.assertEqual(w.review_records('SCOSWAMP')['N001']['pending_master'],w.digest(self.p['source']))
        with self.assertRaisesRegex(ValueError,'introuvable'):
            w.restore_previous_master('SCOSWAMP','N001',w.fingerprint(self.p),'/elsewhere.png')

    def test_context_follows_battle_references_and_both_languages(self):
        for lang in ('FR','EN'):
            for page,body in [(1,'M 7 9 WOLF\nMI 224'),(224,'M 7 9 WOLF'),(3,'MI 1224')]:
                path=self.root/f'SCOSWAMP/TEXT{lang}/N{page//50*50:03d}/N{page:03d}.TXT'
                path.parent.mkdir(parents=True,exist_ok=True)
                path.write_text(f'T {page} Title {lang}\n\n{body}\n')
        contexts=w.scene_context('SCOSWAMP','B224')
        self.assertEqual([s['page'] for s in contexts],[1,224])
        self.assertEqual(contexts[0]['titles'],dict(FR='Title FR',EN='Title EN'))
        self.assertEqual([s['page'] for s in w.scene_context('SCOSWAMP','N001')],[1])

    def test_verification_reads_real_volume_and_detects_stale_packaging(self):
        # The real builder and reader must agree about N001.RLE.BIN -> N001.RLE.
        binary=self.root/'SCOSWAMP/SCOSWAMP.BIN'
        binary.write_bytes(b'\x60')
        dist=self.root/'dist';dist.mkdir()
        result=subprocess.run([str(self.original/'ADVKIT/TOOLS/build/build_prodos_volume'),
                               str(self.root/'SCOSWAMP'),str(self.original/'ADVKIT/TOOLS/prodos_boot.tmpl'),
                               str(dist/'SCOSWAMP.HDV')],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        expected=w.image_hashes('SCOSWAMP')
        self.assertEqual(w.verify_volume('SCOSWAMP',expected),dict(ok=True,checked=1,mismatches=[]))
        real_run=w.subprocess.run
        def build_noop(command,**kw):
            return subprocess.CompletedProcess(command,0,'','') if command[0]=='make' else real_run(command,**kw)
        with patch.object(w.subprocess,'run',side_effect=build_noop):
            status,data=self.post('/api/build',dict(game='SCOSWAMP'))
            self.assertEqual(status,200,data)
            self.assertEqual(data['verification']['checked'],1)
        self.p['output'].write_bytes(b'new saved bytes')
        stale=w.verify_volume('SCOSWAMP')
        self.assertFalse(stale['ok'])
        self.assertEqual(stale['mismatches'],['SCOSWAMP/DHGR/N000/N001.RLE.BIN'])
        with patch.object(w.subprocess,'run',side_effect=build_noop):
            status,data=self.post('/api/build',dict(game='SCOSWAMP'))
            self.assertEqual(status,400,data)
            self.assertNotIn('volume',data,'never offer a stale disk as verified')
        self.assertFalse(w.verify_volume('SCOSWAMP',expected)['ok'],'changes during build must fail too')
        self.p['output'].unlink()
        with self.assertRaisesRegex(ValueError,'Aucune image'):
            w.verify_volume('SCOSWAMP')


if __name__=='__main__':unittest.main()
