# Une musique par clairière — conception

**2026-09-03** · branche `feat/scoswamp-memoire` · dépôt
`/Users/gistair/src/pom2adventure`. **Document de conception : aucun fichier de
code ni de texte n'a été modifié.** Les propositions musicales, elles, sont
posées dans `SCOSWAMP.MORE/MUSIC/propositions/` (voir son `INDEX.md`).

Demande à laquelle ce document répond, mot pour mot :

> « une musique data driven certes mais pas qui recharge à chaque page. En fait
> chaque clairière (tu en fais un plan) devrait avoir une musique propre qui
> reste active uniquement dans les pages de cette clairière et ne recharge pas à
> chaque page de la même clairière. Seul le changement de clairière change la
> musique. »

---

## 1. Résumé et recommandation

Aujourd'hui, `load_scene()` coupe la musique **avant toute lecture disque**
(`SCOSWAMP/SRC/scoswamp.c:1858`), puis la recharge et la relance **après**
(`:1957`). Une page sans ligne `MU` est muette (`scoswamp.c:731-733`). Il n'y a
d'ailleurs qu'**une seule ligne `MU` dans tout le corpus** :
`SCOSWAMP/TEXTFR/N000/N000.TXT:19` (et son jumeau anglais), `MU COMEAGAIN.MB`.
Le mécanisme est donc entièrement disponible pour être redéfini.

**Ce qu'il faut changer tient en une phrase : le moteur doit se souvenir du nom
de ce qui joue.** Tout le reste en découle.

| Décision | Réponse | Coût |
| --- | --- | --- |
| **§2** Rattachement page → musique | Une ligne `MU` sur la **page d'arrivée** de chaque clairière ; **pas de `MU` = la musique courante continue** ; `MU -` = silence ; `MU +NOM.MB` = surcouche d'une page. Le moteur ne recharge que si le nom diffère de ce qui joue. | ~110 o `CODE`, 33 o `BSS` |
| **§3** Continuité entre pages | `music_pause()` / `music_resume()` autour des lectures, mais **appelés seulement autour du chargement d'image** ; le trou mesuré décidera. Aucun rechargement entre deux pages d'une même clairière. | ~75 o `CODE`, 1 o `BSS` |
| **§4** Combat / mort / victoire | Le combat est une **surcouche** d'une page, pas une zone. Deux demi-tampons de 1 280 o taillés dans le tampon actuel : aucun rechargement à l'entrée ni à la sortie du combat. La mort est câblée dans `die_and_restart()`, elle n'a pas de page. | ~55 o `CODE`, 2 o `BSS` |
| **§5** Plan des musiques | **11 fichiers** couvrant les 35 clairières et les écrans, tous du domaine public (Mutopia Project), déjà convertis dans `SCOSWAMP.MORE/MUSIC/propositions/`. | 7 490 o disque |
| **§6** Données et mémoire | `MUSIC_BUF_SIZE` reste à **2 560**, mais devient **2 × 1 280**. La RAM auxiliaire n'est **pas** nécessaire, et son chiffrage confirme qu'elle serait un mauvais marché. | net **+~240 o** sur 3 012 |

**Marge actuelle mesurée** (`cd SCOSWAMP/SRC && make check`, exécuté pour ce
document) :

```
  BSS           : $A31A - $B1BC
  Tas           : $B1BC - $BD80  (3012 o)
  Empreinte     : 29116 o sur 32128 o disponibles
  LOWBSS        : $1000 - $1FBD  (4030 o, reste 66 o sous $2000)
  OK : tient en mémoire, marge de 3012 octets.
```

Le plan complet consomme **~240 octets sur 3 012**. Si l'on renonce à la
surcouche de combat (§4, option 1), le tampon retombe à un seul demi de 1 280
octets et le bilan devient **−1 040 octets, c'est-à-dire une marge en hausse**.

---

## 2. Rattachement page → musique, sans rechargement

### 2.1 Les trois options, et pourquoi deux d'entre elles n'en font qu'une

| | Principe | Lignes à écrire | RAM moteur | Robustesse |
| --- | --- | --- | ---: | --- |
| **(a)** | Une ligne `MU` sur **chaque** page de la clairière, nom identique | **412 × 2** (FR + EN) = 824 | 16 o | Une faute de frappe sur une page → rechargement au milieu de la clairière |
| **(b)** | Table page → clairière → musique dans le futur fichier `MAP` | 0 dans le corpus, 447 o de données | **447 o + ~80 o** de lecture | Une page ajoutée hors `MAP` est muette et personne ne le voit |
| **(c)** | Une ligne `MU` sur les seules **pages d'arrivée** | **35 × 2 + ~25 × 2** = 120 | 16 o | Une arrivée oubliée → la musique précédente déborde |

Le point qui tranche : **dès que l'on adopte la règle « pas de `MU` = la musique
courante continue » — qui est littéralement la demande du propriétaire — les
options (a) et (c) deviennent le même moteur.** La différence n'est plus
technique, elle est éditoriale : (a) répète 412 fois une information, (c) la dit
une fois. Et une information répétée 412 fois dans deux langues est une
information qui divergera.

**(b) perd pour trois raisons chiffrées.**

1. **447 octets de `BSS` sur 3 012** — 412 pour la table plate `MAP_OF_PAGE[412]`
   prévue par `CARTOGRAPHIE.md:951-953`, 35 pour clairière → musique, plus la
   routine de lecture et une ouverture de fichier de plus au démarrage. Deux fois
   plus que **tout** le reste de ce document réuni.
