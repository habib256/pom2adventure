/*
 * Banc d'essai des regles de Defis Fantastiques, sur machine hote.
 *
 * Les regles sont de l'arithmetique pure : les verifier ici coute une seconde,
 * alors que les verifier dans l'emulateur demande de rejouer une partie et ne
 * couvre qu'un chemin. Chaque test porte la phrase du livre qu'il defend.
 */
#include "../../SCOSWAMP/SRC/rules.h"
#include "../../SCOSWAMP/SRC/dice.h"
#include <stdio.h>
#include <string.h>

static int failures = 0;

#define CHECK(cond, ...)                                                      \
    do {                                                                      \
        if (!(cond)) {                                                        \
            printf("ECHEC %s:%d: ", __FILE__, __LINE__);                      \
            printf(__VA_ARGS__); printf("\n"); ++failures;                    \
        }                                                                     \
    } while (0)

/* Un heros dont la CHANCE rend "Tentez votre Chance" deterministe :
 * cha=12 -> 2d6 <= 12 toujours vrai ; cha=1 -> 2d6 >= 2 toujours faux. */
static Character hero(unsigned char hab, unsigned char end, unsigned char cha)
{
    Character c;
    memset(&c, 0, sizeof c);
    c.hab = c.hab0 = hab;
    c.end = c.end0 = end;
    c.cha = c.cha0 = cha;
    return c;
}

static void test_dice(void)
{
    int i, seen[7] = {0};
    dice_seed(12345);
    for (i = 0; i < 6000; ++i) {
        unsigned char d = roll_d6();
        CHECK(d >= 1 && d <= 6, "de hors bornes: %u", d);
        ++seen[d];
    }
    for (i = 1; i <= 6; ++i) {
        /* 1000 attendus par face ; large fourchette, on cherche une face
         * morte ou un modulo biaise, pas la qualite statistique fine. */
        CHECK(seen[i] > 800 && seen[i] < 1200, "face %d sortie %d fois", i, seen[i]);
    }
    for (i = 0; i < 2000; ++i) {
        unsigned char d = roll_2d6();
        CHECK(d >= 2 && d <= 12, "2d6 hors bornes: %u", d);
    }
    /* Deterministe a semence egale : c'est ce qui rend ce fichier possible. */
    dice_seed(7); i = roll_d6() * 10 + roll_d6();
    dice_seed(7); CHECK(i == roll_d6() * 10 + roll_d6(), "semence non reproductible");
}

static void test_creation(void)
{
    int i;
    dice_seed(99);
    for (i = 0; i < 500; ++i) {
        Character c;
        character_roll(&c);
        /* "Lancez un de. Ajoutez 6 [...] HABILETE" */
        CHECK(c.hab >= 7  && c.hab <= 12, "HABILETE %u hors 7..12", c.hab);
        /* "Lancez ensuite les deux des. Ajoutez 12 [...] ENDURANCE" */
        CHECK(c.end >= 14 && c.end <= 24, "ENDURANCE %u hors 14..24", c.end);
        /* "Lancez a nouveau un de, ajoutez 6 [...] CHANCE" */
        CHECK(c.cha >= 7  && c.cha <= 12, "CHANCE %u hors 7..12", c.cha);
        CHECK(c.hab == c.hab0 && c.end == c.end0 && c.cha == c.cha0,
              "les valeurs de depart doivent egaler les courantes");
    }
}

static void test_plafond(void)
{
    /* "ce total ne doit en aucun cas exceder vos points de depart" */
    Character c = hero(9, 20, 8);
    character_adjust_end(&c, -6);   CHECK(c.end == 14, "END %u", c.end);
    character_adjust_end(&c, +99);  CHECK(c.end == 20, "END plafonnee a 20, vu %u", c.end);
    character_adjust_end(&c, -99);  CHECK(c.end == 0,  "END plancher 0, vu %u", c.end);
    CHECK(character_is_dead(&c), "ENDURANCE a zero = mort");
    character_adjust_hab(&c, +5);   CHECK(c.hab == 9,  "HAB plafonnee, vu %u", c.hab);
    character_adjust_cha(&c, +5);   CHECK(c.cha == 8,  "CHA plafonnee, vu %u", c.cha);
}

/* La bourse. Elle n'a pas de plafond dans le livre -- "quelques Pieces d'Or
 * qui vous permettront de subvenir a de menues depenses", jamais de maximum --
 * mais elle a un plancher, et c'est lui qui compte : le champ est non signe,
 * et un heros sans le sou qui paie une piece a l'aubergiste (page 078)
 * repassait a 65535 Pieces d'Or. */
static void test_or(void)
{
    Character c = hero(9, 20, 8);

    c.gold = 0;
    character_adjust_gold(&c, -1);
    CHECK(c.gold == 0, "une bourse vide reste vide, vu %u", c.gold);

    c.gold = 3;
    character_adjust_gold(&c, -5);
    CHECK(c.gold == 0, "on ne paie pas ce qu'on n'a pas, vu %u", c.gold);

    c.gold = 3;
    character_adjust_gold(&c, +100);
    CHECK(c.gold == 103, "aucun plafond sur l'or, vu %u", c.gold);

    /* Le contrat va jusqu'a 32 767, la borne de l'int 16 bits de cc65 par
     * lequel le calcul passe. Le corpus distribue 370 Pieces d'Or en tout :
     * la borne est hors d'atteinte de deux ordres de grandeur, mais elle est
     * le contrat, et un test la tient. */
    c.gold = 20000u;
    character_adjust_gold(&c, +12000);
    CHECK(c.gold == 32000u, "la bourse porte quatre chiffres et plus, vu %u", c.gold);

    /* Le jet `ED OR +1` de la page 135 passe par la meme porte : un gain
     * ordinaire s'ajoute, sans plafond de depart contrairement aux trois
     * caracteristiques. */
    c.gold = 20;
    character_adjust_gold(&c, +6);
    CHECK(c.gold == 26, "un de d'or s'ajoute, vu %u", c.gold);
}

