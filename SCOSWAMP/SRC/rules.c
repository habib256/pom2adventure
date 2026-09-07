#include "rules.h"
#include "dice.h"
#include <string.h>

/* ── Les Pierres ─────────────────────────────────────────────────────────── */

static const char* const kStoneFr[STONE_COUNT] = {
    "HABILETE", "ENDURANCE", "CHANCE", "FEU", "GLACE", "ILLUSION",
    "AMITIE", "CROISSANCE", "BENEDICTION",
    "TERREUR", "FLETRISSURE", "MALEDICTION"
};

static const char* const kStoneEn[STONE_COUNT] = {
    "SKILL", "STAMINA", "LUCK", "FIRE", "ICE", "ILLUSION",
    "FRIENDSHIP", "GROWTH", "BLESSING",
    "FEAR", "WITHERING", "CURSE"
};

#pragma rodata-name (push, "LC")
static const char* const kObjectFr[OBJ_COUNT] = {
    "Anneau Cuivre", "Cape Rouge", "Chaine Or", "Aimant Or", "Fiole",
    "Baie Antherique", "Epee Magique", "Bijou Violet", "Corne Licorne",
    "Plumes de Perroquet", "Graines d'Arbre-Epee", "", "", "", "", ""
};
static const char* const kObjectEn[OBJ_COUNT] = {
    "Copper Ring", "Red Cape", "Gold Chain", "Gold Magnet", "Vial", "Antherique Berry",
    "Magic Sword", "Purple Jewel", "Unicorn Horn", "Parrot Feathers",
    "Sword Tree Seeds", "", "", "", "", ""
};
static const char* const kObjectKey[OBJ_COUNT] = {
    "ANNEAU", "CAPE", "CH", "AI", "FI", "BA", "EP", "BJ", "CO", "PL", "GR", ".T", ".G", ".P", ".S", ".D"
};
static const char* const kAmuletFr[AMULET_COUNT] = {
    "Amulette du Loup", "Amulette de la Fleur", "Amulette de l'Oiseau",
    "Amulette de l'Araignee", "Amulette de la Grenouille",
    "Fausse Amulette de l'Oiseau"
};
static const char* const kAmuletEn[AMULET_COUNT] = {
    "Wolf Amulet", "Flower Amulet", "Bird Amulet", "Spider Amulet",
    "Frog Amulet", "False Bird Amulet"
};
static const char* const kAmuletKey[AMULET_COUNT] = {
    "LOUP", "FLEUR", "OISEAU", "ARAIGNEE", "GRENOUILLE", "FAUX"
};
#pragma rodata-name (pop)

StoneKind stone_kind(Stone s)
{
    if (s >= STONE_TERREUR) return STONE_MALEFIQUE;
    if (s >= STONE_AMITIE)  return STONE_BENEFIQUE;
    return STONE_NEUTRE;
}

const char* stone_name(Stone s, int english)
{
    if (s < 0 || s >= STONE_COUNT) return "";
    return english ? kStoneEn[s] : kStoneFr[s];
}

static char upcase(char ch)
{
    return (ch >= 'a' && ch <= 'z') ? (char)(ch - 'a' + 'A') : ch;
}

static int same_name(const char* a, const char* b)
{
    while (*a && *b) {
        if (upcase(*a) != upcase(*b)) return 0;
        ++a; ++b;
    }
    return *a == *b;
}

#pragma code-name (push, "LC")
const char* object_name(Object o, int english)
{
    if (o < 0 || o >= OBJ_COUNT) return "";
    return english ? kObjectEn[o] : kObjectFr[o];
}

Object object_from_name(const char* name)
{
    int i;
    for (i = 0; i < OBJ_COUNT; ++i)
        if (same_name(name, kObjectKey[i])) return (Object)i;
    return OBJ_COUNT;
}

const char* amulet_name(Amulet a, int english)
{
    if (a < 0 || a >= AMULET_COUNT) return "";
    if (english) return kAmuletEn[a];
    return kAmuletFr[a];
}

Amulet amulet_from_name(const char* name)
{
    int i;
    for (i=0;i<AMULET_COUNT;i++) if (same_name(name,kAmuletKey[i])) return (Amulet)i;
    return AMULET_COUNT;
}
#pragma code-name (pop)

Stone stone_from_name(const char* name)
{
    int i;
    for (i = 0; i < STONE_COUNT; ++i) {
        if (same_name(name, kStoneFr[i]) || same_name(name, kStoneEn[i])) {
            return (Stone)i;
        }
    }
    return STONE_COUNT;
}

