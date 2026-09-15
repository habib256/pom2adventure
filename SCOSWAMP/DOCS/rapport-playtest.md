# La traversée automatisée — rapport

**Branche `feat/scoswamp-playtest`, 2026-09-04.**

Personne n'avait joué ce jeu de bout en bout. Les trois derniers bugs —
Pompatarte qui n'offrait aucune Pierre, les Graines d'Arbre-Épée qui
n'existaient pas au catalogue, les deux Loups combattus sous le portrait de
leur Maître — auraient tous été attrapés par un banc qui rejoue les missions.
Ce banc existe maintenant. Il s'appelle `SCOSWAMP.MORE/TOOLS/playtest.py`, il
se lance par `make -C SCOSWAMP/SRC playtest`, et il a trouvé un bug.

---

## 1. Ce qui est livré

| Fichier | Rôle |
| --- | --- |
| `SCOSWAMP.MORE/TOOLS/playtest.py` | le banc : client POM2, résolution d'adresses, 23 scénarios |
| `SCOSWAMP/SRC/Makefile` | `-Wl -Ln,build.lbl` dans les `LDFLAGS`, et la cible `playtest` |
| `SCOSWAMP/DOCS/AUTOMATISATION.md` | nouvelle section 7, « État au 2026-09-04 » |
| `.gitignore` | `*.lbl`, artefact de lien au même titre que `*.map` |

Rien d'autre n'a été touché : ni les textes, ni la musique, ni le code du jeu.

**Résultat du dernier passage complet :**

```
23 scénarios, 207 assertions passées, 1 en échec, 2 min 30
  images   les 412 pages ont toutes leur planche  [il en manque 5 : 407..411]
```

Le seul échec est un vrai bug du jeu, décrit au § 4. Conformément à la
consigne, il n'a **pas** été corrigé : le banc le montre, à quelqu'un de
décider.

---

## 2. Comment le banc entre dans le jeu

Aucune porte dérobée n'a été ajoutée au binaire livré. **Zéro octet.** Le banc
écrit directement dans la BSS du jeu par `POST /mem`, en profitant du fait que
la boucle principale relit `pending_scene` *avant* chaque `cgetc()` :

```
poser la graine des dés, la Feuille d'Aventure, hero_ready, restoring,
les mémoires de clairières et de monstres, puis pending_scene ;
frapper une touche inerte ; la boucle reprend et charge la page.
```

`restoring = 0` rejoue les effets d'entrée de la page (visite fraîche),
`restoring = 1` les inhibe (reprise de sauvegarde) : les deux moitiés du
filtre de `classify_line` sont donc couvertes, code par code.

Les adresses ne sont écrites nulle part à la main. `ld65 -Ln` — ajouté aux
`LDFLAGS` — produit `build.lbl` **dans la même commande que le `.BIN`**, mais
il n'y met que les symboles globaux. `restoring`, `state`, `visited`, `seen`
sont des `static` C, `mb_slot`, `playing`, `cur_lo` des labels locaux de
`music.s` : aucun n'y figure. La classe `Symbols` les reconstruit en croisant
les offsets par module de `build.map` avec la suite ordonnée des `.res` des
`.s`, et **vérifie le résultat contre le `.lbl`** pour les symboles qui, eux,
y sont. Une divergence d'un octet, et le banc refuse de démarrer.

Trois garde-fous supplémentaires, tous gratuits :

- `_restoring - _app == 238` : c'est la taille d'`AppState`. Elle a changé
  depuis l'étude (215 → 238 : `foe_img`, `music_name`, `music_over`). Si elle
  rebouge, la table d'offsets Python est périmée et le banc s'arrête.
- `_visited - _seen == 160` : `rules.c` n'a pas bougé.
- Sonde d'exécution : `app.language` doit valoir `FR` ou `EN` avant la
  première écriture.

