# Consolidation SCOSWAMP — travail en cours

Objectif autorise : (1) contrats texte/moteur, (2) transitions d'etat,
(3) marge memoire. Ce document suit le travail ouvert ; les anciennes mesures
de l'audit memoire restent historiques jusqu'a regeneration finale.

## Contrainte d'architecture : moteur Apple II partage avec SPACETRIP

Instruction utilisateur ajoutee au goal : tout doit etre le plus data-driven
possible ; le moteur Apple II complet doit pouvoir servir au prochain jeu,
SPACETRIP. Cette exigence s'applique aux trois etapes, pas seulement a l'atelier
JavaScript ou aux outils de fabrication.

Critere de livraison : SCOSWAMP et un parcours representatif de SPACETRIP
doivent fonctionner avec les memes sources du moteur natif, sans branche de
logique C propre a un jeu. Les donnees peuvent etre compilees hors Apple II
pour tenir en memoire ; le format de travail doit rester lisible et validable.

- Dans les donnees du jeu : identification, chemins, langue et textes UI,
  catalogues d'objets et ressources, caracteristiques, conditions, effets,
  objectifs, regles de rencontre, fins et migrations de sauvegardes.
- Dans le moteur : lecture de ces donnees, evaluation de conditions et
  application d'effets generiques, transitions, rendu, entrees clavier,
  sauvegardes, fichiers ProDOS et audio/video Apple II.
- Un effet temporaire de combat doit exprimer une caracteristique, une
  variation et une duree ; il ne doit pas tester une « potion naine » en C.
- Les etats de quete sont des donnees ; la migration d'une sauvegarde ne
  doit pas connaitre Gayolard, Pompatarte, Stratagus ou leurs numeros de pages.
- Les parametres de combat, recompenses, soins et conditions d'acces doivent
  etre declarables sans ajouter un opcode specialise pour chaque evenement.
- Les mesures de memoire doivent separer le cout du moteur, des tables de
  configuration et du contenu resident. La generalisation ne doit pas etre
  obtenue en supprimant des controles ou en reduisant la pile sans mesure.
- Les tests des comportements corriges restent obligatoires pendant la
  generalisation. Ajouter une preuve native POM2 pour SPACETRIP, en preservant
  ses modifications en cours dans le depot.

Dette introduite dans le premier lot, a resorber avant de clore le goal :
`restore_mission()` et sa version JavaScript contiennent des pages propres a
SCOSWAMP ; les enums `OBJ_MISSION_*` et `OBJ_POTION_NAINE` donnent au moteur
une connaissance du scenario ; `EH` et le traitement de `.D` doivent etre
remplaces par des operations parametrees. Les corrections de comportement
restent utiles, mais cette implementation intermediaire n'est pas la cible.

## Livraison suivante demandee : editeurs JavaScript des donnees

Apres la consolidation du moteur partage, ajouter des editeurs utilisables
pour les regles, objets, monstres, personnages, maitres/employeurs, Pierres,
amulettes et les donnees associees. Cette demande fait partie du travail
autorise restant ; ne pas clore le goal apres le seul moteur.

- Les formulaires lisent et ecrivent les sources canoniques compilees pour
  l'Apple II. Ils ne maintiennent pas une seconde definition des regles.
- Les entites ont des identifiants stables ; la modification d'un libelle ne
  change pas leurs references, positions dans les sauvegardes ou conditions.
- Les regles relient conditions, effets et durees ; les entites relient leurs
  caracteristiques, dialogues, images, sons et roles selon le schema partage.
- Les interfaces valident les references et les limites du moteur avant
  export/construction. Montrer les usages d'une entite avant sa suppression.
- Verifier un cycle creation/modification/enregistrement/reouverture puis
  construction et lecture native d'un exemple, pour SCOSWAMP et SPACETRIP.
- Preserver le travail existant de l'atelier et de SPACETRIP ; ces editeurs
  s'integrent a l'interface en place.

## Etape 1 : corrections posees

Source primaire locale : `Defis Fantastiques 08 - Le Marais aux Scorpions.pdf`
a la racine du depot. Extraction de travail : `/tmp/scoswamp-livre.txt`.

| Page | Contrat corrige dans les deux langues |
| --- | --- |
| 049 | La vente de l'anneau rapporte 100 pieces. |
| 056 | `CV 280 158` exige une visite de Courbensaule pour la victoire. |
| 075 | Les Arbres-Epees touches par le Feu combattent avec END 10, et non 12 ; meme portrait et victoire 362. |
| 078 | L'auberge facture une piece, puis rend 2 END. |
| 141 | `PS` rend toutes les Pierres ; les blessures sont gueries. Les autres biens restent acquis. |
| 193 | Les trois caracteristiques reviennent a leur plafond. |
| 228 | Les graines semees sont retirees du sac. |
| 272 | Le retour precipite coute 2 CHANCE. |
| 285 | `EH` divise l'END restante par deux. Pour une valeur impaire, reste arrondi en bas (perte arrondie en haut) : convention du portage, le paragraphe ne tranche pas l'arrondi. |
| 365 | Le sort de Terreur retourne coute 1 HAB. |
| 395 | La chambre coute une piece, en plus de la mauvaise nuit. |

Les choix des pages 074, 119, 130 et 191 avaient des lettres differentes en
FR et EN ; l'ordre anglais suit maintenant le francais, sans changer les issues.

`audit_contracts.py` inventorie les directives des 840 fichiers, compare les
deux langues en ignorant les titres traduits, et exige les contrats explicites
ci-dessus. `CONTRATS-SCOSWAMP.json` contient leurs empreintes. Cela ne constitue
pas une preuve automatique de coherence de toute la prose.

`CV` est recalcule depuis le bitmap des visites deja sauvegarde, sans nouveau
drapeau de Courbensaule. Il conserve un choix visible mais inaccessible lorsque
la condition manque. `PS`, `EH` et `CV` sont egalement implementes dans l'atelier
JavaScript et declares dans son descripteur.

## Validation deja observee

- POM2 headless, Mockingboard : 17 assertions du scenario `contrats_soins_or`
  passees apres introduction de CV (avant introduction de PS/EH).
- Sauvegardes reelles : 13 assertions ; sauvegarde des blessures : 2 ; chargement
  d'un fichier forge : 10, apres la simplification de serialisation ci-dessous.
- Regles C sur machine hote : tout passe.
- Verificateur JavaScript sur le HDV, FR et EN : 420 pages chacune, aucune
  directive incomprise, cible absente, page inaccessible ni divergence disque/source.
- La campagne incluant PS/EH et `contrats_speciaux` doit etre consignée apres sa fin.

Le banc a montre une course d'injection : l'ecran peut etre stable pendant le
fondu musical de 0,9 s, avant que le chargement termine ne remette `restoring`
a zero. Les nouveaux scenarios attendent 24 releves stables avant de poser
un autre etat. Une synchronisation sur l'attente clavier est a etudier a
l'etape 2 ; les essais par injection ne remplacent pas les vraies sauvegardes.

## Economie prealable necessaire aux corrections

Le binaire initial n'avait que 29 octets libres avant la pile. Sur cc65,
les 40 enregistrements de monstres sont deja exactement les 160 octets
little-endian du format SCS4/SCS5. Leur export/import utilise maintenant
`memcpy` ; le chemin hote garde la conversion explicite (int de taille differente).
Gain mesure au lien : 333 octets de marge principale, de 29 a 362 avant les
nouvelles directives. Apres CV/PS/EH : 197 octets libres, pile toujours reservee
a 384 octets. Ce n'est pas encore le chantier memoire de fond.

## Constats au premier audit — historique

Cette liste décrit l'état au premier audit. Les sections suivantes documentent
les corrections de MR (181/306), MF (221), CV composé (363), CT (008/141) et
CG (auberges), désormais vérifiées. Les points encore ouverts sont recensés
dans le bilan de consolidation en fin de document.

- Les retours conditionnels simples sont maintenant corriges : 129 (Ours),
  210 (Bete), 330 (taniere), 331 (Aigle), 342 (Geant), 343 (Brigands), 262
  (Courbensaule). Le cas a trois issues du Patrouilleur, 363, reste a traiter.
- 181/200 : l'Ours deja blesse recupere 1 END, sans depasser son maximum.
- 306/378 : le Patrouilleur retrouve toute son END lors de son retour.
- 221 : la fuite n'est permise qu'apres deux assauts, actuellement disponible avant.
- 289 : ancien tarif d’une demi-piece ; remplace sur instruction utilisateur par une piece entiere le 6 septembre 2026 (voir derniere section).
- Paiements : une bourse vide est bornee a zero, mais le service reste obtenu ;
  verifier les conditions d'acces aux auberges.
- 141 : verifier que l'echange propose au 008 exige encore des Pierres.
- 061 : le saut direct vers la mort du Geant est corrige par la reprise 420
  (validation detaillee ci-dessous). Verifier encore la variante 211.
- Poursuivre l'audit des effets partiels, conditions d'objets, paiements et fins.

## Etapes suivantes

2. Formaliser et tester les entrees de scene, retours de menus, sauvegardes
et chargements : effets uniques, reprises sans reroll, etat de combat, erreurs
de fichiers, compatibilite des formats. Verifier aussi les nouvelles directives
entre C natif et atelier JavaScript.

3. Mesurer le pic des piles (C et processeur), augmenter la marge principale
de facon significative, fixer un budget controle automatiquement, regenerer
les mesures et rejouer les trois missions completes dans POM2 sur le binaire final.

## Mise a jour du premier lot

- Mission explicite dans les bits caches `.G`, `.P`, `.S` : les prologues
  371/173/206 effacent les deux autres missions avant d'affecter la nouvelle.
  Les pages 013, 131, 159, 170, 232, 286, 305 et 328 utilisent ces conditions.
  Les sauvegardes anciennes sans ces bits sont migrees a partir des visites
  (371, puis 173, puis 206 : une reconversion apres Stratagus prime).
- `PX` conserve les drapeaux caches, tout en retirant les objets visibles,
  les Pierres et les amulettes. Le comportement JavaScript suit le natif.
- `CX page destination titre` complete `CV` pour la condition inverse.
  Les deux branches de 056 et 262 sont maintenant exclusives.
- 266 verse 250 pieces pour le lot, quel que soit le nombre d'amulettes,
  et retire toutes les amulettes (`GA 0`, puis `E OR +250`).
- La potion 253 pose `.D`, dernier bit libre du bitmap 16 bits. Elle penalise
  la Force d'Attaque de 1 au prochain combat (HAB effective bornee a zero),
  puis disparait apres victoire, fuite ou mort. Un combat deja termine ne la
  consomme pas. Les soins restent acquis : on ne reinitialise pas l'HAB du
  heros, on retire un modificateur temporaire. La prose FR/EN precise ce sens.
- Message de choix bloque generalise : « Choix indisponible. », y compris
  lorsqu'il s'agit d'une condition de mission plutot que d'une Pierre.
- Le validateur confronte maintenant aussi la table d'opcodes C, son enum
  et le descripteur JavaScript (reconnaissance et statut d'effet d'entree).

Resultats observes sur les versions successives du lot : 51 assertions/5
scenarios pour soins/effets/sauvegardes ; 27 pour les conditions de mission,
3 pour une ancienne SCS4 apres reconversion ; 39 pour les trois prologues et
la fin 158 ; 9 pour le trajet potion 253 -> 088 -> 121 -> 275 -> combat 012
-> 061. Ne pas additionner ces campagnes comme des tests uniques du binaire
final. La campagne `contrats_retours` passe ses 14 assertions dans POM2.

