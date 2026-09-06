/* DIAPO: automatic DHGR slideshow. Same decoder and video path as the game.
 * Two simultaneous streams use ProDOS buffers $0800 and $0C00. DIAPO has
 * no MAPBSS, so both are available; packed_data starts at $1000.
 */
#include <stdio.h>
#include <string.h>
#include <conio.h>
#include <unistd.h>
#include "hgr_rle.h"
#include "memory_swap.h"
#include "music.h"

static struct Slide { char path[64]; char title[80]; } slide;
static unsigned int frame;
unsigned char diapo_mixed, diapo_menu, diapo_track, diapo_slot;
/* Exported diagnostics also make frame/sequence validation possible. */
unsigned int diapo_index, diapo_errors, diapo_loops, diapo_total;
static unsigned char image_ok;
#define TRACKS 64
#define PAGE_ROWS 16
#define PAGE_SIZE (PAGE_ROWS * 3)
static struct Track { char file[16]; char title[32]; } tracks[TRACKS];
unsigned char diapo_selected;
unsigned int diapo_menu_draws;
static unsigned char track_count = 1;

static unsigned char quit_key(char key)
{
    return key == 'q' || key == 'Q' || key == 27;
}

static unsigned char read_metadata(void)
{
    FILE* f;
    unsigned char header[8];
    unsigned char valid = 0, i;
    unsigned int bytes;
    f = fopen("DIAPO/DIAPO.DATA", "rb");
    if (!f) return 0;
    if (fread(header, 1, 8, f) == 8 && !memcmp(header, "DIA1", 4) &&
        header[6] && header[6] <= TRACKS && header[7] == sizeof(struct Track)) {
        diapo_total = header[4] | ((unsigned int)header[5] << 8);
        track_count = header[6];
        bytes = track_count * sizeof(struct Track);
        valid = diapo_total && fread(tracks, 1, bytes, f) == bytes;
        for (i = 0; i < track_count; ++i) {
            tracks[i].file[15] = 0;
            tracks[i].title[31] = 0;
        }
    }
    fclose(f);
    return valid;
}

static unsigned char play_track(unsigned char selection)
{
    FILE* f;
    char filename[40];
    size_t n, total = 0;
    unsigned char valid = 1;
    music_stop();
    diapo_track = 0;
    if (!selection) return 1;
    if (!diapo_slot) return 0;
    sprintf(filename, "MUSIC/%s", tracks[selection].file);
    f = fopen(filename, "rb");
    if (!f) return 0;
    do {
        n = fread(music_buf, 1, MUSIC_STAGE, f);
        if (!total && (n <= 8 || memcmp(music_buf, "MB1", 3))) valid = 0;
        if (total + n > MUSIC_ZONE) { valid = 0; break; }
        if (n) music_store(total, n);
        total += n;
    } while (n == MUSIC_STAGE);
    if (ferror(f)) valid = 0;
    fclose(f);
    if (valid) {
        music_select(0);
        music_set_loop(1);
        music_play();
        diapo_track = selection;
    }
    return valid;
}

/* Three columns, 16 rows each. Only the marker changes within a page. */
static void menu_marker(unsigned char item, char marker)
{
    item %= PAGE_SIZE;
    cputcxy(1 + (item / PAGE_ROWS) * 26, 5 + item % PAGE_ROWS, marker);
}

static void menu_draw(unsigned char first)
{
    unsigned char i, cell;
    ++diapo_menu_draws;
    clrscr();
    gotoxy(23, 1); cputs("DIAPO / MOCKINGBOARD MUSIC");
    gotoxy(1, 3);
    if (diapo_slot) cprintf("Mockingboard slot %u   Playing: %s", diapo_slot, tracks[diapo_track].title);
    else cputs("No Mockingboard detected. Silent slideshow remains available.");
    for (i = first; i < track_count && i < first + PAGE_SIZE; ++i) {
        cell = i - first;
        gotoxy(3 + (cell / PAGE_ROWS) * 26, 5 + cell % PAGE_ROWS);
        cprintf("%.23s", tracks[i].title);
    }
    gotoxy(1, 22); cputs("ARROWS select   RETURN play / STOP   M back to image   Q quit");
}

/* Text page and DHGR page occupy separate memory: no image reload needed. */
static unsigned char music_menu(void)
{
    unsigned char previous, first;
    char key;
    diapo_selected = diapo_track;
    diapo_menu = 1;
    switch_to_text();
    first = (diapo_selected / PAGE_SIZE) * PAGE_SIZE;
    menu_draw(first);
    menu_marker(diapo_selected, '>');
    for (;;) {
        key = cgetc();
        if (quit_key(key)) { diapo_menu = 0; return 1; }
        if (key == 'm' || key == 'M') break;
        previous = diapo_selected;
        if (key == 11) diapo_selected = diapo_selected ? diapo_selected - 1 : track_count - 1;
        if (key == 10) diapo_selected = (diapo_selected + 1) % track_count;
        if (key == 8) diapo_selected = diapo_selected >= PAGE_ROWS ? diapo_selected - PAGE_ROWS : diapo_selected;
        if (key == 21 && diapo_selected + PAGE_ROWS < track_count) diapo_selected += PAGE_ROWS;
        if (previous != diapo_selected) {
            if (diapo_selected / PAGE_SIZE != previous / PAGE_SIZE) {
                first = (diapo_selected / PAGE_SIZE) * PAGE_SIZE;
                menu_draw(first);
            } else menu_marker(previous, ' ');
            menu_marker(diapo_selected, '>');
        }
        if (key == 13) {
            if (play_track(diapo_selected)) break;
            gotoxy(1, 23); cputs("Cannot play this track. Select another title or STOP.");
        }
    }
    diapo_menu = 0;
    return 0;
}

