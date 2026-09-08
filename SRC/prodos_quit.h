/*
 * prodos_quit.h - Sortie propre vers ProDOS 8
 *
 * À utiliser à la place de exit() dans tout binaire lié avec
 * SRC/apple2enh-game.cfg, qui détruit BASIC.SYSTEM en cours d'exécution.
 *
 * Auteur  : Arnaud VERHILLE (@habib256)
 * Licence : GNU GPL v3.0
 */

#ifndef PRODOS_QUIT_H
#define PRODOS_QUIT_H

/*
 * Rend la main à ProDOS 8 via l'appel MLI QUIT ($BF00, commande $65).
 * ProDOS relance son sélecteur de programme. Ne revient jamais.
 */
void prodos_quit(void);

#endif /* PRODOS_QUIT_H */
