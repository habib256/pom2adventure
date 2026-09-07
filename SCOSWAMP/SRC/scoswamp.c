#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <errno.h>
#include <unistd.h>
#include <fcntl.h>
#include <conio.h>
#include <stdarg.h>
#include <apple2enh.h>
#include <peekpoke.h>
#include "paths.h"
#include "memory_swap.h"
#include "hgr_rle.h"
#include "rules.h"
#include "dice.h"
#include "messages.h"
#include "sfx.h"
#include "music.h"

/* Bornes du segment LOWBSS, exportees par le lieur (define = yes) sous les
 * noms __LOWBSS_RUN__ et __LOWBSS_SIZE__. cc65 prefixe tout identifiant C
 * d'un '_', d'ou un souligne de moins ici. Leur "adresse" est la valeur :
 * c'est l'idiome cc65 pour les symboles de segment. */
extern char _LOWBSS_RUN__[];
extern char _LOWBSS_SIZE__[];

/* Adresse de la page HGR 1 */
#define HGR_PAGE1 ((unsigned char*)0x2000)
#define HGR_SIZE  16384
/* Le corpus ne depasse jamais 5 choix sur une page. Choice occupe 8 octets :
 * les titres pointent dans file_buffer et ne sont pas recopies par choix.
 * reflow_txt.py tient la limite de cinq choix. */
#define MAX_CHOICES 5
/* Pas FILENAME_MAX : build_paths n'ecrit jamais que "N999.RLE" (9 octets) et
 * "N999" (5). Deux champs de 64 octets pour ca, c'etaient 96 octets de BSS
 * dormants -- et c'est le seul levier memoire du programme qui ne depende
 * d'aucune mesure du corpus. */
#define MAX_PATH  10

/* Mise en page d'une scene, en dur sur les 24 lignes de l'ecran 80 colonnes :
 *
 *   ligne  1      barre en video inverse : titre de la scene + rappel touches
 *   lignes 2-19   le texte, deja replie a 78 colonnes dans le fichier
 *   ligne  20     clairiere et sorties, en video inverse
 *   lignes 21-24  les choix
 *
 * Les 4 lignes du bas ne sont pas un choix esthetique : ce sont EXACTEMENT
 * celles que le mode mixte laisse voir sous l'image HGR. Les choix y etant
 * toujours, on peut choisir sans quitter l'illustration.
 *
 * Le corps et les choix tiennent dans ce budget pour les 804 pages du corpus,
 * et SCOSWAMP.MORE/TOOLS/reflow_txt.py le verifie fichier par fichier. */
#define BODY_ROW0    1    /* premiere ligne de texte (0 = barre de titre) */
#define BODY_ROWS    18   /* lignes 2 a 19 */
#define PLACE_ROW    19   /* ligne 20, juste au-dessus du mode mixte */
#define CHOICE_ROW0  20   /* lignes 21 a 24 */
#define CHOICE_ROWN  23
#define CHOICE_COL2  40   /* colonne du 2e choix quand deux tiennent sur 1 ligne */
#define CHOICE_WIDTH 39   /* largeur utile d'une colonne de choix */

/* Le livre ne met jamais plus de trois adversaires sur une page : les deux
 * LOUPS du 224, les trois BRIGANDS du 235. */
#define MAX_FOES 3

/* Le titre de choix le plus long du corpus fait 72 caracteres, remesure le
 * 2026-08-30 sur les deux langues. 76 laisse trois caracteres de battement --
 * a cinq emplacements, chaque caractere de rab se paie cinq fois, donc
 * descendre a 73 rend 15 octets. Levier tenu en reserve, PAS pris : le corpus
 * est en cours d'edition ailleurs, et un titre de 73 caracteres serait
 * tronque a l'ecran sans que rien ne le dise. reflow_txt.py le refuse
 * desormais, ce qui rendra le levier prenable. */

typedef struct {
    int scene_id;
    /* Pierre remise en choisissant cette option, STONE_COUNT si aucune. Le
     * livre pose le cas au paragraphe 283 : "Il vous donne alors une Pierre de
     * Magie benefique (choisissez vous-meme laquelle)". */
    unsigned char grant;
    /* Pierre exigee par ce choix, STONE_COUNT si aucune. Elle est consommee
     * en le prenant : "les Pierres de Magie se desintegrent des qu'on les a
     * utilisees". Sans ce champ, les 37 choix du corpus qui depensent une
     * Pierre ne touchaient pas au sac -- et rien n'empechait d'en lancer une
     * qu'on n'avait pas. */
    unsigned char require;
    unsigned char object; /* OBJ_COUNT si aucune condition d'objet */
    unsigned char obj_mode; /* 1=possede, 2=ne possede pas, 3=consomme */
    char* title;          /* pointe dans file_buffer, valide jusqu'a la scene suivante */
} Choice;

/* Structure pour l'état global de l'application */
typedef struct {
    int current_scene;
    unsigned char video_mode;  /* 0=texte 80col, 1=HGR plein, 2=mixte */
    Choice choices[MAX_CHOICES];
    unsigned char num_choices;
    char language[3];  /* FR ou EN */
    char imgPath[MAX_PATH];
    char txtPath[MAX_PATH];
    unsigned char has_image; /* image de la scene decodee en page HGR 1 ? */

    /* La Feuille d'Aventure et la rencontre en cours. */
    Character hero;
    unsigned char hero_ready; /* les des ont ete jetes */
    /* "Parfois, vous les affronterez comme si elles n'etaient qu'un seul
     * monstre ; parfois, vous les combattrez une par une." Les deux rencontres
     * a plusieurs du Marais sont du second type : une file, affrontee dans
     * l'ordre ou la page la donne. */
    Monster   foes[MAX_FOES];
    /* Ligne MI : la page dont on emprunte l'image de bataille pour CET
     * adversaire, 0 si c'est celle de la page courante. Une file peut melanger
     * les especes -- deux Loups puis leur Maitre, page 120 -- et une seule
     * illustration pour les trois montrait le Maitre des le premier assaut. */
    unsigned int  foe_img[MAX_FOES];
    unsigned char foe_count; /* nombre de lignes M sur la page */
    unsigned char foe_cur;   /* adversaire en cours dans la file */
    int       flee_target;   /* scene ou mene la Fuite, -1 si la page n'en offre pas */
    int       pending_scene; /* scene a charger au prochain tour de boucle, -1 sinon */
    int       revisit;       /* ligne V : ou aller si la clairiere est deja vue, -1 sinon */
    unsigned char choose_n;  /* Pierres a choisir en entrant, 0 si aucune */
    char      choose_cats[3];/* categories permises : N, B, M */
    int       luck_ok;       /* scene si Chanceux, -1 si la page ne teste rien */
    int       luck_ko;       /* scene si Malchanceux */
    int       luck_dok;      /* effet Chanceux : END pour CL, dice_carac pour CE */
    int       luck_dko;
    /* Ligne MV : ou aller quand le dernier adversaire de la file est tombe,
     * -1 si la page rend la main aux choix comme avant. */
    int       win_scene;
    /* Ligne ED : le jet de des visible. `dice_n` porte le SIGNE (gain ou
     * perte) et le NOMBRE de des dans sa valeur absolue ; 0 = pas de jet.
     * La valeur interne 3 reserve CE ; ED positif est borne a deux des. */
    signed char   dice_n;
    unsigned char dice_carac;  /* 0 END, 1 HAB, 2 CHA, 3 OR */
    /* Ligne CS : 2d6 contre une caracteristique NOMMEE, sans depenser de
     * point de CHANCE -- le "Lancez deux des. Si le total est inferieur ou
     * egal a vos points d'ENDURANCE..." du livre. -1 = pas de test. */
    int       cs_ok, cs_ko;
    unsigned char cs_carac;
    /* Ligne MB : duel au premier sang. La premiere blessure arrete le combat
     * et decide de la suite -- qui a touche, pas qui est mort. -1 = non. */
    int       mb_ok, mb_ko;
    /* Ligne DV : l'ENDURANCE perdue au dernier combat GAGNE, pour que la
     * page d'apres n'ait pas a demander au joueur d'evaluer ses blessures.
     * dv_done bloque la cascade a la premiere ligne DV qui correspond. */
    unsigned char last_loss;
    unsigned char dv_done;
    char music_name[16];     /* ligne MU : MUSIC/<NOM>.MB, "-" = silence, vide = rien */
    unsigned char music_over; /* la ligne MU portait un + : surcouche de la page */
} AppState;

/* Variables globales optimisées.
 *
 * `app` vit en RAM basse avec les tampons : 238 octets rendus a la fenetre
 * principale, et pas un cycle de plus a l'acces -- une adresse absolue en
 * $1xxx coute exactement ce qu'elle coutait en $Axxx. */
#pragma bss-name (push, "LOWBSS")
AppState app;
#pragma bss-name (pop)
/* La page la plus longue du corpus fait 1270 octets (TEXTFR/N350/N361.TXT
 * avec sa ligne MU, mesure du 2026-09-06). fread en lit SIZE-1 et reserve le dernier
 * octet au '\0'. reflow_txt.py tient exactement la meme limite. */
#define FILE_BUFFER_SIZE 1280
/* En LOWBSS ($1000-$1FFF, voir scoswamp.cfg) : la RAM basse entre le tampon
 * ProDOS et HGR page 1, que le lieur ignorait. main() la met a zero. */
#pragma bss-name (push, "LOWBSS")
char file_buffer[FILE_BUFFER_SIZE];
#pragma bss-name (pop)

/* Sauvegarde binaire SCS5, avec lecture des anciens fichiers SCS4.
 * Dix emplacements numerotes de 0 a 9 sur le disque. */
#define SAVE_HEADER 8
/* Le titre de la page ou la partie s'est arretee, tel que la ligne T le
 * donne, sur 32 octets termines par zero : la page des sauvegardes l'affiche
 * pour que le joueur se situe dans le Marais avant de reprendre. */
#define SAVE_TITLE  32
/* SCS4 a ajoute la clairiere collante du menu MAP. Sans elle, une
 * partie reprise au milieu d'un combat -- une page qui n'est d'aucun lieu --
 * rouvrait la carte sans savoir ou l'on se tient. C'est ce qui fait passer le
 * format de SCS3 a SCS4 : les anciennes sauvegardes sont refusees par la
 * signature, pas lues de travers. */
/* SCS5 ajoute last_loss apres la clairiere : DV doit retrouver les blessures
 * du combat, meme si une autre partie a ete jouee entre-temps. */
#define SAVE_SIZE (SAVE_HEADER + SAVE_TITLE + sizeof(Character) + SCENE_MEMORY_SIZE + MONSTER_MEMORY_SIZE + 2)
#define save_data ((unsigned char*)file_buffer)
static unsigned char restoring;
/* La clairiere ou l'on se tient, MAP_NONE si aucune n'est connue. Declaree
 * ici parce que la sauvegarde l'emporte (SCS4) et qu'elle est ecrite bien
 * avant le bloc de la carte. */
#define MAP_NONE 0xFF
static unsigned char map_here = MAP_NONE;
static char* scene_title;   /* la ligne T de la page, dans file_buffer */
static void render_scene(void);
static void clear_bottom(void);
static void pad_to(unsigned char col);   /* defini avec le bandeau de combat */
void load_scene(int scene_id);
static unsigned char show_saves(unsigned char saving);

/* La memoire d'une rencontre appartient a la clairiere, pas au paragraphe
 * qui a lance le combat. Une fuite puis un retour par une autre page doit
 * donc retrouver le meme adversaire blesse. Les clairieres commencent a 1
 * pour laisser 0 libre dans la table claircie de rules.c ; une page hors carte
 * garde une cle secondaire disjointe pour les rares combats scenarises. */
static unsigned int monster_zone_key(void)
{
    if (map_here != MAP_NONE) return (unsigned int)map_here + 1u;
    return 0x0100u + (unsigned int)app.current_scene;
}

#pragma code-name (push, "LC")
#pragma rodata-name (push, "LC")
#pragma code-name (push, "CODE")
static unsigned char* save_u16(unsigned char* p, unsigned int v)
{ *p++ = (unsigned char)v; *p++ = (unsigned char)(v >> 8); return p; }
#pragma code-name (pop)
#pragma code-name (push, "CODE")
static unsigned int load_u16(const unsigned char* p)
{ return (unsigned int)p[0] | ((unsigned int)p[1] << 8); }
#pragma code-name (pop)

#pragma code-name (push, "CODE")
static unsigned char save_checksum(void)
{
    unsigned int i; unsigned char sum=0;
    for(i=5;i<SAVE_SIZE;i++) sum^=save_data[i];
    return sum;
}
#pragma code-name (pop)

/* pack_save reste en CODE : la Language Card ne peut pas accueillir
 * cette fonction. Les marges courantes sont mesurees dans build.map. */
#pragma code-name (push, "CODE")
static void pack_save(void)
{
    unsigned char* p = save_data + SAVE_HEADER;
    unsigned char n = scene_title ? (unsigned char)strlen(scene_title) : 0;
    if (n > SAVE_TITLE - 1) n = SAVE_TITLE - 1;
    /* Le titre vit dans file_buffer, que save_data recouvre : il part en
     * premier, et par memmove, car sa source peut chevaucher sa place. */
    if (n) memmove(p, scene_title, n);
    memset(p + n, 0, SAVE_TITLE - n);
    p += SAVE_TITLE;
    memcpy(save_data, "SCS5", 4);
    save_u16(save_data + 5, (unsigned int)app.current_scene);
    save_data[7] = app.language[0];
    memcpy(p,&app.hero,sizeof app.hero); p+=sizeof app.hero;
    scene_memory_export(p); p += SCENE_MEMORY_SIZE;
    monster_memory_export(p); p += MONSTER_MEMORY_SIZE;
    *p++ = map_here;
    *p = app.last_loss;
    save_data[4]=save_checksum();
}

#pragma code-name (pop)
/* Les migrations du jeu sont compilees hors machine depuis RULES.json.
 * Chaque ligne teste un groupe de drapeaux absent, puis une visite ; poser
 * un drapeau du groupe empeche les branches suivantes de l'ecraser. */
#include "game_rules.h"
#pragma code-name (push, "CODE")
#pragma rodata-name (push, "RODATA")
static void migrate_saved_flags(void)
{
    static const unsigned int rows[][3] = GAME_SAVE_MIGRATIONS;
    const unsigned int* p = rows[0];
    unsigned char i;
    for (i = 0; i < GAME_SAVE_MIGRATION_COUNT; ++i, p += 3) {
        if (!(app.hero.objects & p[0]) && scene_visited(p[1]))
            app.hero.objects |= p[2];
    }
}
#pragma rodata-name (pop)
#pragma code-name (pop)
static unsigned char unpack_save(void)
{
    const unsigned char* p; int scene;
    /* load_game a deja valide la version et sa longueur exacte. */
    if (memcmp(save_data,"SCS",3)!=0 || save_data[4]!=save_checksum()) return 0;
    p=save_data+5; scene=(int)load_u16(p); p+=2;
    app.language[0]=*p++; app.language[1]=(app.language[0]=='F')?'R':'N'; app.language[2]='\0';
    p += SAVE_TITLE;
    memcpy(&app.hero,p,sizeof app.hero); p+=sizeof app.hero;
    scene_memory_import(p); p+=SCENE_MEMORY_SIZE;
    monster_memory_import(p); p+=MONSTER_MEMORY_SIZE;
    migrate_saved_flags();
    map_here=*p++;
    app.last_loss=*p;
    app.hero_ready=1;
    restoring=1;
    app.pending_scene=scene;
    return 1;
}
#pragma rodata-name (pop)
#pragma code-name (pop)

/* Les appels ProDOS doivent vivre en memoire principale : ProDOS utilise la
 * Language Card et peut remplacer le code LC pendant un open/read/write. */
static unsigned char enter_save(unsigned char slot)
{
    memcpy(app.imgPath,"SAVE0",6); app.imgPath[4]=(char)('0'+slot);
    return chdir("/SCOSWAMP")==0 && chdir("SAVE")==0;
}

static unsigned char save_game(unsigned char slot)
{
    int fd; unsigned char ok; pack_save();
    if(!enter_save(slot)) return 0;
    fd=open(app.imgPath,O_WRONLY|O_TRUNC); if(fd<0) return 0;
    ok=(write(fd,save_data,SAVE_SIZE)==SAVE_SIZE); close(fd); return ok;
}

static unsigned char load_game(unsigned char slot)
{
    FILE* f; unsigned char ok;
    size_t n;
    if(!enter_save(slot)) return 0;
    f=fopen(app.imgPath,"r"); if(!f) return 0;
    /* Refuser longueurs et en-tetes invalides avant toute mutation du heros.
     * Le checksum XOR detecte certaines alterations, pas toutes. */
    /* SCS4 reste lisible : il n'avait pas last_loss. Le zero ajoute ne change
     * pas son checksum XOR et evite d'heriter des blessures d'une autre partie. */
    save_data[SAVE_SIZE - 1] = 0;
    n=fread(save_data,1,SAVE_SIZE,f);
    ok=(fgetc(f)==EOF && !ferror(f));
    fclose(f);
    if (!ok || (save_data[7]!='F' && save_data[7]!='E') ||
        load_u16(save_data+5) >= SCENE_MEMORY_SIZE*8u) return 0;
    ok=(unsigned char)(save_data[3]-'4');
    return ok <= 1 && n == SAVE_SIZE-1+ok && unpack_save();
}

/* Le titre range dans un emplacement, ou une chaine vide si l'emplacement
 * est vierge (les SAVEn du disque font deux octets) ou d'un autre format.
 * Ne lit que l'en-tete : dix emplacements a lister, pas dix parties. */
#pragma bss-name (push, "MAPBSS")
static void slot_title(unsigned char slot, char* out)
{
    FILE* f;
    unsigned char hdr[SAVE_HEADER + SAVE_TITLE];
    out[0] = '\0';
    if (!enter_save(slot)) return;
    f = fopen(app.imgPath, "r"); if (!f) return;
    if (fread(hdr, 1, sizeof hdr, f) == sizeof hdr &&
        memcmp(hdr, "SCS", 3) == 0 && (hdr[3] == '4' || hdr[3] == '5')) {
        memcpy(out, hdr + SAVE_HEADER, SAVE_TITLE);
        out[SAVE_TITLE - 1] = '\0';
    }
    fclose(f);
}
#pragma bss-name (pop)

