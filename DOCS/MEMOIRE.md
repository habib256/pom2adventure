# Mémoire sur Apple IIe Enhanced

**Mesures actuelles de SCOSWAMP, 6 septembre 2026 :** voir
l'[audit du binaire, des fonctions et des buffers](AUDIT-MEMOIRE-SCOSWAMP.md).
Les valeurs historiques ci-dessous expliquent les étapes de développement ;
elles ne remplacent pas les adresses et marges mesurées dans cet audit.

Comment le projet occupe la mémoire, ce qui reste disponible, et ce qu'il en
coûte de le récupérer. Toutes les valeurs ont été mesurées avec cc65 2.19.

---

## Carte mémoire

```
$0000-$01FF  Page zéro + pile 6502 (système)
$0200-$03FF  Buffer d'entrée, vecteurs
$0400-$07FF  Page texte 1  ← utilisée, sauvegardée par memory_swap.c
$0800-$0BFF  Tampon d'E/S ProDOS du fichier ouvert (iobuf-0800)
$0C00-$0FFF  MAPBSS (1 Ko) ← données du menu MAP + tampons ; voir plus bas
$1000-$1FFF  LOWBSS (4 Ko) ← gros tampons, segment à part, voir « Zones récupérables »
$2000-$3FFF  HGR page 1 (8 Ko)  ← images des scènes
$4000-....   Moteur : CODE, RODATA, DATA, BSS
     ....    Tas C (buffers ProDOS, 1 Ko par fichier ouvert)
     ....    Pile C (2 Ko, __STACKSIZE__)
$9600-$BEFF  BASIC.SYSTEM  ← récupérable (10,25 Ko), voir plus bas
$BF00-$BFFF  Page globale ProDOS 8 — JAMAIS disponible
$C000-$CFFF  Espace d'E/S
$D000-$FFFF  ROM / Language Card (banques commutées)
```

Le moteur charge à `$4000` et non à l'adresse cc65 par défaut `$0803`, afin de
préserver HGR page 1. `$1000-$1FFF` est repris depuis le 2026-09-03 par le
segment `LOWBSS` de `SRC/scoswamp.cfg`, et `$0C00-$0FFF` depuis le 2026-09-04
par le segment `MAPBSS`.

---

## Les deux plafonds

Ne pas confondre la taille du fichier et l'empreinte réelle.

| Contrainte | Ce qu'elle limite | Vérifiée par |
|------------|-------------------|--------------|
| Taille du `.BIN` | CODE + RODATA + DATA + INIT + ONCE | `check-project.sh` |
| Empreinte exécution | + BSS + tas + pile | `check-memory.sh` (lit le `.map`) |

Le `.BIN` **ne contient pas la BSS** : les variables non initialisées sont
allouées au lancement, juste après DATA. Un binaire de taille acceptable peut
donc parfaitement déborder à l'exécution.

### Le piège `ld65`

La zone BSS est définie ainsi dans les configs cc65 :

```
BSS: start = __ONCE_RUN__, size = __HIMEM__ - __STACKSIZE__ - __ONCE_RUN__;
```

Si `__ONCE_RUN__` dépasse déjà le plafond, la taille se calcule **en négatif**,
déborde en non signé vers ~4 Go, et le contrôle d'overflow est neutralisé :
**le link réussit sans le moindre avertissement**, et la BSS écrase ProDOS.

Le contrôle fonctionne normalement dans les autres cas — un tableau de 30 Ko
produit bien `Segment 'BSS' overflows memory area 'BSS' by 10284 bytes`. Le
piège ne se déclenche que lorsque la BSS démarre du mauvais côté du plafond,
c'est-à-dire exactement quand on en aurait le plus besoin.

**Ne jamais conclure d'un link réussi que le binaire tient.** Produire le `.map`
et le vérifier :

```bash
cl65 ... -Wl -m,build.map -o PROG.BIN ...
./tools/check-memory.sh build.map            # config standard
./tools/check-memory.sh build.map --himem 0xBF00   # config étendue
```

---

## Configuration standard vs étendue

