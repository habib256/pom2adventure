# Le bassin observé sans boire

La page 031 utilisait `V 364 077 394`. La visite de 394 (observer un lézard
boire) était ainsi assimilée à celle de 077 (boire et récupérer 3 END).
Même une simple entrée puis sortie de 031 suffisait, car V teste aussi
implicitement la page courante. Au retour, 364 affirmait que le joueur avait
bu l'eau guérisseuse et lui interdisait de s'approcher sous une volée de flèches.

Reproduction POM2 avant correction : historique 031/394, retour par 031,
destination constatée 364 au lieu de 394 ; une assertion en échec.

Correction dans les deux langues :

```
VR 364 077 364
VR 394 394
```

Les preuves explicites distinguent boire, observer, et simplement passer.
Après avoir bu, les flèches continuent d'empêcher de reprendre le soin.
Si le joueur n'avait fait qu'observer, il revient à la description paisible
et peut encore boire. Aucun nouvel état sauvegardé et aucun ajout au moteur.

Vérifications :

- `bassin_observe` : boire après observation, +3 END plafonné au maximum,
  sac et sauvegarde sans répétition, priorité de la preuve de consommation,
  passage sans boire ni observer.
- `musique_transitions` : maintien du thème lors des revisites.
- `auberges_solvabilite` et `contrats_soins_or` : contrôles existants des
  paiements, des soins et des restaurations, rejoués sur le disque courant.
- JavaScript : historiques des bassins FR/EN, entrée et restauration.
- Vérificateurs du volume FR/EN et reformatage : aucune anomalie.

Ces scénarios natifs utilisent des états contrôlés, pas des parties complètes.
Le registre d'audit atteint 106 paragraphes revus ; les contrôles mécaniques
portent sur les 842 textes bilingues. Marge mémoire inchangée : 2059 octets.

Attribution : le défaut est établi dans les données de cette adaptation.
Aucune comparaison avec une édition du livre original ne permet ici de
lui attribuer cette erreur.

Le test musical a été adapté : ses fixtures utilisaient auparavant la seule
visite de 031 ou 092 pour provoquer une revisite épuisée. Elles utilisent
maintenant les preuves 077 (eau bue) et 232 (baie cueillie). Le premier passage
a donc échoué sur une attente devenue obsolète, sans panne musicale constatée.

Résultat final : 56 assertions natives réussies, zéro échec après mise à jour
du scénario musical (11 bassin, 4 musique, 24 solvabilité, 17 soins/or).