/* ── La Feuille d'Aventure ───────────────────────────────────────────────── */

void character_roll(Character* c)
{
    int i;

    c->hab0 = c->hab = (unsigned char)(roll_d6()  + 6);
    c->end0 = c->end = (unsigned char)(roll_2d6() + 12);
    c->cha0 = c->cha = (unsigned char)(roll_d6()  + 6);

    /* "quelques Pieces d'Or qui vous permettront de subvenir a de menues
     * depenses" : le livre ne chiffre pas, le corpus parle en dizaines. */
    c->gold       = 20;
    c->weapon_bonus = 0;
    for (i = 0; i < STONE_COUNT; ++i) c->stones[i] = 0;
    c->objects = (1u << OBJ_ANNEAU); /* l'Anneau de Cuivre est l'objet initial */
    c->amulets = 0;
}

#pragma code-name (push, "LC")
void character_give_object(Character* c, Object o)
{
    if (o >= 0 && o < OBJ_COUNT) c->objects |= (1u << o);
}

void character_take_object(Character* c, Object o)
{
    if (o >= 0 && o < OBJ_COUNT) c->objects &= ~(1u << o);
}

int character_has_object(const Character* c, Object o)
{
    return (o >= 0 && o < OBJ_COUNT) && (c->objects & (1u << o));
}

void character_give_amulet(Character* c, Amulet a)
{ if (a >= 0 && a < AMULET_COUNT) c->amulets |= (1u << a); }
int character_has_amulet(const Character* c, Amulet a)
{ return (a >= 0 && a < AMULET_COUNT) && (c->amulets & (1u << a)); }
#pragma code-name (push, "CODE")
unsigned char character_amulet_count(const Character* c)
{
    unsigned char bits=c->amulets, n=0;
    while (bits) { n += bits & 1; bits >>= 1; }
    return n;
}
unsigned char character_trade_amulets(Character* c, unsigned int each)
{
    unsigned char n=character_amulet_count(c);
    character_adjust_gold(c,(int)(n*each));
    c->amulets=0;
    return n;
}
#pragma code-name (pop)
#pragma code-name (pop)

/* Plancher a zero, plafond au total de depart. */
static void adjust(unsigned char* cur, unsigned char start, int delta)
{
    int v = (int)*cur + delta;
    if (v < 0)             v = 0;
    if (v > (int)start)    v = (int)start;
    *cur = (unsigned char)v;
}

void character_adjust_hab(Character* c, int d) { adjust(&c->hab, c->hab0, d); }
void character_adjust_end(Character* c, int d) { adjust(&c->end, c->end0, d); }
void character_adjust_cha(Character* c, int d) { adjust(&c->cha, c->cha0, d); }

/* Plancher a zero, et pas de plafond : "quelques Pieces d'Or qui vous
 * permettront de subvenir a de menues depenses", le livre n'en pose aucun.
 *
 * Le calcul passe par un `int` SIGNE -- c'est le seul moyen de voir la
 * soustraction descendre sous zero au lieu de repasser par le haut. Un
 * `gold += delta` ecrit a la main sur le champ non signe donnait 65 535
 * Pieces d'Or au heros sans le sou qui en depense une (page 078).
 *
 * Ce que ce choix borne implicitement : sur cc65 l'int fait 16 bits, donc la
 * bourse ne va pas au-dela de 32 767. Le corpus en distribue 370 en tout --
 * 20 au depart, 100 au 049, 250 au 266 -- et la borne est hors d'atteinte de
 * deux ordres de grandeur. La verifier couterait une comparaison 16 bits
 * signee, soit 20 octets sur un binaire qui n'en a plus 110 : on la
 * documente au lieu de la payer. */
void character_adjust_gold(Character* c, int d)
{
    int v = (int)c->gold + d;
    c->gold = (unsigned int)(v < 0 ? 0 : v);
}

/* Deplace le plafond ET la valeur courante, du meme pas.
 *
 * En perte (page 87) : "vous perdez 2 points d'HABILETE et devez reduire
 * aussi de 2 points votre total initial" -- les deux baissent de 2, et la
 * valeur courante reste sous son nouveau plafond. En gain (page 155) les
 * points sont donnes tout de suite ET restent rattrapables ensuite : le
 * plafond monte d'autant, la valeur courante aussi.
 *
 * La paire (valeur, total de depart) est atteinte par son rang dans la
 * structure -- voir le commentaire du typedef -- ce qui epargne trois
 * wrappers et deux `if` : 150 octets de cc65 que la fenetre n'avait plus.
 * Pas de borne haute non plus : les totaux tiennent sous 25 et le corpus ne
 * releve un plafond qu'une fois, de 2. */