/* Decoupage de la scene courante. Titre et lignes de corps ne sont pas
 * recopies : ce sont des pointeurs DANS file_buffer, dont les fins de ligne
 * ont ete remplacees par des '\0'. Le buffer n'est reecrit qu'au chargement
 * de la scene suivante, donc ils restent valides tant qu'on affiche celle-ci
 * -- et ca evite un seul octet de copie. */
/* En RAM basse, avec les autres tampons : ce sont des octets rendus a la
 * fenetre principale, ou il ne restait que 510 avant le menu MAP. */
#pragma bss-name (push, "LOWBSS")
static char* body_lines[BODY_ROWS];
#pragma bss-name (pop)
static unsigned char body_count;

/* La langue tient dans une initiale : strcmp(app.language, "FR") coutait la
 * boucle de comparaison et sa chaine, a chaque fois. */
static unsigned char is_fr(void) { return app.language[0] == 'F'; }

static int enter_asset_dir(const char* kind, int scene_id)
{
    char bucket[5];
    unsigned int subdirectory = ((unsigned int)scene_id / 50u) * 50u;

    if (chdir("/SCOSWAMP") != 0) return 0;
    if (chdir(kind) != 0) return 0;
    *put_scene(bucket, subdirectory) = '\0';
    if (chdir(bucket) != 0) return 0;
    return 1;
}

/* La Mockingboard, si music_detect l'a trouvee ; 0 sinon, et music_load ne
 * lit meme pas le disque. */
static unsigned char music_slot;

/* Ce qui joue, et le theme de la zone courante : deux noms de MUSIC/.
 * music_cur vide = silence. Ils different quand une surcouche joue.
 * cur_half est la moitie qui joue. music_here suit la derniere clairiere
 * mise en musique, independamment de map_here que les sauvegardes restaurent. */
#pragma bss-name (push, "LOWBSS")
static char music_cur[16];
static char music_zone[16];
#pragma bss-name (pop)
static unsigned char cur_half;
static unsigned char music_here = MAP_NONE;

/* Lit MUSIC/<name> dans la moitie `half`. Rend 1 si c'est bien un flux MB1
 * qui y tient en entier -- la moitie 1 ne fait que 1 280 octets, et un flux
 * tronque partirait dans les octets qui suivent. Un seul fichier ouvert a la
 * fois, comme partout ; la musique en cours joue pendant la lecture. */
static unsigned char music_load(const char* name, unsigned char half)
{
    FILE* f;
    size_t n, total = 0, cap = half ? MUSIC_OVER : MUSIC_ZONE;
    unsigned int offset = half ? MUSIC_ZONE : 0;
    unsigned char valid = 1;
    if (!music_slot) return 0;
    if (chdir("/SCOSWAMP") != 0 || chdir("MUSIC") != 0) return 0;
    f = fopen(name, "rb"); if (!f) return 0;
    do {
        n = fread(music_buf, 1, MUSIC_STAGE, f);
        if (total == 0 && (n <= 8 || memcmp(music_buf, "MB1", 3))) valid = 0;
        if (total + n > cap) { valid = 0; break; }
        if (n) music_store(offset + total, n);
        total += n;
    } while (n == MUSIC_STAGE);
    if (ferror(f)) valid = 0;
    fclose(f);
    return valid;

}

/* Charge <name> dans la moitie qui ne joue pas -- l'autre continue pendant
 * la lecture -- puis bascule dessus : la seule interruption est la bascule,
 * quelques microsecondes. Si la moitie libre est la petite et que le flux
 * n'y tient pas, on passe par la grande, au prix d'une coupure : cela
 * n'arrive qu'en changeant de zone. Le seul chemin qui lit le disque. */
/* Attend la fin du fondu en cours ; le tick tourne pendant ce temps. */
static void music_settle(void)
{
    while (music_fading()) ;
}

static void music_switch(const char* name, unsigned char over)
{
    unsigned char h = (unsigned char)(1 - cur_half);
    music_fade_out();           /* l'ancienne s'efface pendant la lecture */
    if (!music_load(name, h)) {
        if (h == 0) { music_fade_in(); return; }   /* le fichier manque : on remonte */
        music_settle();
        music_stop();
        music_cur[0] = '\0';
        h = 0;
        if (!music_load(name, 0)) return;
    }
    music_settle();
    music_pause();              /* tick arrete : l'echange de curseurs est sur */
    /* Le pilote lit ce drapeau à END. Les thèmes et scènes restent à passage
     * unique ; seule la surcouche de combat, appelée avec over=1, boucle. */
    music_select(h);
    music_set_loop(over);
    music_play();               /* et la nouvelle monte en fondu */
    cur_half = h;
    memcpy(music_cur, name, sizeof music_cur);
}

/* load_scene decide si le lieu musical change. Ici, l'ancien theme s'efface
 * puis celui de MU commence depuis le debut ; MU absent ou "-" fait silence.
 * La position musicale ne se restaure pas depuis la sauvegarde : elle doit
 * encore designer ce qui jouait avant le chargement pour detecter le saut. */
static void music_for_clearing(void)
{
    const char* n = app.music_name;
    music_fade_out();
    music_settle();
    music_stop();
    music_cur[0] = music_zone[0] = '\0';
    music_here = map_here;
    if (n[0] == '\0' || n[0] == '-') return;
    /* Forcer la grande moitié : même deux clairières portant le même nom
     * doivent chacune jouer le morceau une fois depuis son début. */
    cur_half = 1;
    music_switch(n, 0);
    if (music_cur[0]) memcpy(music_zone, music_cur, sizeof music_zone);
}

/* Fonction pour charger une image DHGR */
/* Charge DHGR/<bucket>/<prefixe><id>.RLE dans les deux banques DHGR page 1.
 *
 *   'N' : l'illustration de la clairiere ;
 *   'B' : l'image de bataille, les deux adversaires face a face. Elle est
 *         optionnelle -- quand elle manque, on retombe sur l'illustration de
 *         la clairiere, qui montre deja la creature.
 *
 * build_paths ecrit "N012.RLE" ; changer le premier caractere suffit, et evite
 * un second sprintf dans un binaire ou chaque octet compte. */
static unsigned char load_hgr_image_as(int scene_id, char prefix) {
    if (build_paths(scene_id, app.language, app.imgPath, app.txtPath) != 0) {
        return 0;  /* Scene ID hors plage */
    }
    app.imgPath[0] = prefix;

    if (!enter_asset_dir("DHGR", scene_id)) {
        return 0;
    }
    return hgr_rle_load(app.imgPath);
}

/* La page dont l'image de bataille est actuellement en HGR page 1, ou 0 quand
 * on n'en a pas encore charge pour cette scene. */
static int foe_shown;
static unsigned char magic_forbidden; /* MM 1 : aucune Pierre pendant ce combat */
static unsigned char flee_after; /* MF : assauts encore a resoudre avant la fuite */

/* L'illustration de l'adversaire EN COURS. Le disque range une image de
 * bataille par page (B<page>.RLE), mais une page peut aligner trois creatures
 * differentes : la ligne MI dit alors de quelle page emprunter l'image. Sans
 * elle, c'est celle de la page -- exactement l'ancien comportement.
 *
 * Le garde `foe_shown` est ce qui rend l'appel gratuit quand l'image ne change
 * pas : une file d'une seule espece, ou une page sans ligne MI, ne relit pas
 * le disque entre deux adversaires. */
static void load_foe_image(void)
{
    int p = (int)app.foe_img[app.foe_cur];
    if (!p) p = app.current_scene;
    if (p == foe_shown) return;
    foe_shown = p;
    app.has_image = load_hgr_image_as(p, 'B');
}

/* Soft switches pour les modes video - version optimisée avec memory swap */
static void set_video_mode(unsigned char mode) {
    if (mode == 0) {
        /* Mode texte 80 colonnes - restaurer le texte sauvegardé */
        switch_to_text();
        app.video_mode = 0;
    } else if (mode == 1) {
        /* Mode HGR plein écran - sauvegarder le texte actuel */
        switch_to_hgr();
        app.video_mode = 1;
    } else if (mode == 2) {
        /* Mode mixte HGR + 4 lignes texte */
        switch_to_mixed();
        app.video_mode = 2;
    }
}

/* ── Mise en page ─────────────────────────────────────────────────────── */

/* Barre de titre, ligne 1, en video inverse sur les 80 colonnes. Les aides
 * clavier sont reservees au bandeau bas : le titre reste lisible et la carte
 * est la seule source des directions et des clairieres deja visitees. */
#pragma bss-name (push, "LOWBSS")
static char title_bar[81];
#pragma bss-name (pop)

/* Le formateur maison, a la place de la famille printf.
 *
 * Il connait %u, %s et %c, une largeur (%2u, %-12s) et une precision (%.75s)
 * -- tout ce que le code et le catalogue MSGFR/MSGEN emploient. Toute autre
 * lettre de conversion est lue comme %u. Rien de plus : _printf, vsnprintf,
 * vcprintf et ltoa coutaient 1,5 Ko de code pour ces trois conversions, et
 * sprintf les embarquait meme sans affichage formate.
 *
 * Les valeurs passent en `unsigned int` : cc65 promeut les caracteres et
 * octets a l'appel (pusha0), comme pour printf. Tout est en unsigned char
 * ici, et les locales sont statiques (-Cl) : chaque `int` ou variable de
 * pile coute une poignee d'octets par acces sur 6502. */
/* La sortie de cfmt : l'ecran, ou un tampon quand fmt_out est pose. La barre
 * de titre se compose ainsi en memoire pour etre peinte d'un bloc. */
static char* fmt_out;
static void emit(char c) { if (fmt_out) { *fmt_out = c; ++fmt_out; } else cputc(c); }
static void pad_spaces(unsigned char n) { while (n) { emit(' '); --n; } }

/* Les statiques de cfmt logent dans le fond de la zone MAPRAM : quelques
 * octets de plus rendus a la fenetre principale, et pas un cycle de plus --
 * une adresse absolue en $0Fxx vaut une adresse absolue en $Bxxx. */
#pragma bss-name (push, "MAPBSS")
static void cfmt(const char* f, ...)
{
    va_list ap;
    char buf[6];
    /* Trois pointeurs en page zero (la banque de registres de cc65 en tient
     * exactement trois). `f` reste en pile : va_start prend son adresse. */
    register const char* p = f;
    register const char* s;
    register char* q;
    unsigned char c, left, width, prec, n;
    va_start(ap, f);
    for (;;) {
        c = (unsigned char)*p++;
        if (c == 0) break;
        if (c != '%') { emit((char)c); continue; }
        left = 0; width = 0; prec = 255;
        c = (unsigned char)*p++;
        if (c == '-') { left = 1; c = (unsigned char)*p++; }
        while (c >= '0' && c <= '9') { width = width * 10 + (c - '0'); c = (unsigned char)*p++; }
        if (c == '.') {
            prec = 0;
            while ((c = (unsigned char)*p++) >= '0' && c <= '9') prec = prec * 10 + (c - '0');
        }
        if (c == 'c') {
            buf[0] = (char)va_arg(ap, int); buf[1] = '\0'; s = buf;
        } else if (c == 's') {
            s = va_arg(ap, const char*);
        } else {
            unsigned int v = va_arg(ap, unsigned int);
            q = buf + sizeof(buf) - 1;
            *q = '\0';
            do { *--q = (char)('0' + v % 10u); v /= 10u; } while (v);
            s = q;
        }
        n = (unsigned char)strlen(s);
        if (n > prec) n = prec;
        width = (width > n) ? (unsigned char)(width - n) : 0;
        if (!left) { pad_spaces(width); width = 0; }
        while (n) { emit(*s++); --n; }
        pad_spaces(width);
    }
    va_end(ap);
}
#pragma bss-name (pop)

/* Toute panne de disque passe par ici : l'etape qui a echoue, les deux codes
 * -- errno est celui de cc65, l'autre le code ProDOS brut -- et une touche.
 * Cinq variantes ecrites a la main coutaient chacune ses chaines et son code,
 * pour des pannes qu'un disque correct ne produit jamais : elles disent
 * maintenant la meme chose en un mot. */
static void oops(const char* etape)
{
    cputs(etape);
    cfmt(" errno=%u ProDOS=%u -- une touche\r\n",
         (unsigned)errno, (unsigned)_oserror);
    cgetc();
}

/* Q est une action destructive : une seconde touche valide explicitement le
 * depart, toute autre touche rend l'ecran courant sans quitter la partie. */
static unsigned char confirm_quit(void)
{
    char key;
    clear_bottom();
    gotoxy(0, CHOICE_ROW0 + 1);
    cputs(is_fr() ? "QUITTER vraiment ? O=oui, autre touche=non"
                  : "REALLY QUIT? Y=yes, any other key=no");
    pad_to(79);
    key = cgetc();
    if (is_fr() ? (key == 'O' || key == 'o') : (key == 'Y' || key == 'y')) {
        set_video_mode(0);
        videomode(VIDEOMODE_40COL);
        clrscr();
        cputs(is_fr() ? "Au revoir!\r\n" : "Goodbye!\r\n");
        exit(0);
    }
    render_scene();
    return 0;
}

/* `sheet` est un tampon statique (-Cl) : il part avec les autres en RAM
 * basse, ou il ne coute rien a la fenetre principale. */
#pragma bss-name (push, "LOWBSS")
static void render_title_bar(void)
{
    char sheet[40];
    unsigned char n;

    /* Une fois les des jetes, la barre porte la Feuille d'Aventure : les trois
     * caracteristiques sont ce qu'on consulte a chaque page, et le livre les
     * veut sous les yeux en permanence. Avant la creation du personnage, elle
     * sert encore au rappel des touches. */
    memset(title_bar, ' ', 80);
    title_bar[80] = '\0';

    if (scene_title != NULL) {
        n = (unsigned char)strlen(scene_title);
        if (n > 40) n = 40;
        memcpy(title_bar + 1, scene_title, n);
    }
    if (app.hero_ready) {
        /* Les etiquettes suivent la langue : en anglais ce sont SKILL,
         * STAMINA et LUCK, les trois mots de Fighting Fantasy.
         * cfmt ecrit dans `sheet` (fmt_out), et le bloc est cale a droite. */
        fmt_out = sheet;
        cfmt(is_fr() ? "HAB %u/%u  END %u/%u  CHA %u/%u"
                     : "SKL %u/%u  STA %u/%u  LCK %u/%u",
             app.hero.hab, app.hero.hab0, app.hero.end, app.hero.end0,
             app.hero.cha, app.hero.cha0);
        n = (unsigned char)(fmt_out - sheet);
        fmt_out = NULL;
        memcpy(title_bar + 79 - n, sheet, n);
    } else {
        /* Avant la creation du personnage : le rappel des touches. Il vit au
         * catalogue -- la barre ne se peint jamais avant messages_load. */
        const char* hint = msg(M_TOUCHES);
        n = (unsigned char)strlen(hint);
        memcpy(title_bar + 79 - n, hint, n);
    }

    revers(1);
    cputsxy(0, 0, title_bar);
    revers(0);
}
#pragma bss-name (pop)

/* Les choix, dans les 4 lignes du bas.
 *
 * Deux par ligne quand les deux tiennent dans une demi-largeur, sinon un seul
 * sur toute la ligne : c'est ce qui fait entrer jusqu'a 5 choix dans 4 lignes
 * (6 scenes du livre en ont 5). Rien n'est jamais ecrit dans la derniere
 * cellule de l'ecran : le firmware ferait scroller et toute la mise en page
 * remonterait d'une ligne. */
/* Un choix qui exige une Pierre absente du sac ne porte pas de lettre : on
 * le voit -- le livre l'ecrit, et savoir ce qu'une Pierre aurait permis fait
 * partie de la lecture -- mais on ne peut pas le prendre. */
/* The same goods can satisfy CB and be removed by PO/PD. */
#define STEALABLE ((unsigned int)((1u << OBJ_HIDDEN0) - 2u))

static unsigned char choice_available(unsigned char i)
{
    Choice* c = &app.choices[i];
    unsigned char has;
    if (c->require == 255) return 0; /* condition de visite non satisfaite */
    if (c->require < STONE_COUNT && !character_has_stone(&app.hero, (Stone)c->require)) return 0;
    if (c->object < OBJ_COUNT) {
        has = (unsigned char)character_has_object(&app.hero, (Object)c->object);
        return c->obj_mode == 2 ? !has : has;
    }
    if (c->object & 0x80) {
        has = (unsigned char)character_has_amulet(&app.hero, (Amulet)(c->object & 0x7f));
        return c->obj_mode == 2 ? !has : has;
    }
    if (c->object == 0x7d) return app.hero.gold >= c->obj_mode;
    if (c->object == 0x7f || c->object == 0x7e || c->object == 0x7c) {
        unsigned char n, s;
        if (c->object == 0x7f) n = character_amulet_count(&app.hero);
        else {
            n = 0;
            for (s = 0; s < STONE_COUNT; ++s) {
                if (app.hero.stones[s] >= 15 - n) { n = 15; break; }
                n += app.hero.stones[s];
            }
        }
        if (c->object == 0x7c) {
            if ((app.hero.objects & STEALABLE) || app.hero.amulets) n = 1;
            return !!n == c->obj_mode;
        }
        return n >= (c->obj_mode >> 4) && n <= (c->obj_mode & 15);
    }
    return 1;
}

static char choice_tag(unsigned char i)
{
    return choice_available(i) ? (char)('A' + i) : '-';
}

/* Deux choix courts tiennent sur une ligne, en deux colonnes. */
static unsigned char pair_fits(unsigned char i)
{
    return i + 1 < app.num_choices &&
           strlen(app.choices[i].title)     <= CHOICE_WIDTH - 3 &&
           strlen(app.choices[i + 1].title) <= CHOICE_WIDTH - 3;
}

static void render_choices(void)
{
    unsigned char i, rows = 0, row;

    /* Les choix se calent en BAS des quatre lignes : la derniere ligne de
     * choix est toujours la ligne 24, et le vide reste au-dessus, contre le
     * texte. On compte d'abord les lignes, avec la meme regle de pairage. */
    for (i = 0; i < app.num_choices; i += pair_fits(i) ? 2 : 1) rows++;
    if (rows > CHOICE_ROWN - CHOICE_ROW0 + 1) rows = CHOICE_ROWN - CHOICE_ROW0 + 1;
    row = (unsigned char)(CHOICE_ROWN + 1 - rows);

    i = 0;
    while (i < app.num_choices && row <= CHOICE_ROWN) {
        gotoxy(0, row);
        if (pair_fits(i)) {
            cfmt("%c) %s", choice_tag(i), app.choices[i].title);
            gotoxy(CHOICE_COL2, row);
            cfmt("%c) %s", choice_tag(i + 1), app.choices[i + 1].title);
            i += 2;
        } else {
            cfmt("%c) %.75s", choice_tag(i), app.choices[i].title);
            i += 1;
        }
        row++;
    }
}