Derniere empreinte principale apres les correctifs : 32 064 octets sur
32 128 ; marge principale 64 octets, LOWBSS 33, MAPBSS 12, LC pleine.
La suppression des initialisations deja garanties par le memset LOWBSS a
rendu 36 octets supplementaires. La pile C reste a 384 octets reserves.
Les analyses MEMOIRE-SCOSWAMP.json et AUDIT-MEMOIRE-SCOSWAMP.md anterieures
ne representent donc pas encore ce nouveau binaire.

## Extraction des migrations vers les donnees

`SCOSWAMP/RULES.json` est maintenant la source de la migration des anciens
etats de quete. `tools/compile_game_rules.py` compile les groupes de drapeaux
et branches de visites en constantes natives (`SRC/game_rules.h`, dependance
du Makefile). `migrate_saved_flags()` applique une table, sans nom d'employeur
ni numero de page dans son code. Les groupes sont independants ; dans chaque
groupe, la premiere visite correspondante prime et un etat explicite existant
est conserve. Le lecteur JavaScript lit le meme fichier via `rulesSource`.

Validation : quatre tests du compilateur ; tests JavaScript avec vocabulaire
independant (equipage/pilote), priorite, groupes multiples, idempotence et
references invalides ; verificateurs FR/EN sur le volume. Le banc natif de
reprise SCS4 et sauvegardes passe ses 16 assertions dans POM2 headless avec
Mockingboard.

Limite explicite du premier compilateur : les masques de migration natifs
sont encore sur 16 bits. SPACETRIP possede deja 17 objets/drapeaux : la capacite
du catalogue doit devenir configurable dans le moteur partage. Les autres
couplages, notamment le modificateur de potion, ne sont pas encore extraits.
Ce lot n'est donc pas une preuve de reutilisation du moteur complet.

Cout de la migration generique mesure au lien : 44 octets supplementaires,
marge principale 20 octets. La pile n'a pas ete reduite. Le prochain travail
doit tenir compte de cette limite ; les chiffres du lot precedent sont historiques.

## Reprise du combat interrompu

Le choix de continuer au 061 conduit desormais au 420, qui declare le meme
Geant (HAB 9, END initiale 12, blessures de 4) sans seuil d'interruption.
La page 366 ne s'ouvre qu'apres les derniers assauts. Les textes FR/EN et
l'image de cette nouvelle page reutilisent les caracteristiques et le visuel
existants du 012.

La memoire des rencontres distingue maintenant une fin de file avec END
positive (interruption) d'une mort (END zero). Un seuil plus bas reprend le
dernier adversaire avec ses blessures ; le meme seuil ne recommence pas le
combat. Cette logique C et JavaScript ne contient ni page ni nom du Geant.

Validation : six assertions passent dans POM2 headless avec Mockingboard,
trajet 275 -> 012 -> 061, sauvegarde et chargement au dialogue, puis 420
(END 6 conservee, blessures de 4) -> 366. Le heros initial est injecte pour
ce test cible : ce n'est pas une traversee naturelle complete du jeu.
Le premier essai sans entree par la clairiere avait une cle de rencontre
artificielle et a ete corrige dans le banc. Les tests de regles C et JavaScript
couvrent aussi seuil, reprise et mort. Les verificateurs FR et EN lisent chacun
421 pages depuis le HDV : aucune cible absente, page inaccessible ou difference
avec les sources. L'audit inventorie 842 fichiers et 25 contrats explicites,
sans erreur ; il ne certifie pas tout le contenu narratif.

La remise a zero de la memoire des monstres par memset compense le cout de
la reprise : gain net de 44 octets par rapport au lot des migrations.
Empreinte principale actuelle 32 064/32 128 octets, soit 64 octets disponibles
($BD40-$BD7F). LOWBSS garde 33 octets, MAPBSS 12, LC aucune marge ; la pile C
reste reservee a 384 octets, sans mesure de son pic a ce stade. Ce gain local
ne remplit pas encore l'objectif d'une marge significative.

## Refus transactionnel des sauvegardes navigateur

`Engine.readSave()` controle le JSON, les champs obligatoires, les tailles
des memoires et les valeurs numeriques avant chargement. Une migration est
preparee sur l'instantane detache avant tout remplacement de l'etat actif.
Le menu utilise le meme lecteur : un emplacement corrompu ne fait plus lever
une exception qui empechait d'afficher ou de quitter la liste.

`node tools/test_browser_saves.mjs` verifie les JSON invalides, les feuilles
incompletes, les tailles et valeurs invalides, une migration impossible,
la conservation de l'etat et du RNG en cas de refus, la sortie du menu et
une reprise valide. Un emplacement invalide apparait actuellement vide ; son
contenu reste conserve tant que le joueur ne sauvegarde pas dessus.

Limites restantes : l'existence effective de la page n'est pas validee (seulement son
intervalle), et le format natif doit recevoir ses propres controles et tests.
Cette validation structurelle ne constitue pas une preuve de validite de
toutes les combinaisons d'etat possibles du jeu.

La reprise navigateur restaure maintenant la langue sauvegardee. Le chargement
asynchrone prepare catalogues, carte et aide avant d'appliquer la langue et
l'instantane ; le menu attend son resultat. Un echec de lecture du catalogue
obligatoire conserve la partie, la langue et le RNG actifs. Le selecteur de
langue suit l'etat restaure. Le meme mecanisme differe l'application lors d'un
changement de langue manuel. Les ressources facultatives (carte/aide) gardent
leur repli existant si elles manquent.

Le banc `test_browser_saves.mjs` passe les reprises FR -> EN et EN -> FR,
verifie les messages effectivement selectionnes et le refus transactionnel
si le catalogue est inaccessible. Le verificateur FR lit toujours les 421
pages du volume sans ecart. Cette campagne concerne le lecteur JavaScript,
pas une nouvelle validation du binaire Apple II.

## Catalogue d'objets editable

`SCOSWAMP/OBJECTS.json` remplace la liste Python comme source des objets et
drapeaux. Chaque entree porte son identifiant stable, son bit explicite, son
statut cache et ses libelles FR/EN. `tools/compile_objects.py` genere les deux
catalogues avec une capacite de backend explicite. Le Makefile depend de cette
source ; `build_objects.py` conserve son ancienne commande comme point d'entree.

Trois tests verifient l'identite octet par octet avec les catalogues existants,
y compris apres inversion des lignes JSON, les references/valeurs invalides,
et un catalogue independant de 17 objets accepte pour un backend 32 bits mais
refuse pour 16. La construction HDV passe sans changement des fichiers OBJ.
Le compilateur exige des bits contigus et des drapeaux apres les objets visibles,
conformement au format actuel. Il ne rend pas encore les enums et regles C
independants du scenario : leur extraction reste necessaire, de meme que les
formulaires JavaScript et leur cycle complet jusqu'a POM2.

## Colonne des Pierres dans le sac

Le message « Aucune Pierre Magique » depend uniquement de l'absence de
Pierres. Les objets visibles et les drapeaux de mission ne le masquent plus ;
les amulettes et objets restent dans la colonne de droite. Le lecteur
JavaScript applique la meme condition. Le test POM2 `sac_sans_pierres` passe
10 assertions : sac vide, mission cachee, objet visible, amulette, conservation
du heros lors de chaque consultation et presence des objets a droite.

La simplification rend 8 octets de code : empreinte principale 32 056/32 128,
marge 72 octets ($BD38-$BD7F), pile C toujours reservee a 384 octets. LOWBSS
33 octets et MAPBSS 12 octets restent inchanges. Le HDV reconstruit contient
1364 fichiers, dont le nouveau catalogue source OBJECTS.json ; le verificateur
FR lit 421 pages sans ecart. Ce gain ne remplace pas la reorganisation memoire
encore demandee.

## Mesure des flux musicaux avant deplacement

`tools/audit_music.py` lit les flux MB1 reels et produit
`DOCS/MUSIQUE-MEMOIRE-SCOSWAMP.json` : tailles, SHA-256, durees en ticks,
comptes d'opcodes et maximum de commandes entre deux delais. Les 45 morceaux
livres passent les controles de format et totalisent 84 883 octets sur disque.
Les tests rejettent notamment voix invalides, indices hors table de notes,
volumes/periodes de bruit hors limites, operandes tronques et absence de END.
Ces controles portent sur les flux statiques, pas sur le rendu audio.

Le plus gros theme actuel est MARAISUD : 2 277 octets sur 2 304 reserves.
La plus grosse surcouche est VICTOIRE : 1 265 sur 1 280 ; COMBAT fait 1 228,
MORT 673. Ajuster les deux capacites a ces maxima ne rendrait que 42 octets,
avant tout cout de code : cette piste ne peut pas satisfaire le gain demande.
La documentation ancienne citant 2 285 octets pour le plus gros theme ne
correspond donc pas au corpus mesure ici.

Le lecteur assembleur fait des lectures indirectes `(cur)` directement dans
le tampon principal pendant l'IRQ ; ses lectures d'en-tete utilisent aussi
la meme banque. Un deplacement AUX doit adapter les deux chemins et garantir
le retour aux soft-switches precedents, y compris pendant les appels ProDOS
et les changements video. Il ne suffit pas de modifier l'adresse du tampon.
La mesure ne pretend pas encore demontrer une implementation AUX ni son gain.

## Sonde native d'acces AUX

Le scenario `aux_music_probe` assemble une sonde 65C02 isolee et l'execute
dans une instance jetable de POM2 headless. Il remplace volontairement le
code/etat du jeu dans cette seule instance. La sonde n'est pas liee au binaire
SCOSWAMP et ne modifie pas la session GUI SPACETRIP.

La routine de lecture est recopiee a la meme adresse en MAIN et AUX. Elle
active RAMRD AUX, lit via un pointeur de page zero, puis remet RAMRD MAIN.
Ainsi les instructions executees pendant la bascule existent dans les deux
banques, sans utiliser de place en Language Card. La sonde remplit AUX
$1000-$1DFF avec un motif dependant de l'adresse et MAIN avec une sentinelle ;
elle controle les 3 584 lectures, la conservation de MAIN et les etats finaux
RAMRD/RAMWRT. Son resultat global $A5 est observe dans POM2 (scenario passe).

Limites importantes : IRQ desactivees, ALTZP principal suppose, entree/sortie
RAMRD et RAMWRT MAIN ; aucune lecture ProDOS simultanee. L'integration doit
reserver l'emplacement miroir, copier les morceaux par un petit tampon,
adapter les lectures d'en-tete et de flux, et tester les interruptions avec
chargements et video. Aucun octet n'a encore ete retire du tampon musical
du jeu : la marge principale reste de 72 octets.

## Integration du lecteur musical AUX

Le binaire utilise maintenant AUX $1000-$1DFF pour les deux flux residents
(2 304 + 1 280 octets). MAIN ne garde qu'une page de transit de 256 octets.
`music_load()` lit le disque par blocs, controle la capacite avant copie et
refuse aussi les erreurs de lecture. Les copies masquent les IRQ pendant leur
courte bascule RAMWRT ; les appels disque gardent leur comportement habituel.
Les deux routines de lecture sont recopiees en AUX a leurs adresses CODE
($9607-$9618 dans ce lien), hors des images DHGR page 1 et des flux. Le
lecteur IRQ reste en MAIN ; seuls ses acces au flux et a l'en-tete basculent.
Le contrat d'entree reste RAMRD/RAMWRT et page zero MAIN, comme le pilote
existant. L'emplacement miroir doit rester reserve lors de la generalisation.

Mesure `MEMOIRE-SCOSWAMP-AUX.json` : binaire disque 31 690 octets, empreinte
principale 28 986/32 128, tas $B13A-$BD7F = **3 142 octets**. Gain net depuis
le lot precedent : **3 070 octets**. La suppression de 3 328 octets de BSS
est compensee partiellement par 258 octets de code/etat supplementaires.
LOWBSS garde 33 octets et MAPBSS 12 ; la pile C reste a 384 octets reserves,
son pic n'est pas encore mesure. Le binaire disque grandit car les donnees
BSS ne sont pas stockees dans le fichier : c'est la RAM occupee qui diminue.

