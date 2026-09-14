# Automatiser SCOSWAMP sous POM2 — porte d'entrée cachée et banc de test

Document de conception. Aucun fichier suivi n'a été modifié pour l'écrire.
Deux dépôts : `/Users/gistair/src/pom2adventure` (le jeu) et
`/Users/gistair/src/pom2` (l'émulateur). Toutes les adresses et tous les
offsets ci-dessous sont **mesurés** sur l'arbre de travail au 2026-09-03
(`SCOSWAMP/SRC/build.map`, `SCOSWAMP/SRC/scoswamp.s`, `dist/SCOSWAMP.HDV`),
pas estimés.

---

## 1. État des lieux POM2

### 1.1 Le serveur AI-control existe et il est complet côté machine

`src/AiControlServer.h` / `src/AiControlServer.cpp` (242 + 1432 lignes).
Listener HTTP/1.1 **loopback uniquement**, port par défaut **6503**
(`AiControlServer.h:95`). Un thread worker, un client à la fois ; chaque
requête prend `EmulationController::stateMutex()` pour la tranche qui touche
CPU/Memory/slots (`AiControlServer.h:60-63`). Le commentaire d'en-tête
`AiControlServer.h:29-58` est le contrat de référence — `DEV.md:3431-3433` le
dit explicitement.

Table de routage : `AiControlServer.cpp:808-827`.

| Méthode | Chemin | Paramètres | Réponse | Impl. |
| --- | --- | --- | --- | --- |
| GET | `/status` | — | `{profile, cpu_mode, mode, cycles_per_frame, requests_served, cpu:{pc,a,x,y,p,sp,cycles}, disks:[...]}` | `:832-899` |
| POST | `/reset` | `{"kind":"soft\|hard\|cold"}` | `{kind}` | `:901-913` |
| GET | `/cpu` | — | registres + `cycles` | `:915-931` |
| POST | `/cpu` | `{pc,a,x,y,p,sp}` (tous optionnels) | `{}` | `:933-949` |
| GET | `/mem` | `addr` (0..0xFFFF), `len` (≤ **4096**), **`bank=main\|aux`** | `{addr,len,bank,data:"hex"}` | `:951-977` |
| POST | `/mem` | `?addr=N`, corps `{"data":"hex"}` | `{addr,written}` — **refuse `addr+len > 0xC000`**, banque **principale seulement** | `:979-1017` |
| POST | `/keyboard` | `{"text":"..."}` et/ou `{"raw":"..."}` | `{queued:N}` | `:1019-1037` |
| POST | `/disk` | `{slot,drive,path}` | monte une disquette **Disk II uniquement** | `:1112-1190` |
| POST | `/eject` | `{slot,drive}` | idem | `:1191-1240` |
| POST | `/snapshot/save` | `{"path":"*.pom2snap"}` | extension **obligatoire** | `:1241-1297` |
| POST | `/snapshot/load` | `{"path":...}` | contrôle du magic | `:1299-1350` |
| POST | `/speed` | `{cycles_per_frame}` ou `{preset:"1x\|2x\|max"}` | `{cycles_per_frame}` | `:1352-1380` |
| GET | `/screen.ppm` | — | PPM P6 binaire du framebuffer | `:1382-1428` |
| POST | `/mouse` | `{dx,dy}` / `{x,y,btn,reset}` | — | `:1039-1110` |

Authentification : en-tête `X-POM2-Token` ; **token vide ⇒ requêtes acceptées
sans authentification**, avec un test Origin+Host pour bloquer le DNS
rebinding (`:775-777`). Activation : trois clés de settings
(`ai_control_enable`, `ai_control_port`, `ai_control_token`, persistées
`src/MainWindow_Session.cpp:204-206`), ou la CLI `--ai-control[=PORT]`
(`src/CliDispatcher.cpp:230-241` → `src/MainWindow.cpp:825-837`) — **cette
voie force le token vide** (`MainWindow.cpp:828`).

### 1.2 Trois découvertes qui changent la conception

**(a) La page texte 80 colonnes est déjà lisible par HTTP, sans rien ajouter.**
`GET /mem` accepte un paramètre `bank` non documenté dans l'en-tête :
`AiControlServer.cpp:957-959` puis `:967-968` (`st.memory().auxData()`,
déclaré `src/Memory.h:695`). Deux requêtes suffisent :

```
GET /mem?addr=0x0400&len=1024             → colonnes IMPAIRES (1,3,…,79)
GET /mem?addr=0x0400&len=1024&bank=aux    → colonnes PAIRES  (0,2,…,78)
```

Et côté jeu, `SCOSWAMP/SRC/memory_swap.c:4-8` garantit que **le texte ne
quitte jamais `$400-$7FF`**, même en HGR plein écran : « Aucune copie d'écran
ici, et c'est le point important ». On peut donc lire l'écran texte à tout
instant, dans les trois modes vidéo. C'est ~4 Ko de hex par lecture contre
~645 Ko pour un `/screen.ppm` (560×384×3) : le polling d'attente de stabilité
doit passer par `/mem`, pas par le PPM.

**(b) La file de touches est auto-cadencée.** `pasteText`/`pasteRawKeys`
(`src/Memory.h:618-628` → `src/Keyboard.h:74-77`) poussent dans un
`std::deque<uint8_t>` dont **un octet est promu dans le verrou à chaque
effacement de strobe** (`Keyboard.h:20-24, 68`). Une séquence entière envoyée
en un seul POST est donc consommée exactement au rythme des `cgetc()` du jeu :
aucun `delay_ms` n'est nécessaire côté pom2. En revanche `pendingPasteSize()`
(`Memory.h:634`) n'est **pas exposé** par HTTP — c'est l'indicateur « toutes
les touches sont consommées » qui manque le plus.

**(c) Le décodage `& 0x7F` des tests de pom2 est faux pour SCOSWAMP.**
`tests/c2plus_boot_probe.cpp:52-81` (`scrapeTextPage` / `scrape80Col`) masque
à 7 bits. Or SCOSWAMP écrit sa barre de titre et ses rappels de touches en
**vidéo inverse** (`scoswamp.c:469-471` `revers(1)`, `scoswamp.c:1195`
`put_key`). Sur //e avec ALTCHARSET (allumé par le firmware 80 colonnes),
l'inverse occupe `$00-$7F` : `& 0x7F` sur un `$13` (S inverse) rend `0x13`,
illisible. Le décodeur du banc doit être :

```python
def cell(b):
    if b >= 0x80: return chr(b & 0x7F)     # normal
    if b <  0x20: return chr(b + 0x40)     # inverse @ A-Z [ \ ] ^ _
    if b <  0x40: return chr(b)            # inverse espace et ponctuation
    if b <  0x60: return '▯'          # MouseText — le jeu n'en met pas
    return chr(b)                          # inverse minuscules
```

Sans ça, **aucune assertion sur la Feuille d'Aventure** (`HAB 12/12 END 20/20
CHA 11/11`, ligne 0) ne passe.

### 1.3 Ce qui manque vraiment à POM2

Vérifié dans les sources, pas dans la doc.

| Manque | Preuve | Impact |
| --- | --- | --- |
| **Pas de headless + HTTP** | `src/pom2_headless.cpp` (420 l.) ne référence jamais `AiControlServer` ; flags `--rom --prom --disk --port --paste-after --setup --no-setup --frames --screenshot` (`:187-209`). L'API vit dans le binaire GUI, qui exige GLFW (aucun `GLFW_VISIBLE`/OSMesa dans l'arbre) | le banc tourne avec une fenêtre visible ; palliatifs `--kiosk`, `POM2_AUTO_QUIT=<s>`, `POM2_AUTO_BOOT_HDV=<s>` (`src/main.cpp:847-861`) |
| **Pas de lecture texte** | `/screen.ppm` = pixels ; `scrape80Col` dupliqué dans `tests/`, jamais partagé ; grep vide sur `Debugger_ImGui.cpp` | à faire côté banc (§5.1) ou à ajouter (§4.5) |
| **Pas d'écriture en RAM aux** | `POST /mem` passe par `mem.memWrite()` seul (`:1010`) | sans effet sur la porte cachée (la BSS du jeu est en RAM principale) |
| **`.hdv` non remontable par HTTP** | `handleDiskInsert` valide contre le Disk II primaire (`:1152-1165`) ; `hdv5_` (`AiControlServer.h:157`) est attaché (`:428`) et nullé (`:444`) mais **référencé par aucun handler** | pas de changement de disque à chaud |
| **`.hdv` mis en cache en RAM** | `src/Block512Backing.h:37-47` (`loadImage` lit *inline*, ≤ 32 MiB), membres `image_`/`dirtyBlocks_`/`writeBack_` (`:214-230`) ; aucun `reload`, aucun watch de mtime | une réécriture hôte à chaud est **invisible**, et un `flush()` write-back la **remplace** ; seul garde-fou `preserveNewerThan`/`mountTime_` (`ProDOSVolume.h:105-109`), réservé aux volumes synthétisés depuis un dossier |
| **Snapshots sans média** | `MachineSnapshot.h:33-40` : `/snapshot` passe `includeSlots=false`. Magic `POM2SNAP`, v2, sections `CPU` (17 o), `MEM` (64 KiB), `MEX` (aux + LC + RamWorks + soft-switches + `DisplayState`) — `src/SnapshotIO.h:20-56`, `src/MachineSnapshot.cpp:36-80` | restaure **tout l'état du jeu en RAM**, laisse le disque tel quel : idéal pour mettre en cache un état de départ |
| **E/S jailées au CWD** | `safeCwdRelativePath`, `AiControlServer.cpp:84-116` | le CWD de lancement doit contenir le `.hdv` et les snapshots |
| **Aucun client Python** | `ls tools/` : rien ; grep `6503\|requests\|urllib` sur `tools/`+`docs/` : rien. Seuls exemples : les trois `curl` de `src/MainWindow_DevicePanels.cpp:753-758` | harnais à copier : `tests/ai_control_server_smoke_test.cpp` (`connectLoopback` 20 × 10 ms `:65-84` ; `Connection: close` comme fin de réponse `:96-108`) |

---

## 2. État des lieux du jeu

### 2.1 Le flux

`main()` — `scoswamp.c:2050-2112`. Met `LOWBSS` à zéro (`:2055`), initialise
`app`, `chdir("/SCOSWAMP")`, `select_language()` (qui **sème les dés avec le
temps d'attente de la première touche**, `dice.c:34-54`), `messages_load`,
`load_scene(0)`, puis la boucle : *tant que `app.pending_scene >= 0`, le
consommer et appeler `load_scene`, en remettant `restoring` à 0 ; sinon
`key = cgetc(); handle_user_input(key)`*. La lecture de `pending_scene`
**précède** le `cgetc()` : c'est la charnière de toute la conception (§4.3).

`handle_user_input` — `:1985-2048`. `ESPACE`/`RETURN`/`ESC` →
`cycle_video_mode()` ; `I` → `show_inventory(0)` ; `H` → `show_help()` ;
`S`/`L` → `show_saves(saving)` ; `Q` → `exit(0)` ; `A`-`Z` → choix, avec
consommation de la Pierre exigée (`:2037`), don de la Pierre offerte
(`:2039`), consommation d'objet si `obj_mode == 3` (`:2040`),
`roll_character()` si `!hero_ready` (`:2044`), puis `load_scene`.

`load_scene` — `:1779-1902`. Remet à zéro les champs de page, appelle
`display_scene_text` (c'est **la lecture du fichier qui applique les effets
d'entrée**), puis dans cet ordre : court-circuit `V` (`:1817`),
`scene_mark_visited` (`:1821`), jet `ED` (`:1832`), test `CS` (`:1845`), jet
`CL` (`:1852`), choix de Pierres `PC` (`:1859`), image `B<id>.RLE` puis
`N<id>.RLE` (`:1866-1868`), `monster_seal` + `monster_enter` (`:1872-1877`),
`run_combat()` (`:1884`).

`classify_line` — `:735-1022`. 30 directives reconnues sur `l[0..2]`, avec un
filtre `restoring` (`:751-758`) qui **inhibe** `E E0 ED P PC PD PO PX G GX GA
CE TR V` à la reprise d'une sauvegarde. Inventaire complet en §5.2.

### 2.2 Format de sauvegarde SCS3 — vérifié octet par octet

`pack_save` `:191-207`, `unpack_save` `:210-223`, `save_checksum` `:180-185`.
`SAVE_SIZE = 8 + 32 + sizeof(Character) + 52 + 160 = **276**` (`:156-161`).
`save_data` est un alias de `file_buffer` (`:162`), donc de `$1000`.

| Offset | Taille | Contenu |
| --- | --- | --- |
| 0 | 4 | `"SCS3"` |
| 4 | 1 | somme de contrôle = **XOR des octets 5..275** (`:183`) |
| 5 | 2 | `current_scene`, u16 little-endian |
| 7 | 1 | `language[0]` : `'F'` ou `'E'` (`unpack_save` recalcule `[1]`, `:215`) |
| 8 | 32 | titre de la page (ligne `T`), NUL-padded, 31 car. utiles |
| 40 | 24 | `Character` |
| 40..45 | 6 | `hab, hab0, end, end0, cha, cha0` |
| 46 | 2 | `gold` u16 LE |
| 48 | 1 | `weapon_bonus` (0..2) |
| 49 | 12 | `stones[STONE_COUNT]`, un compteur par Pierre |
| 61 | 2 | `objects` u16 LE, 1 bit par `Object` (11 objets) |
| 63 | 1 | `amulets`, 1 bit par `Amulet` (6) |
| 64 | 52 | mémoire des clairières : bit `s&7` de l'octet `s>>3` (`rules.c:394-405`) |
| 116 | 160 | mémoire des monstres : 40 × `{scene u16 LE, index u8, end u8}` (`rules.c:362-371`) |

Ordre des énumérations, pour l'encodeur hôte (`rules.h:23-61`) :
`STONE` = HABILETE, ENDURANCE, CHANCE, FEU, GLACE, ILLUSION, AMITIE,
CROISSANCE, BENEDICTION, TERREUR, FLETRISSURE, MALEDICTION.
`Object` = ANNEAU, CAPE, CHAINE, AIMANT, FIOLE, BAIE, EPEMAGIQUE, BIJOU,
CORNE, PLUMES, ANTHERIQUE. `Amulet` = LOUP, FLEUR, OISEAU, ARAIGNEE,
GRENOUILLE, FAUSSE_OISEAU.

`load_game(slot)` (`:243-252`) : `chdir /SCOSWAMP/SAVE`, `fopen("PARTIE<n>")`,
`fread` de 276 octets exactement, puis `unpack_save()` — qui pose
`hero_ready=1`, `restoring=1`, `pending_scene=scene`. `show_saves`
(`:1952-1983`) liste les dix emplacements par `slot_title` (`:257-269`, ne lit
que les 40 premiers octets et exige `"SCS3"`).

Un prototype d'encodeur, **écrit et testé** pendant cette étude, est dans
`scratchpad/forge_save.py` (voir §4.3).

### 2.3 Adresses runtime — dérivées de `build.map` + `scoswamp.s`

Segments (`SCOSWAMP/SRC/build.map:301-313`) :

```
LOWBSS  $1000-$1FAC   (4013 o ; il ne reste que 83 o sous $2000)
CODE    $4085-$97FF
RODATA  $9800-$9D8A
DATA    $9D8B-$9E2F
BSS     $9E8E-$A311   (ONCE $9E8E-$9F4D est recouvert après le démarrage)
LC      $D400-$DF09   (3 030 / 3 072 o — plein)
```

`tools/check-memory.sh --himem 0xBF00 --stack 0x0180 SCOSWAMP/SRC/build.map`
(les valeurs du `Makefile:56,63`) rend : *Empreinte 25 361 o sur 32 128 o ;
**marge de 6 767 octets***. C'est le budget de la porte cachée.

`_app` **n'est pas dans la liste d'exports** de `build.map` (ld65 n'y met que
les symboles réellement importés par un autre module) mais il est le
**premier symbole du premier bloc `BSS`** de `scoswamp.s:242-245`, et
`scoswamp.o` est le premier contributeur BSS (`build.map:303`,
`BSS Offs=000000`). Donc :

```
_app        = $9E8E   (215 octets — .res 215 à scoswamp.s:245)
_restoring  = $9F65   (1)      scoswamp.s:250
_scene_title= $9F66   (2)
_body_lines = $9F68   (38)
_body_count = $9F8E   (1)
_title_bar  = $9F8F   (81)
_file_buffer= $1000   (1253)   premier symbole LOWBSS, = save_data
_seen       = $A1D8   (160)    rules.o BSS Offs=$34A → $9E8E+$34A
_visited    = $A278   (52)
_state      = $9D8C   (4)      dice.o DATA Offs=1 → $9D8B+1 ; LCG 32 bits
```

`_state` vérifié dans le binaire : `SCOSWAMP.BIN` offset `$9D8C-$4000` =
`01 00 00 00`.

Décomposition de `AppState` (aucun bourrage en cc65 ; le total 215 recoupe
`.res 215`, et `scoswamp.s:343` `stz _app+43` confirme `num_choices`) :

| Champ | Off | Adresse | Taille |
| --- | --- | --- | --- |
| `current_scene` | 0 | `$9E8E` | 2 |
| `video_mode` | 2 | `$9E90` | 1 |
| `choices[5]` | 3 | `$9E91` | 40 (8 o/choix) |
| `num_choices` | 43 | `$9EB9` | 1 |
| `language[3]` | 44 | `$9EBA` | 3 |
| `imgPath` / `txtPath` | 47 / 57 | `$9EBD` / `$9EC7` | 10 / 10 |
| `has_image` | 67 | `$9ED1` | 1 |
| **`hero`** | 68 | **`$9ED2`** | 24 |
| ↳ `hab, hab0, end, end0, cha, cha0` | 68-73 | `$9ED2`..`$9ED7` | 6 |
| ↳ `gold` | 74 | `$9ED8` | 2 |
| ↳ `weapon_bonus` | 76 | `$9EDA` | 1 |
| ↳ `stones[12]` | 77 | `$9EDB` | 12 |
| ↳ `objects` | 89 | `$9EE7` | 2 |
| ↳ `amulets` | 91 | `$9EE9` | 1 |
| `hero_ready` | 92 | `$9EEA` | 1 |
| `foes[3]` | 93 | `$9EEB` | 87 (29 o/monstre) |
| `foe_count` / `foe_cur` | 180 / 181 | `$9F42` / `$9F43` | 1 / 1 |
| `flee_target` | 182 | `$9F44` | 2 |
| **`pending_scene`** | 184 | **`$9F46`** | 2 |
| `revisit` | 186 | `$9F48` | 2 |
| `choose_n` / `choose_cats[3]` | 188 / 189 | `$9F4A` / `$9F4B` | 1 / 3 |
| `luck_ok/ko/dok/dko` | 192-199 | `$9F4E`..`$9F55` | 2 ×4 |
| `win_scene` | 200 | `$9F56` | 2 |
| `dice_n` / `dice_carac` | 202 / 203 | `$9F58` / `$9F59` | 1 / 1 |
| `cs_ok/cs_ko/cs_carac` | 204-208 | `$9F5A`..`$9F5E` | 2+2+1 |
| `mb_ok/mb_ko` | 209-212 | `$9F5F`..`$9F62` | 2+2 |
| `last_loss` / `dv_done` | 213 / 214 | `$9F63` / `$9F64` | 1 / 1 |

Toutes ces adresses sont **< `$C000`**, donc atteignables par `POST /mem`
(qui refuse `addr+len > 0xC000`, `AiControlServer.cpp:997`).

### 2.4 L'image disque — l'emplacement 9 est déjà un bloc à patcher

Analyse de `dist/SCOSWAMP.HDV` (7 326 blocs). Répertoire racine bloc 2-3 ;
`SAVE` est un sous-répertoire, clé **bloc 5878**. Ses entrées (39 octets,
première à l'offset 4) :

```
PARTIE0 … PARTIE9 : storage_type=1 (seedling), blocks_used=1, EOF=2
PARTIE9 : entrée au bloc 5878 offset 394, bloc de données 5888
```

Les dix `SCOSWAMP/SAVE/PARTIEn` du dépôt font 2 octets. Un seedling ProDOS
porte jusqu'à 512 octets : **276 octets y entrent sans réallocation, sans
toucher la bitmap ni le type de stockage**. Un patch hôte se réduit donc à
deux écritures :

```
bloc 5888 (offset fichier 3 014 656)  ← les 276 octets SCS3
entrée 5878×512+394, champ EOF (+$15) ← 14 01 00   (=276, 3 octets LE)
```

`ADVKIT/TOOLS/build_prodos_volume.cpp` (85 l.) montre la même
manipulation d'entrées : offsets `[0x00]` storage<<4|namelen, `[0x01..]` nom,
`[0x10]` type, `[0x11..0x12]` clé, `[0x13..0x14]` blocs, `[0x15..0x17]` EOF,
`[0x1F..0x20]` aux type — il patche l'aux type de `SCOSWAMP` à `$4000`
(`:58-75`) et duplique les champs de compatibilité ProDOS 8 des en-têtes de
sous-répertoire (`:38-53`, sans quoi BASIC.SYSTEM répond `FILE NOT FOUND`).
Il s'appuie sur `pom2::buildVolumeFromFolder` (`pom2/src/ProDOSVolume.h:70`) —
seule API disponible, **dossier hôte → volume entier** ; il n'existe *aucune*
fonction « ouvrir un `.hdv` et y écrire un fichier ».

---

## 3. Options de porte cachée, comparées

| | Option | Coût binaire | Ce qu'elle permet | Robustesse | Effort | Ajouts POM2 |
| --- | --- | --- | --- | --- | --- | --- |
| **a1** | `PARTIE9` forgé + `make hdv` + relance de pom2 | **0 o** | état **complet** (page, 3 caracs + plafonds, or, bonus d'arme, 12 Pierres, 11 objets, 6 amulettes, 412 bits de clairières, 40 monstres blessés) | très haute : format versionné, checksum, `unpack_save` refuse le reste | faible (`forge_save.py` + une cible make) | aucun, mais **relance obligatoire** (§1.3-5) |
| **a2** | `PARTIE9` forgé **patché en place** dans le `.hdv` (bloc 5888 + EOF) | **0 o** | idem a1 | haute ; casse si le volume est reconstruit (les numéros de bloc bougent) ⇒ relire le catalogue à chaque fois | faible (fait, testé) | aucun, mais relance quand même (cache RAM) |
| **a3** | idem a2 **+ `POST /hdv` de remontage** | **0 o** | idem, **sans relancer le process** | haute | faible côté jeu, ~30 lignes côté pom2 | `POST /hdv` (le membre `hdv5_` est déjà attaché, `AiControlServer.h:157`) |
| **b1** | séquence secrète `*` + 3 chiffres → `pending_scene` | **~110 o** (90-130) | **page seule** | moyenne : un `*` dans un titre de choix ne peut pas déclencher (la touche est lue hors saisie), mais la porte est dans le binaire livré | très faible | aucun |
| **b2** | grammaire `*<lettre><valeur>` (page + HAB/END/CHA/OR) | **~250-300 o** | page + caracs + or | moyenne | faible | aucun |
| **b3** | même grammaire étendue aux Pierres, objets, amulettes, clairières | **500-800 o** | état complet | moyenne | moyen | aucun |
| **b4** | b1/b2 sous `#ifdef SCOSWAMP_CHEAT` + cible `make debug` | **0 o en release** | selon la variante | haute, mais le binaire testé n'est plus celui livré | faible | aucun |
| **c** | injection mémoire directe (`POST /mem` sur `_app`, `_visited`, `_seen`, `_state`) | **0 o** | état **complet** + **dés déterministes** (`_state`) + états *impossibles* (mi-combat, `foes[]` en cours) | fragile au relink → à corriger par un **fichier de symboles généré au build** (`ld65 -Ln`) | faible | rien d'obligatoire ; `GET /screen.txt` et `paste_pending` très utiles |
| **d** | fichier `CHEAT` sur le disque, lu au démarrage | **~200-300 o** + le nom + une E/S ProDOS de plus | état complet si le format est riche | moyenne ; un `CHEAT` oublié sur le disque du joueur change le jeu en silence | moyen | aucun |

Notes de chiffrage. La marge est de 6 767 o, donc **toutes** les options
tiennent — la question est le coût dans le binaire *livré*. Les estimations
b1/b2/b3 s'appuient sur les calibrages que le code documente lui-même :
« chaque emplacement [`Choice`] coûte 77 octets » (`scoswamp.c:32`), « une
version à trois wrappers et deux `if` coûtait 150 octets » (`rules.h:134`),
« 40 octets pour choisir entre un et deux [dés] » (`scoswamp.c:1420`), « deux
champs de 64 octets, 96 octets de BSS dormants » (`scoswamp.c:38`). Un `else
if (key == '*')` en cc65 ≈ 8-12 o ; une boucle de trois chiffres avec `n*10`
≈ 60-80 o ; l'affectation ≈ 10 o.

Ce que **c** permet et que **a** ne permet pas : entrer dans un état que le
format de sauvegarde ne sait pas décrire — un combat au troisième assaut avec
`foes[1].end = 3` et `foe_cur = 1`, une page dont `luck_dok`/`luck_dko` sont
posés à la main, `last_loss` réglé pour choisir la branche d'une cascade `DV`.
Et surtout : **fixer `_state` rend les dés reproductibles**, ce qui transforme
« l'ENDURANCE a baissé » en « l'ENDURANCE valait 20, elle vaut 18 ».

Ce que **a** permet et que **c** ne permet pas : tester le chemin de
sauvegarde/chargement lui-même, et livrer un bug reproductible qu'un humain
rejoue par `[L] 9` sans outillage.

---

## 4. Recommandation et conception détaillée

### 4.1 La combinaison retenue

**Primaire : (c)** injection mémoire sur le binaire de release **non modifié**,
adressée par un fichier de symboles généré au link. Coût 0 octet, aucune porte
dans le jeu livré, et c'est le seul mécanisme qui atteint les états de
mi-combat et les dés déterministes.

**Secondaire : (a2)** `PARTIE9` forgé et patché en place, pour la famille de
scénarios « la sauvegarde elle-même » et pour les répros humaines. Coût 0
octet.

**Rejetées :** (b) et (d) — payantes en octets dans le binaire livré pour
strictement moins de pouvoir que (c). (b4) reste en réserve si l'on veut une
porte pour du test *à la main* sans HTTP : elle ne coûte rien en release.

### 4.2 Exporter les adresses au build (le seul point fragile de (c))

`ld65` sait déjà le faire : `-Ln name  Create a VICE label file`. Une ligne à
ajouter à `SCOSWAMP/SRC/Makefile:67-68` :

```make
LDFLAGS = -t $(TARGET) -C $(LDCFG) -Wl -D,__EXEHDR__=0 -Wl -S,0x4000 \
          -Wl -D,__HIMEM__=$(HIMEM) -Wl -D,__STACKSIZE__=$(STACK) \
          -Wl -m,$(MAPFILE) -Wl -Ln,build.lbl
```

Le `.lbl` contient `al 009E8E ._app` pour **tous** les symboles, y compris
ceux que `build.map` omet. Le banc le lit et en tire la table d'adresses.
Deux garde-fous, tous deux gratuits :

1. **Invariant de taille** : `_restoring - _app == 215`. S'il ne vaut pas 215,
   `AppState` a changé et la table d'offsets Python est périmée ⇒ le banc
   refuse de démarrer. (Même garde pour `_visited - _seen == 160`.)
2. **Sonde runtime** : avant toute écriture, lire `app.language` à `$9EBA` et
   vérifier `b"FR"` ou `b"EN"`. Si ce n'est pas le cas, l'adresse est fausse
   ou le jeu n'a pas fini de démarrer ⇒ abandon.

Les offsets *internes* à `AppState` restent une table Python maintenue à la
main (cc65 n'exporte pas de layout de structure). Le point 1 les pinne : toute
modification de `AppState` change la taille et fait échouer le banc bruyamment,
au lieu de poker au hasard.

### 4.3 Le geste d'injection, pas à pas

L'astuce est que la boucle principale relit `pending_scene` **avant** chaque
`cgetc()` (`scoswamp.c:2101-2108`). Donc :

```
1. attendre un écran stable (le jeu est bloqué dans cgetc)
2. POST /mem sur _state        → semence des dés
3. POST /mem sur _app+68 (24 o) → la Feuille d'Aventure d'un coup
4. POST /mem sur _app+92        → hero_ready = 1
5. POST /mem sur _visited, _seen → mémoire des clairières et des monstres
6. POST /mem sur _restoring      → 0 (rejouer les effets d'entrée)
                                    ou 1 (les inhiber, comme une reprise)
7. POST /mem sur _app+184 (2 o)  → pending_scene = <page>
8. POST /keyboard {"raw":""} → une touche inerte ('Z' : la branche
   lettre calcule choice_num=25 >= num_choices et ne fait rien)
9. la boucle reprend, consomme pending_scene, appelle load_scene(<page>)
```

Le pas 6 est le levier le plus intéressant : `restoring=0` fait **rejouer**
`E`, `E0`, `ED`, `G`, `GX`, `GA`, `P`, `PC`, `PD`, `PO`, `PX`, `CE`, `TR`, `V`
(filtre `scoswamp.c:751-758`), donc chaque page peut être testée « en visite
fraîche ». `restoring=1` teste l'autre moitié du filtre.

Détail à respecter : `hero_ready` doit valoir 1 **avant** le pas 8, sinon la
première prise de choix déclenche `roll_character()` (`:2044`) et écrase les
caracs injectées.

Deux mises en garde :

- Les 192 premiers octets de la BSS ($9E8E-$9F4D) recouvrent le segment
  `ONCE` (`build.map:311-312`, `__ONCE_RUN__ == __BSS_RUN__`). Après le
  démarrage, c'est bien `_app`. **Ne rien injecter avant que l'écran de
  langue soit affiché.**
- `POST /mem` passe par `mem.memWrite()` (`:1010`), pas par un `memcpy` : ça
  respecte la protection ROM et les soft-switches, donc les écritures dans
  `$9Exx`/`$A2xx` sont de vraies écritures RAM. Correct ici.

### 4.4 `forge_save.py` — écrit et vérifié

Prototype dans `scratchpad/forge_save.py` (85 l.). Il construit les 276 octets
SCS3 depuis des arguments nommés (page, langue, titre, `(hab,hab0)`,
`(end,end0)`, `(cha,cha0)`, or, bonus d'arme, Pierres, objets, amulettes,
clairières visitées, monstres blessés), fait le XOR sur `[5:]`, puis :

```python
def patch_hdv(hdv, blob, entry_blk=5878, entry_off=394, key_blk=5888):
    with open(hdv, "r+b") as f:
        f.seek(key_blk * 512); f.write(blob.ljust(512, b"\0"))
        f.seek(entry_blk * 512 + entry_off + 0x15)     # EOF, 3 octets LE
        f.write(bytes((len(blob) & 0xFF, (len(blob) >> 8) & 0xFF, 0)))
```

Test effectué sur une **copie** de `dist/SCOSWAMP.HDV` — relecture des octets
écrits :

```
SCS3 276 octets, checksum $D0
entry: st 1 name b'PARTIE9' eof 276 used 1
magic b'SCS3' cs stored $D0 computed $D0 scene 155 lang F title b'FORGE 155'
carac [12,12,24,24,12,12] gold 99 stones [0,0,2,3,0,...] obj 0022 amu 05
visited bytes non nuls [(0,'0x2'), (19,'0x8')]     # clairières 1 et 155
monstre slot0 (12, 0, 6)                            # page 012, index 0, END 6
```

Les numéros de bloc doivent être **redécouverts** à chaque reconstruction du
volume : ajouter une résolution de `/SCOSWAMP/SAVE/PARTIE9` par parcours du
catalogue (blocs 2-3 racine → entrée `SAVE` type `$0F` → clé 5878 → entrée
`PARTIE9`), 25 lignes, plutôt que des constantes. Voir §6.10.

### 4.5 Ce qu'il faut ajouter à POM2, par rendement décroissant

| Prio | Ajout | Où | Taille | Pourquoi |
| --- | --- | --- | --- | --- |
| 1 | `GET /screen.txt` — 24 lignes × 80 colonnes ASCII, désentrelacé main/aux, décodage inverse/ALTCHARSET, page choisie par `videoTextPage2()` | nouveau handler + route à `AiControlServer.cpp:824` ; factoriser `scrape80Col` de `tests/c2plus_boot_probe.cpp:67` dans un header partagé, et l'adressage de `src/Apple2Display_Internal.h:38` | ~50 l. | supprime 2 requêtes hex + tout le décodage côté banc, et le rend correct une fois pour toutes |
| 2 | `paste_pending` dans `/status` | `AiControlServer.cpp:880-897`, `mem.pendingPasteSize()` (`Memory.h:634`) | 2 l. | « toutes les touches sont consommées » sans heuristique de temps |
| 3 | `POST /hdv {"slot":5,"path":...}` | `AiControlServer.cpp` : le membre `hdv5_` est déjà attaché (`:428`) et `ProDOSBlockCard::loadImage`/`adoptImage` existent | ~30 l. | débloque l'option (a3) : changer d'état disque sans relancer le process |
| 4 | `--ai-control[=PORT]` dans `pom2_headless` | `src/pom2_headless.cpp:187-209` — il a déjà `EmulationController` + `Apple2Display` | ~20 l. | vrai headless pour la CI |
| 5 | `POST /mem?bank=aux` | symétrique de `:957-968`, via `auxDataMutable()` (`Memory.h:696`) | ~10 l. | injection de texte, pas nécessaire à la porte cachée |
| 6 | `GET /mem` : lever `len ≤ 4096` à 8192 | `:961` | 1 l. | lire les deux pages texte en une requête |

---

## 5. Plan de test automatisé

### 5.1 Squelette du pilote hôte

```python
#!/usr/bin/env python3
"""scoswamp_drive.py — banc de test de SCOSWAMP piloté par l'API AI-control."""
import hashlib, json, re, struct, time, urllib.request

BASE, TOKEN = "http://127.0.0.1:6503", None   # TOKEN = ai_control_token, ou None

# ── transport ────────────────────────────────────────────────────────────
def rq(path, body=None):
    req = urllib.request.Request(BASE + path,
            data=json.dumps(body).encode() if body is not None else None,
            headers={"X-POM2-Token": TOKEN} if TOKEN else {})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())

def peek(addr, n, bank="main"):
    q = f"/mem?addr={addr}&len={n}" + ("&bank=aux" if bank == "aux" else "")
    return bytes.fromhex(rq(q)["data"])

def poke(addr, data):
    assert addr + len(data) <= 0xC000          # POST /mem refuse I/O et ROM
    return rq(f"/mem?addr={addr}", {"data": data.hex()})["written"]

def keys(s): return rq("/keyboard", {"raw": s})      # ESC = "\x1b"

# ── écran texte 80 col ($400-$7FF, jamais déplacé : memory_swap.c:4-8) ────
def _cell(b):
    if b >= 0x80: return chr(b & 0x7F)         # normal
    if b <  0x20: return chr(b + 0x40)         # inverse majuscules
    if b <  0x40: return chr(b)                # inverse ponctuation
    if b <  0x60: return "\u25af"                  # MouseText
    return chr(b)                              # inverse minuscules

def screen():
    main, aux = peek(0x0400, 1024), peek(0x0400, 1024, "aux")
    out = []
    for r in range(24):                        # entrelacement texte Apple II
        base = 0x80 * (r % 8) + 0x28 * (r // 8)
        out.append("".join(_cell(aux[base+c]) + _cell(main[base+c])
                           for c in range(40)))
    return out

def stable(tries=40, pause=0.05):
    """Attend que l'écran ne bouge plus deux relevés de suite."""
    prev = None
    for _ in range(tries):
        cur = hashlib.blake2s("\n".join(screen()).encode()).digest()
        if cur == prev: return screen()
        prev = cur; time.sleep(pause)
    raise TimeoutError("l'écran ne se stabilise pas")

def press(k): keys(k); return stable()

# ── table d'adresses, lue dans build.lbl (ld65 -Ln) ──────────────────────
SYM = {}
def load_symbols(path="SCOSWAMP/SRC/build.lbl"):
    for line in open(path):
        m = re.match(r"al\s+([0-9A-Fa-f]{6})\s+\.(\S+)", line)
        if m: SYM[m.group(2)] = int(m.group(1), 16)
    assert SYM["_restoring"] - SYM["_app"] == 215, "AppState a changé"
    assert SYM["_visited"]  - SYM["_seen"] == 160, "rules.c a changé"

OFF = dict(current_scene=0, video_mode=2, num_choices=43, language=44,
           has_image=67, hero=68, hero_ready=92, foes=93, foe_count=180,
           foe_cur=181, flee_target=182, pending_scene=184, revisit=186,
           luck_ok=192, win_scene=200, dice_n=202, cs_ok=204, mb_ok=209,
           last_loss=213, dv_done=214)
def A(f): return SYM["_app"] + OFF[f]

# ── la porte cachée ──────────────────────────────────────────────────────
def sheet_bytes(hab=12, end=20, cha=11, gold=20, bonus=0,
                stones=(), objects=(), amulets=()):
    """Les 24 octets de Character, dans l'ordre de rules.h:79-91."""
    st = bytearray(12)
    for name, n in stones: st[STONES.index(name)] = n
    return (bytes([hab, hab, end, end, cha, cha])
            + struct.pack("<H", gold) + bytes([bonus]) + bytes(st)
            + struct.pack("<H", sum(1 << OBJECTS.index(o) for o in objects))
            + bytes([sum(1 << AMULETS.index(a) for a in amulets)]))

def goto(page, seed=0x1234, replay=True, visited=(), foes_seen=(), **kw):
    """Téléporte le héros à `page` avec l'état demandé."""
    assert peek(A("language"), 2) in (b"FR", b"EN"), "adresse _app invalide"
    poke(SYM["_state"], seed.to_bytes(4, "little"))       # dés déterministes
    poke(A("hero"), sheet_bytes(**kw))
    poke(A("hero_ready"), b"\x01")                        # sinon roll_character
    if visited:   poke(SYM["_visited"], bits52(visited))
    if foes_seen: poke(SYM["_seen"], slots160(foes_seen))
    poke(SYM["_restoring"], b"\x00" if replay else b"\x01")
    poke(A("pending_scene"), page.to_bytes(2, "little", signed=True))
    keys("Z")            # touche inerte : choice_num=25 >= num_choices,
    return stable()      # la boucle reprend et consomme pending_scene

# ── assertions ───────────────────────────────────────────────────────────
BAR = re.compile(r"HAB (\d+)/(\d+) END (\d+)/(\d+) CHA (\d+)/(\d+)")
def sheet(rows=None):
    m = BAR.search((rows or screen())[0])      # ligne 0, vidéo inverse
    assert m, "Feuille d'Aventure absente de la barre de titre"
    v = list(map(int, m.groups()))
    return dict(hab=v[0], hab0=v[1], end=v[2], end0=v[3], cha=v[4], cha0=v[5])

def choices(rows=None):
    """Les lettres offertes lignes 20-23 ; '-)' = choix barré."""
    return [m for r in (rows or screen())[20:24]
              for m in re.findall(r"(?:^|\s{2})([A-Z-]\))", r)]

def sc_benediction_155():                      # scénario 10 de §5.3
    before = sheet(goto(155, cha=9))
    after  = sheet(press(" "))
    assert after["cha"]  == before["cha"]  + 2
    assert after["cha0"] == before["cha0"] + 2, "E0 doit lever le PLAFOND"
```

Le pilote suppose pom2 lancé depuis le dossier qui contient l'image (le CWD
est le jail de `safeCwdRelativePath`, `AiControlServer.cpp:84-116`) :

```
cd /Users/gistair/src/pom2adventure/dist
/Users/gistair/src/pom2/build/POM2 --ai-control=6503 --speed 200000 SCOSWAMP.HDV
```

`--speed`/`POST /speed {"preset":"max"}` accélère les chargements ProDOS et le
décodage RLE ; le pilote le remet à `1x` pour les scénarios sensibles au temps.

### 5.2 Directives réellement présentes — la base des scénarios

Relevé exhaustif sur `SCOSWAMP/TEXTFR` (412 fichiers). Les colonnes sont le
nombre de **lignes** et les pages représentatives.

| Code | Occ. | Pages | Code | Occ. | Pages |
| --- | --- | --- | --- | --- | --- |
| `T` | 412 | toutes | `CN` | 4 | N006, N092, N229, N290 |
| `C` | 567 | 334 pages | `CA` | 4 | N015, N226 (×3) |
| `E` | 44 | END 20, HAB 12, CHA 10, BONUS 2 | `P` | 4 | N189 (×2), N381 (×2) |
| `CU` | 43 | 17 pages, ex. N400, N074 | `PC` | 4 | N206 `PC 6 NM`, N283 `PC 1 B`, N371 `PC 6 NB`, N396 |
| `M` | 42 | 32 pages | `GA` | 3 | N099 `GA 0`, N207 `GA 500`, N266 `GA 250` |
| `MV` | 31 | 31 pages | `CS` | 3 | N091, N257, N377 |
| `G` | 16 | N042, N154, N184… | `DV` | 3 | **N156 seule** (`DV 0 241`, `DV 5 193`, `DV 99 326`) |
| `CL` | 16 | N005, N024 `CL 273 297 0 -2`, N041 | `E0` | 2 | N087 `-2 HAB`, N155 `+2 CHA` |
| `CF` | 15 | N012, N120… | `MD` | 2 | N012 `MD 4`, N026 `MD 3` |
| `V` | 14 | N010, N350, N336… | `MS` | 2 | N012 `MS 6`, N341 `MS 6` |
| `ED` | 9 | N044, N135 `ED OR +1`, N274 | `GU` | 2 | N006 `GU BA 175`, N015 `GU BJ 276` |
| `CI` | 6 | N015, N092, N229, N290, N350 (×2) | `MB` | 1 | **N079 seule** (`MB 360 128`) |
| `GX` | 5 | N049, N253… | `PD`/`PO`/`PX`/`TR` | 1 chacun | N289 / N407 / N017 / N408 |
| `CE` | 4 | N058, N073, N190, N249 | `CP` | **0** | **code mort** (`scoswamp.c:950`) |

Deux enseignements pour le banc : `CP` n'est jamais exercé par les données
(soit on le supprime, soit on lui fabrique une page de test), et huit
directives n'ont qu'une ou deux pages — elles ne seront jamais atteintes par
une exploration au hasard. C'est précisément l'argument de la porte cachée.

### 5.3 Les scénarios à couvrir

Chacun se lit « `goto(page, état)`, des touches, des assertions ». Les 34
entrées ci-dessous couvrent les 30 directives, les cinq écrans hors-page
(sac, aide, sauvegardes, création, mort) et les trois modes vidéo.

**Navigation et rendu**

1. `goto(1)` → la barre porte `Le chemin vers le Marais` puis `I:SAC H:AIDE` ;
   24 lignes, rien au-delà de la colonne 79.
2. Page à 5 choix (`N152`, `N191`, `N256`, `N374`, `N387`) → 5 lettres `A)`..`E)`
   sur ≤ 4 lignes, deux par ligne si les deux titres font ≤ 36 car.
   (`render_choices`, `scoswamp.c:514-527`).
3. Page terminale (`N003`, `N313`, `N401`) → 0 lettre offerte.
4. `ESPACE` sur une page illustrée → `video_mode` (`$9E90`) cycle 0→1→2→0, et
   l'écran texte reste intact en mode 1 (invariant de `memory_swap.c:4-8`).
5. Page sans image (`has_image == 0` à `$9ED1`) et page de combat avec image
   `B<id>` (`IMG/N400/B402.RLE.BIN`) → `has_image == 1`, combat en mode mixte
   (`run_combat`, `scoswamp.c:1526`).
6. Page la plus longue du corpus (`TEXTFR/N350/N361.TXT`, 1252 o) → 19 lignes
   de corps au plus, rien ne scrolle (`FILE_BUFFER_SIZE 1253`, `:144-147`).

**Effets d'entrée**

7. `N017` (`PX` + `E ENDURANCE -3`) avec Pierres et objets injectés →
   `hero.stones` (`$9EDB`) et `hero.objects` (`$9EE7`) nuls, END -3.
8. `N042` (`G FI`) → bit `FIOLE` (4) posé ; `N154` (`G LOUP`) → bit
   `AMULET_LOUP` posé dans `hero.amulets` (`$9EE9`) ; `N049` (`GX ANNEAU`) →
   bit 0 retiré.
9. `N087` (`E0 HABILETE -2`) → `hab` **et** `hab0` baissent ; un `E HABILETE
   +5` ultérieur ne dépasse plus le nouveau plafond.
10. `N155` (`E0 CHANCE +2`) sur un héros à sa CHANCE de départ → `cha` et
    `cha0` montent tous les deux (le cas que `rules.h:127-131` motive).
11. `N340` (`E BONUS +2`) → `weapon_bonus` (`$9EDA`) = 2, et reste à 2 après
    `N241` (`E BONUS +1`).
12. `N207` (`GA 500`) avec 3 amulettes → or += 1500, `amulets` = 0 ; puis
    `N099` (`GA 0`) → or inchangé, amulettes tout de même consommées.
13. `N289` (`PD`) et `N407` (`PO`) → 2 puis 1 possessions retirées
    (`lose_items`).
14. `goto(042, replay=False)` (`restoring=1`) → **aucun** effet d'entrée ;
    répéter sur `N017` (`PX`), `N155` (`E0`), `N044` (`ED`), `N350` (`V`) pour
    couvrir le filtre `scoswamp.c:751-758` code par code.

**Hasard cadré** (seed posé dans `_state`, `$9D8C`)

15. `N005` (`CL 273 297`), CHANCE 9 → `Vous jetez les deux dés : R, contre une
    CHANCE de 9`, `cha` -1 **dans les deux cas**, page 273 si R ≤ 9 sinon 297.
16. `N024` (`CL 273 297 0 -2`) → sur la branche malchanceuse, END -2 en plus.
17. `N058` (`CE ENDURANCE 0 -1`) → la page **continue de se lire** après le jet
    (contrairement à `CL`), les choix restent affichés.
18. `N044` (`ED ENDURANCE -1`) → `Vous jetez : R` puis END -= R ; avec un seed
    qui met END à 0, on sort par `game_over` (`load_scene:1836`).
19. `N091` (`CS ENDURANCE 404 405`) → 2d6 contre END **sans** consommer de
    CHANCE (`cha` inchangé), branchement selon le jet.
20. `N135` (`ED OR +1`) → l'or monte de R ; pas de plafond (`rules.h:114-119`)
    mais jamais sous 0.
21. `N156` (cascade `DV 0 241` / `DV 5 193` / `DV 99 326`) → `last_loss`
    (`$9F63`) injecté à 0, 3 puis 12 mène à 241, 193, 326, et `dv_done`
    (`$9F64`) bloque la cascade à la première ligne qui correspond.

**Combat**

22. `N012` (`M 9 12 GEANT`, `MD 4`, `MS 6`, `CF 161`, `MV 061`) → bandeau
    `VOUS HAB h [####------] e/e0` à gauche, `GEANT HAB 9 [...] 12/12` à
    droite (`put_fighter`, `:1200-1213`) ; `ESPACE` engage.
23. Même page : chaque coup encaissé retire **4** points (et non 2 — `MD 4`),
    et la jauge perd des cases, arrondi vers le haut (`put_gauge`, `:1179`).
24. Même page : `MS 6` → le combat cesse à 6 points d'ENDURANCE du GÉANT et
    l'on part au 061 (`MV`).
25. Même page : `F` → `Vous fuyez : elle vous blesse au passage`, -2 END,
    proposition de Tenter la Chance, puis page 161 (`flee_target`, `$9F44`).
26. `N120` (trois lignes `M`) → file dans l'ordre ; `goto` avec `_seen`
    pré-rempli `(120, 1, 3)` → on reprend au **deuxième** adversaire à 3
    points (`monster_enter`, `rules.c:335-347`).
27. `N079` (`MB 360 128`) → la **première** blessure arrête le combat : 360 si
    le héros a touché, 128 sinon.
28. Combat perdu (END injecté à 2) → `Votre ENDURANCE est tombée à zéro` ;
    `[R]` remet `hero_ready=0`, `pending_scene=0` et **vide** `_visited` et
    `_seen` (`die_and_restart`, `:1769-1776`).

**Objets, amulettes, Pierres**

29. `N015` (`CI AI`, `CA 1 6 198`, `GU BJ 276`, `C`) → sans l'aimant le choix
    `CI` porte `-)` (`choice_tag`, `:504-507`) et la lettre affiche `Pierre
    absente.` ; avec l'aimant, la lettre apparaît. `N006` (`GU BA` + `CN BA`)
    → les deux branches selon la baie, `GU` la consommant.
30. `N226` (`CA 0 0 054`, `CA 1 2 007`, `CA 3 6 194`) → 0, 2 puis 4 amulettes
    activent chacun exactement un des trois choix.
31. `N400` (3 × `CU`) → `CU FEU` avec `stones[FEU]=1` décrémente à 0 après le
    saut ; avec 0, le choix est barré.
32. `N206` (`PC 6 NM`) → l'écran des Pierres ne liste que les neutres et les
    maléfiques (`choose_stones`, `:1471-1508`), le compteur descend de 6 à 0,
    et la même Pierre peut être prise plusieurs fois. `N408` (`TR`) → troc de
    3 possessions contre 3 Pierres neutres, plus la branche « rien à troquer ».

**Interface, sauvegardes, page déjà visitée**

33. `[I]` hors combat → `SAC A DOS -- <or> Pieces d'Or…` ligne 2, Pierres à
    gauche, objets colonne 40 ligne 4, amulettes ligne 13 ; `[I]`/`ESC`
    referme et `render_scene` restitue la page **à l'identique** (comparaison
    d'écran avant/après). Sac vide → `Aucune Pierre Magique.` En combat après
    le premier assaut, `I` n'est plus offert et une Pierre de caractéristique
    affiche ` interdite en plein combat` (`stone_usable`). `[H]` → `HELPFR`
    lignes 2-19 puis retour. `[Q]` → `Au revoir!` en 40 colonnes puis
    `exit(0)`.
34. `[S] 9` → `Partie sauvee.` ; `[L]` montre le **titre de la page** à
    l'emplacement 9 et non `-- vide --` (`slot_title`, `:257-269`). `[L] 9`
    sur la sauvegarde de `forge_save.py` → page et état voulus, effets
    d'entrée inhibés : **test de bout en bout de l'option (a)**. `[L] 0` sur
    un `PARTIE0` de 2 octets et `[L] 8` sur un checksum corrompu →
    `Emplacement vide ou fichier corrompu.` et la partie en cours survit
    (`:2006-2009`). Enfin `N350` (`V 331`) : bit 350 posé dans `_visited` →
    court-circuit immédiat vers 331 sans rien afficher (`:1817-1820`).

**Le scénario que la porte cachée existe pour rendre possible**

35. Balayage des **412 pages** : `goto(p)` pour chacune, puis vérifier
    qu'aucune ligne ne dépasse 79 colonnes, qu'il y a au moins un choix ou que
    la page figure parmi les 22 pages terminales, et qu'aucun `Erreur`
    (`report_open_error`, `:291-295`) ni `errno=` n'apparaît. Aucune partie
    jouée à la main ne donnera jamais cette couverture.

---

## 6. Risques et questions ouvertes

**1. Le relink déplace tout.** `_app` est à `$9E8E` *aujourd'hui* ; il bougera
au premier octet ajouté au code ou aux données. Le `.lbl` règle le problème à
condition d'être **régénéré dans la même commande que le `.BIN`** — un `.lbl`
périmé et un `.BIN` neuf, c'est un banc qui poke dans le tas. Le garde
`_restoring - _app == 215` n'attrape que les changements d'`AppState`, pas un
décalage global : ajouter la sonde `peek(_app+44, 2) in (b"FR", b"EN")` **et**
la vérification que `peek(_app+184, 2) == FF FF` (`pending_scene == -1`) avant
d'injecter.

**2. La marge de 6 767 octets n'est pas acquise.** `LOWBSS` n'a plus que
**83 octets** sous `$2000` et le segment `LC` est à 3 030/3 072 : la Language
Card est pleine, aucune porte cachée ne peut y aller ; en `CODE` elle mange la
marge principale. Argument de plus pour l'option (c) à coût nul. Noter aussi
que le `build.map` de l'arbre de travail ne passe `check-memory.sh` **qu'avec**
`--himem 0xBF00 --stack 0x0180` (les valeurs du `Makefile:56,63`) : au défaut
`0x9600` il déclare un débordement de 5 393 octets.

**3. Le cache de blocs rend l'option (a) coûteuse en temps.** Chaque état forgé
impose de tuer et relancer pom2 (~2 s de boot ProDOS + choix de langue).
Tenable sur 35 scénarios, pas sur le balayage des 412 pages — d'où la priorité
3 de §4.5. *Question ouverte* : le write-back est-il actif sur le `.hdv` du
banc ? Si oui, un `flush()` de pom2 peut **écraser** le `PARTIE9` que l'hôte
vient de patcher (`writeBack_`, et le comportement de `bootHdvImage`,
`src/MainWindow_Media.cpp:72`).

**4. Snapshot vs disque.** `/snapshot/load` restaure CPU + RAM + aux mais pas
le média (`MachineSnapshot.h:33-40`). Un unique snapshot « jeu démarré, langue
FR choisie », restauré avant chaque `goto(p)`, économise le boot pour le
scénario 35 — tant que le `.hdv` monté reste le même. *Question ouverte* :
l'état du ProDOS 8 résident survit-il ? Ses tampons `$0800-$0BFF` sont dans la
section `MEM`, donc a priori oui, mais à mesurer.

**5. Pas de headless : une fenêtre GLFW est obligatoire.** Sur macOS il n'y a
pas de Xvfb. Pas de CI sans session graphique tant que `--ai-control` n'est pas
ajouté à `pom2_headless`, et `POM2_AUTO_QUIT` (`src/main.cpp:851`) est le seul
moyen propre de faire mourir pom2 tout seul.

**6. Le décodage vidéo inverse est une hypothèse.** Le mapping de §1.2(c)
suppose ALTCHARSET allumé par le firmware 80 colonnes. Premier test à faire :
lire la ligne 0 après `roll_character` et vérifier que `HAB %u/%u` se
reconstitue. Sinon, lire `DisplayState` (section `MEX`,
`MachineSnapshot.cpp:57-63`) — ou implémenter la priorité 1 de §4.5 et laisser
pom2 décider, puisque `src/Apple2Display_Internal.h:38` sait déjà le faire.

**7. Déterminisme des dés.** Poker `_state` (`$9D8C`) suffit à rendre le LCG
reproductible (`dice.c:14-18`), mais `dice_seed_from_keypress` (`:34-54`)
resème au choix de langue : poker **après** ce choix, et re-poker avant chaque
jet dont on veut prédire le résultat. *Question ouverte* : combien de tirages
une page consomme-t-elle avant celui qui nous intéresse (l'ordre est `ED`, puis
`CS`, puis `CL`, puis le combat — `load_scene:1832-1884`) ? Le plus simple est
d'écrire un modèle Python du LCG et de le faire avancer en parallèle.

**8. `CP` n'est exercé par aucune page** (0 occurrence dans TEXTFR *et* TEXTEN,
`scoswamp.c:950`). Soit le code part, soit il faut une page hors corpus — et
aucune des quatre options ne sait charger une scène absente du disque.
*Question ouverte* : vaut-il un `TEXTFR/N999/` réservé au banc ?

