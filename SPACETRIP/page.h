/* page.h -- le format de page de SCOSWAMP, reduit a ce dont SPACE TRIP a
 * besoin, et SANS UN SEUL APPEL A L'ECRAN.
 *
 * Tout ce qui vit ici est de l'arithmetique sur des chaines et des bits :
 * l'analyseur de ligne, le sac (un mot de 16 bits), le bitmap des pages deja
 * vues, et la regle qui dit si un choix est prenable. Aucune de ces reponses
 * ne depend de conio, donc le meme code se compile sous cc65 pour l'Apple II
 * ET sous cc sur la machine hote, ou test_parse.c le fait tourner en une
 * seconde. Verifier la ligne V dans l'emulateur demanderait de rejouer une
 * partie entiere et ne couvrirait qu'un chemin ; c'est la raison d'etre de
 * cette separation, la meme que celle de rules.c dans SCOSWAMP.
 *
 * POURQUOI UN .h ET PAS UN .c : le README impose la ligne de compilation
 * `cl65 ... spacetrip.c paths.c` et on n'y ajoute pas de troisieme module.
 * Chaque programme n'inclut donc ce fichier qu'UNE seule fois (spacetrip.c
 * d'un cote, test_parse.c de l'autre) : il n'y a jamais deux exemplaires d'un
 * meme symbole a l'edition de liens, et les definitions peuvent rester
 * ordinaires plutot que `static` -- ce qui evite au passage les avertissements
 * "fonction definie mais jamais utilisee" du cote qui n'en appelle qu'une
 * partie.
 */
#ifndef PAGE_H
#define PAGE_H

#include <string.h>

/* ── Les bornes ───────────────────────────────────────────────────────────
 *
 * Cinq choix au plus (la bible le fixe), dix-huit lignes de texte : c'est ce
 * qui tient entre la barre de titre (ligne 0) et les quatre lignes de choix
 * du bas sur un ecran 80x24. Trente-deux objets : le catalogue en compte
 * dix-sept -- il en comptait quinze jusqu'a ce qu'un solveur montre que deux
 * entrees (le Nostalgo, la cour de Mingus) se contournaient par une revisite,
 * et la seule parade propre est un drapeau cache par entree. Le sac passe
 * donc a un unsigned long : quatre octets, que le 6502 manipule un peu plus
 * lentement, et un jeu qu'on ne peut plus tricher. Mille
 * pages, soit 125 octets de bitmap -- l'equivalent d'une ligne d'ecran, pour
 * se souvenir de tout le jeu. */
#define MAX_CHOICES  5
#define BODY_ROWS   18
#define OBJ_MAX     32
#define OBJ_BUF    512   /* le catalogue entier, lu une fois au demarrage */
#define SCENE_BITS 125   /* 1000 pages / 8 */
#define OBJ_NONE   OBJ_MAX

/* Un choix. `title` pointe DANS le tampon de la page, jamais une copie : sur
 * cette machine, cinq titres de 80 octets recopies valent 400 octets de RAM
 * qu'on n'a pas, et le tampon reste en place tant que la page est affichee. */
typedef struct {
    int           scene_id;
    char*         title;
    unsigned char obj;    /* le bit teste, OBJ_NONE si le choix est libre */
    unsigned char mode;   /* 0 libre, 1 = CI, 2 = CN, 3 = GU */
} Choice;

/* ── L'etat du jeu ───────────────────────────────────────────────────────
 *
 * Le sac ET les faits acquis sont le meme mecanisme : un bit nomme. Un jeton
 * prefixe d'un point est un drapeau cache -- il compte pour les choix, mais
 * ne s'affiche jamais dans "votre chaine". */
unsigned long inventory;              /* un bit par jeton du catalogue */
char          obj_buf[OBJ_BUF];       /* OBJFR / OBJEN, decoupe en place */
char*         obj_tok[OBJ_MAX];       /* le jeton de la ligne N = le bit N */
char*         obj_lbl[OBJ_MAX];       /* son libelle, vide pour un drapeau */
unsigned char obj_count;
unsigned char visited[SCENE_BITS];

