# L'entrée dans le jeu — prologue de Bourbenville

Branche : `feat/scoswamp-prologue`, fusionnée avec `feat/scoswamp-memoire`
Date : 2026-09-04

Ce rapport couvre la mise en place de l'entrée dans SCOSWAMP : la présentation
du personnage à la création, et le village de Bourbenville rendu parcourable
avant qu'on choisisse un employeur.

> **Note sur la base.** Le premier jet a été écrit sur un worktree issu de
> `main`, où ni la musique, ni `carte.json`, ni l'indentation de trois espaces
> n'existaient : le rapport concluait à tort à l'absence d'une couche
> musicale. La vraie base est `feat/scoswamp-memoire`, fusionnée depuis. Tout
> ce qui suit décrit l'état **après** fusion.

---

## 1. Ce qui a été livré

### 1.1 La présentation du personnage — par une page, pas par le catalogue

`roll_character` (SCOSWAMP/SRC/scoswamp.c) affichait un titre, trois lignes de
chiffres, l'équipement, la règle du plafond, puis « [ESPACE] entrer dans le
Marais ». Le joueur entrait dans le Marais sans savoir ce qu'est l'Anneau de
Cuivre — qu'il porte pourtant au doigt depuis l'introduction du livre — ni
pourquoi trois hommes l'attendent au village.

Deux lignes de contexte ont d'abord été ajoutées **au catalogue de messages**.
Elles ne tiennent pas : le catalogue vit en `LOWBSS` ($1000-$1FFF, plafonné par
HGR page 1 en $2000), il y restait 43 octets, et les deux lignes en coûtaient
149. Le lieur l'a dit sans ambiguïté :

```
ld65: Warning: scoswamp.cfg(33): Segment 'LOWBSS' overflows memory area 'LOWRAM' by 85 bytes
```

**La présentation est donc passée par une page synthétique, la 419** — le
repli prévu, et le meilleur des deux : une page ne coûte pas un octet de RAM,
en dit quatre fois plus, et se traduit sans relier le binaire.

Le chemin d'entrée devient :

```
page 000 (accueil, MU ACCUEIL.MB)
   └─ A) Creer mon personnage  ──► roll_character() : la Feuille d'Aventure
                                      └─ [ESPACE] ──► page 419 (MU ACCUEIL.MB)
                                                        └─ A) ──► page 001
```

`roll_character` joue au **premier choix pris**, quel qu'en soit le but : il a
suffi de faire pointer le choix de la page 000 sur la 419 au lieu de la 001.
Aucune ligne de code n'a été ajoutée pour cela — un numéro de page a changé
dans deux fichiers texte.

La page 419 (« Qui vous etes » / « Who You Are ») dit l'aventurier, la vieille
femme relevée sur la route du Roi, l'anneau de cuivre qui s'ajuste, ses deux
pouvoirs — le nord et la chaleur devant le Mal — et les trois hommes qui
attendent à Bourbenville.

**Le catalogue rend 25 octets plutôt que d'en prendre.** `M_CHANCEUX2` et
`M_MALCHANCEUX2` portaient mot pour mot le texte de `M_CHANCEUX` et
`M_MALCHANCEUX` ; les deux doublons sont supprimés et les deux points d'appel
utilisent les originaux. `roll_character` est identique à la version de
`feat/scoswamp-memoire`, au commentaire près qui explique pourquoi le texte
n'est pas là.

### 1.2 Le prologue jouable — pages 412 à 418

Sept pages, en français et en anglais, un fichier par page dans
`TEXTFR/N400/` et `TEXTEN/N400/` :

| Page | Titre | Rôle |
| --- | --- | --- |
| 412 | La place de Bourbenville | le carrefour, description longue, porte `V 413` |
| 413 | Bourbenville | la même place en deux lignes, à la deuxième visite |
| 414 | La salle de la taverne | les clients, le colosse aux deux loups, Grognard dans son coin |
| 415 | La boutique du vieil homme | il dit où habitent Gayolard et Pompatarte, et se tait sur la tour |
| 416 | Le bout du village | Gayolard à son tour de potier, la maison de Pompatarte, la tour de Stratagus au nord |
| 417 | L'Anneau de Cuivre | les deux pouvoirs de l'Anneau, d'après l'introduction |
| 418 | Ce qu'on dit des trois hommes | les trois missions, telles que le village les raconte |

