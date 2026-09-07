/*
 * Banc d'essai du format de page, sur machine hote.
 *
 * L'analyseur de ligne, le sac et la ligne V sont de l'arithmetique pure :
 * les verifier ici coute une seconde, alors que les verifier dans
 * l'emulateur demande de rejouer une partie et ne couvre qu'un chemin.
 * page.h ne touche ni a conio ni au disque, c'est ce qui rend ce banc
 * possible -- meme code des deux cotes, aucune copie a maintenir.
 *
 *     cc -Wall -Wextra -o /tmp/test_parse test_parse.c && /tmp/test_parse
 */
#include <stdio.h>
#include <string.h>

#include "page.h"

static int failures = 0;
static int checks   = 0;

#define CHECK(cond, ...)                                                      \
    do {                                                                      \
        ++checks;                                                             \
        if (!(cond)) {                                                        \
            printf("ECHEC %s:%d: ", __FILE__, __LINE__);                      \
            printf(__VA_ARGS__); printf("\n"); ++failures;                    \
        }                                                                     \
    } while (0)

/* Le catalogue reel du jeu, dans l'ordre de OBJFR.TXT : la ligne N est le
 * bit N. Les trois derniers sont des drapeaux caches. */
static const char kCatalogue[] =
    "SERV Serviette de bain\n"
    "PILE Pile d'Holophone\n"
    "CROQ Croquettes pour chat\n"
    "UNIF Armure de trouffion\n"
    "EPIC Fiole d'Epice\n"
    "PASS Accreditation presse\n"
    "S1 Selfie : Seigneur Vapeur\n"
    "S2 Selfie : Monsieur Spork\n"
    "S3 Selfie : le Ver des Dunes\n"
    "S4 Selfie : Ouiti\n"
    "S5 Selfie : Barbastella\n"
    "S6 Selfie : la Bete du Cargo\n"
    ".CHAG\n"
    ".CAL\n"
    ".BIZZ\n";

/* Le tampon de page du moteur : les titres de choix et les lignes de texte
 * pointent DEDANS, il doit donc survivre a l'analyse. */
static char page_buf[2048];

/* Joue une page comme le moteur le ferait : la page courante est <id>, le
 * texte est recopie dans le tampon puis decoupe en place. */
static void play(int id, const char* text)
{
    size_t n = strlen(text);
    memcpy(page_buf, text, n + 1);
    current_scene = id;
    parse_page(page_buf, (unsigned int)n);
}

static void load_catalogue(void)
{
    size_t n = strlen(kCatalogue);
    memcpy(obj_buf, kCatalogue, n + 1);
    objects_parse(obj_buf, (unsigned int)n);
}

/* ── Le catalogue ──────────────────────────────────────────────────────── */

static void test_catalogue(void)
{
    load_catalogue();
    CHECK(obj_count == 15, "15 jetons attendus, %u lus", obj_count);
    CHECK(object_bit("SERV") == 0, "SERV doit etre le bit 0");
    CHECK(object_bit("S6") == 11, "S6 doit etre le bit 11");
    CHECK(object_bit(".BIZZ") == 14, "le dernier drapeau est le bit 14");
    /* Le JETON se compare sans tenir compte de la casse : `G croq` marche. */
    CHECK(object_bit("croq") == 2, "la casse ne doit pas compter");
    CHECK(object_bit("CroQ") == 2, "la casse ne doit pas compter");
    /* Un jeton inconnu est ignore en silence, pas une erreur. */
    CHECK(object_bit("PLASMA") == OBJ_NONE, "jeton inconnu -> OBJ_NONE");
    /* Un prefixe n'est pas un jeton : S1 ne doit pas repondre a S. */
    CHECK(object_bit("S") == OBJ_NONE, "un prefixe n'est pas un jeton");

    CHECK(strcmp(obj_lbl[0], "Serviette de bain") == 0,
          "libelle du bit 0 : '%s'", obj_lbl[0]);
    CHECK(strcmp(obj_lbl[6], "Selfie : Seigneur Vapeur") == 0,
          "libelle du bit 6 : '%s'", obj_lbl[6]);
    /* Un drapeau cache n'a pas de libelle et ne se montre jamais. */
    CHECK(obj_lbl[12][0] == '\0', "un drapeau n'a pas de libelle");
    CHECK(!object_hidden(0), "SERV est un objet visible");
    CHECK(object_hidden(12), ".CHAG est un drapeau cache");
    CHECK(object_hidden(13) && object_hidden(14), ".CAL et .BIZZ sont caches");
}