Adresses mesurées au 2026-09-04 :
`_app $A897`, `_restoring $A985`, `_state $A773`, `_seen $AC2B`,
`_visited $ACCB`, `_music_buf $AD4A`, `mb_slot $BB4A`.

---

## 3. Les scénarios

23 scénarios, chacun sur un émulateur neuf et une **copie** de
`dist/SCOSWAMP.HDV` — l'original n'est jamais ouvert en écriture.

**(a) Le prologue et les trois employeurs.** `demarrage` va de l'écran de
langue à la création du personnage (les trois caractéristiques dans leurs
bornes, les totaux de départ égaux aux valeurs courantes) puis au village.
`gayolard`, `pompatarte` et `stratagus` mènent chacun jusqu'à la page 009,
l'entrée du Marais, **en vérifiant l'offre de Pierres dans le sac** : six
neutres ou bénéfiques chez Gayolard (`PC 6 NB`, aucune Malédiction proposée),
**cinq neutres chez Pompatarte** (`PC 5 N` — c'est l'assertion qui aurait
attrapé le bug de septembre), six sans le Bien chez Stratagus (`PC 6 NM`,
aucune Bénédiction proposée).

**(b) Le combat.** `combat` engage le Démon de la page 222 avec une graine
fixée et vérifie, coup après coup, que **chaque blessure encaissée coûte
exactement 2 points** et chaque coup porté 2 points à l'adversaire. `mort`
descend le héros à 2 d'ENDURANCE, encaisse l'écran de mort (« Votre ENDURANCE
est tombée à zéro », `[R] [L] [Q]`), et vérifie qu'après `[R]` le héros n'est
plus prêt et que les deux mémoires sont vidées. `premier_sang` couvre la
directive `MB` de la page 079 : la première blessure arrête le duel.

**(c) La page 155.** `benediction` injecte une CHANCE de 9 sur 9 et vérifie
que `E0 CHANCE +2` monte **la valeur et le plafond** — puis qu'à `restoring=1`
elle ne rejoue pas.