**Le graphe.** Un seul point d'entrée : un choix ajouté à la page 240, `C 412
Faire un tour au village avant de choisir` (`C 412 Take a turn around the
village before choosing`). C'est l'endroit naturel — Grognard vient de dire
qu'il y a trois hommes dans ce village. Toutes les sorties du prologue
ramènent à la place (412) ; la place ramène au 240, où les trois offres
s'ouvrent (240 → 205 → 335 / 255 / 027). Aucune page existante ne change de
sens : hors du prologue, les seules retouches sont cette ligne de choix et le
numéro de but du choix de la page 000.

**La directive `V`.** La place porte `V 413`. La deuxième fois qu'on y revient
— et on y revient jusqu'à cinq fois — le moteur court-circuite la longue
description et sert la courte, avec la même liste de directions. C'est
l'usage que le livre fait de « Si vous y êtes déjà venu, rendez-vous au… »,
vérifié dans l'émulateur (§ 5).

**`SCENE_MEMORY_SIZE` passe de 52 à 53 octets** (rules.h, rules.c). À 52
octets la mémoire des clairières s'arrêtait au paragraphe 415 : les pages 416
à 419 n'auraient jamais été enregistrées, et toute ligne `V` posée au-delà
aurait échoué **en silence**. `SCOSWAMP.MORE/TOOLS/forge_save.py` suit
(`SCENE_MEM = 53`, `SAVE_SIZE` 276 → 277) : il fabrique une sauvegarde SCS3
octet par octet, et un décalage d'un octet y aurait faussé la mémoire des
monstres et la somme de contrôle. Les dix emplacements de `SCOSWAMP/SAVE/`
sont vides, aucune partie réelle n'est invalidée.

---

## 2. La musique

Les huit pages neuves portent une ligne `MU`, comme le reste du corpus :

- **412 à 418 : `MU VILLAGE.MB`.** Le village est un lieu, il a un thème, et
  les pages 001, 095 et 240 le portaient déjà. Entrer dans le prologue depuis
  le 240 et en ressortir ne change donc pas la musique : c'est le même thème
  d'un bout à l'autre du séjour à Bourbenville.
- **419 : `MU ACCUEIL.MB`.** La page hérite du thème de la page 000 au lieu
  d'en changer. C'est la réponse au « ACCUEIL.MB coupe trop tôt » : le thème
  d'accueil couvre maintenant l'accueil, la création du personnage et la
  présentation, et ne cède au thème du village qu'à la page 001, quand le
  voyage commence pour de bon. Le fondu croisé étant automatique, il n'y a
  rien d'autre à écrire.

`reflow_txt.py` vérifie les deux choses qui pouvaient déraper : que le fichier
`SCOSWAMP/MUSIC/<NOM>.MB.BIN` existe, et qu'une clairière de `carte.json` ne
porte pas deux thèmes de zone. Les pages du village ne sont pas des clairières
du Marais — `carte.json` ne décrit que les 35 clairières, `depart_prologue`
valant 009 — donc aucun arbitrage à y ajouter.

---

## 3. Fidélité au livre — et trois écarts assumés

Tous les faits du prologue sortent du livre, et d'aucune autre source :

- **L'Anneau de Cuivre** (pages 417 et 419) : introduction « La Sorcière et
  l'Anneau ». L'anneau montre le nord et empêche de perdre son chemin ; il
  **se réchauffe en présence d'un être malfaisant, même si celui-ci fait de
  grandes démonstrations d'amitié** ; il est resté **froid** une semaine
  entière chez des brigands « rudes et brutaux » mais honnêtes à leur manière,
  et a **prévenu** devant des grottes où l'on pratiquait la magie noire. La
  formule « chaud devant le Mal, froid devant le Bien » est donc **exacte**.
- **La taverne et le colosse aux deux loups** (page 414) : paragraphe 1.
- **Le vieil homme appuyé contre la vitrine de sa boutique** (page 415) et
  **la petite maison de Gayolard en bordure du village, avec son jardin et sa
  poterie** (page 416) : paragraphe 335.
- **La grande maison de Pompatarte au bord du marché** (pages 412, 416) :
  paragraphe 27.
- **La tour de Stratagus près du marais, cernée de statues grimaçantes** (page
  416) : paragraphe 255.
- **Les trois missions** (page 418) : la baie d'Anthérique (371), la carte
  jusqu'à Courbensaule (173), les Amulettes d'argent des sorciers du Marais
  (206). Le jugement de Grognard est celui du 205.

Aucune règle nouvelle, aucun objet nouveau, aucune Pierre distribuée : les
huit pages ne portent **que** des lignes `T`, `V`, `MU` et `C`. Elles ne
touchent ni à l'ENDURANCE, ni à la CHANCE, ni au sac.

### Trois écarts par rapport à la commande

1. **« La Lance Tordue » n'est pas à Bourbenville.** Le livre la situe à
   **Courbensaule**, la ville au nord du Marais : c'est l'une de ses trois
   auberges (paragraphes 78, 214, 280, 395), on y dort au retour, pas au
   départ. La taverne du paragraphe 1, à Bourbenville, n'a pas de nom dans le
   livre. La page 414 la laisse donc sans nom.
2. **La boutique d'Alphonse Mâchefer n'est pas à Bourbenville non plus.**
   Paragraphe 150 : « la rue qui mène à la sortie de la ville » — de
   Courbensaule — et c'est une scène de **retour**, où l'on troque contre des
   Pierres les objets rapportés du Marais. La page 415 met à sa place le vieil
   homme du paragraphe 335, qui est bien de Bourbenville et qui vend de la
   corde et des lanternes, rien de magique.
3. **Les trois missions sont données comme rumeur, pas comme contrat.** Le
   livre ne les révèle qu'en visitant chaque homme, et chacun y attache ses
   conditions (six Pierres bénéfiques ou neutres chez Gayolard, six maléfiques
   ou neutres et 500 Pièces d'Or par Amulette chez Stratagus, cinq Pierres
   neutres et la moitié des bénéfices chez Pompatarte). La page 418 dit ce que
   chacun **cherche** — c'est public, le 205 le dit — et laisse les termes
   exacts aux pages 371, 206 et 173.

Le nom anglais du village suit le corpus existant : **Marshville**, et
Courbensaule reste Courbensaule, comme dans TEXTEN/N150/N173.

---

## 4. Côté image

Les huit pages n'ont pas d'illustration, et **ce n'est pas un blocage** : une
page sans `.RLE.BIN` retombe sur le texte plein écran — vérifié dans
l'émulateur. Le précédent existe : les pages 407 à 411 ne sont ni illustrées ni
inscrites dans `SCOSWAMP.MORE/scene_manifest.jsonl` (qui s'arrête à 406).

`scene_manifest.jsonl` n'a donc **pas** été modifié : le pipeline ne l'exige
pas pour que le jeu tourne, et y écrire une entrée sans savoir produire la
planche donnerait un manifeste qui ment. Manquent aujourd'hui 13 planches sur
420 (`check-project.sh` : « Images : 407 / 420 scènes illustrées ») : les 407
à 411 d'un lot antérieur, et les 412 à 419 de celui-ci. Les décors utiles sont
tous décrits dans le livre : une place de bourgade en terre battue, une salle
de taverne, une devanture de boutique, un jardin de potier avec une tour noire
à l'horizon, un anneau de cuivre au doigt.

---

## 5. Tests

| Test | Résultat |
| --- | --- |
| `reflow_txt.py SCOSWAMP --apply` puis sans `--apply` | `a reecrire : 0 fichiers` / `problemes : 0` |
| `reflow_txt.py SCOSWAMP --derive` | `problemes : 0` (recoupement mécanique FR ↔ EN, existence des `.MB.BIN`, un seul thème par clairière) |
| `cd SCOSWAMP/SRC && make` | OK — marge principale **498 o**, LOWBSS **68 o** libres sous $2000 |
| `make hdv` | `SCOSWAMP: 1345 files, 7652 blocks` |
| `test_rules` | `regles : tout passe` |
| `./check-project.sh` | OK — 420 FR + 420 EN |
| émulateur, parcours FR | 000 → Feuille → 419 → 001 → 095 → 240 → 412 → 414 → 418 → 412(court) → 417 → 412 → 240 → 205 |

La marge principale passe de 499 à 498 octets (l'octet de `SCENE_MEMORY_SIZE`)
et **LOWBSS de 43 à 68 octets libres** : le lot rend plus de RAM basse qu'il
n'en prend, grâce aux deux doublons du catalogue.

Commande d'essai : `../pom2/build/POM2 --preset iie dist/SCOSWAMP.HDV
--ai-control=6512`, pilotage par `POST /keyboard`, lecture de l'écran 80
colonnes par `GET /mem` (colonnes paires en banque `aux`, impaires en `main`).

### Capture 1 — la Feuille d'Aventure, puis la page 419

```
                                                      7/7      16/16      12/12


