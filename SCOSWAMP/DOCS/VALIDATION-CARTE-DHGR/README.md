# Retour de carte depuis DHGR

Deux défauts reproduits dans POM2 :

1. En DHGR plein, `80STORE` est désactivé pour l'affichage. Le retour de carte
   réécrivait le récit via conio dans cette configuration, perdant une colonne
   sur deux. `render_scene` active désormais 80STORE pendant les écritures puis
   rétablit le plein écran. Les images ne sont ni rechargées ni modifiées.
2. Pendant un combat, la carte laissait le corps du récit vide. La boucle de
   combat ne redessine que le bandeau : elle ne pouvait pas le restaurer.
   La fermeture de carte restaure maintenant la scène avant le mode précédent.

Tests : `carte_retour_dhgr`, `carte_retour_combat`, `video` dans playtest.py.
Le premier compare aussi les captures PPM avant/après en plein et mixed,
avec M et ESC pour fermer. Les textes, les 16384 octets d'image et l'état
du héros sont comparés. Le test combat vérifie le récit et l'absence d'assaut
joué pendant l'affichage de la carte.

Les reproductions initiales ont échoué sur le texte restauré (deux cas en
scène plein écran, deux cas en combat). Les octets DHGR restaient intacts :
ce n'était pas une corruption des fichiers d'images.

Marge de tas après correction : 2051 octets, contre 2065 avant. Le budget
minimal de 2048 et la réserve de pile C de 384 octets sont respectés.

Validation finale : 52 assertions réussies, zéro échec, avec Mockingboard.
Les quatre paires de captures avant/après sont identiques pixel par pixel.