void character_shift0(Character* c, unsigned char k, int delta)
{
    static const unsigned char pair[3] = { 2, 0, 4 };  /* END, HAB, CHA */
    unsigned char* v = &c->hab + pair[k];
    int n0 = (int)v[1] + delta;
    if (n0 < 1) n0 = 1;              /* une caracteristique nulle serait une mort */
    v[1] = (unsigned char)n0;
    adjust(v, (unsigned char)n0, delta);
}

int character_is_dead(const Character* c) { return c->end == 0; }

/* ── Tentez votre Chance ─────────────────────────────────────────────────── */

int luck_test(Character* c)
{
    unsigned char roll = roll_2d6();
    int lucky = (roll <= c->cha);

    /* Le point se paie meme quand la CHANCE est deja a zero -- auquel cas le
     * jet est perdu d'avance, ce que le livre assume : "plus vous vous fierez
     * a votre chance, plus vous courrez de risques". */
    if (c->cha > 0) --c->cha;
    return lucky;
}

/* ── Batailles ───────────────────────────────────────────────────────────── */

void monster_init(Monster* m)
{
    m->hab = 0; m->end = 0; m->end0 = 0;
    m->damage = 2; m->stop_at = 0; m->name[0] = '\0';
}

void monster_seal(Monster* m) { m->end0 = m->end; }

int monster_is_beaten(const Monster* m) { return m->end <= m->stop_at; }

void combat_round(const Character* c, const Monster* m, Round* out)
{
    /* Les des un par un, et non par roll_2d6 : c'est la meme somme -- donc la
     * meme partie a semence egale -- mais l'ecran peut ensuite montrer le jet
     * au lieu du seul total.
     *
     * L'assaut se compose dans `t` et ne touche `out` qu'a la toute fin, par
     * une seule affectation de structure. Cc65 ne garde pas un pointeur de
     * parametre : chaque `out->x` relit sp, reconstruit ptr1 et refait le
     * detour, une douzaine d'octets a chaque champ -- sept champs, quatre-
     * vingts octets de rechargement de pointeur. Avec -Cl les locales sont
     * statiques, donc `t` s'ecrit en adressage absolu (trois octets par
     * champ) et la copie finale est un memcpy de sept octets. */
    unsigned char a  = roll_d6();
    unsigned char b  = roll_d6();
    unsigned char d  = roll_d6();
    unsigned char e  = roll_d6();
    Round t;

    t.monster_d1 = a; t.monster_d2 = b;
    t.hero_d1    = d; t.hero_d2    = e;
    t.monster_force = (unsigned char)(a + b + m->hab);
    t.hero_force    = (unsigned char)(d + e + c->hab);
    if (c->hab && (c->objects & (1u << OBJ_POTION_NAINE))) --t.hero_force;
    if (c->objects & (1u << OBJ_EPEMAGIQUE))
        t.hero_force = (unsigned char)(t.hero_force + c->weapon_bonus);
    if (t.hero_force > t.monster_force)      t.outcome = ROUND_HERO_HITS;
    else if (t.hero_force < t.monster_force) t.outcome = ROUND_MONSTER_HITS;
    else                                     t.outcome = ROUND_DODGE;
    *out = t;
}

int combat_apply(Character* c, Monster* m, const Round* r, int use_luck)
{
    int lucky = 0;
    int dmg;

    if (r->outcome == ROUND_HERO_HITS) {
        dmg = 2;
        if (use_luck) {
            lucky = luck_test(c);
            /* "Chanceux : oter deux points de plus. Malchanceux : la blessure
             * n'etait qu'une simple ecorchure [...] vous n'aurez ote qu'un
             * seul point." */
            dmg = lucky ? 4 : 1;
        }
        m->end = (unsigned char)((m->end > dmg) ? (m->end - dmg) : 0);
    } else if (r->outcome == ROUND_MONSTER_HITS) {
        dmg = (int)m->damage;
        if (use_luck) {
            lucky = luck_test(c);
            /* "Chanceux : rajoutez un point d'ENDURANCE [...] Malchanceux :
             * enlevez encore un point." Le modificateur est de UN point, pas
             * une moitie : sur une blessure doublee il donne 3 ou 5. */
            dmg += lucky ? -1 : 1;
        }
        character_adjust_end(c, -dmg);
    }
    return lucky;
}