FEUILLE D'AVENTURE

HABILETE   7   (1 de + 6)
ENDURANCE 16   (2 des + 12)
CHANCE    12   (1 de + 6)

Une epee, un justaucorps de cuir, un sac a dos, 20 Pieces d'Or.
Aucun de ces trois totaux ne pourra depasser sa valeur de depart.

[ESPACE] entrer dans le Marais
```

```
  ui vous etes   :       :                            7/7      16/16      12/12
   Vous etes un aventurier intrepide qu'aucun peril n'a jamais fait reculer,
et assez sage pour ne s'etre jamais hasarde dans le Marais aux Scorpions. Nul
n'a jamais pu en dresser la carte : ses sentiers egarent, le brouillard cache
le ciel, et les boussoles y perdent le nord.

   Puis le destin s'en est mele. Sur la route du Roi vous avez releve une
vieille femme, vous l'avez portee a l'ombre, et elle vous a donne un cercle de
cuivre sans gravure. Une heure plus tard, l'anneau s'etait ajuste a votre
doigt.

   Tant que vous le portez, vous savez ou est le nord et vous ne perdez jamais
votre chemin. Et il se rechauffe chaque fois que vous vous trouvez devant un
etre malfaisant, meme si celui-ci vous fait de grandes demonstrations
d'amitie. Chaud devant le Mal, froid devant le Bien.

   Voila de quoi entrer dans le Marais. Reste a savoir pourquoi : a