**(d) Les sauvegardes.** `sauvegardes` écrit dans l'emplacement 7, rouvre la
page de chargement, **y lit le titre de la page** (« 7) Le large rond-point »
et non « -- vide -- »), abîme volontairement le héros, recharge, et vérifie que
l'or, l'ENDURANCE, les Pierres et les objets reviennent ; puis qu'un
emplacement vide est refusé sans emporter la partie en cours. `forge` fait le
chemin inverse : une sauvegarde SCS3 fabriquée sur l'hôte, posée dans le
volume ProDOS par **parcours du catalogue** (les numéros de bloc bougent à
chaque reconstruction ; les porter en dur reviendrait un jour à écrire 276
octets au milieu d'une image RLE), rechargée par `[L] 9`.

**(e) L'interface.** `interface` ouvre et referme le sac — et **compare
l'empreinte de l'écran avant et après** pour prouver que la page est restituée
à l'identique —, fait de même pour l'aide, vérifie le message du sac vide, et
qu'une page terminale (175) n'offre aucune lettre mais bien `[R] [L] [Q]`.
`video` fait tourner les trois modes et vérifie que **la page texte survit au
HGR plein écran** (l'invariant de `memory_swap.c`). `anglais` rejoue le tout
en anglais : `TEXTEN`, `HELPEN`, et la barre en `SKL/STA/LCK`.

**(f) Un objet donné puis exigé.** `graines` prend les Graines à la page 022,
les voit nommées dans le sac, et montre qu'à la page 374 le sortilège de
Croissance est **barré** sans elles et **prenable** avec — puis consommé.
`baie_anneau` fait le pendant sur la Baie (page 006, `GU BA` contre `CN BA` :
le joueur voit toujours les deux réponses, une seule porte une lettre) et sur
l'Anneau vendu page 049.

**(g) La revisite.** `revisite` lit la ligne `V` de la page 350 dans le corpus
et vérifie les trois cas : première visite, retour par la même porte, et
**retour par une autre porte** — c'est-à-dire par l'une des pages citées après
la cible, la liste qui empêche une créature de ressusciter. Puis qu'à la
reprise d'une sauvegarde, `V` est inhibé.

**(h) Les trois fins.** `fin_175`, `fin_158`, `fin_358` partent chacune d'une
sauvegarde forgée juste avant la fin — chez Gayolard avec la Baie, chez
Pompatarte, à la porte de la tour avec trois Amulettes — et vont jusqu'au
texte terminal. Pour 358, le chemin complet est joué : `CA 3 6` est la seule
branche prenable, `GA 500` paie bien 500 pièces par Amulette et les retire du
sac.

**(i) La musique.** `musique` lit `mb_slot`, `playing` et le curseur de
lecture derrière `_music_buf`, plus les noms `music_cur`/`music_zone`.
Vérifie : la Mockingboard est trouvée (slot 4 chez le propriétaire, d'après
`~/Library/Application Support/POM2/state.cfg` — non modifié), un air joue et
son curseur avance, **il ne change pas entre deux pages de la même clairière**
(195 et 058, clairière 1, `MU RONDPOINT.MB`), il **change** en passant à
Courbensaule, et la zone mémorisée suit.

**Et la couverture.** `hasard` prouve le déterminisme des dés (même graine,
même jet) et couvre `ED`, `CS` (gratuit : aucun point de CHANCE dépensé), `CL`
(le point part dans les deux cas) et la cascade `DV` de la page 156, aux trois
seuils. `balayage` charge quarante pages choisies pour leurs directives rares.
`images` inventorie les illustrations.

---

## 4. Le bug trouvé

### Cinq pages sans illustration

**Où** : pages 407, 408, 409, 410 et 411.
**Reproduction** : lancer le jeu, atteindre l'une des cinq pages ; ou plus
simplement `make -C SCOSWAMP/SRC playtest PLAYTEST="--only images"`.

| Page | Titre | On y arrive depuis |
| --- | --- | --- |
| 407 | L'objet donné aux Brigands | 128 (`PO`) |
| 408 | Échange chez Alphonse | 150 (`TR`) |
| 409 | Potion d'HABILETÉ | 164 |
| 410 | Potion d'ENDURANCE | 164 |
| 411 | Potion de CHANCE | 164 |

**Attendu** : comme les 407 autres pages du corpus, chacune affiche son
illustration ; `app.has_image` vaut 1 après le chargement.
**Obtenu** : `SCOSWAMP/IMG/N400/` contient `N400` à `N406` (et `B402`), mais
pas `N407` à `N411`. `load_hgr_image_as` échoue silencieusement,
`app.has_image` reste à 0, et `[ESPACE]` ne montre rien.

Ce n'est pas une régression du moteur : c'est un trou dans les données. Les
douze pages-relais `N402`…`N411` ont été ajoutées par le portage ; la
campagne « chaque page a sa planche » en a illustré sept et manqué les cinq
dernières — exactement les cinq dont le numéro dépasse 406. Le correctif est
une exécution de plus de `SCOSWAMP.MORE/TOOLS/generate_images.sh` +
`convert_images.sh` sur ces cinq numéros, puis `make hdv`. **Non fait ici :
c'est du contenu, et le banc est là pour le signaler, pas pour le décider.**

---

## 5. Ce qui a été vérifié et qui va bien

**Le corpus entier passe.** Un balayage des **412 pages** — chacune chargée
avec un héros complet, tous les objets, toutes les Pierres, toutes les
Amulettes — a duré 291 secondes et n'a rien trouvé : **0 page inatteignable,
0 message d'erreur d'ouverture de fichier, 0 ligne hors des 80 colonnes, 0
page sans titre dans la barre.** Aucune partie jouée à la main ne donnera
jamais cette couverture. (Ce balayage n'est pas dans le banc courant — cinq
minutes, c'est trop pour un aller-retour de développement ; `balayage` en
rejoue quarante, choisies pour leurs directives.)

**Les trois bugs de septembre ne reviendront pas.** Chacun a maintenant son
assertion nommée : `pompatarte` sur les cinq Pierres, `graines` sur l'objet
donné puis exigé, et l'image de bataille d'une page de combat dans `images`.

**Le décodage vidéo inverse était juste.** La question ouverte n° 6 de
`SCOSWAMP/DOCS/AUTOMATISATION.md` est tranchée : le mapping en quatre branches
(`≥ $80` normal, `< $20` majuscules inverses, `< $40` ponctuation inverse,
sinon minuscules inverses) relit la Feuille d'Aventure sans une faute, dans
les trois modes vidéo.

---

## 6. Deux observations, qui ne sont pas des bugs

**L'illustration arrive après le jet.** Trente-trois pages affichent
`has_image = 0` tant que le joueur n'a pas répondu à leur invite. C'est
l'ordre de `load_scene` : le jet `ED`, le test `CS`, le jet `CL` et le choix
des Pierres `PC` passent **avant** le chargement de l'image, qui est
délibérément le dernier client ProDOS de la scène. Conséquence de jeu : sur
ces trente-trois pages, on lance les dés devant un écran de texte, et
l'illustration n'apparaît qu'ensuite. C'est peut-être voulu ; c'est en tout
cas visible, et ça mérite d'être su. (Pour le banc, c'était surtout un piège :
un `goto` qui rend la main pendant l'invite laisse le jeu dans un `cgetc()`
interne.)

**Une fenêtre POM2 vole le clavier.** Au tout premier essai, l'écran de langue
est passé tout seul en français sans qu'aucune touche ait été envoyée. Non
reproductible depuis, et `dice_seed_from_keypress` attend bien `kbhit()` : la
fenêtre GLFW venait de s'ouvrir et a probablement capté une frappe du
terminal. Ce n'est pas un défaut du jeu, mais c'est un rappel que le banc n'est
pas *headless* — voir la priorité 4 du § 4.5 (`--ai-control` dans
`pom2_headless`), qui reste la condition d'une intégration continue.

---

## 7. Ce que la fusion a coûté

Le worktree avait été ouvert sur `main`, en retard de quarante commits sur la
vraie base de travail. `git merge feat/scoswamp-memoire` dans
`feat/scoswamp-playtest` **n'a coûté aucun conflit** : 264 fichiers, deux
commits (`218fd3f` et `d4dd245`, les musiques remontées d'un cran avec
percussions). Mes modifications du `Makefile` (les `LDFLAGS`) et celles de la
branche (la section des musiques) ne se touchent pas.

Après fusion, `make all` puis `make hdv` : **les adresses n'ont pas bougé d'un
octet** (`_app $A897`, `AppState` 238 octets), l'empreinte reste à 31 618
octets sur 32 128 — 510 octets de marge — et les 23 scénarios repassent à
l'identique. Le seul vrai coût a été de refaire les dix musiques de zone et
les trente-cinq de clairière, plus l'image disque : environ trois minutes de
`make`.

---

## 8. Comment s'en servir

```sh
make -C SCOSWAMP/SRC playtest                              # tout, ~2 min 30
make -C SCOSWAMP/SRC playtest PLAYTEST=--list              # la liste
make -C SCOSWAMP/SRC playtest PLAYTEST="--only combat -v"  # un seul, détaillé
make -C SCOSWAMP/SRC playtest PLAYTEST="--only fin_358 --keep"
```

`--keep` laisse l'émulateur ouvert à la fin du dernier scénario, pour regarder
l'écran où le banc s'est arrêté. `--port` change le port `--ai-control` : le
défaut est **6520**, parce que 6503 à 6506 et 6510 sont pris ailleurs.
`--hdv`, `--pom2` et `--src` disent où sont l'image, l'émulateur et les
fichiers de lien.

Le banc sort en code 1 dès qu'une assertion échoue — aujourd'hui, celle des
cinq planches manquantes.