/* ── L'etat de la page courante ──────────────────────────────────────── */
Choice        choices[MAX_CHOICES];
unsigned char num_choices;
char*         body_lines[BODY_ROWS];
unsigned char body_count;
char*         page_title;
int           page_revisit;   /* -1, ou la page ou la ligne V nous renvoie */
int           current_scene;
/* Garde anti-boucle : deux pages qui se renverraient l'une a l'autre par
 * leurs lignes V bloqueraient la machine. Le moteur relit alors la derniere
 * en levant ce drapeau : la page s'affiche entiere, avec ses choix, et le
 * joueur garde la main. Un corpus sain ne l'active jamais. */
unsigned char page_ignore_v;

/* ── Le catalogue des objets ─────────────────────────────────────────── */

char page_upcase(char ch)
{
    return (ch >= 'a' && ch <= 'z') ? (char)(ch - 'a' + 'A') : ch;
}

/* Comparaison insensible a la casse : les pages ecrivent `G CROQ` mais rien
 * n'interdit `g croq`, et une page ne doit pas rater son objet pour une
 * majuscule. */
int page_same_name(const char* a, const char* b)
{
    while (*a && *b) {
        if (page_upcase(*a) != page_upcase(*b)) return 0;
        ++a; ++b;
    }
    return *a == *b;
}

/* Decoupe le catalogue EN PLACE : chaque fin de ligne devient un '\0' et on
 * ne garde que des pointeurs. Une ligne vaut "JETON libelle" ; le libelle
 * peut manquer (drapeau cache), auquel cas obj_lbl pointe une chaine vide.
 * L'ORDRE FAIT FOI : la ligne N est le bit N -- c'est le contrat que
 * build_objects.py tient du cote outils. */
void objects_parse(char* buf, unsigned int len)
{
    char* p   = buf;
    char* end = buf + len;
    char* q;
    char* lbl;
    unsigned char crlf;

    obj_count = 0;
    while (p < end && obj_count < OBJ_MAX) {
        q = p;
        while (q < end && *q != '\r' && *q != '\n') q++;
        crlf = (unsigned char)(q + 1 < end && *q == '\r' && q[1] == '\n');
        *q = '\0';
        if (*p) {
            lbl = p;
            while (*lbl && *lbl != ' ') lbl++;
            if (*lbl == ' ') { *lbl++ = '\0'; while (*lbl == ' ') lbl++; }
            obj_tok[obj_count] = p;
            obj_lbl[obj_count] = lbl;
            obj_count++;
        }
        p = q + 1;
        if (crlf) p++;
    }
}

/* Rend le bit du jeton, ou OBJ_NONE. Un jeton inconnu n'est PAS une erreur :
 * la page qui le porte joue simplement sans lui. Un corpus en cours
 * d'ecriture par plusieurs mains doit rester jouable. */
unsigned char object_bit(const char* name)
{
    unsigned char i;
    for (i = 0; i < obj_count; ++i)
        if (page_same_name(name, obj_tok[i])) return i;
    return OBJ_NONE;
}

/* Un jeton commencant par '.' est un drapeau : il ne se montre jamais. */
unsigned char object_hidden(unsigned char b)
{
    return (unsigned char)(b >= obj_count || obj_tok[b][0] == '.');
}

unsigned char inv_has(unsigned char b)
{
    if (b >= OBJ_MAX) return 0;
    return (unsigned char)((inventory & (1ul << b)) != 0);
}

void inv_give(unsigned char b) { if (b < OBJ_MAX) inventory |=  (1ul << b); }
void inv_take(unsigned char b) { if (b < OBJ_MAX) inventory &= ~(1ul << b); }

/* ── Les pages deja parcourues ───────────────────────────────────────── */

int scene_visited(unsigned int scene)
{
    if (scene >= (unsigned int)SCENE_BITS * 8) return 0;
    return (visited[scene >> 3] & (1 << (scene & 7))) != 0;
}

void scene_mark_visited(unsigned int scene)
{
    if (scene < (unsigned int)SCENE_BITS * 8) visited[scene >> 3] |= (1 << (scene & 7));
}

void scene_memory_reset(void)
{
    memset(visited, 0, sizeof visited);
    inventory = 0;
}

/* ── Lecture des champs d'une ligne ──────────────────────────────────────
 *
 * take_uint / take_word plutot que sscanf : sur cc65 le PREMIER appel a la
 * famille scanf fait entrer plusieurs kilo-octets d'analyseur de format dans
 * le binaire, pour lire trois chiffres. Le moteur tient a $4000 et l'image
 * HGR occupe deja $2000-$3FFF ; on ne paie pas ca. */