static void test_chance(void)
{
    Character c;
    int i;

    /* "Si le chiffre obtenu est egal ou inferieur a vos points de CHANCE,
     * vous etes Chanceux" : a 12, tout 2d6 passe. */
    dice_seed(4);
    c = hero(9, 20, 12);
    CHECK(luck_test(&c) == 1, "CHANCE 12 doit toujours etre Chanceux");
    /* "il vous faudra oter un point a votre total de CHANCE" */
    CHECK(c.cha == 11, "un point de CHANCE consomme, vu %u", c.cha);

    c = hero(9, 20, 1);
    CHECK(luck_test(&c) == 0, "CHANCE 1 ne peut jamais etre Chanceux");
    CHECK(c.cha == 0, "CHANCE consommee, vu %u", c.cha);
    /* A zero, le jet est perdu d'avance et ne descend pas sous zero. */
    for (i = 0; i < 5; ++i) CHECK(luck_test(&c) == 0, "CHANCE 0 -> Malchanceux");
    CHECK(c.cha == 0, "CHANCE ne passe pas sous zero, vu %u", c.cha);
}

static void test_assaut(void)
{
    Character c = hero(10, 20, 12);
    Monster m; Round r; int i;
    dice_seed(31);
    monster_init(&m); m.hab = 8; m.end = 12; strcpy(m.name, "GEANT");

    for (i = 0; i < 500; ++i) {
        combat_round(&c, &m, &r);
        /* "Jetez les deux des [...] Ajoutez ses points d'HABILETE" */
        CHECK(r.hero_force    >= 12 && r.hero_force    <= 22, "FA heros %u", r.hero_force);
        CHECK(r.monster_force >= 10 && r.monster_force <= 20, "FA monstre %u", r.monster_force);
        CHECK((r.outcome == ROUND_HERO_HITS)    == (r.hero_force >  r.monster_force), "issue");
        CHECK((r.outcome == ROUND_MONSTER_HITS) == (r.hero_force <  r.monster_force), "issue");
        CHECK((r.outcome == ROUND_DODGE)        == (r.hero_force == r.monster_force), "issue");
        /* Les des exposes doivent etre les des du jet, pas un decor : l'ecran
         * ecrit "d1 + d2 + HABILETE = force", et une somme qui ne retombe pas
         * dessus ferait mentir la ligne sous les yeux du joueur. */
        CHECK(r.hero_d1 >= 1 && r.hero_d1 <= 6 && r.hero_d2 >= 1 && r.hero_d2 <= 6 &&
              r.monster_d1 >= 1 && r.monster_d1 <= 6 && r.monster_d2 >= 1 && r.monster_d2 <= 6,
              "des hors de 1..6");
        CHECK(r.hero_d1 + r.hero_d2 + c.hab == r.hero_force, "des du heros");
        CHECK(r.monster_d1 + r.monster_d2 + m.hab == r.monster_force, "des de la creature");
    }

    /* Les deux epees magiques du livre n'ont pas la meme puissance : celle
     * offerte par Stratagus vaut +1, celle prise sur lui vaut +2. */
    c = hero(10, 20, 12); c.objects = (1u << OBJ_EPEMAGIQUE); c.weapon_bonus=2;
    dice_seed(77); combat_round(&c, &m, &r); i = r.hero_force;
    c.weapon_bonus=1;
    dice_seed(77); combat_round(&c, &m, &r);
    CHECK(i == r.hero_force + 1, "epee prise +2 contre epee offerte +1");
    c.objects |= (1u << OBJ_POTION_NAINE);
    dice_seed(77); combat_round(&c, &m, &r);
    CHECK(i == r.hero_force + 2, "potion naine : -1 cumule avec l'epee +1");
    CHECK(c.hab == 10 && c.hab0 == 10, "le malus temporaire ne modifie pas le plafond");
    c.hab = 0;
    dice_seed(77); combat_round(&c, &m, &r);
    CHECK(r.hero_force == r.hero_d1 + r.hero_d2 + c.weapon_bonus,
          "la potion ne rend pas l'HABILETE negative");
}

static void test_blessures(void)
{
    Character c;
    Monster m;
    Round r;
    dice_seed(5);
    monster_init(&m); m.hab = 8; m.end = 20; strcpy(m.name, "X");

    /* "vous diminuez donc de deux points son ENDURANCE" */
    c = hero(10, 20, 9); r.outcome = ROUND_HERO_HITS;
    combat_apply(&c, &m, &r, 0);
    CHECK(m.end == 18, "blessure simple = -2, vu %u", m.end);

    /* Chanceux : "vous pouvez oter deux points de plus" -> -4 en tout */
    c = hero(10, 20, 12); m.end = 20;
    CHECK(combat_apply(&c, &m, &r, 1) == 1, "CHANCE 12 = Chanceux");
    CHECK(m.end == 16, "blessure grave = -4, vu %u", m.end);
    CHECK(c.cha == 11, "le jet coute un point de CHANCE");

    /* Malchanceux : "au lieu d'enlever les deux points [...] un seul" */
    c = hero(10, 20, 1); m.end = 20;
    CHECK(combat_apply(&c, &m, &r, 1) == 0, "CHANCE 1 = Malchanceux");
    CHECK(m.end == 19, "ecorchure = -1, vu %u", m.end);

    /* Le heros encaisse */
    r.outcome = ROUND_MONSTER_HITS;
    c = hero(10, 20, 9);  combat_apply(&c, &m, &r, 0);
    CHECK(c.end == 18, "blessure recue = -2, vu %u", c.end);
    c = hero(10, 20, 12); combat_apply(&c, &m, &r, 1);
    CHECK(c.end == 19, "coup attenue = -1, vu %u", c.end);
    c = hero(10, 20, 1);  combat_apply(&c, &m, &r, 1);
    CHECK(c.end == 17, "coup aggrave = -3, vu %u", c.end);

    /* Paragraphe 12 : la massue coute 4 points au lieu de 2, et le
     * modificateur de CHANCE reste de UN point -- donc 3 ou 5. */
    m.damage = 4;
    c = hero(10, 20, 9);  combat_apply(&c, &m, &r, 0);
    CHECK(c.end == 16, "massue = -4, vu %u", c.end);
    c = hero(10, 20, 12); combat_apply(&c, &m, &r, 1);
    CHECK(c.end == 17, "massue attenuee = -3, vu %u", c.end);
    c = hero(10, 20, 1);  combat_apply(&c, &m, &r, 1);
    CHECK(c.end == 15, "massue aggravee = -5, vu %u", c.end);
    m.damage = 2;

    /* Esquive : personne ne perd rien */
    r.outcome = ROUND_DODGE;
    c = hero(10, 20, 9); m.end = 20;
    combat_apply(&c, &m, &r, 0);
    CHECK(c.end == 20 && m.end == 20, "l'esquive ne coute rien");

    /* L'ENDURANCE d'une creature ne passe pas sous zero */
    r.outcome = ROUND_HERO_HITS; m.end = 1;
    c = hero(10, 20, 9); combat_apply(&c, &m, &r, 0);
    CHECK(m.end == 0, "ENDURANCE creature plancher 0, vu %u", m.end);
}

