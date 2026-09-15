/* Human correction workspace. Crops are always 35:24 in source coordinates;
 * the master stays intact. Only native conversion results can be applied. */
const $ = (s, root=document) => root.querySelector(s);
const ratio = 35/24;
export function cropAt(width,height,zoom=1,cx=width/2,cy=height/2) {
  const w=Math.min(width,height*ratio)/zoom, h=w/ratio;
  const x=Math.max(0,Math.min(width-w,cx-w/2));
  const y=Math.max(0,Math.min(height-h,cy-h/2));
  return [Math.round(x),Math.round(y),Math.round(x+w),Math.round(y+h)];
}
const controls = [
  ['brightness','Luminosité',.3,2], ['contrast','Contraste',.4,2.5],
  ['gamma','Gamma',.4,2.5], ['colourNoise','Bruit de couleur',0,1],
  ['diffusion','Diffusion · grain',0,1],
];
export class Workshop {
  constructor(root) {
    this.root=root; this.game='SCOSWAMP'; this.version=0; this.busy=false;
    this.dirty=false; this.zoom=1; this.enabled=false;
    root.innerHTML=`
      <header class="studio-head"><a class="brand" href="?">A<span> / </span>ATELIER</a>
        <select id="project" aria-label="Projet"><option>SCOSWAMP</option><option>SPACETRIP</option></select>
        <nav><button class="active" id="image-mode">Images</button><a id="play-mode" href="?mode=jeu">Tester le jeu ↗</a></nav>
        <span class="head-note">Édition visuelle · Apple II</span></header>
      <div class="studio-body">
        <aside class="library"><div class="library-heading"><h2>Illustrations</h2><span id="count"></span></div>
          <input id="search" type="search" placeholder="Rechercher N012, B120…" aria-label="Rechercher une image">
          <select id="filter" aria-label="Filtrer"><option value="">Toutes les images</option><option value="N">Scènes</option><option value="B">Combats</option><option value="saved">Corrigées</option></select>
          <div id="assets" class="asset-list"></div></aside>
        <main class="image-desk">
          <div class="desk-title"><div><p class="eyebrow">CORRECTION D’IMAGE</p><h1 id="asset-title">Choisir une illustration</h1></div><span class="badge">35:24 · ratio verrouillé</span></div>
          <div class="view-toolbar"><label>Image <select id="asset-select" aria-label="Sélectionner une image"></select></label><label>Affichage <select id="layout"><option value="side">Côte à côte</option><option value="result">Résultat agrandi</option></select></label>
            <label><input id="mask" type="checkbox"> Zone de texte</label><label><input id="onion" type="checkbox"> Calque source</label></div>
          <div class="canvases" id="canvases">
            <section class="source-panel"><div class="panel-caption"><strong>Original & cadrage</strong><span>Glisser pour déplacer</span></div>
              <div class="source-stage"><div class="source-frame" id="source-frame"><img id="source" draggable="false" alt="Master original"><div id="crop" tabindex="0" role="slider" aria-label="Cadrage, flèches pour déplacer"><i></i><i></i><i></i><i></i><button id="crop-handle" aria-label="Redimensionner le cadrage"></button></div></div></div>
              <div class="crop-tools"><button id="crop-toggle">Activer le cadrage</button><label>Zoom <input id="zoom" type="range" min="1" max="8" step=".01" value="1"><output id="zoom-value">1×</output></label></div>
              <p id="crop-info" class="subtle">Original conservé · cadrage non destructif</p>
            </section>
            <section class="result-panel"><div class="panel-caption"><strong>Résultat Apple II</strong><select id="display" aria-label="Rendu"><option value="composite">Composite · POM2</option><option value="chat">Chat Mauve · blocs</option></select></div>
              <div class="result-stage"><div class="result-frame"><img id="result" alt="Aperçu converti" hidden><canvas id="overlay" hidden></canvas><div id="text-mask" hidden>ZONE DE TEXTE · 4 LIGNES</div><p id="placeholder">L’aperçu apparaîtra ici.</p></div></div>
              <p id="result-info" class="subtle">Conversion native HGRImport</p></section>
          </div>
          <div class="desk-bottom"><div><span class="status-dot"></span><span id="status" role="status" aria-live="polite">Chargement du catalogue…</span></div><span id="saved-state">Master intact</span></div>
        </main>
        <aside class="adjustments"><div class="adjust-heading"><h2>Réglages</h2><button id="reset">Réinitialiser</button></div>
          <fieldset id="settings" disabled><legend>Tonalité & couleur</legend>${controls.map(([id,label,min,max])=>`<label class="slider-label" for="${id}">${label}<output id="${id}-value"></output></label><input id="${id}" type="range" min="${min}" max="${max}" step=".01">`).join('')}
            <div class="setting-divider"></div><label class="select-label">Modèle DHGR<select id="model"><option value="0">560 points · anticipation</option><option value="1">140 pixels · Dazzle Draw</option><option value="2">560 monochrome · 1 bit</option><option value="3">560 NTSC · fenêtre 8 points</option></select></label>
            <label class="select-label">Noyau de diffusion<select id="kernel"><option value="0">Floyd–Steinberg</option><option value="1">Jarvis-mod</option></select></label>
            <label class="check"><input id="dither" type="checkbox"> Tramage</label><label class="check"><input id="stretch" type="checkbox"> Étirer pour remplir</label>
            <label class="check disabled" title="Désactivé dans HGRImport : le décodage NTSC se fait de gauche à droite."><input type="checkbox" disabled> Serpentine · non applicable</label>
          </fieldset>
          <div class="apply-actions"><label class="check"><input id="auto" type="checkbox" checked> Aperçu automatique</label><button id="preview">Actualiser l’aperçu</button><button class="primary" id="apply" disabled>Générer & enregistrer le DHGR RLE</button><p>Enregistre le cadrage, les réglages et l’image Apple II. Le master reste intact.</p><button id="build">Construire le disque .HDV</button><a id="download" hidden>Télécharger le disque</a></div>
        </aside>
      </div>`;
    this.el={}; root.querySelectorAll('[id]').forEach(e=>this.el[e.id]=e);
    this.el.project.onchange=()=>this.loadGame();
    this.el.search.oninput=this.el.filter.onchange=()=>this.renderAssets();
    this.el['asset-select'].onchange=()=>this.select(this.el['asset-select'].value);
    this.el.search.onkeydown=e=>{if(e.key==='Enter'){const a=this.assets.find(a=>a.id===this.el.search.value.trim().toUpperCase())||this.assets.find(a=>a.id.includes(this.el.search.value.trim().toUpperCase()));if(a)this.select(a.id);}};
    for(const [id] of controls) this.el[id].oninput=()=>{this.recipe[id]=Number(this.el[id].value);this.labels();this.changed();};
    for(const id of ['model','kernel','dither','stretch']) this.el[id].onchange=()=>{this.recipe[id]=['dither','stretch'].includes(id)?this.el[id].checked:Number(this.el[id].value);this.changed();};
    this.el.reset.onclick=()=>{if(!this.recipe)return;this.recipe=structuredClone(this.defaults);this.sync();this.changed();};
    this.el.preview.onclick=()=>this.preview();
    this.el.apply.onclick=()=>this.apply();
    this.el.build.onclick=()=>this.build();
    this.el.auto.onchange=()=>{if(this.el.auto.checked)this.schedule();};
    this.el.display.onchange=()=>this.showResult();
    this.el.layout.onchange=()=>this.el.canvases.dataset.layout=this.el.layout.value;
    this.el.mask.onchange=()=>this.el['text-mask'].hidden=!this.el.mask.checked;
    this.el.onion.onchange=()=>this.drawOverlay();
    this.el['crop-toggle'].onclick=()=>{this.recipe.crop=this.recipe.crop?null:cropAt(this.w,this.h);this.zoom=1;this.syncCrop();this.changed();};
    this.el.zoom.oninput=()=>{const c=this.recipe.crop||[0,0,this.w,this.h];this.zoom=Number(this.el.zoom.value);this.recipe.crop=cropAt(this.w,this.h,this.zoom,(c[0]+c[2])/2,(c[1]+c[3])/2);this.syncCrop();this.changed();};
    this.el.crop.onpointerdown=e=>this.startDrag(e);
    this.el.crop.onkeydown=e=>{const moves={ArrowLeft:[-1,0],ArrowRight:[1,0],ArrowUp:[0,-1],ArrowDown:[0,1]};if(!moves[e.key])return;e.preventDefault();const c=this.recipe.crop;const [dx,dy]=moves[e.key];const step=e.shiftKey?10:1;this.recipe.crop=cropAt(this.w,this.h,this.zoom,(c[0]+c[2])/2+dx*step,(c[1]+c[3])/2+dy*step);this.syncCrop();this.changed();};
    window.addEventListener('beforeunload',e=>{if(this.dirty||[...(this.drafts?.values()||[])].some(d=>d.dirty)){e.preventDefault();e.returnValue='';}});
    const params=new URLSearchParams(location.search);
    if(params.get('jeu')?.toUpperCase()==='SPACETRIP')this.el.project.value='SPACETRIP';
    this.loadGame();
  }
  status(text,error=false){this.el.status.textContent=text;this.el.status.classList.toggle('error',error);}
  async api(path,body){const r=await fetch(path,body?{method:'POST',headers:{'Content-Type':'application/json','X-Workshop-Token':this.csrf},body:JSON.stringify(body)}:{});let data;try{data=await r.json();}catch{throw Error('Démarrez serve.sh pour activer la conversion et l’enregistrement.');}if(!r.ok)throw Error(data.error||r.statusText);return data;}
  async loadGame(){
    this.keepDraft();this.asset=null;this.recipe=null;this.game=this.el.project.value;this.version++;this.token=null;this.dirty=false;this.el.apply.disabled=true;
    const version=this.version, game=this.game;
    try {const data=await this.api('/api/images?game='+game);if(version!==this.version)return;this.assets=data.assets;this.defaults=data.defaults;this.mode=data.mode;this.csrf=data.csrf;
      this.el.apply.textContent=this.mode==='hgr'?'Générer & enregistrer le HGR':'Générer & enregistrer le DHGR RLE';this.el.model.disabled=this.mode==='hgr';this.el.display.options[1].disabled=this.mode==='hgr';this.el.display.value='composite';
      this.el['play-mode'].href=`?mode=jeu&jeu=${this.game.toLowerCase()}&source=arbre&langue=FR`;
      this.renderAssets();const requested=new URLSearchParams(location.search).get('image');const first=this.assets.find(a=>a.id===requested)||this.assets.find(a=>a.id==='B120')||this.assets[0];
      if(first)await this.select(first.id);else this.status('Aucun master PNG dans ce projet.');
    }catch(e){this.status(e.message,true);}
  }
  keepDraft(){this.drafts??=new Map();if(this.asset&&this.recipe)this.drafts.set(this.game+':'+this.asset,{recipe:structuredClone(this.recipe),dirty:this.dirty});}
  renderAssets(){
    const q=this.el.search.value.toUpperCase(), f=this.el.filter.value;
    const assets=this.assets.filter(a=>a.id.includes(q)&&(!f||(f==='saved'?a.corrected:a.id.startsWith(f))));
    this.el.count.textContent=assets.length;const scroll=this.el.assets.scrollTop;this.el.assets.replaceChildren();
    if(this.el['asset-select'].dataset.game!==this.game){this.el['asset-select'].replaceChildren(...this.assets.map(a=>new Option(a.id,a.id)));this.el['asset-select'].dataset.game=this.game;}
    this.el['asset-select'].value=this.asset||'';
    for(const a of assets){const b=document.createElement('button');b.className='asset'+(this.asset===a.id?' selected':'');b.dataset.asset=a.id;b.innerHTML=`<img loading="lazy" src="${a.source}" alt=""><span><strong>${a.id}</strong><small>${a.id[0]==='B'?'Combat':'Scène'}${a.corrected?' · corrigée':''}</small></span>`;b.onclick=()=>this.select(a.id);this.el.assets.append(b);}
    this.el.assets.scrollTop=scroll;
  }
  async select(id){
    // Keep unsaved edits per image while browsing this session.
    this.keepDraft();this.recipe=null;this.el.settings.disabled=true;this.el.zoom.disabled=true;this.el['crop-toggle'].disabled=true;
    const version=++this.version;this.asset=id;const url=new URL(location.href);url.searchParams.set('image',id);url.searchParams.set('jeu',this.game.toLowerCase());history.replaceState(null,'',url);this.token=null;this.el.apply.disabled=true;this.result=null;this.el.result.hidden=true;this.el.placeholder.hidden=false;
    this.el['asset-title'].textContent=`${id} / ${id[0]==='B'?'Combat':'Scène'}`;this.renderAssets();this.status('Chargement du master…');
    try{const data=await this.api(`/api/recipe?game=${this.game}&asset=${id}`);if(version!==this.version)return;
      const draft=this.drafts.get(this.game+':'+id);this.recipe=draft?.recipe||data.recipe;this.dirty=draft?.dirty||false;this.w=data.width;this.h=data.height;
      this.el.source.src=this.assets.find(a=>a.id===id).source;await this.el.source.decode();if(version!==this.version)return;
      this.el.apply.disabled=false;this.el.settings.disabled=false;this.el.zoom.disabled=false;this.el['crop-toggle'].disabled=false;this.sync();this.el['saved-state'].textContent=this.dirty?'Correction non enregistrée':'Master intact';this.status('Réglages prêts.');this.preview();
    }catch(e){if(version===this.version)this.status(e.message,true);}
  }
  labels(){for(const [id] of controls)this.el[id+'-value'].textContent=Number(this.recipe[id]).toFixed(2);}
  sync(){for(const [id] of controls)this.el[id].value=this.recipe[id];for(const id of ['model','kernel'])this.el[id].value=this.recipe[id];for(const id of ['dither','stretch'])this.el[id].checked=this.recipe[id];const c=this.recipe.crop;this.zoom=c?Math.min(this.w,this.h*ratio)/(c[2]-c[0]):1;this.labels();this.syncCrop();}
  syncCrop(){const c=this.recipe.crop;this.el.crop.hidden=!c;this.el.zoom.value=this.zoom;this.el['zoom-value'].value=this.zoom.toFixed(2)+'×';this.el['crop-toggle'].textContent=c?'Retirer le cadrage':'Activer le cadrage';
    if(c){Object.assign(this.el.crop.style,{left:100*c[0]/this.w+'%',top:100*c[1]/this.h+'%',width:100*(c[2]-c[0])/this.w+'%',height:100*(c[3]-c[1])/this.h+'%'});this.el.crop.setAttribute('aria-valuetext',c.join(', '));}
    this.el['crop-info'].textContent=c?`${c[2]-c[0]} × ${c[3]-c[1]} px · origine ${c[0]}, ${c[1]} · ratio 35:24`:`${this.w} × ${this.h} px · image entière`;this.drawOverlay();
  }
  startDrag(e){if(!this.recipe.crop)return;e.preventDefault();const start=this.recipe.crop.slice(), rect=this.el.source.getBoundingClientRect(),x=e.clientX,y=e.clientY,resize=e.target===this.el['crop-handle'];this.el.crop.setPointerCapture(e.pointerId);
    const move=ev=>{const dx=(ev.clientX-x)*this.w/rect.width,dy=(ev.clientY-y)*this.h/rect.height;
      if(resize){const maxW=Math.min(this.w-start[0],(this.h-start[1])*ratio);const w=Math.max(Math.min(this.w,this.h*ratio)/8,Math.min(maxW,start[2]-start[0]+Math.max(dx,dy*ratio)));this.zoom=Math.min(this.w,this.h*ratio)/w;this.recipe.crop=cropAt(this.w,this.h,this.zoom,start[0]+w/2,start[1]+w/ratio/2);}
      else this.recipe.crop=cropAt(this.w,this.h,this.zoom,(start[0]+start[2])/2+dx,(start[1]+start[3])/2+dy);
      this.syncCrop();this.changed(false);};
    const end=()=>{this.el.crop.removeEventListener('pointermove',move);this.el.crop.removeEventListener('pointerup',end);this.el.crop.removeEventListener('pointercancel',end);this.schedule();};
    this.el.crop.addEventListener('pointermove',move);this.el.crop.addEventListener('pointerup',end);this.el.crop.addEventListener('pointercancel',end);
  }
  changed(schedule=true){this.version++;this.token=null;this.dirty=true;this.el.apply.disabled=false;this.el['saved-state'].textContent='Correction non enregistrée';this.status('Réglages modifiés · aperçu à actualiser');this.drawOverlay();if(schedule)this.schedule();}
  schedule(){clearTimeout(this.timer);if(this.el.auto.checked)this.timer=setTimeout(()=>this.preview(),120);}
  async preview(){
    clearTimeout(this.timer);if(!this.recipe)return;if(this.busy){this.pending=true;return;}this.busy=true;this.pending=false;
    const version=this.version;this.status('Conversion native en cours…');this.el.preview.disabled=true;
    try{const data=await this.api('/api/convert',{game:this.game,asset:this.asset,recipe:structuredClone(this.recipe)});if(version!==this.version)return;this.result=data;this.token=data.token;this.el.apply.disabled=false;this.showResult();if(!this.saving)this.status('Aperçu prêt · vous pouvez enregistrer cette correction.');this.el['result-info'].textContent=`${data.bytes.toLocaleString('fr')} octets · ${this.mode.toUpperCase()} · aperçu issu des octets convertis`;
    }catch(e){if(version===this.version)this.status(e.message,true);}finally{this.busy=false;this.el.preview.disabled=false;if(this.pending){this.pending=false;this.preview();}}
  }
  showResult(){if(!this.result)return;this.el.result.src=this.result[this.el.display.value];this.el.result.hidden=false;this.el.placeholder.hidden=true;}
  drawOverlay(){const canvas=this.el.overlay;canvas.hidden=!this.el.onion.checked;if(!this.recipe||!this.el.source.complete)return;canvas.width=560;canvas.height=384;const ctx=canvas.getContext('2d');const c=this.recipe.crop||[0,0,this.w,this.h],w=c[2]-c[0],h=c[3]-c[1];let dw=560,dh=384;if(!this.recipe.stretch){const scale=Math.min(dw/w,dh/h);dw=w*scale;dh=h*scale;}ctx.drawImage(this.el.source,...[c[0],c[1],w,h],(560-dw)/2,(384-dh)/2,dw,dh);}
  async apply(){
    if(!this.recipe || this.saving)return;
    this.saving=true;this.el.apply.disabled=true;clearTimeout(this.timer);
    const version=this.version, game=this.game, asset=this.asset;
    this.status('Génération finale et enregistrement…');
    try {
      let token=this.token;
      if(!token){const result=await this.api('/api/convert',{game,asset,recipe:structuredClone(this.recipe)});
        if(version!==this.version)throw Error('Réglages modifiés pendant la génération : cliquez à nouveau sur Enregistrer.');
        this.result=result;this.token=token=result.token;this.showResult();}
      const data=await this.api('/api/apply',{token});
      if(version!==this.version)return;
      this.dirty=false;this.keepDraft();this.assets.find(a=>a.id===asset).corrected=true;this.renderAssets();
      this.el['saved-state'].textContent='DHGR RLE enregistré';
      this.status(`${data.saved} enregistré · reconstruisez le disque pour POM2.`);
    }catch(e){this.status(e.message,true);}finally{this.saving=false;this.el.apply.disabled=!this.recipe;}
  }
  async build(){this.el.build.disabled=true;this.status('Construction du disque…');try{const data=await this.api('/api/build',{game:this.game});this.el.download.href=data.volume;this.el.download.hidden=false;this.el.download.download='';this.status('Disque construit avec les corrections enregistrées.');}catch(e){this.status(e.message,true);}finally{this.el.build.disabled=false;}}
}
