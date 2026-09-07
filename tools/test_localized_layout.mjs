// Exercise the same HTTP data layer used by the editor, without fallback paths.
import assert from 'node:assert/strict';
import {writeFile} from 'node:fs/promises';
globalThis.RACINE_DONNEES='http://127.0.0.1:8765/';
const D=await import('../SCOSWAMP.MORE/TOOLS/interpreter/data.js');
const proj=await D.loadProject('http://127.0.0.1:8765/SCOSWAMP.MORE/TOOLS/interpreter/project.scoswamp.json');
const volume=await D.ouvrirVolume(proj);
const files=volume.liste();
for(const name of ['HELPFR','HELPEN','MSGFR','MSGEN','OBJFR','OBJEN','OBJECTS.JSON','RULES.JSON','DIAPO','DIAPO.CODE','DIAPO.LIST'])assert.ok(!files.includes(name),name+' must leave root');
for(let i=0;i<10;i++){assert.ok(volume.lire('SAVE/SAVE'+i));assert.ok(!volume.lire('SAVE/PARTIE'+i));}
assert.equal(files.filter(f=>f.startsWith('MUSIC/')).length,45);
assert.ok(!files.some(f=>f.startsWith('TOOLS/')||f.startsWith('DIAPO/MUSIC/')));
assert.equal(files.filter(f=>f.startsWith('DHGR/')).length,453);
assert.ok(!files.some(f=>f.startsWith('IMG/')));
for(const name of ['N000/N000.RLE.BIN','N000/B012.RLE.BIN']){
 const path='SCOSWAMP/DHGR/'+name;
 assert.ok((await D.getBytes(path)).length>8);
 assert.equal(await D.comparerAuDepot(path),'identique');
}
const checked=[];
for(const lang of ['FR','EN'])for(const kind of ['aide','messages','objets']){
 const path=D.fill(proj,proj.assets[kind],{lang});
 assert.ok(!path.includes('{LANG}'));
 assert.ok((await D.getText(path)).length>0);
 assert.equal(await D.comparerAuDepot(path),'identique');
 checked.push(path);
}
for(const name of ['OBJECTS.JSON','RULES.JSON'])assert.ok(volume.lire('JSON/'+name));
for(const name of ['DIAPO.SYSTEM','DIAPO.CODE','DIAPO.LIST','DIAPO.DATA','DIAPO.IMAGES','MUSIC.LIST'])assert.ok(volume.lire('DIAPO/'+name));
assert.equal(D.etatSource().horsVolume.length,0);
const tree=files.filter(f=>!f.includes('/'));
const result={checks:checked,root:tree,files:files.length,failures:[]};
await writeFile(new URL('../DOCS/VALIDATION-DIAPO-MUSIC/layout.json',import.meta.url),JSON.stringify(result,null,2)+'\n');
console.log('PASS HTTP editor assets in FR/EN, repeated language template, exact disk/source match, DIAPO, DHGR and JSON, clean root',tree);
