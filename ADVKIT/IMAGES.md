# Atelier de correction des images

Lancement depuis le dépôt :

```sh
cmake --build ADVKIT/TOOLS/build --target scoswamp_dhgr build_prodos_volume
sh ADVKIT/serve.sh 8765
```

Ouvrir `http://127.0.0.1:8765/ADVKIT/`.
Le serveur Python statique ne suffit plus pour convertir et enregistrer.
Le serveur de l’atelier écoute uniquement sur la machine locale.

1. Choisir SCOSWAMP ou SPACETRIP, puis une vignette ou le menu **Image**.
   La recherche accepte `B120` / `N012` ; Entrée sélectionne le résultat.
2. Activer le cadrage. Déplacer le cadre, tirer son coin inférieur droit ou
   utiliser Zoom. Le cadre conserve le ratio visuel Apple II **35:24**.
   Les flèches déplacent le cadre d’un pixel source ; Maj multiplie par dix.
3. Ajuster luminosité, contraste, gamma, bruit de couleur et diffusion.
   Choisir le noyau Floyd–Steinberg / Jarvis-mod et le modèle DHGR.
   **Le tramage est désactivé par défaut et après Réinitialiser.**
   Une correction déjà enregistrée retrouve ses propres réglages.
4. Comparer original et résultat, éventuellement en vue agrandie. Le calque
   source superpose l’original cadré ; la zone de texte matérialise les quatre
   lignes du mode mixte. Ces deux aides ne sont pas inscrites dans l’image.
5. Cliquer **Générer & enregistrer le DHGR RLE**. Le bouton reste visible sous
   les réglages, même quand ceux-ci défilent. Si l’aperçu n’est pas à jour,
   cette action réalise la conversion finale avant d’enregistrer.
6. **Construire le disque .HDV**, puis télécharger le disque pour POM2.
   Seules les corrections enregistrées sont incluses dans ce disque.

Pour B120, les sorties sont :

- `SCOSWAMP/DHGR/N100/B120.RLE.BIN` : flux final DHRR, 16 384 octets décompressés ;
- `SCOSWAMP.MORE/IMAGE-RECIPES/B120.json` : réglages et rectangle en pixels source ;
- `SCOSWAMP.MORE/HGR-PREVIEW/B120.png` : rendu composite ColorNTSC de POM2 ;
- `SCOSWAMP.MORE/CHATMAUVE-PREVIEW/B120.png` : rendu des blocs Chat Mauve.

Le master `GENERATED/B120.png` reste intact. Les scripts `convert_images.sh`
relisent la recette si le master ou les réglages changent. Les images sans
recette gardent leur ancienne chaîne de conversion. Les brouillons conservés
pendant la navigation entre images restent en mémoire du navigateur : il faut
les enregistrer avant de fermer la page.

SPACETRIP utilise actuellement le format HGR brut : le même atelier écrit
`SPACETRIP/IMG/Nxxx.HGR.BIN` (8 192 octets) et sa recette, sans modifier le
format attendu par son moteur actuel. Le bouton disque reconstruit ce moteur
et son volume ; cela ne constitue pas encore la migration au moteur commun.

## Conversion et fidélité

Le programme `scoswamp_dhgr import` compile directement les sources portables
`HgrConvert.cpp`, `Cam16.cpp`, `HgrPaintModel.cpp` et `DhgrNtsc8Palette.cpp` de
POM2. Aucun filtre CSS ne remplace la conversion. Les quatre modèles DHGR sont
exposés : anticipation 560 points, blocs 140 pixels, monochrome 560 points,
NTSC à fenêtre de 8 points. La sortie monochrome emploie un aperçu monochrome.
L’aperçu composite couleur utilise le décodeur ColorNTSC du convertisseur ;
il ne simule pas les autres pipelines analogiques OE/AppleWin de POM2.

Le modèle 140 pixels de HgrConvert traite son ajustement comme une grille de
pixels carrés. L’adaptateur de l’atelier ajoute donc les éventuelles bandes
noires dans l’espace visuel 280 × 192 avant la quantification : les pixels
DHGR sont deux fois plus larges. Ce correctif empêche l’aplatissement avec
**Étirer** décoché. Le reste de la quantification reste celui de POM2.

