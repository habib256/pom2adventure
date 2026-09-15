# Les impasses de contenu, tranchees livre en main

Branche : `feat/scoswamp-contenu`, fusionnee avec `feat/scoswamp-memoire` qui
en est la vraie base. Apport net de ce lot au-dessus de la base : **31
fichiers, 88 insertions, 33 suppressions**, tous dans `SCOSWAMP/TEXTFR` et
`SCOSWAMP/TEXTEN`. Aucune ligne de code, aucun octet du catalogue d'objets.

L'arbitre est le livre : `SCOSWAMP.MORE/Defis Fantastiques 08 - Le Marais aux
Scorpions.pdf`, dont le texte s'extrait proprement (400 paragraphes, aucun
trou). Chaque decision ci-dessous cite le paragraphe qui la fonde.

## Ce que la fusion a coute

Le worktree partait de `main`, trente commits derriere `feat/scoswamp-memoire`.
La fusion a leve **50 conflits**, tous dans le corpus. Ils ont ete resolus en
prenant la base sans discuter (`git checkout feat/scoswamp-memoire --
SCOSWAMP/TEXTFR SCOSWAMP/TEXTEN`), puis en reposant a la main les seuls apports
qui restaient propres a ce lot. Cette methode etait la bonne : la base avait
reindente tout le corpus (trois espaces par paragraphe), retire les numeros de
clairiere de la prose, corrige 255 coquilles et pose ~176 lignes `MU`. Un
rapiecage hunk par hunk aurait melange les deux mises en forme.

**Six trouvailles du premier passage etaient deja traitees par la base, et ont
ete jetees** :

| trouvaille | ce que la base en a fait |
| --- | --- |
| douze lignes `V` manquantes | posees, et **mieux** : la ligne porte desormais la liste des pages de la clairiere (`V 331 202 025 112`), et le moteur teste la page courante, la cible, puis chaque page citee |
| `CL 213 267` au 147 | corrige en `CL 213 106` |
| `CU FEU 336` / `CU FLETRISSURE 336` au 400 | corriges en 188 et 380 |
| `CU GLACE 126` manquant au 145 | pose |
| `C 129` manquant au 330 | pose |
| page anglaise 382 tronquee | restauree |

**Quatre accords fautifs** que j'avais corriges (« plusieurs annes », « est
termine », « Pierres Magiques inutilises ») faisaient partie des 255 coquilles
de la base : jetes eux aussi.

Ce que la base n'avait **pas** vu, et qui fait le present lot : les six points
ci-dessous.

---

## 1. L'Amulette d'Oiseau exigee au 350

**Ce que dit le livre.** Le paragraphe 350 demande « Avez-vous une Amulette
d'Argent en forme d'oiseau ? Rendez-vous au 25 ». La vraie amulette est au cou
de la Maitresse des Oiseaux (288), et aucune des quatre approches ne la donne :

| voie | § | issue |
| --- | --- | --- |
| l'attaquer | 391 | les oiseaux l'emportent, -2 CHANCE, retour au 217 |
| Pierre d'Amitie | 111 | « Vous avez sottement gache votre Pierre », renvoi au 184 |
| Pierre de Terreur | 201 | les oiseaux la protegent, elle disparait, retour au 217 |
| Pierre de Malediction | 260 | mort du heros |
| lui parler | 184 | elle **forge une fausse amulette** |

La vraie n'est donc **jamais** obtenable. Le livre le dit au 184 : « Je vais
fabriquer une fausse Amulette en forme d'oiseau. **Quiconque la verra pensera
qu'elle est authentique.** » L'Aigle du 350 est quelqu'un qui la verra.

**Avant / apres** (`N350.TXT`, FR et EN) :

    - CI OISEAU 025 Une Amulette d'Argent en forme d'oiseau
    + CI FAUX 025 Une Amulette d'Argent en forme d'oiseau

Le libelle ne bouge pas -- pour l'Aigle comme pour Stratagus, la fausse *est*
l'amulette. Remplacee plutot que doublee : `render_choices` affiche aussi les
choix indisponibles, marques `-`, et deux lignes identiques dont l'une morte a
jamais auraient encombre l'ecran a chaque passage. `AMULET_OISEAU` reste dans
l'enumeration : le bit sert au comptage (`GA`, `CA`), et le livre veut que
Stratagus soit dupe et paie ses 500 Pieces d'Or.

## 2. Le drapeau `.T`, pose et jamais relu

Deux paragraphes interrogent la decouverte du buisson : le **36** (« Si vous
avez deja decouvert le buisson d'Antherique, rendez-vous au 283, sinon au
396 ») et le **76** (« ... au 166. Sinon, au 333 »). Le portage laissait ces
deux pages en choix libres, et le `G .T` du 389 ne servait a rien.

**Ou poser le drapeau.** Le 389 n'est atteint que par 232, lui-meme atteint par
247 -- et c'est au **247** que le livre fait decouvrir le buisson (« un buisson
de forme inhabituelle... En haut, une grosse baie violette »). Le 232 bifurque
ensuite selon le sorcier servi : un heros au service de Pompatarte a vu le
buisson sans jamais passer par le 389. Le drapeau appartient au 247.

| page | avant | apres |
| --- | --- | --- |
| 247 | (rien) | `G .T` |
| 389 | `G .T` | inchange (descendant strict du 247) |
| 036 | `C 283` / `C 396` | `CI .T 283` / `CN .T 396` |
| 076 | `C 166` / `C 333` | `CI .T 166` / `CN .T 333` |

C'est la forme que le corpus emploie deja au 092 (`CI LOUP 344` / `CN LOUP
068`).

## 3. Les trois pages ou l'anglais en disait plus

| page | le livre | verdict | correction |
| --- | --- | --- | --- |
| 124 | « C'est un combat a mort et il n'est pas question d'essayer de prendre la fuite. » | l'anglais avait raison | phrase rendue au FR ; aucune ligne `CF` des deux cotes, la mecanique etait juste |
| 126 | « C'est le seul effet que vous obteniez. » | l'anglais avait raison | phrase rendue au FR |
| 140 | « il s'agit la d'une **Epee Magique qui donne 2 points d'HABILETE supplementaire** a celui qui s'en sert au combat » | l'anglais avait raison, **et les deux langues avaient tort sur la mecanique** | phrase rendue au FR, `G EP` et `E BONUS +2` poses **dans les deux langues** |

Le 140 etait le vrai trou. La page 340 -- l'autre mort de Stratagus, celle du
duel final -- portait bien `G EP` + `E BONUS +2` ; la 140, celle du Stratagus
9/10 du paragraphe 225, ne donnait rien. Le heros ramassait une epee que le
moteur ne lui mettait pas dans les mains.

## 4. Les sept fins vivantes non victorieuses

La liste de l'enonce est exacte : **049, 052, 100, 141, 298, 327, 349**. Le
recensement complet des pages sans issue donne 21 pages, dont 11 morts (003,
030, 098, 260, 297, 313, 332, 361, 372, 375, 401) et 3 victoires (158, 175,
358).

Chacune des sept recoit la derniere ligne que le 175 et le 260 portaient deja,
en paragraphe indente comme au 175 :

    FIN DE L'AVENTURE.        /        END OF ADVENTURE.

Et la musique qui convient. Aucune des sept n'appartient a une clairiere de
`carte.json` : le theme de zone ne les contraint pas, et `MU -` comme
`MU +...` ne comptent pas dans le jeu de themes verifie par le validateur.

| page | musique | pourquoi |
| --- | --- | --- |
| 049 | `MU +MORT.MB` | l'Anneau vendu, l'aventure finie avant d'avoir commence |
| 052 | `MU +MORT.MB` | revenu sans la baie : la quete a echoue |
| 100 | `MU +MORT.MB` | mission manquee, le heros regagne l'auberge |
| 141 | `MU -` | le repos, les blessures guéries : pas un echec, le silence |
| 298 | `MU -` (etait `MU TOUR.MB`) | vivant, le monde debarrasse de Stratagus : fin en demi-teinte |
| 327 | `MU +MORT.MB` (etait `MU TOUR.MB`) | de longues annees dans les geoles |
| 349 | `MU -` (etait `MU TOUR.MB`) | echappe sain et sauf |

Jamais `VICTOIRE.MB`, reserve aux 158 et 175. Le theme de la tour cede la
place sur les trois pages qui le portaient : il accompagnait une fin
d'aventure comme s'il restait un couloir a parcourir.

**Un mot d'excuse.** Au premier passage, sur la mauvaise base, j'ai conclu que
la musique n'existait pas -- il n'y avait alors ni `SCOSWAMP/MUSIC`, ni
`music.s`, ni `MU` dans `DIRECTIVE`. C'etait vrai de `main` et faux de la vraie
base. Les lignes `MU` ci-dessus sont posees sur la base fusionnee, ou le
validateur les controle (forme, existence de `MUSIC/<NOM>.BIN`, unicite du
theme par clairiere).

## 5. Relecture ciblee : objets, Pierres et amulettes de la prose

`reflow_txt.py --derive` ne signale rien. Le balayage par grep sur les libelles
du catalogue et les six amulettes rend quinze pages, toutes verifiees :

- **descriptives, aucune directive attendue** : 053, 144, 209, 288, 305, 398
  (l'amulette pend au cou d'un PNJ), 184 (`G FAUX` deja present), 150 (la liste
  d'Alphonse ; l'echange se fait au 408 par `TR`, dont le masque couvre Chaine
  d'Or, Aimant d'Or, Bijou Violet et Corne de Licorne, plus les amulettes) ;
- **035 et 357** : le livre ne retire pas du sac l'Aimant d'Or maudit, le
  portage non plus. Fidele ;
- **117 et 292** : le Maitre des Jardins passe son Amulette a Fleur a votre cou
  puis « reprend son Amulette et s'en va ». Rien a donner. C'est au 251, quand
  on le tue, qu'on s'en empare -- et le `G FLEUR` y est ;
- **Anneau de Cuivre** : aucun `G ANNEAU` dans le corpus, et aucun n'est
  necessaire -- `character_roll` pose le bit de depart, conformement au
  prologue (la vieille femme de la route du Roi).

Rien a corriger : ce point-la etait sain.

## 6. Les pages synthetiques 402-411

Structure FR/EN identique pour les onze (401 compris), chacune rattachee a un
paragraphe :

| page | § | ce que le livre dit |
| --- | --- | --- |
| 401 | 315 | la trappe, branche Malchanceux |
| 402 | 373 | « vous parvenez a blesser le sorcier... vous oterez 2 points au total d'ENDURANCE de votre adversaire » -- d'ou `M 9 8` et non `M 9 10`, et `MV 140` comme au 225 |
| 403 | 257 | « Augmentez de 2 points votre total de CHANCE et rendez-vous au 153 » |
| 404 / 405 | 91 | le saut reussi / rate (-1 HABILETE), puis 398 / 105 / 208 |
| 406 | 377 | « Vous perdrez alors 3 points d'ENDURANCE... rendez-vous au 319 » |
| 407 | 128 | « donnez-lui un objet de votre choix » -- `PO` |
| 408 | 150 | l'echange chez Alphonse -- `TR` |
| 409 / 410 / 411 | 164 | la potion de la Maitresse des Oiseaux, puis 248 |

Rien a corriger.

---

## Deux verrous que la base n'avait pas vus

La nouvelle ligne `V` teste « la page courante, la cible, puis chaque page
citee, et le premier drapeau leve suffit ». Elle est plus juste que l'ancienne
-- et elle resserre un piege que l'ancienne posait deja : si la cible de la
revisite renvoie a la page qui porte le `V`, celui-ci se redeclenche, et le
joueur fait la navette sans jamais lire la page.

- **336 / 137.** Le 336 porte `V 137 153` ; le 137 disait « Revenir en arriere
  pour trouver une solution » vers 336. Le bassin de Vase devenait
  definitivement illisible. Le livre (137) dit « Retournez au 336 pour examiner
  la meilleure facon de vous tirer d'affaire » : le 137 propose desormais ces
  quatre facons directement (`C 085`, `C 257`, `C 171`, `C 400`), en plus de
  `C 153`. Sa prose etait par ailleurs amputee (« Si vous l'avez deja tuee : »
  suivi de rien) et a ete recousue sur le texte du livre.
- **209 / 168.** Le 209 porte `V 168 082 308 397` ; le 168 renvoyait a 209.
  Il renvoie desormais aux deux pages d'action que la liste du `V` cite
  elle-meme : `C 082` (reprendre le combat -- la memoire des monstres rend bien
  « le meme total d'ENDURANCE qu'au moment de votre fuite », promesse du livre)
  et `C 034` (magie), en plus de `C 330` (quitter).

Verification : aucune page portant un `V` ne se referme sur elle-meme, et
aucune page n'est orpheline, dans les deux langues.

---

## Laisse a l'arbitrage du proprietaire

1. **« FIN DE L'AVENTURE » : jusqu'ou ?** Elle figure sur les sept fins
   vivantes, plus 175 et 260 qui l'avaient deja. Restent sans marqueur les deux
   autres victoires (**158**, **358**) et dix des onze morts.
2. **Terminologie anglaise.** `TEXTEN` melange « Asphodel » (006, 036, 076,
   164, 175, 212) et « Antherique » (389, et `OBJEN.TXT` : « Antherique
   Berry »). Rien n'a ete change ici pour ne pas remuer la base.
3. **Le sorcier servi n'est pas un drapeau.** Le 232 (« Si vous vous etes mis
   au service de Gayolard ») et le 330 (« si vous y avez vu une creature »)
   restent des choix libres, faute d'un bit `.G` et d'une memoire des creatures
   apercues. Deux drapeaux caches suffiraient -- c'est `build_objects.py` et
   ses trois copies.
4. **Le silence des fins.** `MU -` coupe la musique ; reste a decider si une
   fin merite mieux qu'un silence, par exemple un theme court de cloture qui
   ne soit ni `MORT` ni `VICTOIRE`.

---

## Verifications, toutes sur la base fusionnee

    reflow_txt.py SCOSWAMP --apply    -> ecrits : 0 fichiers   problemes : 0
    reflow_txt.py SCOSWAMP            -> a reecrire : 0        problemes : 0
    reflow_txt.py SCOSWAMP --derive   -> problemes : 0
    make -C SCOSWAMP/SRC              -> OK : tient en memoire, marge de 495 octets.
    make -C SCOSWAMP/SRC hdv          -> SCOSWAMP: 1329 files, 7603 blocks
    test_rules                        -> regles : tout passe
    build_objects.py --root .         -> 12 bits, catalogue inchange

Et pour la couverture du corpus : aucune page orpheline, aucune cible
inexistante, aucun `V` referme sur lui-meme, dans les deux langues.