**9. Sécurité.** `--ai-control` force le token vide (`MainWindow.cpp:828`) et
`tests/socket_compat_test.cpp:47-48` documente qu'un process local peut
usurper `127.0.0.1:6503`. Acceptable pour un banc local ; en CI partagée,
poser `ai_control_token` et le passer en en-tête.

**10. Le patch en place du `.hdv` dépend de numéros de bloc.** `PARTIE9` est au
bloc 5888 et son entrée au bloc 5878 offset 394 *dans l'image actuelle* ; toute
reconstruction du volume les déplace. Le script doit parcourir le catalogue
(25 lignes) au lieu de porter des constantes — sinon il écrira 276 octets au
milieu d'une image RLE, et le bug qui en sortira coûtera une soirée.

---

## 7. État au 2026-09-04 — le banc existe

Ce qui précède était une étude. Elle est maintenant réalisée : le banc vit
dans **`SCOSWAMP.MORE/TOOLS/playtest.py`** (≈ 1 100 lignes, bibliothèque
standard seule), et se lance par

```sh
make -C SCOSWAMP/SRC playtest
```

qui reconstruit l'image disque puis rejoue le jeu. **23 scénarios, 207
assertions, environ 2 min 30** sur un Apple //e émulé à 12×. Une fenêtre POM2
s'ouvre et se ferme toute seule pour chaque scénario.