/* Avance sur les chiffres puis sur les espaces, et rend la valeur lue. */
char* take_uint(char* t, unsigned int* out)
{
    unsigned int v = 0;
    while (*t >= '0' && *t <= '9') { v = v * 10u + (unsigned int)(*t - '0'); t++; }
    while (*t == ' ') t++;
    *out = v;
    return t;
}

/* Avance sur un mot, le termine par '\0', et rend le debut du suivant. */
char* take_word(char* t, char** word)
{
    *word = t;
    while (*t && *t != ' ') t++;
    if (*t == ' ') { *t = '\0'; t++; while (*t == ' ') t++; }
    return t;
}

/* ── L'analyseur de ligne ────────────────────────────────────────────────
 *
 * Les huit directives, dans l'ordre qui FAIT FOI : les prefixes de deux
 * lettres passent devant la lettre seule, sinon `C ` avalerait `CI` et `G `
 * avalerait `GX`. Trois octets par entree : les deux lettres, puis le
 * troisieme caractere exige (' ' un espace, '*' n'importe lequel).
 *
 * Une table lue par une boucle plutot qu'une cascade de huit
 * `if (c0 == 'X' && c1 == 'Y' && c2 == ' ')` : c'est la meme liste, dans le
 * meme ordre, mais elle tient en 25 octets de RODATA au lieu d'un pave de
 * code duplique.
 *
 *   T  <id> <titre>              le titre, ligne 0 en video inverse
 *   V  <id> [<page> ...]         "si vous y etes deja venu, allez en <id>" ;
 *                                les numeros qui suivent sont les AUTRES
 *                                pages du meme lieu -- sans elles, entrer
 *                                par une autre porte rejouait la premiere
 *                                visite (objet redonne, selfie repris)
 *   G  <JETON>                   donne l'objet ou pose le drapeau
 *   GX <JETON>                   le retire
 *   C  <id> <libelle>            un choix
 *   CI <JETON> <id> <libelle>    prenable seulement si l'on A le jeton
 *   CN <JETON> <id> <libelle>    prenable seulement si l'on ne l'a PAS
 *   GU <JETON> <id> <libelle>    exige le jeton et le CONSOMME
 *   <reste>                      le texte de la page
 */
static const char kOps[] = "GX GU CI CN G *C *V *T *";

enum { D_GX, D_GU, D_CI, D_CN, D_G, D_C, D_V, D_T, D_TEXTE };

/* Ajoute un choix a la page. Quatre directives fabriquaient chacune le sien :
 * le meme bloc, quatre fois. */
void push_choice(int scene, unsigned char obj, unsigned char mode, char* title)
{
    Choice* c;
    if (num_choices >= MAX_CHOICES) return;
    c = &choices[num_choices++];
    c->scene_id = scene;
    c->title    = title;
    c->obj      = obj;
    c->mode     = mode;
}