Le controle integral a aussi revele un defaut preexistant : `MU +COMBAT`
etait traite comme un theme de lieu, ecrasant celui du Geant avant l'assaut.
Le chargement distingue maintenant les surcouches : un combat les differe
jusqu'au premier assaut, une autre surcouche demarre a l'entree et conserve
le nom du theme de lieu. Le test attend le premier assaut avant de controler
COMBAT et confirme que GEANT reste intact dans l'autre moitie.

POM2 headless avec Mockingboard : les trois scenarios musique passent 29
assertions, dont les octets complets des flux apres video/chargements/combat,
la lecture qui avance pendant le sac et l'integrite du miroir. Le controle
FR du HDV lit 421 pages sans ecart. Ce lot ne constitue pas encore les trois
traversees gagnantes finales, une mesure du pic de pile ou une comparaison
du rendu audio. La conservation du curseur de zone ne prouve pas encore sa
reprise audible : cette transition doit etre auditee explicitement.

Verification complementaire du binaire AUX : 41 assertions passent dans
POM2 sur sauvegardes, mort dans le sac, video, fin 158 et combat interrompu.

## Correction visuelle demandee : Maitre des Loups

B120 montrait un loup alors que les deux loups du 120 utilisent explicitement
MI 224. Le troisieme adversaire utilise B120 et est le Maitre humain. Le
master PNG a ete regenere avec les references HERO et M_LOUPS, converti en
DHGR RLE et inclus dans dist/SCOSWAMP.HDV. Le generateur de manifestes de
bataille filtre desormais les adversaires selon leur affectation MI ; le
prompt B120 ne demande plus les trois adversaires dans une seule image.
Le rendu DHGR a ete inspecte et le volume reconstruit puis verifie en FR.

## Trois traversees completes sur le volume AUX

La campagne [VALIDATION-PARCOURS-AUX](VALIDATION-PARCOURS-AUX/README.md)
valide Gayolard (175), Pompatarte (158) et Stratagus (358), chacune a sa
premiere tentative, sans mort ni erreur de pilote. POM2 headless utilise la
Mockingboard en slot 2. Les personnages sont tires normalement ; le pilote
refuse toute mutation hors clavier. Les journaux conservent les touches,
les etats observes, les fins et le SHA-256 du volume reellement teste.

Cette preuve porte sur les trois itineraires representatifs du volume actuel
avec lecteur AUX et nouvelle image B120. Elle ne ferme pas les autres
contrats narratifs ouverts, le pic de pile, le moteur partage complet ni les
editeurs demandes. Toute modification ulterieure doit etre distinguee de
ce volume par son empreinte et recevoir les verifications appropriees.

## En-tetes et longueurs des sauvegardes natives

Le chargement refuse maintenant une langue autre que F/E, un numero de page
hors de la capacite du bitmap de visites, un suffixe apres la longueur exacte
et les erreurs de lecture, avant `unpack_save()` et avant mutation du heros.
Le checksum XOR conserve sa fonction de detection partielle ; il n'est pas
presente comme une garantie contre toutes les alterations.

POM2 : 38 assertions passent sur cinq scenarios, dont trois fichiers invalides
(langue Q, page 65535, octet surnumeraire) et les sauvegardes SCS4/SCS5 valides.
Les refus conservent heros, page, visites et rencontres. Le banc peut maintenant
injecter un fichier arbitraire dans une copie jetable du disque avant demarrage.
La verification d'existence effective de la page dans le volume et les autres
invariants internes d'une sauvegarde restent a traiter.

Cout mesure du lot : 97 octets, marge principale 3 045 octets ($B19B-$BD7F),
pile C inchangee. Les trois traversees AUX archivees portent sur le volume
precedent ; cette nouvelle version est couverte ici par les tests de chargement.

## Budget de marge obligatoire

Le Makefile fixe `MIN_FREE = 2048`. `check-memory.sh --min-free` refuse un
binaire dont la marge principale tombe sous cette valeur, en plus des
controles de debordement existants. Il s'agit d'une reserve de developpement
choisie pour proteger le gain AUX, pas d'une mesure des besoins maximaux du
tas ou de la pile. La pile reste explicitement reservee a 384 octets.

Le controle s'execute apres le lien, avec `all`, et avant l'empaquetage HDV,
y compris si le binaire existe deja. Six tests couvrent les bornes memoire
et du budget. Une verification de `make hdv MIN_FREE=5000` echoue avant
l'empaquetage sur le binaire actuel ; `make check` passe avec 3045 octets
pour le seuil normal de 2048. Aucun nouveau binaire n'est produit par ce lot.

## Atelier visuel demandé le 6 septembre 2026

La page principale de l’interface web ouvre désormais la correction d’images.
Catalogue scènes / combats, sélection directe et recherche, cadrage 35:24
(glissement, poignée, zoom et clavier), réglages HGRImport, aperçus natifs,
calque source et masque de la zone de texte. Le lecteur de jeu reste accessible
par « Tester le jeu » / `?mode=jeu`.

Le backend local relie les quatre modèles DHGR et le HGR au convertisseur
portable de POM2. Il conserve les masters, écrit une recette JSON par image et
réapplique cette recette dans la chaîne de conversion. Le bouton final,
toujours visible, génère et enregistre le RLE dans `IMG/N<bucket>/` ; celui de
SPACETRIP conserve son format HGR actuel. La construction des deux HDV est
accessible dans l’atelier. Mode d’emploi et limites :
`SCOSWAMP.MORE/TOOLS/interpreter/IMAGES.md`.

Corrections issues de la relecture humaine : ratio d’affichage du mode blocs
140 pixels (fit POM2 interprétait ses pixels comme carrés), accès direct à la
sélection, bouton final hors de la zone défilante, attente d’aperçu 450 → 120 ms,
optimisation native -O2 et tramage désactivé par défaut / Réinitialiser.
Mesure navigateur : 209 ms réglage → aperçu sur le master B120 cadré, modèle
140 pixels. Six tests natifs passent ; test navigateur avec glissement réel,
recette persistée et fichier DHRR temporaire de 5 287 octets validé. Aucun
master utilisateur n’a été modifié par ces tests.

## Reprise des règles de rencontre : récupération explicite

Nouvelle directive générique d’entrée `MR gain maximum` : soigne uniquement
la créature mémorisée vivante de la zone courante. Elle conserve l’indice dans
la file, ne crée aucune rencontre, ne ressuscite pas les morts et ne dépasse
pas le maximum. Elle est inhibée à la reprise d’une sauvegarde, comme les autres
effets d’entrée. Les versions C et JavaScript ont le même contrat, sans numéro
de page particulier dans leur implémentation.

Données françaises et anglaises : page 181 `MR 1 8` (retour de l’Ours), page 306
`MR 255 10` (récupération complète du Patrouilleur). Le soin est mémorisé avant
le passage au combat et utilise le format de sauvegarde existant.

Validation : tests C, JavaScript (dont données bilingues et garde de reprise),
27 contrats narratifs revus sans erreur, 842 pages FR/EN vérifiées sans ligne
incomprise, cible manquante ou différence entre volume et sources. Dans POM2
headless / Mockingboard, 14 assertions passent sur les deux récupérations et
la reprise du Géant interrompu. Le retour de l’Ours est sauvegardé puis chargé
pour vérifier que son point d’endurance n’est pas accordé une deuxième fois.

Coût natif mesuré : 237 octets ; marge principale désormais 2 808 octets,
BSS $B01A-$B287, tas disponible $B288-$BD7F, réserve de pile C 384 octets.
LOWBSS conserve 33 octets libres et MAPBSS 12. La réserve minimale de 2 048
octets est respectée. Ce lot ne mesure pas encore le pic réel de pile.

Le premier nouveau lot de routes (`VALIDATION-PARCOURS-RENCONTRES`) conserve
cinq morts et une tentative interrompue : quatre tirages 8/14/8 identiques
échouaient au même combat 267, un tirage 8/18/10 à la page 28. Il ne constitue
pas une nouvelle validation complète des victoires. Une sonde séparée
`SONDE-ALEA-RENCONTRES.json` observe quatre états initiaux distincts en variant
l’attente avant le choix de langue : le générateur natif varie effectivement.
Le pilote attend désormais 0,137 × numéro de tentative seconde avant la touche
F, archive l’état du générateur et évite de rejouer une graine déjà essayée
pour cette mission. Aucune écriture mémoire n’est ajoutée ; seul le moment de
l’appui clavier change. Une interruption est explicitement archivée.

## Parité du sac JavaScript pendant le combat

Le lecteur web limitait encore `I` au premier assaut, contrairement au moteur
natif corrigé. L’ouverture est maintenant possible après un jet ; elle conserve
le jet, l’état du générateur et la blessure en attente. La restriction porte
sur l’usage des pierres de caractéristique, pas sur l’ouverture du sac.

Une pierre fatale termine le sac immédiatement après son message : en combat,
retour de mort sans appliquer la blessure suspendue ; hors combat, ouverture
de l’écran de mort. Un soin ne ressuscite plus un personnage. Le menu est
nettoyé par `finally`, y compris en cas d’interruption de la vue. Les jeux sans
feuille de personnage (SPACETRIP) conservent un inventaire accessible malgré
leur endurance initiale nulle.

`lastLoss` cumule maintenant les blessures effectivement appliquées, comme
sur Apple II, au lieu de soustraire l’endurance finale de celle de départ : un
soin entre adversaires ne doit pas annuler des blessures pour une directive DV.
`tools/test_browser_combat_inventory.mjs` vérifie les transitions avec le vrai
moteur et ses dés, l’interdiction sans consommation, les morts dans / hors du
combat, les nettoyages de menus et le cas sans feuille. Les tests de sauvegarde
et de rencontre JavaScript restent verts. Aucun binaire Apple II n’est modifié
par ce lot ; les trois victoires natives après MR sont archivées dans
`VALIDATION-PARCOURS-RENCONTRES-V3/README.md`, chacune après une mort conservée.

## Fuite de la Licorne : deux assauts effectivement résolus

Le paragraphe 221 du livre impose deux assauts avant de pouvoir fuir. La
commande CF existante rendait pourtant la fuite immédiatement accessible.
`MF n` configure désormais un nombre d’assauts à résoudre avant la fuite,
indépendamment de la destination CF. Sans MF, la fuite reste immédiate.
La page 221 porte `MF 2` dans les deux langues. La prose ne prétend plus qu’il
faut nécessairement deux assauts pour tuer la Licorne : un coup chanceux peut
la tuer avant ; l’obligation concerne seulement la fuite.

Le compteur décroît après application de la blessure, ou dès une esquive
(puisqu’elle termine l’assaut sans blessure). Un jet affiché dont la blessure
est encore en attente ne suffit pas. Les touches de fuite prématurées ne
modifient ni les dés, ni le héros, ni le compteur. Les menus le conservent ;
le chargement d’une autre page le réinitialise. Le moteur ne comporte aucun
numéro de paragraphe spécifique pour cette règle. Aucun format de sauvegarde
ne change : la sauvegarde n’est pas proposée au milieu des assauts.

Tests JavaScript : blocage avant engagement et pendant le premier jet,
deux blessures résolues, conservation après le sac, deux esquives, valeur zéro
et relecture structurelle des données FR/EN. POM2 headless / Mockingboard :
11 assertions dédiées à la Licorne, aux dommages et à la remise à zéro sur
l’Ours ; les tests MR et reprise du Géant complètent la non-régression.
L’inventaire des contrats compte maintenant 28 cas explicitement revus.