Bourbenville, la derniere bourgade avant les terres basses, trois hommes
cherchent un aventurier assez hardi pour s'y risquer.

A) Prendre la route du Marais
```

### Capture 2 — la place, première visite (page 412)

```
  a place de  ourbenville   :       :                 7/7      16/16      12/12

   Vous laissez Grognard a sa chope et poussez la porte de la taverne. Dehors,
Bourbenville s'etale au soleil : une bourgade de terre battue posee sur les
basses terres, la derniere avant le Marais. Des voyageurs y passent tous les
jours et personne ne se retourne sur votre heaume d'acier.

   Sur la place, un vieil homme somnole contre la vitrine de sa boutique. Plus
loin, le marche bruit de cris et de volailles ; une grande maison en occupe
tout un cote, volets clos. La rue se termine au bout du village, sur des
jardins. Et vers le nord, la ou la terre devient molle, une tour noire se
decoupe sur le ciel.

   Trois hommes de ce village cherchent un aventurier. Rien ne presse encore :
Grognard vous attend, et sa chope est pleine.

A) La salle de la taverne               B) La boutique du vieil homme
C) Le bout du village                   D) Regarder votre Anneau
E) Retourner a la table de Grognard
```

(La barre de titre est en vidéo inverse ; les majuscules initiales manquent
dans ces transcriptions parce que la lecture par `/mem` rend les codes de
vidéo inverse — artefact de la capture, pas de l'affichage.)

### Capture 3 — la place, deuxième visite (la ligne `V 413` a joué)

```
  ourbenville   :       :                             7/7      16/16      12/12

   Vous revenez sur la place. Le vieil homme n'a pas bouge de sa vitrine, le
marche crie toujours, et la tour noire est toujours la, au nord.

A) La salle de la taverne               B) La boutique du vieil homme
C) Le bout du village                   D) Regarder votre Anneau
E) Retourner a la table de Grognard
```

---

## 6. Ce qui reste

- **Les 13 planches manquantes** (407 à 419), § 4.
- **LOWBSS reste le goulot** : 68 octets sous $2000, et la zone ne peut pas
  grandir (HGR page 1 commence là). Toute paire de messages ajoutée devra
  rendre des octets ailleurs, ou passer par une page — c'est exactement ce que
  ce lot a fini par faire.
- **Un second point d'entrée.** Le prologue ne s'atteint que depuis le 240. Un
  joueur qui, à la page 095, refuse le conseil de Grognard (→ 122 → 296) ne
  verra jamais le village. C'était volontaire — n'ouvrir qu'une porte, et ne
  pas toucher au sens des pages existantes — mais un choix supplémentaire au
  122 serait cohérent.