2. **Deuxième source de vérité.** Le principe du projet est que le `.TXT` d'une
   page dit tout de cette page : ses choix, ses adversaires, ses effets, son
   image. Sortir la musique du `.TXT`, c'est demander à l'auteur d'un texte
   d'éditer un fichier binaire pour changer une ambiance.
3. **Elle ne sait pas exprimer les exceptions.** Le combat, la tour, la mort et
   les victoires ne sont pas des clairières : 32 + 14 + 11 + 2 pages éparpillées
   dans les 296 pages hors clairière (`CARTOGRAPHIE.md:929-930`). Une table par
   clairière ne les atteint pas ; il faudrait remettre des `MU` par-dessus.
   **(b) n'élimine donc pas (c), elle s'ajoute à elle.**

> Ce qui ne veut pas dire que `MAP_OF_PAGE` est inutile : elle est très utile —
> **au validateur** (§2.4), pas au moteur. Le fichier `MAP` reste à faire pour la
> cartographie ; il n'a simplement rien à voir avec la musique à l'exécution.

### 2.2 La grammaire retenue

Quatre formes, un seul caractère de syntaxe nouveau :

| Ligne | Sens | Où on l'écrit |
| --- | --- | --- |
| `MU MARAISUD.MB` | **thème de zone** : devient la musique courante *et* la musique de référence | la page d'arrivée d'une clairière, les entrées de zone |
| *(rien)* | la musique courante continue, sans aucune lecture disque | les 350+ autres pages |
| `MU +COMBAT.MB` | **surcouche** : remplace la musique courante pour cette page seule, sans effacer la référence | les 32 pages de combat, les 11 pages de mort |
| `MU -` | silence net | une page qui doit être muette |

Et une règle implicite qui rend la surcouche gratuite : **si une page n'a pas de
`MU` et que la musique courante n'est pas la musique de référence, on revient à
la référence.** Le combat se termine donc tout seul à la page suivante, sans que
le corpus ait à écrire quoi que ce soit.

### 2.3 Ce que cela change dans `scoswamp.c`

Deux champs de plus, en `BSS` :

```c
static char music_cur[16];    /* ce qui joue en ce moment          16 o */
static char music_zone[16];   /* le theme de la zone courante      16 o */
static unsigned char music_over;  /* la ligne MU etait une surcouche 1 o */
```

Dans `classify_line()` (`scoswamp.c:885-888`), la seule chose à ajouter est la
lecture du `+` avant le `strncpy` : un test, un incrément de pointeur, un octet
de drapeau.

Dans `load_scene()`, la fin de la fonction (`scoswamp.c:1957`) devient, en
pseudo-C :

```c
if (app.music_name[0] == '-') {             /* MU -  */
    music_stop();  music_cur[0] = music_zone[0] = '\0';
} else if (app.music_name[0] == '\0') {     /* rien : on retombe sur la zone */
    if (memcmp(music_cur, music_zone, 16) != 0) music_switch(music_zone);
    else music_resume();
} else if (memcmp(app.music_name, music_cur, 16) != 0) {
    music_switch(app.music_name);           /* seul cas qui lit le disque */
    if (!app.music_over) memcpy(music_zone, app.music_name, 16);
} else {
    music_resume();                          /* meme nom : rien a lire */
}
```

`music_switch()` = `music_stop(); if (music_load(n)) { music_play(); memcpy(music_cur, n, 16); }`.

**La ligne qui compte est la dernière branche** : deux pages de la même
clairière portent le même nom (ou aucun), `memcmp` rend zéro, et **il n'y a ni
`fopen`, ni `fread`, ni redémarrage du flux**. C'est exactement la demande.

Et la ligne 1858 — `music_stop();` en tête de `load_scene` — devient
`music_pause();` (§3).

**Coût.** 33 octets de `BSS` ; `memcmp` est déjà lié (`scoswamp.c:315` s'en
sert) ; la cascade compilée en cc65 vaut de l'ordre de **110 octets de `CODE`**.

### 2.4 Comment `reflow_txt.py` le vérifie

Le validateur connaît déjà la directive : `MU` est dans la regex `DIRECTIVE`
(`SCOSWAMP.MORE/TOOLS/reflow_txt.py:51`), mais **il ne vérifie rien de son
contenu**. Cinq contrôles à ajouter, du moins cher au plus utile :

1. **Forme.** `^MU (-|\+?[A-Z0-9]{1,12}\.MB)$`. Le nom est en majuscules, sans
   accent, et `<NOM>.MB` doit tenir en 15 caractères — limite ProDOS, et limite
   du champ `char music_name[16]` de `scoswamp.c:141`. Un nom plus long est
   tronqué **en silence** par le `strncpy` de `:887` : c'est le bogue le plus
   probable de toute cette fonctionnalité.
2. **Existence du fichier.** Le nom doit correspondre à un
   `SCOSWAMP/MUSIC/<NOM>.MB.BIN` (ou, pendant l'atelier, à un
   `SCOSWAMP.MORE/MUSIC/propositions/*/<NOM>.MB.BIN`). Le `music_load` du jeu
   vérifie la magie `MB1` (`scoswamp.c:315`) mais **échoue silencieusement** si
   le fichier manque : le validateur est le seul endroit où l'on peut le voir.