static void test_fuite(void)
{
    /* "Vous oterez alors deux points a votre ENDURANCE. [...] vous pourrez
     * toutefois vous servir de votre CHANCE" */
    Character c;
    Monster m;
    dice_seed(17);
    monster_init(&m); m.hab = 8; m.end = 10;
    c = hero(9, 20, 9);  combat_flee(&c, &m, 0); CHECK(c.end == 18, "fuite = -2, vu %u", c.end);
    c = hero(9, 20, 12); combat_flee(&c, &m, 1); CHECK(c.end == 19, "fuite chanceuse = -1, vu %u", c.end);
    c = hero(9, 20, 1);  combat_flee(&c, &m, 1); CHECK(c.end == 17, "fuite malchanceuse = -3, vu %u", c.end);

    /* Paragraphe 12 : "les coups de votre adversaire vous infligent une double
     * blessure. Vous perdrez donc 4 points d'ENDURANCE en vous echappant." */
    m.damage = 4;
    c = hero(9, 20, 9);  combat_flee(&c, &m, 0); CHECK(c.end == 16, "fuite du GEANT = -4, vu %u", c.end);
    c = hero(9, 20, 12); combat_flee(&c, &m, 1); CHECK(c.end == 17, "fuite chanceuse = -3, vu %u", c.end);
    c = hero(9, 20, 1);  combat_flee(&c, &m, 1); CHECK(c.end == 15, "fuite malchanceuse = -5, vu %u", c.end);
}

static void test_memoire_clairieres(void)
{
    /* "conservez ces indications car il est possible que vous reveniez plus
     * tard dans cette clairiere [...] reprendre le combat la ou vous l'aviez
     * laisse." */
    Monster m[3];
    unsigned char snapshot[MONSTER_MEMORY_SIZE];
    monster_memory_reset();

    monster_init(&m[0]); m[0].hab = 9; m[0].end = 12; strcpy(m[0].name, "GEANT");
    monster_seal(&m[0]);
    CHECK(m[0].end0 == 12, "l'ENDURANCE de depart est figee, vu %u", m[0].end0);
    CHECK(monster_enter(12, m, 1) == 0, "premiere visite : on commence au premier");
    CHECK(m[0].end == 12, "premiere visite : l'ENDURANCE du livre, vu %u", m[0].end);

    m[0].end = 4;
    monster_remember(12, 0, &m[0]);
    CHECK(m[0].end0 == 12, "la jauge garde le maximum du livre, vu %u", m[0].end0);

    monster_init(&m[0]); m[0].hab = 9; m[0].end = 12;   /* la page redonne le livre */
    CHECK(monster_enter(12, m, 1) == 0, "retour : le combat reprend");
    CHECK(m[0].end == 4, "retour : ENDURANCE entamee, vu %u", m[0].end);

    m[0].end = 0; monster_remember(12, 0, &m[0]);
    m[0].end = 12;
    CHECK(monster_enter(12, m, 1) == 1, "creature morte : la file est finie");

    monster_init(&m[0]); m[0].end = 9;
    CHECK(monster_enter(300, m, 1) == 0 && m[0].end == 9, "clairiere jamais visitee");

    /* Le seuil du paragraphe 12 : "si vous parvenez a reduire a 6 les points
     * d'ENDURANCE du Geant, rendez-vous au 61". Le combat cesse a 6, pas a 0. */
    monster_init(&m[0]); m[0].end = 12; m[0].stop_at = 6;
    CHECK(monster_is_beaten(&m[0]) == 0, "12 > 6 : le combat continue");
    m[0].end = 6;
    CHECK(monster_is_beaten(&m[0]) == 1, "a 6, le Geant flechit");
    monster_remember(200, 0, &m[0]);
    m[0].end = 12;
    CHECK(monster_enter(200, m, 1) == 1, "retour : le seuil est deja atteint");
    monster_remember(200, 1, &m[0]); /* index avance par le moteur au seuil */
    m[0].end = 12;
    CHECK(monster_enter(200, m, 1) == 1, "un meme seuil ne rejoue pas le combat");
    m[0].stop_at = 0; m[0].end = 12;
    CHECK(monster_enter(200, m, 1) == 0 && m[0].end == 6,
          "reprendre jusqu'a la mort conserve les six END restants");
    m[0].end = 0; monster_remember(200, 1, &m[0]); m[0].end = 12;
    CHECK(monster_enter(200, m, 1) == 1, "le dernier adversaire mort ne ressuscite pas");

    /* Une file : "vous devrez les combattre tous deux a tour de role"
     * (paragraphe 224, les deux LOUPS). Fuir devant le second puis revenir
     * doit reprendre AU SECOND, pas au premier. */
    monster_memory_reset();
    monster_init(&m[0]); m[0].hab = 7; m[0].end = 5;
    monster_init(&m[1]); m[1].hab = 6; m[1].end = 6;
    CHECK(monster_enter(224, m, 2) == 0, "premiere visite : le premier LOUP");

    m[0].end = 0;                       /* le premier tombe */
    m[1].end = 3;                       /* le second est entame, on fuit */
    monster_remember(224, 1, &m[1]);

    monster_init(&m[0]); m[0].hab = 7; m[0].end = 5;
    monster_init(&m[1]); m[1].hab = 6; m[1].end = 6;
    CHECK(monster_enter(224, m, 2) == 1, "retour : on reprend au second LOUP");
    CHECK(m[1].end == 3, "et il est toujours entame, vu %u", m[1].end);
    CHECK(m[0].end == 5, "le premier n'est pas ressuscite pour autant, vu %u", m[0].end);

    /* C'est ce bloc exact que PARTIE0..PARTIE9 ecrivent sur disque. Une
     * extinction/reprise doit donc conserver l'adversaire courant et sa
     * blessure, pas seulement un retour dans la meme session. */
    monster_memory_export(snapshot);
    monster_memory_reset();
    monster_memory_import(snapshot);
    monster_init(&m[0]); m[0].hab = 7; m[0].end = 5;
    monster_init(&m[1]); m[1].hab = 6; m[1].end = 6;
    CHECK(monster_enter(224, m, 2) == 1,
          "sauvegarde combat : reprise au second LOUP");
    CHECK(m[1].end == 3,
          "sauvegarde combat : blessure conservee, vu %u", m[1].end);

    m[1].end = 0; monster_remember(224, 1, &m[1]);
    monster_init(&m[1]); m[1].hab = 6; m[1].end = 6;
    CHECK(monster_enter(224, m, 2) == 2, "les deux tombes : plus de combat");
}