/* ── La carte du Marais ───────────────────────────────────────────────────
 *
 * « Pour vous aider a etablir votre carte, TOUTES LES CLAIRIERES ONT ETE
 * NUMEROTEES. » Le Marais aux Scorpions est le seul Defis Fantastiques ou le
 * lecteur DOIT dessiner sa carte, et l'une des trois missions -- celle de
 * Pompatarte -- consiste a en rapporter une. Le menu MAP la tient a sa place,
 * et ne montre que ce qu'il a vu.
 *
 * Les donnees sont sur le disque, dans le fichier MAP que TOOLS/build_map.py
 * ecrit depuis SCOSWAMP.MORE/carte.json : le texte du jeu est une donnee, la
 * carte aussi. Elles vivent en $0C00-$0FFF, le kilo-octet que scoswamp.cfg
 * reservait a un SECOND tampon ProDOS -- le jeu n'ouvre jamais qu'un fichier
 * a la fois. Elles ne coutent donc rien a la fenetre principale, ou il ne
 * restait que 510 octets. Seule la table de rabattement page -> clairiere
 * reste en RAM principale : elle est lue a chaque page.
 *
 * Le moteur ne porte AUCUNE table de sentiers, ni aucun bitmap de sentiers
 * parcourus. Une clairiere annonce ses directions ; le voisin est la premiere
 * case occupee de la ligne ou de la colonne, ce qui rend gratuits les trois
 * sentiers de deux cases que la grille a du etirer -- « un sentier peut
 * suivre un trace sinueux mais sa direction generale restera toujours la
 * meme ». Et un sentier est emprunte quand ses deux bouts sont vus : les 52
 * octets du bitmap `visited`, deja sauvegardes, disent tout.
 */
#define MAP_CLR    35                        /* clairieres canoniques */
#define MAP_PAGES  116                       /* pages rattachees a un lieu */
#define MAP_NAMEW  13                        /* 12 caracteres + le zero */
#define MAP_HEAD   20                        /* taille de l'en-tete */
#define MAP_POOL   (MAP_HEAD + 3 * MAP_CLR)  /* 125 : debut du bloc de langue */

/* Les chaines de l'ecran MAP, rangees dans le bloc de langue derriere les 35
 * noms. L'ORDRE FAIT FOI : c'est celui de la liste UI de build_map.py. Elles
 * ne passent pas par MSGFR/MSGEN parce que le catalogue vit en RAM basse, ou
 * il ne restait que 39 octets ; le bloc MAP, lui, a de la place. */
enum {
    MS_TITRE, MS_SUR35, MS_SORTIES, MS_VUE, MS_INCONNUE, MS_HORS,
    MS_LEGENDE, MS_LEG1, MS_LEG2, MS_LEG3, MS_LEG4, MS_LEG5,
    MS_TOUCHES, MS_ANNEAU, MS_LIEU, MS_DEJA, MS_DIRS
};

/* 884 et non 1 024 : le bloc resident mesure 871 octets (125 d'en-tete et de
 * clairieres, 746 pour le plus gros des deux blocs de langue). build_map.py
 * porte la meme constante et refuse de la depasser -- son message dit quoi
 * raccourcir. Les octets qui restent dans la zone MAPRAM accueillent d'autres
 * tampons chasses de la fenetre principale ; ld65 refuse le lien si
 * l'ensemble deborde. */
#pragma bss-name (push, "MAPBSS")
static unsigned char map_data[884];
#pragma bss-name (pop)
/* 115 paires (ecart depuis la page precedente, index de clairiere), triees.
 * La table plate de 412 octets que CARTOGRAPHIE.md Sec. 7.2 preferait ne
 * tenait plus : 115 paires en font 230, et la boucle coute trente octets. */
#pragma bss-name (push, "LOWBSS")
static unsigned char map_pages[2 * MAP_PAGES];
static unsigned char map_vu[MAP_CLR];
#pragma bss-name (pop)
static unsigned char map_ready;
/* map_here -- la clairiere courante, declaree plus haut avec la sauvegarde --
 * est COLLANTE : 297 pages sur 412 (combats, dialogues, morts, prologue) ne
 * sont d'aucun lieu, et presser M au milieu du combat contre l'Herbe a Pinces
 * doit montrer l'Herbe a Pinces. */

/* Un enregistrement de clairiere : trois octets, adresses sans multiplier --
 * le 6502 n'en a pas, et `3 * i` appelait tosmulax a chaque acces. */
#define map_rec(i)  (map_data + MAP_HEAD + (i) + (i) + (i))
#define map_cell(i) (map_rec(i)[0])   /* x | (y << 3) */
#define map_num(i)  (map_rec(i)[1])   /* numero du livre, 0 si anonyme */
#define map_out(i)  (map_rec(i)[2])   /* masque des sorties */
/* 13 * i, en decalages : le nom d'une clairiere dans le bloc de langue. */
#define map_name(i) ((char*)(map_data + MAP_POOL + \
                             (((unsigned)(i)) << 3) + (((unsigned)(i)) << 2) + (i)))

/* Colonne et ligne d'ecran d'une case de la grille. Quinze octets de RODATA
 * qui remplacent deux multiplications par acces. */
static const unsigned char kMapCol[6] = { 2, 8, 14, 20, 26, 32 };
static const unsigned char kMapRow[9] = { 2, 4, 6, 8, 10, 12, 14, 16, 18 };
/* N, S, E, O : le pas d'un sentier, et l'ecart du premier caractere au coin
 * haut-gauche de la case. Le pas vertical sert aussi d'ecart vertical. */
static const signed char kMapDC[4] = { 0, 0,  1, -1 };
static const signed char kMapD[4]  = { -1, 1, 0,  0 };
static const signed char kMapSC[4] = { 1, 1,  3, -1 };

/* Ces quatre-la ne touchent jamais au disque : elles peuvent vivre en
 * $D400, dans la banque deux de la Language Card, avec le reste du code
 * froid. Seul map_load(), qui ouvre un fichier, reste en memoire principale
 * -- ProDOS se sert de la Language Card pendant un open ou un read. */
#pragma code-name (push, "LC")
static char* map_str(unsigned char k)
{
    char* p = (char*)(map_data + MAP_POOL + MAP_NAMEW * MAP_CLR);   /* 455 */
    while (k--) { while (*p) ++p; ++p; }
    return p;
}

#pragma code-name (pop)

/* Trois lectures d'affilee, sans jamais deplacer le curseur : l'en-tete et
 * les clairieres, la table des pages, puis le bloc francais -- que le bloc
 * anglais vient recouvrir a la meme adresse si la partie est en anglais. */
static unsigned char map_load(void)
{
    FILE* f;
    unsigned int n;

    map_ready = 0;
    if (chdir("/SCOSWAMP") != 0) return 0;
    f = fopen("MAP", "rb");
    if (f == NULL) return 0;
    if (fread(map_data, 1, MAP_POOL, f) == MAP_POOL &&
        memcmp(map_data, "MAP\3", 4) == 0 &&
        map_data[4] == MAP_CLR && map_data[5] == MAP_PAGES &&
        map_data[6] == MAP_NAMEW &&
        fread(map_pages, 1, sizeof map_pages, f) == sizeof map_pages) {
        n = load_u16(map_data + 16);
        if (n <= sizeof map_data - MAP_POOL &&
            fread(map_data + MAP_POOL, 1, n, f) == n) {
            n = load_u16(map_data + 18);
            if (is_fr()) map_ready = 1;
            else if (n <= sizeof map_data - MAP_POOL)
                map_ready = (fread(map_data + MAP_POOL, 1, n, f) == n);
        }
    }
    fclose(f);
    return map_ready;
}

/* La clairiere d'une page, MAP_NONE si la page n'est d'aucun lieu. */
static unsigned char map_of_page(unsigned int page)
{
    unsigned char i;
    unsigned int p = 0;
    const unsigned char* t = map_pages;

    for (i = MAP_PAGES; i; --i) {
        p += *t++;
        if (p >= page) return (p == page) ? *t : MAP_NONE;
        ++t;
    }
    return MAP_NONE;
}

/* Le brouillard de guerre, deduit du seul bitmap des pages visitees : une
 * clairiere est vue des qu'UNE de ses pages l'est, quelle que soit la porte
 * par laquelle on y est entre -- c'est le meme rabattement que les lignes V
 * du corpus font page par page. */
static void map_seen(void)
{
    unsigned char i;
    unsigned int p = 0;
    const unsigned char* t = map_pages;

    memset(map_vu, 0, sizeof map_vu);
    for (i = MAP_PAGES; i; --i) {
        p += *t++;
        if (scene_visited(p)) map_vu[*t] = 1;
        ++t;
    }
}

/* map_voisin est la plus grosse des lectures de la carte et la plus froide :
 * elle ne sert qu'a dessiner. Elle part en $D400 ; map_of_page et map_seen,
 * lues a chaque page, restent en memoire principale faute de place dans la
 * banque -- il n'y restait que 428 octets.
 *
 * La premiere clairiere rencontree dans cette direction, MAP_NONE s'il n'y en
 * a pas. Sur les 39 sentiers, trois font deux cases : cette recherche les
 * suit sans qu'aucune table ne les nomme. */
#pragma code-name (push, "LC")
static unsigned char map_voisin(unsigned char i, unsigned char d)
{
    static const signed char kDX[4] = {  0, 0, 1, -1 };  /* N S E O */
    static const signed char kDY[4] = { -1, 1, 0,  0 };
    const unsigned char* r;
    signed char x = (signed char)(map_cell(i) & 7);
    signed char y = (signed char)(map_cell(i) >> 3);
    unsigned char j, cell;

    for (;;) {
        x = (signed char)(x + kDX[d]);
        y = (signed char)(y + kDY[d]);
        if (x < 0 || x > 5 || y < 0 || y > 8) return MAP_NONE;
        cell = (unsigned char)(x | (y << 3));
        r = map_data + MAP_HEAD;
        for (j = 0; j < MAP_CLR; j++) { if (*r == cell) return j; r += 3; }
    }
}

#pragma code-name (pop)

/* L'ecran efface ligne par ligne, et non par clrscr().
 *
 * Ouverte depuis le mode mixte -- c'est-a-dire en plein combat -- la carte ne
 * s'effacait qu'a moitie : l'ancienne page restait dans une colonne sur deux.
 * clrscr() passe par HOME du firmware, qui n'atteint la banque auxiliaire de
 * l'ecran 80 colonnes que si l'entree en graphique n'a pas derange ses
 * commutateurs. cclearxy emprunte le meme chemin que cputc, et celui-la ecrit
 * bien dans les deux banques : la preuve etait sous les yeux, la carte se
 * dessinait juste, seul le fond restait sale.
 * 79 colonnes et non 80 : ecrire la derniere cellule de l'ecran ferait
 * scroller, et le corpus ne depasse de toute facon jamais 78 colonnes.
 *
 * Elle a remplace clrscr() dans TOUS les ecrans du jeu, pas seulement dans la
 * carte : le meme fond sale se voyait, depuis toujours, en revenant au texte
 * apres un combat -- une page repeinte gardait la precedente dans une colonne
 * sur deux. C'etait invisible tant que rien n'occupait 80 colonnes ; la ligne
 * de lieu et la carte l'ont mis en pleine lumiere. */
static void wipe(void)
{
    unsigned char r;

    for (r = 0; r <= CHOICE_ROWN; r++) cclearxy(0, r, 79);
    gotoxy(0, 0);   /* comme clrscr, dont elle prend la place partout */
}

/* Un segment de sentier : `n` caracteres depuis (col,row), en avançant de
 * (dc,dr). Le dernier devient '?' quand la clairiere d'arrivee est encore
 * inconnue -- c'est le « rayon termine par ? » que le plan-modele du livre
 * met au bout de chaque sentier repere mais pas encore emprunte. Les quatre
 * directions passent par ici : ecrites separement, elles coutaient deux fois
 * ce code. */
static void map_trait(unsigned char c, unsigned char r, signed char dc,
                      signed char dr, unsigned char n, unsigned char connu)
{
    char g = dc ? '-' : '|';

    while (n--) {
        gotoxy(c, r);
        cputc((n || connu) ? g : '?');
        c = (unsigned char)(c + dc);
        r = (unsigned char)(r + dr);
    }
}

/* La ligne de lieu, ecrite en video inverse au bas de la zone graphique,
 * juste avant les quatre lignes que le mode mixte laisse visibles. Elle
 * repond a la question que le livre pose a chaque page -- ou suis-je, et par
 * ou puis-je partir -- sans se melanger ni au recit ni aux choix.
 * Quand la page n'est d'aucun lieu, la clairiere collante s'affiche entre
 * parentheses : c'est un souvenir, pas une position. */
static void render_place(void)
{
    const char* help;
    unsigned char help_col;
    /* Peindre d'abord toute la ligne en inverse : sinon un nom court laisse
     * des cellules normales et le bandeau semble decoupe. */
    revers(1);
    gotoxy(0, PLACE_ROW);
    pad_to(79);
    if (map_ready && map_here != MAP_NONE) {
        gotoxy(1, PLACE_ROW);
        if (map_of_page((unsigned int)app.current_scene) != map_here) {
            cfmt("(%s)", map_name(map_here));
        } else {
            map_seen();
            cfmt("%s   %s", map_name(map_here), map_str(MS_LIEU));
        }
    }
    if (app.hero_ready) {
        help = is_fr() ? "I:SAC M:CARTE H:AIDE Q:QUITTER"
                       : "I:BAG M:MAP H:HELP Q:QUIT";
        /* La colonne 79 est reservee au firmware : ecrire dessus peut
         * provoquer un retour automatique sur la ligne suivante. */
        help_col = (unsigned char)(79 - strlen(help));
        gotoxy(help_col, PLACE_ROW);
        cputs(help);
    }
    revers(0);
}

static void render_scene(void)
{
    unsigned char i, row;

    /* conio needs 80STORE for both text banks, even behind full DHGR. */
    *(volatile unsigned char*)0xC001 = 0;
    wipe();
    render_title_bar();
    row = BODY_ROW0;
    for (i = 0; i < body_count; i++) {
        cputsxy(0, row + i, body_lines[i]);
    }
    render_place();
    render_choices();
    if (app.video_mode == 1) *(volatile unsigned char*)0xC000 = 0;
}

/* ── Lecture d'une page de scene ──────────────────────────────────────── */

/* Avance sur les chiffres puis sur les espaces, et rend la valeur lue. */
#pragma code-name (push, "LC")
static char* take_uint(char* t, unsigned int* out)
{
    unsigned int v = 0;
    while (*t >= '0' && *t <= '9') { v = v * 10u + (unsigned int)(*t - '0'); t++; }
    while (*t == ' ') t++;
    *out = v;
    return t;
}

/* La meme chose, signe compris : les effets d'une ligne CE sont negatifs. */
static char* take_int(char* t, int* out)
{
    unsigned int v;
    int neg = 0;
    if (*t == '-') { neg = 1; t++; } else if (*t == '+') t++;
    t = take_uint(t, &v);
    *out = neg ? -(int)v : (int)v;
    return t;
}

/* Avance sur un mot, le termine par '\0', et rend le debut du suivant. */
static char* take_word(char* t, char** word)
{
    *word = t;
    while (*t && *t != ' ') t++;
    if (*t == ' ') { *t = '\0'; t++; while (*t == ' ') t++; }
    return t;
}

/* Les quatre mots que E, E0, CE et ED acceptent, lus une seule fois.
 * Quatre branches repetaient la meme table de strcmp ; ED en aurait fait une
 * cinquieme, et sur cette machine neuf comparaisons de chaines valent un
 * ecran de texte. Rend 4 si le mot n'est pas reconnu.
 * Les mots restent en francais dans les deux corpus, comme les lignes E/E0/CE
 * existantes : c'est de la mecanique, pas du texte affiche. */
#pragma code-name (push, "CODE")
static unsigned char carac_of(const char* w)
{
    /* L'INITIALE suffit : ENDURANCE, HABILETE, CHANCE et OR sont les quatre
     * seuls mots que le format admet, et leurs premieres lettres different
     * deux a deux. Quatre strcmp coutaient les quatre chaines en RODATA plus
     * leur boucle, pour distinguer ce qu'un octet distingue. La contrepartie
     * est qu'une faute de frappe passe -- "EDURANCE" serait lue comme
     * ENDURANCE -- et c'est reflow_txt.py qui la refuse, du cote ou l'on peut
     * se payer une verification. */
    switch (*w) {
    case 'B': return 4;
    case 'E': return 0;
    case 'H': return 1;
    case 'C': return 2;
    case 'O': return 3;
    }
    return 4;
}
#pragma code-name (pop)
#pragma code-name (pop)

/* L'effet, applique par la seule porte qui connaisse les regles de bornes :
 * plafond au total de depart pour les trois caracteristiques, plancher zero
 * pour les quatre. */
static void carac_apply(unsigned char c, int d)
{
    switch (c) {
    case 0: character_adjust_end(&app.hero, d);  break;
    case 1: character_adjust_hab(&app.hero, d);  break;
    case 2: character_adjust_cha(&app.hero, d);  break;
    case 3: character_adjust_gold(&app.hero, d); break;
    case 4:
        app.hero.weapon_bonus += (unsigned char)d;
        if (app.hero.weapon_bonus > 2) app.hero.weapon_bonus=2;
        break;
    }
}

/* Ajoute un choix a la page. Quatre directives fabriquaient chacune le leur
 * a la main : le meme bloc de 120 octets, quatre fois. */
static void push_choice(int scene, unsigned char grant, unsigned char require,
                        const char* title)
{
    Choice* c;
    if (app.num_choices >= MAX_CHOICES) return;
    c = &app.choices[app.num_choices++];
    c->scene_id = scene;
    c->grant    = grant;
    c->require  = require;
    c->object   = OBJ_COUNT;
    c->obj_mode = 0;
    c->title = (char*)title;
}

static void push_object_choice(int scene, Object o, unsigned char mode,
                               const char* title)
{
    Choice* c;
    push_choice(scene, STONE_COUNT, STONE_COUNT, title);
    if (app.num_choices == 0) return;
    c = &app.choices[app.num_choices - 1];
    c->object = (unsigned char)o; c->obj_mode = mode;
}

