# Baie laissée sur le buisson

Le choix C de 247 propose explicitement de laisser la baie. Pourtant la ligne
`V 108 232 247 389` de 092 considérait la simple visite de 247 comme une
preuve de cueillette. Le retour conduisait à 108 : buisson sans baie.

Reproduction POM2 avant correction : historique 247, retour par 092,
résultat 108 alors que 247 est attendu (une assertion en échec).

La correction FR/EN remplace cette condition par deux règles ordonnées :

```
VR 108 020 232 389 108
VR 247 247
```

Une baie mangée (020), rangée (232), rapportée dans le récit (389), ou un
buisson déjà trouvé vide (108), reste épuisé. Sinon, un buisson vu en 247
reste disponible. La priorité de la première règle empêche de recréer une
baie après sa perte. Aucun bit d'état, code moteur ou format de sauvegarde
supplémentaire. Marge de tas toujours 2065 octets.

Le vérificateur accepte désormais plusieurs règles V/VR consécutives avant
le texte et les effets. Le validateur de reformatage permet qu'une cible VR
soit aussi une preuve : contrairement à V, VR ne teste pas implicitement sa
cible. Les doublons entre preuves restent refusés.

Validation :

- `baie_laissee` dans POM2 headless avec Mockingboard : 18 assertions réussies,
  zéro échec (revisite, repas, cueillette, sac, sauvegarde, épuisement).
- `node tools/test_automatic_returns.mjs` : historiques FR/EN, priorité des
  règles, restauration sans rejouer les règles d'entrée, anciens routeurs.
- Vérificateur FR et EN : 421 pages chacune, aucun lien cassé, aucune page
  inaccessible, disque identique au dépôt.

Le scénario natif utilise des historiques contrôlés ; ce n'est pas une
nouvelle partie gagnante complète. Les restaurations préservent la page
sauvegardée, sans réexécuter VR, conformément au contrat existant du moteur.
