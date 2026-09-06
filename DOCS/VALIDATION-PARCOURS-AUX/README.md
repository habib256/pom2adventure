# Traversées complètes — lecteur musical AUX

Les trois missions ont été rejouées au clavier dans POM2 headless avec
Mockingboard en slot 2. Chaque tentative utilise une copie du volume et un
personnage tiré normalement. Le pilote refuse tout POST hors clavier et toute
écriture RAM. Les fins sont contrôlées par page, texte et absence de choix.

| Mission | Tentative gagnante | Fin | Durée | Touches enregistrées | Preuve |
|---|---:|---:|---:|---:|---|
| gayolard | 1 | 175 | 51.4 s | 119 | [rapport](gayolard-01.json) |
| pompatarte | 1 | 158 | 54.2 s | 124 | [rapport](pompatarte-01.json) |
| stratagus | 1 | 358 | 51.4 s | 117 | [rapport](stratagus-01.json) |

SHA-256 du volume testé : `c0659fae16957ab6a9a647421ac6723ddb92dec8c0f95a1d3ab7037e00b3756c`.
SHA-256 du binaire : `1062369ef37808b7e85a269167c0bc5f9cdba6cefe5b2c16860ac72e197733e4`.

Commande :
```
python3 -u SCOSWAMP.MORE/TOOLS/validate_routes.py --attempts 16 --port 6523 --output DOCS/VALIDATION-PARCOURS-AUX
```

Aucune mort ni erreur de pilote dans cette campagne : trois tentatives,
trois réussites. Ces parcours représentent les trois missions ; ils ne
couvrent pas toutes les branches du livre, tous les jets possibles, la pile
au pic ni la fidélité audio. Le moteur partagé SPACETRIP et les éditeurs
restent des livraisons distinctes, encore incomplètes.
