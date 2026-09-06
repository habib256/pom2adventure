import sys,tempfile,pathlib,shutil,time,json,re,hashlib,gzip,urllib.request
sys.path.insert(0,'SCOSWAMP.MORE/TOOLS')
import playtest as pt
root=pathlib.Path('DOCS/VALIDATION-DIAPO-MUSIC')
labels={n:int(a,16) for a,n in re.findall(r'al ([0-9A-F]+) .(\w+)',pathlib.Path('SCOSWAMP/SRC/diapo.lbl').read_text())}
code=pathlib.Path('SCOSWAMP/DIAPO/DIAPO.CODE.BIN').read_bytes();off=3072+labels['_get_current_mode']-0x4000
assert code[off:off+3]==bytes.fromhex('a2 00 ad')
mode_addr=int.from_bytes(code[off+3:off+5],'little')
with tempfile.TemporaryDirectory(prefix='diapo-music-') as work:
 disk=pathlib.Path(work)/'TEST.hdv';shutil.copyfile(pt.HDV_SRC,disk);tested_hash=hashlib.sha256(disk.read_bytes()).hexdigest();p=pt.Pom2(str(disk),port=6526)
 checks=[]
 def value(name,n=1):return int.from_bytes(p.peek(labels['_diapo_'+name],n),'little')
 def wait(test):
  deadline=time.time()+60
  while time.time()<deadline:
   if test():return
   time.sleep(.03)
  raise AssertionError('Timed out: '+str(p.screen()))
 def screen40():
  m=p.peek(0x400,1024)
  return [''.join(p._cell(m[0x80*(r%8)+0x28*(r//8)+c]) for c in range(40)) for r in range(24)]
 def mode(n):return p.peek(mode_addr,1)==bytes([n])
 def shot(name):
  (root/(name+'.ppm')).write_bytes(urllib.request.urlopen(p.base+'/screen.ppm').read())
  (root/(name+'.txt')).write_text('\n'.join(p.screen()))
 def imagebytes():return p.peek(0x2000,8192,'aux')+p.peek(0x2000,8192)
 try:
  p.start();g=pt.Game(p,pt.Symbols(pt.SRCDIR));g.boot('F');g.press('Q');g.press('O')
  print('\n'.join(screen40()),flush=True)
  rows=screen40();row=next(i for i,r in enumerate(rows) if '/DIAPO' in r)
  p.raw(b'\x0a'*(row-2)+b'\r');time.sleep(.5)
  print('\n'.join(screen40()),flush=True)
  rows=screen40();row=next(i for i,r in enumerate(rows) if r.startswith('- DIAPO.SYSTEM '))
  p.rq('/speed',{'preset':'1x'})
  p.raw(b'\x0a'*(row-2)+b'\r')
  wait(lambda:any('PLEASE WAIT' in r for r in p.screen()))
  checks.append('PLEASE WAIT displayed by launcher before loading DIAPO')
  p.rq('/speed',{'cycles_per_frame':200000})
  wait(lambda:any('RETURN start slideshow' in r for r in p.screen()))
  assert value('total',2)==453 and value('slot')==2
  p.stable(need=12)
  shot('title');checks.append('Bitsy Bye DIAPO/DIAPO.SYSTEM, English 80-column title, 453 images, Mockingboard slot 2')
  p.rq('/speed',{'preset':'1x'});p.raw(b'\r');wait(lambda:value('index',2)==1 and mode(1));time.sleep(.1)
  # LEFT wraps first->last; RIGHT wraps last->first; both directions preserve mode.
  p.raw(b'\x08');wait(lambda:value('index',2)==453 and mode(1))
  p.raw(b'\x15');wait(lambda:value('index',2)==1 and mode(1))
  p.raw(b'\x15');wait(lambda:value('index',2)==2)
  p.raw(b'\x08');wait(lambda:value('index',2)==1)
  checks.append('LEFT/RIGHT previous/next including first/last wrap')
  original=imagebytes();shot('full')
  records=pathlib.Path('SCOSWAMP/DIAPO/DIAPO.IMAGES.BIN').read_bytes()
  expected_title=records[64:144].split(b'\0')[0].decode('ascii')
  first_path=records[:64].split(b'\0')[0].decode('ascii');ident=pathlib.Path(first_path).name[1:4]
  source=pathlib.Path(f'SCOSWAMP/TEXTEN/N{int(ident)//50*50:03}/N{ident}.TXT').read_text()
  assert expected_title==re.match(r'T\s+\d{3}\s+(.+)',source).group(1)

  p.raw(b' ');wait(lambda:value('mixed')==1 and mode(2));wait(lambda:p.screen()[20].strip()==expected_title);shot('mixed')
  checks.append('Mixed footer combat image title matches T of its Nxxx scene')
  p.raw(b' ');wait(lambda:value('mixed')==0 and mode(1));assert original==imagebytes()
  p.raw(b'M');wait(lambda:value('menu')==1 and any('MOCKINGBOARD MUSIC' in r for r in p.screen()))
  index=value('index',2);time.sleep(5.2);assert value('index',2)==index
  wait(lambda:any('ARROWS select' in r for r in p.screen()))
  rows=p.screen();assert rows[5][3:7]=='STOP' and rows[5][29:52].strip() and rows[5][55:78].strip()
  draws=value('menu_draws',2)
  shot('music');p.raw(b'\x0a\r');wait(lambda:value('track')==1 and value('menu')==0 and mode(1));assert original==imagebytes()
  # IRQ stream advances while image remains displayed (AUX residency equals track).
  mb=sorted(pathlib.Path('SCOSWAMP/MUSIC').glob('*.MB.BIN'))[0].read_bytes()
  assert p.peek(0x1000,len(mb),'aux')==mb
  start=3072+labels['_music_play']-0x4000
  playcode=code[start:start+100];cursor_pattern=playcode.index(bytes.fromhex('69 08 8d'))
  cursor_addr=int.from_bytes(playcode[cursor_pattern+3:cursor_pattern+5],'little')
  cursor_before=p.peek(cursor_addr,2);time.sleep(.3);assert p.peek(cursor_addr,2)!=cursor_before
  checks.append('Mockingboard IRQ advances the music stream during fullscreen display')
  checks.append('SPACE full/mixed/full preserves all 16384 image bytes; M freezes slide timer; First English track selected and loaded in AUX')
  p.raw(b'M');wait(lambda:value('menu')==1 and any('ARROWS select' in r for r in p.screen()))
  wait(lambda:p.screen()[6][1]=='>')
  draws=value('menu_draws',2);text_before=''.join(p.screen())
  p.raw(b'\x15');wait(lambda:value('selected')==17)
  p.raw(b'\x08');wait(lambda:value('selected')==1)
  p.raw(b'\x0a'*20);wait(lambda:value('selected')==21)
  time.sleep(.1);assert value('menu_draws',2)==draws
  text_after=''.join(p.screen())
  assert sum(a!=b for a,b in zip(text_before,text_after))==2
  shot('music-columns')
  checks.append('Three music columns, four arrow keys; moving cursor alters exactly two text cells, no full redraw')
  p.raw(b'\r');wait(lambda:value('track')==21 and value('menu')==0);assert original==imagebytes()
  p.raw(b' ');wait(lambda:mode(2));p.raw(b'M');wait(lambda:value('menu')==1);p.raw(b'M');wait(lambda:value('menu')==0 and mode(2))
  p.raw(b'\r');wait(lambda:value('index',2)==index+1 and mode(2));assert value('errors',2)==0
  checks.append('Three-column music selection; menu restores mixed; next image retains mixed')
  p.raw(b'M');wait(lambda:value('menu')==1);p.raw(b'\x0b'*21+b'\r');wait(lambda:value('track')==0 and value('menu')==0)
  p.raw(b' ');wait(lambda:mode(1));index=value('index',2);wait(lambda:value('index',2)>index);assert mode(1)
  checks.append('STOP selection; automatic advance remains fullscreen')
  p.raw(b'M');wait(lambda:value('menu')==1);p.raw(b'Q');wait(lambda:any('BITSY  BYE' in r for r in screen40()))
  checks.append('Q quits from music menu to Bitsy Bye')
  (root/'result.json').write_text(json.dumps(dict(hdv_sha256=tested_hash,checks=checks,failures=[]),indent=2)+'\n')
  (root/'failure.txt').unlink(missing_ok=True)
  print('PASS',checks,flush=True)
 except Exception:
  import traceback
  (root/'failure.txt').write_text(traceback.format_exc())
  raise
 finally:
  p.stop();log=pathlib.Path(work)/'pom2.log'
  if log.exists():(root/'pom2.log.gz').write_bytes(gzip.compress(log.read_bytes(),mtime=0))