Coût mesuré : 69 octets, dont un octet d’état. La marge principale est de
2 739 octets ($B2CD-$BD7F), BSS $B05E-$B2CC, avec 384 octets réservés à la pile.
Le seuil de marge de 2 048 octets reste respecté. Les trois victoires archivées
V3 précèdent MF ; elles ne sont pas présentées comme un rejeu de ce binaire.

## Retour au Patrouilleur : choix fondés sur l’historique

Le paragraphe 363 proposait trois réponses librement sélectionnables. La page
378 est l’unique combat contre le Patrouilleur et 219 sa victoire. Les données
FR/EN proposent maintenant une seule issue : absence de combat et de victoire
vers 133 ; victoire 219 vers 234 ; combat 378 sans victoire 219 vers 306.
Ce dernier cas reprend la récupération complète MR déjà implémentée. Dans le
parcours du livre, l’absence de combat correspond au départ en bons termes ;
le moteur ne prétend pas retrouver un dialogue oublié par une sauvegarde
corrompue. Une victoire enregistrée reste prioritaire même si le bit 378 manque.

Extension générique de CV/CX : une liste sans espace de références séparées
par des virgules exige toutes les conditions ; `!page` exige l’absence de
visite. Exemple `CV 378,!219 306 ...`. CX inverse la conjonction entière.
La syntaxe historique à une page conserve exactement son sens. L’évaluation
se fait en lisant la page, y compris lors d’une reprise ; le résultat utilise
le champ d’interdiction existant du choix. Aucun format de sauvegarde ni état
spécifique au Patrouilleur n’est ajouté.

Le validateur vérifie les références, les bornes et la syntaxe des listes.
`tools/test_visited_predicates.mjs` parcourt les 16 combinaisons de quatre
conditions, pour CV et CX, à l’entrée et à la reprise ; il couvre également
l’ancienne syntaxe et les issues FR/EN du Patrouilleur, dont les quatre sorties
de dialogue amical. Le corpus comprend 29 contrats explicitement revus, sans
erreur ; les 842 pages du volume concordent avec les sources.

Coût mesuré : 111 octets de programme, aucun octet d’état supplémentaire.
Marge principale : 2 628 octets ($B33C-$BD7F), BSS $B0CD-$B33B, pile réservée
384 octets. Les résultats POM2 de ce lot portent sur les issues historiques,
leur restauration, la récupération du Patrouilleur et la fuite de la Licorne.


### Échange des dernières Pierres et intégrité du démarrage — 6 septembre 2026

Le choix 008 → 141 accordait une guérison complète même avec un sac sans
Pierres. Les pages FR/EN emploient maintenant `CT 1 15 141` pour l’échange et
`CT 0 0 316` pour déclarer les Pierres épuisées. Le choix d’attaque reste libre.
La page 141 retire toutes les Pierres, soigne jusqu’au total de départ et
conserve les objets ; il s’agit de cette fin de l’aventure, pas d’une preuve
que toutes les fins et tous les paiements du livre sont validés.

`CT min max destination titre` teste le nombre total de Pierres de toutes les
catégories. Les bornes sont comprises entre 0 et 15 ; 15 signifie « quinze ou
plus ». La somme native sature avant toute addition qui dépasserait 15, y
compris avec douze piles de 255 unités. Le prédicat est recalculé à l’affichage
et à la frappe : utiliser la dernière Pierre dans le sac désactive aussitôt
l’échange sans relire la page. Le marqueur 0x7E et l’intervalle occupent les
champs existants de Choice ; aucune donnée de sauvegarde supplémentaire.
CA, qui compte les amulettes, conserve son marqueur distinct 0x7F.

Les tests JavaScript couvrent les bornes, la saturation, les mutations du sac
sur la même page, la restauration, CA et les textes FR/EN. POM2 headless avec
Mockingboard vérifie le refus sans paiement, la consommation de la dernière
Pierre, la sauvegarde/reprise et l’échange de plusieurs piles de 255 Pierres :
17 assertions. Un premier échec de reprise provenait de l’absence d’acquittement
du message de refus dans le pilote ; le test vérifie désormais chaque menu.
Les validateurs lisent 842 pages FR/EN sans erreur ni écart avec le volume ;
le corpus comporte 30 contrats explicitement revus.

Cette extension a exposé une corruption antérieure à la lecture des pages.
Avant correction, le code résident LC différait du binaire sur trois octets,
$D564-$D566, déjà après le démarrage. Les octets de paramètres ProDOS écrits à
`mliparam` recouvraient l’image LC en attente de transfert dans MAIN. Par
exemple, dans la variante diagnostique : source LC $B23F ; $B23F + $0164 =
$B3A3, adresse de `mliparam`. La nouvelle répartition déplaçait les conséquences
sur du code utilisé, avec chute dans le moniteur sur les retours au Patrouilleur
et à l’Ours. Le miroir AUX de lecture musicale était intact.

Le [démarrage cc65](https://github.com/cc65/cc65/blob/master/libsrc/apple2/crt0.s)
appelle `initlib` avant de transférer LC, puis remet BSS à zéro. Des constructeurs
utilisent donc les paramètres MLI alors que leur emplacement BSS contient
encore le code à transférer. `mli_safe.s` fournit l’ABI `callmli` de cc65 2.19,
avec les mêmes protections de $4E/$4F et le même retour d’erreur ; ses 18 octets
de paramètres sont initialisés dans DATA, avant l’image provisoire de LC.
L’objet remplace celui de la bibliothèque au lien. Cela protège ce tampon sans
modifier cc65 installé ni réserver 3 Ko supplémentaires dans MAIN.

Le scénario isolé `lc_integrite` coupe les IRQ, copie le segment LC en MAIN et
compare chaque octet avec l’image source déterminée par les symboles du lien.
Il vérifie aussi l’emplacement de `mliparam` dans DATA. La sonde remplace de la
RAM uniquement dans sa copie jetable du disque et de l’émulateur ; elle n’est
pas un parcours naturel. Les 3 072 octets sont désormais identiques.

Premier lot après correction : musique (15), musique AUX/combat (10), échange
(17), intégrité LC (2 avant ajout du contrôle d’adresse), historique du
Patrouilleur (10), récupération de l’Ours (5) : 59 assertions réussies.
Les validations naturelles V3 archivées précèdent ce binaire ; elles ne sont
pas présentées comme un parcours intégral de cette version.

Mémoire du binaire corrigé : BSS $B154-$B3B1, tas $B3B2-$BD7F, soit 2 510 octets
sous la réserve de pile C de 384 octets. CT coûte 118 octets par rapport au lot
précédent (117 de programme, 1 de BSS). Protéger MLI échange 18 octets de BSS
contre 18 de DATA : aucun coût net dans MAIN. LOWBSS garde 33 octets libres et
MAPBSS 12 ; le seuil de réserve minimale de 2 048 octets passe toujours.

Second lot : suffixe de sauvegarde refusé (5), page invalide (5), langue
invalide (5), sauvegarde/reprise normale (13), intégrité LC avec contrôle
d’adresse (3), fuite différée de la Licorne (11) : 42 assertions réussies.
Total des deux exécutions : 101 assertions, aucun échec ; le scénario LC est
exécuté dans les deux lots. Les suites JavaScript CT et sauvegardes passent.


### Solvabilité des auberges à une pièce — 6 septembre 2026

Les débits de 078 et 395 existaient, mais l’or est borné à zéro : entrer sans
argent accordait les effets de la nuit sans payer. Les trois accès payants
sont désormais conditionnels : 280 → 395, 280 → 078 et 395 → 078. Le tarif
apparaît dans chaque titre. Le paiement reste l’effet d’entrée de la page
cible, avec inhibition habituelle en reprise ; il n’est pas exécuté lors du
simple contrôle du choix.

Directive générique `CG minimum destination titre`, minimum entier 0..255 :
elle exige au moins cette somme d’or. Le solde du héros garde sa capacité
16 bits, donc 256 ou 65 535 pièces satisfont un seuil de 255. L’évaluation est
dynamique, via le marqueur 0x7D du champ object et le seuil dans obj_mode.
Aucune extension de Choice, Character ou de la sauvegarde. Descripteur JS,
interpréteurs natif/JS et validateurs reconnaissent cette règle.

Un défaut de l’outil de repliage a été révélé par le parcours POM2 : il regroupait
les directives avant les choix C, ce qui déplaçait un choix conditionnel et
changeait sa lettre. Le repliage ordinaire conserve désormais l’ordre des
effets et des choix, dont CG, CT, CV/CX, CI/CN, CU/CP, CA, GU et CF. V reste
placé avant le récit comme auparavant. L’option explicite `--derive` conserve
son comportement de génération de règles ; cette garantie porte sur la mise
en forme ordinaire. Deux tests couvrent les mélanges et les pages FR/EN de
l’auberge, avec vérification d’idempotence. Le corpus ne demande aucune
réécriture après cette correction.

Le lecteur d’écran du banc POM2 exigeait deux espaces avant un second choix.
Or un premier titre de 36 caractères laisse un seul espace avant la colonne
40. Le banc lit maintenant les positions natives 0 et 40 ; deux tests couvrent
ce cas et évitent de prendre une mention « B) » dans le titre pour un choix.

Vérification native `auberges_solvabilite` : 16 assertions réussies avec
Mockingboard en headless. Sans or, les deux chambres à une pièce sont refusées
sans soin. Une pièce paie l’Ours Noir mais ne permet plus de payer la Lance
Tordue ; deux pièces permettent les deux nuits, avec solde final zéro et
ENDURANCE 10 → 9 → 11. Le sac puis la sauvegarde/reprise ne rejouent pas le
repos ni le paiement. Les contrôles CT (17) et LC (3) ont également passé sur
ce binaire. Les suites JS vérifient seuils, solde mutable, absence de débit
implicite et textes FR/EN. Les 842 pages du volume concordent avec les sources,
sans erreur structurelle ; 31 contrats sont explicitement revus.

Coût CG mesuré : 136 octets de programme, aucun BSS supplémentaire. La marge
passe de 2 510 à 2 374 octets : BSS $B1DC-$B439, tas $B43A-$BD7F, toujours
384 octets réservés pour la pile C et seuil minimal de 2 048 octets respecté.
L’intégrité de la Language Card reste vérifiée malgré ce nouveau déplacement.

**État historique de ce lot, résolu ensuite :** la demi-pièce de la page 289
n’était pas débitée. L’utilisateur a demandé de remplacer ce tarif par une
pièce entière ; la correction ci-dessous remplace donc la piste d’une
représentation monétaire fractionnaire. Les parcours naturels V3 restent ceux
d’un binaire antérieur.


### Tarif du Cheval Volant porté à une pièce — décision utilisateur

Sur instruction explicite, la chambre de 289 coûte désormais **1 pièce d’or**.
Les textes FR/EN annoncent ce montant et ne présentent plus cette auberge
comme la moins chère des trois. `E OR -1` facture la chambre avant le vol des
deux objets/Pierres et le repos de deux points ; le test de Chance reste en
place. Les accès depuis 280 et 395 emploient `CG 1 289`, tarif affiché.
Aucune fraction ni nouvelle version de sauvegarde n’est nécessaire.

Les trois auberges ayant désormais un prix minimal d’une pièce, 280 propose
également `C 343 Repartir sans passer la nuit`. Un héros sans or ne reste donc
pas bloqué sur trois choix interdits. Les lettres A/B/C des auberges sont
conservées ; le départ occupe D. À l’Ours Noir, sans argent après le paiement,
les deux changements d’auberge sont interdits, tandis que les deux autres
choix restent disponibles.

