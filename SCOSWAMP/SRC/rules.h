/*
 * RULES - Les regles de Defis Fantastiques, telles que le livre les enonce.
 *
 * Source : "Le Marais aux Scorpions" (Defis Fantastiques 08, Gallimard 1985),
 * sections "Habilete, Endurance et Chance", "Batailles", "Fuite", "Chance",
 * "Comment retablir...", "Equipement" et "La Magie" des pages liminaires.
 * Chaque regle non evidente porte ci-dessous la phrase du livre qui la fonde :
 * c'est la seule facon de trancher plus tard un desaccord entre le code et une
 * page du corpus.
 *
 * Ce fichier ne connait ni l'ecran ni ProDOS : il compile aussi bien avec cc65
 * que sur la machine hote, ou tests/test_rules.c le passe au banc.
 */

#ifndef RULES_H
#define RULES_H

/* ── Les douze Pierres Magiques ───────────────────────────────────────────
 * "Il existe en tout douze sortes de Pierres Magiques." Elles se rangent en
 * trois categories, et cette appartenance a une consequence de jeu : "il vous
 * sera impossible d'obtenir des Pierres Magiques benefiques aupres d'un
 * sorcier malefique, ou des pierres malefiques aupres d'un bon sorcier". */
typedef enum {
    /* Neutres */
    STONE_HABILETE = 0,
    STONE_ENDURANCE,
    STONE_CHANCE,
    STONE_FEU,
    STONE_GLACE,
    STONE_ILLUSION,
    /* Benefiques */
    STONE_AMITIE,
    STONE_CROISSANCE,
    STONE_BENEDICTION,
    /* Malefiques */
    STONE_TERREUR,
    STONE_FLETRISSURE,
    STONE_MALEDICTION,
    STONE_COUNT
} Stone;

typedef enum {
    STONE_NEUTRE = 0,
    STONE_BENEFIQUE,
    STONE_MALEFIQUE
} StoneKind;

/* Objets du Sac a Dos. Le nom commencant par un point est un drapeau narratif
 * invisible ; il passe par le meme bitmap afin
 * que les conditions du corpus et la sauvegarde restent simples. */
typedef enum {
    OBJ_ANNEAU = 0, OBJ_CAPE, OBJ_CHAINE, OBJ_AIMANT,
    OBJ_FIOLE, OBJ_BAIE, OBJ_EPEMAGIQUE, OBJ_BIJOU, OBJ_CORNE, OBJ_PLUMES,
    OBJ_GRAINES,
    OBJ_ANTHERIQUE, OBJ_MISSION_GAYOLARD, OBJ_MISSION_POMPATARTE,
    OBJ_MISSION_STRATAGUS, OBJ_POTION_NAINE,
    OBJ_COUNT
} Object;

/* Les drapeaux caches se rangent APRES les objets, et OBJ_HIDDEN0 est le
 * premier d'entre eux : tout ce qui le precede a un nom et se montre dans le
 * sac, tout ce qui le suit est un fait narratif. Les identifiants et bits
 * sont declares dans SCOSWAMP/OBJECTS.json. Ces enums restent a extraire :
 * toute modification des bits exige de les synchroniser et de prevoir la
 * migration des sauvegardes ; inserer un objet decalerait les drapeaux. */
#define OBJ_HIDDEN0 OBJ_ANTHERIQUE

typedef enum {
    AMULET_LOUP = 0, AMULET_FLEUR, AMULET_OISEAU,
    AMULET_ARAIGNEE, AMULET_GRENOUILLE, AMULET_FAUSSE_OISEAU, AMULET_COUNT
} Amulet;

const char* object_name(Object o, int english);
Object object_from_name(const char* name);
const char* amulet_name(Amulet a, int english);
Amulet amulet_from_name(const char* name);

StoneKind   stone_kind(Stone s);
const char* stone_name(Stone s, int english);
/* Rend STONE_COUNT si le nom n'est pas reconnu. Comparaison insensible a la
 * casse et aux accents : les pages du corpus ecrivent "Fletrissure" sans
 * accent, le livre "FLETRISSURE". */
Stone       stone_from_name(const char* name);

/* ── La Feuille d'Aventure ────────────────────────────────────────────────
 * "Bien que vous puissiez obtenir des points supplementaires d'HABILETE,
 * d'ENDURANCE et de CHANCE, ce total ne doit en aucun cas exceder vos points
 * de depart." D'ou le couple (courant, depart) pour chacune des trois. */
