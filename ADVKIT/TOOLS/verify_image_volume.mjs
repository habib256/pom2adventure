/* Verify the exact saved image bytes after packaging, using the player's reader. */
import {readFile,readdir} from 'node:fs/promises';
import {resolve,relative,join} from 'node:path';
import {createHash} from 'node:crypto';
import {pathToFileURL} from 'node:url';
import {VolumeProDOS,cheminVolume} from '../prodos.js';

const sha = bytes => createHash('sha256').update(bytes).digest('hex');
export async function verifyImages(root,game,expected=null) {
  if(!['SCOSWAMP','SPACETRIP'].includes(game))throw Error('Projet inconnu');
  root=resolve(root);
  const volume=join(root,'dist',game==='SCOSWAMP'?'SCOSWAMP.HDV':'SPACETRIP.hdv');
  const disk=new VolumeProDOS(new Uint8Array(await readFile(volume)));
  if(expected===null){
    expected={};
    async function walk(dir){
      for(const entry of await readdir(dir,{withFileTypes:true})){
        const p=join(dir,entry.name);
        if(entry.isDirectory())await walk(p);
        else if(entry.name.endsWith('.BIN'))expected[relative(root,p).split('\\').join('/')]=sha(await readFile(p));
      }
    }
    await walk(join(root,game,game==='SCOSWAMP'?'DHGR':'IMG'));
  }
  const entries=Object.entries(expected);
  if(!entries.length)throw Error('Aucune image à vérifier');
  const mismatches=[];
  for(const [path,hash] of entries){
    if(!path.startsWith(game+'/')||path.split('/').includes('..'))throw Error('Chemin image invalide');
    const saved=await readFile(join(root,path));
    const packed=disk.lire(cheminVolume(path,game+'/'));
    if(sha(saved)!==hash||!packed||sha(packed)!==hash)mismatches.push(path);
  }
  return {ok:!mismatches.length,checked:entries.length,mismatches};
}
if(process.argv[1]&&import.meta.url===pathToFileURL(resolve(process.argv[1])).href){
  try{
    let input='';for await(const chunk of process.stdin)input+=chunk;
    console.log(JSON.stringify(await verifyImages(process.argv[2],process.argv[3],input?JSON.parse(input):null)));
  }catch(e){console.error(e.message);process.exitCode=1;}
}
