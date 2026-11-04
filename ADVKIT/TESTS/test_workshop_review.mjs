import assert from 'node:assert/strict';
import {filteredAssets,sameInputs,sceneLink,reviewMethods,draftKey} from '../workshop_review.js';

const assets=[{id:'N001',selected:true,review:'accepted'},{id:'B002',review:'changed'},{id:'N003',review:'rework'}];
assert.deepEqual(filteredAssets(assets,'','todo').map(a=>a.id),['B002','N003']);
assert.deepEqual(filteredAssets(assets,'n','selected').map(a=>a.id),['N001']);
assert.equal(sameInputs({source:'a',recipe:'b'},{source:'a',recipe:'b'}),true);
assert.equal(sameInputs({source:'a',recipe:'b'},{source:'new',recipe:'b'}),false);
const link=new URL(sceneLink('SPACETRIP',12,'EN','volume'),'http://localhost/');
assert.equal(link.searchParams.get('page'),'12');
assert.equal(link.searchParams.get('source'),'volume');
assert.equal(link.searchParams.get('jeu'),'spacetrip');

// Drafts survive a page reload, but never attach to a different master/recipe.
const storage=new Map();globalThis.localStorage={setItem:(k,v)=>storage.set(k,v),getItem:k=>storage.get(k)||null,removeItem:k=>storage.delete(k)};
const workshop={...reviewMethods,game:'SCOSWAMP',asset:'N001',recipe:{crop:[0,0,140,96]},dirty:true,
  fingerprint:{source:'a',recipe:'b'},drafts:new Map(),status(){}};
workshop.storeDraft();workshop.drafts.clear();
assert.deepEqual(workshop.readDraft('SCOSWAMP','N001',{source:'a',recipe:'b'}).recipe,workshop.recipe);
assert.equal(workshop.readDraft('SCOSWAMP','N001',{source:'new',recipe:'b'}),null);
workshop.dirty=false;workshop.storeDraft();assert.equal(storage.has(draftKey('SCOSWAMP','N001')),false);

// A decision can never validate an unsaved candidate, even with a previous token.
let called=false,message='';
Object.assign(workshop,{review:{},dirty:true,token:'old',result:{sha256:'out'},fingerprint:{output:'out'},
  el:{'review-decision':{value:'accepted'}},api:async()=>{called=true;},status:m=>message=m});
await workshop.saveReview();assert.equal(called,false);assert.match(message,/Enregistrez/);
console.log('PASS review selection, scene links, persistent drafts, master changes and unsaved acceptance guard');