La suite JS couvre les trois conditions et le départ sans argent en FR/EN.
Les sources et le volume concordent sur les 842 pages, sans erreur de
structure ; le corpus compte 32 contrats explicitement revus. Le binaire
moteur ne change pas : marge principale de 2 374 octets et sauvegardes SCS5.

POM2 headless avec Mockingboard : 24 assertions reussies dans
`auberges_solvabilite`, couvrant les refus sans or, le depart libre, les
paiements successifs, le sac et la reprise, puis le Cheval Volant : une piece
debitee, deux points rendus, deux Pierres volees et Anneau conserve.


### Troc configurable et vérification des prélèvements — 6 septembre 2026

Les critères de TR ne sont plus dupliqués sous forme de masque 0x018C et de
limite 3 dans les deux interpréteurs. `SCOSWAMP/RULES.json`, section `trade`,
définit les clés d’objets acceptés (CH, AI, BJ, CO), l’acceptation des amulettes,
le maximum de trois biens et la catégorie N des Pierres remises. Le compilateur
résout les bits depuis le catalogue d’objets ; le navigateur utilise le même
fichier chargé par le descripteur du projet.

Le comportement actuel reste explicite : les biens acceptés sont prélevés
dans l’ordre du catalogue, objets avant amulettes, puis le joueur choisit une
Pierre de la catégorie autorisée par bien prélevé. L’ordre des clés dans la
liste JSON ne change pas cette priorité. Le lot n’ajoute pas de sélection
manuelle des biens et ne prétend pas terminer l’éditeur de règles ni le
portage du moteur complet vers SPACETRIP.

Le format accepte un maximum entier 0..255, un booléen d’acceptation des
amulettes et une ou deux catégories distinctes parmi N/B/M (limite actuelle
du champ natif). Le compilateur refuse les objets absents/dupliqués, les
paramètres mal typés et les masques au-delà des 16 bits du backend natif.
Un projet sans section trade désactive le prélèvement TR. Les erreurs de
politique JS sont rejetées avant modification du sac. La compilation native
reste requise après modification des critères ; aucune lecture JSON en RAM
Apple II n’est introduite.

Tests : six tests du compilateur, dont des clés et positions d’un autre jeu ;
1 024 combinaisons d’inventaire côté JS couvrent les quatre objets éligibles
et les six amulettes, le plafond, le nombre de biens effectivement retirés et
la conservation de l’Anneau et de la Cape. La même suite vérifie les pages
FR/EN, la reprise, une politique alternative et les configurations invalides.
Ce test à vocabulaire différent prouve la paramétrabilité de cette opération,
pas le fonctionnement du jeu SPACETRIP complet.

POM2 headless avec Mockingboard : `troc_alphonse` passe 20 assertions sur les
cas quatre objets plus une amulette, un objet plus trois amulettes, un seul
objet et aucun bien accepté. Les Pierres déjà possédées sont conservées,
autant de nouvelles Pierres sont remises que de biens pris, et S/L ne rejoue
ni le prélèvement ni le choix des Pierres. `lc_integrite` passe ses trois
assertions. Les 842 pages concordent entre sources et volume ; 33 contrats
sont explicitement revus par l’audit.

Les constantes sont résolues à la compilation, avec élimination des branches
inutiles. Coût net du passage aux données pour SCOSWAMP : zéro octet. BSS
$B1DC-$B439, tas $B43A-$BD7F, marge 2 374 octets ; réserve de pile C 384 octets,
LOWBSS libre 33 octets, MAPBSS libre 12 octets. Sauvegardes SCS5 inchangées.

### Bilan des parcours et mesure consolidée V4 — 6 septembre 2026

La campagne `VALIDATION-PARCOURS-CONSOLIDATION-V4` est terminée, code de
sortie 0 : Gayolard atteint 175, Pompatarte 158, Stratagus 358, chacun à la
première tentative. Les parcours sont joués au clavier dans POM2 headless,
Mockingboard slot 2, sans injection d'état. Le [rapport détaillé](VALIDATION-PARCOURS-CONSOLIDATION-V4/README.md)
contient les itinéraires et les liens vers les preuves brutes. Les trois
héros ont le même tirage initial : cette campagne ne mesure donc pas une
probabilité de succès. Elle ne vérifie pas encore les actions R/L/Q après
chacune des trois fins.

SHA-256 testé et comparé au volume actuel :
`127011da70d48eaabd109e372defd201906f68bc80039624acba0c78c943e0ec`.
La [mesure mémoire V4](MEMOIRE-CONSOLIDATION-V4.json) porte sur ce même
volume : binaire 32 470 octets, CODE 26 693, RODATA 1 999, DATA 219,
BSS 606, LC 3 072. Le tas disponible est $B43A-$BD7F, soit 2 374 octets,
avec 384 octets réservés à la pile C. Le seuil de construction de 2 048
laisse 326 octets de marge supplémentaire. Les segments ONCE et BSS se
recouvrent à des moments distincts ; la taille sur disque ne doit pas être
assimilée à l'occupation permanente en mémoire principale.

Le tour précédent a apporté une vérification ciblée du tarif d'une pièce ;
ce tour clôt l'observation du processus de parcours lancé précédemment et
archive ses résultats. Aucun changement moteur n'a été nécessaire pour ces
victoires.

Travail encore nécessaire avant de déclarer l'objectif atteint :

- Poursuivre l'audit narratif au-delà des 33 contrats explicitement revus,
  notamment la variante du Géant 211 et les effets/conditions non couverts.
- Vérifier les commandes après les fins, les erreurs de sauvegarde restantes
  et les invariants sémantiques des états chargés ; les tests ciblés déjà
  passés ne couvrent pas toutes les transitions.
- Mesurer les pics réels des piles C et processeur. Les 384 octets sont une
  réservation, pas une mesure d'usage maximal.
- Conserver une validation des trois missions après toute prochaine
  modification du binaire. Les gains mémoire déjà obtenus ne dispensent
  pas de vérifier les collisions et les réserves à l'exécution.

### Géant après Pierre de Feu : contrat vérifié — 6 septembre 2026

La variante 211 est maintenant examinée : le choix `CU FEU 211` au 145
consomme une Pierre, puis `M 6 12` déclare le Géant affaibli. L'absence de
`MD` conserve les dégâts de base de 2 définis par `monster_init`, contre 4
explicitement déclarés au combat normal 012. L'absence de `MS` supprime
l'arrêt à mi-ENDURANCE ; l'absence de `CF` interdit la retraite. `MV 366`
conduit à la mort du Géant. Le texte bilingue décrit son affaiblissement et
l'interdiction de retraite, sans imposer de dégâts différents. Aucun
changement narratif ou moteur n'est justifié par cette vérification.

Le nouveau scénario `geant_feu` passe 11 assertions dans POM2 avec
Mockingboard sur le volume V4 : passage 275 → 145, sauvegarde/reprise au
choix magique sans consommation, passage 145 → 211 avec consommation unique,
caractéristiques et dégâts du monstre, absence de fuite, sac sans mutation
du héros/adversaire/RNG, fin au 366 et choix indisponible sans Pierre.

Cette vérification utilise un héros de test injecté (HAB 12, END 60) pour
isoler le contrat et garantir une réserve suffisante pour le combat. Elle
ne constitue pas une nouvelle victoire naturelle. La sauvegarde est testée
au choix des Pierres, pas pendant l'assaut. Le montant des dégâts est lu dans
l'état du monstre ; les jets de dégâts ne font pas l'objet d'une nouvelle
campagne statistique. Les assertions précédentes du combat normal restent
la preuve distincte de l'application des dégâts par le moteur.

Commande : `python3 -u SCOSWAMP.MORE/TOOLS/playtest.py --only geant_feu --port 6526`.
Résultat : 11 assertions, 0 échec, 12,1 secondes, code de sortie 0.
L'audit bilingue compte désormais 35 contrats explicitement revus, 842
scènes, zéro erreur. Binaire et HDV inchangés : la mesure mémoire et les
victoires V4 restent applicables. L'audit des autres contrats et la mesure
des pics des piles restent ouverts.

### Transitions après les trois fins — 6 septembre 2026

Trois scénarios POM2, `fin_transitions_175`, `fin_transitions_158` et
`fin_transitions_358`, vérifient désormais les commandes après chaque fin.
Résultat : 54 assertions, zéro échec, code de sortie 0 ; durées respectives
11,7 / 11,5 / 11,5 secondes, Mockingboard présente dans POM2.

Chaque scénario crée une sauvegarde au 195 avec un héros blessé, 37 pièces,
deux Pierres de Feu, une Cape, la mission Stratagus, des visites et un Ours
blessé mémorisé. Il rejoint ensuite la fin par injection de test et vérifie :

- Q affiche sa confirmation ; N restitue la fin sans mutation d'état.
- L puis ESC restitue la fin sans mutation du héros ni des mémoires.
- L puis 1 reprend le 195 et restaure exactement héros, visites et monstres.
- R revient au 000, invalide le héros et efface visites et monstres.
- La création suivante possède 20 pièces, aucun ancien sort ou amulette et
  seulement l'Anneau de Cuivre initial.
- Recommencer conserve le fichier de sauvegarde : L puis 1 restitue encore
  le héros et les mémoires d'avant la fin.

Le premier passage avait six assertions en échec à cause d'une préparation
incohérente : la visite 206 figurait dans la sauvegarde sans le drapeau de
mission Stratagus. `migrate_saved_flags` rétablissait donc normalement ce
bit au chargement. Le test final utilise une mission cohérente et initialise
une mémoire de monstre non vide afin que sa remise à zéro soit probante.
Aucun changement du moteur n'a été effectué pour faire passer ces tests.

Ces tests structuraux complètent les parcours naturels V4 ; ils ne les
remplacent pas. Ils sont en français et ne vérifient pas encore Q puis O,
la sortie effective vers ProDOS. La validation des pics des piles et les
contrats narratifs restants demeurent ouverts. Binaire et volume inchangés.

### Sortie confirmée vers ProDOS — 6 septembre 2026

La réserve précédente sur Q puis O est levée pour les trois fins en français.
Les scénarios `fin_transitions_175`, `fin_transitions_158` et
`fin_transitions_358` effectuent maintenant cette sortie après leurs contrôles
R/L et d'annulation. Ils reconnaissent le sélecteur Bitsy Bye, le volume
`/SCOSWAMP` et ses commandes `RETURN:SELECT`, à partir de la page texte MAIN
en 40 colonnes. Le décodeur 80 colonnes du jeu ne convient pas après la
sortie : il entrelacerait les nouveaux caractères MAIN avec l'ancien texte
AUX, donnant un faux diagnostic d'affichage corrompu.

Résultat POM2 avec Mockingboard : 63 assertions, zéro échec, code de sortie 0,
durées 14,1 / 14,0 / 14,1 secondes. Ces 63 assertions incluent les 54 du lot
précédent ; il ne faut pas additionner les deux campagnes comme des contrôles
distincts. La sortie est effective vers le sélecteur du système, pas seulement
vers un message « Au revoir ». Le test ne relance pas un programme depuis
Bitsy Bye. Aucun changement du binaire ni du volume n'a été nécessaire.

### Sorts gratuits contre Stratagus corrigés — 6 septembre 2026

Le contrôle des transactions a mené au choix magique 256 : les quatre sorts
étaient déclarés avec C, sans condition ni prélèvement. Un sac vide permettait
donc de maudire Stratagus, de lancer Terreur, Feu ou Illusion. Les paragraphes
274/365/385/351 décrivent pourtant le lancement d'une Pierre.

Les deux langues utilisent désormais CU MALEDICTION 274, CU TERREUR 365,
CU FEU 385 et CU ILLUSION 351. Le choix E vers 057 demeure libre. Cette
correction réutilise la directive générique de consommation : aucune règle
spéciale Stratagus ni modification du moteur n'est ajoutée.

