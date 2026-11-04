import {decodeToImageData,decodeRawHgr} from './dhgr.js';

export const reviewLabels={todo:'À revoir',accepted:'Validée par vous',rework:'À retoucher',changed:'Modifiée depuis votre avis'};
export const draftKey=(game,asset)=>`atelier:draft:${game}:${asset}`;
export const sameInputs=(a,b)=>a?.source===b?.source&&a?.recipe===b?.recipe;
export function sceneLink(game,page,lang,source){
  return '?'+new URLSearchParams({mode:'jeu',jeu:game.toLowerCase(),page,langue:lang,source});
}
export function filteredAssets(assets,query,filter){
  return assets.filter(a=>a.id.includes(query.toUpperCase())&&(!filter||
    (filter==='saved'?a.corrected:filter==='selected'?a.selected:filter==='todo'?a.review!=='accepted':a.id.startsWith(filter))));
}

export const reviewMethods={
  setupReview(){
    this.el.previous.onclick=()=>this.moveReview(-1);
    this.el.next.onclick=()=>this.moveReview(1);
    this.el['save-review'].onclick=()=>this.saveReview();
    this.el['scene-select'].onchange=this.el['scene-language'].onchange=()=>this.showScene();
    this.el.layout.onchange=()=>{this.el.canvases.dataset.layout=this.el.layout.value;this.showResult();};
    this.el['restore-master'].onclick=()=>this.restoreMaster();
  },
  visibleAssets(){return filteredAssets(this.assets||[],this.el.search.value,this.el.filter.value);},
  moveReview(offset){
    const items=this.visibleAssets(),i=items.findIndex(a=>a.id===this.asset);
    const next=items[i+offset];if(next)this.select(next.id);
  },
  reviewNavigation(){
    const items=this.visibleAssets(),i=items.findIndex(a=>a.id===this.asset);
    this.el.previous.disabled=i<=0;this.el.next.disabled=i<0||i>=items.length-1;
    this.el['review-progress'].textContent=`${this.assets.filter(a=>a.review==='accepted').length} / ${this.assets.length} validées par vous`;
  },
  readDraft(game,asset,fingerprint){
    let draft=this.drafts.get(game+':'+asset);
    if(!draft){try{draft=JSON.parse(localStorage.getItem(draftKey(game,asset)));}catch{}}
    return draft&&sameInputs(draft.fingerprint,fingerprint)?draft:null;
  },
  storeDraft(){
    if(!this.asset||!this.recipe)return;
    const draft={recipe:structuredClone(this.recipe),dirty:this.dirty,fingerprint:this.fingerprint};
    this.drafts??=new Map();this.drafts.set(this.game+':'+this.asset,draft);
    try{if(draft.dirty)localStorage.setItem(draftKey(this.game,this.asset),JSON.stringify(draft));else localStorage.removeItem(draftKey(this.game,this.asset));}
    catch{this.status('Brouillon conservé dans cet onglet ; stockage du navigateur indisponible.',true);}
  },
  async loadReview(version=this.version){
    const game=this.game,asset=this.asset;
    this.review=null;this.el['save-review'].disabled=true;this.el['before-image'].hidden=true;
    this.el['before-empty'].hidden=false;this.el['before-empty'].textContent='Lecture de l’image enregistrée…';
    this.el['previous-master-box'].hidden=true;this.el['scene-select'].replaceChildren();this.el['scene-text'].textContent='';
    for(const id of ['scene-tree','scene-volume']){this.el[id].hidden=true;this.el[id].removeAttribute('href');}
    try{
      const data=await this.api(`/api/review?game=${game}&asset=${asset}`);
      if(game!==this.game||asset!==this.asset||version!==this.selectionVersion)return;
      this.review=data;this.el['review-selected'].checked=!!data.record.selected;
      Object.assign(this.assets.find(a=>a.id===asset),{selected:!!data.record.selected,review:data.state});this.renderAssets();
      this.el['review-notes'].value=data.record.notes||'';
      this.el['review-decision'].value=data.state==='changed'?'todo':data.state;
      this.el['review-state'].textContent=reviewLabels[data.state];this.el['save-review'].disabled=false;
      this.el['scene-select'].replaceChildren(...data.scenes.map(s=>new Option(`§ ${s.page} · ${s.titles.FR||''}`,s.page)));
      this.showScene();this.drawComparison();
      if(data.previous_master){this.el['previous-master-box'].hidden=false;this.el['previous-master'].src=data.previous_master;}
    }catch(e){if(game===this.game&&asset===this.asset)this.status(e.message,true);}
  },
  showScene(){
    const page=Number(this.el['scene-select'].value),lang=this.el['scene-language'].value;
    const scene=this.review?.scenes.find(s=>s.page===page);
    this.el['scene-text'].textContent=scene?.texts[lang]||'Aucune scène associée à cette image.';
    for(const [id,source] of [['scene-tree','arbre'],['scene-volume','volume']]){
      this.el[id].hidden=!scene;
      if(scene)this.el[id].href=sceneLink(this.game,page,lang,source);
    }
    if(scene)this.el['play-mode'].href=sceneLink(this.game,page,lang,'arbre');
  },
  drawComparison(){
    const draw=(canvas,data)=>{
      canvas.hidden=!data;if(!data)return false;
      const bytes=Uint8Array.from(atob(data),c=>c.charCodeAt(0)),ctx=canvas.getContext('2d');
      const pixels=this.mode==='hgr'?decodeRawHgr(bytes,ctx):decodeToImageData(bytes,'chatmauve',ctx);
      if(!pixels){canvas.hidden=true;return false;}canvas.width=pixels.width;canvas.height=pixels.height;ctx.putImageData(pixels,0,0);return true;
    };
    this.el['before-empty'].hidden=draw(this.el['before-image'],this.review?.saved);
    this.el['before-empty'].textContent=this.review?.saved?'Image enregistrée illisible.':'Pas encore d’image enregistrée.';
    const compare=this.el.layout.value==='compare';
    const ready=draw(this.el['after-image'],compare?this.result?.binary:null);
    this.el.result.hidden=compare||!this.result;
    this.el.placeholder.hidden=compare?ready:!!this.result;
    this.el['comparison-note'].hidden=!compare;
    this.el.display.disabled=compare;
  },
  async saveReview(){
    if(!this.review)return;
    const game=this.game,asset=this.asset,state=this.el['review-decision'].value;
    if(state==='accepted'&&(this.dirty||!this.token||this.result?.sha256!==this.fingerprint?.output)){
      this.status('Enregistrez la proposition affichée avant de la valider.',true);return;
    }
    this.el['save-review'].disabled=true;
    try{
      const {record}=await this.api('/api/review',{game,asset,state,notes:this.el['review-notes'].value,
        selected:this.el['review-selected'].checked,fingerprint:this.review.fingerprint,token:this.token});
      if(game!==this.game||asset!==this.asset)return;
      this.review.record=record;this.review.state=record.state;
      Object.assign(this.assets.find(a=>a.id===asset),{selected:record.selected,review:record.state});
      this.renderAssets();this.el['review-state'].textContent=reviewLabels[record.state];this.status('Votre avis est enregistré.');
    }catch(e){if(game===this.game&&asset===this.asset)this.status(e.message,true);}
    finally{if(game===this.game&&asset===this.asset)this.el['save-review'].disabled=false;}
  },
  async restoreMaster(){
    if(!this.review?.previous_master||this.job?.state==='running')return;
    const game=this.game,asset=this.asset;
    this.el['restore-master'].disabled=true;
    try{await this.api('/api/restore-master',{game,asset,fingerprint:this.review.fingerprint,previous_master:this.review.previous_master});
      await this.masterReplaced(game,asset);
      this.status('Master précédent repris. Ajustez puis enregistrez votre proposition.');
    }catch(e){this.status(e.message,true);}finally{this.el['restore-master'].disabled=false;}
  },
};
