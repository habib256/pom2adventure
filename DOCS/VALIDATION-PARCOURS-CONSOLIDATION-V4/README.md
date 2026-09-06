# Parcours complets après consolidation — 6 septembre 2026

Trois missions réussies dans POM2 headless avec Mockingboard slot 2, sur des
copies jetables du même volume. Le processus de validation est terminé avec
le code 0. Chaque mission réussit à sa première tentative : aucun échec ni
essai interrompu dans cette campagne.

Le pilote `SCOSWAMP.MORE/TOOLS/validate_routes.py` utilise uniquement le
clavier pour modifier le jeu ; sa classe `KeyboardOnlyPom2` interdit les
écritures RAM et les autres requêtes de mutation. Les états sont lus pour
vérifier les résultats. Les personnages sont créés par le jeu.

| Mission | Fin | Tentative | Durée | Touches consignées | END finale |
|---|---:|---:|---:|---:|---:|
| gayolard | 175 | 1 | 57.6 s | 126 | 9/18 |
| pompatarte | 158 | 1 | 50.0 s | 108 | 16/18 |
| stratagus | 358 | 1 | 48.5 s | 106 | 7/18 |

SHA-256 du HDV testé : `127011da70d48eaabd109e372defd201906f68bc80039624acba0c78c943e0ec`.

Ce hash concorde avec `dist/SCOSWAMP.HDV` au moment de cette consolidation.
La mesure associée est [MEMOIRE-CONSOLIDATION-V4.json](../MEMOIRE-CONSOLIDATION-V4.json).
Les modifications ultérieures du volume nécessitent une nouvelle comparaison.

## Portée des preuves

Chaque fin est vérifiée par son numéro, son texte affiché, l’absence de
choix narratifs et la présence de la Mockingboard. Les captures textuelles
conservent aussi les commandes recommencer/reprendre/quitter. Cela ne teste
pas encore leur activation depuis chacune de ces fins.

Les trois démarrages partagent le même état aléatoire `dad60000` et le même
héros initial : HAB 11, END 18, CHA 10, 20 pièces, Anneau de Cuivre. Ce sont
trois parcours différents, pas trois tirages indépendants ni une mesure du
taux de victoire. La campagne est en français ; elle ne valide pas tous les
embranchements, les sauvegardes ou les combats du corpus.

Les JSON conservent chaque touche, paragraphe et état du héros, les Pierres
choisies et la capture finale ; les fichiers `.log` contiennent les journaux POM2.

## Gayolard

[Rapport complet](gayolard-01.json) · [Journal POM2](gayolard-01.log)

Parcours observé (changements de paragraphe, y compris issues de combat) :

000 → 419 → 001 → 095 → 240 → 205 → 335 → 371 → 009 → 195 → 058 → 398 → 314 → 090 → 370 → 157 → 028 → 362 → 022 → 320 → 119 → 381 → 348 → 204 → 269 → 367 → 304 → 131 → 164 → 410 → 248 → 202 → 014 → 088 → 121 → 275 → 145 → 328 → 244 → 161 → 092 → 068 → 215 → 247 → 232 → 389 → 342 → 300 → 161 → 121 → 338 → 088 → 331 → 112 → 202 → 138 → 101 → 118 → 070 → 110 → 319 → 066 → 147 → 213 → 267 → 386 → 179 → 010 → 227 → 265 → 348 → 279 → 362 → 022 → 090 → 370 → 239 → 314 → 195 → 058 → 208 → 159 → 006 → 175

Pierres choisies : HABILETE × 1, ENDURANCE × 1, FEU × 1, GLACE × 2, BENEDICTION × 1.

## Pompatarte

[Rapport complet](pompatarte-01.json) · [Journal POM2](pompatarte-01.log)

Parcours observé (changements de paragraphe, y compris issues de combat) :

000 → 419 → 001 → 095 → 240 → 205 → 027 → 173 → 009 → 195 → 058 → 398 → 314 → 090 → 370 → 157 → 028 → 362 → 022 → 320 → 368 → 348 → 204 → 269 → 367 → 304 → 131 → 023 → 248 → 202 → 014 → 088 → 121 → 218 → 336 → 085 → 153 → 065 → 163 → 079 → 360 → 214 → 019 → 280 → 078 → 343 → 199 → 019 → 137 → 153 → 218 → 121 → 338 → 088 → 331 → 112 → 202 → 138 → 101 → 118 → 070 → 110 → 319 → 066 → 147 → 106 → 179 → 010 → 227 → 265 → 348 → 279 → 362 → 022 → 090 → 370 → 239 → 314 → 195 → 058 → 208 → 159 → 056 → 158

Pierres choisies : HABILETE × 1, ENDURANCE × 1, FEU × 1, GLACE × 2.

## Stratagus

[Rapport complet](stratagus-01.json) · [Journal POM2](stratagus-01.log)

Parcours observé (changements de paragraphe, y compris issues de combat) :

000 → 419 → 001 → 095 → 240 → 205 → 255 → 040 → 097 → 284 → 156 → 193 → 206 → 009 → 195 → 058 → 398 → 191 → 093 → 154 → 046 → 314 → 195 → 058 → 105 → 390 → 144 → 026 → 354 → 165 → 388 → 167 → 322 → 081 → 187 → 010 → 227 → 320 → 368 → 348 → 204 → 080 → 196 → 367 → 304 → 131 → 288 → 184 → 217 → 250 → 367 → 265 → 348 → 157 → 028 → 362 → 022 → 090 → 370 → 239 → 314 → 195 → 058 → 208 → 159 → 226 → 194 → 207 → 358

Pierres choisies : HABILETE × 1, ENDURANCE × 1, GLACE × 1, FLETRISSURE × 2, MALEDICTION × 1.
