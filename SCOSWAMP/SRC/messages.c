/*
 * MESSAGES - le catalogue de l'interface, lu sur le disque.
 *
 * Voir SCOSWAMP.MORE/TOOLS/build_messages.py : l'enumeration de messages.h et
 * les fichiers MSGFR / MSGEN sortent du meme script, dans le meme ordre.
 */

#include "messages.h"
#include <stdio.h>
#include <string.h>
#include <unistd.h>

/* MSG_BYTES est genere avec le catalogue. Le texte est decoupe en place :
 * les pointeurs visent dedans, rien n'est recopie. Pour les tailles mesurees,
 * voir DOCS/AUDIT-MEMOIRE-SCOSWAMP.md et messages.h. */

/* Le dernier octet reste a zero : c'est la chaine vide que rend msg() quand
 * le catalogue n'a pas pu etre charge. */
#pragma bss-name (push, "LOWBSS")   /* RAM basse $1000-$1FFF, cf. scoswamp.cfg */
static char  pool[MSG_BYTES];
static char* slot[MSG_COUNT];
#pragma bss-name (pop)
static int   ready;

int messages_load(int english)
{
    FILE* f;
    size_t n;
    char* p;
    char* end;
    int count = 0;

    ready = 0;
    if (chdir("/SCOSWAMP") != 0) return 0;
    f = fopen(english ? "TEXTEN/MSGEN" : "TEXTFR/MSGFR", "r");
    if (f == NULL) return 0;
    n = fread(pool, 1, sizeof(pool) - 1, f);
    fclose(f);
    if (n == 0) return 0;
    pool[n] = '\0';

    p = pool;
    end = pool + n;
    while (p < end && count < MSG_COUNT) {
        slot[count++] = p;
        while (p < end && *p != '\n' && *p != '\r') p++;
        if (p < end) {
            const char cr = *p;
            *p++ = '\0';
            if (cr == '\r' && p < end && *p == '\n') p++;
        }
    }
    /* Un catalogue incomplet decalerait tous les messages suivants : mieux
     * vaut le refuser en bloc. */
    if (count != MSG_COUNT) return 0;
    ready = 1;
    return 1;
}

char* msg(int id)
{
    if (!ready || id < 0 || id >= MSG_COUNT) return pool + MSG_BYTES - 1;
    return slot[id];
}