int combat_flee(Character* c, const Monster* m, int use_luck)
{
    int lucky = 0;
    /* "rappelez-vous que les coups de votre adversaire vous infligent une
     * double blessure. Vous perdrez donc 4 points d'ENDURANCE en vous
     * echappant" : la blessure de fuite est celle de la creature. */
    int dmg = (int)m->damage;

    if (use_luck) {
        lucky = luck_test(c);
        dmg += lucky ? -1 : 1;
    }
    character_adjust_end(c, -dmg);
    return lucky;
}

/* ── Memoire des clairieres ──────────────────────────────────────────────── */

/* Table clairsemee : seules les clairieres ou l'on a effectivement combattu y
 * figurent. `zone == 0` marque un emplacement libre -- la clairiere 0 est
 * l'ecran de titre, elle n'a pas d'adversaire. `index` retient lequel de la
 * file etait en cours ; sans lui, fuir devant le deuxieme LOUP puis revenir
 * ferait recommencer au premier. */
/* En RAM basse ($1000-$1FFF, segment LOWBSS de scoswamp.cfg), avec les gros
 * tampons : 160 octets de moins dans la fenetre principale, ou il n'en restait
 * que 89 apres la fusion du menu MAP, du prologue et du combat rythme. Rien ne
 * change a l'acces -- une adresse absolue en $1xxx vaut une adresse absolue en
 * $Bxxx -- ni a la sauvegarde, qui passe par monster_memory_export. */
#pragma bss-name (push, "LOWBSS")
static struct {
    unsigned int  scene;
    unsigned char index;
    unsigned char end;
} seen[MONSTER_SLOTS];
#pragma bss-name (pop)

void monster_memory_reset(void)
{
    memset(seen, 0, sizeof seen);
}

static int slot_of(unsigned int zone)
{
    int i;
    for (i = 0; i < MONSTER_SLOTS; ++i) if (seen[i].scene == zone) return i;
    return -1;
}

void monster_recover(unsigned int zone, unsigned char amount, unsigned char maximum)
{
    int i = slot_of(zone);
    unsigned int total;
    if (i < 0 || !seen[i].end || seen[i].end >= maximum) return;
    total = (unsigned int)seen[i].end + amount;
    seen[i].end = (unsigned char)(total > maximum ? maximum : total);
}

int monster_enter(unsigned int zone, Monster* foes, int count)
{
    int i = slot_of(zone);
    int idx;

    if (i < 0) return 0;                 /* jamais combattu ici */
    idx = (int)seen[i].index;
    if (idx >= count) {
        /* Une interruption au seuil MS laisse le dernier adversaire vivant.
         * Une nouvelle page peut reprendre ce combat avec un seuil plus bas.
         * Un adversaire mort, ou une autre longueur de file, ne ressuscite pas. */
        if (idx != count || !seen[i].end) return count;
        --idx;
    }
    foes[idx].end = seen[i].end;
    /* L'adversaire en cours peut avoir ete acheve juste avant la fuite. */
    if (monster_is_beaten(&foes[idx])) return idx + 1;
    return idx;
}

void monster_remember(unsigned int zone, int index, const Monster* m)
{
    int i = slot_of(zone);
    if (i < 0) i = slot_of(0);      /* premier emplacement libre */
    /* Table pleine : on oublie cette clairiere, ses adversaires seront de
     * nouveau entiers au prochain passage. Impossible avec les 26 du livre. */
    if (i >= 0) {
        seen[i].scene = zone;
        seen[i].index = (unsigned char)index;
        seen[i].end   = m->end;
    }
}

void monster_memory_export(unsigned char* out)
{
#ifdef __CC65__
    /* cc65 : unsigned int 16 bits little-endian, structure de quatre octets.
     * La representation native est exactement celle de SCS4/SCS5. */
    memcpy(out, seen, MONSTER_MEMORY_SIZE);
#else
    int i;
    for (i = 0; i < MONSTER_SLOTS; ++i) {
        *out++ = (unsigned char)seen[i].scene;
        *out++ = (unsigned char)(seen[i].scene >> 8);
        *out++ = seen[i].index;
        *out++ = seen[i].end;
    }
#endif
}