static void lose_items(unsigned char n)
{
    unsigned char i;
    unsigned int bits;
    while (n) {
        for (i = 0; i < STONE_COUNT && !app.hero.stones[i]; ++i) {}
        if (i < STONE_COUNT) { --app.hero.stones[i]; --n; continue; }
        /* Seuls les objets visibles peuvent etre voles, l'Anneau de Cuivre
         * (bit 0) excepte : il est la boussole de Stratagus et le recit ne le
         * reprend qu'a la page 049. Les bits a partir d'OBJ_HIDDEN0 sont des
         * faits narratifs caches, pas des biens poses dans le sac. Le masque
         * se calcule -- bits 1 a OBJ_HIDDEN0-1 -- pour qu'un objet ajoute a
         * l'enum devienne volable sans qu'on ait a y repenser ; c'est une
         * constante, le compilateur la plie. */

        bits = app.hero.objects & STEALABLE;
        if (bits) {
            bits &= bits - 1;
            app.hero.objects = (app.hero.objects & ~STEALABLE) | bits;
            --n; continue;
        }
        if (app.hero.amulets) {
            app.hero.amulets &= (unsigned char)(app.hero.amulets - 1);
            --n; continue;
        }
        break;
    }
}

/* Les directives, dans l'ordre qui FAIT FOI : les prefixes de deux lettres
 * passent devant la lettre seule, sinon `M ` avalerait `MV` et `E ` avalerait
 * `ED`. Quatre octets par ligne : les deux lettres, le troisieme caractere
 * exige (' ' un espace, '.' la fin de ligne, '*' n'importe lequel), puis '1'
 * si la directive est un EFFET D'ENTREE -- gain, perte, jet, Pierre, detour --
 * que la reprise d'un instantane ne doit pas rejouer.
 *
 * Cette table remplace une cascade de vingt-neuf `if (c0 == 'X' && c1 == 'Y'
 * && c2 == ' ')` et le pave de douze comparaisons du garde `restoring`. Les
 * regles n'ont pas bouge d'un iota : c'est la meme liste, dans le meme ordre,
 * lue par une boucle au lieu d'etre depliee en code. */
static const char kOps[] =
    "AC.0GX 1GA 1G *1CI 0CN 0CG 0CB 0CT 0CA 0CV 0CX 0GU 0PD.1PO.1PS.1PX.1TR.1"
    "MM 0MF 0MR 1MD 0MS 0MI 0MU 0MV 0MB 0M *0E0 1CE 1ED 1EH.1E *1"
    "PC 1P *1CL 0CU 0CP 0VR 1V *1CS 0DV 0CF 0T *0C *0";

enum { D_AC, D_GX, D_GA, D_G, D_CI, D_CN, D_CG, D_CB, D_CT, D_CA, D_CV, D_CX, D_GU, D_PD, D_PO, D_PS, D_PX, D_TR,
       D_MM, D_MF, D_MR, D_MD, D_MS, D_MI, D_MU, D_MV, D_MB, D_M, D_E0, D_CE, D_ED, D_EH, D_E,
       D_PC, D_P, D_CL, D_CU, D_CP, D_VR, D_V, D_CS, D_DV, D_CF, D_T, D_C,
       D_TEXTE };

/* audit_contracts.py verifie la correspondance de kOps avec cette enum et
 * avec le descripteur JavaScript, y compris les effets d'entree. */

/* Classe une ligne du fichier. Le format d'une page :
 *
 *   T  <id> <titre>             titre, en video inverse ligne 1
 *   VR <cible> <page> ...        detour si une issue explicite a ete visitee
 *   V  <id> [<page> ...]        "si vous y etes deja venu, rendez-vous au
 *                               <id>" -- doit preceder tout le reste de la
 *                               page, qu'un detour annule. Les numeros qui
 *                               suivent sont les AUTRES pages de la meme
 *                               clairiere (page-hub, variantes de recit) :
 *                               le detour se declenche si l'une d'elles, ou
 *                               <id>, ou la page courante, a deja ete vue.
 *                               Sans elles, entrer par un autre sentier
 *                               rejouait la premiere visite
 *   M  <hab> <end> <nom>        la creature de la clairiere (Batailles)
 *   MD <n>                      ses coups coutent n ENDURANCE (defaut 2)
 *   MF <n>                     fuite permise apres n assauts resolus (defaut 0)
 *   MR <gain> <maximum>        recupere la creature vivante memorisee du lieu
 *   MS <n>                      le combat cesse a n ENDURANCE (defaut 0)
 *   MB <ok> <ko>                duel au premier sang : la premiere blessure
 *                               arrete le combat, <ok> si vous touchez,
 *                               <ko> si c'est vous qui etes touche
 *   CS <STAT> <ok> <ko>         "Lancez deux des" contre la caracteristique
 *                               nommee, gratuit (pas de point de CHANCE)
 *   DV <max> <id>               en cascade : premiere ligne dont la perte du
 *                               dernier combat est <= max fabrique l'unique
 *                               choix "continuer" vers <id>
 *   MI <page>                   l'image de bataille du dernier adversaire
 *                               declare est celle d'une AUTRE page : le disque
 *                               n'en range qu'une par page (B<page>.RLE) et
 *                               une file peut melanger les especes. Page 120,
 *                               les deux Loups empruntent le B224 du combat
 *                               contre les Loups seuls, et le Maitre garde le
 *                               B120 de sa page. Sans MI, ou si l'emprunt
 *                               manque au disque, c'est l'image de la page
 *   MU <NOM>.MB                 dans le Marais, musique lue uniquement lors
 *                               de l'entree dans une nouvelle clairiere ;
 *                               hors clairieres, morceau scenarise de la page
 *                               (accueil, village, prologue, fin). Toujours
 *                               joue une fois sans boucle ; MU - fait silence
 *   MV <id>                     apres le dernier adversaire tombe, la page
 *                               envoie en <id> sans repasser par les choix.
 *                               Le jumeau de CF cote victoire : elle remplace
 *                               le choix de garde que le joueur devait
 *                               prendre lui-meme, et rend la ligne d'ecran
 *                               qu'il mangeait sur les 4 disponibles
 *   E  <CARAC> <delta>          effet a l'entree : E ENDURANCE -2
 *   E0 <CARAC> <delta>          variation du TOTAL DE DEPART, valeur courante
 *                               comprise. En perte elle est definitive :
 *                               E0 HABILETE -2 (page 87). En gain elle releve
 *                               le plafond : E0 CHANCE +2, la benediction de
 *                               Grognard (page 155)
 *   ED <CARAC> <+-ndes>         jet de des VISIBLE : `ED ENDURANCE -1` =
 *                               "lancez un de et perdez autant de points
 *                               d'ENDURANCE" ; `ED OR +1` = un de de Pieces
 *                               d'Or. Le signe dit gain ou perte, la valeur
 *                               absolue le nombre de des (1 ou 2). Le jet est
 *                               DIFFERE, contrairement a CE : la ligne remplit
 *                               seulement dice_n / dice_carac, et load_scene
 *                               le joue une fois la page AFFICHEE -- sinon le
 *                               joueur ne verrait rien. Donc la position de la
 *                               ligne dans le fichier n'ordonne rien : le jet
 *                               tombe toujours avant le combat de la page
 *   CE <CARAC> <dok> <dko>      "Tentez votre Chance" sans branchement : il
 *                               decide d'un effet, la page continue
 *   P  <PIERRE> <n>             le sorcier vous donne n Pierres Magiques
 *   PC <n> <cats>               il vous en laisse choisir n parmi les
 *                               categories citees (N neutre, B benefique,
 *                               M malefique)
 *   PD / PO / PX                 retire deux objets, un objet, ou tout le sac
 *   TR                           echange jusqu'a trois objets/amulettes contre
 *                               autant de Pierres neutres a choisir
 *   CL <ok> <ko> [<dok> <dko>]  "Tentez votre Chance" : la page envoie en
 *                               <ok> si Chanceux, en <ko> sinon, avec un
 *                               effet d'ENDURANCE optionnel sur chaque
 *                               branche -- le livre en pose deux ("si vous
 *                               etes Chanceux, vous perdez 2 points
 *                               d'ENDURANCE et vous vous rendez au 270")
 *   CP <PIERRE> <id> <titre>    choix qui remet une Pierre Magique
 *   CU <PIERRE> <id> <titre>    choix qui EXIGE et consomme une Pierre
 *   G/GX/GA <OBJET>              donne/retire un objet, ou remet les amulettes
 *   CI/CN/GU <OBJET> <id> ...   possede/ne possede pas/possede et consomme
 *   C  <id> <titre>             choix
 *   CF <id> <titre>             Fuite -- "n'est possible que si elle est
 *                               specifiee a la page ou vous vous trouverez"
 *   <reste>                     le texte de la scene
 */
static void classify_line(char* l)
{
    char* t;
    char* word;
    unsigned int a, b;
    const char* k;
    unsigned char op;
    /* Les trois premieres lettres, lues une fois. Chaque `l[1] == 'X'` sur le
     * pointeur coutait un rechargement indirect (ldy/lda (ptr),y) ; sur trois
     * octets statiques c'est un `lda` absolu. */
    unsigned char c0 = (unsigned char)l[0];
    unsigned char c1 = (unsigned char)l[1];
    unsigned char c2 = (unsigned char)l[2];

    k = kOps;
    for (op = 0; op < D_TEXTE; ++op, k += 4)
        if (k[0] == (char)c0 && k[1] == (char)c1 &&
            (k[2] == '*' || (k[2] == '.' ? c2 == '\0' : c2 == ' '))) break;

    /* V saute le recit et ses effets, mais conserve le theme du lieu :
     * certaines pages courtes n'ont aucune ligne MU. */
    if (app.revisit >= 0 && op != D_MU) return;

    /* L'instantane contient deja les effets d'entree de la scene reprise. */
    if (op < D_TEXTE && restoring && k[3] == '1') return;

    switch (op) {
    case D_GX:
        take_word(l + 3, &word);
        character_take_object(&app.hero, object_from_name(word));
        break;

    case D_GA:
        take_uint(l + 3, &a);
        character_trade_amulets(&app.hero, a);
        break;

    case D_G: {
        unsigned char am; /* object/amulet indices and sentinels fit in a byte */
        take_word(l + 2, &word);
        am = amulet_from_name(word);
        if (am != AMULET_COUNT) character_give_amulet(&app.hero, am);
        else {
            am = object_from_name(word);
            /* G replaces the weapon; its following E BONUS defines this blade. */
            if (am == OBJ_EPEMAGIQUE) app.hero.weapon_bonus = 0;
            character_give_object(&app.hero, am);
        }
        break;
    }

    case D_CI:
    case D_CN: {
        Object o;
        Amulet am;
        unsigned char mode = (op == D_CI) ? 1 : 2;
        t = take_word(l + 3, &word); o = object_from_name(word);
        t = take_uint(t, &a);
        am = amulet_from_name(word);
        if (am != AMULET_COUNT) push_object_choice((int)a, (Object)(0x80 | am), mode, t);
        else if (o != OBJ_COUNT) push_object_choice((int)a, o, mode, t);
        break;
    }

    case D_CB:
    case D_CG:
        t = take_uint(l + 3, &b); t = take_uint(t, &a);
        push_object_choice((int)a, (Object)(op == D_CB ? 0x7c : 0x7d), (unsigned char)b, t);
        break;

    case D_CT:
    case D_CA: {
        unsigned int lo, hi;
        t = take_uint(l + 3, &lo); t = take_uint(t, &hi); t = take_uint(t, &a);
        push_object_choice((int)a, (Object)(op == D_CT ? 0x7e : 0x7f),
                           (unsigned char)((lo << 4) | hi), t);
        break;
    }

    case D_GU: {
        Object o;
        t = take_word(l + 3, &word); o = object_from_name(word);
        t = take_uint(t, &a);
        if (o != OBJ_COUNT) push_object_choice((int)a, o, 3, t);
        break;
    }

    /* CV <page deja visitee> <destination> <titre>. Le bitmap sauvegarde
     * fait foi, y compris pour les anciennes parties : aucun second drapeau
     * de quete a maintenir. L'historique reste fixe pendant cette page. */
    case D_AC:
        app.revisit = -2; /* automatic history choices on this page */
        break;

    case D_CV:
    case D_CX:
        /* Une liste est une conjonction ; ! exige une page non visitee.
         * CX inverse le resultat complet. Le choix reste du meme format. */
        t = l + 3;
        b = 1;
        for (;;) {
            c0 = (*t == '!');
            if (c0) ++t;
            t = take_uint(t, &a);
            if (!!scene_visited(a) == c0) b = 0;
            if (*t != ',') break;
            ++t;
        }
        c0 = (b == (op == D_CV));
        t = take_uint(t, &b);
        if (app.revisit == -2 && c0) {
            app.revisit = (int)b;
            break;
        }
        push_choice((int)b, STONE_COUNT, c0 ? STONE_COUNT : 255, t);
        break;

    case D_PD:
    case D_PO:
        lose_items((unsigned char)(op == D_PD ? 2 : 1));
        break;

    case D_PX:
        /* Perdre son sac ne fait pas oublier sa mission ou ses decouvertes. */
        app.hero.objects &= ~((1u << OBJ_HIDDEN0) - 1u);
        app.hero.amulets = 0;
        /* puis les Pierres, comme PS */

    case D_PS: /* remettre toutes les Pierres, en conservant les objets */
        memset(app.hero.stones, 0, sizeof app.hero.stones);
        break;

    case D_TR: {
        unsigned int bits = app.hero.objects & GAME_TRADE_OBJECT_MASK;
        a = 0;
        while (bits && a < GAME_TRADE_LIMIT) { bits &= bits - 1; ++a; }
        app.hero.objects = (app.hero.objects & ~GAME_TRADE_OBJECT_MASK) | bits;
#if GAME_TRADE_AMULETS
        while (app.hero.amulets && a < GAME_TRADE_LIMIT) {
            app.hero.amulets &= (unsigned char)(app.hero.amulets - 1); ++a;
        }
#endif
        app.choose_n = (unsigned char)a;
        app.choose_cats[0] = GAME_TRADE_CATEGORY_0;
        app.choose_cats[1] = GAME_TRADE_CATEGORY_1;
#if GAME_TRADE_CATEGORY_1
        app.choose_cats[2] = '\0';
#endif
        break;
    }

    /* MD, MS et MI qualifient le dernier adversaire declare. */
    case D_MM:
        take_uint(l + 3, &a);
        magic_forbidden = (a != 0);
        break;

    case D_MF:
        take_uint(l + 3, &a);
        flee_after = (unsigned char)a;
        break;

    case D_MR:
        t = take_uint(l + 3, &a);
        take_uint(t, &b);
        monster_recover(monster_zone_key(), (unsigned char)a, (unsigned char)b);
        break;

    case D_MD:
        if (app.foe_count) {
            take_uint(l + 3, &a);
            app.foes[app.foe_count - 1].damage = (unsigned char)a;
        }
        break;

    case D_MS:
        if (app.foe_count) {
            take_uint(l + 3, &a);
            app.foes[app.foe_count - 1].stop_at = (unsigned char)a;
        }
        break;

    /* MI <page> : l'illustration de bataille de CETTE creature-la est celle
     * d'une autre page. Le disque ne porte qu'un B<page>.RLE par page, et la
     * file du 120 comptait trois adversaires pour une seule image. */
    case D_MI:
        if (app.foe_count) take_uint(l + 3, app.foe_img + (app.foe_count - 1));
        break;

    /* La musique de la page : "MU NOM.MB" est le theme de la zone,
     * "MU +NOM.MB" une surcouche pour cette page seule, "MU -" le silence.
     * Voir music.h et music_for_page. */
    case D_MU:
        t = l + 3;
        if (*t == '+') { app.music_over = 1; t++; }
        strncpy(app.music_name, t, sizeof(app.music_name) - 1);
        app.music_name[sizeof(app.music_name) - 1] = '\0';
        break;

    case D_MV:
        take_uint(l + 3, &a);
        app.win_scene = (int)a;
        break;

    /* MB <si-vous-touchez> <si-touche> : duel au premier sang. */
    case D_MB:
        t = take_uint(l + 3, &a);
        app.mb_ok = (int)a;
        take_uint(t, &b);
        app.mb_ko = (int)b;
        break;

    /* Chaque ligne M ajoute un adversaire a la file, dans l'ordre de la
     * page -- c'est l'ordre dans lequel le livre les fait venir. */
    case D_M:
        if (app.foe_count < MAX_FOES) {
            Monster* f = &app.foes[app.foe_count];
            monster_init(f);
            t = take_uint(l + 2, &a);
            t = take_uint(t, &b);
            f->hab = (unsigned char)a;
            f->end = (unsigned char)b;
            strncpy(f->name, t, sizeof(f->name) - 1);
            f->name[sizeof(f->name) - 1] = '\0';
            /* Par defaut l'image de la page ; une ligne MI qui suit corrige.
             * C'est ici la remise a zero du tableau, load_scene n'en fait pas. */
            app.foe_img[app.foe_count] = 0;
            app.foe_count++;
        }
        break;

    /* Variation du total de depart : perte definitive (page 87) ou
     * benediction qui releve le plafond (page 155). Ce n'est pas carac_apply
     * -- celle-ci deplace le PLAFOND -- mais la meme numerotation, que
     * rules.c connait. */
    case D_E0:
        t = take_word(l + 3, &word);
        character_shift0(&app.hero, carac_of(word), atoi(t));
        break;

    /* "Tentez votre Chance" qui ne branche pas : il decide seulement d'un
     * effet, et la page continue de se lire. Le livre le fait souvent --
     * "si vous etes Malchanceux, vous tombez et perdez 2 points
     * d'ENDURANCE, mais vous parvenez tout de meme a grimper". */
    case D_CE:
        t = take_word(l + 3, &word);
        app.dice_carac = carac_of(word);
        t = take_int(t, &app.luck_dok);
        take_int(t, &app.luck_dko);
        app.dice_n = 3; /* deferred Luck effect, sharing the visible dice path */
        break;

    case D_ED:
        t = take_word(l + 3, &word);
        app.dice_carac = carac_of(word);
        /* atoi et pas take_uint : ici le signe porte le sens de la ligne.
         * Aucun bornage ici -- deux comparaisons 16 bits signees coutaient 55
         * octets pour un cas qui ne se presente pas. C'est run_dice_roll qui
         * tient la regle "deux des au plus", et il la tient quoi qu'ecrive la
         * page. */
        if (app.dice_carac < 4) app.dice_n = (signed char)atoi(t);
        if (app.dice_n > 2) app.dice_n = 2; /* 3 is internal CE, never ED */
        break;

    case D_E:
        t = take_word(l + 2, &word);
        /* L'or passe par character_adjust_gold comme le reste : un
         * `gold += delta` sur un champ non signe donnait 65535 Pieces d'Or au
         * heros sans le sou qui en depense une. */
        carac_apply(carac_of(word), atoi(t));
        break;

    case D_EH: /* Faiblesse : ENDURANCE restante divisee par deux, entier bas. */
        app.hero.end >>= 1;
        break;

    case D_PC:
        t = take_uint(l + 3, &a);
        app.choose_n = (unsigned char)a;
        strncpy(app.choose_cats, t, sizeof(app.choose_cats) - 1);
        app.choose_cats[sizeof(app.choose_cats) - 1] = '\0';
        break;

    case D_P: {
        Stone s;
        t = take_word(l + 2, &word);
        s = stone_from_name(word);
        if (s != STONE_COUNT) {
            unsigned int n = 1;
            if (*t) take_uint(t, &n);
            character_give_stone(&app.hero, s, (unsigned char)n);
        }
        break;
    }

    case D_CL:
        t = take_uint(l + 3, &a);
        app.luck_ok = (int)a;
        t = take_uint(t, &a);
        app.luck_ko = (int)a;
        /* Les deux deltas sont optionnels et peuvent etre negatifs : atoi
         * plutot que take_uint, qui ne lit pas le signe. */
        if (*t) {
            app.luck_dok = atoi(t);
            while (*t && *t != ' ') t++;
            while (*t == ' ') t++;
            app.luck_dko = atoi(t);
        }
        break;

    case D_CU:
    case D_CP: {
        Stone st;
        t = take_word(l + 3, &word);
        st = stone_from_name(word);
        t = take_uint(t, &a);
        if (st != STONE_COUNT) {
            if (op == D_CU)
                push_choice((int)a, (unsigned char)STONE_COUNT, (unsigned char)st, t);
            else
                push_choice((int)a, (unsigned char)st, (unsigned char)STONE_COUNT, t);
        }
        break;
    }

    /* "Si vous y etes deja venu, rendez-vous au 142. Sinon, lisez ce qui
     * suit." Le detour decide, plus rien de la page ne doit jouer : ni
     * son texte, ni ses choix, ni surtout ses lignes E et P, qui
     * donneraient une seconde fois ce qu'on a deja pris. D'ou le garde
     * en tete de fonction -- et l'invariant, verifie par reflow_txt.py,
     * que la ligne V precede tout le reste.
     *
     * Le livre dit "si vous Y etes deja venu" -- dans la CLAIRIERE, pas
     * sur cette page. Or une clairiere en occupe plusieurs : la page
     * d'arrivee, la page-hub qui porte les sentiers, la page de revisite
     * ou l'on entre parfois directement depuis le voisin. Le bitmap est
     * indexe sur la page, donc revenir par une autre porte rejouait la
     * premiere visite -- creature ressuscitee, objets redonnes. D'ou la
     * liste : on teste la page courante, la cible, puis chaque page
     * citee, et le premier drapeau leve suffit. */
    /* V adds current/target visits; VR tests only explicit outcome pages.
     * Reading the list and applying the redirect is common to both. */
    case D_V:
    case D_VR:
        t = l + 2;
        if (op == D_VR) ++t;
        t = take_uint(t, &a);
        if (op == D_V && (scene_visited((unsigned int)app.current_scene) ||
                         scene_visited(a))) goto revisit_found;
        while (*t) {
            t = take_uint(t, &b);
            if (scene_visited(b)) goto revisit_found;
        }
        return;
revisit_found:
        app.revisit = (int)a;
        break;

    /* CS <STAT> <ok> <ko> : le jet est joue par load_scene, comme un jet
     * de Chance, mais contre la caracteristique nommee et gratuit. */
    case D_CS:
        t = take_word(l + 3, &word);
        app.cs_carac = carac_of(word);
        t = take_uint(t, &a);
        app.cs_ok = (int)a;
        take_uint(t, &b);
        app.cs_ko = (int)b;
        break;

    /* DV <max> <id>, en cascade : la premiere ligne dont la perte du
     * dernier combat ne depasse pas <max> fabrique l'unique choix de la
     * page -- "continuer" -- vers sa cible. Le moteur repond ainsi a
     * "Evaluez vos blessures" a la place du joueur. */
    case D_DV:
        t = take_uint(l + 3, &a);
        t = take_uint(t, &b);
        if (!app.dv_done && app.last_loss <= (unsigned char)a) {
            app.dv_done = 1;
            push_choice((int)b, (unsigned char)STONE_COUNT,
                        (unsigned char)STONE_COUNT, msg(M_K_CONTINUER));
        }
        break;

    case D_CF:
        take_uint(l + 3, &a);
        app.flee_target = (int)a;
        break;

    case D_T:
        t = l + 2;
        while (*t >= '0' && *t <= '9') t++;
        while (*t == ' ') t++;
        scene_title = t;
        break;

    /* take_uint plutot que sscanf : sur cc65 le premier appel a scanf
     * fait entrer plusieurs kilo-octets d'analyseur de format dans le
     * binaire, pour lire trois chiffres. */
    case D_C:
        t = take_uint(l + 2, &a);
        if (t != l + 2 && *t != '\0')
            push_choice((int)a, (unsigned char)STONE_COUNT,
                        (unsigned char)STONE_COUNT, t);
        break;

    /* Pas de ligne vide en tete : le fichier en a une sous le titre, et
     * elle couterait la ligne de marge du budget de 19. */
    default:
        if (body_count < BODY_ROWS && (body_count > 0 || c0 != '\0'))
            body_lines[body_count++] = l;
        break;
    }
}

