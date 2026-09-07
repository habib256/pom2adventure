/* SPACE EXPLORER TRIP -- le moteur.
 *
 * Le jeu est une DONNEE : le binaire ne connait que le format de page decrit
 * dans SPACETRIP.MORE/BIBLE.md section 7 (un sous-ensemble exact de celui de
 * SCOSWAMP), et tout le reste vit sur le volume ProDOS. Ajouter une zone ne
 * demande pas de recompiler.
 *
 * Ce fichier ne contient que ce qui touche a l'ECRAN et au DISQUE ; l'analyse
 * des lignes, le sac et le bitmap des pages vues sont dans page.h, qui se
 * compile aussi bien ici que sur la machine hote (voir test_parse.c).
 *
 * Cible : Apple IIe enhanced (65C02), 64 Ko, ProDOS, carte 80 colonnes.
 * Le binaire demarre a $4000 parce que la page HGR 1 occupe $2000-$3FFF.
 */
#include <stdio.h>
#include <string.h>
#include <conio.h>
#include <apple2enh.h>
#include "paths.h"
#include "page.h"

/* Adresse de la page HGR 1 */
#define HGR_PAGE1 ((unsigned char*)0x2000)
#define HGR_SIZE  8192
#define MAX_PATH  64

/* Mise en page, 80x24.
 *
 * Ligne 0 : le titre, en video inverse. Lignes 1 a 18 : le texte (les 18
 * lignes que la bible autorise). Ligne 19 : la respiration. Lignes 20 a 23 :
 * les choix, cales EN BAS. Rien n'est jamais ecrit dans la derniere cellule
 * de l'ecran (colonne 79, ligne 23) : le firmware ferait defiler et toute la
 * mise en page remonterait d'une ligne. */
#define BODY_ROW0     1
#define CHOICE_ROW0  20
#define CHOICE_ROWN  23
#define CHOICE_COL2  40   /* colonne du 2e choix quand deux tiennent sur 1 ligne */
#define CHOICE_WIDTH 39   /* largeur utile d'une colonne de choix */

/* Le tampon de page. 2 Ko : dix-huit lignes de 78 colonnes, plus le titre et
 * cinq choix, c'est le pire cas que la bible autorise. Il est STATIQUE et pas
 * local -- cc65 met les gros locaux sur une pile logicielle de quelques
 * centaines d'octets, et une page entiere l'ecraserait. */
static char file_buffer[2048];

static int  video_mode   = 0;    /* 0 = texte 80 col, 1 = HGR plein ecran */
static unsigned char has_image = 0;
static char language[3] = "FR";
static char g_imgPath[MAX_PATH];
static char g_txtPath[MAX_PATH];
static char title_bar[81];

static void render_page(void);

static unsigned char is_fr(void) { return (unsigned char)(language[0] == 'F'); }

/* ── Les modes video ──────────────────────────────────────────────────────
 *
 * Que des soft-switches. Le texte reste en $400-$7FF et l'image en
 * $2000-$3FFF pendant toute la bascule : aucune ne relit le disque ni ne
 * repeint quoi que ce soit. */
static void enable_text_mode(void)
{
    __asm__("sta $C051");  /* TXTSET */
}

static void enable_hgr_full(void)
{
    __asm__("sta $C050");  /* TXTCLR */
    __asm__("sta $C057");  /* HIRES  */
    __asm__("sta $C054");  /* LOWSCR */
    __asm__("sta $C052");  /* MIXCLR */
}

static void set_video_mode(int mode)
{
    video_mode = mode;
    if (mode) enable_hgr_full(); else enable_text_mode();
}

/* ── Primitives d'ecran ─────────────────────────────────────────────────── */

/* 79 et pas 80 : effacer la derniere cellule ferait defiler l'ecran. */
static void wipe(void)
{
    unsigned char r;
    for (r = 0; r <= CHOICE_ROWN; r++) cclearxy(0, r, 79);
    gotoxy(0, 0);
}

