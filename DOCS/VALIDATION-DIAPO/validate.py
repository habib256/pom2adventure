import sys,tempfile,pathlib,shutil,time,json,re,hashlib,gzip
sys.path.insert(0,'SCOSWAMP.MORE/TOOLS')
import playtest as pt
root=pathlib.Path(sys.argv[1]);root.mkdir(exist_ok=False)
labels={n:int(a,16) for a,n in re.findall(r'al ([0-9A-F]+) .(\w+)',pathlib.Path('SCOSWAMP/SRC/diapo.lbl').read_text())}
paths=pathlib.Path('SCOSWAMP/DIAPO.LIST.TXT').read_text().splitlines()
def decode(path):
 b=path.read_bytes();assert b[:8]==b'DHRR\x01\x00\x00\x40';o=bytearray();i=8
 while len(o)<16384:
  t=b[i];i+=1
  if t&128:o.extend([b[i]]*((t&127)+3));i+=1
  else:o.extend(b[i:i+t+1]);i+=t+1
 assert len(o)==16384 and i==len(b)
 return bytes(o)
with tempfile.TemporaryDirectory(prefix='diapo-validate-') as work:
 disk=pathlib.Path(work)/'TEST.hdv';shutil.copyfile(pt.HDV_SRC,disk);tested_hash=hashlib.sha256(disk.read_bytes()).hexdigest();p=pt.Pom2(str(disk),port=6526)
 def value(name,n=2):return int.from_bytes(p.peek(labels['_diapo_'+name],n),'little')
 def wait(test):
  deadline=time.time()+10
  while time.time()<deadline:
   if test():return
   time.sleep(.01)
  raise AssertionError('Timed out')
 def screen40():
  m=p.peek(0x400,1024)
  return [''.join(p._cell(m[0x80*(r%8)+0x28*(r//8)+c]) for c in range(40)) for r in range(24)]
 try:
  p.start();g=pt.Game(p,pt.Symbols(pt.SRCDIR));g.boot('F');g.press('Q');g.press('O')
  rows=screen40();assert any('BITSY  BYE' in r for r in rows)
  row=next(i for i,r in enumerate(rows) if r.startswith('- DIAPO '));p.raw(b'\x0a'*(row-2)+b'\r')
  wait(lambda:any('RETURN start slideshow' in r for r in p.screen()))
  title_rows=p.screen();assert any('453 scene and combat images' in r for r in title_rows)
  (root/'title.txt').write_text('\n'.join(title_rows)+'\n')
  import urllib.request
  (root/'title.ppm').write_bytes(urllib.request.urlopen(p.base+'/screen.ppm').read())
  p.rq('/speed',{'preset':'1x'})
  p.raw(b'\r ')
  wait(lambda: value('paused',1)==1 and 1<=value('index')<=len(paths))
  import urllib.request
  wait(lambda: 'Paused' in p.screen()[22])
  assert value('info_frames',1)>0
  started=time.monotonic()
  rows=p.screen();assert 'SCORPION SWAMP' in rows[20] and 'SPACE pause/resume' in rows[23]
  (root/'mixed.txt').write_text('\n'.join(rows)+'\n')
  (root/'mixed.ppm').write_bytes(urllib.request.urlopen(p.base+'/screen.ppm').read())
  wait(lambda:value('info_frames',1)==0)
  info_seconds=time.monotonic()-started
  assert 0.65<info_seconds<1.4,info_seconds
  (root/'full.ppm').write_bytes(urllib.request.urlopen(p.base+'/screen.ppm').read())
  start=value('index');time.sleep(.2);assert value('index')==start
  p.rq('/speed',{'cycles_per_frame':200000})
  p.raw(b' ');wait(lambda:value('index')!=start);p.raw(b' ');wait(lambda:value('paused',1)==1)
  print('PASS English title, one-second mixed intro, full DHGR, pause and auto resume',info_seconds,flush=True)
  verified=[]
  for count in range(len(paths)):
   index=value('index');assert 1<=index<=len(paths)
   expected=decode(pathlib.Path('SCOSWAMP')/(paths[index-1]+'.BIN'))
   actual=p.peek(0x2000,8192,'aux')+p.peek(0x2000,8192)
   assert actual==expected,(index,paths[index-1],value('errors'))
   assert value('errors')==0
   verified.append(dict(index=index,path=paths[index-1],sha256=hashlib.sha256(actual).hexdigest()))
   p.raw(b'\r');next_index=index%len(paths)+1;wait(lambda:value('index')==next_index)
   if (count+1)%50==0:print('PASS images',count+1,flush=True)
  assert len({r['index'] for r in verified})==len(paths)
  assert value('loops')>=1
  p.raw(b'\x1b');wait(lambda:any('BITSY  BYE' in r for r in screen40()))
  result=dict(info_seconds_observed=info_seconds,images=len(verified),failures=[],headless=pt.POM2,hdv_sha256=tested_hash,checks=['80-column English title', 'one-second mixed introduction then full DHGR', 'Bitsy Bye keyboard launch','pause stable','automatic resume','all image bytes AUX+MAIN','manual advance','wrap to first image','ESC returns to Bitsy Bye'],verified=verified)
  (root/'result.json').write_text(json.dumps(result,indent=2)+'\n')
  print('PASS',len(verified),'images, wrap, return to Bitsy Bye',flush=True)
 finally:
  p.stop();(root/'pom2.log.gz').write_bytes(gzip.compress((pathlib.Path(work)/'pom2.log').read_bytes(),mtime=0))