/* Fonction commune pour parser un fichier texte */
static unsigned char parse_text_file(int scene_id, unsigned char display_mode) {
    FILE* f;
    size_t bytes_read;
    char* p;
    char* q;
    char* end;
    unsigned char crlf;

    /* Build paths */
    if (build_paths(scene_id, app.language, app.imgPath, app.txtPath) != 0) {
        if (display_mode) oops("SCENE");
        return 0;
    }

    /* Réinitialiser la scène */
    app.num_choices = 0;
    body_count = 0;
    scene_title = NULL;

    /* Mode texte si on doit afficher */
    if (display_mode) {
        set_video_mode(0);
        videomode(VIDEOMODE_80COL);
        clrscr();
    }
    
    /* cc65/ProDOS rejects multi-component names in fopen on this runtime.
     * Navigate one component at a time, then open only the short basename. */
    if (!enter_asset_dir(is_fr() ? "TEXTFR" : "TEXTEN",
                         scene_id)) {
        if (display_mode) oops("TEXTE");
        return 0;
    }

    /* Open text file */
    f = fopen(app.txtPath, "r");
    if (!f) {
        if (display_mode) oops(app.txtPath);
        return 0;
    }
    
    /* Read file into buffer */
    bytes_read = fread(file_buffer, 1, sizeof(file_buffer) - 1, f);
    fclose(f);
    
    if (bytes_read == 0) {
        if (display_mode) oops("VIDE");
        return 0;
    }
    file_buffer[bytes_read] = '\0';

    /* Découper le buffer EN PLACE : chaque fin de ligne devient un '\0' et on
     * ne garde que des pointeurs. Plus de recopie ligne par ligne, donc plus
     * de tampon de 120 octets sur la pile ni de limite de longueur. */
    p = file_buffer;
    end = file_buffer + bytes_read;
    while (p < end) {
        q = p;
        while (q < end && *q != '\r' && *q != '\n') q++;
        crlf = (q + 1 < end && *q == '\r' && *(q + 1) == '\n');
        *q = '\0';
        classify_line(p);
        p = q + 1;
        if (crlf) p++;
    }

    if (display_mode && app.revisit < 0) {
        render_scene();
    }

    return 1;
}

/* Parser et afficher le fichier texte */
static void display_scene_text(int scene_id) {
    parse_text_file(scene_id, 1);  /* Mode display */
}

/* Cycle des modes video : texte 80 col -> DHGR plein -> DHGR mixte -> texte.
 *
 * Que des soft-switches. Le texte reste en $400-$7FF et l'image en
 * $2000-$3FFF pendant tout le cycle, donc aucune bascule ne relit le disque ni
 * ne repeint quoi que ce soit -- et aucune ne passe par un mode intermediaire.
 * L'ancienne version redessinait l'ecran depuis le fichier de scene a chaque
 * retour au texte : c'etait l'acces disque et le clignotement. */
static void cycle_video_mode(void) {
    if (!app.has_image) {
        return;  /* Pas d'image pour cette scene : le texte reste. */
    }
    app.video_mode = app.video_mode == 2 ? 0 : app.video_mode + 1;
    set_video_mode(app.video_mode);
}

/* ── Combat et sac a dos ──────────────────────────────────────────────────
 *
 * Tout se joue dans les 4 lignes du bas : en mode mixte, l'illustration de la
 * creature reste a l'ecran pendant l'echange d'assauts. Les regles elles-memes
 * sont dans rules.c, qui ne connait pas l'ecran ; ici il n'y a que de
 * l'affichage et le dialogue avec le joueur.
 */

/* Les invites qui reviennent, nommees une fois : cc65 ne fusionne pas les
 * litteraux identiques, chaque repetition coutait sa place en RODATA. */
static const char* msg_continue(void)
{ return msg(M_ESPACE_CONTINUER); }

/* Le nom de la barre d'espace, seul mot de l'invite qui ne vient pas du
 * catalogue : il est le meme dans les deux langues a une lettre pres. */
static const char* msg_space(void)
{ return is_fr() ? "ESPACE" : "SPACE"; }


/* Le bandeau de bataille : les deux adversaires face a face, chacun dans sa
 * moitie d'ecran, sous l'illustration. C'est la ligne qu'on lit entre deux
 * assauts, elle doit tenir en un coup d'oeil. */
/* Comble d'espaces jusqu'a la colonne demandee.
 *
 * C'est la moitie de la recette contre le clignotement : au lieu d'effacer une
 * ligne puis d'y ecrire -- deux passages, donc chaque cellule vue blanche
 * avant d'etre remplie -- on ecrit le texte puis on pousse des espaces jusqu'au
 * bord. Un seul passage, aucune cellule ne passe par le blanc. En 80 colonnes,
 * ou chaque caractere traverse la firmware, la difference se voit a l'oeil :
 * les 4 lignes du bas clignotaient a chaque coup porte. */
static void pad_to(unsigned char col)
{
    unsigned char x = wherex();
    while (x < col) { cputc(' '); x++; }
}

/* Efface une ligne du bandeau sans la faire clignoter. */
static void row_blank(unsigned char row)
{
    gotoxy(0, row);
    pad_to(79);
}

/* Une jauge de dix cases, en pleins et en creux : "[####------]" ou les
 * pleins sont des espaces en video inverse -- le seul pave plein dont
 * dispose la machine, et le seul qui se lise d'un metre. Le diese faisait
 * une trame grise ou l'on ne comptait rien.
 *
 * Ecrite a l'ecran et non dans un tampon : le pave plein n'est pas un
 * caractere mais un MODE, il ne se range pas dans une chaine.
 *
 * Les chiffres restent -- le livre compte en points -- mais c'est la barre qui
 * dit d'un coup d'oeil qui est en train de mourir. Arrondi vers le HAUT : tant
 * qu'il reste un point d'ENDURANCE, il reste une case, sinon la creature
 * paraitrait morte un assaut trop tot. */
static void put_gauge(unsigned char v, unsigned char v0)
{
    unsigned char i, n;
    n = (v0 == 0 || v == 0)
        ? 0
        : (unsigned char)(((unsigned int)v * 10u + v0 - 1u) / v0);
    if (n > 10) n = 10;
    cputc('[');
    revers(1);
    for (i = 0; i < n; i++) cputc(' ');
    revers(0);
    for (; i < 10; i++) cputc('-');
    cputc(']');
}

/* La touche seule, en video inverse comme la barre de titre. Entre crochets,
 * l'oeil devait chercher ; en inverse il accroche. Separee de put_key parce
 * que l'invite de Chance ecrit son enjeu a la main derriere le C. */
static void put_tag(const char* key)
{
    revers(1); cfmt(" %s ", key); revers(0);
}

/* Une touche et son verbe. */
static void put_key(const char* key, const char* label)
{
    put_tag(key);
    cfmt(" %s   ", label);
}

/* Un demi-bandeau de combattant : nom en inverse, HABILETE, jauge, points. */
static void put_fighter(const char* name, unsigned char nmax,
                        unsigned char hab,
                        unsigned char end, unsigned char end0)
{
    unsigned char n = 0;

    revers(1);
    while (name[n] && n < nmax) { cputc(name[n]); n++; }
    revers(0);

    cfmt(is_fr() ? " HAB %u " : " SKL %u ", hab);
    put_gauge(end, end0);
    /* Sous cinq points, deux assauts ordinaires suffisent a tuer : le compte
     * passe en video inverse. La machine ne fait pas de rouge en 80 colonnes ;
     * l'inverse est le seul cri dont elle dispose, et il porte des deux cotes
     * du bandeau -- une creature a bout est une nouvelle, elle aussi. */
    revers(end < 5);
    cfmt(" %u/%u", end, end0);
    revers(0);
}

/* Un jet d'assaut ecrit en clair : "Vous : 4 + 3 + 12 = 19".
 *
 * Le livre fait lancer deux des et ajouter l'HABILETE ; l'ecran ne montrait
 * que la somme, et une somme n'a pas de suspense -- on lisait un verdict deja
 * rendu. Les deux des, l'HABILETE et le total, c'est le geste du joueur de
 * table rendu a l'ecran.
 *
 * L'HABILETE affichee est deduite (force - d1 - d2) plutot que relue : c'est
 * ce qui fait entrer le bonus de l'Epee Magique dans le compte sans un champ
 * de plus ni un second appel. La colonne 11 laisse "ASSAUT %u" a gauche. */
static void put_roll(unsigned char row, const char* who,
                     unsigned char d1, unsigned char d2, unsigned char force)
{
    gotoxy(11, row);
    cfmt("%s %u + %u + %u = %u", who, d1, d2,
         (unsigned char)(force - d1 - d2), force);
    pad_to(79);
}

/* Le verdict de l'assaut, a DROITE du jet de la creature et non par-dessus :
 * les deux lignes de des restent sous les yeux pendant que le coup tombe. Les
 * effacer pour annoncer la blessure reprendrait d'une main ce que put_roll
 * vient de donner. */
static void put_verdict(const char* text)
{
    gotoxy(40, CHOICE_ROW0 + 2);
    cputs(text);
    pad_to(79);
}

static void prompt_luck(void)
{
    gotoxy(0, CHOICE_ROWN);
    put_key(msg_space(), msg(M_K_ENCAISSER));
    put_key("C", msg(M_K_CHANCE));
    pad_to(79);
}

static void show_fighters(void)
{
    const Monster* m = &app.foes[app.foe_cur];

    gotoxy(0, CHOICE_ROW0);
    /* "VOUS" tient en quatre lettres, l'adversaire pas : la colonne de droite
     * commence a 33 plutot qu'a la moitie de l'ecran, ce qui laisse 19
     * caracteres a "MAITRE DES ARAIGNEES" au lieu de 12. Le demi-bandeau de
     * droite doit finir avant la colonne 79, ou l'ecran scrollerait. */
    put_fighter(msg(M_VOUS), 12, app.hero.hab, app.hero.end, app.hero.end0);
    pad_to(33);
    /* "vous devrez les combattre tous deux a tour de role" : le rang dans la
     * file appartient au bandeau, a cote de celui qui est en face -- il etait
     * jusqu'ici perdu au bout de la ligne d'assaut, la seule que les des
     * viennent de reprendre. Le nom cede trois lettres quand la file compte :
     * "PREMIERE GRENOUI" en dit assez, et 80 colonnes sont 80 colonnes. */
    put_fighter(m->name, app.foe_count > 1 ? 16 : 19, m->hab, m->end, m->end0);
    if (app.foe_count > 1) cfmt(" %u/%u", app.foe_cur + 1, app.foe_count);
    pad_to(79);
}

static void clear_bottom(void)
{
    unsigned char r;
    /* 79 et pas 80 : ecrire la derniere cellule de l'ecran ferait scroller. */
    for (r = CHOICE_ROW0; r <= CHOICE_ROWN; r++) cclearxy(0, r, 79);
}


static void print_at(unsigned char row, const char* text)
{
    /* Le texte PUIS des espaces jusqu'au bord, en un seul passage : une
     * invite courte ecrite par-dessus une longue ne laisse pas depasser sa
     * fin -- "[ESPACE] continuer" suivi du reste de "[C] Tentez votre
     * Chance" -- et la ligne ne clignote pas. 79 et pas 80, la derniere
     * cellule de l'ecran ferait scroller. */
    gotoxy(0, row);
    cputs(text);
    pad_to(79);
}

static void wait_key_at(unsigned char row, const char* prompt)
{
    print_at(row, prompt);
    cgetc();
}

/* La meme attente, mais avec la touche en video inverse comme le reste du
 * combat : "[ESPACE] continuer" jurait a cote de " ESPACE  encaisser ". */
static void wait_space_at(unsigned char row, const char* label)
{
    gotoxy(0, row);
    put_key(msg_space(), label);
    pad_to(79);
    cgetc();
}

/* Le sac a dos. Affiche par-dessus le texte, refermé par ESC.
 * `in_combat` = un assaut a deja eu lieu : les pierres d'HABILETE, d'ENDURANCE
 * et de CHANCE deviennent alors interdites (regle "Quand peut-on se servir des
 * Pierres de Magie ?"). */
#pragma bss-name (push, "LOWBSS")
/* Rend vrai si une Pierre a tue le heros. L'appelant quitte alors la scene
 * ou le combat avant d'ouvrir l'ecran de mort, sans recursion de load_scene. */