/* La file de TROIS du paragraphe 120 : "ses deux creatures bondissent sur
 * vous. Vous devez les combattre tour a tour. Si vous les tuez, il faudra
 * ensuite affronter le Maitre lui-meme." Deux Loups puis leur Maitre, dans
 * l'ordre des lignes M -- et la clairiere 32 est de celles ou l'on revient.
 *
 * C'est le combat sur lequel un joueur a signale que l'ecran montrait le
 * Maitre du debut a la fin. La file, elle, etait juste : ces verifications
 * fixent l'invariant que le portrait doit suivre (scoswamp.c, ligne MI). */
static void file_120(Monster* m)
{
    monster_init(&m[0]); m[0].hab = 7;  m[0].end = 5;  strcpy(m[0].name, "PREMIER LOUP");
    monster_init(&m[1]); m[1].hab = 6;  m[1].end = 6;  strcpy(m[1].name, "DEUXIEME LOUP");
    monster_init(&m[2]); m[2].hab = 11; m[2].end = 10; strcpy(m[2].name, "MAITRE DES LOUPS");
    monster_seal(&m[0]); monster_seal(&m[1]); monster_seal(&m[2]);
}

static void test_file_120(void)
{
    Monster m[3];
    unsigned char snapshot[MONSTER_MEMORY_SIZE];

    monster_memory_reset();
    file_120(m);
    CHECK(monster_enter(120, m, 3) == 0,
          "premier passage : on commence au PREMIER LOUP, pas au Maitre");
    CHECK(m[0].end == 5 && m[1].end == 6 && m[2].end == 10,
          "premier passage : les trois sont entiers");

    /* Le premier Loup tombe : run_combat avance la file PUIS retient le
     * suivant, entier. C'est cet appel-la qu'on rejoue ici. */
    m[0].end = 0;
    monster_remember(120, 1, &m[1]);
    file_120(m);
    CHECK(monster_enter(120, m, 3) == 1, "revisite : au DEUXIEME LOUP");
    CHECK(m[1].end == 6, "le second n'a pas encore ete touche, vu %u", m[1].end);
    CHECK(m[1].end0 == 6, "sa jauge garde le maximum du livre, vu %u", m[1].end0);

    /* On l'entame et on fuit : la Fuite retient l'adversaire courant. */
    m[1].end = 2;
    monster_remember(120, 1, &m[1]);
    file_120(m);
    CHECK(monster_enter(120, m, 3) == 1, "retour apres la Fuite : au DEUXIEME");
    CHECK(m[1].end == 2, "et il est toujours entame, vu %u", m[1].end);
    CHECK(m[2].end == 10, "le Maitre attend son tour, entier, vu %u", m[2].end);

    /* Le second tombe a son tour : reste le Maitre, entier. */
    m[1].end = 0;
    monster_remember(120, 2, &m[2]);
    file_120(m);
    CHECK(monster_enter(120, m, 3) == 2, "les deux Loups tombes : au MAITRE");
    CHECK(m[2].end == 10, "le Maitre est intact, vu %u", m[2].end);

    /* Fuir DEVANT le Maitre entame, puis revenir, en passant par le disque. */
    m[2].end = 4;
    monster_remember(120, 2, &m[2]);
    monster_memory_export(snapshot);
    monster_memory_reset();
    monster_memory_import(snapshot);
    file_120(m);
    CHECK(monster_enter(120, m, 3) == 2,
          "sauvegarde : la reprise reste au troisieme adversaire");
    CHECK(m[2].end == 4, "sauvegarde : le Maitre reste blesse, vu %u", m[2].end);

    /* Le Maitre tombe : foe_cur vaut alors 3, et c'est CE nombre-la que
     * run_combat retient. La file est finie, la page part sur sa ligne MV. */
    m[2].end = 0;
    monster_remember(120, 3, &m[2]);
    file_120(m);
    CHECK(monster_enter(120, m, 3) == 3, "les trois tombes : plus de combat");
    CHECK(m[0].end == 5 && m[2].end == 10,
          "file finie : monster_enter ne touche a aucune ENDURANCE");

    /* Un adversaire acheve juste avant la Fuite : la memoire retient l'indice
     * courant avec une ENDURANCE nulle, et la reprise saute au suivant. */
    monster_memory_reset();
    file_120(m);
    m[0].end = 0;
    monster_remember(120, 0, &m[0]);
    file_120(m);
    CHECK(monster_enter(120, m, 3) == 1,
          "acheve puis fuite : la reprise passe au DEUXIEME LOUP");

    /* Une AUTRE clairiere garde ses propres Loups : le 224 (Pierre de Terreur)
     * n'herite pas des blessures du 120. */
    monster_memory_reset();
    file_120(m);
    m[0].end = 1;
    monster_remember(120, 0, &m[0]);
    file_120(m);
    CHECK(monster_enter(224, m, 2) == 0 && m[0].end == 5,
          "le 224 ne lit pas la memoire du 120");
}