3. **Cohérence FR/EN.** `TEXTFR/Nxxx/Nyyy.TXT` et `TEXTEN/Nxxx/Nyyy.TXT` doivent
   porter **la même** ligne `MU`, ou aucune des deux. Deux langues qui ne jouent
   pas la même musique sur la même page est une divergence invisible à
   l'exécution.
4. **Une seule `MU` par page.** Le `strncpy` de `:887` écrase sans prévenir : la
   dernière gagne. Un avertissement suffit.
5. **Croisement avec `carte.json`.** C'est le contrôle qui donne son sens au
   plan :
   - toute clairière doit avoir **exactement une** page portant un `MU` de zone
     (un `MU` sans `+`) — sinon *« clairière muette »* ou *« clairière à deux
     musiques »* ;
   - aucune **autre** page de la même liste `pages` ne doit porter un `MU` de
     zone : ce serait un rechargement au milieu de la clairière, précisément ce
     qu'on veut éviter ;
   - toute page portant une ligne `M` (les 32 pages de combat,
     `CARTOGRAPHIE.md:597-599`) devrait porter `MU +COMBAT.MB` — avertissement,
     pas erreur.

Les trois pages que deux clairières se disputent (363, 394, 330 —
`CARTOGRAPHIE.md:810-820`) doivent être arbitrées **avant** ce contrôle, sinon il
criera à tort. L'arbitrage est déjà appliqué dans
`SCOSWAMP.MORE/MUSIC/propositions/INDEX.md § 2`.

---

## 3. Ne pas couper la musique entre deux pages de la même clairière

### 3.1 Pourquoi `music_stop()` est là aujourd'hui

Le commentaire de `scoswamp.c:1855-1857` le dit :