static void clear_bottom(void)
{
    unsigned char r;
    for (r = CHOICE_ROW0; r <= CHOICE_ROWN; r++) cclearxy(0, r, 79);
}

/* Ecrit au plus `max` caracteres : une ligne trop longue ne doit pas
 * deborder sur la suivante -- en bas d'ecran, un debordement fait defiler. */
static void put_trunc(unsigned char col, unsigned char row,
                      const char* s, unsigned char max)
{
    gotoxy(col, row);
    while (*s && max--) cputc(*s++);
}

static void print_at(unsigned char row, const char* text)
{
    put_trunc(0, row, text, 79);
}

static void wait_key_at(unsigned char row, const char* prompt)
{
    print_at(row, prompt);
    cgetc();
}

/* La barre de titre : le titre de la page a gauche, le rappel des touches
 * cale a droite, le tout en video inverse sur la ligne 0. C'est la seule
 * ligne toujours presente, donc le seul endroit ou l'aide ne coute rien. */
static void render_title_bar(const char* title)
{
    const char* hint = is_fr() ? "I:CHAINE  ESPACE:IMAGE  Q:QUITTER"
                               : "I:CHANNEL  SPACE:IMAGE  Q:QUIT";
    unsigned char n;

    memset(title_bar, ' ', 80);
    title_bar[80] = '\0';
    if (title != 0) {
        n = (unsigned char)strlen(title);
        if (n > 40) n = 40;
        memcpy(title_bar + 1, title, n);
    }
    n = (unsigned char)strlen(hint);
    memcpy(title_bar + 79 - n, hint, n);

    revers(1);
    cputsxy(0, 0, title_bar);
    revers(0);
}

/* Un choix non prenable porte '-' au lieu de sa lettre : on le VOIT -- savoir
 * ce que l'armure de trouffion aurait ouvert fait partie de la lecture --
 * mais la touche le refuse. */
static char choice_tag(unsigned char i)
{
    return choice_available(i) ? (char)('A' + i) : '-';
}

/* Deux choix courts tiennent sur une ligne, en deux colonnes : c'est ce qui
 * fait entrer cinq choix dans les quatre lignes du bas. */
static unsigned char pair_fits(unsigned char i)
{
    return (unsigned char)(i + 1 < num_choices &&
           strlen(choices[i].title)     <= CHOICE_WIDTH - 3 &&
           strlen(choices[i + 1].title) <= CHOICE_WIDTH - 3);
}

static void put_choice(unsigned char col, unsigned char row,
                       unsigned char i, unsigned char width)
{
    gotoxy(col, row);
    cputc(choice_tag(i));
    cputc(')');
    cputc(' ');
    put_trunc((unsigned char)(col + 3), row, choices[i].title, width);
}

static void render_choices(void)
{
    unsigned char i, rows = 0, row;

    /* Les choix se calent en BAS : la derniere ligne de choix est toujours la
     * ligne 23, et le vide reste au-dessus, contre le texte. On compte donc
     * d'abord les lignes, avec la meme regle de pairage. */
    for (i = 0; i < num_choices; i += pair_fits(i) ? 2 : 1) rows++;
    if (rows > CHOICE_ROWN - CHOICE_ROW0 + 1) rows = CHOICE_ROWN - CHOICE_ROW0 + 1;
    row = (unsigned char)(CHOICE_ROWN + 1 - rows);

    i = 0;
    while (i < num_choices && row <= CHOICE_ROWN) {
        if (pair_fits(i)) {
            put_choice(0, row, i, CHOICE_WIDTH - 3);
            put_choice(CHOICE_COL2, row, (unsigned char)(i + 1), CHOICE_WIDTH - 3);
            i += 2;
        } else {
            put_choice(0, row, i, 75);
            i += 1;
        }
        row++;
    }
}