/* Le catalogue reel, avec des fins de ligne CRLF : l'empaqueteur ProDOS peut
 * en produire, et une ligne finissant par '\r' donnerait un jeton different. */
static void test_catalogue_crlf(void)
{
    static const char crlf[] = "SERV Serviette\r\nPILE Pile\r\n.CAL\r\n";
    size_t n = strlen(crlf);
    memcpy(obj_buf, crlf, n + 1);
    objects_parse(obj_buf, (unsigned int)n);
    CHECK(obj_count == 3, "3 jetons attendus, %u lus", obj_count);
    CHECK(object_bit("PILE") == 1, "CRLF : PILE doit rester le bit 1");
    CHECK(strcmp(obj_lbl[0], "Serviette") == 0,
          "CRLF : libelle '%s'", obj_lbl[0]);
    CHECK(object_hidden(2), "CRLF : .CAL reste un drapeau");
    load_catalogue();
}

/* ── T, texte et choix simples ─────────────────────────────────────────── */

static void test_titre_et_texte(void)
{
    scene_memory_reset();
    play(12,
        "T 012 La Cantina de Moche-Isley\n"
        "\n"
        "   Le barman ne sert pas les inconnus.\n"
        "\n"
        "   Trois verres attendent sur le comptoir.\n"
        "C 013 Repondre a la devinette\n"
        "C 003 Retour au cockpit\n");

    CHECK(page_title != 0 && strcmp(page_title, "La Cantina de Moche-Isley") == 0,
          "titre lu : '%s'", page_title ? page_title : "(nul)");
    /* La ligne vide sous le titre ne compte pas ; celle du milieu, si. */
    CHECK(body_count == 3, "3 lignes de texte attendues, %u", body_count);
    CHECK(strcmp(body_lines[0], "   Le barman ne sert pas les inconnus.") == 0,
          "1re ligne : '%s'", body_lines[0]);
    CHECK(body_lines[1][0] == '\0', "la ligne vide du milieu est conservee");
    CHECK(num_choices == 2, "2 choix attendus, %u", num_choices);
    CHECK(choices[0].scene_id == 13, "cible du choix A : %d", choices[0].scene_id);
    CHECK(strcmp(choices[0].title, "Repondre a la devinette") == 0,
          "libelle du choix A : '%s'", choices[0].title);
    CHECK(choices[1].scene_id == 3, "cible du choix B : %d", choices[1].scene_id);
    CHECK(choice_available(0) && choice_available(1), "un C est toujours prenable");
    CHECK(page_revisit < 0, "pas de ligne V : pas de detour");
}

/* Cinq choix au plus : le sixieme tombe, il ne tiendrait pas dans les quatre
 * lignes du bas de l'ecran. */
static void test_cinq_choix_max(void)
{
    scene_memory_reset();
    play(1,
        "T 001 Trop de choix\n"
        "C 002 un\nC 003 deux\nC 004 trois\nC 005 quatre\nC 006 cinq\nC 007 six\n");
    CHECK(num_choices == MAX_CHOICES, "borne a %u choix, %u lus",
          (unsigned)MAX_CHOICES, num_choices);
    CHECK(choices[4].scene_id == 6, "le 5e choix est garde");
}

/* Une ligne C sans libelle, ou sans numero, n'est pas un choix : elle serait
 * une porte sans etiquette, ou une porte vers la page 000. La ligne sans
 * numero retombe dans le texte, la ligne sans libelle disparait. */
static void test_choix_mal_formes(void)
{
    scene_memory_reset();
    play(1, "T 001 Bancal\nC 002\nC  Sans numero\nC 003 Bon choix\n");
    CHECK(num_choices == 1, "seul le choix complet compte, %u lus", num_choices);
    CHECK(choices[0].scene_id == 3, "cible : %d", choices[0].scene_id);
    CHECK(body_count == 1 && strcmp(body_lines[0], "C  Sans numero") == 0,
          "la ligne sans numero est du texte, pas un choix");
}