typedef struct {
    /* Chaque caracteristique est suivie de son total de depart, et les trois
     * paires se suivent dans l'ordre HABILETE, ENDURANCE, CHANCE :
     * character_shift0 compte la-dessus pour les atteindre sans aiguillage. */
    unsigned char hab,  hab0;
    unsigned char end,  end0;
    unsigned char cha,  cha0;
    unsigned int  gold;
    unsigned char weapon_bonus;  /* bonus d'assaut de l'Epee Magique : 0, 1 ou 2 */
    unsigned char stones[STONE_COUNT];
    unsigned int  objects;       /* un bit par Object */
    unsigned char amulets;       /* loup, fleur, oiseau, araignee, grenouille */
} Character;

void character_give_object(Character* c, Object o);
void character_take_object(Character* c, Object o);
int  character_has_object(const Character* c, Object o);
void character_give_amulet(Character* c, Amulet a);
int  character_has_amulet(const Character* c, Amulet a);
unsigned char character_amulet_count(const Character* c);
unsigned char character_trade_amulets(Character* c, unsigned int each);

/* "Lancez un de. Ajoutez 6 [...] HABILETE. Lancez ensuite les deux des.
 * Ajoutez 12 [...] ENDURANCE. [...] Lancez a nouveau un de, ajoutez 6 [...]
 * CHANCE." L'equipement de depart : une epee, une cotte de mailles, un sac a
 * dos et "quelques Pieces d'Or". */
void character_roll(Character* c);

/* Ajoute (ou retire, si delta < 0) des points en respectant le plafond de
 * depart et le plancher zero. Passer par ici pour TOUTE variation : c'est le
 * seul endroit qui connait la regle du plafond. */
void character_adjust_hab(Character* c, int delta);
void character_adjust_end(Character* c, int delta);
void character_adjust_cha(Character* c, int delta);

/* L'or n'a pas de plafond -- le livre n'en pose aucun -- mais il a le meme
 * plancher que le reste : "vous ne pouvez pas payer ce que vous n'avez pas".
 * Passer par ici pour TOUTE variation de bourse. Un `gold += delta` ecrit a
 * la main sur un champ non signe donne 65535 Pieces d'Or au heros sans le
 * sou qui paie une piece a l'aubergiste (page 078). */
void character_adjust_gold(Character* c, int delta);

/* Variation du TOTAL DE DEPART, et de la valeur courante avec lui.
 *
 * Vers le bas : "vous perdez 2 points d'HABILETE et devez reduire aussi de 2
 * points votre total initial d'HABILETE. Vous ne pourrez plus jamais
 * retrouver tous vos points de depart" (paragraphe 87). La perte ordinaire se
 * rattrape ; celle-ci abaisse le plafond, donc rien ne la rend jamais.
 *
 * Vers le haut : la benediction de Grognard (paragraphe 155) tombe au village,
 * avant le premier pas dans le Marais, ou le heros est encore a sa CHANCE de
 * depart. Deux points plafonnes n'y donneraient rien : une benediction est
 * une benediction, elle releve le plafond et la valeur courante avec lui.
 *
 * `k` suit la numerotation de carac_of : 0 ENDURANCE, 1 HABILETE, 2 CHANCE.
 * Rien d'autre n'est admis, et rien n'est verifie ici -- une version a trois
 * wrappers et deux `if` coutait 150 octets que le binaire n'a pas ; c'est
 * reflow_txt.py qui refuse `E0 OR` et `E0 BONUS`. */
void character_shift0(Character* c, unsigned char k, int delta);

int  character_is_dead(const Character* c);   /* ENDURANCE tombee a zero */

/* ── Tentez votre Chance ──────────────────────────────────────────────────
 * "jetez deux des. Si le chiffre obtenu est egal ou inferieur a vos points de
 * CHANCE, vous etes Chanceux [...] Chaque fois que vous Tenterez votre
 * Chance, il vous faudra oter un point a votre total de CHANCE."
 * Rend 1 si Chanceux. Le point de CHANCE est consomme dans tous les cas. */
int luck_test(Character* c);

/* ── Batailles ────────────────────────────────────────────────────────────
 * L'adversaire n'a que deux nombres : "vous inscrirez les points d'HABILETE
 * et d'ENDURANCE de la creature". */