static void render_page(void)
{
    unsigned char i;

    set_video_mode(0);
    wipe();
    render_title_bar(page_title);
    for (i = 0; i < body_count; i++)
        put_trunc(0, (unsigned char)(BODY_ROW0 + i), body_lines[i], 79);
    render_choices();
}

/* Un message d'erreur qui ne fait pas planter la lecture : la page manque,
 * on le dit, et le joueur revient d'ou il vient avec une touche. */
static void oops(const char* what)
{
    wipe();
    render_title_bar(is_fr() ? "PANNE DE TRANSMISSION" : "TRANSMISSION FAILURE");
    print_at(2, what);
    wait_key_at(4, is_fr() ? "[ESPACE] continuer" : "[SPACE] continue");
}

/* ── Le catalogue des objets ──────────────────────────────────────────────
 *
 * OBJFR / OBJEN vivent a la RACINE du volume, sans extension : l'empaqueteur
 * retire .TXT comme il le fait des textes. Lus UNE fois, juste apres le choix
 * de la langue : le catalogue ne change plus de la partie, et le relire a
 * chaque page couterait un acces disque par page pour rien. */
static void objects_load(void)
{
    FILE* f;
    size_t n;

    obj_count = 0;
    f = fopen(is_fr() ? "OBJFR" : "OBJEN", "r");
    /* Repli sur le nom long : le dossier du depot, monte tel quel dans
     * l'emulateur, garde encore l'extension. */
    if (!f) f = fopen(is_fr() ? "OBJFR.TXT" : "OBJEN.TXT", "r");
    if (!f) return;

    n = fread(obj_buf, 1, sizeof obj_buf - 1, f);
    fclose(f);
    obj_buf[n] = '\0';
    objects_parse(obj_buf, (unsigned int)n);
}

/* ── Le disque ──────────────────────────────────────────────────────────── */

/* Une page sans image reste en texte, sans erreur : toutes n'en ont pas. */
static unsigned char load_hgr_image(int page_id)
{
    FILE* f;
    size_t bytes_read;

    if (build_paths(page_id, language, g_imgPath, g_txtPath) != 0) return 0;
    f = fopen(g_imgPath, "rb");
    if (!f) return 0;
    bytes_read = fread(HGR_PAGE1, 1, HGR_SIZE, f);
    fclose(f);
    return (unsigned char)(bytes_read == HGR_SIZE);
}

/* Lit la page et la joue : les lignes G/GX posent leurs bits, la ligne V peut
 * decider d'un detour. Rien n'est affiche ici. */
static unsigned char read_page(int page_id)
{
    FILE* f;
    size_t bytes_read;

    if (build_paths(page_id, language, g_imgPath, g_txtPath) != 0) {
        oops(is_fr() ? "Page hors plage (0-999)." : "Page out of range (0-999).");
        return 0;
    }
    f = fopen(g_txtPath, "r");
    if (!f) {
        oops(g_txtPath);
        return 0;
    }
    bytes_read = fread(file_buffer, 1, sizeof file_buffer - 1, f);
    fclose(f);
    if (bytes_read == 0) {
        oops(is_fr() ? "Page vide." : "Empty page.");
        return 0;
    }
    file_buffer[bytes_read] = '\0';

    current_scene = page_id;   /* la ligne V teste la page COURANTE */
    parse_page(file_buffer, (unsigned int)bytes_read);
    return 1;
}

/* Charge une page et l'affiche.
 *
 * Le detour de la ligne V se joue par une BOUCLE et non par un appel
 * recursif : la pile logicielle de cc65 tient quelques centaines d'octets et
 * une chaine de revisites la mangerait. Le compteur borne les cycles. */
