# DIAPO.SYSTEM et rangement ProDOS

Version finale : lancer TOOLS/DIAPO.SYSTEM depuis Bitsy Bye.

`validate.py` lance une copie du disque dans POM2 headless (IIe Enhanced,
Mockingboard slot 2), port 6526. Il vérifie PLEASE WAIT, les flèches et leurs
boucles aux extrémités, le titre Nxxx en mixed, le maintien des 16 384 octets
de l’image après les menus, le flux musical qui avance en IRQ, STOP et Q.
Le déplacement dans les trois colonnes ne modifie que deux cellules texte ;
le compteur de réaffichages complets reste constant.

Captures finales inspectées : `mixed.png`, `music-columns.png`.
Les titres des 453 images proviennent tous d’une directive T existante.

`tools/test_localized_layout.mjs` utilise le serveur HTTP de l’éditeur :
six catalogues français/anglais identiques dans le dépôt et dans ProDOS,
JSON dans JSON, DIAPO dans TOOLS, SAVE0 à SAVE9 dans SAVE. Aucun recours aux
anciens chemins. `layout.json` contient le résultat.

Vérification du lecteur web : 421 pages FR et 421 pages EN, aucune erreur,
aucun écart disque/dépôt. Tests POM2 `sauvegardes`, `interface`, `anglais` :
34 assertions, zéro échec. Le jeu conserve 2 119 octets de tas (minimum
2 048), 26 octets libres en LOWRAM et 12 en MAPRAM.

`benchmark_startup.py disque.hdv resultat.json` mesure entre Entrée dans
Bitsy Bye et la page de garde, à vitesse POM2 1x. Les mesures avant/après
sont conservées dans les deux fichiers `startup-*.json` ; elles incluent le
lanceur, les lectures ProDOS et la préparation de la page de titre.
L’ancienne version recompte les 453 images et analyse le catalogue musical
caractère par caractère ; la nouvelle lit 2 216 octets de métadonnées binaires.
Le retour à l’image précédente utilise désormais un accès direct au catalogue
binaire (453 enregistrements de 144 octets).