typedef struct {
    unsigned char hab;
    unsigned char end;
    unsigned char end0;      /* l'ENDURANCE que le livre lui donne, pour la jauge */
    /* Deux exceptions que le livre pose page par page, et qu'il faut donc
     * pouvoir ecrire dans la page plutot que dans le code. Au paragraphe 12 :
     * "vous perdez 4 points d'ENDURANCE au lieu de 2 en raison de la puissance
     * du coup" (damage=4) et "si vous parvenez a reduire a 6 les points
     * d'ENDURANCE du Geant, rendez-vous au 61" (stop_at=6). */
    unsigned char damage;    /* ENDURANCE perdue par coup recu -- 2 par defaut */
    unsigned char stop_at;   /* le combat cesse a cette ENDURANCE -- 0 par defaut */
    char          name[24];
} Monster;

/* Met les valeurs par defaut du livre : 2 points par blessure, combat jusqu'a
 * zero. A appeler avant de lire les champs d'une page. */
void monster_init(Monster* m);
/* Fige l'ENDURANCE de depart. A appeler quand la page a fini d'etre lue et
 * AVANT monster_enter, qui peut rendre une valeur deja entamee. */
void monster_seal(Monster* m);
int  monster_is_beaten(const Monster* m);

typedef enum {
    ROUND_DODGE = 0,      /* Forces d'Attaque egales : "vous avez chacun esquive" */
    ROUND_HERO_HITS,
    ROUND_MONSTER_HITS
} RoundOutcome;

typedef struct {
    /* Les deux des de chacun, gardes a part de leur somme : "chacun lance
     * deux des". Un total tout fait ne se lit pas comme un jet -- l'ecran
     * doit pouvoir montrer "4 + 3 + 11 = 18", sinon le joueur n'a plus qu'un
     * verdict, et un verdict n'a pas de suspense. Quatre octets de plus dans
     * l'unique Round de run_combat -- pas un de plus par adversaire. */
    unsigned char hero_d1, hero_d2;
    unsigned char monster_d1, monster_d2;
    unsigned char hero_force;      /* 2d6 + HABILETE du heros (+ Epee Magique) */
    unsigned char monster_force;   /* 2d6 + HABILETE de la creature */
    /* Un RoundOutcome, range dans un octet et non dans l'enum lui-meme. Sur
     * cc65 un enum est un `int` : chaque comparaison passait par le jeu
     * d'appels 16 bits (pushax, toscmp...), et le seul fait de descendre ce
     * champ a un octet a rendu 63 octets de code -- de quoi payer les quatre
     * des ci-dessus cinq fois. Le type reste documente ici. */
    unsigned char outcome;
} Round;

/* Un assaut : etapes 1 a 3 du livre. Ne modifie rien, se contente de jeter les
 * des et de remplir `out` -- c'est l'appelant qui decide ENSUITE s'il Tente sa
 * Chance, parce que le livre place ce choix apres la blessure.
 *
 * Le resultat passe par un pointeur et non par la valeur de retour : cc65 rend
 * les structures par valeur de travers, et ca s'etait vu a l'ecran sous la
 * forme d'assauts a Forces d'Attaque egales qui blessaient au lieu d'esquiver.
 * Le banc d'essai sur machine hote ne pouvait pas l'attraper -- il compile
 * avec un vrai compilateur C. */
void combat_round(const Character* c, const Monster* m, Round* out);

/* Etapes 4 a 6. `use_luck` = le joueur Tente sa Chance sur cette blessure.
 *   il blesse   : -2 ENDURANCE ; Chanceux -4, Malchanceux -1
 *   il est blesse : -damage ; Chanceux -(damage-1), Malchanceux -(damage+1)
 * Rend 1 si la Chance a ete tentee ET etait bonne (pour l'affichage). */
int combat_apply(Character* c, Monster* m, const Round* r, int use_luck);

/* "Si vous prenez la Fuite, cependant, la creature vous aura automatiquement
 * inflige une blessure [...] Vous oterez alors deux points a votre ENDURANCE.
 * Pour cette blessure, vous pourrez toutefois vous servir de votre CHANCE." */
int combat_flee(Character* c, const Monster* m, int use_luck);

