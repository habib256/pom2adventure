# Validation de DIAPO

Les campagnes sont terminées avec le code 0.

La campagne complète (`result.json`) lance DIAPO depuis Bitsy Bye uniquement
au clavier, vérifie pause/reprise automatique, puis compare les **453 images**
octet par octet aux 16 Ko décodés dans MAIN et AUX. Elle contrôle aussi le
bouclage et le retour au sélecteur par Échap. Aucune écriture RAM injectée.
Le disque testé porte le SHA-256 `b125c2954c5e049d16d7219c01356c8b08499d3125df9786d6f7a7200f2db5fb`.

La [campagne visuelle finale](../VALIDATION-DIAPO-FINAL/result.json) porte sur
le volume `e0a8891a41f0bcd0c9c7512bd595206130edd1f3def5cee5463f4ba1c5cefc3e`.
Elle contrôle la page de titre anglaise en 80 colonnes, le panneau mixed,
sa disparition après **1,00 seconde** à vitesse 1×, le plein écran, la pause,
la reprise, trois images et la sortie. Ce contrôle de trois images ne vaut
pas une nouvelle comparaison complète des images modifiées depuis la campagne
de 453 images. Les corrections d'images dans l'atelier peuvent changer le HDV.

## Captures finales inspectées

- [Page de titre](../VALIDATION-DIAPO-FINAL/title.png)
- [Première seconde en mixed](../VALIDATION-DIAPO-FINAL/mixed.png)
- [DHGR plein écran](../VALIDATION-DIAPO-FINAL/full.png)

Le pointeur AUX manquait dans l'hôte headless : les premières captures
80 colonnes/DHGR étaient fausses malgré des lectures RAM exactes. Il est
maintenant initialisé dans `pom2_playtest.cpp`. Une reconstruction cohérente
avec le cœur POM2 actuel a aussi été nécessaire pour que les captures reflètent
la transition de mode. Les captures antérieures sont conservées dans les
dossiers V1/V2/VISUEL ; elles ne prouvent pas le rendu final.

## Reproduire

Depuis la racine du dépôt, avec les artefacts du même build :

```sh
sh SCOSWAMP.MORE/TOOLS/build_pom2_playtest.sh
python3 -u DOCS/VALIDATION-DIAPO/validate.py /tmp/diapo-campagne-neuve
python3 -u DOCS/VALIDATION-DIAPO-FINAL/validate.py /tmp/diapo-visuel-neuf
```

Les pilotes exigent un dossier de résultats neuf et capturent le hash de
leur copie du disque au démarrage. Ils utilisent le port 6526, un Apple IIe
Enhanced sans fenêtre et une Mockingboard en slot 2. Le manifeste et les
fichiers RLE source doivent rester stables pendant leur comparaison.

Le rendu capturé ici est celui du banc POM2 ; il ne constitue pas une
validation du rendu CRT OpenEmulator de l'atelier.
