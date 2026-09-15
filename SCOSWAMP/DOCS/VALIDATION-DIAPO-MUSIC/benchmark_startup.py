import sys,time,tempfile,pathlib,shutil,json
sys.path.insert(0,'SCOSWAMP.MORE/TOOLS');import playtest as pt
with tempfile.TemporaryDirectory(prefix='diapo-startup-') as work:
 disk=pathlib.Path(work)/'TEST.hdv';shutil.copyfile(sys.argv[1],disk);p=pt.Pom2(str(disk),port=6527)
 def rows40():
  m=p.peek(0x400,1024)
  return [''.join(p._cell(m[0x80*(r%8)+0x28*(r//8)+c])for c in range(40))for r in range(24)]
 try:
  p.start();g=pt.Game(p,pt.Symbols(pt.SRCDIR));g.boot('F');g.press('Q');g.press('O')
  row=next(i for i,r in enumerate(rows40())if '/DIAPO' in r);p.raw(b'\x0a'*(row-2)+b'\r');time.sleep(.5)
  row=next(i for i,r in enumerate(rows40())if r.startswith(('- DIAPO.SYSTEM ', '- DIAPO ')));p.raw(b'\x0a'*(row-2));time.sleep(.2)
  p.rq('/speed',{'preset':'1x'});start=time.monotonic();p.raw(b'\r');please=None
  while time.monotonic()-start<180:
   rows=p.screen()
   if please is None and any('PLEASE WAIT' in r for r in rows):please=time.monotonic()-start
   if any('RETURN start slideshow' in r for r in rows):break
   time.sleep(.1)
  else:raise Exception('startup >180 seconds')
  result={'disk':sys.argv[1],'speed':'1x','please_wait_seconds':please,'title_seconds':time.monotonic()-start}
  pathlib.Path(sys.argv[2]).write_text(json.dumps(result,indent=2)+'\n');print(result,flush=True)
 finally:p.stop()
