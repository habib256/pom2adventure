/*
 * DICE - Les des du livre, et de quoi les semer.
 *
 * Defis Fantastiques ne connait qu'un de a six faces. Tout le reste des
 * regles en decoule : 1d6+6, 2d6+12, et le 2d6 des Forces d'Attaque.
 */

#ifndef DICE_H
#define DICE_H

/* Semence explicite. Le moteur est deterministe a semence egale : c'est ce
 * qui rend les regles testables sur machine hote. */
void dice_seed(unsigned int seed);

unsigned char roll_d6(void);    /* 1..6  */
unsigned char roll_2d6(void);   /* 2..12 */

#ifdef __CC65__
/* Attend une touche en comptant, seme le generateur avec le compte, et rend
 * la touche. Sur Apple II il n'y a pas d'horloge : le seul hasard disponible
 * au demarrage est le temps que met le joueur a appuyer. Une constante en dur
 * (`srand(0x1234)`) donnerait la meme partie a
 * chaque lancement, des a la creation du personnage.
 * Passe par kbhit/cgetc et non par $C000 : voir dice.c. */
char dice_seed_from_keypress(void);
#endif

#endif /* DICE_H */