/* ── G / GX ────────────────────────────────────────────────────────────── */

static void test_g_gx(void)
{
    scene_memory_reset();
    CHECK(inventory == 0, "le sac part vide");

    play(80, "T 080 La Decharge\nG SERV\nG PILE\nC 003 Repartir\n");
    CHECK(inv_has(object_bit("SERV")), "G SERV doit poser le bit");
    CHECK(inv_has(object_bit("PILE")), "G PILE doit poser le bit");
    CHECK(!inv_has(object_bit("CROQ")), "rien d'autre ne bouge");

    /* G est idempotent : rouvrir la page ne double rien (un bit est un bit). */
    play(81, "T 081 Encore\nG SERV\nC 003 Repartir\n");
    CHECK(inv_has(object_bit("SERV")), "G deux fois reste un bit");

    play(82, "T 082 Chagrin se mouche\nGX SERV\nC 003 Repartir\n");
    CHECK(!inv_has(object_bit("SERV")), "GX SERV doit retirer le bit");
    CHECK(inv_has(object_bit("PILE")), "GX ne touche qu'a son jeton");

    /* Un jeton inconnu du catalogue est ignore en silence : un corpus ecrit a
     * plusieurs mains doit rester jouable. */
    play(83, "T 083 Jeton fantome\nG PLASMA\nGX PLASMA\nC 003 Repartir\n");
    CHECK(inventory == (1ul << object_bit("PILE")),
          "un jeton inconnu ne doit rien changer (sac = %lu)", inventory);

    /* La casse ne compte pas dans le JETON... */
    play(84, "T 084 Casse melangee\nG CroQ\nC 003 Repartir\n");
    CHECK(inv_has(object_bit("CROQ")), "G CroQ doit poser le bit de CROQ");

    /* ...mais la DIRECTIVE, elle, est en majuscules : `g croq` est du texte.
     * C'est la regle de SCOSWAMP, et elle evite qu'une phrase de recit
     * commencant par une minuscule ne pose un objet par accident. */
    scene_memory_reset();
    play(85, "T 085 Minuscules\ng serv\nC 003 Repartir\n");
    CHECK(inventory == 0, "une directive en minuscules est du texte");
    CHECK(body_count == 1 && strcmp(body_lines[0], "g serv") == 0,
          "elle s'affiche telle quelle");
}

/* ── CI / CN / GU ──────────────────────────────────────────────────────── */

static const char kPosteDeGarde[] =
    "T 020 Le hangar de l'Etoile du Malheur\n"
    "\n"
    "   Deux trouffions verifient les laissez-passer.\n"
    "CI UNIF 021 Franchir le poste en armure\n"
    "CN UNIF 022 Franchir le poste a visage decouvert\n"
    "C 003 Faire demi-tour\n";

static void test_ci_cn(void)
{
    scene_memory_reset();

    /* Sans l'armure : CN est prenable, CI ne l'est pas -- mais les DEUX sont
     * lus, car le joueur doit voir l'issue qu'il rate. */
    play(20, kPosteDeGarde);
    CHECK(num_choices == 3, "les deux issues restent visibles, %u", num_choices);
    CHECK(!choice_available(0), "sans UNIF, le choix CI est refuse");
    CHECK(choice_available(1), "sans UNIF, le choix CN est prenable");
    CHECK(choice_available(2), "un C reste toujours prenable");

    /* Avec l'armure : exactement l'inverse. */
    scene_memory_reset();
    inv_give(object_bit("UNIF"));
    play(20, kPosteDeGarde);
    CHECK(choice_available(0), "avec UNIF, le choix CI est prenable");
    CHECK(!choice_available(1), "avec UNIF, le choix CN est refuse");

    /* Prendre un CI ne consomme rien : l'armure reste sur le dos. */
    CHECK(choice_take(0) == 21, "CI mene bien en 021");
    CHECK(inv_has(object_bit("UNIF")), "CI ne consomme pas son jeton");
}