Tous les contrôles de conversion de HGRImport sont présents. Serpentine reste
indisponible, comme dans HGRImport. Les paramètres internes de test
`exhaustiveSearch` et `refinePasses` ne sont pas des contrôles de cette fenêtre.
Le bouton Réinitialiser reprend ses valeurs de tonalité / diffusion, avec le
tramage désactivé conformément au choix du projet, et retire le cadrage.

Un jeton d’aperçu lie les octets convertis au master et à la recette.
L’enregistrement réutilise ces octets et refuse un master ou un fichier final
modifié entre-temps. Les écritures sont atomiques par fichier, avec restauration
si une écriture du groupe échoue. Les aperçus sont temporaires et limités à 48
par session serveur ; les recettes persistantes ne sont pas limitées.

## Réduction par moyenne de zone (`--resample area`)

Par défaut (`bilinear`), le rééchantillonneur de POM2 ne lit que 2 × 2 texels
par cellule DHGR : sur un master de 1 500 px, plus de 99 % des pixels sont
ignorés et le détail fin revient en mouchetis. `--resample area` réduit
d’abord le master à la grille du quantifieur (140 × 192 pour le modèle 140
pixels, 560 × 192 pour les trois autres, 280 × 192 en HGR) par moyenne de zone
exacte, en lumière linéaire, chaque texel pesant au prorata de sa surface
recouverte. Le cadrage, l’ajout des bandes 35:24 et les réglages de tonalité
de la recette restent appliqués comme avant ; le quantifieur est inchangé.

```sh
ADVKIT/TOOLS/build/scoswamp_dhgr convert --resample area N144.png /tmp/N144.RLE.BIN
ADVKIT/TOOLS/build/scoswamp_dhgr import --resample area N144.png dhgr options.txt out.bin c.png m.png
RESAMPLE=area sh SCOSWAMP.MORE/TOOLS/convert_images.sh      # lot, recettes comprises
python3 ADVKIT/image_workshop.py --replay SCOSWAMP N144 --resample area
```

**Le défaut reste `bilinear`**, octet pour octet : les 452 RLE du dépôt
(304 par `convert`, 148 par rejeu de recette) se refabriquent à l’identique
sans l’option. L’atelier web n’expose pas encore ce choix, et une recette ne
l’enregistre pas : `RESAMPLE=area` s’applique à tout le lot. Attention : ce
lot réécrit les `.RLE.BIN`, jamais sans accord.

Mesure du 14 septembre 2026 sur les 452 images, conversions faites par le
binaire, métriques de l’audit (référence : master ramené à 140 × 192 par
moyenne de zone, cadrage de la recette compris) :

| moyenne              | bilinear (jeu) | area   |
|----------------------|---------------:|-------:|
| pixels isolés        | 2,64 %         | 1,70 % |
| SSIM (L\*)           | 0,786          | 0,814  |
| ΔE moyen             | 12,05          | 10,66  |
| ΔE après flou 3 × 3  | 7,97           | 8,21   |
| gris                 | 2,4 %          | 3,2 %  |
| images > 4,5 % isolés | 46            | 4      |

`area` améliore le SSIM de 375 images, les pixels isolés de 419, le ΔE de 429.
Il perd surtout sur les recettes réglées à l’œil pour le bilinéaire (B225 à
B402, N001, N149, N393, N406, N411) : un trait fin clair devient gris au lieu
de rester blanc, et le ΔE après flou monte légèrement. Reconvertir image par
image dans l’atelier avant de généraliser.

## Mesure de qualité et refus des masters

`ADVKIT/TOOLS/image_quality.py` (numpy et Pillow : `/usr/bin/python3` sur
macOS) mesure un master et/ou un `.RLE.BIN` décodé :

- **palette** : % des pixels du master à moins de 10 ΔE (CIELAB) d’une des 16
  couleurs DHGR — ce qui prédit l’erreur de conversion ;
- **isolés** : % des pixels 140 × 192 de la conversion dont les quatre voisins
  ont une autre couleur ;
- **SSIM** de la luminance contre le master ramené à 140 × 192 ;
- **gris** : % des pixels sur les deux gris de la palette ; **ΔE** moyen.