| | `apple2enh.cfg` (cc65) | `SRC/apple2enh-game.cfg` |
|---|---|---|
| Adresse de chargement | `$0803` (forcée à `$4000` par `-Wl -S`) | `$4000` (dans la config) |
| `__HIMEM__` | `$9600` | `$BF00` |
| Plafond BSS + tas | `$8E00` | `$B700` |
| **Utilisable depuis `$4000`** | **19 968 o** | **30 464 o** |
| BASIC.SYSTEM | préservé | **détruit** |
| Sortie du programme | `exit()` | `prodos_quit()` **obligatoire** |

Le gain est de **10 496 octets**.

`$9600` est la valeur prudente de cc65 (« presumed RAM end ») : elle suppose
BASIC.SYSTEM résident en `$9600-$BEFF`, ce qu'implique un lancement par `]BRUN`.
Un programme qui renonce à revenir au BASIC peut occuper cette zone. La limite
absolue reste `$BF00`, début de la page globale ProDOS.

### Contrepartie : la sortie

Avec la config étendue, la BSS et le tas s'étendent au-dessus de `$9600` et
détruisent BASIC.SYSTEM **en cours de partie**. Un `exit()` rendrait la main à
un programme qui n'existe plus.

Il faut sortir par l'appel MLI QUIT — voir `SRC/prodos_quit.asm` :

```c
#include "prodos_quit.h"
...
} else if (key == 'Q' || key == 'q') {
    set_video_mode(0);
    videomode(VIDEOMODE_40COL);
    clrscr();
    cprintf("Au revoir!\r\n");
    prodos_quit();          /* et non exit(0) */
}
```

---

## Zones récupérables

### 1. `$9600-$BEFF` — BASIC.SYSTEM : **+10 496 o** ✅ retenu

Décrit ci-dessus. C'est le gain le plus important et le plus simple : un
changement de config plus un remplacement de `exit()`.

### 2. `$1000-$1FFF` — RAM basse : 4 096 o ✅ retenu (segment LOWBSS, 2026-09-03)

Cette zone est réellement libre, puisque le chargement commence à `$4000`. Y
reloger **toute** la BSS serait un piège : dans cc65 le tas n'est pas un
segment, `_heap.o` calcule

```
__heaporg = __BSS_RUN__ + __BSS_SIZE__     (juste après la BSS)
__heapend = sp - __STACKSIZE__
```

et **le tas suit la BSS, où qu'elle soit**. Relogée en `$0800`, le tas partirait
de là jusqu'à la pile, à travers HGR page 1 puis le code. Vérifié : le linker
accepte cette configuration sans broncher, `tools/check-memory.sh` la refuse.

La bonne façon est un **second segment**. `SRC/scoswamp.cfg` (copie de
`apple2enh.cfg`) ajoute une zone `LOWRAM` `$1000-$1FFF` et un segment `LOWBSS`
de type bss. La BSS principale reste derrière le code, le tas derrière elle ;
seuls les gros tampons désignés partent en bas :

```c
#pragma bss-name (push, "LOWBSS")
char file_buffer[FILE_BUFFER_SIZE];
#pragma bss-name (pop)
```