static void load_page(int page_id)
{
    unsigned char hops = 0;

    for (;;) {
        if (!read_page(page_id)) { render_page(); return; }
        if (page_revisit < 0) break;
        if (++hops > 8) {
            /* Deux pages qui se renvoient l'une a l'autre : on relit
             * celle-ci en ignorant sa ligne V, pour que le joueur retrouve
             * son texte et ses choix au lieu d'un ecran mort. */
            page_ignore_v = 1;
            read_page(page_id);
            page_ignore_v = 0;
            break;
        }
        page_id = page_revisit;
    }

    /* La page du detour n'est PAS marquee : c'est celle ou l'on arrive qui
     * l'est, et de toute facon elle l'etait deja. */
    scene_mark_visited((unsigned int)page_id);

    /* L'image est decodee en page HGR 1 mais PAS montree : on reste sur le
     * texte, c'est au joueur de basculer. */
    has_image = load_hgr_image(page_id);
    render_page();
}

/* ── Votre chaine (le sac) ────────────────────────────────────────────────
 *
 * Le sac EST la chaine : il montre les selfies pris et le materiel ramasse.
 * Les jetons prefixes d'un point sont des drapeaux de scenario -- "Chagrin
 * console", "Bizz humilie" -- et ne s'affichent jamais.
 *
 * L'ecran force le mode texte : ouvert depuis le mode image, il se dessinerait
 * derriere l'illustration et la machine semblerait bloquee. On rend au joueur,
 * en sortant, le mode qu'il avait choisi. */
static void show_inventory(void)
{
    unsigned char i, row = 3, n = 0;
    int back = video_mode;
    char key;

    set_video_mode(0);
    wipe();
    render_title_bar("@COSMOSELFIE");

    for (i = 0; i < obj_count; ++i) {
        if (object_hidden(i) || !inv_has(i)) continue;
        put_trunc(2, row, "- ", 2);
        put_trunc(4, row, obj_lbl[i], 70);
        row++; n++;
    }
    if (n == 0)
        print_at(3, is_fr() ? "  Votre chaine est vide. Zero selfie, zero materiel."
                            : "  Your channel is empty. No selfie, no gear.");

    print_at(CHOICE_ROWN, is_fr() ? "[I] ou [ESC] pour revenir a l'aventure"
                                  : "[I] or [ESC] to go back to the adventure");
    do {
        key = cgetc();
    } while (key != 27 && key != 'I' && key != 'i');

    render_page();
    set_video_mode(back);
}

/* ── L'ecran de titre ─────────────────────────────────────────────────── */

static void select_language(void)
{
    char key;

    videomode(VIDEOMODE_80COL);
    enable_text_mode();
    clrscr();

    cprintf("\r\n\r\n\r\n");
    cprintf("          ====================================================\r\n");
    cprintf("                      SPACE EXPLORER TRIP\r\n");
    cprintf("          ====================================================\r\n");
    cprintf("\r\n\r\n");
    cprintf("                    SELECT YOUR LANGUAGE / LANGUE\r\n");
    cprintf("\r\n\r\n");
    cprintf("                         [F] - Francais\r\n");
    cprintf("\r\n");
    cprintf("                         [E] - English\r\n");
    cprintf("\r\n\r\n\r\n");
    cprintf("          ====================================================\r\n");

    for (;;) {
        key = cgetc();
        if (key == 'F' || key == 'f') { strcpy(language, "FR"); return; }
        if (key == 'E' || key == 'e') { strcpy(language, "EN"); return; }
    }
}

