/* Human correction workspace. Crops are always 35:24 in source coordinates;
 * the master stays intact. Only native conversion results can be applied. */
import {reviewMethods,reviewLabels,draftKey} from './workshop_review.js';
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
          <select id="filter" aria-label="Filtrer"><option value="">Toutes les images</option><option value="selected">Ma sélection</option><option value="todo">À revoir ou retoucher</option><option value="N">Scènes</option><option value="B">Combats</option><option value="saved">Corrigées</option></select>
          <div id="assets" class="asset-list"></div></aside>
        <main class="image-desk">
          <div class="desk-title"><div><p class="eyebrow">CORRECTION D’IMAGE</p><h1 id="asset-title">Choisir une illustration</h1></div><span class="badge">35:24 · ratio verrouillé</span></div>
          <div class="review-navigation"><button id="previous">← Précédente</button><span id="review-progress"></span><button id="next">Suivante →</button></div>
          <details class="scene-context"><summary>Scènes et texte associés</summary><div class="scene-links"><select id="scene-select" aria-label="Scène associée"></select><select id="scene-language" aria-label="Langue du contexte"><option>FR</option><option>EN</option></select><a id="scene-tree" target="_blank" rel="noopener">Voir en jeu ↗</a><a id="scene-volume" target="_blank" rel="noopener">Voir depuis le disque ↗</a></div><pre id="scene-text"></pre></details>
          <div class="view-toolbar"><label>Image <select id="asset-select" aria-label="Sélectionner une image"></select></label><label>Affichage <select id="layout"><option value="side">Master & proposition</option><option value="compare">Avant / après</option><option value="result">Résultat agrandi</option></select></label>
            <label><input id="mask" type="checkbox"> Zone de texte</label><label><input id="onion" type="checkbox"> Calque source</label></div>
          <div class="canvases" id="canvases">
            <section class="before-panel"><div class="panel-caption"><strong>Avant · image enregistrée</strong></div><div class="result-stage"><div class="result-frame"><canvas id="before-image" hidden></canvas><p id="before-empty">Lecture de l’image enregistrée…</p></div></div></section>
            <section class="source-panel"><div class="panel-caption"><strong>Original & cadrage</strong><span>Glisser pour déplacer</span></div>
              <div class="source-stage"><div class="source-frame" id="source-frame"><img id="source" draggable="false" alt="Master original"><div id="crop" tabindex="0" role="slider" aria-label="Cadrage, flèches pour déplacer"><i></i><i></i><i></i><i></i><button id="crop-handle" aria-label="Redimensionner le cadrage"></button></div></div></div>
              <div class="crop-tools"><button id="crop-toggle">Activer le cadrage</button><label>Zoom <input id="zoom" type="range" min="1" max="8" step=".01" value="1"><output id="zoom-value">1×</output></label></div>
              <p id="crop-info" class="subtle">Original conservé · cadrage non destructif</p>
              <div class="regen-tools"><button id="regen" title="Demande à codex un nouveau master avec le prompt du manifeste pour cette image. L’ancien est gardé dans GENERATED/.rejets/.">Régénérer le master avec codex</button>
                <details id="previous-master-box" hidden><summary>Master avant la dernière régénération</summary><img id="previous-master" alt="Master précédent"><button id="restore-master">Reprendre ce master</button></details>
                <details id="prompt-box"><summary>Prompt de cette image</summary><pre id="prompt-text">…</pre></details></div>
            </section>
            <section class="result-panel"><div class="panel-caption"><strong>Proposition Apple II</strong><select id="display" aria-label="Rendu"><option value="composite">Composite · POM2</option><option value="chat">Chat Mauve · blocs</option></select></div>
              <div class="result-stage"><div class="result-frame"><img id="result" alt="Aperçu converti" hidden><canvas id="after-image" hidden></canvas><canvas id="overlay" hidden></canvas><div id="text-mask" hidden>ZONE DE TEXTE · 4 LIGNES</div><p id="placeholder">L’aperçu apparaîtra ici.</p></div></div>
              <p id="result-info" class="subtle">Conversion native HGRImport</p></section>
          </div>
          <p id="comparison-note" class="subtle" hidden>Avant : fichier enregistré · Après : proposition. Même rendu en blocs pour comparer les changements ; l’aperçu composite reste disponible dans « Master & proposition ».</p>
          <details class="review-card"><summary>Mon avis · <span id="review-state">À revoir</span></summary><label class="check"><input id="review-selected" type="checkbox"> Ajouter à ma sélection</label><label>Décision <select id="review-decision"><option value="todo">À revoir</option><option value="rework">À retoucher</option><option value="accepted">Valider l’image enregistrée</option></select></label><label for="review-notes">Mes notes</label><textarea id="review-notes" rows="2" maxlength="2000" placeholder="Cadrage à reprendre, variante préférée…"></textarea><button id="save-review" disabled>Enregistrer mon avis</button></details>
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
    this.el.regen.onclick=()=>this.regenerate();
    this.el['prompt-box'].ontoggle=()=>{if(this.el['prompt-box'].open)this.loadPrompt();};
    this.el.auto.onchange=()=>{if(this.el.auto.checked)this.schedule();};
    this.el.display.onchange=()=>this.showResult();
    this.el.layout.onchange=()=>this.el.canvases.dataset.layout=this.el.layout.value;
    this.setupReview();
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
    if(this.saving){this.el.project.value=this.game;return;}
    this.el.download.hidden=true;this.keepDraft();this.asset=null;this.recipe=null;this.game=this.el.project.value;this.version++;this.token=null;this.dirty=false;this.el.apply.disabled=true;
    const version=this.version, game=this.game;
    try {const data=await this.api('/api/images?game='+game);if(version!==this.version)return;this.assets=data.assets;this.defaults=data.defaults;this.mode=data.mode;this.csrf=data.csrf;this.regenerable=data.regenerable;this.job=data.job;
      this.el.apply.textContent=this.mode==='hgr'?'Générer & enregistrer le HGR':'Générer & enregistrer le DHGR RLE';this.el.model.disabled=this.mode==='hgr';this.el.display.options[1].disabled=this.mode==='hgr';this.el.display.value='composite';
      this.el['play-mode'].href=`?mode=jeu&jeu=${this.game.toLowerCase()}&source=arbre&langue=FR`;
      this.renderAssets();const requested=new URLSearchParams(location.search).get('image');const first=this.assets.find(a=>a.id===requested)||this.assets.find(a=>a.id==='B120')||this.assets[0];
      if(first)await this.select(first.id);else this.status('Aucun master PNG dans ce projet.');
      if(this.job?.state==='running')this.watchJob();
    }catch(e){this.status(e.message,true);}
  }
  keepDraft(){this.drafts??=new Map();this.storeDraft();}
  renderAssets(){
    const assets=this.visibleAssets();
    this.el.count.textContent=assets.length;const scroll=this.el.assets.scrollTop;this.el.assets.replaceChildren();
    if(this.el['asset-select'].dataset.game!==this.game){this.el['asset-select'].replaceChildren(...this.assets.map(a=>new Option(a.id,a.id)));this.el['asset-select'].dataset.game=this.game;}
    this.el['asset-select'].value=this.asset||'';
    for(const a of assets){const b=document.createElement('button');b.className='asset'+(this.asset===a.id?' selected':'');b.dataset.asset=a.id;b.innerHTML=`${a.source?`<img loading="lazy" src="${a.source}" alt="">`:''}<span><strong>${a.id}${a.selected?' ★':''}</strong><small>${a.source?(reviewLabels[a.review]||'À revoir'):'Master absent'}</small></span>`;b.onclick=()=>this.select(a.id);this.el.assets.append(b);}
    this.el.assets.scrollTop=scroll;
    this.reviewNavigation();
  }
  async select(id){
    if(this.saving)return;
    // Keep unsaved edits per image across navigation and reloads.
    this.keepDraft();this.recipe=null;this.el.settings.disabled=true;this.el.zoom.disabled=true;this.el['crop-toggle'].disabled=true;
    const version=++this.version;this.selectionVersion=version;this.asset=id;const url=new URL(location.href);url.searchParams.set('image',id);url.searchParams.set('jeu',this.game.toLowerCase());history.replaceState(null,'',url);this.token=null;this.el.apply.disabled=true;this.result=null;this.el.result.hidden=true;this.el.placeholder.hidden=false;
    this.loadReview(version);
    this.el['asset-title'].textContent=`${id} / ${id[0]==='B'?'Combat':'Scène'}`;this.el['prompt-box'].open=false;this.el['prompt-text'].textContent='…';this.regenControls();this.renderAssets();this.status('Chargement du master…');
    try{const data=await this.api(`/api/recipe?game=${this.game}&asset=${id}`);if(version!==this.version)return;
      if(data.missing_master){this.fingerprint=data.fingerprint;this.el.source.removeAttribute('src');this.el.crop.hidden=true;this.el.layout.value='compare';this.el.canvases.dataset.layout='compare';this.drawComparison();this.status(data.warning,true);return;}
      this.fingerprint=data.fingerprint;const draft=this.readDraft(this.game,id,data.fingerprint);this.recipe=draft?.recipe||data.recipe;this.recipeWarning=data.warning;this.dirty=draft?.dirty||data.pending_master||false;this.w=data.width;this.h=data.height;
      this.el.source.src=this.assets.find(a=>a.id===id).source;await this.el.source.decode();if(version!==this.version)return;
      this.el.apply.disabled=false;this.el.settings.disabled=false;this.el.zoom.disabled=false;this.el['crop-toggle'].disabled=false;this.sync();this.el['saved-state'].textContent=this.dirty?'Correction non enregistrée':'Master intact';this.status(this.recipeWarning||'Réglages prêts.',!!this.recipeWarning);this.preview();
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
  changed(schedule=true){this.notice=null;this.version++;this.token=null;this.dirty=true;this.keepDraft();this.el.apply.disabled=false;this.el['saved-state'].textContent='Correction non enregistrée';this.status('Réglages modifiés · aperçu à actualiser');this.drawOverlay();if(schedule)this.schedule();}
  schedule(){clearTimeout(this.timer);if(this.el.auto.checked)this.timer=setTimeout(()=>this.preview(),120);}
  async preview(){
    clearTimeout(this.timer);if(!this.recipe)return;if(this.busy){this.pending=true;return;}this.busy=true;this.pending=false;
    const version=this.version;this.status('Conversion native en cours…');this.el.preview.disabled=true;
    try{const data=await this.api('/api/convert',{game:this.game,asset:this.asset,recipe:structuredClone(this.recipe)});if(version!==this.version)return;this.result=data;this.token=data.token;this.el.apply.disabled=false;this.showResult();if(!this.saving)this.status(this.notice?.asset===this.asset?this.notice.text:'Aperçu prêt · vous pouvez enregistrer cette correction.',this.notice?.asset===this.asset&&this.notice.error);this.el['result-info'].textContent=`${data.bytes.toLocaleString('fr')} octets · ${this.mode.toUpperCase()} · aperçu issu des octets convertis`;
    }catch(e){if(version===this.version)this.status(e.message,true);}finally{this.busy=false;this.el.preview.disabled=false;if(this.pending){this.pending=false;this.preview();}}
  }
  showResult(){if(this.result){this.el.result.src=this.result[this.el.display.value];this.el.result.hidden=false;this.el.placeholder.hidden=true;}this.drawComparison();}
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
      this.el.download.hidden=true;this.fingerprint=data.fingerprint;this.dirty=false;this.keepDraft();this.assets.find(a=>a.id===asset).corrected=true;this.renderAssets();
      await this.loadReview(this.selectionVersion);
      this.status(`${data.saved} enregistré · reconstruisez le disque pour POM2.`);
      this.el['saved-state'].textContent=this.mode==='hgr'?'HGR enregistré':'DHGR RLE enregistré';
    }catch(e){this.status(e.message,true);}finally{this.saving=false;this.el.apply.disabled=!this.recipe;}
  }
  regenControls(){
    const running=this.job?.state==='running';clearTimeout(this.armed);this.armedFor=null;
    this.el.regen.hidden=!this.regenerable;this.el['prompt-box'].hidden=!this.regenerable;this.el.regen.disabled=running||!this.asset;
    this.el.regen.textContent=running?`Régénération de ${this.job.asset} en cours…`:'Régénérer le master avec codex';
  }
  async loadPrompt(){
    const asset=this.asset;this.el['prompt-text'].textContent='Lecture du manifeste…';
    try{const data=await this.api(`/api/prompt?game=${this.game}&asset=${asset}`);if(asset!==this.asset)return;
      this.el['prompt-text'].textContent=data.prompt+(data.refs.length?`\n\nPlanches de référence :\n${data.refs.join('\n')}`:'');
    }catch(e){if(asset===this.asset)this.el['prompt-text'].textContent=e.message;}
  }
  // Deux clics plutôt qu'une boîte modale : une génération dure plusieurs minutes.
  async regenerate(){
    if(!this.asset||this.job?.state==='running')return;
    if(this.armedFor!==this.asset){this.armedFor=this.asset;this.el.regen.textContent=`Confirmer : nouveau master pour ${this.asset}`;
      clearTimeout(this.armed);this.armed=setTimeout(()=>this.regenControls(),5000);return;}
    clearTimeout(this.armed);this.armedFor=null;this.el.regen.disabled=true;
    try{const data=await this.api('/api/regenerate',{game:this.game,asset:this.asset});this.job=data.job;this.regenControls();this.watchJob();}
    catch(e){this.status(e.message,true);this.regenControls();}
  }
  async watchJob(){
    clearTimeout(this.jobTimer);const job=this.job;if(!job)return;
    const tick=async()=>{
      try{this.job=(await this.api('/api/regenerate')).job;}catch(e){this.status(e.message,true);this.jobTimer=setTimeout(tick,5000);return;}
      const j=this.job;this.regenControls();
      // Serveur relance pendant la generation : la tache et son fil sont perdus.
      if(!j||j.asset!==job.asset||j.started!==job.started){this.status(`${job.asset} : suivi perdu, le serveur de l’atelier a redémarré. Vérifiez GENERATED/${job.asset}.png.`,true);return;}
      if(j.state==='running'){const s=Math.round(Date.now()/1000-j.started);this.status(`codex dessine ${j.asset} · ${Math.floor(s/60)} min ${String(s%60).padStart(2,'0')} s (souvent 2 à 6 min)`);this.jobTimer=setTimeout(tick,3000);return;}
      if(j.state==='failed'){this.status(`${j.asset} : ${j.error}`,true);return;}
      // Le message survit a l'apercu qui suit, jusqu'au prochain reglage.
      this.notice={asset:j.asset,error:!!j.warning,text:j.warning?`${j.asset} : nouveau master hors seuils de qualité, gardé quand même · ${j.warning}`:`${j.asset} : nouveau master · ajustez puis enregistrez le DHGR.`};
      this.status(this.notice.text,this.notice.error);
      await this.masterReplaced(j.game,j.asset);
    };
    tick();
  }
  // Le master a change sous la meme URL : on casse le cache, et l'ancienne
  // recette (cadrage, tonalite) visait une autre composition. Le DHGR du disque
  // reste l'ancien tant que la correction n'est pas enregistree.
  // Le brouillon est remis a zero meme si l'on regarde un autre projet : il
  // garderait sinon un cadrage pris sur l'ancien master.
  async masterReplaced(game,id){
    this.drafts??=new Map();this.drafts.delete(game+':'+id);try{localStorage.removeItem(draftKey(game,id));}catch{}
    if(game!==this.game)return;
    const a=this.assets.find(a=>a.id===id);if(!a)return;a.source=`/${this.game}.MORE/GENERATED/${id}.png?v=${Date.now()}`;a.corrected=false;
    if(this.asset===id){this.asset=null;await this.select(id);}else this.renderAssets();
    if(this.asset===id)this.el['saved-state'].textContent='Nouveau master · proposition à enregistrer';
  }
  async build(){const game=this.game;this.el.build.disabled=true;this.el.download.hidden=true;this.status('Construction du disque…');try{const data=await this.api('/api/build',{game});if(game!==this.game)return;this.el.download.href=data.volume;this.el.download.hidden=false;this.el.download.download='';const drafts=this.dirty||[...(this.drafts?.entries()||[])].some(([key,d])=>key.startsWith(game+':')&&d.dirty);this.status(`Disque vérifié : ${data.verification.checked} images identiques aux fichiers enregistrés.${drafts?' Vos brouillons ne sont pas inclus.':''}`);}catch(e){this.status(e.message,true);}finally{this.el.build.disabled=false;}}
}
Object.assign(Workshop.prototype,reviewMethods);