static void test_gu(void)
{
    scene_memory_reset();
    inv_give(object_bit("CROQ"));

    play(34,
        "T 034 Un couloir du Nostalgo\n"
        "GU CROQ 035 Secouer le sac de croquettes\n"
        "CN CROQ 036 Appeler le chat a mains nues\n");
    CHECK(num_choices == 2, "2 choix, %u lus", num_choices);
    CHECK(choice_available(0), "avec CROQ, le GU est prenable");
    CHECK(!choice_available(1), "avec CROQ, le CN est refuse");

    /* GU exige le jeton ET le consomme en servant : c'est ce qui distingue le
     * materiel (qui se depense) du selfie (qu'on garde). */
    CHECK(choice_take(0) == 35, "GU mene bien en 035");
    CHECK(!inv_has(object_bit("CROQ")), "GU doit consommer son jeton");

    /* Le sac vide, le meme choix se voit encore mais ne se prend plus. */
    play(34,
        "T 034 Un couloir du Nostalgo\n"
        "GU CROQ 035 Secouer le sac de croquettes\n"
        "CN CROQ 036 Appeler le chat a mains nues\n");
    CHECK(num_choices == 2, "le GU refuse reste visible, %u", num_choices);
    CHECK(!choice_available(0), "sans CROQ, le GU est refuse");
    CHECK(choice_available(1), "sans CROQ, le CN redevient prenable");
}

/* Un choix dont le jeton est inconnu disparait : offrir un passage dont la
 * condition ne sera jamais testee serait pire que de ne pas l'offrir. */
static void test_choix_jeton_inconnu(void)
{
    scene_memory_reset();
    play(1, "T 001 Fantome\nCI PLASMA 002 Passer\nC 003 Rester\n");
    CHECK(num_choices == 1, "le choix au jeton inconnu tombe, %u", num_choices);
    CHECK(choices[0].scene_id == 3, "cible : %d", choices[0].scene_id);
}

/* ── La ligne V ────────────────────────────────────────────────────────── */

/* Premiere visite : la page se lit et ses effets jouent. */
static void test_v_premiere_visite(void)
{
    scene_memory_reset();
    play(2, "T 002 Le cockpit, premiere fois\nV 003\n\n   La carte stellaire s'allume.\nC 004 Secteur interieur\n");
    CHECK(page_revisit < 0, "jamais venu : pas de detour (revisit=%d)", page_revisit);
    /* La ligne vide sous le titre ne compte pas : elle couterait une des
     * dix-huit lignes du budget. */
    CHECK(body_count == 1, "le texte se lit, %u lignes", body_count);
    CHECK(num_choices == 1, "les choix se lisent, %u", num_choices);
}

/* Deja venu : la page cede la place, et RIEN d'autre ne joue -- ni le texte,
 * ni les choix, ni surtout les lignes G qui redonneraient l'objet. */
static void test_v_deja_venu(void)
{
    scene_memory_reset();
    scene_mark_visited(2);
    play(2,
        "T 002 Le cockpit, premiere fois\n"
        "V 003\n"
        "G S1\n"
        "\n   La carte stellaire s'allume.\n"
        "C 004 Secteur interieur\n");
    CHECK(page_revisit == 3, "detour attendu vers 003, obtenu %d", page_revisit);
    CHECK(body_count == 0, "rien ne s'affiche, %u lignes", body_count);
    CHECK(num_choices == 0, "aucun choix, %u", num_choices);
    CHECK(!inv_has(object_bit("S1")), "le G ne doit PAS rejouer");
}

/* La cible du detour compte aussi : passer par la version courte marque le
 * lieu, et y revenir ne doit pas rejouer la version longue. */
static void test_v_cible_visitee(void)
{
    scene_memory_reset();
    scene_mark_visited(3);       /* on n'a jamais lu 002, mais on a vu 003 */
    play(2, "T 002 Le cockpit\nV 003\nG S1\nC 004 Partir\n");
    CHECK(page_revisit == 3, "la cible vue suffit, revisit=%d", page_revisit);
    CHECK(!inv_has(object_bit("S1")), "le G ne doit pas rejouer");
}

/* Les ids qui suivent sont les AUTRES pages du meme lieu : entrer par une
 * autre porte ne doit pas rejouer la premiere visite (selfie repris). */