static unsigned char __fastcall__ show_inventory(unsigned char in_combat)
{
    /* N)eutre, B)enefique, M)alefique : la categorie compte (un bon sorcier ne
     * donne pas de pierre malefique), mais elle tient en une lettre. */
    static const char kKind[3] = { 'N', 'B', 'M' };
    unsigned char shown[STONE_COUNT]; /* indices 0..11, pas des enum 16 bits */
    unsigned char n, i, row, back;
    char key;
    Stone s;

    /* Le sac s'ecrit dans la page texte, et il faut donc l'ALLUMER : sans ca,
     * ouvert depuis le mode image, il se dessinait derriere l'illustration et
     * sa boucle avalait ESPACE, RETURN et les lettres sans que rien ne bouge a
     * l'ecran -- seul ESC en sortait, et il en fallait un second pour que la
     * bascule video reprenne. Vu de l'exterieur, la machine etait bloquee en
     * HGR. Les autres ecrans modaux (l'aide, le choix des Pierres) forcaient
     * deja le texte ; celui-ci etait le seul a ne pas le faire.
     * On rend au joueur, en sortant, le mode qu'il avait choisi : le sac
     * ouvert en plein combat rend son illustration au combat. */
    back = app.video_mode;
    set_video_mode(0);

    for (;;) {
        wipe();
        render_title_bar();
        gotoxy(0, 2);
        cfmt(msg(M_SAC_A_DOS), app.hero.gold);

        n = 0; row = 4;
        for (s = 0; s < STONE_COUNT; s++) {
            if (app.hero.stones[s] == 0) continue;
            gotoxy(0, row++);
            cfmt("%c) %2u  %-12s  %c%s",
                    'A' + n + (n >= 8), app.hero.stones[s],
                    stone_name(s, !is_fr()), kKind[stone_kind(s)],
                    stone_usable(s, in_combat)
                        ? "" : (msg(M_INTERDITE_EN_PLEIN)));
            shown[n++] = s;
        }
        /* Objets visibles, suivis des six amulettes, dans la colonne de
         * droite ; les drapeaux narratifs (OBJ_HIDDEN0 et au-dela) ne
         * figurent jamais dans le sac.
         *
         * Les deux listes se SUIVENT au lieu d'occuper chacune une plage
         * fixe : les amulettes commencaient ligne 13, c'est-a-dire sur le
         * dixieme objet, et le onzieme (les Graines) serait tombe dessous.
         * Onze objets plus six amulettes tiennent lignes 4 a 20, au-dessus
         * de l'invite de la ligne 22, et le compteur coute moins cher que
         * l'addition qu'il remplace. */
        row = 4;
        for (i = 0; i < OBJ_HIDDEN0; ++i) {
            if (!character_has_object(&app.hero, (Object)i)) continue;
            gotoxy(40, row++);
            cfmt("- %s", object_name((Object)i, !is_fr()));
        }
        for (i = 0; i < AMULET_COUNT; ++i) {
            if (!character_has_amulet(&app.hero, (Amulet)i)) continue;
            gotoxy(40, row++);
            cfmt("- %s", amulet_name((Amulet)i, !is_fr()));
        }
        /* Ce message concerne la colonne des Pierres, independamment des
         * objets, amulettes et drapeaux caches de la colonne de droite. */
        if (n == 0) {
            gotoxy(0, 4);
            cputs(msg(M_AUCUNE_PIERRE_MAGIQUE));
        }

        print_at(22, msg(M_UNE_PIERRE_SE));
        key = cgetc();
        /* [I] est une bascule : elle ouvre le sac et le referme. */
        if (key == 27 || key == 'I' || key == 'i') break;
        /* Une lettre hors de A..Z passe en negatif, donc au-dela de n
         * une fois dans l'octet : un seul test suffit. */
        i = (unsigned char)((key >= 'a') ? (key - 'a') : (key - 'A'));
        /* I ferme le sac ; les Pierres sautent donc cette lettre (H, J, K...). */
        if (i > 8) --i;
        if (i >= n) continue;

        s = shown[i];
        clear_bottom();
        gotoxy(0, 22);
        switch (stone_use(&app.hero, s, in_combat)) {
        case STONE_USE_FORBIDDEN:
            cputs(msg(in_combat == 2 ? M_PIERRE_ABSENTE : M_LE_PREMIER_COUP));
            break;
        case STONE_USE_NONE:
            cputs(msg(M_PIERRE_ABSENTE));
            break;
        default:
            cfmt(msg(M_LA_PIERRE_DE), stone_name(s, !is_fr()));
            break;
        }
        wait_key_at(23, msg_continue());
        if (!app.hero.end) break;
    }

    render_scene();
    set_video_mode(back);
    return app.hero_ready && !app.hero.end;
}
#pragma bss-name (pop)


/* L'ecran MAP, en texte 80 colonnes.
 *
 * Le mode texte ne demande aucune primitive de trace -- c'est ce qui a coute
 * 5 019 octets a l'ancien mode carte, retire faute de place -- et rien a
 * sauvegarder : les bascules video ne touchent que des soft-switches, la page
 * texte reste en $400-$7FF pendant tout le passage en graphique. Presser M
 * depuis l'illustration ne coute donc pas une copie de la page HGR.
 *
 * A gauche la grille 6 x 9, une case de quatre caracteres par clairiere et
 * deux caracteres de liaison entre deux colonnes : 34 colonnes en tout. A
 * droite, a partir de la colonne 38, le lieu ou l'on se tient, ses sorties et
 * la legende. La derniere cellule de l'ecran n'est jamais ecrite : le
 * firmware ferait scroller.
 *
 * Bascule, comme [I] et [H] : M ou ESC referme et rend au joueur le mode
 * video qu'il avait choisi.
 */
static void show_map(void)
{
    const char* dirs;
    const char* nom;
    const char* etat;
    const unsigned char* rec;
    unsigned char back, i, j, d, r, c, b, m, n;
    unsigned char vus;   /* le compte des clairieres vues : n sert de longueur */
    char key;

    back = app.video_mode;
    set_video_mode(0);
    /* La carte est uniquement en texte. Elle ne charge aucune illustration
     * et ne doit pas annoncer has_image si le chargement de scene a echoue. */
    wipe();
    map_seen();
    vus = 0;
    for (i = 0; i < MAP_CLR; i++) vus = (unsigned char)(vus + map_vu[i]);

    /* La barre de titre, en video inverse comme celle du recit. Ecrite
     * directement a l'ecran et comblee jusqu'au bord : un seul passage,
     * aucune cellule ne clignote, et pas de tampon a remplir d'abord. */
    revers(1);
    gotoxy(0, 0);
    cputc(' ');
    cfmt("%s -- %u %s", map_str(MS_TITRE), (unsigned)vus, map_str(MS_SUR35));
    pad_to(79);
    cputc(' ');
    revers(0);

    /* Les sentiers d'abord, les cases par-dessus : un trait qui arrive sur
     * une clairiere ne doit pas mordre sur ses parentheses. Un sentier n'est
     * dessine que depuis une clairiere VUE -- c'est la regle du livre, qui
     * fait noter « un rayon termine par ? » au bout d'un chemin repere mais
     * pas encore emprunte. */
    rec = map_data + MAP_HEAD;
    for (i = 0; i < MAP_CLR; i++, rec += 3) {
        if (!map_vu[i]) continue;
        m = rec[2];
        r = kMapRow[rec[0] >> 3];
        c = kMapCol[rec[0] & 7];
        /* La lisiere du Marais : ce n'est pas un sentier, elle a son signe. */
        if (m & 0x10) { gotoxy((unsigned char)(c + 1), (unsigned char)(r + 1)); cputc('v'); }
        for (d = 0; d < 4; d++) {
            if (!(m & (1 << d))) continue;
            j = map_voisin(i, d);
            if (j == MAP_NONE) continue;
            /* Longueur du trait : deux caracteres vers un inconnu -- un trait
             * et son point d'interrogation -- sinon de bord a bord, ce qui
             * couvre les trois sentiers de deux cases sans les nommer. */
            n = 2;
            if (map_vu[j]) {
                if (d < 2) { b = kMapRow[map_cell(j) >> 3];
                             n = (unsigned char)((b > r ? b - r : r - b) - 1); }
                else       { b = kMapCol[map_cell(j) & 7];
                             n = (unsigned char)((b > c ? b - c : c - b) - 3); }
            }
            map_trait((unsigned char)(c + kMapSC[d]), (unsigned char)(r + kMapD[d]),
                      kMapDC[d], kMapD[d], n, map_vu[j]);
        }
    }

    /* Les cases restent volontairement anonymes : une etoile signale chaque
     * clairiere connue, sans dupliquer les numeros du livre. Celle ou l'on se
     * tient passe en video inverse. */
    rec = map_data + MAP_HEAD;
    for (i = 0; i < MAP_CLR; i++, rec += 3) {
        if (!map_vu[i]) continue;
        j = (i == map_here);
        gotoxy(kMapCol[rec[0] & 7], kMapRow[rec[0] >> 3]);
        if (j) revers(1);
        cputs("(*)");
        if (j) revers(0);
    }

    /* Le panneau de droite : ou l'on est, et ce qui en part. */
    dirs = map_str(MS_DIRS);
    r = 2;
    if (map_here != MAP_NONE) {
        gotoxy(38, r++);
        cputs(map_name(map_here));
        cputsxy(38, r++, map_str(MS_SORTIES));
        m = map_out(map_here);
        for (d = 0; d < 4; d++) {
            if (!(m & (1 << d))) continue;
            j = map_voisin(map_here, d);
            nom = "?";
            etat = map_str(MS_INCONNUE);
            if (j != MAP_NONE && map_vu[j]) { nom = map_name(j); etat = map_str(MS_VUE); }
            gotoxy(38, r++);
            cfmt("  %c  %-12s  %s", dirs[d], nom, etat);
        }
        if (m & 0x10) { gotoxy(38, r++); cfmt("  %c  %-12s  %s", 'v', "", map_str(MS_HORS)); }
    }

    cputsxy(38, 11, map_str(MS_LEGENDE));
    for (i = 0; i < 5; i++) cputsxy(40, (unsigned char)(12 + i), map_str((unsigned char)(MS_LEG1 + i)));
    gotoxy(38, 18);
    cfmt("%u %s", (unsigned)vus, map_str(MS_SUR35));
    cputsxy(0, CHOICE_ROWN, map_str(MS_TOUCHES));

    for (;;) {
        key = cgetc();
        if (key == 27 || key == 'M' || key == 'm') break;
    }
    /* Restore the narrative while text writes still address both banks.
     * Combat redraws only its HUD, so returning a blank body loses the scene. */
    render_scene();
    set_video_mode(back);
}

/* [M] hors de l'Anneau de Cuivre : refus, avec la phrase du livre.
 *
 * « Personne n'a jamais pu dresser une carte de cette region [...] les
 * boussoles elles-memes en perdent le nord. [...] aussi longtemps que vous
 * garderez cet anneau a votre doigt, vous saurez toujours ou est le nord. »
 * L'Anneau est ce qui AUTORISE la carte. On refuse la touche plutot que de
 * montrer une carte desorientee : une carte qu'on ne peut pas orienter n'est
 * pas une carte, et un second rendu aurait coute des centaines d'octets dans
 * un binaire ou l'on en comptait 510. Le refus donne surtout son prix a la
 * page 049, ou l'on peut VENDRE l'anneau. Rend 1 si la carte s'est ouverte. */
static unsigned char open_map(void)
{
    if (!map_ready) return 0;
    if (!character_has_object(&app.hero, OBJ_ANNEAU)) {
        clear_bottom();
        print_at(CHOICE_ROW0, map_str(MS_ANNEAU));
        wait_key_at(CHOICE_ROWN, msg_continue());
        return 0;
    }
    show_map();
    return 1;
}

/* "A plusieurs reprises au cours de votre aventure [...] vous aurez la
 * possibilite de faire appel a votre chance" -- mais sur ces pages-la le livre
 * ne laisse pas le choix : il ORDONNE le jet et annonce les deux issues. Le
 * moteur le joue donc lui-meme, une fois la page lue. Rend la scene ou aller. */
#pragma code-name (push, "LC")
static void wait_test_key(void)
{
    row_blank(CHOICE_ROW0 + 1);
    row_blank(CHOICE_ROW0 + 2);
    cgetc();
}

static int run_luck_test(void)
{
    unsigned char roll;
    unsigned char lucky;

    gotoxy(0, CHOICE_ROW0);
    cfmt(msg(M_TENTEZ_VOTRE_CHANCE), app.hero.cha);
    pad_to(79);
    wait_test_key();

    /* Le jet est releve avant d'etre applique, pour pouvoir le montrer : la
     * regle veut qu'un point de CHANCE parte a chaque tentative, gagnee ou
     * perdue. */
    roll = roll_2d6();
    lucky = (unsigned char)(roll <= app.hero.cha);
    gotoxy(0, CHOICE_ROW0);
    cfmt(msg(M_JET_DE_CHANCE), (unsigned)roll, (unsigned)app.hero.cha);
    pad_to(79);
    row_blank(CHOICE_ROW0 + 2);
    if (app.hero.cha > 0) app.hero.cha--;

    print_at(CHOICE_ROW0 + 1, lucky ? msg(M_CHANCEUX) : msg(M_MALCHANCEUX));
    carac_apply(app.dice_n == 3 ? app.dice_carac : 0,
                lucky ? app.luck_dok : app.luck_dko);
    render_title_bar();
    wait_key_at(CHOICE_ROWN, msg_continue());
    return lucky ? app.luck_ok : app.luck_ko;
}
#pragma code-name (pop)

/* "Lancez un de et retranchez le chiffre obtenu de votre total d'ENDURANCE."
 * Le livre ordonne le jet, il ne le propose pas : le moteur le joue, mais il
 * le MONTRE -- un de qui tombe en coulisse ne se distingue pas d'une perte
 * seche, et le joueur ne saurait pas ce qu'il vient de payer.
 *
 * Meme cadre que run_luck_test, et deux messages seulement : la prose de la
 * page est encore a l'ecran au-dessus, elle dit deja ce que le de coute et
 * sur quoi ; la Feuille d'Aventure de la ligne 1 dit ce qu'il a coute. */
#pragma code-name (push, "LC")
static void prompt_dice(void)
{
    print_at(CHOICE_ROW0, msg(M_LANCEZ_LES_DES));
    wait_test_key();
}

static void run_dice_roll(void)
{
    signed char   n = app.dice_n;
    unsigned char roll;

    if (n == 3) { run_luck_test(); return; }
    prompt_dice();

    /* Un de, deux au plus : le livre n'en jette jamais davantage sur ces
     * pages, et un compteur en bonne et due forme demandait une valeur
     * absolue de char signe -- 40 octets pour choisir entre un et deux. */
    roll = roll_d6();
    if (n > 1 || n < -1) roll = (unsigned char)(roll + roll_d6());

    gotoxy(0, CHOICE_ROW0);
    cfmt(msg(M_VOUS_JETEZ), (unsigned)roll);
    pad_to(79);
    carac_apply(app.dice_carac, (n < 0) ? -(int)roll : (int)roll);
    render_title_bar();
    wait_key_at(CHOICE_ROWN, msg_continue());
}
#pragma code-name (pop)

/* La valeur courante d'une caracteristique, pour le test CS. L'or n'est pas
 * testable : le livre ne compare jamais 2d6 a une bourse. */
static unsigned char carac_value(unsigned char c)
{
    if (c == 0) return app.hero.end;
    if (c == 1) return app.hero.hab;
    return app.hero.cha;
}

/* Ligne CS : "Lancez deux des. Si le total est inferieur ou egal a vos points
 * d'ENDURANCE..." -- le meme geste que le jet de Chance, mais contre la
 * caracteristique nommee et sans depenser de point de CHANCE. Rend la scene
 * ou aller. */
#pragma code-name (push, "LC")
static int run_stat_test(void)
{
    unsigned char roll, against;

    prompt_dice();

    roll = roll_2d6();
    against = carac_value(app.cs_carac);
    gotoxy(0, CHOICE_ROW0);
    cfmt(msg(M_JET_CONTRE), (unsigned)roll, (unsigned)against);
    pad_to(79);
    wait_key_at(CHOICE_ROWN, msg_continue());
    return (roll <= against) ? app.cs_ok : app.cs_ko;
}
#pragma code-name (pop)

/* "Vous choisirez ces six Pierres dans la liste qui figure au debut de ce
 * livre, mais vous ne pourrez les prendre que..." -- un bon sorcier ne donne
 * pas de Pierre malefique, un mauvais pas de Pierre benefique, et l'on a le
 * droit de prendre plusieurs fois la meme ("par exemple 4 Pierres de Feu"). */
#pragma code-name (push, "LC")
#pragma bss-name (push, "MAPBSS")
static void choose_stones(void)
{
    static const char kKindLetter[3] = { 'N', 'B', 'M' };
    unsigned char allowed[STONE_COUNT]; /* indices 0..11 */
    unsigned char count, i;
    char key;
    Stone s;

    /* La liste des Pierres permises ne bouge pas d'un choix a l'autre : on la
     * dessine UNE fois. Seul le compteur change, et il tient sur une ligne.
     * Tout repeindre a chaque prise faisait clignoter l'ecran neuf fois de
     * suite pour six Pierres. */
    set_video_mode(0);
    wipe();
    render_title_bar();

    count = 0;
    for (s = 0; s < STONE_COUNT; s++) {
        const char k = kKindLetter[stone_kind(s)];
        if (strchr(app.choose_cats, k) == NULL) continue;
        gotoxy(0, 4 + count);
        cfmt("%c) %-12s %c", 'A' + count, stone_name(s, !is_fr()), k);
        allowed[count++] = s;
    }
    if (count == 0) { app.choose_n = 0; return; }
    while (app.choose_n > 0) {
        gotoxy(0, CHOICE_ROW0);
        cfmt(msg(M_CHOISISSEZ_PIERRES), (unsigned)app.choose_n);
        pad_to(79);
        gotoxy(0, CHOICE_ROW0 + 1);
        cputs("ESC: "); cputs(msg(M_K_IMAGE));
        pad_to(79);
        key = cgetc();
        if (key == 27 || key == ' ') { cycle_video_mode(); continue; }
        i = (unsigned char)((key >= 'a') ? (key - 'a') : (key - 'A'));
        if (i < count) {
            character_give_stone(&app.hero, allowed[i], 1);
            app.choose_n--;
        }
    }
}
#pragma bss-name (pop)
#pragma code-name (pop)

