# Atelier de correction des images

Lancement depuis le dépôt :

```sh
cmake --build SCOSWAMP.MORE/TOOLS/build --target scoswamp_dhgr build_prodos_volume
sh SCOSWAMP.MORE/TOOLS/interpreter/serve.sh 8765
```

Ouvrir `http://127.0.0.1:8765/SCOSWAMP.MORE/TOOLS/interpreter/`.
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

## Vérification

```sh
python3 tools/test_image_workshop.py
# Avec Chrome headless exposant CDP sur 9228 et le serveur sur 8765 :
node --experimental-websocket tools/test_workshop_browser.mjs
```

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