static void title_screen(void)
{
    clrscr();
    cprintf("\r\n");
    cprintf("          ====================================================\r\n");
    cprintf("                      SPACE EXPLORER TRIP\r\n");

    if (is_fr()) {
        cprintf("                 Une Odyssee Interactive Galactique\r\n");
        cprintf("          ====================================================\r\n");
        cprintf("\r\n");
        cprintf("  Vous animez @CosmoSelfie. Vous avez douze abonnes, dont votre mere\r\n");
        cprintf("  et un bot. Le Grand Defi Selfie Galactique vient d'etre lance : le\r\n");
        cprintf("  premier createur qui poste un selfie avec cinq legendes de l'univers\r\n");
        cprintf("  decroche un million d'abonnes.\r\n");
        cprintf("\r\n");
        cprintf("  Vous avez un Cabriolet chrome, un Holophone et du culot. C'est un\r\n");
        cprintf("  debut.\r\n");
        cprintf("\r\n");
        cprintf("  COMMANDES:\r\n");
        cprintf("    [A-E]    - Choisir\r\n");
        cprintf("    [I]      - Votre chaine (selfies et materiel)\r\n");
        cprintf("    [ESPACE] - Basculer entre texte et image\r\n");
        cprintf("    [Q]      - Quitter l'aventure\r\n");
        cprintf("\r\n");
        cprintf("  Un jeu de VERHILLE Arnaud - gist974@gmail.com\r\n");
        cprintf("\r\n");
        cprintf("            >>> Appuyez sur une touche pour decoller ! <<<\r\n");
    } else {
        cprintf("                 An Interactive Galactic Odyssey\r\n");
        cprintf("          ====================================================\r\n");
        cprintf("\r\n");
        cprintf("  You host @CosmoSelfie. You have twelve subscribers, one of them your\r\n");
        cprintf("  mother and one a bot. The Great Galactic Selfie Challenge has just\r\n");
        cprintf("  started: the first creator to post a selfie with five legends of the\r\n");
        cprintf("  universe wins a million subscribers.\r\n");
        cprintf("\r\n");
        cprintf("  You have a chrome Convertible, a Holophone and some nerve. It is a\r\n");
        cprintf("  start.\r\n");
        cprintf("\r\n");
        cprintf("  COMMANDS:\r\n");
        cprintf("    [A-E]    - Choose\r\n");
        cprintf("    [I]      - Your channel (selfies and gear)\r\n");
        cprintf("    [SPACE]  - Toggle between text and picture\r\n");
        cprintf("    [Q]      - Quit the adventure\r\n");
        cprintf("\r\n");
        cprintf("  A game by VERHILLE Arnaud - gist974@gmail.com\r\n");
        cprintf("\r\n");
        cprintf("              >>> Press any key to launch! <<<\r\n");
    }
    cgetc();
}

/* ── La boucle principale ─────────────────────────────────────────────── */

void main(void)
{
    char key;
    unsigned char choice_num;

    select_language();
    objects_load();
    title_screen();

    scene_memory_reset();
    load_page(1);

    for (;;) {
        key = cgetc();

        if (key == ' ') {
            /* Pas d'image pour cette page : le texte reste. */
            if (has_image) set_video_mode(video_mode ? 0 : 1);

        } else if (key == 'Q' || key == 'q') {
            enable_text_mode();
            videomode(VIDEOMODE_40COL);
            clrscr();
            cputs(is_fr() ? "Au revoir!\r\n" : "Goodbye!\r\n");
            return;

        } else if (key == 'I' || key == 'i') {
            show_inventory();

        } else if ((key >= 'A' && key <= 'Z') || (key >= 'a' && key <= 'z')) {
            /* Une lettre hors de A..Z passe en negatif, donc au-dela de
             * num_choices une fois dans l'octet : un seul test suffit. */
            choice_num = (unsigned char)((key >= 'a') ? (key - 'a') : (key - 'A'));
            if (choice_num >= num_choices) continue;

            if (!choice_available(choice_num)) {
                /* On ne franchit pas un poste de garde sans l'armure. */
                set_video_mode(0);
                clear_bottom();
                print_at(CHOICE_ROW0, is_fr()
                    ? "Il vous manque quelque chose pour ca."
                    : "You are missing something for that.");
                wait_key_at(CHOICE_ROWN, is_fr() ? "[ESPACE] continuer"
                                                 : "[SPACE] continue");
                render_page();
                continue;
            }
            load_page(choice_take(choice_num));
        }
    }
}