/* Un combat. Rend 0 si le heros meurt, 1 si la creature tombe, 2 s'il fuit. */
static unsigned char run_combat(void)
{
    unsigned char assaut = 0;
    unsigned char use_luck, lucky;
    unsigned char pending = 0;  /* une blessure annoncee attend d'etre encaissee */
    /* "c'est le heros qui a touche" : lu quatre fois par assaut, dans
     * l'invite, le bruitage, la blessure et le duel au premier sang. Un octet
     * coute une comparaison directe la ou `r.outcome` en coutait une par
     * dereference de pointeur. */
    unsigned char hits = 0;
    unsigned char hurt;
    /* Ce que la Chance ferait de la blessure annoncee : Chanceux, puis
     * Malchanceux. Calcules au moment ou la blessure s'affiche et gardes
     * jusqu'a l'invite, qui les montre au joueur avant qu'il ne parie. */
    unsigned char wgood = 0, wbad = 0;
    unsigned char end_in;   /* ENDURANCE avant le coup, pour last_loss (DV) */
    Round r;
    char key;

    app.last_loss = 0;

    /* La page reste en texte jusqu'au premier "engager" : le joueur lit ce
     * qui l'attend, le bandeau des combattants occupant les 4 lignes du bas.
     * Le combat passe ensuite en mode mixte, l'illustration des adversaires
     * au-dessus de l'echange d'assauts -- c'est pour ca que le bandeau porte
     * les caracteristiques des DEUX combattants, la barre de titre
     * disparaissant sous l'image. */

    for (;;) {
        /* Chaque ligne est reecrite en un passage, aucune n'est effacee
         * d'abord : c'est ce qui faisait clignoter le bandeau a chaque coup. */
        /* conio ecrit les deux banques texte via 80STORE, meme en DHGR plein. */
        *(volatile unsigned char*)0xC001 = 0;
        render_title_bar();
        show_fighters();
        if (assaut == 0) {
            row_blank(CHOICE_ROW0 + 1);
            row_blank(CHOICE_ROW0 + 2);
        }

        /* Repeindre depuis le jet conserve : ouvrir le sac ne relance pas
         * les des et ne consomme pas la blessure encore en attente. */
        else {
            gotoxy(0, CHOICE_ROW0 + 1);
            cfmt(msg(M_ASSAUT_N), assaut);
            put_roll(CHOICE_ROW0 + 1, msg(M_JET_VOUS),
                     r.hero_d1, r.hero_d2, r.hero_force);
            put_roll(CHOICE_ROW0 + 2, msg(M_JET_LUI),
                     r.monster_d1, r.monster_d2, r.monster_force);
            if (r.outcome == ROUND_DODGE) put_verdict(msg(M_VOUS_AVEZ_CHACUN));
            else {
                /* Le verdict reste a cote du jet de la creature. */
                gotoxy(40, CHOICE_ROW0 + 2);
                cputs(hits ? msg(M_VOUS_L_AVEZ) : msg(M_ELLE_VOUS_A));
                cfmt(msg(M_DEGATS), hurt);
                pad_to(79);
            }
        }

        /* L'invite : une touche par assaut. Avant le premier coup, les Pierres
         * de caracteristique sont encore permises dans le sac ;
         * ensuite la meme frappe encaisse la blessure annoncee et enchaine sur
         * l'assaut suivant. Seule la Chance demande une frappe de plus, et
         * c'est voulu : le livre la fait choisir APRES avoir vu qui a touche. */
        gotoxy(0, CHOICE_ROWN);
        put_key(msg_space(),
                msg(assaut == 0 ? M_K_ENGAGER
                    : (!pending ? M_K_SUIVANT
                       : (hits ? M_K_FRAPPER : M_K_ENCAISSER))));
        if (assaut == 0) put_key("I", msg(M_K_SAC));
        if (app.flee_target >= 0 && !flee_after) put_key("F", msg(M_K_FUIR));
        /* L'enjeu, et pas seulement la touche. "Tentez votre Chance" ne dit
         * pas ce qu'on parie ; le joueur pariait a l'aveugle un point de
         * CHANCE contre une blessure dont il ignorait les deux issues. Le
         * livre, lui, les donne : "vous pouvez oter deux points de plus" ou
         * "vous n'aurez ote qu'un seul point".
         * Une CHANCE a zero ne propose plus rien : le jet serait perdu
         * d'avance -- 2d6 ne descend pas sous 2 -- et couterait quand meme sa
         * frappe au joueur.
         * L'enjeu passe en dernier et la touche image lui cede la place : les
         * deux ne tiennent pas dans 80 colonnes, et le temps d'une frappe
         * l'enjeu compte davantage. ESC continue de fonctionner, il n'est
         * simplement plus annonce. */
        if (pending && app.hero.cha) {
            put_tag("C");
            cfmt(msg(M_K_ENJEU), app.hero.cha, wgood, wbad);
        } else {
            put_key("ESC", msg(M_K_IMAGE));
        }
        pad_to(79);

        /* Rendre le mode DHGR plein apres les ecritures texte. */
        if (app.video_mode == 1) *(volatile unsigned char*)0xC000 = 0;
        key = cgetc();
        *(volatile unsigned char*)0xC001 = 0;
        /* ESC fait tourner les modes video sans quitter le combat : le mode
         * mixte met l'illustration de la creature au-dessus des 4 lignes ou
         * s'echangent les assauts. */
        if (key == 27) { cycle_video_mode(); continue; }
        if (key == 'I' || key == 'i') {
            if (show_inventory(magic_forbidden ? 2 : (assaut != 0))) return 0;
            continue;
        }
        /* La carte en plein combat : c'est le moment ou l'on decide de fuir,
         * et savoir vers quoi. Le tour de boucle qui suit repeint la barre,
         * le bandeau et l'invite, comme apres le sac a dos. */
        if (key == 'M' || key == 'm') {
            open_map();
            row_blank(CHOICE_ROW0 + 1);
            row_blank(CHOICE_ROW0 + 2);
            continue;
        }
        if ((key == 'F' || key == 'f') && app.flee_target >= 0 && !flee_after) {
            gotoxy(0, CHOICE_ROW0);
            cputs(msg(M_VOUS_FUYEZ_ELLE));
            pad_to(79);
            row_blank(CHOICE_ROW0 + 1);
            row_blank(CHOICE_ROW0 + 2);
            prompt_luck();
            key = cgetc();
            use_luck = (key == 'C' || key == 'c');
            lucky = combat_flee(&app.hero, &app.foes[app.foe_cur], use_luck);
            render_title_bar();
            if (use_luck) print_at(CHOICE_ROW0 + 2, lucky ? (msg(M_CHANCEUX))
                                                          : (msg(M_MALCHANCEUX)));
            /* La creature blessee garde son ENDURANCE entamee : on peut
             * revenir dans la clairiere et reprendre le combat. */
            monster_remember(monster_zone_key(), app.foe_cur, &app.foes[app.foe_cur]);
            wait_space_at(CHOICE_ROWN, msg(M_K_CONTINUER));
            set_video_mode(0);
            music_stop();
            return !app.hero.end ? 0 : 2;
        }
        /* Le `cha` est le meme que celui qui decide d'afficher l'enjeu : une
         * touche qu'on n'a pas proposee ne doit pas repondre. */
        use_luck = (pending && app.hero.cha && (key == 'C' || key == 'c'));
        if (!use_luck && key != ' ' && key != '\r') continue;
        if (assaut == 0) {
            /* La musique d'action commence avec le premier assaut, pas pendant
             * la lecture de la page ni l'ouverture éventuelle du sac. */
            music_switch("BATTLE.MB", 1);
            if (app.has_image) set_video_mode(2);   /* on engage : l'image */
        }

        /* Encaisser la blessure en attente, puis enchainer : c'est ce qui fait
         * tenir un assaut en une seule frappe. */
        if (pending) {
            pending = 0;
            if (flee_after) --flee_after;
            end_in = app.hero.end;
            lucky = combat_apply(&app.hero, &app.foes[app.foe_cur], &r, use_luck);
            /* Compter les blessures elles-memes : un soin dans le sac avant
             * l'assaut (ou entre deux adversaires) ne doit pas les effacer. */
            if (end_in > app.hero.end) app.last_loss += end_in - app.hero.end;
            render_title_bar();
            /* La jauge ne bouge qu'ICI, une fois la blessure portee et la
             * Chance tentee : elle est le constat du coup, pas son annonce.
             * Le battement qui suit laisse voir les cases tomber avant que
             * les des de l'assaut suivant ne reprennent la ligne. */
            show_fighters();
            sfx_beat();
            if (use_luck) {
                /* La Chance a change la blessure : le dire, et rendre la main
                 * plutot que d'enchainer -- on vient de payer un point. */
                put_verdict(lucky ? (msg(M_CHANCEUX)) : (msg(M_MALCHANCEUX)));
                wait_space_at(CHOICE_ROWN, msg(M_K_CONTINUER));
            }
            if (monster_is_beaten(&app.foes[app.foe_cur])) {
                sfx_fall();
                gotoxy(0, CHOICE_ROW0 + 2);
                cfmt(msg(M_S_EFFONDRE), app.foes[app.foe_cur].name);
                pad_to(79);
                /* "vous devrez les combattre tous deux a tour de role" : le
                 * suivant se presente, et le heros garde l'ENDURANCE qui lui
                 * reste -- aucun repit entre deux adversaires. */
                app.foe_cur++;
                monster_remember(monster_zone_key(), app.foe_cur,
                                 &app.foes[app.foe_cur < app.foe_count
                                           ? app.foe_cur : app.foe_count - 1]);
                wait_space_at(CHOICE_ROWN, msg(M_K_CONTINUER));
                if (app.foe_cur >= app.foe_count) {
                    set_video_mode(0);
                    music_stop();
                    return 1;
                }
                assaut = 0;      /* les pierres de caracteristique redeviennent permises */
                /* Le suivant amene son portrait -- sans quoi les deux Loups du
                 * 120 se battaient sous l'image du Maitre des Loups, du
                 * premier assaut au dernier. Seulement s'il CHANGE : une file
                 * d'une seule espece ne relit pas le disque, et une page sans
                 * ligne MI se comporte comme avant. */
                load_foe_image();
                continue;
            }
            if (!app.hero.end) {
                sfx_death();
                /* L'ecran de mort n'arrive pas sur le coup : la jauge vide
                 * reste une seconde de plus sous les yeux. */
                sfx_beat();
                monster_remember(monster_zone_key(), app.foe_cur, &app.foes[app.foe_cur]);
                set_video_mode(0);
                music_stop();
                return 0;
            }
            /* Duel au premier sang : la blessure vient d'etre encaissee, le
             * combat s'arrete la et la suite dit QUI a touche. Le detour par
             * win_scene reutilise la sortie de MV telle quelle. */
            if (app.mb_ok >= 0) {
                app.win_scene = hits ? app.mb_ok : app.mb_ko;
                wait_space_at(CHOICE_ROWN, msg(M_K_CONTINUER));
                set_video_mode(0);
                music_stop();
                return 1;
            }
        }

        /* L'assaut suivant : les des d'abord, le verdict apres.
         *
         * "Lancez les deux des pour la creature. Ajoutez ses points
         * d'HABILETE" -- deux lignes, une par combattant, la ou l'ecran ne
         * donnait qu'un total et un signe. */
        assaut++;
        combat_round(&app.hero, &app.foes[app.foe_cur], &r);
        hits = (r.outcome == ROUND_HERO_HITS);

        /* Separateur sonore entre les assauts ; les jets et le verdict
         * seront peints ensemble au retour en tete de boucle. */
        sfx_beat();

        /* Le bruitage suit QUI a touche : lame seche contre coup sourd. Il
         * part avant le texte, pour tomber en meme temps que l'annonce. */
        if (r.outcome == ROUND_DODGE) {
            if (flee_after) --flee_after;
            sfx_dodge();
            continue;   /* personne n'est blesse : rien a encaisser */
        }
        if (hits) sfx_hit(); else sfx_hurt();
        /* "chaque blessure coute 2 points d'ENDURANCE" -- sauf aux creatures
         * dont la page dit autrement (ligne MD). On annonce la perte seche ;
         * la Chance peut encore la changer, et la jauge dira le vrai.
         *
         * Et on retient ce que la Chance en ferait, pour que l'invite le dise
         * avant le pari : "vous pouvez oter deux points de plus" (4 au lieu de
         * 2) ou "vous n'aurez ote qu'un seul point" quand le heros frappe ;
         * un point de moins ou un point de plus quand il encaisse. */
        if (hits) {
            hurt = 2; wgood = 4; wbad = 1;
        } else {
            hurt = app.foes[app.foe_cur].damage;
            wgood = (unsigned char)(hurt - 1);
            wbad  = (unsigned char)(hurt + 1);
        }
        pending = 1;
    }
}

/* ── L'aide ──────────────────────────────────────────────────────────────
 *
 * Le texte vit sur le disque, dans /SCOSWAMP/TEXTFR/HELPFR et /SCOSWAMP/TEXTEN/HELPEN, pas
 * dans le binaire : c'est du contenu, il se traduit et se corrige sans
 * recompiler -- et il tenait mal dans les 22 Ko de la fenetre programme.
 */
static void show_help(void)
{
    FILE* f;
    /* La barre de titre vient d'etre peinte : son tampon est libre jusqu'au
     * render_scene de la sortie, qui la refait. 81 octets de moins dans la
     * fenetre principale, pour un tampon qui ne sert qu'ici. */
#define line title_bar
    unsigned char row = 2;
    unsigned char n;

    set_video_mode(0);
    wipe();
    render_title_bar();

    if (chdir("/SCOSWAMP") != 0 ||
        (f = fopen(msg(M_HELPFR), "r")) == NULL) {
        print_at(4, msg(M_FICHIER_D_AIDE));
    } else {
        while (row < CHOICE_ROW0 && fgets(line, 81, f) != NULL) {
            n = (unsigned char)strlen(line);
            while (n > 0 && (line[n - 1] == '\n' || line[n - 1] == '\r')) line[--n] = '\0';
            if (n > 0) cputsxy(0, row, line);
            row++;
        }
        fclose(f);
    }
    wait_key_at(CHOICE_ROWN, msg_continue());
    render_scene();
#undef line
}

/* Fin de partie : "jusqu'a ce que vos points d'ENDURANCE [...] aient ete
 * reduits a zero (mort)". */
/* "jusqu'a ce que vos points d'ENDURANCE [...] aient ete reduits a zero
 * (mort)". Le joueur repart de zero ou rend la main a ProDOS -- avec ProDOS
 * 2.4 c'est Bitsy Bye qui reprend, et l'on peut lancer autre chose sans
 * redemarrer la machine. Le stub de sortie cc65 fait le QUIT du MLI ; c'est
 * la seule sortie possible depuis que le jeu occupe la place de
 * BASIC.SYSTEM. */
#pragma code-name (push, "LC")
/* Rend 1 si le joueur a repris une sauvegarde : unpack_save a alors deja
 * pose le heros, les memoires et la scene en attente, rien a remettre a
 * zero. L'ecran se repeint apres une page des sauvegardes refermee sans
 * charger. */
static unsigned char game_over(void)
{
    char key;

    for (;;) {
        set_video_mode(0);
        wipe();          /* et non clrscr : on y arrive depuis le mode mixte */
        gotoxy(0, 6);
        cputs(msg(M_VOTRE_ENDURANCE_EST));
        print_at(8, msg(M_MORT_RECOMMENCER));
        key = cgetc();
        if (key == 'R' || key == 'r') return 0;
        if ((key == 'L' || key == 'l') && show_saves(0)) return 1;
        if (key == 'Q' || key == 'q') {
            confirm_quit();
        }
    }
}
#pragma code-name (pop)

/* La creation du personnage, telle que le livre l'ouvre. */
#pragma code-name (push, "LC")
static void roll_character(void)
{
    character_roll(&app.hero);
    app.hero_ready = 1;
    scene_title = NULL;   /* sinon la barre garde le titre de la scene fatale */

    set_video_mode(0);
    videomode(VIDEOMODE_80COL);
    wipe();
    render_title_bar();
    gotoxy(0, 3);
    cputs(msg(M_FEUILLE_D_AVENTURE));
    gotoxy(0, 5);
    cfmt(msg(M_HABILETE_DE),   app.hero.hab);
    gotoxy(0, 6);
    cfmt(msg(M_ENDURANCE_DES), app.hero.end);
    gotoxy(0, 7);
    cfmt(msg(M_CHANCE_DE),   app.hero.cha);
    gotoxy(0, 9);
    cfmt(msg(M_UNE_EPEE_UNE), app.hero.gold);
    gotoxy(0, 10);
    cputs(msg(M_AUCUN_DE_CES));
    /* Qui est ce personnage, et non seulement ce qu'il vaut : c'est la page
     * 419 qui le dit, juste apres cet ecran, et la 000 juste avant. Deux
     * lignes de plus ICI auraient coute 149 octets de LOWBSS, qui n'en a que
     * 39 de libres -- la RAM basse s'arrete a $2000, ou commence HGR. Une
     * page ne coute rien, en dit davantage, et se traduit sans relier. */
    wait_key_at(13, msg(M_ESPACE_ENTRER_DANS));
}
#pragma code-name (pop)

/* La mort et ce qui la suit, en un seul endroit. Le combat n'en a plus le
 * monopole : "si vous survivez" (pages 252, 261, 274) dit que le de de la
 * ligne ED peut tuer lui aussi, et dupliquer les cinq lignes couterait plus
 * cher que la fonction. */
static void die_and_restart(void)
{
    /* L'ecran de mort n'est pas une page : sa marche funebre se pose ici, en
     * surcouche, et ne boucle pas. */
    if (strcmp(music_cur, "DEATH.MB") != 0) {
        music_stop();              /* coupe notamment la boucle BATTLE.MB */
        music_switch("DEATH.MB", 0);
    }
    if (game_over()) return;
    monster_memory_reset();
    scene_memory_reset();
    map_here = MAP_NONE;
    app.hero_ready = 0;
    app.pending_scene = 0;
}