void classify_line(char* l)
{
    char* t;
    char* word;
    unsigned int a, b;
    const char* k;
    unsigned char op;
    unsigned char o;
    /* Les trois premieres lettres, lues une fois : sur le pointeur, chaque
     * `l[1] == 'X'` coutait un acces indirect (ldy/lda (ptr),y) ; sur trois
     * octets statiques c'est un `lda` absolu. */
    unsigned char c0 = (unsigned char)l[0];
    unsigned char c1 = (unsigned char)l[1];
    unsigned char c2 = (unsigned char)l[2];

    /* La ligne V a parle : la page est court-circuitee. Rien d'autre ne joue,
     * ni les G/GX (l'objet ne se redonne pas), ni les choix, ni le texte. */
    if (page_revisit >= 0) return;

    k = kOps;
    for (op = 0; op < D_TEXTE; ++op, k += 3)
        if (k[0] == (char)c0 && k[1] == (char)c1 &&
            (k[2] == '*' || c2 == ' ')) break;

    switch (op) {
    case D_GX:
        take_word(l + 3, &word);
        inv_take(object_bit(word));
        break;

    case D_G:
        take_word(l + 2, &word);
        inv_give(object_bit(word));
        break;

    /* CI/CN/GU : meme forme, seul le mode change. Un choix dont le jeton est
     * inconnu du catalogue disparait -- c'est la regle de SCOSWAMP, et elle
     * evite d'offrir un passage dont la condition ne sera jamais testee. */
    case D_CI:
    case D_CN:
    case D_GU:
        t = take_word(l + 3, &word);
        o = object_bit(word);
        t = take_uint(t, &a);
        if (o != OBJ_NONE && *t != '\0')
            push_choice((int)a, o,
                        (unsigned char)(op == D_CI ? 1 : (op == D_CN ? 2 : 3)), t);
        break;

    /* Un CHIFFRE est exige juste apres "C " : sans cette garde, une ligne de
     * recit commencant par "C " -- "C'etait la Cantina." n'en est pas une,
     * mais "C ette fois..." coupe par le remise en forme le serait --
     * fabriquerait un choix muet vers la page 000. Le corpus s'ecrit a
     * plusieurs mains ; le moteur ne doit pas transformer une faute de frappe
     * en cul-de-sac. */
    case D_C:
        if (l[2] < '0' || l[2] > '9') goto texte;
        t = take_uint(l + 2, &a);
        if (*t != '\0') push_choice((int)a, OBJ_NONE, 0, t);
        break;

    /* Le livre dit "si vous Y etes deja venu" -- dans le LIEU, pas sur cette
     * page. Or un lieu en occupe plusieurs : la page d'arrivee, la page qui
     * porte les sorties, la variante de revisite. Le bitmap etant indexe sur
     * la page, revenir par une autre porte rejouait la premiere visite. D'ou
     * la liste : on teste la page courante, la cible, puis chaque page citee,
     * et le premier drapeau leve suffit. */
    case D_V:
        if (page_ignore_v) break;
        t = take_uint(l + 2, &a);
        b = (unsigned int)current_scene;
        while (!scene_visited(b)) {
            if (*t) { t = take_uint(t, &b); continue; }
            if (b == a) return;   /* la cible a ete testee : la liste est finie */
            b = a;                /* passer par la revisite compte aussi */
        }
        page_revisit = (int)a;
        break;

    case D_T:
        t = l + 2;
        while (*t >= '0' && *t <= '9') t++;
        while (*t == ' ') t++;
        page_title = t;
        break;

    /* Pas de ligne vide en tete : le fichier en a une sous le titre, et elle
     * couterait une des dix-huit lignes du budget. */
    default:
    texte:
        if (body_count < BODY_ROWS && (body_count > 0 || c0 != '\0'))
            body_lines[body_count++] = l;
        break;
    }
}

/* Decoupe la page EN PLACE et la joue ligne a ligne. Pas de recopie ligne par
 * ligne, donc pas de tampon de 120 octets sur la pile ni de limite de
 * longueur. */
void parse_page(char* buf, unsigned int len)
{
    char* p   = buf;
    char* end = buf + len;
    char* q;
    unsigned char crlf;

    num_choices  = 0;
    body_count   = 0;
    page_title   = 0;
    page_revisit = -1;

    while (p < end) {
        q = p;
        while (q < end && *q != '\r' && *q != '\n') q++;
        crlf = (unsigned char)(q + 1 < end && *q == '\r' && q[1] == '\n');
        *q = '\0';
        classify_line(p);
        p = q + 1;
        if (crlf) p++;
    }
}

/* ── La regle des choix ──────────────────────────────────────────────────
 *
 * Un choix dont la condition n'est pas remplie se VOIT quand meme -- savoir
 * ce que l'armure de trouffion aurait permis fait partie de la lecture --
 * mais ne porte pas de lettre et la touche le refuse. */
unsigned char choice_available(unsigned char i)
{
    Choice* c;
    unsigned char has;
    if (i >= num_choices) return 0;
    c = &choices[i];
    if (c->mode == 0) return 1;
    has = inv_has(c->obj);
    return (unsigned char)(c->mode == 2 ? !has : has);
}

/* Prendre le choix : GU consomme le jeton en servant. Rend la page cible. */
int choice_take(unsigned char i)
{
    Choice* c = &choices[i];
    if (c->mode == 3) inv_take(c->obj);
    return c->scene_id;
}

#endif /* PAGE_H */