### 7.1 Ce qui a été retenu de l'étude

L'option **(c)**, l'injection mémoire, telle que décrite au § 4.1 et § 4.3 :
`pending_scene`, la Feuille d'Aventure, `hero_ready`, `restoring`, les deux
mémoires et la graine des dés, puis une touche inerte. **Zéro octet ajouté au
binaire livré.** L'option **(a2)**, la sauvegarde forgée, sert les quatre
scénarios qui testent la sauvegarde elle-même et les trois fins.

Trois corrections par rapport à l'étude, toutes trouvées en le faisant marcher :

1. **Les adresses ne viennent pas seulement du `.lbl`.** `ld65 -Ln` (ajouté
   aux `LDFLAGS`, cf. § 4.2) n'écrit que les symboles **globaux** : `_app` y
   est, mais `restoring`, `state`, `visited`, `seen` sont des `static` C, et
   `mb_slot`, `playing`, `cur_lo` des labels locaux de `music.s`. La classe
   `Symbols` les retrouve en croisant trois sources — les adresses de segment
   et les offsets par module de `build.map`, la suite ordonnée des labels et
   de leurs `.res` dans les `.s`, et le `.lbl` comme **contre-épreuve** : si
   les deux méthodes divergent d'un octet, le banc refuse de démarrer. Les
   deux invariants de l'étude tiennent toujours (`_restoring - _app` — 238
   aujourd'hui, `AppState` ayant gagné `foe_img`, `music_name` et
   `music_over` — et `_visited - _seen == 160`), plus la sonde `app.language
   ∈ {FR, EN}` avant toute écriture.