/* Charger une nouvelle scene - version optimisée */
void load_scene(int scene_id) {
    unsigned char issue;

    app.current_scene = scene_id;
    /* La clairiere courante suit la page quand la page en designe une, et
     * reste en place sinon : 297 pages sur 412 ne sont d'aucun lieu. */
    if (map_ready) {
        issue = map_of_page((unsigned int)scene_id);
        if (issue != MAP_NONE) map_here = issue;
    }
    app.num_choices = 0;  /* Réinitialiser les choix */
    app.has_image = 0;
    app.foe_count = 0;
    app.foe_cur = 0;
    app.flee_target = -1;
    flee_after = 0;
    magic_forbidden = 0;
    app.revisit = -1;
    app.choose_n = 0;
    app.luck_ok = -1;
    app.luck_dok = 0;
    app.luck_dko = 0;
    /* Les deux premiers sont obligatoires : sans remise a zero ils fuiraient
     * d'une clairiere a la suivante -- une victoire d'hier renverrait ailleurs
     * la page d'aujourd'hui. Le troisieme est du zele, dice_carac n'etant lu
     * que si dice_n vaut autre chose que zero. */
    app.win_scene  = -1;
    app.dice_n     = 0;
    app.dice_carac = 0;
    app.cs_ok = -1; app.cs_ko = -1;
    app.mb_ok = -1; app.mb_ko = -1;
    /* last_loss ne se remet PAS a zero ici : c'est la page SUIVANT le combat
     * qui la lit (lignes DV). dv_done, si : la cascade repart a chaque page. */
    app.dv_done = 0;
    app.music_name[0] = '\0';
    app.music_over = 0;

    /* Charger d'abord le texte et les choix. Le chargeur HGR assembleur est
     * ensuite le dernier client ProDOS de la scène : son décodage direct en
     * mémoire vidéo ne peut donc perturber une ouverture de texte ultérieure.
     * C'est aussi la lecture du fichier qui applique les lignes E (effet) et
     * P (Pierres reçues) : elles jouent une fois par visite. */
    app.video_mode = 0;
    display_scene_text(scene_id);
    /* La musique de la page, des que sa ligne MU est connue : avant les des,
     * les jets et les Pierres, qui attendent une touche. La lecture du texte
     * s'est faite musique ouverte -- ProDOS masque les IRQ ~45 ms, une note
     * tenue, moins genante qu'un silence deliberer. */
    if (app.music_over) {
        /* Un combat lance sa surcouche au premier assaut. Les autres
         * surcouches jouent a l'entree, sans remplacer le theme conserve. */
        if (!app.foe_count) music_switch(app.music_name, 0);
    } else if (map_ready &&
        ((issue != MAP_NONE && issue != music_here) ||
         (issue == MAP_NONE && app.music_name[0] != '\0' &&
          /* Bourbenville est une seule zone, meme si ses rues, maisons et
           * dialogues sont plusieurs pages hors de la carte du Marais. Tant
           * que VILLAGE joue (ou vient de finir), ne pas le recharger. Une
           * surcouche change music_cur et permettra naturellement sa reprise. */
          (strcmp(app.music_name, "VILLAGE.MB") != 0 ||
           strcmp(music_cur, "VILLAGE.MB") != 0))))
        music_for_clearing();
    /* Une ligne E peut tuer a l'entree -- "vous perdez 5 points d'ENDURANCE",
     * page 357 -- et seuls le de et le combat etaient testes. La page se lit
     * d'abord, puis c'est la mort. La garde hero_ready ecarte l'accueil, ou
     * le heros n'existe pas encore et son ENDURANCE vaut zero. */
    if (app.hero_ready && character_is_dead(&app.hero)) {
        wait_key_at(CHOICE_ROWN, msg_continue());
        die_and_restart();
        return;
    }

    /* Deja venu : la page longue cede la place a sa version courte, sans rien
     * afficher entre les deux. Le passage n'est PAS marque -- c'est la page
     * courte qui l'est, et de toute facon celle-ci l'etait deja. */
    if (app.revisit >= 0) {
        app.pending_scene = app.revisit;
        return;
    }
    scene_mark_visited((unsigned int)scene_id);


    /* L'image est decodee en page HGR 1 mais PAS montree : on reste sur le
     * texte, c'est au joueur de basculer. Le decodage se fait donc sous un
     * ecran texte deja lisible, et non derriere une image qui s'affiche
     * toute seule. */
    /* Le de de la ligne ED tombe avant tout le reste : avant le jet de
     * Chance, avant le choix des Pierres, avant l'image, avant le combat.
     * C'est ce qui garantit l'ordre du 261 -- le de precede le combat de la
     * meme page quelle que soit la position de la ligne dans le fichier. */
    if (app.dice_n != 0) {
        run_dice_roll();
        /* "si vous survivez" : un ENDURANCE tombe a zero apres le jet part sur
         * game_over, exactement comme une mort au combat. */
        if (character_is_dead(&app.hero)) { die_and_restart(); return; }
        /* Le jet a ecrase les 4 lignes du bas : les repeindre. run_luck_test
         * n'en a jamais besoin, il rend toujours une scene ; ED laisse la
         * page en place et lui rend la main. */
        render_scene();
    }

    /* La page teste une caracteristique : 2d6 contre elle, et la suite
     * depend du jet -- rien a choisir. */
    if (app.cs_ok >= 0) {
        app.pending_scene = run_stat_test();
        return;
    }

    /* La page ordonne un jet de Chance : il decide de la suite, il n'y a donc
     * pas de choix a offrir au joueur. */
    if (app.luck_ok >= 0) {
        app.pending_scene = run_luck_test();
        return;
    }

    /* Le sorcier tend ses Pierres avant tout le reste : le joueur vient de
     * lire la page qui les lui offre. L'image de la page (ou du personnage
     * qui donne les Pierres) est chargee avant l'ecran de choix, afin que la
     * bascule DHGR reste disponible pendant les six prises. */
    app.has_image = 0;
    foe_shown = 0;
    if (app.choose_n > 0) {
        app.has_image = load_hgr_image_as(scene_id, 'N');
        choose_stones();
        render_scene();
    }

    /* Une clairiere avec un adversaire prend son image de bataille si elle
     * existe, sinon son illustration ordinaire. */
    /* La musique joue pendant les lectures : ProDOS masque les IRQ le temps
     * de l'E/S, le tick prend un peu de retard et reprend -- jamais de
     * coupure, c'est la regle. */
    /* monster_seal et monster_enter passent DEVANT l'image : ils ne touchent
     * pas au disque, et l'image a montrer est celle de l'adversaire ou l'on
     * reprend, pas celle du premier de la file. Le chargeur HGR reste ainsi le
     * dernier client ProDOS de la scene. */
    /* La page precedente ne prete pas la sienne. Ne pas remettre has_image a
     * zero ici : l'illustration chargee pour le choix des Pierres peut servir
     * de repli si aucun adversaire n'est present. */
    if (app.foe_count > 0) {
        for (issue = 0; issue < app.foe_count; issue++) monster_seal(&app.foes[issue]);
        /* "il est possible que vous reveniez plus tard dans cette clairiere et
         * que ce ou ces monstres s'y trouvent encore" : monster_enter rend
         * l'ENDURANCE laissee au dernier passage, et 0 si la creature est deja
         * morte. */
        app.foe_cur = monster_enter(monster_zone_key(), app.foes, app.foe_count);
        if (app.foe_cur < app.foe_count) load_foe_image();
    }
    if (!app.has_image)  app.has_image = load_hgr_image_as(scene_id, 'N');

    if (app.foe_count == 0) return;
    /* La file peut avoir ete videe lors d'une visite precedente : c'est une
     * victoire acquise, pas un combat a rejouer. Elle sort donc par la meme
     * porte, et non plus par un `return` sec -- sans quoi une page passee a
     * MV, qui n'a plus AUCUNE ligne C, laisserait le joueur devant un ecran
     * sans issue. 3 = "gagne avant d'arriver" ; run_combat ne rend que 0
     * (mort), 1 (victoire) ou 2 (fuite). */
    issue = (app.foe_cur < app.foe_count) ? run_combat() : 3;
    if (issue != 3) app.hero.objects &= ~(1u << OBJ_POTION_NAINE);

    if (issue == 0) {
        die_and_restart();
    } else if (issue == 2) {
        app.pending_scene = app.flee_target;
    } else if (app.win_scene >= 0) {
        /* La page dit ou mene la victoire : y aller, au lieu de repeindre une
         * page dont le seul choix etait "vous avez tue le Maitre". run_combat
         * a deja annonce l'effondrement et attendu ESPACE. */
        app.pending_scene = app.win_scene;
    } else if (issue == 1) {
        /* La creature vient de tomber : le combat a mange les 4 lignes du bas,
         * il faut y remettre les choix. Une file deja abattue (3) n'a rien
         * peint par-dessus : la page est restee telle que display_scene_text
         * l'a rendue. */
        render_scene();
    }
}

/* Fonction pour afficher l'écran de sélection de langue */
/* L'ecran-titre vit sur le disque (TITLE.TXT), comme tout le contenu : 26
 * cprintf et ~850 octets de chaines pour un ecran montre une fois etaient le
 * plus gros gisement d'octets du binaire. S'il manque, la ligne de secours
 * suffit a choisir la langue. */
static void display_language_selection(void) {
    /* Le tampon de page est vide -- aucune scene n'est encore lue -- et il
     * fait 1 280 octets en RAM basse : la ligne du titre y tient sans rien
     * couter a la fenetre principale. */
#define line file_buffer
    FILE* f;

    videomode(VIDEOMODE_80COL);
    clrscr();
    /* Sur le volume, l'empaqueteur retire l'extension .TXT -- meme
     * convention que MSGFR/MSGEN. */
    f = fopen("TITLE", "r");
    if (f) {
        while (fgets(line, 81, f)) { cputs(line); cputc('\r'); }
        fclose(f);
    } else {
        cputs("[F] Francais   [E] English\r\n");
    }
#undef line
}

/* [D] et [T] de l'ecran-titre : DIAPO ou TOTAL, les deux autres programmes
 * du volume. Leur lanceur SYS est lu en $2000, la ou ProDOS l'aurait mis, et
 * l'on y saute : le jeu ne revient pas, le lanceur charge son programme en
 * $4000 par-dessus. Bien moins cher que exec() de cc65, et la page HGR est
 * libre a ce moment. La ROM est remise en lecture pour le demarrage cc65 du
 * lanceur ; le prefixe, lui, est refait par le lanceur (chdir /SCOSWAMP).
 * Bitsy Bye n'honore pas le QUIT etendu avec chemin, qui aurait ete plus
 * court encore. */
static void launch(const char* path)
{
    FILE* f = fopen(path, "rb");
    if (!f) return;
    fread(HGR_PAGE1, 1, 0x2000, f);
    fclose(f);
    music_stop();
    __asm__("bit $C082");
    ((void (*)(void))HGR_PAGE1)();
}

/* Fonction pour sélectionner la langue */
static void select_language(void) {
    char key;
    
    display_language_selection();
    
    /* Attendre le choix de langue. C'est le premier appui de touche de la
     * partie : on en profite pour semer les des avec le temps d'attente --
     * l'Apple II n'a pas d'autre source de hasard au demarrage. */
    while (1) {
        key = dice_seed_from_keypress();
        if (key == 'F' || key == 'f') {
            strcpy(app.language, "FR");
            break;
        } else if (key == 'E' || key == 'e') {
            strcpy(app.language, "EN");
            break;
        } else if (key == 'D' || key == 'd') {
            launch("DIAPO/DIAPO.SYSTEM");
        } else if (key == 'T' || key == 't') {
            launch("TOTAL/TOTAL.SYSTEM");
        }
    }
}

/* Fonction pour gérer les choix de l'utilisateur */
/* La page des sauvegardes. Dix emplacements, chacun sous le titre de la
 * page ou la partie s'est arretee. `saving` dit si [0-9] ecrit ou reprend.
 * La touche qui l'a ouverte la referme, ESC aussi. Rend 1 si une partie a
 * ete chargee (pending_scene est alors pose par unpack_save). */
#pragma bss-name (push, "LOWBSS")
static unsigned char show_saves(unsigned char saving)
{
    char title[SAVE_TITLE];
    unsigned char slot;
    char key;

    set_video_mode(0);
    for (;;) {
        wipe();
        render_title_bar();
        print_at(2, msg(saving ? M_SAUVEGARDES : M_CHARGEMENTS));
        for (slot = 0; slot < 10; slot++) {
            slot_title(slot, title);
            gotoxy(2, 4 + slot);
            cfmt("%c) %s", '0' + slot, title[0] ? title : msg(M_VIDE));
        }
        key = cgetc();
        if (key == 27) return 0;
        if (saving  && (key == 'S' || key == 's')) return 0;
        if (!saving && (key == 'L' || key == 'l')) return 0;
        if (key < '0' || key > '9') continue;
        slot = (unsigned char)(key - '0');
        if (saving) {
            print_at(CHOICE_ROW0, msg(save_game(slot) ? M_SAUVE_OK : M_SAUVE_ERREUR));
            wait_key_at(CHOICE_ROWN, msg_continue());
            return 0;
        }
        if (load_game(slot)) {
            /* La sauvegarde restaure aussi la langue : les deux catalogues
             * residents doivent suivre avant de repeindre la page. */
            messages_load(!is_fr());
            map_load();
            return 1;
        }
        print_at(CHOICE_ROW0, msg(M_CHARGE_ERREUR));
        wait_key_at(CHOICE_ROWN, msg_continue());
    }
}
#pragma bss-name (pop)

void handle_user_input(char key) {
    unsigned char choice_num;
    Choice* c;
    
    if (key == ' ' || key == '\r' || key == 27) {
        /* Barre d'espace, RETURN ou ESC : cycler les modes */
        cycle_video_mode();
        
    } else if (key == 'I' || key == 'i') {
        /* Hors combat, toutes les Pierres sont utilisables. */
        if (show_inventory(0)) { die_and_restart(); return; }

    } else if (key == 'H' || key == 'h') {
        show_help();

    } else if (key == 'S' || key == 's' || key == 'L' || key == 'l') {
        /* pack_save et load_game partagent file_buffer avec le texte de la
         * scene. Sans partie chargee, on relit la page au prochain tour pour
         * restaurer ses pointeurs ; restoring interdit de rejouer les gains,
         * pertes, jets et autres effets d'entree. */
        if (!show_saves(key == 'S' || key == 's')) {
            restoring = 1;
            app.pending_scene = app.current_scene;
        }

    } else if ((key == 'R' || key == 'r') && app.num_choices == 0) {
        /* Recommencer depuis une page sans issue : la meme remise a zero que
         * die_and_restart, sans l'ecran de mort -- la page vient de la dire. */
        monster_memory_reset();
        scene_memory_reset();
        map_here = MAP_NONE;
        app.hero_ready = 0;
        app.pending_scene = 0;

    } else if (key == 'M' || key == 'm') {
        /* La carte. Le test precede la branche A-Z : `M` y serait lu comme
         * l'index 12, donc jamais un choix valide (MAX_CHOICES = 5), mais le
         * code deviendrait fragile au premier elargissement. */
        if (map_ready) {
            open_map();
            /* La carte ne touche pas file_buffer : les pointeurs de texte
             * et les choix sont encore valides. Relire la page rejouerait
             * ses effets d'entree et son detour V, et forcerait le texte. */
            render_scene();
        }

    } else if (key == 'Q' || key == 'q') {
        confirm_quit();
        
    } else if ((key >= 'A' && key <= 'Z') || (key >= 'a' && key <= 'z')) {
        /* Choix par lettre */
        choice_num = (unsigned char)((key >= 'a') ? (key - 'a') : (key - 'A'));
        if (choice_num < app.num_choices) {
            c = &app.choices[choice_num];
            if (!choice_available(choice_num)) {
                /* On ne lance pas un sort qu'on n'a pas. */
                clear_bottom();
                print_at(CHOICE_ROW0, msg(M_PIERRE_ABSENTE));
                wait_key_at(CHOICE_ROWN, msg_continue());
                render_scene();
                return;
            }
            /* La Pierre exigee se desintegre en servant. */
            if (c->require < STONE_COUNT) {
                /* Le contrecoup de Malediction est le jet ED de la page cible.
                 * stone_use le ferait payer une premiere fois en silence. */
                if (c->require == STONE_MALEDICTION) --app.hero.stones[c->require];
                else stone_use(&app.hero, (Stone)c->require, 0);
            }
            /* Une Pierre offerte par le choix change de main avant le saut. */
            if (c->grant < STONE_COUNT) character_give_stone(&app.hero, (Stone)c->grant, 1);
            if (c->obj_mode == 3) character_take_object(&app.hero, (Object)c->object);
            /* Le premier choix de l'introduction lance la creation : le
             * joueur comprend d'abord qui il va incarner, puis les des
             * produisent sa Feuille d'Aventure avant l'entree au Marais. */
            if (!app.hero_ready) roll_character();
            load_scene(c->scene_id);
        }
    }
}

void main(void) {
    char key;

    /* LOWBSS n'est pas dans la BSS que crt0 met a zero : on le fait ici,
     * avant tout, avec les bornes que le lieur exporte (scoswamp.cfg). */
    memset(_LOWBSS_RUN__, 0, (size_t)_LOWBSS_SIZE__);

    /* app vient d'etre mise a zero avec LOWBSS. load_scene initialise les
     * champs de scene ; seule la sentinelle de la boucle est necessaire ici. */
    app.pending_scene = -1;
    monster_memory_reset();
    scene_memory_reset();
    strcpy(app.language, "FR");  /* Valeur par défaut */

    /* BASIC.SYSTEM ne garantit pas le préfixe cc65. Le fixer explicitement
     * valide aussi le nom de volume ProDOS avant toute ouverture de fichier. */
    if (chdir("/SCOSWAMP") != 0) {
        clrscr();
        oops("VOLUME /SCOSWAMP");
        return;
    }
    
    /* Note: Le prefix ProDOS est défini par l'environnement de lancement
     * (typiquement via BASIC.SYSTEM ou le répertoire du fichier .SYSTEM)
     * Les chemins relatifs dans ce programme sont résolus à partir de ce prefix
     * Voir PRODOS-MLI.md pour plus de détails sur chdir() et getcwd()
     */
    
    /* Sélection de langue */
    select_language();

    /* Le catalogue de l'interface suit la langue choisie. */
    messages_load(app.language[0] != 'F');
    /* La carte suit la meme langue, et le meme principe : c'est une donnee du
     * disque. Sans le fichier MAP, map_ready reste a zero et la touche M ne
     * repond pas -- le reste du jeu ne s'en apercoit pas. */
    map_load();
    music_slot = music_detect();   /* Mockingboard : slots 7..1 ; 0 = muet */

    /* L'introduction vient avant les des : son choix A initie explicitement
     * la creation du personnage. [L] peut aussi reprendre une partie ici. */
    load_scene(0);
    
    /* Boucle principale. La scène en attente évite que load_scene s'appelle
     * lui-même sur une Fuite ou une mort : la pile cc65 fait 2 Ko et une
     * poursuite de clairière en clairière la mangerait. */
    while (1) {
        if (app.pending_scene >= 0) {
            int next = app.pending_scene;
            app.pending_scene = -1;
            load_scene(next);
            restoring = 0;
            continue;
        }
        /* Une page restee sans aucun choix est une fin -- mort par la prose,
         * victoire, ou combat gagne sans suite. Le moteur offre alors de
         * recommencer, de reprendre une sauvegarde ou de quitter, plutot que
         * de laisser le joueur devant un ecran muet. Ici, au point ou la
         * page est vraiment inactive : apres les des, les jets et le combat. */
        if (app.num_choices == 0) print_at(CHOICE_ROWN, msg(M_MORT_RECOMMENCER));
        key = cgetc();
        handle_user_input(key);
    }
}
