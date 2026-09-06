/* Genere par SCOSWAMP.MORE/TOOLS/build_messages.py -- ne pas editer.
 * L'ordre suit MSGFR / MSGEN sur le disque. */

#ifndef MESSAGES_H
#define MESSAGES_H

enum {
    M_ESPACE_CONTINUER,
    M_VOUS,
    M_SAC_A_DOS,
    M_INTERDITE_EN_PLEIN,
    M_AUCUNE_PIERRE_MAGIQUE,
    M_UNE_PIERRE_SE,
    M_LE_PREMIER_COUP,
    M_PIERRE_ABSENTE,
    M_LA_PIERRE_DE,
    M_VOUS_FUYEZ_ELLE,
    M_CHANCEUX,
    M_MALCHANCEUX,
    M_ASSAUT_N,
    M_JET_VOUS,
    M_JET_LUI,
    M_VOUS_AVEZ_CHACUN,
    M_VOUS_L_AVEZ,
    M_ELLE_VOUS_A,
    M_K_ENGAGER,
    M_K_ENCAISSER,
    M_K_FRAPPER,
    M_K_CHANCE,
    M_K_ENJEU,
    M_K_SUIVANT,
    M_K_FUIR,
    M_K_SAC,
    M_K_IMAGE,
    M_K_CONTINUER,
    M_DEGATS,
    M_TOUCHES,
    M_JET_CONTRE,
    M_S_EFFONDRE,
    M_HELPFR,
    M_FICHIER_D_AIDE,
    M_VOTRE_ENDURANCE_EST,
    M_ESPACE_RECOMMENCER,
    M_FEUILLE_D_AVENTURE,
    M_HABILETE_DE,
    M_ENDURANCE_DES,
    M_CHANCE_DE,
    M_UNE_EPEE_UNE,
    M_AUCUN_DE_CES,
    M_ESPACE_ENTRER_DANS,
    M_CHOISISSEZ_PIERRES,
    M_PRENDRE_UNE_PIERRE,
    M_TENTEZ_VOTRE_CHANCE,
    M_JET_DE_CHANCE,
    M_MORT_RECOMMENCER,
    M_LANCEZ_LES_DES,
    M_VOUS_JETEZ,
    M_SAUVEGARDES,
    M_CHARGEMENTS,
    M_VIDE,
    M_SAUVE_OK,
    M_SAUVE_ERREUR,
    M_CHARGE_ERREUR,
    MSG_COUNT
};

/* La taille du tampon vient d'ici, pas de messages.c : ecrite a la
 * main elle etait a la fois fausse et genereuse -- 1408 octets pour
 * un catalogue qui en demandait 1100, dans un binaire ou il en
 * restait 215 de libres. La marge de 32 laisse la place a une
 * traduction un peu plus longue sans toucher au code. */
#define MSG_BYTES 1642

/* Charge le catalogue de la langue voulue. Rend 0 si le fichier manque
 * ou ne contient pas MSG_COUNT lignes -- mieux vaut un ecran vide
 * qu'un catalogue decale d'une ligne. */
int  messages_load(int english);
char* msg(int id);

#endif /* MESSAGES_H */