Le scénario POM2 `stratagus_pierres` passe 25 assertions en 26,6 secondes,
code de sortie 0, avec Mockingboard : sans Pierre seul E est disponible ;
pour chacun des quatre sorts, seule la lettre correspondante et E restent
disponibles, une Pierre sur deux est prélevée, le bon paragraphe est atteint,
le sac et la sauvegarde/reprise conservent le résultat sans nouvelle perte.
Le cas Malédiction résout son jet visible avant de tester la conservation.
Il s'agit d'états de test injectés, pas de parcours naturels complets.

Audit : 36 contrats explicitement revus, 842 scènes, zéro erreur. Reflow :
zéro réécriture et zéro problème. Vérificateur JS depuis le volume : 421
pages par langue, aucune cible absente, aucun écart source/HDV.

Le HDV a été régénéré ; son nouveau SHA-256 est
`867a90bf56a4bc94e3445ee57f11ed45c42b358fcaad056e1f19b46c5464334d`.
Le binaire moteur est inchangé (tas libre 2 374 octets). Les parcours naturels
V4 documentent leur ancien hash ; ils n'ont pas été rejoués sur ce nouveau
volume et ne couvrent pas ce choix magique. Leur preuve n'est pas étendue
implicitement à cette correction.

### Extension de l'audit des lancements de sorts — 6 septembre 2026

La recherche des choix C nommant un sort et la lecture de leurs conséquences
ont identifié neuf autres consommations manquantes, corrigées en FR et EN :

| Source | Destination et Pierre désormais exigée/consommée |
|---|---|
| 034 | 237 FLETRISSURE ; 291 FEU ; 356 TERREUR |
| 374 | 299 TERREUR ; 060 ILLUSION ; 160 AMITIE |
| 324 | 383 BENEDICTION |
| 258 | 198 TERREUR ; 127 AMITIE |

Les choix C deviennent CU. Les destinations restent identiques. Les textes
237/291/356, 299/060/160, 383 et 127 décrivent explicitement la Pierre lancée ;
258 appelle « Peur » le sort de Terreur. La bénédiction inefficace du Nain
consomme aussi sa Pierre : revenir au 324 ne permet plus de la relancer
indéfiniment sans coût. GU GR 228, consommation des Graines contre la Bête,
reste distinct. Les choix ouvrant un menu de magie restent gratuits.

POM2 avec Mockingboard : `sorts_consommation`, 49 assertions, zéro échec,
55,5 secondes, code 0. Pour chaque source : choix gratuits disponibles sac
vide ; pour chaque sort : une seule Pierre ouvre la bonne lettre, mène à
la conséquence attendue et est consommée, puis sac et S/L conservent l'état.
Ces cas utilisent une préparation injectée, pas un itinéraire naturel.

JS : `tools/test_spell_choices.mjs` couvre ces quatre pages et le 256 corrigé
précédemment : 152 combinaisons de possession, deux langues et entrée/reprise.
Il vérifie aussi les conditions après changement du sac sans reparsage et
l'absence de consommation lors de l'affichage. Sa première exécution avait
omis le chargement des catalogues ; cette préparation a été corrigée avant
le passage réussi. Le test de consommation effective est celui de POM2.

Audit : 40 contrats explicitement revus, 842 scènes, zéro erreur. Reflow :
zéro réécriture/problème. Les 421 pages par langue lues depuis le HDV
concordent avec les sources. Binaire moteur et tas libre (2 374 octets)
inchangés. HDV régénéré, SHA-256 :
`37b63edd02639758b6b3da3bfac63b53585c91dbbd6a69972bf434f7edc03b10`.
Les parcours naturels sur ce volume restent à exécuter. Cette recherche
textuelle élargit la couverture, sans constituer une preuve exhaustive de
tous les contrats narratifs ou de tous les lancements formulés autrement.

### Validation V5 en cours et nouveaux constats — 6 septembre 2026

La campagne `VALIDATION-PARCOURS-SORTS-V5` rejoue les trois missions sur une
copie figée du HDV après les treize corrections de consommation. Les rapports
JSON de chaque tentative conservent le hash du volume et le tirage initial.
Au présent point d'observation, les trois premières tentatives de Gayolard
sont perdues (267, 028, 028) et la quatrième est active. Aucun résultat final
n'est encore revendiqué ; consulter les rapports et le processus avant de
relancer ou de conclure. Le pilote reste autorisé à aller jusqu'à seize
tentatives par mission.

La recherche complémentaire des destinations décrivant une Pierre lancée a
révélé deux contrats incorrects, encore à corriger :

- 399, C 188 « Aucune de celles-ci » conduit à « Feu inutile » contre la
  Vase, puis au menu 400 ou à la tactique 336. Cela quitte arbitrairement la
  rencontre avec les Orques sans consommation ni lien narratif. La même
  incohérence existe en anglais. Les entrées 035/151/357 vers 399 comportent
  des blessures : y revenir naïvement rejouerait ces pertes.
- 346 annonce qu'un Orque fuit sous Terreur et que deux restent, mais son
  choix conduit au 281, qui déclare encore trois adversaires (6/7, 7/7,
  6/5). Les caractéristiques des deux survivants et la mémoire de rencontre
  doivent rester cohérentes lors de la correction ; changer seulement le
  libellé du choix ne résoudrait pas le contrat.

La mesure `MEMOIRE-SORTS-V5.json` confirme le tas de 2 374 octets.
`EXPERIENCES-MEMOIRE-SORTS-V5.json` conserve six compilations temporaires du
module scoswamp, sans modification ni remplacement du binaire testé :

| Variante | CODE du module | BSS du module | LC du module |
|---|---:|---:|---:|
| Référence -Cl, codesize 100 | 16 519 | 223 | 2 238 |
| codesize 120 | 16 519 | 223 | 2 238 |
| codesize 150 | 16 525 | 223 | 2 238 |
| codesize 200 | 17 539 | 223 | 2 296 |
| Sans -Cl | 16 581 | 12 | 2 229 |
| Tableaux de Pierres en enum 16 bits | 16 543 | 223 | 2 262 |

Augmenter codesize n'offre donc pas ici de gain mémoire. Retirer -Cl échange
les locales statiques contre davantage de pile : le gain apparent de 149
octets sur CODE+BSS principal n'est pas une preuve de marge utilisable et ne
justifie pas ce changement avant mesure des pics. Ces tailles concernent
l'objet compilé, pas un programme complet lié et validé ; aucune de ces
variantes n'est adoptée.

### Contrats des Orques corrigés — 6 septembre 2026

399 propose maintenant C 309 « Renoncer aux Pierres et prendre la fuite »
au lieu de C 188, qui téléportait à la Vase et racontait un sort de Feu jamais
lancé. La fuite était déjà possible aux trois paragraphes d'accès 035/151/357.
Elle rejoint directement les sorties de la clairière et ne repasse pas par
leurs pertes d'ENDURANCE/HABILETE. La lettre D conserve le combat à l'épée.

346 engage désormais deux Orques, puis MV 135 ouvre le butin. Choix de
réalisation explicite : les deux premiers combattants du 281 (HAB/END 6/7 et
7/7) restent, le troisième (6/5) est celui qui fuit. Le texte ne désignait pas
l'individu effrayé ; cette sélection n'est pas présentée comme une donnée
historique du livre. Les deux MI 281 réutilisent l'image existante, MU lance
la musique de combat. Aucune nouvelle page ni extension moteur n'est requise.

`orques_terreur` dans POM2 avec Mockingboard : 12 assertions, zéro échec,
13,1 secondes, code 0. Fuite sans effet, consommation de Terreur, nombre et
caractéristiques des adversaires, conservation par le sac, victoire au 135,
mémoire de deux vaincus, conservation après S/L et absence de second paiement
du butin. La préparation passe par la clairière 309 pour établir la clé de
rencontre ; le héros de test a HAB 12 et END 60. Cette campagne ne mesure
pas le taux de victoire ni toutes les revisites possibles.

Le test JS couvre désormais 168 combinaisons d'inventaire en FR/EN et les
deux combattants de 346 avec leurs images. Audit : 42 contrats, 842 scènes,
zéro erreur ; reflow sans problème ; volume et sources concordants dans les
deux langues. Le moteur et le tas libre de 2 374 octets sont inchangés.
Nouveau HDV : `5064f2f61c624f96c25f64c79d9729a5f9c0400d694146bb69a6a66b6e37644a`.
La campagne naturelle V5 en cours conserve sa copie antérieure à ce lot ;
elle ne sera pas présentée comme une validation de ce nouveau hash.

### Biens payables et réutilisation de la RAM au démarrage — 6 septembre 2026

Au 128, les deux choix inconditionnels permettaient de prétendre n'avoir que
l'Anneau malgré un sac rempli, ou de payer sans rien posséder. La directive
partagée CB 0|1 destination titre teste maintenant l'absence/présence d'au
moins un bien que PO pourrait prélever : Pierre, objet visible hors Anneau,
ou amulette. L'or et les drapeaux narratifs sont exclus. La condition est
réévaluée depuis l'état du sac, sans prélèvement implicite. 128 utilise CB 0
180 et CB 1 407 ; 407 garde PO. Le texte du 180 couvre aussi un sac entièrement
vide, sans faire apparaître un Anneau absent. Les lettres A/B sont conservées.

L'implémentation native partage le masque STEALABLE avec lose_items et la
boucle de comptage des Pierres avec CT. Côté JS, hasPayableItem concorde avec
loseItems sur 262 144 inventaires ; le test couvre aussi FR/EN, reprise et
modification du sac sans reparsage. Reflow reconnaît CB, contrôle sa valeur
0/1 et sa destination. Le descripteur de l'éditeur et l'audit connaissent
cette directive. Le corpus atteint 45 contrats explicitement revus.

La première compilation a exposé une contrainte distincte du tas : le
binaire flat dépassait la fenêtre de chargement MAIN de 86 octets, puis de
72 après mutualisation du code. Avant CB, cette fenêtre ne conservait que
42 octets, alors que le tas après démarrage en conservait 2 374. Augmenter
le plafond au-delà de $BF00 aurait écrasé la page système ProDOS.

Sur instruction utilisateur d'exploiter la RAM disponible, le chargement
réutilise maintenant temporellement la RAM basse :

| Moment | MAIN $1000-$1BFF | MAIN $4000 et suivantes | LC banque 2 $D400-$DFFF |
|---|---|---|---|
| Lanceur | Préfixe LC de 3 072 octets | Reste du binaire | Pas encore installé |
| crt0 | Source temporaire de la copie | Code et constructeurs | Copie du préfixe |
| main et jeu | LOWBSS : état et tampons | Code, données, tas, pile | Code exécutable résident |

scoswamp.cfg écrit d'abord LCIMAGE, taille fixe $0C00 avec remplissage, puis
MAIN. loader.c lit ce préfixe à $1000, puis le reste à $4000 et saute à $4000.
Le nouveau crt0.s reprend exactement la version officielle cc65 V2.19 et
remplace la source de copie __ONCE_LOAD__+__ONCE_SIZE__ par
__LCIMAGE_START__. Une première source locale d'une autre version a été
écartée après incompatibilité des exports ; la version retenue correspond
à la bibliothèque installée. Provenance :
https://github.com/cc65/cc65/blob/V2.19/libsrc/apple2/crt0.s

La copie précède l'initialisation LOWBSS ; les tampons n'écrasent donc le
préfixe qu'après son transfert. Le lanceur vit à $2000, le tampon ProDOS
reste à $0800. HGR/DHGR, la RAM AUX de la musique et la page système ProDOS
ne changent pas. mli_safe reste en place. Le fichier SCOSWAMP devient une
image à chargement séparé et exige le lanceur SYSTEM associé : ce n'est plus
un binaire flat à BRUN directement.