static void test_v_liste_du_lieu(void)
{
    unsigned char i;
    static const unsigned int kAilleurs[3] = { 22, 23, 24 };

    for (i = 0; i < 3; ++i) {
        scene_memory_reset();
        scene_mark_visited(kAilleurs[i]);
        play(21, "T 021 Vapeur pose\nV 029 022 023 024\nG S1\nC 003 Repartir\n");
        CHECK(page_revisit == 29,
              "la page %u du meme lieu doit declencher le detour (revisit=%d)",
              kAilleurs[i], page_revisit);
        CHECK(!inv_has(object_bit("S1")), "le selfie ne se reprend pas");
    }

    /* Aucune page du lieu vue : la premiere visite joue, selfie compris. */
    scene_memory_reset();
    play(21, "T 021 Vapeur pose\nV 029 022 023 024\nG S1\nC 003 Repartir\n");
    CHECK(page_revisit < 0, "aucune page du lieu vue : pas de detour");
    CHECK(inv_has(object_bit("S1")), "le selfie se prend une premiere fois");

    /* Une page du lieu NON citee ne compte pas : la liste fait foi. */
    scene_memory_reset();
    scene_mark_visited(25);
    play(21, "T 021 Vapeur pose\nV 029 022 023 024\nG S1\nC 003 Repartir\n");
    CHECK(page_revisit < 0, "une page hors liste ne declenche rien");
}

/* La ligne V precede tout le reste, mais une page qui n'en a pas se lit
 * normalement meme au dixieme passage : c'est le cas du cockpit court. */
static void test_sans_v_relit_toujours(void)
{
    scene_memory_reset();
    scene_mark_visited(3);
    play(3, "T 003 Le cockpit du Cabriolet\n\n   Ou aller ?\nC 004 Interieur\n");
    CHECK(page_revisit < 0, "sans V, jamais de detour");
    CHECK(num_choices == 1, "sans V, la page se lit, %u choix", num_choices);
}

/* La garde anti-boucle : deux pages qui se renvoient l'une a l'autre. Le
 * moteur relit la derniere en levant page_ignore_v, et la page doit alors
 * s'afficher entiere -- texte et choix -- au lieu d'un ecran mort. */
static void test_garde_anti_boucle(void)
{
    scene_memory_reset();
    scene_mark_visited(40);
    scene_mark_visited(41);

    play(40, "T 040 Aller\nV 041\n\n   Du texte.\nC 003 Repartir\n");
    CHECK(page_revisit == 41, "sans la garde, le detour joue");
    CHECK(num_choices == 0, "sans la garde, la page est court-circuitee");

    page_ignore_v = 1;
    play(40, "T 040 Aller\nV 041\n\n   Du texte.\nC 003 Repartir\n");
    page_ignore_v = 0;
    CHECK(page_revisit < 0, "la garde annule le detour (revisit=%d)", page_revisit);
    CHECK(body_count == 1, "le texte revient, %u lignes", body_count);
    CHECK(num_choices == 1, "le joueur garde la main, %u choix", num_choices);
}

/* ── Le bitmap des pages ───────────────────────────────────────────────── */

static void test_bitmap(void)
{
    unsigned int p;
    scene_memory_reset();
    for (p = 0; p < 1000; ++p)
        CHECK(!scene_visited(p), "page %u marquee apres reset", p);
    for (p = 0; p < 1000; p += 7) scene_mark_visited(p);
    for (p = 0; p < 1000; ++p)
        CHECK(scene_visited(p) == (p % 7 == 0), "page %u mal memorisee", p);
    /* Hors plage : jamais vu, jamais marque, jamais d'ecriture sauvage. */
    CHECK(!scene_visited(1000), "1000 est hors plage");
    scene_mark_visited(5000);
    CHECK(!scene_visited(5000), "5000 est hors plage");
}

/* ── Les fins de ligne ─────────────────────────────────────────────────── */

/* Le meme corpus se lit avec des fins de ligne CRLF : les fichiers passent
 * par un empaqueteur ProDOS et un '\r' colle en fin de titre de choix se
 * verrait a l'ecran. */