void monster_memory_import(const unsigned char* in)
{
#ifdef __CC65__
    memcpy(seen, in, MONSTER_MEMORY_SIZE);
#else
    int i;
    for (i = 0; i < MONSTER_SLOTS; ++i) {
        seen[i].scene = (unsigned int)in[0] | ((unsigned int)in[1] << 8);
        seen[i].index = in[2]; seen[i].end = in[3]; in += 4;
    }
#endif
}

/* ── Les clairieres deja parcourues ────────────────────────────────────── */

#define SCENE_BITS SCENE_MEMORY_SIZE /* 419 paragraphes arrondis a l'octet */

/* Le bitmap des pages vues part dans la zone MAPRAM ($0C00-$0FFF), avec les
 * donnees du menu MAP qui le lisent : 52 octets de moins dans la fenetre
 * principale, et rien de change pour qui l'appelle. */
#pragma bss-name (push, "MAPBSS")
static unsigned char visited[SCENE_BITS];
#pragma bss-name (pop)

void scene_memory_reset(void)
{
    unsigned int i;
    for (i = 0; i < SCENE_BITS; ++i) visited[i] = 0;
}

int scene_visited(unsigned int scene)
{
    if (scene >= SCENE_BITS * 8) return 0;
    return (visited[scene >> 3] & (1 << (scene & 7))) != 0;
}

void scene_mark_visited(unsigned int scene)
{
    if (scene < SCENE_BITS * 8) visited[scene >> 3] |= (1 << (scene & 7));
}

void scene_memory_export(unsigned char* out) { memcpy(out, visited, SCENE_BITS); }
void scene_memory_import(const unsigned char* in) { memcpy(visited, in, SCENE_BITS); }

/* ── La Magie ────────────────────────────────────────────────────────────── */

void character_give_stone(Character* c, Stone s, unsigned char n)
{
    if (s >= 0 && s < STONE_COUNT) {
        /* "vous aurez le droit de prendre plusieurs pierres semblables, par
         * exemple 4 Pierres de Feu." */
        unsigned int total = (unsigned int)c->stones[s] + n;
        c->stones[s] = (unsigned char)(total > 255u ? 255u : total);
    }
}

int character_has_stone(const Character* c, Stone s)
{
    return (s >= 0 && s < STONE_COUNT) ? c->stones[s] : 0;
}

int stone_usable(Stone s, int in_combat)
{
    if (in_combat == 2) return 0; /* rencontre interdisant toute magie */
    if (!in_combat) return 1;
    /* Seules les trois pierres de caracteristique sont bridees, et seulement
     * une fois le premier coup donne. */
    return !(s == STONE_HABILETE || s == STONE_ENDURANCE || s == STONE_CHANCE);
}

/* "vous recupererez un nombre de points egal a la moitie de votre total de
 * depart (si ce total est impair, arrondissez le resultat au chiffre
 * superieur)". */
static int half_round_up(unsigned char start) { return ((int)start + 1) / 2; }

StoneUse stone_use(Character* c, Stone s, int in_combat)
{
    if (s < 0 || s >= STONE_COUNT)  return STONE_USE_NONE;
    if (c->stones[s] == 0)          return STONE_USE_NONE;
    if (!stone_usable(s, in_combat)) return STONE_USE_FORBIDDEN;

    --c->stones[s];

    switch (s) {
    case STONE_HABILETE:
        character_adjust_hab(c, half_round_up(c->hab0));
        break;
    case STONE_ENDURANCE:
        character_adjust_end(c, half_round_up(c->end0));
        break;
    case STONE_CHANCE:
        character_adjust_cha(c, half_round_up(c->cha0));
        break;
    case STONE_MALEDICTION:
        /* "vous devrez lancer un de et reduire votre total d'ENDURANCE d'un
         * nombre de points equivalant au chiffre obtenu." Le sort qui frappe
         * l'adversaire est narratif : c'est la page qui l'ecrit. */
        character_adjust_end(c, -(int)roll_d6());
        break;
    default:
        /* FEU, GLACE, ILLUSION, AMITIE, CROISSANCE, BENEDICTION, TERREUR,
         * FLETRISSURE : aucun effet chiffre sur le heros. La pierre est
         * consommee, la page decide de la suite. BENEDICTION soigne une
         * creature (+3/+3/+3), mais le livre ne donne les totaux de depart
         * d'aucune creature : l'effet reste a la narration. */
        break;
    }
    return STONE_USE_OK;
}