> *La musique ne joue que sur l'accueil : coupée avant toute lecture disque
> (ProDOS masque les IRQ pendant les E/S, et l'AY tiendrait la dernière note),
> relancée plus bas une fois la page 000 chargée.*

Le fond est établi par `SCOSWAMP/DOCS/MUSIQUE.md § 6.1` : **ProDOS 8 encadre chaque
descente vers un pilote d'un `PHP / SEI … PLP` et ne fait jamais de `CLI`**
(`POSNOPEN.S:373` pour toutes les E/S fichier, `XDOSMLI.S:150` pour
READ_BLOCK). Pendant ce masquage le T1 continue de compter, **IFR6 est un verrou
unique et non un compteur**, donc N expirations masquées s'effondrent en une
seule IRQ tardive : la musique **cale et repart avec du retard, elle
n'accélère pas**. Et pendant ce temps l'AY joue les registres laissés — donc
**une note tenue, pas un silence**.

### 3.2 Combien de temps dure le trou, sur un `.hdv`

Le pilote de disque dur de POM2 est une boucle `LDA $C0x0 / STA (buf),y`
(`pom2/src/ProDOSHardDiskCard.h:17-37`, cité par `MUSIQUE.md § 6.1`) : pas de
latence rotationnelle, pas de délai de pas, pas de 64 tentatives. À ~15 cycles
par octet, un bloc de 512 octets coûte **~7 700 cycles ≈ 7,5 ms**, plus le
surcoût MLI.

| Lecture | Blocs (données + répertoire) | Masquage cumulé | Ticks 50 Hz perdus |
| --- | ---: | ---: | ---: |
| Le fichier texte de la page (600-1 250 o) | ~6 | **~45 ms** | 1 à 2 |
| L'image RLE (~6 Ko), par tranches de 1 Ko | ~16, en 6 tranches | **~120 ms**, en tranches de ~20 ms | 0 à 1 par tranche |
| **La musique**, uniquement au changement de zone (550-1 060 o) | ~6 | **~45 ms** | 1 à 2 |

Deux conséquences, et la seconde est la plus importante.

- **Le trou n'est jamais un seul long silence** : c'est une succession de
  fenêtres de 15 à 45 ms, séparées par du décodage RLE pendant lequel les IRQ
  passent normalement (`MUSIQUE.md § 6.2` : *« une IRQ de 500 cycles y est
  invisible »*). Le pire artefact audible est donc **une note tenue de ~45 ms**,
  soit deux ticks.
- **Avec le §2, la musique n'est plus lue qu'au changement de clairière.** La
  troisième ligne du tableau disparaît pour trois pages sur quatre : les 116
  pages rattachées à un lieu se répartissent sur 35 clairières, soit **3,3 pages
  par clairière** (`CARTOGRAPHIE.md:928`), et les 296 pages hors clairière
  héritent. Le coût disque de la musique tombe à **une lecture toutes les trois
  ou quatre pages.**

### 3.3 Les trois mécaniques possibles

**(i) `music_pause()` / `music_resume()`.** `pause` ferme le mixeur (R7 = `$3F`),
met les trois amplitudes à zéro, désarme l'IER — mais **ne touche ni au curseur
de flux, ni à `delay`, ni à `vols`, ni au drapeau `playing`**. `resume` rouvre le
mixeur (R7 = `$38`), réécrit les trois amplitudes depuis `vols`, efface l'IFR
puis réarme l'IER. Le timer T1 reste en marche continue : rien à réarmer, et
l'effacement de l'IFR au réveil évite la volée d'IRQ en retard.

C'est exactement la parade d'époque : le lecteur de *Music Construction Set*
(1983) n'expose que deux entrées, `PAUSE` et `CONTINUE` (`MUSIQUE.md § 6.1`).

**(ii) Laisser jouer et accepter la note tenue.** Coût nul. Artefact : ~45 ms de
note tenue par fenêtre, et un décalage de tempo de 3 à 8 ticks par page.

**(iii) Tout précharger.** Onze musiques × 680 octets de moyenne = **7 490
octets** ; la marge est de 3 012. Impossible dans la fenêtre principale, et
`MUSIQUE.md § 3.3` a déjà écarté la RAM auxiliaire pour un objet de cette taille.
**Mais le §2 en réalise l'essentiel gratuitement** : la musique de la clairière
courante *est* déjà résidente, et il n'y a aucune lecture tant qu'on reste dedans.

### 3.4 Recommandation

**Implémenter (i), mais ne l'appeler qu'autour du chargement d'image, et
mesurer.** Le raisonnement :

- entre deux pages d'une même clairière, il n'y a **plus** de lecture de
  musique ; il reste le texte (~45 ms) et l'image (~120 ms en six tranches) ;
- 45 ms de note tenue est moins audible que 165 ms de silence **délibéré** ;
  couper franchement peut donc être *pire* que ne rien faire ;
- mais 165 ms de note tenue à cheval sur une cadence, ça s'entend. D'où le
  compromis : `music_pause()` avant `load_hgr_image_as()` et `music_resume()`
  juste après (`scoswamp.c:1955-1956`), en laissant la lecture de texte jouer.

Les deux entrées coûtent 75 octets et doivent exister de toute façon : ce sont
elles qui permettront d'arbitrer à l'oreille dans POM2 sans recompiler la
logique.

### 3.5 Les changements dans `music.s`, chiffrés

Le lecteur actuel (`SCOSWAMP/SRC/music.s`) a déjà tout ce qu'il faut : `set_via`,
`silence`, les curseurs `cur_lo`/`cur_hi`, `delay`, `vols`, et un `_music_stop`
qui fait précisément *pause + oubli*. Les deux entrées se taillent dedans.

```asm
.segment "BSS"
paused:         .res 1              ; +1 o

; ── void music_pause(void) ─────────────────────────  ~24 o
_music_pause:
        lda mb_slot
        beq @rts
        lda #1
        sta paused
        jsr set_via
        ldy #IER                    ; interdire T1 -- le compteur, lui, tourne
        lda #$40
        sta (via),y
        ldy #IFR
        lda #$7F
        sta (via),y
        jmp silence                 ; R7 = $3F, trois amplitudes a 0
@rts:   rts

; ── void music_resume(void) ────────────────────────  ~45 o
_music_resume:
        lda mb_slot
        beq @rts
        lda playing                 ; rien a reprendre si rien ne jouait
        beq @rts
        stz paused
        jsr set_via
        ldx #7                      ; tons A, B, C ouverts, bruit ferme
        lda #$38
        jsr ay_write
        ldx #8                      ; les trois amplitudes, depuis vols
        lda vols
        jsr ay_write
        inx
        lda vols+1
        jsr ay_write
        inx
        lda vols+2
        jsr ay_write
        ldy #IFR                    ; effacer AVANT de reautoriser :
        lda #$7F                    ; sinon la volee en retard part d'un coup
        sta (via),y
        ldy #IER
        lda #$C0
        sta (via),y
@rts:   rts
```

`music_irq` n'a **rien** à changer : l'IER étant désarmée, aucune interruption
n'arrive, et `playing` reste à un, donc le flux repart où il en était.

| Poste | Octets |
| --- | ---: |
| `_music_pause` | ~24 `CODE` |
| `_music_resume` | ~45 `CODE` |
| `paused` (utile seulement au débogage) | 1 `BSS` |
| Deux `.export`, deux prototypes dans `music.h` | 0 |
| **Total** | **~70 o** |

Côté C, deux lignes de plus dans `music.h`, un `music_pause()` à la place du
`music_stop()` de `scoswamp.c:1858`, et un `music_resume()` après le chargement
d'image.

---

## 4. Le combat, la mort, la victoire

### 4.1 Le combat

Les 32 pages qui portent une ligne `M` (`CARTOGRAPHIE.md:597-599`) sont pour la
plupart **dans** une clairière : la page 312 (SCORPION GÉANT) appartient à la
clairière `id` 32, la page 281 (TROIS ORQUES) à la clairière `id` 26. Trois
politiques :

| Politique | Lectures disque par combat | RAM | Verdict |
| --- | ---: | ---: | --- |
| **1. Garder la musique de la clairière** | 0 | 0 | Le moins cher, mais le combat est le sommet dramatique du livre-jeu : c'est le seul moment où le joueur *agit*. |
| **2. Un seul tampon, rechargement aller-retour** | **2** (entrée : 644 o ≈ 45 ms ; sortie : 550-1 060 o ≈ 45 ms) | 0 | Correct. Le trou d'entrée est masqué par l'écran d'annonce de l'adversaire, celui de sortie par « vous avez vaincu ». |
| **3. Deux demi-tampons** | **0** | 0 *(voir ci-dessous)* | ✅ **Retenue.** |

**La politique 3 est gratuite, et c'est le point important de cette section.**
`music.h:11` déclare `MUSIC_BUF_SIZE 2560`, et `music.s` réserve
`_music_buf: .res 2560`. Or la plus grosse pièce du plan §5 fait **1 058
octets**. Le tampon actuel contient donc **deux musiques**, et il suffit de le
couper en deux :

```
_music_buf + 0x000 … 0x4FF   demi-tampon 0 : le theme de zone
_music_buf + 0x500 … 0x9FF   demi-tampon 1 : la surcouche (combat, mort, victoire)
```

Ce qu'il faut modifier dans `music.s` : le lecteur lit trois octets d'en-tête à
adresse absolue dans sa poignée `@end` —

```asm
@end:   lda _music_buf+5             ; drapeau de boucle
        ...
        lda _music_buf+6
        clc
        adc #<_music_buf
```

— et `_music_play` charge `cur_lo`/`cur_hi` avec `_music_buf+8`. Il faut
introduire un `base` de deux octets en `BSS`, posé par une nouvelle entrée
`music_select(unsigned char half)`, et rendre ces quatre accès indirects. Coût :
**~30 octets de `CODE`, 2 octets de `BSS`**, et deux cycles de plus par
bouclage — c'est-à-dire une fois toutes les 30 à 60 secondes.

Le déclenchement est déjà écrit au §2.2 : la page de combat porte
`MU +COMBAT.MB`, le moteur charge dans le demi-tampon 1 et joue ; la page
suivante n'a pas de `MU`, `music_cur` diffère de `music_zone`, le moteur rebascule
sur le demi-tampon 0 **sans rien lire**. La musique de la clairière reprend là où
la surcouche l'avait laissée — le curseur du demi-tampon 0 n'a pas bougé.

> **Conséquence à ne pas oublier.** Avec la politique 3, la musique joue
> *pendant* le combat, donc pendant les bruitages de `sfx.s`, qui sont des
> boucles de délai cycle-comptées (`sfx.s:29-35`). `MUSIQUE.md § 3.4` a chiffré
> le conflit : une IRQ de 600 cycles au milieu d'un balayage le désaccorde
> audiblement. La parade — `php / sei … plp` autour de chacun des cinq
> `_sfx_*` — coûte **8 octets** et cesse d'être facultative.

### 4.2 La mort

`game_over()` (`scoswamp.c:1788-1815`) **n'est pas une page** : c'est un écran
texte 40 colonnes dessiné par le moteur, sans fichier `.TXT`, donc sans ligne
`MU` possible. La musique s'y pose en dur, dans `die_and_restart()`
(`scoswamp.c:1842`) :

```c
static void die_and_restart(void)
{
    music_switch_over("MORT.MB");    /* +~25 o */
    if (game_over()) return;
    ...
}
```

Les **onze pages de mort narrative** (003, 030, 098, 260, 297, 313, 332, 361,
372, 375, 401 — `CARTOGRAPHIE.md:232-237`), elles, sont de vraies pages et
portent `MU +MORT.MB` comme n'importe quelle surcouche.

**`MORT.MB` ne doit pas boucler.** Le lecteur sait déjà le faire : la poignée
`@end` de `music.s` teste le bit 0 des drapeaux et, s'il est nul, branche sur
`@stop` qui appelle `_music_stop`. Il suffit que le convertisseur ne pose pas le
bit — `midi_to_mb.py` le pose systématiquement aujourd'hui, il lui faut un
`--no-loop`. Une marche funèbre en boucle serait comique au troisième tour.

### 4.3 Les fins

Le jeu n'a **pas de page finale unique** : trois fins, une par employeur.

| Page | Fin | Musique | Pourquoi |
| --- | --- | --- | --- |
| **175** | Le miracle de l'Anthérique (Gayolard) — *« FIN DE L'AVENTURE - SUCCÈS COMPLET »* (`TEXTFR/N150/N175.TXT:20`) | `MU +VICTOIRE.MB` | La seule victoire pleine. |
| **158** | Réussite : la carte est complète (Pompatarte) | `MU +VICTOIRE.MB` | Victoire de marchand, mais victoire. |
| **358** | Mission accomplie (Stratagus) — *« votre peu reluisante mission »* (`TEXTFR/N350/N358.TXT:12`) | **rien** : `TOUR.MB` continue | Le texte dit que c'est sale. La musique doit le dire aussi. |

Les **sept fins vivantes non victorieuses** (049, 052, 100, 141, 298, 327, 349)
ne prennent pas `VICTOIRE.MB` : elles gardent leur zone, ou passent en `MU -`.
Une fanfare sur une fuite est un contresens, et c'est le genre d'erreur que le
contrôle 5 du §2.4 ne saura pas détecter — il faut l'écrire à la main.

`VICTOIRE.MB` ne boucle pas non plus.

---

## 5. Le plan des musiques

Le détail — pages couvertes, citations, tempos, justifications, commandes de
régénération — est dans **`SCOSWAMP.MORE/MUSIC/propositions/`**, un dossier par
zone, plus un `INDEX.md` qui donne la table complète des 35 clairières. Les onze
pièces sont **déjà téléchargées, converties et rendues en `.wav`** : le `.wav`
sort de l'ancien aperçu, à volumes linéaires : reconvertir avec le
`midi_to_mb.py` actuel, qui rejoue `music.s` sur la table de volume de l'AY,
avant de juger.

### 5.1 Les onze musiques

| Zone | Fichier | Pièce | Auteur, date | bpm | Durée | Octets |
| --- | --- | --- | --- | ---: | ---: | ---: |
| `accueil` | `COMEAGAIN.MB` *(en place)* | Come Again | J. Dowland, 1597 | 120 | — | 478 |
| `village` | `VILLAGE.MB` | Il Est de Bonne Heure Né | Anonyme, c. 1470 | 150 | 48,0 s | 916 |
| `courbensaule` | `COURBENS.MB` | Saltarello | V. Galilei, 1584 | 180 | 35,8 s | 553 |
| `sud` | `MARAISUD.MB` | Pavane « Belle qui tiens ma vie » | T. Arbeau, 1588 | 125 | 31,5 s | 574 |
| `nord` | `MARAISNO.MB` | Tmeiskin | J. Japart, av. 1507 | 200 | 58,4 s | **1 058** |
| `riviere` | `RIVIERE.MB` | The Silver Swan | O. Gibbons, 1612 | 136 | 37,8 s | 719 |
| `danger` | `DANGER.MB` | Unquiet Thoughts | J. Dowland, 1597 | 140 | 55,6 s | 960 |
| `tour` | `TOUR.MB` | Pavan 2 | L. Milán, XVI<sup>e</sup> s. | 150 | 58,4 s | 548 |
| `combat` | `COMBAT.MB` | Bourrée en mi mineur BWV 996 | J. S. Bach, c. 1710 | 180 | 32,8 s | 644 |
| `mort` | `MORT.MB` | Marche funèbre KV 453a | W. A. Mozart, 1784 | 120 | 32,3 s | 725 |
| `victoire` | `VICTOIRE.MB` | Old 100th | L. Bourgeois, c. 1550 | 150 | 39,2 s | 315 |

Toutes du **domaine public** chez le Mutopia Project (Creative Commons *No
Rights Reserved*) — aucune sous CC-BY-SA, pour ne pas rouvrir la question de
compatibilité GPL v3 traitée par `MUSIQUE.md § 6.5`.

### 5.2 Les 35 clairières regroupées en cinq zones

| Zone | Clairières (`hub`) | Nb |
| --- | --- | ---: |
| `sud` | 304, 094, 179, 047, 031, 348, 227, 230, 314, **058**, 390, 082 | **12** |
| `danger` | 153, 088, 270, 319, 367, 187, 309, 125, 022, 165 | **10** |
| `nord` | 234, 084, 232, 218, 121, 161, 019, 202 | **8** |
| `riviere` | 295, 183, **045**, 044 | **4** |
| `courbensaule` | 078 | **1** |

`danger` est la seule zone **non géographique** : elle traverse le nord et le sud
et regroupe les dix clairières dont la page d'arrivée menace directement le
joueur — *« deux yeux rouges vous fixent, furieux »* (`TEXTFR/N000/N011.TXT:9-10`),
*« Leur pollen inspire la terreur »* (`TEXTFR/N200/N204.TXT:9-10`), *« un bruit de
succion »* (`TEXTFR/N300/N336.TXT:4-5`). C'est le seul endroit du plan où
l'ambiance l'emporte sur la carte, et c'est assumé : le joueur ne lit pas une
grille, il lit des pages.

### 5.3 Le tempo, qui est le vrai sujet

Les rendus actuels (100-120 à la noire) sont **trop lents sur la carte**, et pour
une raison technique : l'onde carrée n'a ni attaque ni extinction, donc une note
longue ne meurt pas — elle reste pleine jusqu'à la suivante. Ce qui passe pour de
la gravité au clavecin devient de l'inertie sur l'AY. D'où : **danses** au tempo
réel de la danse (180, 180, 200), **pièces graves** dans le haut de leur
fourchette (120 à 150). 100, 120, 125, 150 et 200 tombent juste sur le tick de
50 Hz (30, 25, 24, 20 et 15 ticks à la noire) ; 136, 140 et 180 demandent un
arrondi inaudible. Toutes les boucles font **31 à 59 s**, plus long que le séjour
dans une clairière moyenne (3,3 pages) : la couture ne s'entendra presque jamais.

---

## 6. Les données et la mémoire

### 6.1 Format et nommage

Rien à inventer : la chaîne existe déjà (`SCOSWAMP/SRC/Makefile:126-154`).

- Dans l'arbre de construction : `$(OUTDIR)/MUSIC/<NOM>.MB.BIN`.
- Sur le volume : `MUSIC/<NOM>.MB` — l'empaqueteur retire la dernière extension
  (`Makefile:126-128`).
- `<NOM>` en **majuscules ASCII, 12 caractères au plus**, pour que `<NOM>.MB`
  tienne dans les 15 caractères d'un nom ProDOS **et** dans le `char
  music_name[16]` de `scoswamp.c:141`. Le `+` d'une surcouche est consommé au
  moment du parsing (§2.3), il n'entre jamais dans le champ.
- `MUSIC` est déjà dans `PAYLOAD` (`Makefile:202`) : le piège documenté par
  `MUSIQUE.md § 5.2` — *« make hdv répondra "Nothing to be done" »* — a été
  refermé.

À faire : dix règles de plus dans `MUSICS` (`Makefile:134-149`), sur le modèle
exact des quatre existantes, et remplacer `ACCUEIL.MB.BIN` (2 339 octets pour un
seul écran) par les nouvelles.

### 6.2 Le disque

**7 490 octets pour les onze pièces**, sur ~28 Mo libres du `.hdv`. À comparer
aux 439 images RLE à ~6 Ko, soit 3,4 Mo (`MUSIQUE.md § 3.1`) : la musique
représente **deux millièmes** du volume. Le disque n'est pas une contrainte et ne
le sera jamais.

### 6.3 Le tampon

| | Aujourd'hui | Proposé |
| --- | ---: | ---: |
| `MUSIC_BUF_SIZE` (`music.h:11`, `music.s` `.res`) | 2 560 | **2 560** (= 2 × 1 280) |
| Plus grosse pièce | 2 339 (`ACCUEIL.MB`) | **1 058** (`MARAISNO.MB`) |
| Musiques simultanément résidentes | 1 | **2** |

Le tampon ne change pas de taille : il change de découpage. Deux demi-tampons de
1 280 octets couvrent la plus grosse pièce (1 058) avec 222 octets de marge, et
permettent zone + surcouche sans aucune lecture disque au moment du combat.

**Si l'on renonce à la surcouche** (politique 1 ou 2 du §4.1), `MUSIC_BUF_SIZE`
tombe à 1 280 et **rend 1 280 octets** au tas : la marge passerait de 3 012 à
~4 050. C'est la porte de sortie si un jour la mémoire manque — et elle ne coûte
qu'une constante.

Contrôle à ajouter au `Makefile` ou au validateur : **aucun `.MB.BIN` ne doit
dépasser la moitié du tampon**. Un flux plus gros serait tronqué par le `fread`
de `scoswamp.c:314` et le lecteur partirait dans les octets suivants.

### 6.4 Et la RAM auxiliaire ? Non, et voici le chiffre

`MUSIQUE.md § 3.2` a déjà établi le fond : le segment `LC` de cc65 est en
banque 2, or le stub d'interruption de ProDOS (`$BFEB`) commute la **banque 1** —
**aucun code ni donnée d'interruption ne peut vivre en `LC`**. Reste `AUXMOVE`
(`$C311`) via `a2e.auxmem.emd`.

| Poste | Octets |
| --- | ---: |
| Pilote `a2e.auxmem.emd` | 454 |
| Colle : sauvegarde/restauration de `$3C-$3F` et `$42-$43` (ProDOS ne sauve que `$FA-$FF`), garde `INTCXROM` | ~60 |
| **Coût** | **~514** |
| Économie : un demi-tampon | **−1 280** |
| **Gain net** | **766 o** |

766 octets, contre : le risque `RAMRD` de `MUSIQUE.md § 6.2` (`hgr_loader.s:151`
fait `sta $C002`, et une IRQ tombant entre la commutation et sa restauration
lirait la mauvaise banque), une recopie aux → principal aussi longue qu'une
lecture disque de 1 Ko, et un chantier entier là où il s'agit de gagner moins
d'un kilo-octet. **Non.** Le §6.3 obtient le même résultat avec une constante.

---

## 7. Plan d'implémentation

Ordonné par le risque : chaque étape est vérifiable seule dans POM2, et les deux
premières lèvent tout le doute.

| # | Fichier | Ce qu'on fait | Octets | Vérification dans POM2 |
| ---: | --- | --- | ---: | --- |
| **1** | `SCOSWAMP/SRC/music.s`, `music.h` | `_music_pause` / `_music_resume` (§3.5) | **+70 `CODE`, +1 `BSS`** | Panneau *Devices ▸ Sound ▸ Mockingboard* (Ctrl+Shift+P) : R7 doit passer à `$3F` et les amplitudes à 0 pendant le chargement, puis revenir à `$38`. |
| **2** | `scoswamp.c:1858`, `:1955-1957` | `music_pause()` au lieu de `music_stop()` ; `music_resume()` après l'image | **~10** | Poser `MU MARAISUD.MB` sur deux pages voisines : la musique ne repart plus du début. C'est **le test qui valide la demande**. |
| **3** | `scoswamp.c` (`music_cur`, `music_zone`, `music_over`, `music_switch`) | La cascade du §2.3 | **+110 `CODE`, +33 `BSS`** | Une page sans `MU` ne coupe plus rien ; `MU -` fait le silence. Vérifier au panneau qu'**aucune** écriture AY ne part au changement de page dans la même clairière. |
| **4** | `classify_line` (`scoswamp.c:885-888`) | Lecture du `+` de surcouche | **+15** | `MU +COMBAT.MB` sur une page isolée : la page suivante revient au thème de zone. |
| **5** | `music.s` (`base`, `music_select`) | Deux demi-tampons de 1 280 (§4.1) | **+30 `CODE`, +2 `BSS`** | Entrer dans un combat : la bascule est **instantanée**, aucun voyant d'accès disque. |
| **6** | `scoswamp.c:1842` (`die_and_restart`) | `MORT.MB` sur l'écran de mort | **+25** | Mourir en combat : la marche funèbre part, joue une fois, s'arrête. |
| **7** | `sfx.s` (5 entrées) | `php / sei … plp` (`MUSIQUE.md § 3.4`) | **+8** | Un coup d'épée pendant `COMBAT.MB` : le bruitage ne craque plus. |
| **8** | `SCOSWAMP.MORE/MUSIC/midi_to_mb.py` | `--no-loop` pour `MORT.MB` et `VICTOIRE.MB` | 0 (outil) | Le bit 0 de l'octet +5 du `.MB.BIN` doit être nul (`xxd -l 8`). |
| **9** | `SCOSWAMP/SRC/Makefile:134-149` | Dix règles `MUSICS`, retrait d'`ACCUEIL.MB` | 0 | `make hdv` doit **refabriquer** le volume après une modification de musique (`MUSIC` est dans `PAYLOAD`, `:202`). |
| **10** | `SCOSWAMP/TEXTFR` + `TEXTEN` | 35 lignes `MU` d'arrivée + ~25 lignes de zone et de surcouche, **×2 langues** | 0 | Parcourir une traversée complète : la musique ne change qu'aux frontières du §5.2. |
| **11** | `SCOSWAMP.MORE/TOOLS/reflow_txt.py` | Les cinq contrôles du §2.4 | 0 (outil) | Le validateur doit crier si l'on retire une ligne `MU` d'arrivée. |
| | | **Bilan `CODE` + `BSS`** | **~+305** | Marge : 3 012 → **~2 707** |

L'étape 10 est la seule qui touche au corpus, et **elle vient en dernier** : tant
que les étapes 1 à 9 ne sont pas vertes, poser 120 lignes dans deux langues
serait poser 120 lignes à refaire.

Après chaque étape : `cd SCOSWAMP/SRC && make check`. `SCOSWAMP/DOCS/MEMOIRE.md:46-63`
rappelle que **`ld65` peut manquer un débordement de `BSS`** — si `__ONCE_RUN__`
dépasse déjà le plafond, la taille se calcule en négatif et le lien réussit *sans
avertissement* en écrasant ProDOS. **Ne jamais conclure d'un lien réussi que le
binaire tient.**

---

## 8. Risques

| # | Risque | Gravité | Parade |
| ---: | --- | --- | --- |
| 1 | **IRQ masquées par ProDOS** pendant les E/S (`MUSIQUE.md § 6.1`). Note tenue de ~45 ms par fenêtre, dérive de 3 à 8 ticks par page. | Moyenne | §3.4. Le §2 supprime déjà la lecture de musique pour trois pages sur quatre. À arbitrer **à l'oreille**, pas sur le papier. |
| 2 | **`sfx.s` désaccordé par l'IRQ musicale** (`MUSIQUE.md § 3.4`, `sfx.s:29-35`). Aujourd'hui théorique ; avec une musique de combat, **permanent et audible**. | **Haute** | Étape 7 : `php / sei … plp`, 8 octets. Non facultatif. |
| 3 | **Une arrivée de clairière sans `MU`** : la musique de la clairière précédente déborde. Le jeu marche, personne ne le voit. | **Haute** (silencieux) | Contrôle 5 du §2.4, croisé avec `carte.json`. C'est la raison d'être du validateur. |
| 4 | **Nom de musique tronqué** par le `strncpy` de `scoswamp.c:887` : `music_name[16]` ne tient que 15 caractères. Échec silencieux à la lecture. | Moyenne | Contrôle 1 du §2.4. Aucun `<NOM>` au-delà de 12 caractères. |
| 5 | **Les trois pages disputées** (363, 394, 330 — `CARTOGRAPHIE.md:810-820`) reçoivent deux `MU` de zone contradictoires. | Moyenne | Appliquer l'arbitrage de `propositions/INDEX.md § 2` **avant** de poser les lignes. |
| 6 | **Divergence FR/EN** : deux langues, deux musiques sur la même page. | Faible | Contrôle 3 du §2.4. |
| 7 | **Débordement de `BSS` non signalé par `ld65`** (`MEMOIRE.md:46-63`). | **Haute** | `make check` après chaque étape, jamais `make` seul. |
| 8 | **Un `.MB.BIN` plus gros que le demi-tampon** : `fread` tronque, le lecteur part dans les octets suivants. | Moyenne | Contrôle de taille au `Makefile` (§6.3). `MARAISNO.MB` à 1 058 o est déjà à 83 % du demi. |
| 9 | **`ACCUEIL.MB` (2 339 o) ne rentre plus** dans un demi-tampon de 1 280. | Faible | Elle est de toute façon remplacée par `COMEAGAIN.MB` (478 o), déjà en place sur la page 000. |
| 10 | **Pas de musique sur //c** : pas de slot, et POM2 n'émule pas la Mockingboard 4c (`MUSIQUE.md § 6.4`). | Nulle | `music_detect()` rend 0, toutes les entrées commencent par `lda mb_slot / beq rts` : le jeu est identique, `sfx.s` continue seul. Aucun `#ifdef`. |
| 11 | **`MORT.MB` ou `VICTOIRE.MB` qui boucle** faute du `--no-loop` de l'étape 8. | Faible mais ridicule | `xxd -l 8` sur le `.MB.BIN` : bit 0 de l'octet +5. |
| 12 | **Droits.** Les onze pièces sont dans le domaine public chez Mutopia, mais `MUSIQUE.md § 6.5` rappelle que la GPL v3 exige la redistribuabilité de **toute** l'œuvre. | Faible | Aucune pièce sous CC-BY-SA n'a été retenue, délibérément. Les licences sont dans chaque `README.md` de `propositions/`. |

---

*Mesures faites pour ce document : `make check` (marge 3 012 o, LOWBSS 66 o) ;
`grep -rn '^MU ' SCOSWAMP/TEXT{FR,EN}` (une seule occurrence) ; onze pièces
téléchargées depuis `mutopiaproject.org`, converties par `midi_to_mb.py` et
rendues en `.wav` dans `SCOSWAMP.MORE/MUSIC/propositions/`.*