static void test_crlf(void)
{
    scene_memory_reset();
    play(12, "T 012 Titre\r\n\r\n   Du texte.\r\nG PILE\r\nC 003 Retour\r\n");
    CHECK(strcmp(page_title, "Titre") == 0, "titre CRLF : '%s'", page_title);
    CHECK(body_count == 1, "texte CRLF : %u lignes", body_count);
    CHECK(strcmp(body_lines[0], "   Du texte.") == 0,
          "texte CRLF : '%s'", body_lines[0]);
    CHECK(num_choices == 1 && strcmp(choices[0].title, "Retour") == 0,
          "choix CRLF : '%s'", num_choices ? choices[0].title : "(aucun)");
    CHECK(inv_has(object_bit("PILE")), "G en CRLF doit marcher");
}

/* ── Les champs, un a un ───────────────────────────────────────────────── */

static void test_take(void)
{
    static char s1[] = "012 Titre de la page";
    static char s2[] = "CROQ 034 Secouer le sac";
    unsigned int v;
    char* w;
    char* t;

    t = take_uint(s1, &v);
    CHECK(v == 12, "take_uint lit 012 -> %u", v);
    CHECK(strcmp(t, "Titre de la page") == 0, "take_uint saute les espaces");

    t = take_word(s2, &w);
    CHECK(strcmp(w, "CROQ") == 0, "take_word lit le jeton -> '%s'", w);
    t = take_uint(t, &v);
    CHECK(v == 34, "puis le numero -> %u", v);
    CHECK(strcmp(t, "Secouer le sac") == 0, "puis le libelle -> '%s'", t);
}

/* ── Une petite partie, bout a bout ────────────────────────────────────── */

/* La chaine de la Decharge : ramasser la serviette, consoler Chagrin, et
 * verifier qu'un second passage a la Decharge ne redonne rien. */
static void test_partie(void)
{
    scene_memory_reset();

    /* 081 : le module spa ecrase donne la serviette. */
    play(81, "T 081 Le module spa ecrase\nV 082\nG SERV\nC 080 Continuer le tri\n");
    CHECK(page_revisit < 0, "premiere visite du module spa");
    CHECK(inv_has(object_bit("SERV")), "la serviette est ramassee");
    scene_mark_visited(81);

    /* Second passage : le detour part vers la page "le bac est vide". */
    play(81, "T 081 Le module spa ecrase\nV 082\nG SERV\nC 080 Continuer le tri\n");
    CHECK(page_revisit == 82, "second passage -> 082, obtenu %d", page_revisit);

    /* 061 : Chagrin veut une serviette. Elle y passe. */
    play(61,
        "T 061 Chagrin bloque le couloir\n"
        "GU SERV 062 Tendre la serviette\n"
        "CN SERV 007 L'ecouter parler de sa vie\n");
    CHECK(choice_available(0), "avec la serviette, on peut la tendre");
    CHECK(choice_take(0) == 62, "cela mene en 062");
    CHECK(!inv_has(object_bit("SERV")), "Chagrin se mouche dedans : elle est perdue");

    /* 062 : le drapeau cache se pose et ne se voit jamais dans la chaine. */
    play(62, "T 062 Chagrin vous laisse passer\nG .CHAG\nC 063 Avancer\n");
    CHECK(inv_has(object_bit(".CHAG")), "le drapeau cache est pose");
    CHECK(object_hidden(object_bit(".CHAG")), ".CHAG ne se montre pas");
}

int main(void)
{
    test_catalogue();
    test_catalogue_crlf();
    test_titre_et_texte();
    test_cinq_choix_max();
    test_choix_mal_formes();
    test_g_gx();
    test_ci_cn();
    test_gu();
    test_choix_jeton_inconnu();
    test_v_premiere_visite();
    test_v_deja_venu();
    test_v_cible_visitee();
    test_v_liste_du_lieu();
    test_sans_v_relit_toujours();
    test_garde_anti_boucle();
    test_bitmap();
    test_crlf();
    test_take();
    test_partie();

    if (failures == 0) {
        printf("test_parse : %d verifications, tout passe.\n", checks);
        return 0;
    }
    printf("test_parse : %d verifications, %d echec(s).\n", checks, failures);
    return 1;
}
