# TODO

Chantiers ouverts, du plus rentable au moins rentable. Convention :
`🟠 haute · 🟡 moyenne · 🟢 basse`, effort en *italique*, fichiers en
`backticks`. L'émulateur a son propre TODO : `../pom2/TODO.md`.

Ce qui est fait, et le *pourquoi* des corrections passées (pièges cc65, ld65,
80STORE, ProDOS, génération d'images) : [SCOSWAMP/DOCS/CHANGELOG.md](SCOSWAMP/DOCS/CHANGELOG.md).
Chiffres mémoire de référence : [l'audit du binaire](SCOSWAMP/DOCS/AUDIT-MEMOIRE-SCOSWAMP.md).
Mesures ci-dessous : 2026-09-14.

---

## 1. D'abord — gros gain, petit effort

La première vague (préfiltre, rapport des pires, aperçu fidèle, tempos,
contrôles) est faite le 2026-09-14 : voir le [CHANGELOG](SCOSWAMP/DOCS/CHANGELOG.md).
Il reste ce qu'elle a ouvert, et qui demande une oreille ou une décision :

1. 🟠 **Écouter, puis régler les volumes** — *petit* — les aperçus sont enfin
   fidèles (`make -C SCOSWAMP/SRC musics` les écrit à côté de chaque MIDI dans
   `SCOSWAMP.MORE/MUSIC/propositions-moderne/`). Tous les flux sont en
   `--vol 10,8,8,9,8,8` : la mélodie sort à +6,8 dB. Propositions chiffrées,
   à trancher à l'oreille : `12,11,11,11,11,11` ou `10,9,9,9,9,9`. Écouter en
   priorité GIANT (+8,7 % de tempo) et ORCS (−9,6 %) ; BENTBEAKS n'a plus que
   11 octets de marge.
2. 🟠 **Décider `--resample area` par défaut** — *petit, mais reconvertit
   tout* — `SCOSWAMP.MORE/TOOLS/convert_images.sh` (`RESAMPLE=area`). Sur les
   452 images : pixels isolés 2,64 → 1,70 %, SSIM 0,786 → 0,814, images au-delà
   de 4,5 % d'isolés 46 → 4. Mais 24 empirent, surtout des recettes réglées
   pour le bilinéaire (B225, B235, B281, B301, B355, B378, B402, N001, N023,
   N028, N035, N036, N045, N133, N149, N287, N314, N363, N393, N396, N406,
   N409, N411, N419), et un trait fin clair tourne au gris (N144). L'atelier
   web ne propose pas encore `area`, et une recette ne l'enregistre pas.
3. 🟡 **Calibrer les seuils de refus des masters** — *petit* —
   `generate_images.sh` (`IMAGE_MIN_PALETTE`, `IMAGE_MAX_ISOLATED`) : à 80 % /
   4,5 %, 203 des 452 masters actuels seraient refusés. Trop sévère pour la
   prochaine génération sans ajustement.
4. 🟡 **Bourdon possible sur la voix 5** — *petit* — dans 29 flux, la voix de
   batterie reçoit un volume avant sa première frappe et rejoue la dernière
   hauteur restée dans le registre : un bourdon après une pièce qui chantait
   sur cette voix. À corriger dans `midi_to_mb.py`, ce qui change les flux.
5. 🟢 **Docs restées à l'ancienne** — *trivial* — les README des pièces citent
   les anciens bpm et « le .wav est ce que la carte jouera »
   (`propositions-moderne/accueil/README.md:62`…) ; la docstring de
   `SCOSWAMP.MORE/TOOLS/build_map.py` annonce 115 pages (116 depuis N421).
6. 🟢 **Dépendances de `image_quality.py`** — *trivial* — numpy et Pillow
   manquent au `python3` Homebrew ; les scripts retombent sur
   `/usr/bin/python3` et désactivent le contrôle sans eux. Choisir et
   documenter.

## 2. Ensuite — qualité des images et de la musique

- 🟡 **Régénérer les pires masters** avec un seul modèle et une taille fixe —
  *moyen* — N144, N089, N313, N248, N125, N243, N209, N066, N339, N227, N216,
  N163, N065, N082, N308, N371, N040, N113, B028, B215, puis ce que désigne
  `ADVKIT/TOOLS/image_quality.py worst`.
- 🟡 **Enveloppe logicielle par voix** (attaque, décroissance, palier) — *moyen* —
  `SCOSWAMP/SRC/music.s` (`@note`, tick), `compose.py` (`GATE`). C'est la
  cause principale du son terne : chaque note est un bloc carré coupé net.
  Estimé 60 à 90 o CODE + 12 o BSS contre la marge de `make` (1 919 o,
  plancher 1 792) ; rend environ 20 % des octets de flux.
- 🟡 **Une voix fixe par piste MIDI** — *petit* — `midi_to_mb.py`
  (`reduce_voices`) : jusqu'à 41 % des notes d'accompagnement changent de voix.
- 🟡 **Batterie prioritaire sur un même tick** — *trivial* — `midi_to_mb.py`
  (`write_mb1`) : SPIDERS perd 40 coups.
- 🟡 **Boucle de BATTLE sans fondu ni silence** — *trivial* — `--fade 0 --tail 0`,
  `music.s` (`@end`) : un creux d'environ 0,9 s à chaque tour.
- 🟡 **Règle de cadrage des images** — *petit* — les gros plans des batailles
  (B225–B402 ne gardent que 2 à 15 % du master, B392 réduite à une tête
  d'aigle ; B012–B224 coupent le héros ; N017, N023) sont-ils voulus ? Si oui,
  les demander dans le prompt. Abandonner les retouches de tonalité : elles
  n'améliorent aucune mesure et faussent les couleurs (B028).
- 🟢 **Commande de répétition dans le flux MB1** — *moyen* — `music.s`,
  `midi_to_mb.py`, `SCOSWAMP.MORE/TOOLS/audit_music.py` : environ 50 o CODE
  estimés, flux ramenés à 44–76 % ; de quoi faire boucler les zones, qui se
  taisent après 31 à 54 s.
- 🟢 **Décroissance AY pour la batterie** (voix 5) — *petit* — `music.s` (`@noise`).
- 🟢 **Recomposer les plus faibles** : SPIDERS, WILLOWISP, GIANT, BENTBEAKS,
  CLIFF — *moyen* — `SCOSWAMP.MORE/MUSIC/propositions-moderne/clairieres/`.
- 🟢 **Cohérence des planches** — *petit* — `SCOSWAMP.MORE/TOOLS/build_manifest.py` :
  les 30 `REF/CLAIRIERE_xx` ne sont jamais jointes (leurs alias « Clairiere n 1 »
  n'existent pas dans les textes) ; `COUPEUR` et `AMULETTE_GRENOUILLE` non plus ;
  `REF/T364.png` égaré ; pantalon du héros vert dans B124, B134, B215, B392.
  Puis `build_manifest.py --record` : aujourd'hui 0/453 empreintes
  correspondent, `--stale` ne sert à rien.

## 3. Le jeu

- 🟡 **Pages hors aventure** (N900+) — *moyen* — la carte du livre, les règles
  du combat, les crédits : du pur contenu, le mécanisme `[H]` existe.
- 🟡 **Game feel** — *petit* — le dé qui roule (quelques valeurs avec un clic,
  ~40 o), le flash de blessure (bandeau inversé un instant), une directive
  `S <n>` de jingle d'entrée de scène (danger, victoire, découverte).
- 🟢 **Vérifier en jeu les branches 193 et 326 de `DV`** — *petit* — seule la
  branche « aucune blessure » (241) a été vue.
- 🟢 **Les invites de combat en mode image** — *petit* — `wait_space_at` et
  `prompt_luck` écrivent sans allumer le texte : invisibles en plein écran,
  mais n'importe quelle touche les satisfait. À confirmer puis corriger comme
  `show_inventory`.
- 🟢 **Les Provisions** existent dans `Character`, aucune page ne s'en sert
  (l'or, lui, est câblé : `E OR`, `ED OR`). Vérifier contre le livre si des
  repas manquent.

## 4. Outillage et parc

- 🟡 **SPACETRIP et le tas de 270 octets** — *petit* — `SPACETRIP/build.sh`
  ne lie pas `apple2enh-iobuf-0800.o` et `spacetrip.c` ouvre 4 fichiers :
  vérifier qu'il ne souffre pas du `fopen` impossible corrigé dans SCOSWAMP
  le 2026-08-29.
- 🟡 **`reflow_txt.py` dans `make check`** — *petit* — ses invariants (corps
  ≤ 19 lignes à 78 colonnes, choix ≤ 4 lignes, titre ≤ 60, ASCII seul) ne
  tournent qu'à la main : une page trop longue ne se voit qu'à l'écran.
- 🟢 **Presets //c+ et PAL** dans `ADVKIT/TOOLS/pom2_playtest.cpp` — *petit* —
  le //e et le //c se vérifient au banc, pas eux.
- 🟢 **Non-régression du décodeur 6502** — *moyen* — les bugs de flags de
  `hgr_loader.s` n'ont été vus qu'en exécutant ; décoder le corpus sous POM2 et
  comparer au décodeur C.
- 🟢 **`build_paths()` ignore `lang`** — *trivial* — `SCOSWAMP/SRC/paths.c:29`,
  paramètre `(void)` : le retirer de la signature.
- 🟢 **Documenter les pièges `errno` / `_oserror`** — *trivial* —
  `SCOSWAMP/DOCS/MEMOIRE.md` : en cc65 `errno=2` vaut `ENOMEM`, et
  `_oserror == 0` dit que l'échec est côté runtime C, pas ProDOS.

---

## Constats des audits du 2026-09-14

Les deux chaînes sont reproductibles à l'octet : les 452 RLE se refabriquent
depuis masters et recettes, les 45 `.MB.BIN` depuis leurs MIDI. La qualité se
perd en amont, pas dans l'outillage.

**Images.** L'erreur de conversion suit la distance du master à la palette
(corrélation 0,99) : les 102 pires sont des masters RGB sombres et désaturés,
dont 64 % seulement des pixels sont à moins de 10 ΔE de la palette ; le
mouchetis suit leur détail fin (0,85). Deux modèles mélangés (gpt-image-1.5
et 2), 31 tailles de sortie. La réduction bilinéaire (2×2 texels par cellule)
amplifie le tout. Les meilleures images sont des aplats (N407, N096, N315,
N049).

**Musique.** 0 note perdue, désaccord moyen 2 à 4 cents. Les défauts sont
systémiques : pas d'enveloppe par note (ENV/ENVON de MUSIQUE.md §5.2 jamais
implantés), tempos entre deux ticks, voix réparties par hauteur, collisions de
batterie, fondu d'entrée qui avale le premier temps, zones qui ne bouclent pas.

Non vérifié : rien n'a été écouté (ni POM2 ni carte réelle), le rendu CRT des
images n'est pas mesuré, les coûts en octets 6502 sont estimés.