Mesure finale dans MEMOIRE-LC-STAGE.json : fichier 32 584 octets dont 3 072
pour LC, chargement MAIN $4000-$B347, marge jusqu'à $BF00 de 3 000 octets.
Le placement retire 3 072 octets de cette fenêtre ; après les 114 octets
ajoutés par CB, le gain net face à l'ancien binaire est 2 958 octets. Le tas
en jeu est distinct : $B4AC-$BD7F, 2 260 octets, réserve pile C de 384 octets.
Aucun agrandissement fictif du tas ni du plafond système n'est revendiqué.
Les pics réels des piles restent à mesurer.

Validation POM2 avec Mockingboard : première campagne, sortie/reprise après
175 (21 assertions) et musique (4) passent ; LC (3) passe après adaptation
du contrôle au préfixe. Le scénario Brigands avait un acquittement de Pierre
manquant dans le test. Après ajout de la touche de continuation : campagne
finale de 50 assertions, zéro échec, code 0 — sac en combat 26, LC 3,
Brigands 21. Ne pas compter la répétition LC comme une preuve différente.
Les 3 072 octets exécutables sont comparés au préfixe du fichier, pas seulement
un écran de démarrage. Les 842 pages FR/EN concordent entre sources et HDV.

La campagne naturelle VALIDATION-PARCOURS-LC-STAGE-V6 est lancée sur le
nouveau volume, avec seize tentatives maximales par mission. Son processus
est actif au présent point d'observation ; aucun résultat final n'est encore
revendiqué. Reprendre son observation avant toute relance.

### Contrôle automatique du chargement séparé — 6 septembre 2026

`tools/check_lc_layout.py` est exécuté après liaison et par `make check`.
Il compare les symboles ld65 au lanceur : préfixe à l'offset fichier zéro,
adresse et taille LC identiques, offset MAIN égal à la taille du préfixe,
point de chargement MAIN cohérent, longueur totale du fichier conforme.
Il refuse un chevauchement de la zone temporaire avec les tampons ProDOS ou
le lanceur à $2000, une sortie de la fenêtre LC $D400-$DFFF, ou un chargement
MAIN qui dépasse $BF00. Le remplissage du préfixe reste valide si le code LC
rétrécit : sa taille physique reste fixe pour le lecteur du lanceur.

Cinq tests de ce contrat couvrent le cas valide avec remplissage, des
constantes de lanceur divergentes, les offsets/longueurs incorrects, un
chevauchement déclaré simultanément des deux côtés et les dépassements LC
ou système. Avec les six tests existants du budget mémoire : 11 tests,
zéro échec. `make -C SCOSWAMP/SRC check` passe sur les artefacts réels.
La première invocation du contrôle a révélé une résolution incorrecte de
`--src .` ; le chemin est maintenant résolu avant recherche du binaire.
Ces contrôles de construction n'ajoutent aucun octet au jeu et ne changent
pas le volume en cours de validation V6.

### Campagne V6 terminée

Les trois missions atteignent leurs fins sur le volume du chargement LC en
RAM basse : Gayolard au sixième essai, Pompatarte et Stratagus au premier.
Cinq morts de Gayolard sont conservées. Processus terminé, code 0 ; le hash
des huit rapports concorde avec le HDV actuel. Voir le [rapport V6](VALIDATION-PARCOURS-LC-STAGE-V6/README.md).
Les contrôles de construction ajoutés durant la campagne ne modifient ni
le moteur ni le volume. Les contrats non revus et les pics réels des piles
restent à vérifier avant de déclarer la consolidation achevée.

### Première mesure des piles dans l'émulateur — 6 septembre 2026

Une copie instrumentée de POM2, construite sous /tmp, observe le processeur
sans modifier le jeu, le volume ou l'émulateur installé. Les cinq scénarios
(démarrage, sac en combat, musique AUX, troc et transitions de fin 175)
passent 95 assertions. Le processus de mesure est terminé avec le code 0.
Les traces et leur provenance sont dans [PROFIL-PILES-V1](PROFIL-PILES-V1/README.md).

Pile 6502 : maximum observé de 59 octets, SP=$C4, sur ces exécutions après
l'entrée de main et avant exit. Le lanceur et les constructeurs sont exclus.
La sonde observe les instructions et les empilements, y compris les appels
système et interruptions pendant cette période.

Pile C : maximum de 82 octets aux appels JSR observés dans MAIN, SP=$BEAE.
Ce n'est pas le pic exact : les allocations entre appels et les appels issus
de LC ne sont pas entièrement couverts. La réserve de 384 octets est donc
maintenue. Lire naïvement $80/$81 à chaque instruction risquerait d'interpréter
une mise à jour partielle du pointeur comme une profondeur réelle.

Étape suivante : compléter cette mesure C et couvrir la période de démarrage
avant toute réaffectation fondée sur les réserves de piles. Les observations
actuelles ne suffisent pas à déclarer toute la mémoire Apple II exploitée,
ni la consolidation complète. Le volume testé par V6 reste inchangé.

### Pointeur C suivi instruction par instruction — campagne V2

Le [profil V2](PROFIL-PILES-V2/README.md) remplace l'échantillonnage des appels
par la trace complète des changements de `$80/$81`. Les 178 101 changements
des cinq scénarios sont continus. L'analyse du binaire prouve que leur minimum
est atteint après une décrémentation complète : pic C de 82 octets, exact
pour ces exécutions. Le suivi commence après l'initialisation C et inclut les
constructeurs ; le lanceur SYSTEM et les destructeurs restent exclus.

La campagne a été rejouée avec l'hôte réellement headless `pom2_playtest`,
Mockingboard slot 2 : 95 assertions, aucun échec, processus terminé code 0.
Son maximum matériel est 58 octets. Le premier essai V2 utilisait par erreur
l'exécutable graphique via API ; ses traces sont conservées séparément et
ne servent pas de preuve headless. Les réserves du jeu et le HDV sont inchangés.

La marge observée de 302 octets sur la pile C ne justifie pas à elle seule
une réduction de réserve. Elle permet maintenant de comparer une expérience
de déplacement de locales statiques vers la pile, à couverture identique,
avant de l'élargir aux parcours complets. Les contrats narratifs non audités
et les transitions non couvertes restent dans l'objectif de consolidation.

### Rencontre 355 : interdiction de magie explicite

Les deux textes disent que les Coupeurs de Bourses ne laissent pas le temps
d'utiliser la magie. Le sac autorisait pourtant les Pierres avant le premier
assaut et les Pierres non caractéristiques après celui-ci. `MM 1` exprime
maintenant cette règle dans les données de la rencontre, en FR et EN.
`MM 0` (défaut à chaque entrée de scène) conserve les règles ordinaires.
Le sac reste consultable ; les tentatives interdites ne consomment ni Pierre,
ni effet, ni aléatoire. Les amulettes déjà équipées ne sont pas désactivées.

Le moteur C et l'interpréteur JavaScript appliquent la même restriction.
La directive est structurelle : elle est relue à la restauration sans devenir
un effet unique ni ajouter un champ à la sauvegarde. Le test POM2 headless
`combat_sans_magie` passe 9 assertions, avant/après assaut et au combat suivant.
Les tests JavaScript couvrent les 12 Pierres et l'ouverture du sac avant
l'assaut. L'audit compte maintenant 46 contrats revus et 842 textes vérifiés,
sans erreur ; ce total n'est toujours pas une preuve de tous les contrats.

Le coût mesuré est 88 octets chargés et 1 octet de BSS supplémentaires :
tas 2 171 octets, marge de chargement 2 912 octets. Voir
[MEMOIRE-MM.json](MEMOIRE-MM.json). Les traces des piles V2 portent sur le
binaire précédent ; leurs adresses ne s'appliquent pas à ce nouveau lien.

### DIAPO et outil de validation vidéo