2. **La stabilité d'écran demande une fenêtre généreuse.** Deux relevés
   identiques à 50 ms (§ 5.1) ne suffisent pas : une page de combat écrit son
   texte, **lit son image RLE au disque — 160 ms d'écran figé** — puis peint
   le bandeau des combattants. Le banc rendait la main pendant la lecture et
   jurait que le bandeau n'existait pas. Six relevés, soit 300 ms de silence.

3. **Une touche à la fois.** La file de POM2 est auto-cadencée et **garde ce
   qui n'a pas été lu** (§ 1.2 b). Une rafale envoyée pendant que le jeu était
   bloqué dans un `cgetc()` interne se déversait ensuite d'un coup et faisait
   traverser le Marais au hasard. `goto()` frappe donc **une seule touche par
   tentative**, et parcourt un alphabet d'échappement : `Z` (inerte dans la
   boucle principale), `ESPACE` (jets, assauts, « continuer »), `A` (le choix
   des Pierres), `ESC` (sac, aide, sauvegardes), `R` (**la seule sortie de
   l'écran de mort**), puis dix `ESPACE` de plus pour mener un combat à son
   terme — en couchant au passage les adversaires (`end = 0`), sans quoi la
   file de trois du 120 n'en finissait pas.

Un piège de plus, qui n'est pas dans le jeu : **le lecteur JSON de POM2 ne
connaît pas les échappements `\uXXXX`** (`AiControlServer.cpp:220-244`, il
prend la lettre qui suit une contre-oblique telle quelle). Un
`json.dumps("\x1b")` lui fait taper « u001b » — cinq touches, dont un `b` qui
prend le choix B de la page en cours. `Pom2.raw()` bâtit donc le corps de la
requête à la main, octet brut compris.

### 7.2 Les scénarios

| Famille | Scénarios |
| --- | --- |
| Prologue et missions | `demarrage`, `gayolard`, `pompatarte`, `stratagus` |
| Combat et mort | `combat`, `premier_sang`, `mort` |
| Effets d'entrée | `benediction`, `graines`, `baie_anneau`, `revisite` |
| Hasard cadré | `hasard` (ED, CS, CL, DV) |
| Sauvegardes | `sauvegardes`, `forge` |
| Interface | `interface`, `video`, `anglais` |
| Les trois fins | `fin_175`, `fin_158`, `fin_358` |
| Musique | `musique` |
| Couverture | `images`, `balayage` |

`make playtest PLAYTEST=--list` les liste ;
`PLAYTEST="--only combat --keep"` en joue un seul et **laisse l'émulateur
ouvert** pour regarder ; `PLAYTEST="--port 6530"` change de port. Le défaut
est **6520** : 6503-6506 et 6510 sont pris ailleurs.

### 7.3 Ce que le banc a trouvé, et ce qu'il garantit

Un balayage des **412 pages** (hors banc, ≈ 5 min) : aucune page inatteignable,
aucun message d'erreur, aucune ligne hors des 80 colonnes, toutes portent leur
titre. Le corpus est sain.

Le banc échoue sur **une** assertion, et c'est son travail : **les pages 407 à
411 n'ont pas d'illustration** alors que les 407 autres en ont une. Détail,
reproduction et diagnostic dans `DOCS/rapport-playtest.md`.

### 7.4 Ce qu'il faudrait encore à POM2

Les priorités du § 4.5 restent valables, dans le même ordre. Deux ont gagné du
poids à l'usage : `paste_pending` dans `/status` (priorité 2) supprimerait les
300 ms d'attente de stabilité, soit **la moitié du temps du banc** ; et
`--ai-control` dans `pom2_headless` (priorité 4) reste la condition d'une CI.
`GET /screen.txt` (priorité 1) ferait gagner 40 lignes de décodage — le
décodage inverse/ALTCHARSET du § 1.2 (c) s'est révélé **exact**, la barre de
titre se relit sans une faute.