static void test_pierres(void)
{
    Character c = hero(11, 20, 9);
    Stone s;

    /* Les trois categories */
    CHECK(stone_kind(STONE_HABILETE)    == STONE_NEUTRE,    "HABILETE neutre");
    CHECK(stone_kind(STONE_ILLUSION)    == STONE_NEUTRE,    "ILLUSION neutre");
    CHECK(stone_kind(STONE_AMITIE)      == STONE_BENEFIQUE, "AMITIE benefique");
    CHECK(stone_kind(STONE_BENEDICTION) == STONE_BENEFIQUE, "BENEDICTION benefique");
    CHECK(stone_kind(STONE_TERREUR)     == STONE_MALEFIQUE, "TERREUR malefique");
    CHECK(stone_kind(STONE_MALEDICTION) == STONE_MALEFIQUE, "MALEDICTION malefique");

    /* Aucune categorie ne doit etre vide : choose_stones dresse sa liste en
     * filtrant les douze Pierres par leur categorie, et si le filtre ne rend
     * rien il abandonne le choix EN SILENCE (`count == 0` -> choose_n = 0).
     * Une ligne PC citant une categorie sans Pierre ne donnerait donc rien,
     * exactement comme la ligne PC absente du 173 (Pompatarte).
     * Le compte, lui, tient la liste dans les 20 lignes de l'ecran. */
    {
        int par_kind[3];
        par_kind[0] = par_kind[1] = par_kind[2] = 0;
        for (s = 0; s < STONE_COUNT; ++s) par_kind[stone_kind(s)]++;
        CHECK(par_kind[STONE_NEUTRE]    == 6, "6 Pierres neutres (PC ... N)");
        CHECK(par_kind[STONE_BENEFIQUE] == 3, "3 Pierres benefiques (PC ... B)");
        CHECK(par_kind[STONE_MALEFIQUE] == 3, "3 Pierres malefiques (PC ... M)");
    }

    /* Reconnaissance des noms, telle que les pages les ecrivent */
    CHECK(stone_from_name("Feu")         == STONE_FEU,         "Feu");
    CHECK(stone_from_name("fletrissure") == STONE_FLETRISSURE, "casse ignoree");
    CHECK(stone_from_name("FIRE")        == STONE_FEU,         "nom anglais");
    CHECK(stone_from_name("Pouet")       == STONE_COUNT,       "nom inconnu");
    for (s = 0; s < STONE_COUNT; ++s) {
        CHECK(stone_from_name(stone_name(s, 0)) == s, "aller-retour FR %d", (int)s);
        CHECK(stone_from_name(stone_name(s, 1)) == s, "aller-retour EN %d", (int)s);
    }

    /* "vous aurez le droit de prendre plusieurs pierres semblables" */
    character_give_stone(&c, STONE_FEU, 4);
    CHECK(character_has_stone(&c, STONE_FEU) == 4, "4 Pierres de Feu");

    /* "les Pierres de Magie se desintegrent des qu'on les a utilisees" */
    CHECK(stone_use(&c, STONE_FEU, 0) == STONE_USE_OK, "usage");
    CHECK(character_has_stone(&c, STONE_FEU) == 3, "une pierre consommee");
    CHECK(stone_use(&c, STONE_GLACE, 0) == STONE_USE_NONE, "pierre absente");

    /* "un nombre de points egal a la moitie de votre total de depart (si ce
     * total est impair, arrondissez au chiffre superieur)" : 11 -> 6 */
    c = hero(11, 20, 9);
    c.hab = 2;
    character_give_stone(&c, STONE_HABILETE, 1);
    CHECK(stone_use(&c, STONE_HABILETE, 0) == STONE_USE_OK, "pierre d'HABILETE");
    CHECK(c.hab == 8, "2 + 6 = 8, vu %u", c.hab);

    /* et jamais au-dela du total de depart */
    c = hero(11, 20, 9);
    c.hab = 10;
    character_give_stone(&c, STONE_HABILETE, 1);
    stone_use(&c, STONE_HABILETE, 0);
    CHECK(c.hab == 11, "plafonnee au depart, vu %u", c.hab);

    /* "il vous est interdit de vous en servir sitot que le premier coup a ete
     * donne" -- et la pierre ne doit pas etre consommee pour autant. */
    c = hero(11, 20, 9);
    c.end = 5;
    character_give_stone(&c, STONE_ENDURANCE, 1);
    CHECK(stone_use(&c, STONE_ENDURANCE, 1) == STONE_USE_FORBIDDEN, "interdite en combat");
    CHECK(character_has_stone(&c, STONE_ENDURANCE) == 1, "pierre non consommee");
    CHECK(c.end == 5, "aucun effet");
    CHECK(stone_use(&c, STONE_ENDURANCE, 0) == STONE_USE_OK, "autorisee hors combat");
    CHECK(c.end == 15, "5 + 10, vu %u", c.end);

    /* Les autres pierres restent utilisables pendant un combat. */
    c = hero(11, 20, 9);
    character_give_stone(&c, STONE_TERREUR, 1);
    CHECK(stone_use(&c, STONE_TERREUR, 1) == STONE_USE_OK, "TERREUR en combat");

    /* "vous devrez lancer un de et reduire votre total d'ENDURANCE d'un
     * nombre de points equivalant au chiffre obtenu." */
    {
        int i;
        dice_seed(3);
        for (i = 0; i < 200; ++i) {
            Character d = hero(11, 20, 9);
            character_give_stone(&d, STONE_MALEDICTION, 1);
            stone_use(&d, STONE_MALEDICTION, 0);
            CHECK(d.end >= 14 && d.end <= 19,
                  "MALEDICTION coute 1d6 ENDURANCE, vu %u", d.end);
        }
    }
}

static void test_objets(void)
{
    Character c = hero(9, 20, 8);
    c.objects = 0;
    CHECK(object_from_name("inconnu") == OBJ_COUNT, "objet inconnu");
    CHECK(object_from_name("BJ") == OBJ_BIJOU, "bijou violet reconnu");
    CHECK(object_from_name("CO") == OBJ_CORNE, "corne de licorne reconnue");
    CHECK(object_from_name("PL") == OBJ_PLUMES, "plumes reconnues");
    character_give_object(&c, OBJ_BIJOU);
    character_give_object(&c, OBJ_CORNE);
    character_give_object(&c, OBJ_PLUMES);
    CHECK(character_has_object(&c, OBJ_BIJOU), "bijou entre dans le sac");
    CHECK(character_has_object(&c, OBJ_CORNE), "corne entre dans le sac");
    CHECK(character_has_object(&c, OBJ_PLUMES), "plumes entrent dans le sac");
    character_take_object(&c, OBJ_BIJOU);
    CHECK(!character_has_object(&c, OBJ_BIJOU), "bijou remis quitte le sac");
    /* Les Graines d'Arbres-Epees (pages 362 et 393, ramassees au 022,
     * repandues au 228) : le jeton du corpus doit tomber sur un objet
     * VISIBLE, sans quoi la page les donne dans le vide et le sac reste
     * muet -- c'est exactement le bug qu'on a eu. */
    CHECK(object_from_name("GR") == OBJ_GRAINES, "graines reconnues");
    character_give_object(&c, OBJ_GRAINES);
    CHECK(character_has_object(&c, OBJ_GRAINES), "graines entrent dans le sac");
    CHECK(OBJ_GRAINES < OBJ_HIDDEN0, "les graines sont un objet, pas un drapeau");
    CHECK(object_name(OBJ_GRAINES, 0)[0] && object_name(OBJ_GRAINES, 1)[0],
          "les graines ont un nom dans les deux langues");
    character_take_object(&c, OBJ_GRAINES);
    CHECK(!character_has_object(&c, OBJ_GRAINES), "graines repandues au 228");
    /* Tout ce qui precede OBJ_HIDDEN0 se montre, donc doit se nommer ; tout
     * ce qui suit est un fait narratif et reste anonyme. */
    {
        int k;
        for (k = 0; k < OBJ_COUNT; ++k)
            CHECK((object_name((Object)k, 0)[0] != '\0') == (k < OBJ_HIDDEN0),
                  "objet %d : nom present si et seulement si visible", k);
    }
    c.amulets = 0;
    CHECK(amulet_from_name("ARAIGNEE") == AMULET_ARAIGNEE, "amulette araignee");
    CHECK(amulet_from_name("FAUX") == AMULET_FAUSSE_OISEAU,
          "fausse amulette distincte");
    CHECK(character_amulet_count(&c) == 0, "aucune amulette au depart");
    character_give_amulet(&c, AMULET_LOUP);
    CHECK(character_amulet_count(&c) == 1, "palier Stratagus : une amulette");
    character_give_amulet(&c, AMULET_FLEUR);
    CHECK(character_amulet_count(&c) == 2, "palier Stratagus : deux amulettes");
    character_give_amulet(&c, AMULET_OISEAU);
    character_give_amulet(&c, AMULET_ARAIGNEE);
    character_give_amulet(&c, AMULET_GRENOUILLE);
    CHECK(character_amulet_count(&c) == 5, "les cinq vraies amulettes sont distinctes");
    character_give_amulet(&c, AMULET_FAUSSE_OISEAU);
    CHECK(character_has_amulet(&c, AMULET_OISEAU), "l'amulette Oiseau authentique reste presente");
    CHECK(character_has_amulet(&c, AMULET_FAUSSE_OISEAU), "la fausse Oiseau a son propre bit");
    CHECK(character_amulet_count(&c) == 6,
          "la fausse trompe Stratagus sans remplacer l'authentique");
    c.gold=20;
    CHECK(character_trade_amulets(&c,500)==6, "six amulettes remises");
    CHECK(c.gold==3020, "500 pieces par amulette, vu %u",c.gold);
    CHECK(character_amulet_count(&c)==0, "les amulettes remises quittent le sac");
}