DIAPO est un programme ProDOS SYS distinct, sélectionnable dans Bitsy Bye.
Il partage le lanceur, le décodeur DHGR et les bascules vidéo du jeu, et lit
un catalogue généré depuis tous les fichiers d'images. Il n'augmente pas la
mémoire résidente de SCOSWAMP. Voir le [mode d'emploi](../SCOSWAMP/DOCS/DIAPO.md)
et les [preuves de validation](VALIDATION-DIAPO/README.md).

L'examen visuel a également révélé que l'hôte `pom2_playtest` ne raccordait
pas la RAM AUX à `Apple2Display`. Les lectures mémoire restaient correctes,
mais ses captures 80 colonnes/DHGR étaient fausses. L'hôte initialise désormais
ce pointeur comme le fait l'application graphique POM2.

### Rencontre 215 : seconde interdiction de magie explicite

Les Loups annoncent également « Pas le temps pour la magie » / « No time
for magic », mais leur scène n'appliquait pas la restriction. `MM 1` est
maintenant présent dans les deux langues. Aucun code ni état supplémentaire :
le binaire reste identique, avec 2 171 octets de tas et 2 912 au chargement.

Le scénario `combat_sans_magie` couvre désormais 215 et 355 : 18 assertions
réussies dans POM2 headless avec Mockingboard slot 2, avant et après le premier
assaut, sans consommation de Pierre, effet ou RNG lors des refus. Il vérifie
aussi que le combat suivant réautorise une Pierre avant son premier assaut.
Voir [VALIDATION-LOUPS-MM.json](VALIDATION-LOUPS-MM.json).

Le test JavaScript lit les deux scènes en FR/EN, en entrée initiale comme en
restauration, et vérifie `MM 0`. Il contrôle également l'absence de fuite.
L'auditeur impose désormais l'absence de `CF` dans ces deux rencontres,
en plus de leurs directives requises : 47 contrats revus, 842 textes,
aucune erreur ([CONTRATS-LOUPS-MM.json](CONTRATS-LOUPS-MM.json)). Les contrôles
de reflow et de concordance entre dépôt et HDV passent dans les deux langues.

### Malédiction du Maître des Araignées : 074 → 261 → 354

Ce parcours a été vérifié sans changement du moteur ni des textes. Le choix
exige une Pierre de Malédiction et la consomme une seule fois. Le dé de la
page 261 attend sa validation, inflige entre 1 et 6 points d'ENDURANCE, puis
laisse combattre une Araignée HAB 8 / END 9. La touche de fuite n'a aucun
effet ; ouvrir et refermer le sac ne rejoue ni le dé ni son coût.

La victoire atteint 354 et donne précisément le bit Amulette Araignée.
Sauvegarder/reprendre avant le choix magique ou après le butin conserve les
caractéristiques et l'inventaire. Avec un seul point d'ENDURANCE, la blessure
de Malédiction ouvre l'écran de mort avant tout assaut ; l'Araignée conserve
ses 9 points. Le test POM2 headless avec Mockingboard passe 15 assertions,
processus terminé code 0 ([rapport](VALIDATION-ARAIGNEE.json)).

Le premier essai échouait uniquement parce que le test cherchait « MORT »
dans un écran qui dit « Votre ENDURANCE est tombée à zéro ». Le libellé
a été corrigé et l'absence de coup porté avant cette mort vérifiée explicitement.
Le test JavaScript lit les trois scènes en FR/EN et contrôle notamment que
la restauration ne reprogramme pas le dé et ne redonne pas l'amulette.

L'audit fixe aussi l'absence de `CF` en 261 et compte désormais 50 pages à
contrats explicitement revus ([inventaire](CONTRATS-ARAIGNEE.json)). Les voies
Feu et Amitié de 074 n'ont pas été parcourues par ce scénario ; leur présence
dans les choix contrôlés ne vaut pas une validation de leurs conséquences.

### Retour du choix magique : faux incendie corrigé

La poursuite de l'audit Feu/Amitié a révélé un bug distinct :
144 → 074 → « faire un autre choix » renvoyait à 345 et retirait un point
d'ENDURANCE, même sans avoir utilisé de Pierre ni combattu. La reproduction
POM2 donnait 345 au lieu de 144, et 23 points au lieu de 24. La ligne
`V 345 165 354` assimilait la visite de 144 (ou des chemins 165) à la mort
du Maître et à l'incendie.

La directive réutilisable `VR cible preuves...` teste uniquement les pages
explicitement listées : si au moins une a été visitée, elle redirige vers la
cible. Ni la page courante ni la cible ne sont testées implicitement. La
scène 144 utilise `VR 345 113 354` : le Feu ou la prise de l'amulette après
victoire déclenchent réellement l'incendie. Comme `V`, `VR` ne rejoue pas
lors de la restauration de la scène sauvegardée. Le comportement historique
de `V` reste inchangé pour les autres rencontres.

Les trois scénarios Araignées passent 41 assertions dans POM2 headless avec
Mockingboard : annulation sans blessure, reprise du Maître vivant, preuves
de l'incendie, reprise sans seconde brûlure, Feu coûtant une Pierre et trois
points sans amulette, sortie 165, Amitié terminant l'aventure avec possibilité
de recommencer, et non-régression de la Malédiction. Voir le
[rapport natif](VALIDATION-ARAIGNEE-VR.json).

Le JavaScript vérifie 32 historiques de visite × deux langues × deux modes
d'entrée/restauration, plus le comportement historique de `V`. Les effets
Feu/Amitié sont également vérifiés en FR/EN à l'entrée et à la restauration.
Reflow et vérificateur de graphe reconnaissent maintenant `VR` ; les pages
preuves sont des références à valider, pas des destinations de navigation.
Les 842 textes et les 54 pages à contrats revus passent l'audit
([inventaire](CONTRATS-ARAIGNEE-VR.json)).

Coût natif mesuré : +104 octets chargés, aucune nouvelle BSS, aucun champ de
sauvegarde. Le tas passe de 2 171 à 2 067 octets ; le seuil imposé de 2 048
reste satisfait avec 19 octets d'écart. La marge au chargement est 2 808
octets ([MEMOIRE-VR.json](MEMOIRE-VR.json)). Ces chiffres appellent une nouvelle
optimisation avant d'accumuler d'autres directives ; aucune réserve de pile
n'a été réduite pour faire tenir ce correctif.

### Mutualisation des règles V et VR : 64 octets récupérés

Les deux directives partagent maintenant la lecture de la liste des pages
et l'application du détour. `V` ajoute ses tests implicites de page courante
et de cible ; `VR` continue à tester exclusivement les pages explicites.
Le test de la cible de `V` se fait désormais avant la liste : tous ces tests
lisent simplement le bitmap, sans effet de bord, et la destination est unique.

Le lien mesure −68 octets de CODE et +4 octets de RODATA, soit **64 octets
nets récupérés**. Aucune BSS, aucun format de sauvegarde ni réserve de pile
ne change. Binaire : 32 712 octets, marge de chargement 2 872 octets,
tas `$B52D–$BD7F` de **2 131 octets**, soit 83 au-dessus du seuil imposé.
Le coût net de `VR` par rapport à l'état précédent son introduction n'est
donc plus 104 mais 40 octets. Voir [mesures](MEMOIRE-REVISITES-PARTAGEES.json).

POM2 headless avec Mockingboard passe 26 assertions : `V` à la première
visite, par la même porte, par une page sœur, par sa cible seule et à la
restauration ; `VR` avec les événements incendiaires et les visites
insuffisantes ; musique aux revisites et à la reprise. Le test JavaScript
des historiques et l'audit des 842 textes passent également. Le processus
est terminé code 0 ([rapport](VALIDATION-REVISITES-PARTAGEES.json)). Ce lot ne
remplace pas une nouvelle campagne complète des trois missions gagnantes.


### Maître des Jardins : récompenses et effets uniques vérifiés

Audit narratif des 17 pages de cette rencontre, avec contrats explicites
ajoutés au vérificateur : voies des trois employeurs, dialogue, sorts,
récompenses, combat et amulette. Les pages 117 (Amitié) et 292 (Vérité)
reprennent l’amulette prêtée : aucune directive G ne doit la conserver.
Les pages 283 et 396 donnent chacune une Pierre bénéfique ; 264 inflige
2 points d’ENDURANCE avant 379, qui retire 3 HABILETÉ. La victoire 251 donne
FLEUR et retire 3 CHANCE. Aucun nouveau défaut du moteur n’a été établi
sur ces contrats ; aucune mécanique n’a été modifiée pour ce lot.

POM2 headless avec Mockingboard : **23 assertions, zéro échec**, incluant
l’enregistrement et le rechargement après les deux récompenses, l’Amitié,
la brûlure et le butin. Les récompenses ne sont pas redonnées, les coûts
ne sont pas rejoués. Le test JavaScript vérifie les sept pages d’effets en
FR/EN, à l’entrée et à la restauration. Voir
[validation](VALIDATION-JARDINS.json) et [contrats](CONTRATS-JARDINS.json).
Le contrôle statique porte désormais sur **71 pages explicitement revues**,
avec 842 textes FR/EN et zéro erreur. Il ne prouve pas que les autres
contrats narratifs sont corrects.

Limites : le test utilise des entrées de scènes préparées ; il ne remplace
ni un trajet naturel complet ni la résolution du combat 379 jusqu’à 251.
Les choix des employeurs et les revisites ont été relus et contrôlés dans
les directives, mais ce nouveau scénario ne traverse pas toutes leurs
combinaisons. Le chantier global reste ouvert.


### Jardins : duel abouti et retours par les chemins

Le nouveau scénario `jardins_parcours` ferme deux limites de la validation
précédente. Depuis 305 avec un héros préparé aux valeurs normales (HAB 12,
END 24, CHANCE 10, mission Stratagus), il traverse 334 puis 379. Le combat
est résolu avec les touches Espace, sans forcer la mort de l’adversaire ni
l’entrée dans la page de butin : victoire 251, FLEUR et CHANCE 7. Le passage
par le sac ne rejoue pas le sort initial (-3 HAB), et sauver/recharger la
victoire ne rejoue ni amulette ni pénalité.

La seconde traversée prend la fuite depuis 379 : aucune amulette et CHANCE
10 conservée. Les deux voies empruntent ensuite 363 → 133 → 234 → 305,
la revisite redirigeant vers la clairière déserte 238, sans autre mutation
du héros. **25 assertions, zéro échec** dans POM2 headless avec Mockingboard
([résultat](VALIDATION-JARDINS-PARCOURS.json)). Aucun correctif moteur
supplémentaire n’a été nécessaire. Ce sont des parcours locaux avec entrée
préparée à 305, pas des parties complètes depuis la création du personnage.


### Retours automatiques : le joueur ne confirme plus l’historique

À la demande du joueur ayant remporté Gayolard, les retours 129, 210, 330,
331, 342, 343 et 363 portent désormais `AC`. Cette directive structurelle
fait suivre automatiquement le premier CV/CX satisfait par les visites.
Les questions « avez-vous tué / fui / rencontré ? » ne sont plus affichées.
Les vrais choix de sentier restent interactifs. Les règles vivent dans les
textes FR/EN, sans table de numéros de pages dans le moteur. AC est aussi
interprété lors de la restauration : une ancienne sauvegarde placée sur
l’écran de question rejoint la bonne issue, sans rester sur un écran vide.
Le moteur JavaScript partage ce comportement et son vérificateur conserve
toutes les arêtes CV/CX, même celles court-circuitées lors d’une lecture.

La page 073 reproduisait aussi sa Chaîne d’Or après une visite antérieure,
avec un nouveau test de Chance. POM2 confirmait qu’elle restait en 073 au
lieu de rejoindre 202. `VR 202 073` protège désormais la fouille unique :
première prise et test de Chance conservés, reprise de sauvegarde inchangée,
mais une chaîne perdue ne réapparaît pas dans le nid vide.

81 assertions natives passent sur six scénarios, dont les deux issues du
Patrouilleur à la restauration et le combat Jardins joué jusqu’à la fin.
Le JavaScript vérifie les branches FR/EN et la restauration ; les 842 pages
passent le vérificateur sans cible absente ni écart avec le disque. Le coût
natif est 58 octets, sans BSS ajoutée : tas 2 061 octets, 13 au-dessus du
seuil imposé. Aucun budget de pile n’a été réduit. Voir
[preuves ciblées](VALIDATION-RETOURS-AUTO.json).

Le signalement des tests de Chance reste à traiter : quatre pages utilisent
CE (058, 073, 190, 249), qui effectue actuellement son jet pendant l’analyse,
sans l’écran de dés des tests CL. Le cas précis vécu par le joueur a été
demandé ; ce constat technique ne présume pas qu’il explique tous les défauts
qu’il a observés. La campagne des trois missions est conservée dans
VALIDATION-RETOURS-AUTO-PARCOURS.


Campagne complète terminée avec code de sortie 0 : Gayolard gagné à la
première tentative, Pompatarte à la première et Stratagus à la sixième,
après cinq morts normales au combat. Les personnages ont été tirés à la
création, sans modification de leurs statistiques ni téléportation. Les
scripts de trajet acceptent désormais qu’une destination intermédiaire soit
déjà atteinte par une orientation automatique, sans ajouter une frappe.
Les huit tentatives, réussies et perdues, sont conservées dans
[les rapports de parcours](VALIDATION-RETOURS-AUTO-PARCOURS).


### Les quatre tests CE deviennent visibles

058, 073, 190 et 249 lançaient leur test de Chance pendant l’analyse du texte.
CE prépare maintenant le jet, qui est exécuté après l’affichage du paragraphe :
invite, somme des deux dés, CHANCE de comparaison, verdict et effet visible
sur la feuille. Les choix sont effacés pendant le test puis rétablis. CL garde
son branchement ; CE reste sur la même page et applique la caractéristique
nommée, notamment HABILETÉ en 249. Une chute mortelle passe à la mort avant
les choix. La restauration ignore CE et ne rejoue pas le coût ni l’effet.

Le lecteur de dés existant reconnaît une valeur interne réservée (dice_n=3).
Les nombres ED positifs supérieurs à deux restent bornés à deux dés, et ne
peuvent pas déclencher CE. Aucun champ de sauvegarde ni de structure n’a été
ajouté. Les invites et l’effacement des choix sont mutualisés en LC. Au total,
CODE -2 octets, BSS -4, LC -2 : tas 2 067 octets, réserve de pile inchangée.
Ce petit gain ne satisfait pas à lui seul l’objectif d’augmentation
significative de la marge mémoire.

POM2 headless Mockingboard : 89 assertions pour CE (chanceux, malchanceux,
CHANCE zéro, END/HAB, absence d’effet avant le jet, sac, sauvegarde et mort),
16 assertions des autres types de jet et 7 sur la fouille unique du nid.
Le JavaScript vérifie les quatre pages en FR/EN et la restauration, ainsi
que la séparation ED/CE. Voir [résultats](VALIDATION-CHANCE-VISIBLE/result.json).
Le premier essai du nouveau scénario contenait une recherche de libellé
incorrecte (« Jet » au lieu de « Vous jetez les deux dés ») ; elle a été
corrigée, puis les 89 assertions ont passé. Aucun défaut d’effet n’était
masqué par ces huit échecs de libellé.


Le parcours Gayolard complet est gagné à la première tentative sur ce disque
avec un personnage tiré normalement. Les événements enregistrent les deux
acquittements du test visible en 058 ; les passages par cette page continuent
à consommer la Chance conformément à leurs visites. Voir
[rapport au clavier](VALIDATION-CHANCE-VISIBLE-PARCOURS/gayolard-01.json).
