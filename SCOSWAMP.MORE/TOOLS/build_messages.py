#!/usr/bin/env python3
"""Genere le catalogue de messages de l'interface.

Le texte du jeu est une donnee : les pages, l'aide et la carte vivent sur le
disque ProDOS. Les messages de l'interface faisaient exception -- 39 paires
FR/EN en dur, 2 409 octets de litteraux dans un binaire qui n'avait plus 21
octets de libre. Ils vivent maintenant dans MSGFR / MSGEN, et le binaire n'en
charge qu'une langue.

Les chaines de l'ecran MAP, elles, ne passent PAS par ici : elles voyagent
dans le fichier MAP (SCOSWAMP.MORE/TOOLS/build_map.py), avec les noms des
clairieres. Le catalogue vit en RAM basse, ou il ne restait que quelques
dizaines d'octets ; le bloc MAP vit dans le kilo-octet de $0C00, ou il y a
de la place.

Ce script est la seule source : il ecrit d'un meme geste l'enumeration C et les
deux fichiers. Editer l'un sans l'autre decalerait tout le catalogue, et le jeu
afficherait les messages les uns pour les autres.

    python3 build_messages.py --root <depot>
"""
import argparse
from pathlib import Path

# (nom C, francais, anglais) -- L'ORDRE FAIT FOI, il fixe les indices.
MESSAGES = [
    ('M_ESPACE_CONTINUER', '[ESPACE] continuer', '[SPACE] continue'),
    ('M_VOUS', 'VOUS', 'YOU'),
    ('M_SAC_A_DOS', "SAC A DOS -- %u Pieces d'Or, une epee, un justaucorps de cuir", 'BACKPACK -- %u Gold Pieces, a sword, a leather jerkin'),
    ('M_INTERDITE_EN_PLEIN', '   interdite en plein combat', '   forbidden mid-fight'),
    ('M_AUCUNE_PIERRE_MAGIQUE', 'Aucune Pierre Magique.', 'No Magic Stones.'),
    ('M_UNE_PIERRE_SE', "Une Pierre se desintegre a l'usage.  [A-Z] utiliser  [I/ESC] fermer", 'A Stone crumbles when used.  [A-Z] use  [I/ESC] close'),
    ('M_LE_PREMIER_COUP', 'Le premier coup a ete donne.', 'The first blow was struck.'),
    ('M_PIERRE_ABSENTE', 'Choix indisponible.', 'Choice unavailable.'),
    ('M_LA_PIERRE_DE', 'La Pierre de %s se desintegre.', 'The %s Stone crumbles.'),
    ('M_VOUS_FUYEZ_ELLE', 'Vous fuyez : elle vous blesse au passage.', 'You flee: it wounds you on the way.'),
    ('M_CHANCEUX', 'Chanceux !', 'Lucky!'),
    ('M_MALCHANCEUX', 'Malchanceux !', 'Unlucky!'),
    # L'assaut ne dit plus que son numero : les deux jets s'ecrivent en clair
    # sur les deux lignes suivantes, ou le joueur voit les des au lieu d'un
    # total tout fait. Les 39 octets rendus par l'ancienne ligne de force ont
    # paye les trois messages neufs, catalogue a taille constante.
    ('M_ASSAUT_N', 'ASSAUT %u', 'ROUND %u'),
    # Les deux etiquettes du jet, alignees sur la meme largeur dans chaque
    # langue : "Vous :" et "Lui  :" font six caracteres, "You:" et "It :"
    # quatre. Sans cet alignement les deux totaux ne se comparent pas d'un
    # coup d'oeil, et c'est toute l'affaire d'un assaut.
    ('M_JET_VOUS', 'Vous :', 'You:'),
    ('M_JET_LUI', 'Lui  :', 'It :'),
    ('M_VOUS_AVEZ_CHACUN', 'Vous avez chacun esquive.', 'You have each dodged.'),
    ('M_VOUS_L_AVEZ', "Vous l'avez blesse", 'You have wounded it'),
    ('M_ELLE_VOUS_A', 'Elle vous a blesse', 'It has wounded you'),
    ('M_K_ENGAGER', 'engager', 'engage'),
    # Raccourcis de "encaisser le coup" et "porter le coup" : la ligne du
    # dessus vient de dire qui a blesse qui, et les huit caracteres rendus
    # sont exactement ce qui manquait a l'enjeu ci-dessous pour tenir dans les
    # 80 colonnes a cote de FUIR.
    ('M_K_ENCAISSER', 'encaisser', 'take it'),
    ('M_K_FRAPPER', 'frapper', 'strike'),
    ('M_K_CHANCE', 'tenter la Chance', 'test your Luck'),
    # L'enjeu, et non la seule touche. "Tentez votre Chance" ne dit pas ce
    # qu'on parie : un point de CHANCE contre une blessure qui passe de 2 a 4,
    # ou qui retombe a 1. Le premier nombre est le sort du Chanceux, le second
    # celui du Malchanceux. Commence par une espace : il s'ecrit juste apres
    # la touche C en video inverse.
    # Largeur : 42 caracteres au plus (CHANCE a deux chiffres, blessures a un
    # seul -- le corpus ne connait que MD 3 et MD 4). Avec " ESPACE  encaisser "
    # et " F  fuir ", la ligne fait 79 colonnes, la derniere qu'on puisse
    # ecrire sans faire defiler l'ecran.
    ('M_K_ENJEU',
     ' Tentez votre Chance (CHANCE %u) : %u ou %u',
     ' Test your Luck (LUCK %u): %u or %u'),
    ('M_K_SUIVANT', 'assaut suivant', 'next round'),
    ('M_K_FUIR', 'fuir', 'flee'),
    ('M_K_SAC', 'sac a dos', 'backpack'),
    ('M_K_IMAGE', 'image', 'picture'),
    ('M_K_CONTINUER', 'continuer', 'continue'),
    ('M_DEGATS', '  -%u END', '  -%u STA'),
    ('M_TOUCHES', 'ESPACE=VUE  A-Z=CHOIX  I=SAC  M=CARTE  Q=QUITTER', 'SPACE=VIEW  A-Z=CHOICE  I=BAG  M=MAP  Q=QUIT'),
    ('M_JET_CONTRE', 'Vous jetez : %u, contre %u.', 'You roll: %u, against %u.'),
    ('M_S_EFFONDRE', "%s s'effondre.", '%s collapses.'),
    ('M_HELPFR', 'TEXTFR/HELPFR', 'TEXTEN/HELPEN'),
    ('M_FICHIER_D_AIDE', "Fichier d'aide introuvable.", 'Help file not found.'),
    ('M_VOTRE_ENDURANCE_EST', 'Votre ENDURANCE est tombee a zero.', 'Your STAMINA has fallen to zero.'),
    ('M_ESPACE_RECOMMENCER', '[ESPACE] recommencer', '[SPACE] start again'),
    ('M_FEUILLE_D_AVENTURE', "FEUILLE D'AVENTURE", 'ADVENTURE SHEET'),
    ('M_HABILETE_DE', 'HABILETE  %2u   (1 de + 6)', 'SKILL    %2u   (1 die + 6)'),
    ('M_ENDURANCE_DES', 'ENDURANCE %2u   (2 des + 12)', 'STAMINA  %2u   (2 dice + 12)'),
    ('M_CHANCE_DE', 'CHANCE    %2u   (1 de + 6)', 'LUCK     %2u   (1 die + 6)'),
    ('M_UNE_EPEE_UNE', "Une epee, un justaucorps de cuir, un sac a dos, %u Pieces d'Or.", 'A sword, a leather jerkin, a backpack, %u Gold Pieces.'),
    ('M_AUCUN_DE_CES', 'Aucun de ces trois totaux ne pourra depasser sa valeur de depart.', 'None of these three scores may ever rise above its start value.'),
    ('M_ESPACE_ENTRER_DANS', '[ESPACE] entrer dans le Marais', '[SPACE] enter the Swamp')
,
    ('M_CHOISISSEZ_PIERRES',
     'CHOISISSEZ VOS PIERRES MAGIQUES -- il en reste %u a prendre',
     'CHOOSE YOUR MAGIC STONES -- %u left to take'),
    ('M_PRENDRE_UNE_PIERRE',
     'Vous pouvez prendre plusieurs fois la meme.  [A-Z] prendre',
     'You may take the same one several times.  [A-Z] take'),
    ('M_TENTEZ_VOTRE_CHANCE',
     'Le sort en decide. [ESPACE] Tentez votre Chance (CHANCE %u)',
     'Fate decides. [SPACE] Test your Luck (LUCK %u)'),
    ('M_JET_DE_CHANCE',
     'Vous jetez les deux des : %u, contre une CHANCE de %u.',
     'You roll two dice: %u, against a LUCK of %u.'),
    ('M_MORT_RECOMMENCER',
     '[R] recommencer une aventure  [L] reprendre une sauvegarde  [Q] quitter',
     '[R] start a new adventure  [L] resume a saved game  [Q] quit to ProDOS'),
    # Le jet de des VISIBLE de la ligne ED. Deux messages, et deux seulement :
    # la prose de la page est encore a l'ecran au-dessus et dit deja ce que le
    # de coute ("lancez un de et perdez autant de points d'ENDURANCE"), donc
    # l'invite n'a pas a le repeter et le resultat n'a pas a nommer la
    # caracteristique. C'est ce qui evite huit messages (quatre caracs fois
    # gain ou perte) ; la Feuille d'Aventure de la ligne 1 dit le reste.
    ('M_LANCEZ_LES_DES',
     'Le sort en decide. [ESPACE] lancer les des',
     'Fate decides. [SPACE] roll the dice'),
    ('M_VOUS_JETEZ',
     'Vous jetez : %u.',
     'You roll: %u.'),
    # La page des sauvegardes : dix emplacements, chacun sous le titre de la
    # page ou la partie s'est arretee -- c'est ce qui permet de se situer dans
    # le Marais avant de reprendre. [S] et [L] la ferment comme ils l'ouvrent.
    ('M_SAUVEGARDES',
     'SAUVER -- [0-9] ecrire dans un emplacement   [S/ESC] retour',
     'SAVE -- [0-9] write to a slot   [S/ESC] back'),
    ('M_CHARGEMENTS',
     'REPRENDRE -- [0-9] charger un emplacement   [L/ESC] retour',
     'RESUME -- [0-9] load a slot   [L/ESC] back'),
    ('M_VIDE', '-- vide --', '-- empty --'),
    ('M_SAUVE_OK', 'Partie sauvee.', 'Game saved.'),
    ('M_SAUVE_ERREUR', 'Echec de la sauvegarde.', 'Save failed.'),
    ('M_CHARGE_ERREUR', 'Emplacement vide ou fichier corrompu.', 'Empty slot or corrupt file.'),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, required=True)
    args = ap.parse_args()

    header = ["/* Genere par SCOSWAMP.MORE/TOOLS/build_messages.py -- ne pas editer.",
              " * L'ordre suit MSGFR / MSGEN sur le disque. */",
              "",
              "#ifndef MESSAGES_H",
              "#define MESSAGES_H",
              "",
              "enum {"]
    header += [f"    {name}," for name, _, _ in MESSAGES]
    header += ["    MSG_COUNT",
               "};",
               "",
               "/* La taille du tampon vient d'ici, pas de messages.c : ecrite a la",
               " * main elle etait a la fois fausse et genereuse -- 1408 octets pour",
               " * un catalogue qui en demandait 1100, dans un binaire ou il en",
               " * restait 215 de libres. La marge de 32 laisse la place a une",
               " * traduction un peu plus longue sans toucher au code. */",
               f"#define MSG_BYTES {max(len(m[1]) for m in MESSAGES) and (max(sum(len(m[i]) + 1 for m in MESSAGES) for i in (1, 2)) + 32)}",
               "",
               "/* Charge le catalogue de la langue voulue. Rend 0 si le fichier manque",
               " * ou ne contient pas MSG_COUNT lignes -- mieux vaut un ecran vide",
               " * qu'un catalogue decale d'une ligne. */",
               "int  messages_load(int english);",
               "char* msg(int id);",
               "",
               "#endif /* MESSAGES_H */",
               ""]
    (args.root / "SCOSWAMP" / "SRC" / "messages.h").write_text("\n".join(header), encoding="utf-8")

    for suffix, index in (("FR", 1), ("EN", 2)):
        lines = [m[index] for m in MESSAGES]
        (args.root / "SCOSWAMP" / f"TEXT{suffix}" / f"MSG{suffix}.TXT").write_text(
            "\n".join(lines) + "\n", encoding="utf-8")

    longest = max(len(m[1]) for m in MESSAGES)
    total = max(sum(len(m[i]) + 1 for m in MESSAGES) for i in (1, 2))
    print(f"{len(MESSAGES)} messages ; {total} octets pour la langue la plus longue ; "
          f"ligne la plus longue {longest}")


main()