static void test_perte_definitive(void)
{
    /* "vous perdez 2 points d'HABILETE et devez reduire aussi de 2 points
     * votre total initial d'HABILETE. Vous ne pourrez plus jamais retrouver
     * tous vos points de depart" (paragraphe 87). */
    Character c = hero(11, 20, 8);
    character_shift0(&c, 1, -2);
    CHECK(c.hab0 == 9, "le plafond descend a 9, vu %u", c.hab0);
    CHECK(c.hab  == 9, "la valeur courante suit, vu %u", c.hab);

    /* Et rien ne la rend : le soin plafonne au nouveau total. */
    character_adjust_hab(&c, +5);
    CHECK(c.hab == 9, "le soin s'arrete au nouveau plafond, vu %u", c.hab);

    /* "vous perdez 2 points [...] et devez reduire aussi de 2 points votre
     * total initial" : une HABILETE deja entamee perd ses 2 points elle aussi. */
    c = hero(11, 20, 8); c.hab = 4;
    character_shift0(&c, 1, -2);
    CHECK(c.hab == 2 && c.hab0 == 9, "4-2 sous un plafond de 9, vu %u/%u", c.hab, c.hab0);

    /* Le plafond ne tombe jamais a zero : ce serait une mort que le livre ne
     * prononce pas. La valeur courante, elle, a le plancher ordinaire. */
    c = hero(11, 20, 8);
    character_shift0(&c, 1, -50);
    CHECK(c.hab0 == 1 && c.hab == 0, "plafond a 1, valeur a 0, vu %u/%u", c.hab, c.hab0);
}

static void test_benediction(void)
{
    /* Grognard benit le paladin au village, avant le Marais, ou la CHANCE est
     * encore a son total de depart : les 2 points relevent le plafond, sinon
     * ils ne donneraient rien (paragraphe 155). */
    Character c = hero(11, 20, 8);
    character_shift0(&c, 2, +2);
    CHECK(c.cha0 == 10, "le plafond monte a 10, vu %u", c.cha0);
    CHECK(c.cha  == 10, "les points sont donnes tout de suite, vu %u", c.cha);

    /* Une CHANCE deja entamee (page 272, -2, puis retour vers Grognard)
     * recoit ses 2 points ET garde le nouveau plafond pour plus tard. */
    c = hero(11, 20, 8); c.cha = 6;
    character_shift0(&c, 2, +2);
    CHECK(c.cha == 8 && c.cha0 == 10, "6+2 sous un plafond de 10, vu %u/%u", c.cha, c.cha0);
    character_adjust_cha(&c, +5);
    CHECK(c.cha == 10, "le rattrapage s'arrete au plafond releve, vu %u", c.cha);
}

/* Le test de la ligne `V <cible> [<page> ...]`, tel que classify_line le joue :
 * la page courante, puis la cible, puis chaque page citee. Le moteur vit dans
 * scoswamp.c, qui n'est pas lie ici -- mais la REGLE, elle, ne tient qu'au
 * bitmap de rules.c, et c'est elle qu'on verifie. */
static int detour_clairiere(unsigned int courante, unsigned int cible,
                            const unsigned int* autres, unsigned int n)
{
    unsigned int i;
    if (scene_visited(courante) || scene_visited(cible)) return 1;
    for (i = 0; i < n; ++i)
        if (scene_visited(autres[i])) return 1;
    return 0;
}