/* ── Memoire des clairieres ───────────────────────────────────────────────
 * "notez les modifications intervenues dans son total d'ENDURANCE et conservez
 * ces indications car il est possible que vous reveniez plus tard dans cette
 * clairiere [...] il vous faudrait peut-etre reprendre le combat la ou vous
 * l'aviez laisse." Le Marais est le seul Defis Fantastiques ou l'on revient
 * sur ses pas : sans cette memoire, fuir puis revenir soignerait le monstre. */
/* Une entree par creature laissee blessee derriere soi. Le livre ne place un
 * adversaire que dans 29 clairieres : 40 emplacements couvrent le pire cas
 * avec de la marge, pour 120 octets, la ou un octet par paragraphe en aurait
 * coute 412 -- et sur cette machine pres de 300 octets, soit un ecran. */
#define MONSTER_SLOTS 40

void monster_memory_reset(void);
/* Recupere uniquement la creature memorisee vivante de cette zone.
 * Les deux bornes viennent des donnees; aucune resurrection ni nouvelle entree. */
void monster_recover(unsigned int zone, unsigned char amount, unsigned char maximum);

/* Reprend la file d'adversaires d'une clairiere la ou on l'avait laissee.
 *
 * "Parfois, vous les affronterez comme si elles n'etaient qu'un seul monstre ;
 * parfois, vous les combattrez une par une" : les deux rencontres a plusieurs
 * du Marais sont du second type, d'ou une file. Il faut donc se souvenir non
 * seulement de l'ENDURANCE entamee mais de QUEL adversaire etait en cours.
 *
 * `zone` est la cle de clairiere fournie par le moteur (jamais le numero de
 * page) : revenir par une autre entree retrouve donc exactement la meme file.
 * Rend l'indice ou reprendre, et ajuste l'ENDURANCE de cet adversaire-la.
 * Rend `count` si toute la file est tombee lors d'une visite precedente. */
int  monster_enter(unsigned int zone, Monster* foes, int count);
void monster_remember(unsigned int zone, int index, const Monster* m);

/* ── Les clairieres deja parcourues ────────────────────────────────────────
 * "Si vous y etes deja venu, rendez-vous au 142. Sinon, lisez ce qui suit."
 * Quatorze pages du livre ouvrent sur cette phrase : la clairiere a une
 * description longue la premiere fois et une courte ensuite. Le livre confie
 * ce comptage au joueur ; le portage le tient lui-meme, par la ligne `V`.
 *
 * Un bit par paragraphe, 419 bits arrondis a 53 octets -- assez peu pour ne
 * pas chercher plus malin, et sans le plafond d'une table clairsemee. Le
 * corpus est monte a 419 pages avec le prologue de Bourbenville : a 52 octets
 * la memoire s'arretait au 415 et les lignes V posees au-dela n'auraient
 * jamais declenche, en silence. */
void scene_memory_reset(void);
int  scene_visited(unsigned int scene);
void scene_mark_visited(unsigned int scene);

/* Etat opaque exporte pour la sauvegarde. Les tailles sont stables sur cc65. */
#define SCENE_MEMORY_SIZE 53
#define MONSTER_MEMORY_SIZE (MONSTER_SLOTS * 4)
void scene_memory_export(unsigned char* out);
void scene_memory_import(const unsigned char* in);
void monster_memory_export(unsigned char* out);
void monster_memory_import(const unsigned char* in);

/* ── La Magie ─────────────────────────────────────────────────────────────
 * "chacune d'elle vous permettra de jeter un sort, mais un seul, car les
 * Pierres de Magie se desintegrent des qu'on les a utilisees." */
typedef enum {
    STONE_USE_OK = 0,        /* consommee, effet narratif a la page */
    STONE_USE_NONE,          /* le heros n'en a pas */
    STONE_USE_FORBIDDEN      /* interdite a ce moment (voir stone_usable) */
} StoneUse;

void character_give_stone(Character* c, Stone s, unsigned char n);
int  character_has_stone(const Character* c, Stone s);

/* "Vous avez le droit d'utiliser les pierres d'ENDURANCE, d'HABILETE et de
 * CHANCE a tout moment, sauf au cours d'un combat. Si vous souhaitez en faire
 * usage au debut de l'affrontement, rien ne s'y oppose, mais il vous est
 * interdit de vous en servir sitot que le premier coup a ete donne."
 * `in_combat` : 0 avant assaut, 1 apres assaut, 2 toute magie interdite. */
int      stone_usable(Stone s, int in_combat);
StoneUse stone_use(Character* c, Stone s, int in_combat);

#endif /* RULES_H */