Y vivent le catalogue des messages (1 763 o), le tampon de page (1 280 o), le
tampon du décodeur HGR (**128 o** depuis le 2026-09-04 — ProDOS lit par blocs
de 512 octets et les met en cache dans son propre tampon, donc le même nombre
de blocs lus, seulement plus d'appels à `fread`), l'état de l'application
`app` (238 o), la mémoire des monstres `seen` (160 o), la barre de titre
(81 o), les lignes de corps, les deux noms de musique et la table de
rabattement page → clairière : 4 073 octets, 23 restent. Deux règles :

- `crt0` ne met à zéro que le segment `BSS` ; `main()` efface `LOWBSS` lui-même
  avec `__LOWBSS_RUN__` / `__LOWBSS_SIZE__` (déclarés côté C avec un souligné
  de moins, cc65 en ajoute un) ;
- jamais plus de **deux fichiers ouverts à la fois** : `iobuf-0800` distribue
  ses tampons de 1 Ko à partir de `$0800` vers le haut sans connaître `LOWRAM`.
  Le jeu n'en ouvre qu'un.

### 2 bis. `$0C00-$0FFF` — le second tampon ProDOS : 1 024 o ✅ retenu (segment MAPBSS, 2026-09-04)

Le kilo-octet que la note ci-dessus réservait « pour un éventuel second tampon
ProDOS » n'a jamais été réclamé : **le jeu n'ouvre qu'un fichier à la fois**,
chaque `fopen` étant suivi de son `fclose` avant le suivant (texte, image,
musique, aide, sauvegarde, catalogue, carte). `SRC/scoswamp.cfg` y pose la zone
`MAPRAM` et le segment `MAPBSS`, qui loge :

| Contenu | Taille |
|---|---|
| `map_data[]` — en-tête, 35 clairières, bloc de langue du fichier `MAP` | 884 o |
| `visited[]` de `rules.c` — le bitmap des pages vues | 53 o |
| l'en-tête de sauvegarde lu par `slot_title`, la liste de `choose_stones`, les statiques de `cfmt` | ~87 o |

**Ce sont 1 024 octets qui ne coûtent rien à la fenêtre principale.** C'est ce
qui a rendu le menu MAP possible : la marge du tas était de 510 octets avant le
chantier, et les seules données de la carte en demandaient le double.

**La contrepartie, écrite dans le `.cfg` :** plus jamais deux fichiers ouverts
en même temps. `iobuf-0800` distribue ses tampons de 1 Ko à partir de `$0800`
vers le haut, sans connaître `MAPRAM` : un second `fopen` simultané écraserait
la carte.

### 3. `$D400-$DFFF` — Language Card : 3 072 o ✅ pleine (3 030 o utilisés)

Les configs cc65 définissent déjà un segment `LC` à cette adresse (banque deux,
derrière le code quit). Il accueille du code **en lecture seule**, désigné
fonction par fonction :

```c
#pragma code-name(push, "LC")
void fonction_peu_appelee(void) { ... }
#pragma code-name(pop)
```

C'est fait pour les fonctions froides (jets, pierres, noms d'objets) : il reste
42 octets. Il n'y a **rien d'autre à prendre** dans la Language Card sous
ProDOS 8 : la banque 1 de `$D000-$FFFF` porte le noyau, et `$D000-$D3FF` de la
banque 2 son code de sortie. Les « 16 Ko inutilisés » qu'on lisait ailleurs
n'existent pas.

### 4. RAM auxiliaire — 64 Ko ⚙️ gros gain, gros travail

Un //e Enhanced avec carte 80 colonnes étendue dispose de 64 Ko auxiliaires.
cc65 ne les gère pas : il faut commuter les banques à la main (`$C002-$C005`,
`$C008-$C009`) et copier via `AUXMOVE` (`$C311`).

Piste sérieuse pour un cache d'images HGR — charger plusieurs scènes d'avance
en RAM auxiliaire et les basculer instantanément — mais sans rapport avec la
taille du moteur, que le linker ne saurait pas y placer.

cc65 livre déjà le mécanisme : le pilote de mémoire étendue `a2e.auxmem.emd`
(454 octets, liable en statique) expose l'auxiliaire en pages de 256 octets via
`em_copyto` / `em_copyfrom`. Pour du **code**, la voie est celle des overlays
ld65 (fenêtre commune pour les écrans froids : aide, sauvegarde, création du
personnage, boutique de pierres), préchargés en auxiliaire puis recopiés à
l'appel.

---

## Empreinte mesurée

Mesures cc65 2.19, chargement à `$4000`, pile 2 Ko.