static void test_clairieres_vues(void)
{
    /* "Si vous y etes deja venu, rendez-vous au 142. Sinon, lisez ce qui
     * suit." Vingt-six pages ouvrent la-dessus ; c'est ce drapeau qui les
     * departage, la ou le livre s'en remettait a la memoire du joueur. */
    unsigned int i;
    unsigned char snapshot[SCENE_MEMORY_SIZE];
    scene_memory_reset();

    CHECK(scene_visited(10) == 0, "au depart, aucune clairiere n'est vue");
    scene_mark_visited(10);
    CHECK(scene_visited(10) == 1, "la clairiere 10 est retenue");
    CHECK(scene_visited(11) == 0, "sa voisine ne l'est pas");
    CHECK(scene_visited(2)  == 0, "ni celle qui partage son octet");

    /* Export/import est le chemin utilise par les dix sauvegardes. */
    scene_memory_export(snapshot);
    scene_memory_reset();
    CHECK(scene_visited(10) == 0, "la RAM remise a zero oublie la clairiere");
    scene_memory_import(snapshot);
    CHECK(scene_visited(10) == 1,
          "sauvegarde : la scene deja visitee est restauree");

    /* La derniere scene mecanique est la 411 : elle doit tenir, et ce qui la
     * depasse doit repondre non plutot que d'ecrire hors du tableau. */
    scene_mark_visited(411);
    CHECK(scene_visited(411) == 1, "la derniere scene tient");
    scene_mark_visited(9999);
    CHECK(scene_visited(9999) == 0, "hors bornes : non, et rien d'ecrit");

    /* Une mort remet le marais a neuf : sans cela la partie suivante sauterait
     * les descriptions longues de clairieres ou elle n'est jamais allee. */
    scene_memory_reset();
    for (i = 0; i < 412; ++i)
        if (scene_visited(i)) { CHECK(0, "la remise a zero a laisse %u", i); break; }

    /* La clairiere 30, une seule porte : `V 382 270` sur la page 041.
     * Marquer 041 doit lever le detour, et NE PAS marquer 382 ni 270 --
     * c'est la page de revisite qui sera marquee a son tour, par load_scene. */
    {
        static const unsigned int clr30[] = { 270u };
        scene_memory_reset();
        CHECK(detour_clairiere(41, 382, clr30, 1) == 0,
              "premiere visite des Sables Mouvants : pas de detour");
        scene_mark_visited(41);
        CHECK(scene_visited(382) == 0, "041 vue ne marque pas 382");
        CHECK(scene_visited(270) == 0, "041 vue ne marque pas le hub 270");
        CHECK(detour_clairiere(41, 382, clr30, 1) == 1,
              "revenir en 041 renvoie bien au 382");
    }

    /* La clairiere 13, deux portes : `V 303 319` sur la page 118. Le pont
     * (045) depose au sud sur 303, la page de revisite ; le sentier de l'est
     * depose sur 118. Entrer par l'une puis par l'autre ne doit pas rejouer
     * la nuee de Scorpions -- c'etait le bug : le bitmap disait "page vue",
     * le livre dit "clairiere deja visitee". */
    {
        static const unsigned int clr13[] = { 319u };
        scene_memory_reset();
        CHECK(detour_clairiere(118, 303, clr13, 1) == 0,
              "jamais venu : la premiere visite se joue");
        scene_mark_visited(303);            /* entree par le pont */
        CHECK(scene_visited(118) == 0, "303 vue ne marque pas 118");
        CHECK(detour_clairiere(118, 303, clr13, 1) == 1,
              "deja passe par la revisite : arriver en 118 detourne");
        scene_memory_reset();
        scene_mark_visited(319);            /* seulement la page-hub */
        CHECK(detour_clairiere(118, 303, clr13, 1) == 1,
              "le hub 319 vu suffit a dire que la clairiere est connue");
        scene_memory_reset();
        scene_mark_visited(117);            /* une page d'une AUTRE clairiere */
        CHECK(detour_clairiere(118, 303, clr13, 1) == 0,
              "une page voisine non citee ne declenche rien");
    }
}


/* ── La carte : le rabattement page -> clairiere ──────────────────────────
 *
 * Le fichier MAP est une donnee du disque, comme les pages : ces tests le
 * lisent la ou build_map.py l'ecrit et rejouent, a l'identique, les deux
 * boucles du moteur (map_of_page et map_seen dans scoswamp.c). Le moteur
 * lui-meme ne peut pas etre lie ici -- il parle a ProDOS et a l'ecran -- mais
 * la table, elle, est de l'arithmetique pure, et c'est elle qui decide quelle
 * clairiere la touche M montre.
 */
#define MAP_CLR    35
#define MAP_PAGES  115
#define MAP_NAMEW  13
#define MAP_HEAD   20
#define MAP_POOL   (MAP_HEAD + 3 * MAP_CLR)
#define MAP_NONE   0xFF

static unsigned char carte[2048];
static unsigned char carte_pages[2 * MAP_PAGES];
static int carte_ok;

/* La copie conforme de map_of_page() : meme table, meme boucle. */
static unsigned char map_of_page(unsigned int page)
{
    unsigned char i;
    unsigned int p = 0;
    const unsigned char* t = carte_pages;

    for (i = MAP_PAGES; i; --i) {
        p += *t++;
        if (p >= page) return (p == page) ? *t : MAP_NONE;
        ++t;
    }
    return MAP_NONE;
}

/* La copie conforme de map_seen() : une clairiere est vue des qu'UNE de ses
 * pages l'est, quelle que soit la porte par laquelle on y est entre. */
static void map_seen(unsigned char* out)
{
    unsigned char i;
    unsigned int p = 0;
    const unsigned char* t = carte_pages;

    memset(out, 0, MAP_CLR);
    for (i = MAP_PAGES; i; --i) {
        p += *t++;
        if (scene_visited(p)) out[*t] = 1;
        ++t;
    }
}

static const char* clr_nom(unsigned char i)
{
    return (const char*)(carte + MAP_POOL + MAP_NAMEW * (unsigned)i);
}

static void charger_carte(void)
{
    static const char* const chemins[] = {
        "SCOSWAMP/MAP.BIN", "../SCOSWAMP/MAP.BIN", "../../SCOSWAMP/MAP.BIN",
        "../../../SCOSWAMP/MAP.BIN", "../../../../SCOSWAMP/MAP.BIN"
    };
    unsigned i;
    FILE* f = NULL;
    size_t n;

    for (i = 0; i < sizeof chemins / sizeof *chemins && !f; ++i)
        f = fopen(chemins[i], "rb");
    if (!f) { printf("SAUTE carte : MAP.BIN introuvable\n"); return; }
    n = fread(carte, 1, sizeof carte, f);
    fclose(f);
    CHECK(n > MAP_POOL + 2 * MAP_PAGES, "MAP.BIN tronque : %u octets", (unsigned)n);
    CHECK(memcmp(carte, "MAP\3", 4) == 0, "MAP.BIN : signature absente");
    CHECK(carte[4] == MAP_CLR, "MAP.BIN : %u clairieres, 35 attendues", carte[4]);
    CHECK(carte[5] == MAP_PAGES, "MAP.BIN : %u pages, 115 attendues", carte[5]);
    CHECK(carte[6] == MAP_NAMEW, "MAP.BIN : noms de %u octets", carte[6]);
    if (n <= MAP_POOL + 2 * MAP_PAGES) return;
    memcpy(carte_pages, carte + MAP_POOL, sizeof carte_pages);
    /* Le bloc francais suit la table des pages ; le moteur le lit a la meme
     * adresse (trois freads d'affilee), ici on le ramene sur place pour que
     * clr_nom() vise juste. */
    memmove(carte + MAP_POOL, carte + MAP_POOL + sizeof carte_pages,
            n - MAP_POOL - sizeof carte_pages);
    carte_ok = 1;
}

