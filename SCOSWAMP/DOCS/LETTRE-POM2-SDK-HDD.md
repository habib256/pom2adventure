# À POM2 — exposer les disques durs ProDOS et les primitives de harnais dans le SDK

4 novembre 2026 — demande du dépôt `pom2adventure`, à partir d'un essai du
SDK embarqué par `pom2games`.

Bonjour,

Nous voulons remplacer notre ancien hôte POM2, couplé aux en-têtes internes
de l'émulateur et piloté par HTTP, par un outil du type `a2shot`. Le modèle
de `pom2games` convient : SDK public, exécution sans fenêtre, avancement en
cycles, scripts reproductibles, copies privées des disques et captures.

Le premier blocage est précis : **le SDK public ne permet pas de monter nos
disques durs ProDOS**. Nous avons besoin du volume complet livré au joueur,
jusqu'à la limite ProDOS couramment appelée 32 Mo. Réduire le jeu à une
disquette de 800 Ko ne validerait ni le même média ni l'ensemble du corpus.

## 1. Constat vérifié : HDD absent de l'API publique

L'essai utilise `pom2games` au commit
[`3ce4dfcbacbafad42f31380b9c66d9e3e6f57a34`](https://github.com/habib256/pom2games/tree/3ce4dfcbacbafad42f31380b9c66d9e3e6f57a34).
Son [sdk.mk](https://github.com/habib256/pom2games/blob/3ce4dfcbacbafad42f31380b9c66d9e3e6f57a34/dev/tools/a2shot/sdk.mk)
identifie le cœur POM2 comme `ba7f04da19c3047a83eb33538254c885f3c8cb80`.

Nous avons également relu l'en-tête public sur `main`, dont la tête consultée
était [`b515690ad009d5f3dfebb6d49ff51555b7e627cb`](https://github.com/habib256/pom2/blob/b515690ad009d5f3dfebb6d49ff51555b7e627cb/include/pom2/core.hpp).
Il expose toujours :

```cpp
bool attachSmartPort(int slot = 5);
bool insertSmartPortDisk(int unit, std::string_view path);
bool flushSmartPortDisk(int unit);
bool bootSlot(int slot);
```

Le contrat documente un contrôleur **3,5 pouces**, deux unités de 800 Kio
et des médias bruts de 400/800 Kio ou leurs conteneurs compatibles. Aucune
API HDD n'y est déclarée. L'essai d'exécution ci-dessous concerne le SDK
embarqué `ba7f04da`, pas un binaire reconstruit depuis `b515690a`.

Depuis `pom2adventure` :

```sh
../pom2games/dev/tools/a2shot/a2shot \
  --iie --mockingboard --disk dist/SCOSWAMP.2mg wait:180 text
```

Résultat, code de sortie **1** :

```text
boot failed: Disk35Image: 2IMG ProDOS payload must be 400K or 800K (1.44M requires a SuperDrive), got 7521280
```

Le fichier essayé contient **14 690 blocs de 512 octets**, soit
7 521 280 octets de données ProDOS et 64 octets d'en-tête 2MG.
SHA-256 du `.2mg` essayé :

```text
884e07d70498f80e3255fed72a35cb476186c68e66092193e4fee6be3bf1c076
```

Notre autre volume, `dist/SPACETRIP.hdv`, fait déjà 1 312 768 octets : il
dépasse lui aussi 800 Kio. L'extension `.2mg` décrit un conteneur, elle ne
signifie pas que le média est une disquette de 3,5 pouces.

Le code de notre [ancien hôte](../../ADVKIT/TOOLS/pom2_playtest.cpp) emploie
déjà `ProDOSHardDiskCard` sur //e et `SmartPortHdvUnit` sur //c, avec chargement
et écriture différée. Nous ne demandons donc pas de réinventer le HDD ni
d'élargir artificiellement la géométrie d'une disquette : **exposer dans le
SDK le modèle disque dur déjà utilisé par POM2**.

## 2. Demande prioritaire : un contrat HDD complet et testable

Les noms d'API restent à votre choix. Les opérations nécessaires sont :

- Installer le périphérique adapté à la machine : carte HDD sur //e,
  unité HDD SmartPort sur //c, avec slot/unité configurables lorsque cela
  s'applique. Le //e amélioré est notre première cible.
- Monter un volume brut en ordre ProDOS (`.hdv`, `.po`) ou un conteneur
  2IMG ProDOS, en tenant compte de son offset, de sa longueur et de sa
  protection en écriture. Ne pas déduire une géométrie 3,5 pouces du seul
  suffixe `.2mg`.
- Amorcer le volume par le firmware du périphérique, sans injecter le
  programme en RAM ni contourner ProDOS ou le lanceur `.SYSTEM`.
- Lire, écrire, vider les écritures différées, éjecter et remplacer un
  média ; signaler précisément les erreurs de montage et de flush.
- Donner la capacité en blocs et l'état de protection effectif. Définir
  l'effet du remplacement de média et de la destruction du cœur sur les
  écritures en attente.
- Accepter la limite du format ProDOS à champ de capacité sur 16 bits :
  **65 535 blocs**, soit 33 553 920 octets, ou 32 Mio moins un bloc.
  Documenter séparément toute éventuelle prise en charge d'une image
  physique de 65 536 blocs ; ne jamais tronquer ou reboucler silencieusement
  la capacité. Le dernier bloc d'un volume de 65 535 blocs est `$FFFE`.

Le harnais conservera la responsabilité de créer une copie privée avant
montage. Il faut pouvoir tester de vraies sauvegardes dans cette copie,
demander un flush, puis relire les fichiers ProDOS côté hôte. Le disque
livré restera intact.

## 3. Critères d'acceptation du support HDD

| Cas | Résultat attendu |
| --- | --- |
| SCOSWAMP, payload 7 521 280 octets, brut et 2MG | amorçage ProDOS puis `SCOSWAMP.SYSTEM`, choix FR/EN et entrée dans le jeu |
| SPACETRIP, volume supérieur à 800 Kio | amorçage de son volume complet |
| Volume limite de 65 535 blocs | capacité exacte et accès au dernier bloc valide, sans débordement |
| Sauvegarde puis flush/remontage | contenu relu identique ; les modifications de catalogue et de données persistent |
| Copie privée | SHA-256 de l'image originale inchangé après le scénario |
| Média protégé | écriture refusée côté invité et fichier hôte inchangé |
| En-tête tronqué, offset/longueur hors fichier, capacité invalide | refus explicite, sans montage partiel ni modification du fichier |
| Régression 400/800 Kio et Disk II | chemins existants toujours opérationnels |
| Même script, mêmes ROM/SDK/disque/graine | état invité reproductible aux points de contrôle en cycles |

Les tests de bord doivent exercer le périphérique par ses appels invités,
pas seulement vérifier la taille du fichier hôte. Le contrat de timing HDD
doit être documenté pour que les mesures en cycles restent interprétables.

## 4. Autres besoins pour migrer notre harnais

Ces demandes sont distinctes du blocage HDD et peuvent être livrées ensuite.
Les méthodes `run`, `step`, `cpuState`, `setCpuState`, `queueKey`, les bus
watches et `renderFrame` existent déjà : nous souhaitons les réutiliser.

**Inspection de mémoire sans effets de bord.** Notre banc lit séparément
MAIN et AUX, notamment les deux pages texte à `$0400` et les banques DHGR
à `$2000`. Le SDK n'expose actuellement que `read`/`write` sur le bus, dont
le contrat prévient explicitement des effets matériels. Ajouter une lecture
de plage avec banque explicite, indépendante de RAMRD/RAMWRT/80STORE/PAGE2,
et une écriture de RAM de débogage au contrat aussi explicite. Lire l'écran
ne doit ni changer les banques, ni acquitter une entrée, ni avancer le CPU.
La Language Card et ses banques doivent être nommées sans ambiguïté si elles
sont exposées. Les accès au bus restent utiles pour tester le matériel.

**État du clavier.** Exposer le nombre de caractères en attente et, si
possible, l'état du latch sans l'acquitter. Notre pilote historique attend
une stabilité d'écran et temporise ; une session déterministe devrait
attendre un point d'arrêt ou une consommation de touche observable, avec
un budget de cycles. ESC et RETURN doivent rester des octets de commande,
pas dépendre des limites de l'ancien parseur JSON HTTP.

**Rendu identifiable.** Préciser le pipeline de `renderFrame` et ce qu'il
partage avec le rendu de l'application. Notre cible visuelle est CRT
OpenEmulator ; une capture composite CPU ne doit pas être présentée comme
équivalente sans vérification. Si le profil CRT n'est pas disponible dans
le SDK, le déclarer clairement. **L'utilisateur reste seul juge de la
qualité des images dans l'atelier web**, avec crop, régénération et
comparaison : les captures du harnais servent de preuves techniques.

**Livraison reproductible.** Fournir ensemble l'en-tête, les archives macOS
ARM64/Linux x86_64, le commit et la liste des capacités du SDK. Une mise à
jour de l'en-tête seule ne suffit pas. Documenter les dépendances système
et les ROM requises. Les tests doivent pouvoir enregistrer les empreintes
du cœur, des ROM, du média et du programme réellement exécutés.

Enfin, les convertisseurs d'images de notre atelier compilent encore des
sources privées `hgrpaint` de POM2. C'est une dépendance distincte du HDD :
un convertisseur CLI distribuable ou un paquet de conversion documenté
permettrait à terme de construire l'atelier sans checkout complet de POM2.
Cette évolution ne doit pas retarder l'exposition du disque dur dans le SDK.

## 5. Répartition proposée

POM2 porte le périphérique HDD, les primitives publiques, leurs contrats et
les tests matériels de bord. `a2shot` choisit explicitement le bon type de
média, conserve le protocole de commandes et produit les captures.
`pom2adventure` porte les scénarios, l'association binaire/symboles, les
copies privées et les assertions sur les jeux.

Nous souhaitons aussi reprendre les bonnes pratiques de la bibliothèque
`pom2games` : objets d'archive tirés seulement lorsqu'ils sont utilisés,
contrats C/ASM pour la page zéro, les banques et les IRQ, mesures séparées
à froid/à chaud, budgets de cycles et de mémoire, et pics de piles observés.
Une primitive optimisée devra être mesurée dans notre moteur avant adoption ;
son gain dans un autre jeu ne suffit pas à justifier son remplacement ici.

La première livraison utile est donc simple à définir : **amorcer notre
vrai volume SCOSWAMP depuis le SDK public, jouer un scénario et vérifier une
sauvegarde sur sa copie privée**. Cela débloquera l'intégration d'un harnais
de type `a2shot` sans réduire le jeu pour l'adapter à l'outil.

Merci.

---

## Réponse de POM2

4 novembre 2026 — livré sur `main` au commit
[`0d1d388e`](https://github.com/habib256/pom2/commit/0d1d388e98b2268629cc65269c1aba161720585a).
Le contrat est dans `docs/SDK.md` de POM2. `pom2games` embarque ce SDK sur macOS
depuis `77ca031`.

Le §1 décrit l'état d'avant. Le volume a été reconstruit depuis : SCOSWAMP compte
aujourd'hui 14 684 blocs, et non 14 690.

### §3 : critères d'acceptation

| Cas | Résultat | Où c'est vérifié |
| --- | --- | --- |
| SCOSWAMP, brut et 2MG | amorçage, FR, entrée dans le jeu | suite `a2shot` du harnais |
| SPACETRIP, brut et 2MG | amorçage, FR, entrée dans le jeu | suite `a2shot` |
| Volume de 65 535 blocs | capacité exacte, bloc `$FFFE` lu et écrit, `$FFFF` refusé par `$27` | `pom2_core_hdd` (//e, //c) |
| Sauvegarde, flush, remontage | `SAVE3` passe de 2 à 279 octets, seuls 2 blocs changent, la partie reprend | suite `a2shot` ; vrai ProDOS sur //e, //c, //c+ dans `pom2_core_hdd` |
| Copie privée | SHA-256 de `dist/` inchangé | suite `a2shot` |
| Média protégé | écriture refusée par `$2B`, fichier inchangé | `pom2_core_hdd`, suite `a2shot` |
| En-tête, offset, longueur, capacité invalides | refus nommé, rien de monté ni d'écrit | `pom2_core_hdd` |
| Régression 400/800 Kio et Disk II | chemins inchangés | `ctest` de POM2 (434 sur 434), `make test` de `pom2games` |
| Même script, mêmes ROM et disque | mêmes octets, même écran, même cycle | suite `a2shot`, `pom2_core_hdd` |

Une image physique de 65 536 blocs est aussi acceptée : STATUS y répond `$FFFF`, le
bloc `$FFFF` reste accessible, et seul `hardDiskBlockCount` dit 65 536. Ce travail a
corrigé un bug de l'émulateur : sur //c, cette image répondait 0 bloc.

Le //c+ est couvert aussi. Le disque dur y est le drive 2 du slot 5 : il n'amorce que
lecteur interne vide, et un 3,5 pouces externe le masque aux appels ProDOS.

### §4 : autres besoins

| Besoin | Livré |
| --- | --- |
| Mémoire sans effet de bord | `readRam`, `writeRam`, huit banques nommées |
| État du clavier | `keyboardState` ; `keywait` dans `a2shot` |
| Rendu identifiable | `docs/SDK.md` § Rendering : `renderFrame` est la table composite de MAME, **pas** le CRT OpenEmulator, qui n'est pas dans le SDK |
| Livraison reproductible | `sdkInfo`, `sha256`, `tools/package_core_sdk.sh` et son manifeste, étape `provenance` |
| Convertisseurs sans sources POM2 | paquet `pom2_imageconv`, `-DPOM2_SDK_PREFIX` ; sortie identique octet par octet sur 30 conversions |

L'utilisateur reste seul juge des images : rien de ce qui précède n'en valide une.

### Le banc

`playtest.py` a deux hôtes, tous deux conservés. HTTP pilote l'émulateur POM2 complet ;
`--host a2shot` passe par le SDK. Sur les 79 scénarios, `pom2_playtest` et `a2shot`
donnent chacun 1 133 assertions et 0 échec. Sur l'émulateur complet, `demarrage`,
`combat`, `musique` et `musique_transitions` passent.

Les 19 échecs d'avant venaient du banc, pas du jeu : le lecteur de symboles ignorait
les `.ifdef` de `music.s`, et trois scénarios attendaient autre chose que ce que le
livre demande (pages 058 et 374).

### Ce qui reste ouvert

- L'archive Linux du SDK : tant qu'elle n'est pas reconstruite depuis ce commit,
  `a2shot` sous Linux refuse les disques durs.
- `build_prodos_volume` a encore besoin des sources POM2 : il n'est pas dans le paquet,
  donc l'atelier n'est pas encore constructible sans checkout complet.
- Le job `core-sdk` de `release.yml` n'a jamais tourné : il tournera au prochain tag.

Merci.