| Build | Fin de BSS | Empreinte | Config standard | Config étendue |
|-------|-----------|-----------|-----------------|----------------|
| SPACETRIP | `$79AC` | 14 764 o | ✅ | ✅ |
| COMBAT | `$7A3B` | 14 907 o | ✅ | ✅ |
| SCOSWAMP | `$8516` | 17 686 o | ✅ marge 2 282 o | ✅ marge 12 778 o |
| SCOSWAMP + COMBAT | `$A64B` | 26 187 o | ❌ dépasse de 6 219 o | ✅ marge 4 277 o |
| SCOSWAMP 2026-09-03 matin (objets, amulettes, `__HIMEM__` $BF00, pile 384 o) | `$BCC8` | 31 944 o | — | ✅ marge 184 o |
| SCOSWAMP 2026-09-03 soir (LOWBSS, sans printf, `-Cl`) | `$A0B0` env. | 24 600 o env. | — | ✅ marge 7 544 o |
| SCOSWAMP 2026-09-04 (musique, objets, amulettes) — avant le menu MAP | `$BB82` | 31 618 o | — | ✅ marge **510 o** |
| SCOSWAMP 2026-09-04 (menu MAP, `--codesize 100`, MAPBSS) | `$BC46` | 31 814 o | — | ✅ marge **314 o** |
| SCOSWAMP 2026-09-04 soir (+ prologue, combat rythmé, banc de traversée) | `$BC87` | 31 879 o | — | ✅ marge **249 o** |

La dernière ligne cumule quatre mesures du même jour, chacune faite seule sur
le binaire complet :

| Étape | Gain |
|-------|------|
| segment `LOWBSS` en `$1000` (3 869 o de tampons sortis de la fenêtre) | + 3 869 o |
| `cfmt` maison à la place de cprintf/sprintf (famille printf déliée) | + 876 o |
| `-Cl` (locales statiques) | + 547 o |
| `classify_line` sur trois octets au lieu du pointeur, `int` → `unsigned char`, barre de titre et bandeau via `cfmt` | + 1 100 o env. |

Et le 2026-09-04, pour payer le menu MAP (mesures au lien, chacune seule) :

| Étape | Gain |
|-------|------|
| `--codesize 100` passé à cc65 (il en prend bien plus par défaut) | + 1 310 o |
| zone `MAPRAM` en `$0C00-$0FFF` (segment `MAPBSS`) | + 1 024 o *(hors fenêtre)* |
| `int` → `unsigned char`, `is_fr()` à la place de `strcmp`, `load_hgr_image` morte | + 228 o |
| tampon HGR de 1 Ko à 256 o, puis `app` et les tampons partis en RAM basse | + 416 o |
| `classify_line` : table de 33 directives + `switch`, au lieu de 29 cascades de tests | + 336 o |
| `map_voisin` et `map_str` dans la Language Card, deux tampons de 81 o partagés | + 531 o |
| toutes les pannes de disque par une seule fonction `oops()` | + 213 o |
| `visited[]`, `slot_title`, `choose_stones`, `cfmt` déménagés en `MAPBSS` | + 175 o |

La fusion SCOSWAMP + COMBAT **ne passe qu'avec la configuration étendue**, où
elle laisse 4 277 octets de tas — soit quatre buffers ProDOS, alors que le jeu
n'ouvre qu'un fichier à la fois.

À titre de comparaison, SCOSWAMP seul en configuration standard ne dispose
aujourd'hui que de 2 282 octets de tas : la fusion en config étendue est donc
**moins contrainte que la situation actuelle**.

---

## Validation restant à faire

Les mesures ci-dessus sont statiques, issues des fichiers `.map`. Elles
établissent que le binaire tient. Elles ne remplacent pas un essai réel :

- [ ] Lancer le binaire en configuration étendue sous Virtual ][ ou AppleWin
- [ ] Vérifier que `prodos_quit()` rend bien la main au sélecteur ProDOS
- [ ] Vérifier qu'ouvrir une scène après destruction de BASIC.SYSTEM fonctionne
      (ProDOS tient une carte d'occupation mémoire en `$BF58-$BF6F` ; il faut
      s'assurer que les buffers alloués par cc65 y sont correctement déclarés)
- [ ] Vérifier le comportement quand plusieurs fichiers sont ouverts simultanément

Le dernier point est le plus incertain et doit être testé avant de basculer
SCOSWAMP sur la configuration étendue.