static void test_carte(void)
{
    unsigned char vu[MAP_CLR];
    unsigned char depart, i;
    unsigned int p, prec;
    const unsigned char* t;

    charger_carte();
    if (!carte_ok) return;

    /* La table est TRIEE et sans doublon : c'est ce qui autorise la sortie
     * anticipee de map_of_page des que la page cherchee est depassee. */
    prec = 0;
    t = carte_pages;
    for (i = 0; i < MAP_PAGES; ++i) {
        p = prec + *t++;
        CHECK(p > prec || i == 0, "table des pages non croissante en %u", i);
        CHECK(p < 412u, "page %u hors du corpus", p);
        CHECK(*t < MAP_CLR, "page %u renvoie a la clairiere %u", p, *t);
        ++t;
        prec = p;
    }

    /* Le depart : page 195, la Clairiere n 1, le rond-point.
     * L'en-tete : 0-3 magie, 4 clairieres, 5 pages, 6 largeur d'un nom,
     * 7 clairiere de depart, 8 le pont, 9 la ligne de la riviere. */
    depart = carte[7];
    CHECK(map_of_page(195) == depart, "la page 195 n'est pas la clairiere de depart");
    CHECK(carte[MAP_HEAD + 3 * depart + 1] == 1,
          "la clairiere de depart ne porte pas le numero 1 du livre");
    CHECK(strcmp(clr_nom(depart), "Rond-point") == 0,
          "la clairiere de depart s'appelle %s", clr_nom(depart));

    /* Les deux portes de la clairiere 13 : le sentier de l'est depose sur
     * 118, le pont depose au sud sur 303. Le meme lieu, deux pages -- c'est
     * exactement ce que les listes des lignes V disent page par page. */
    CHECK(map_of_page(118) == map_of_page(303),
          "118 et 303 devraient etre la meme clairiere");
    CHECK(map_of_page(118) != MAP_NONE, "118 n'est rattachee a aucun lieu");

    /* Les trois arbitrages de CARTOGRAPHIE.md Sec. 6.1 I. */
    CHECK(map_of_page(363) == map_of_page(234), "363 va au Patrouilleur (clr 19)");
    CHECK(map_of_page(394) == map_of_page(31),  "394 va au Bassin de cristal (clr 21)");
    CHECK(map_of_page(330) == map_of_page(390), "330 va aux Pierres et tronc (clr 12)");
    CHECK(map_of_page(363) != map_of_page(84),  "363 n'est PAS le Maitre des Jardins");
    CHECK(map_of_page(330) != map_of_page(82),  "330 n'est PAS la Bete du bassin");

    /* Les pages qui ne sont d'aucun lieu : le prologue, les combats, la
     * sortie du Marais. La clairiere courante doit alors rester COLLANTE --
     * c'est le moteur qui s'en charge, la table dit seulement "aucune". */
    CHECK(map_of_page(1) == MAP_NONE,   "la page 1 est le prologue, hors Marais");
    CHECK(map_of_page(134) == MAP_NONE, "le combat de l'Herbe a Pinces n'est pas un lieu");
    CHECK(map_of_page(208) == MAP_NONE, "la sortie sud est la route, pas la clairiere");
    CHECK(map_of_page(0) == MAP_NONE,   "l'ecran d'accueil n'est pas un lieu");

    /* Le brouillard de guerre : une seule page vue allume sa clairiere, et
     * elle seule. */
    scene_memory_reset();
    map_seen(vu);
    for (i = 0; i < MAP_CLR; ++i) CHECK(vu[i] == 0, "clairiere %u vue a blanc", i);

    scene_mark_visited(303);              /* on arrive par le pont */
    map_seen(vu);
    CHECK(vu[map_of_page(118)] == 1, "arriver en 303 allume la clairiere 13");
    CHECK(vu[map_of_page(195)] == 0, "elle n'allume pas le rond-point");

    /* Toute page rattachee allume sa clairiere, et les 35 s'allument. */
    scene_memory_reset();
    t = carte_pages;
    p = 0;
    for (i = 0; i < MAP_PAGES; ++i) { p += *t++; ++t; scene_mark_visited(p); }
    map_seen(vu);
    for (i = 0; i < MAP_CLR; ++i)
        CHECK(vu[i] == 1, "clairiere %u restee eteinte, toutes pages vues", i);
    scene_memory_reset();
}

static void test_recuperation(void)
{
    Monster m;
    unsigned char snapshot[MONSTER_SLOTS * 4];
    monster_memory_reset(); monster_init(&m); m.end = 8;
    monster_recover(34, 1, 8);
    CHECK(monster_enter(34, &m, 1) == 0 && m.end == 8, "MR inconnu : aucune nouvelle rencontre");
    m.end = 3; monster_remember(34, 0, &m);
    monster_recover(34, 1, 8);
    monster_enter(34, &m, 1);
    CHECK(m.end == 4, "MR ours : trois plus un");
    monster_memory_export(snapshot); monster_memory_reset(); monster_memory_import(snapshot);
    m.end = 8; monster_enter(34, &m, 1);
    CHECK(m.end == 4, "MR persiste dans le format de sauvegarde existant");
    monster_recover(34, 255, 8); monster_enter(34, &m, 1);
    CHECK(m.end == 8, "MR gain 255 sans debordement et plafond huit");
    monster_recover(34, 1, 8); monster_enter(34, &m, 1);
    CHECK(m.end == 8, "MR ne depasse pas le maximum");
    m.end = 2; monster_remember(2, 0, &m);
    monster_recover(2, 255, 10); monster_enter(2, &m, 1);
    CHECK(m.end == 10, "MR Patrouilleur : recuperation complete");
    monster_enter(34, &m, 1); CHECK(m.end == 8, "MR isole les clairieres");
    m.end = 0; monster_remember(34, 1, &m);
    monster_recover(34, 255, 8); m.end = 8;
    CHECK(monster_enter(34, &m, 1) == 1, "MR ne ressuscite pas un mort");
}

int main(void)
{
    test_dice();
    test_creation();
    test_plafond();
    test_or();
    test_chance();
    test_assaut();
    test_blessures();
    test_fuite();
    test_memoire_clairieres();
    test_recuperation();
    test_file_120();
    test_clairieres_vues();
    test_perte_definitive();
    test_benediction();
    test_pierres();
    test_objets();
    test_carte();
    if (failures == 0) printf("regles : tout passe\n");
    else               printf("regles : %d echec(s)\n", failures);
    return failures != 0;
}