/* One VBL edge, about 1/60 second on an NTSC IIe. No CPU-speed delay. */
static void wait_frame(void)
{
    while (*(volatile unsigned char*)0xC019 & 0x80) {}
    while (!(*(volatile unsigned char*)0xC019 & 0x80)) {}
}

static unsigned char read_path(FILE* catalog)
{
    if (fread(&slide, 1, sizeof(slide), catalog) != sizeof(slide)) return 0;
    slide.path[63] = 0;
    slide.title[79] = 0;
    return slide.path[0] != 0;
}

static void footer(void)
{
    unsigned char row;
    switch_to_mixed();
    for (row = 20; row < 24; ++row) {
        gotoxy(0, row);
        cclear(79);
    }
    gotoxy(0, 20);
    cputs(slide.title);
    gotoxy(0, 21);
    cprintf("Image %u of %u  -  %.50s", diapo_index, diapo_total, slide.path);
    gotoxy(0, 22);
    cputs(!image_ok ? "Unable to read this image." :
          tracks[diapo_track].title);
    gotoxy(0, 23);
    cputs("SPACE full/mixed   LEFT/RIGHT previous/next   M music   Q quit");
}

static void title(void)
{
    switch_to_text();
    clrscr();
    gotoxy(32, 2); cputs("D I A P O");
    gotoxy(27, 5); cputs("S C O R P I O N  S W A M P");
    gotoxy(17, 7); cputs("A DOUBLE HIGH-RESOLUTION IMAGE SLIDESHOW");
    gotoxy(7, 10); cputs("Explore the world of Scorpion Swamp through its illustrations.");
    gotoxy(7, 12); cprintf("This collection brings together all %u scene and combat images.", diapo_total);
    gotoxy(7, 14); cputs("The slideshow advances automatically and loops after the last image.");
    gotoxy(7, 16); cputs("Images fill the screen. SPACE toggles fullscreen / mixed information.");
    gotoxy(7, 18); cputs("LEFT / RIGHT arrows: previous / next image. RETURN also advances.");
    gotoxy(7, 20); cputs("M opens the music menu. RETURN skips ahead. Q returns to Bitsy Bye.");
    gotoxy(23, 22); cputs("RETURN start slideshow    M music    Q quit");
}

int main(void)
{
    FILE* catalog;
    char key;
    videomode(VIDEOMODE_80COL);
    clrscr();
    cputs("PLEASE WAIT");
    if (chdir("/SCOSWAMP") || !read_metadata() ||
        !(catalog = fopen("DIAPO/DIAPO.IMAGES", "rb"))) {
        cputs("DIAPO: image catalogue not found.\r\n");
        cgetc();
        return 1;
    }
    diapo_slot = music_detect();
    title();
    for (;;) {
        key = cgetc();
        if (quit_key(key)) goto done;
        if (key == 13) break;
        if (key == 'm' || key == 'M') {
            if (music_menu()) goto done;
            title();
        }
    }
    for (;;) {
        if (!read_path(catalog)) {
            if (ferror(catalog) || !diapo_index) break;
            rewind(catalog);
            diapo_index = 0;
            ++diapo_loops;
            continue;
        }
        image_ok = hgr_rle_load(slide.path);
        if (!image_ok) ++diapo_errors;
        ++diapo_index;
        if (diapo_mixed) footer(); else switch_to_hgr();
        frame = 0;
        while (frame < 300) {
            if (kbhit()) {
                key = cgetc();
                if (quit_key(key)) goto done;
                if (key == ' ') {
                    diapo_mixed = !diapo_mixed;
                    if (diapo_mixed) footer(); else switch_to_hgr();
                }
                if (key == 'm' || key == 'M') {
                    if (music_menu()) goto done;
                    if (diapo_mixed) footer(); else switch_to_hgr();
                }
                if (key == 8) {
                    /* Rewind to the previous entry, wrapping first to last. */
                    unsigned int target = diapo_index > 1 ? diapo_index - 1 : diapo_total;
                    if (fseek(catalog, (long)(target - 1) * sizeof(slide), SEEK_SET)) goto done;
                    diapo_index = target - 1;
                    break;
                }
                if (key == '\r' || key == 21) break;
            }
            wait_frame();
            ++frame;
        }
    }
done:
    music_stop();
    fclose(catalog);
    switch_to_text();
    return 0; /* cc65 QUIT returns to Bitsy Bye. */
}