```sh
/usr/bin/python3 ADVKIT/TOOLS/image_quality.py measure --master M.png --rle X.RLE.BIN --recipe R.json
/usr/bin/python3 ADVKIT/TOOLS/image_quality.py worst --count 20 --sort isolated   # tout SCOSWAMP
/usr/bin/python3 ADVKIT/TOOLS/image_quality.py check M.png   # 0 dans les seuils, 1 hors, 2 erreur
```

Sans `--rle`, la conversion est faite par `scoswamp_dhgr convert` dans un
dossier temporaire. `convert_images.sh` imprime, après chaque lot, les 10 pires
conversions du lot (ΔE moyen).

`generate_images.sh` passe chaque master fraîchement généré à `check`. Seuils :
moins de **80 %** des pixels à 10 ΔE de la palette (`IMAGE_MIN_PALETTE`) ou plus
de **4,5 %** de pixels isolés après conversion (`IMAGE_MAX_ISOLATED`). Un master
refusé est déplacé dans `GENERATED/.rejets/` (jamais effacé) et la génération
reprend, `GEN_TRIES` essais en tout (3 par défaut). Si aucun ne passe, le moins
mauvais — plus petit dépassement relatif cumulé — revient à sa place, et la
fin du lot le liste (`GENERATED/.failed/<nom>.hors-seuils`). Un master présent
avant le lancement n’est jamais mesuré ni déplacé ; sous `FORCE=1`, une copie
en est gardée dans `.rejets/<nom>.avant-<date>.png` avant que codex l’écrase.
`GEN_COMMAND` remplace `codex exec` (prompt sur l’entrée standard, destination
dans `GEN_DEST`) : c’est ainsi que les tests simulent la génération.

Ces seuils sont sévères : 203 des 452 masters actuels les dépassent (168 sous
80 % de palette, 44 au-dessus de 4,5 % d’isolés en conversion sans recette).

## Vérification

```sh
python3 ADVKIT/TESTS/test_image_workshop.py
# Avec Chrome headless exposant CDP sur 9228 et le serveur sur 8765 :
node --experimental-websocket ADVKIT/TESTS/test_workshop_browser.mjs
```

```sh
/usr/bin/python3 ADVKIT/TESTS/test_image_quality.py
```

Ce second fichier vérifie, sur des images synthétiques, le décodage RLE (contre
l’aperçu du convertisseur), les mesures, les codes de `check`, `worst`, le
défaut `bilinear` à l’octet, la moyenne de zone, le cadrage conservé en `area`
pour les quatre modèles, et le refus / la relance / la conservation du moins
mauvais dans une copie de `generate_images.sh`.

Six tests natifs couvrent le ratio sur une mire carrée, les quatre modèles,
le cadrage, le HGR, les bornes RLE, les recettes invalides, l’enregistrement et
la reconversion identique sans modification du master. Le test navigateur
utilise une image temporaire N998 et retire ses fichiers ensuite : clics,
glissement du cadre, slider, bouton visible à 1280 × 800, fichier final au bon
endroit, tramage désactivé et retour à une image avec ses réglages.

Mesure locale du 6 septembre 2026 : environ **209 ms** du changement de
luminosité à l’aperçu natif, modèle 140 pixels, master 1514 × 1039 cadré à 2×.
L’attente avant conversion est de 120 ms ; le convertisseur est compilé avec
`-O2` hors Debug. Cette mesure ne garantit pas ce délai pour les modèles 560
points, qui font davantage de calculs.

## Cible des prochaines améliorations DHGR

Choix explicite : **CRT OpenEmulator**, précisé le 6 septembre 2026.
L’optimisation et l’aperçu doivent viser le même pipeline OE et un profil CRT
identifié. L’aperçu ColorNTSC actuel n’est donc pas encore la référence finale.
La sélection Chat Mauve n’est plus une décision préalable à demander.

POM2 dispose déjà d’un démodulateur OE CPU dans `Apple2Display.cpp`, ainsi que
du chemin GPU `NtscPostProcessor.cpp` et des effets du tube dans
`CrtEffectStack.cpp`. La suite consiste à partager / vérifier ce rendu dans
l’atelier, fixer un profil de référence, puis optimiser les motifs DHGR contre
ce rendu et comparer les variantes. La palette à fenêtre de huit points du
convertisseur est un point de départ, pas une preuve d’équivalence avec la
chaîne complète démodulation + CRT. Ces améliorations restent à réaliser.
