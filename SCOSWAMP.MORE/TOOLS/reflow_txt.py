#!/usr/bin/env python3
"""Remet les pages TXT de SCOSWAMP au format attendu par le moteur.

  T  <id> <Titre>     titre de scene, une seule ligne, barre inversee ligne 1
  V  <cible> [<page> ...]  "si vous y etes deja venu, rendez-vous au <cible>".
                      Doit preceder tout le reste, qu'un detour annule. Les
                      numeros suivants sont les AUTRES pages de la meme
                      clairiere (hub, variantes, revisite) : le detour joue
                      des que l'une d'elles, ou la cible, a ete vue
  <corps>             replie a 78 colonnes, tient dans les lignes 2 a 20 ;
                      chaque paragraphe s'ouvre sur un retrait de trois
                      espaces, comme dans un livre imprime
  M  <hab> <end> <nom>  la creature de la clairiere
  MD <n>              ses coups coutent n ENDURANCE (defaut 2)
  MS <n>              le combat cesse a n ENDURANCE (defaut 0)
  MV <id>             le dernier adversaire tombe : la page envoie en <id>
                      sans repasser par les choix
  MI <page>           son portrait de bataille est le B<page>.RLE d'une
                      AUTRE page : le disque n'en range qu'un par page,
                      et une file peut melanger les especes (les deux
                      Loups du 120 empruntent le B224, leur Maitre garde
                      le B120). Sans MI, l'image est celle de la page
  E  <CARAC> <delta>  effet applique en entrant dans la clairiere
  ED <CARAC> <+-ndes> jet de des visible : le signe dit gain ou perte, la
                      valeur absolue le nombre de des (1 ou 2)
  P  <PIERRE> <n>     Pierres Magiques recues
  PC <n> <cats>       n Pierres a choisir parmi les categories N, B, M
  CF <id> <Titre>     la Fuite, quand la page l'autorise
  CL <ok> <ko> [<dok> <dko>]  Tentez votre Chance : ou l'on va, et ce que
                      chaque branche coute en ENDURANCE
  CP <PIERRE> <id> <Titre>  choix qui remet une Pierre Magique
  CU <PIERRE> <id> <Titre>  choix qui exige et consomme une Pierre
  C  <id> <Titre>     choix, rendus dans les 4 lignes du bas

Ne touche pas aux mots : seuls les retours a la ligne changent. Les lignes
purement decoratives (----- / =====) sautent, la barre de titre les remplace.
"""
import json, re, sys, textwrap
from pathlib import Path

# Le moteur laisse maintenant TOUJOURS la ligne 2 vide sous la barre de titre :
# le corps commence ligne 3 et s'arrete ligne 20. Le budget passe donc de 19 a
# 18 rangs. Les lignes vides du corps -- celles qui font les paragraphes --
# comptent dedans : wrap() les rend telles quelles, une seule a la fois.
BODY_ROWS   = 18   # lignes 3..20, la 2 etant la marge sous le titre
CHOICE_ROWS = 4    # lignes 21..24
MAX_FOES    = 3    # doit suivre MAX_FOES dans scoswamp.c
# Les trois bornes du moteur. Elles ne sont pas decoratives : ce qui les
# depasse est tronque A L'ECRAN, en silence, et c'est ici -- et nulle part
# ailleurs -- qu'on peut se payer la verification.
MAX_CHOICES  = 5     # doit suivre MAX_CHOICES dans scoswamp.c
FILE_BUFFER  = 1280  # doit suivre FILE_BUFFER_SIZE dans scoswamp.c
COL         = 39   # largeur d'une colonne de choix (2 par ligne)
WRAP        = 78
# Le retrait de premiere ligne de paragraphe. Trois espaces : sur une justif'
# de 78 colonnes, deux se voient a peine et quatre mangent un mot de plus par
# paragraphe sans rien ajouter a l'oeil. Il est COMPRIS dans les 78 -- la
# premiere ligne se remplit donc a 75 -- et le moteur n'en sait rien :
# classify_line range toute ligne qui ne commence pas par une lettre de
# directive en colonne 0 dans le corps, et render_scene la sort telle quelle.
INDENT      = "   "

RULE = re.compile(r"^[-=_*~#]{4,}\s*$")
# Les directives de jeu : ni titre, ni corps, ni choix. Elles ne se replient
# pas -- une ligne M coupee en deux ne veut plus rien dire.
# L'ordre de l'alternance FAIT FOI : `M` avant `MV` avalerait la ligne MV et
# wrap() la replierait dans le corps. Les deux lettres passent donc devant la
# lettre seule du meme prefixe, ici comme dans classify_line.
DIRECTIVE = re.compile(r"^(AC|MM|MF|MR|MD|MS|MI|MV|MB|MU|M|E0|ED|EH|E|PC|PD|PO|PS|PX|P|TR|CF|CP|CU|CI|CN|CV|CX|CG|CB|CT|CA|CL|CE|CS|DV|GU|GX|GA|G|VR|V)(?: |$)")
CHOICE = re.compile(r"^(C|CF|CP|CU|CI|CN|CV|CX|CG|CB|CT|CA|GU) ")
LEGACY_TITLE = re.compile(r"^\s*(\d{1,3})\s*:\s*(.+?)\s*$")

# ── Derivation des combats depuis la prose ──────────────────────────────────
#
# Les pages ecrivent deja le combat en toutes lettres : "BETE DU BASSIN
# HABILETE: 8 ENDURANCE: 10". Personne ne devrait avoir a le retaper en ligne
# `M`. La derivation se fait ICI, a la construction, et pas dans le moteur :
# l'Apple II n'a plus la place d'un analyseur de prose, la tolerance aux
# variations d'ecriture y serait fragile, et surtout le resultat serait
# invisible -- alors qu'ici il atterrit dans le fichier, lisible dans un diff.
#
# Regle de conduite : automatique quand c'est net, signale sinon. Une page
# qu'on ne sait pas lire garde sa prose et sort dans le rapport.

STATS = {
    "TEXTFR": (r"HABILETE", r"ENDURANCE"),
    "TEXTEN": (r"SKILL",    r"STAMINA"),
}
# Le nom est une suite de mots en capitales, precedee au besoin d'un ordinal
# ecrit normalement : le corpus dit "Premier LOUP HABILETE: 7 ... Deuxieme LOUP
# HABILETE: 6", et sans l'ordinal les deux loups portaient le meme nom dans le
# bandeau -- et "Premier" restait orphelin dans la prose.
NAME = (r"((?:Premier|Premiere|Deuxieme|Troisieme|Second|Seconde|"
        r"First|Second|Third)?\s*"
        r"(?:[A-ZÀ-Ý][A-ZÀ-Ý'-]*\s+){0,3}[A-ZÀ-Ý][A-ZÀ-Ý'-]*)")
FLEE  = re.compile(r"\b(fuite|fuir|enfuir|flee|fleeing)\b", re.I)
DMG   = re.compile(r"\((\d+)\s*(?:au lieu de|instead of)\s*2\)", re.I)
STOP  = re.compile(r"(?:r[eé]duis\w*|reduce\w*)[^.]{0,30}?\b(?:a|to)\s+(\d+)", re.I)
# Une page qui tend des Pierres sans ligne PC : le moteur ne les donnera pas.
# La formulation varie trop (un chiffre, un nombre en lettres, une categorie
# nommee ou sous-entendue) pour deviner sans risque -- on signale.
# Une Pierre remise par le recit. Deux faux positifs a ecarter : la page qui
# rappelle celles "que Gayolard vous a confiees" (191) et celle ou l'on en
# LANCE une (282) -- dans les deux cas la Pierre change de main dans l'autre
# sens, ou pas du tout.
# Les verbes anglais comptent autant que les francais : sans eux la regle ne
# lisait que la moitie du corpus, et la page 173 -- Pompatarte ouvrant son
# coffret -- passait dans les deux langues, la ligne PC manquant aux deux.
# "notez / inscrivez / note / record" entrent avec eux : c'est la formule du
# livre pour une Pierre recue ("vous notez vos cinq Pierres de Magie sur votre
# Feuille d'Aventure"), et la phrase qui l'offre finit souvent avant elle.
STONES_GIVEN = re.compile(
    r"\b(?:donne|donnerai|offre|remet|prenez|prendre|choisissez|choisir"
    r"|notez|inscrivez|gives?|offers?|choose|note|record)\b"
    r"[^.]{0,80}?\b(?:Pierres?|Stones?)\b"
    r"(?![^.]{0,20}\b(?:desintegre|disintegrat))", re.I)
# Les Pierres qui partent dans l'autre sens : le heros paie le Chef des
# Brigands (128), remet ses Pierres inutilisees a Pompatarte (141), ou troque
# des objets chez le marchand de potions (150, dont la ligne TR est au 408).
STONES_NOT_GIVEN = re.compile(
    r"\b(?:confie[es]?|lancez|lance|depense[es]?|utilis\w+|echang\w+"
    r"|remettez|lui donner|lui donnez"
    r"|entrusted|throw|thrown|spent|used|exchang\w+|traded?"
    r"|give him|give her|hand over)\b", re.I)


def derive_combat(text, choices, lang):
    """Rend (texte_nettoye, directives, avertissements)."""
    hab, end = STATS[lang]
    # Le corpus ecrit le bloc de trois facons : "NOM HABILETE: 9 ENDURANCE: 6",
    # "NOM HABILETE : 5 / ENDURANCE : 17", et "NOM - HABILETE : 12 ...". Le
    # tiret separateur est la raison pour laquelle trois pages passaient au
    # travers.
    block = re.compile(NAME + r"\s*(?:[-–—]\s*)?" + hab + r"\s*:?\s*(\d+)\s*/?\s*"
                       + end + r"\s*:?\s*(\d+)")
    hits = list(block.finditer(text))
    if not hits:
        return text, [], []
    warnings = []
    if len(hits) > MAX_FOES:
        return text, [], [f"{len(hits)} adversaires, le moteur en gere "
                          f"{MAX_FOES} : page laissee en prose"]

    # "Parfois, vous les affronterez comme si elles n'etaient qu'un seul
    # monstre ; parfois, vous les combattrez une par une." Les deux rencontres
    # a plusieurs du Marais sont du second type : une ligne M par adversaire,
    # dans l'ordre de la page.
    directives = []
    for m in hits:
        name = " ".join(m.group(1).split())[:23]
        directives.append(f"M {int(m.group(2))} {int(m.group(3))} {name}")

    # Les blocs de stats sortent de la prose : le bandeau les affiche. On
    # retire de la fin vers le debut pour ne pas decaler les positions.
    for m in reversed(hits):
        text = text[:m.start()] + text[m.end():]
    text = text.replace("  ", " ").strip()
    text = re.sub(r"\s+([.,;:!?])", r"\1", text)

    d = DMG.search(text)
    if d: directives.append(f"MD {int(d.group(1))}")

    for cid, ctitle in choices:
        st = STOP.search(ctitle)
        if st:
            directives.append(f"MS {int(st.group(1))}")
            break

    return text, directives, warnings


# Les deux langues : le corpus anglais dit "Lucky" / "Unlucky". Sans elles,
# TEXTEN restait en choix libres pendant que TEXTFR passait au jet -- deux
# regles du jeu differentes selon la langue choisie.
LUCKY   = re.compile(r"\b(?:chanceux|lucky)\b", re.I)
UNLUCKY = re.compile(r"\b(?:malchanceux|unlucky)\b", re.I)
# "vous perdez 2 points d'ENDURANCE" -- le livre attache parfois un cout a une
# branche du jet, et il appartient a la TRANSITION, pas a la page d'arrivee :
# celle du 270 est atteinte depuis cinq pages, une seule fait perdre 2 points.
LOSS = re.compile(r"\b(?:perdez|perdrez|lose)\s+(\d+)\s*(?:points?\s*d[e']\s*ENDURANCE"
                  r"|STAMINA\s*points?)", re.I)


def branch_loss(text, unlucky):
    """Cout en ENDURANCE attache a la branche Chanceux ou Malchanceux."""
    for sentence in re.split(r"(?<=[.!?])\s+", text):
        has_un = UNLUCKY.search(sentence) is not None
        has_lu = LUCKY.search(sentence) is not None and not has_un
        if unlucky and not has_un:
            continue
        if not unlucky and not has_lu:
            continue
        m = LOSS.search(sentence)
        if m:
            return -int(m.group(1))
    return 0


def derive_luck(choices, body):
    """Une paire Chanceux / Malchanceux devient un jet que le moteur joue.

    Le livre ne propose pas ces deux issues, il ORDONNE le jet et annonce ce
    qui arrive dans chaque cas ; les laisser en choix libres revenait a
    demander au joueur de tirer lui-meme les des, et de tricher.
    """
    lucky = [c for c in choices if LUCKY.search(c[1]) and not UNLUCKY.search(c[1])]
    unlucky = [c for c in choices if UNLUCKY.search(c[1])]
    if len(lucky) != 1 or len(unlucky) != 1:
        return choices, None
    text = " ".join(body)
    dok = branch_loss(text, unlucky=False)
    dko = branch_loss(text, unlucky=True)
    line = "CL %03d %03d" % (lucky[0][0], unlucky[0][0])
    if dok or dko:
        line += " %d %d" % (dok, dko)
    rest = [c for c in choices if c not in lucky and c not in unlucky]
    return rest, line


# Les douze Pierres, dans les deux langues, telles que le corpus les nomme.
STONE_NAMES = {
    "FEU": "FEU", "FIRE": "FEU",
    "GLACE": "GLACE", "ICE": "GLACE",
    "ILLUSION": "ILLUSION",
    "AMITIE": "AMITIE", "FRIENDSHIP": "AMITIE",
    "CROISSANCE": "CROISSANCE", "GROWTH": "CROISSANCE",
    "BENEDICTION": "BENEDICTION", "BLESSING": "BENEDICTION",
    "TERREUR": "TERREUR", "FEAR": "TERREUR", "TERROR": "TERREUR",
    "FLETRISSURE": "FLETRISSURE", "FETRISSURE": "FLETRISSURE",
    "WITHERING": "FLETRISSURE",
    "MALEDICTION": "MALEDICTION", "CURSE": "MALEDICTION",
    "HABILETE": "HABILETE", "SKILL": "HABILETE",
    "ENDURANCE": "ENDURANCE", "STAMINA": "ENDURANCE",
    "CHANCE": "CHANCE", "LUCK": "CHANCE",
}
# "Utiliser une Pierre de Feu", "Use a Magic Fire Stone", "Pierre d'Amitie",
# "Throw an Ice Magic Stone" : le nom peut preceder ou suivre le mot Pierre.
STONE_IN_TITLE = re.compile(
    # "d Amitie" : le corpus ecrit parfois l'elision avec une espace au
    # lieu d'une apostrophe.
    r"\bPierres?\b(?:\s+Magiques?)?\s+(?:de\s+la\s+|de\s+|d[e']\s*|d\s+)([A-Za-zÀ-ÿ]+)"
    r"|\b([A-Za-z]+)\s+(?:Magic\s+)?Stone\b"
    r"|\bStone\s+of\s+([A-Za-z]+)\b", re.I)


def stone_of_title(title):
    """La Pierre qu'un choix depense, ou None."""
    m = STONE_IN_TITLE.search(title)
    if not m:
        return None
    word = next(g for g in m.groups() if g)
    key = (word.upper()
              .replace("É", "E").replace("È", "E").replace("Ê", "E"))
    return STONE_NAMES.get(key)


# Une liste de Pierres s'ecrit souvent en ellipse : "Une Pierre de Terreur /
# d'Illusion / Aucune de celles-ci". Les suivantes ne repetent pas le mot.
ELLIPSIS = re.compile(r"^(?:de\s+la\s+|de\s+|d[e']\s*)?([A-Za-zÀ-ÿ]+)\s*$", re.I)


def derive_stone_use(choices, already):
    """Un choix qui nomme une Pierre l'EXIGE et la consomme (ligne CU).

    Sans ca, 37 choix du corpus depensaient une Pierre sans toucher au sac, et
    rien n'empechait d'en lancer une qu'on n'avait pas.

    `already` dit si la page porte deja un CU : dans ce cas seulement, un titre
    qui n'est QU'un nom de Pierre est lu comme la suite de la liste. Hors de ce
    contexte la regle serait trop large -- "Illusion" peut etre un mot ordinaire.
    """
    rest, lines = [], []
    listing = already
    for cid, title in choices:
        stone = stone_of_title(title)
        if stone is None and listing:
            m = ELLIPSIS.match(title.strip())
            if m:
                key = (m.group(1).upper().replace("É", "E")
                       .replace("È", "E").replace("Ê", "E"))
                stone = STONE_NAMES.get(key)
        if stone:
            lines.append(f"CU {stone} {cid:03d} {title}")
            listing = True
        else:
            rest.append((cid, title))
    return rest, lines


# Une page qui annonce une perte de caracteristique doit l'appliquer : sans
# ligne E, "vous perdez 3 points d'HABILETE" n'etait que du decor.
# Le verbe qualifie la PHRASE ; les valeurs se lisent ensuite partout dedans.
# "vous perdez 3 points d'HABILETE et 1 point d'ENDURANCE" ne porte qu'un seul
# verbe pour deux effets, et le second passait a la trappe.
EFFECT_VERB = re.compile(
    r"\b(perdez|perdrez|coutent|coute|regagnez|gagnez|ajoutez"
    r"|lose|loses|cost|costs|regain|regains|gain|gains)\b", re.I)
# Les deux langues n'ordonnent pas pareil : "3 points d'HABILETE" contre
# "3 SKILL points". Et l'elision s'ecrit parfois avec une espace.
EFFECT_VALUE = re.compile(
    r"(\d+)\s*(?:points?\s*(?:d[e']\s*|d\s+|of\s+))?"
    r"(ENDURANCE|HABILETE|CHANCE|STAMINA|SKILL|LUCK)", re.I)
# Ce qui rend une perte conditionnelle ou deja prise en charge ailleurs.
# Ce qui empeche de deriver une perte seche. "supplementaire" n'en fait plus
# partie : il dit que la perte s'ajoute a une autre, pas qu'elle est
# conditionnelle -- et il bloquait le paragraphe 269, ou elle est bien seche.
EFFECT_GUARD = re.compile(
    r"\b(si|sinon|au lieu de|chaque|initial"
    r"|if|otherwise|instead|each)\b", re.I)
# "additional" est l'equivalent anglais de "supplementaire" : meme raison de
# ne pas l'y mettre.
CARAC = {"ENDURANCE": "ENDURANCE", "STAMINA": "ENDURANCE",
         "HABILETE": "HABILETE", "SKILL": "HABILETE",
         "CHANCE": "CHANCE", "LUCK": "CHANCE"}
# Les quatre mots que le moteur admet sur une ligne E, E0, CE ou ED. Ils
# restent en francais dans les deux corpus : c'est de la mecanique, pas du
# texte affiche -- et E0 n'en accepte que les trois premiers (pas d'OR ni de
# BONUS : c'est un total de depart qu'il deplace).
CARAC_WORDS = {"ENDURANCE", "HABILETE", "CHANCE", "OR", "BONUS"}
GAIN = ("regagnez", "gagnez", "ajoutez", "regain", "gain")


def derive_effects(body, directives):
    """Rend (lignes E, avertissements) pour les pertes annoncees par la page.

    Une perte prise dans une branche de jet (CL) ou dans une regle de combat
    (MD) est deja appliquee ailleurs : on ne la compte pas deux fois. Et une
    phrase qui porte "si", "sinon" ou "supplementaire" n'est pas une perte
    seche -- on la signale plutot que de la deviner.
    """
    # "ED " est dans la liste depuis que le jet de des existe : le de de la
    # page 093 est deja une perte d'ENDURANCE, et la deriver une seconde fois
    # en ligne E la ferait payer deux fois -- une fois seche, une fois au de.
    if any(d.startswith(("E ", "E0 ", "CE ", "CL ", "MD ", "ED "))
           for d in directives):
        return [], []
    lines, warns = [], []
    for sentence in re.split(r"(?<=[.!?])\s+", " ".join(body)):
        verb = EFFECT_VERB.search(sentence)
        if not verb:
            continue
        hits = EFFECT_VALUE.findall(sentence)
        if not hits:
            continue
        if EFFECT_GUARD.search(sentence):
            warns.append("perte de caracteristique sous condition, "
                         "a trancher a la main : " + " ".join(sentence.split())[:70])
            continue
        sign = "+" if verb.group(1).lower() in GAIN else "-"
        for n, carac in hits:
            lines.append(f"E {CARAC[carac.upper()]} {sign}{int(n)}")
    return lines, warns


# ── Le jet de des visible (ligne ED) ────────────────────────────────────────
#
# "jetez un de et perdez autant de points d'ENDURANCE que le chiffre obtenu."
# Sept pages le disent, a un mot pres, et une huitieme le dit pour de l'or.
# Sans ligne ED la phrase n'etait que du decor : le joueur lisait qu'il devait
# lancer un de, et rien ne se passait.
#
# Le corpus ecrit le jet de cinq facons -- "jetez un de", "lancez 1 de",
# "Lancez un de;", "roll a die", "Roll one die" -- d'ou l'alternance sur le
# determinant, chiffre compris.
DICE_CAST = re.compile(
    r"\b(?:lancez|lancer|jetez|jeter|roll)\s+"
    r"(?P<n>un|une|1|a|one|deux|2|two)\s+d(?:es?|ice|ie)\b", re.I)
DICE_N = {"un": 1, "une": 1, "1": 1, "a": 1, "one": 1,
          "deux": 2, "2": 2, "two": 2}
# Un jet COMPARE a une caracteristique n'est pas un ED : c'est le test 2d6 des
# pages 091, 257 et 377, que le format ne sait pas encore ecrire. Le deriver en
# ED ferait perdre les points au lieu de les mettre en jeu -- l'inverse de ce
# que dit le livre.
DICE_COMPARE = re.compile(
    r"\b(?:inferieur\w*|superieur\w*|egal|egale|contre"
    r"|less|equal|greater|higher|lower|against)\b", re.I)
# "Tentez votre CHANCE. Test: lancez 2 des (2d6). Si total <= CHANCE..." :
# quatre pages ecrivent le jet de Chance en toutes lettres. C'est un CL ou un
# CE, jamais un ED -- le deriver en ED ferait perdre des points de CHANCE au
# lieu de les mettre en jeu. La comparaison y est parfois ecrite "<=", que
# DICE_COMPARE ne peut pas voir : c'est le vocabulaire du jet qui la trahit.
LUCK_MARK = re.compile(
    r"\b(?:tentez\s+votre\s+chance|chanceux|malchanceux"
    r"|test\s+your\s+luck|lucky|unlucky)\b", re.I)
# La forme du 044 : "le plus petit des deux chiffres obtenus ; en cas de
# double, la somme". Ni 1d6 ni 2d6, et une seule page la porte : on la signale
# et on la laisse en prose plutot que d'ajouter un champ au format pour elle.
# "smaller" et pas seulement "smallest" : l'anglais du 044 dit "the smaller of
# the two numbers" la ou le francais dit "le plus petit des deux chiffres", et
# c'est le recoupement FR/EN qui a montre le trou -- l'anglais derivait un
# `ED ENDURANCE -2` que le francais refusait, deux regles pour une page.
DICE_ODD = re.compile(
    r"\b(?:plus\s+petit|plus\s+grand|double|smaller|larger"
    r"|smallest|largest|lowest|highest)\b", re.I)
DICE_GOLD = re.compile(r"\b(?:pieces?\s+d[e']?\s*or|gold\s+pieces?)\b", re.I)
DICE_LOSS = re.compile(
    r"\b(?:perd\w*|retranch\w*|otez|oter|deduis\w*|reduis\w*"
    r"|lose|loses|lost|losing|deduct|subtract|reduce)\b", re.I)
DICE_GAIN = re.compile(
    r"\b(?:gagnez|regagnez|ajoutez|recuperez|recevez"
    r"|gain|gains|regain|add|receive|recover)\b", re.I)
DICE_CARAC = re.compile(r"\b(ENDURANCE|HABILETE|CHANCE|STAMINA|SKILL|LUCK)\b")


def derive_dice(body, directives):
    """Rend (ligne ED, avertissements) pour le jet de des annonce par la page.

    Le livre ORDONNE le jet ; le laisser en prose revenait a demander au joueur
    de le lancer lui-meme, et de se croire sur parole. La cible se cherche
    d'abord dans la phrase du jet, et seulement ensuite chez ses voisines :
    la page 093 nomme l'ENDURANCE dans la meme phrase, la 135 parle des Pieces
    d'Or dans la precedente, et elargir d'emblee ferait attraper au 093 le
    "deduisez 2 points d'HABILETE" qui vise le MONSTRE, pas le heros.
    """
    has_cs = any(d.startswith("CS ") for d in directives)
    if any(d.startswith("ED ") for d in directives):
        return None, []
    # Le jet de Chance a deja sa directive : la page ne parle pas d'un de de
    # plus, elle parle de celui-la.
    if any(d.startswith(("CL ", "CE ")) for d in directives):
        return None, []
    sentences = re.split(r"(?<=[.!?])\s+", " ".join(body))
    for i, sentence in enumerate(sentences):
        m = DICE_CAST.search(sentence)
        if not m:
            continue
        short = " ".join(sentence.split())[:70]
        # Les gardes se lisent sur la FENETRE et non sur la seule phrase du
        # jet : "Lancez deux des." tient en une phrase, et c'est la suivante
        # qui dit contre quoi (pages 091, 257, 377).
        window = " ".join(sentences[max(0, i - 1):i + 2])
        if DICE_ODD.search(window):
            return None, ["jet de des d'une forme que ED ne sait pas ecrire "
                          "(minimum, double) : " + short]
        if LUCK_MARK.search(window):
            return None, ["jet de Chance ecrit en prose : c'est un CL ou un "
                          "CE, pas un ED, et la page n'en a aucun : " + short]
        if DICE_COMPARE.search(window):
            return None, [] if has_cs else [
                          "jet de des COMPARE a une caracteristique : ce n'est "
                          "pas un ED, il manque la ligne CS : " + short]
        n = DICE_N[m.group("n").lower()]
        # La phrase du jet d'abord, ses voisines ensuite, et jamais l'inverse.
        for scope in (sentence, window):
            if DICE_GOLD.search(scope):
                # Un de d'or est toujours un gain : on ne paie pas au hasard.
                return f"ED OR +{n}", []
            c = DICE_CARAC.search(scope)
            if c:
                carac = CARAC[c.group(1).upper()]
                if DICE_LOSS.search(scope):
                    return f"ED {carac} -{n}", []
                if DICE_GAIN.search(scope):
                    return f"ED {carac} +{n}", []
                return None, ["jet de des sur %s sans verbe de gain ni de "
                              "perte, a trancher a la main : %s" % (carac, short)]
        return None, ["jet de des dont on ne voit pas la cible : " + short]
    return None, []


# ── L'enchainement de victoire (ligne MV) ───────────────────────────────────
#
# Trente pages a ligne M offraient, apres le dernier adversaire tombe, un
# unique choix -- "Vous avez tue le Maitre", "Le Geant flechit" -- que le
# joueur devait prendre lui-meme alors qu'il n'avait pas d'autre issue. La
# ligne MV le supprime et rend au budget des choix la ligne d'ecran qu'il
# mangeait, sur quatre disponibles.
#
# La regle est le COMPTE, pas le vocabulaire : sur une page a combat, une fois
# la Fuite sortie en ligne CF, un choix unique restant EST la suite de la
# victoire -- il n'y a pas d'autre facon de quitter la clairiere. Le
# vocabulaire ne sert qu'a signaler ce qui n'est pas net.
VICTORY = re.compile(
    r"\b(tue\w*|vaincre|vainqu\w*|abattu\w*|abattez|victoire|terrass\w*"
    r"|detrui\w*|reduis\w*|flechit|survivez"
    r"|kill\w*|defeat\w*|slay|slain|beat|reduce\w*|falters|survive"
    r"|victorious|victory|destroy\w*|strike)\b", re.I)
# "En cas de mort : votre cadavre sert d'engrais." Un choix que le joueur ne
# peut jamais prendre : le moteur tient la mort lui-meme (run_combat rend 0,
# load_scene appelle game_over). Il occupe une ligne d'ecran pour rien.
DEATH_CHOICE = re.compile(
    r"\b(?:en\s+cas\s+de\s+mort|si\s+vous\s+mourez|si\s+vous\s+etes\s+tue"
    r"|in\s+case\s+of\s+death|if\s+you\s+die|if\s+you\s+are\s+killed)\b", re.I)


def derive_win(choices, directives):
    """Rend (choix_restants, ligne MV, avertissements) pour une page a combat."""
    if not any(d.startswith("M ") for d in directives):
        return choices, None, []
    if any(d.startswith("MV ") for d in directives):
        return choices, None, []
    warns = []
    rest = []
    for cid, ctitle in choices:
        if DEATH_CHOICE.search(ctitle):
            # On le retire, mais on le DIT : c'est du texte en moins, et le
            # corpus appartient a quelqu'un d'autre.
            warns.append("choix de mort retire, le moteur tient la mort "
                         "lui-meme : C %03d %s" % (cid, ctitle))
            continue
        rest.append((cid, ctitle))
    if len(rest) == 1:
        cid, ctitle = rest[0]
        if not VICTORY.search(ctitle):
            warns.append("choix unique apres le combat, pris pour la suite de "
                         "la victoire sans que son titre le dise : %s" % ctitle)
        return [], "MV %03d" % cid, warns
    if len(rest) > 1:
        warns.append("%d issues apres le combat : la victoire n'en ouvre pas "
                     "qu'une, page laissee en choix (%s)"
                     % (len(rest), " / ".join(t for _, t in rest)))
    return rest, None, warns


# Le filet, et RIEN DE PLUS qu'un filet. derive_effects ne derive que des
# pertes seches, et abandonne toute page qui porte deja un E : les gains du
# livre ("recuperez 2 points d'ENDURANCE", "vous reprenez des forces") lui
# echappent presque tous, et une douzaine de pages annoncaient un gain que le
# moteur ne donnait pas. Les POSER automatiquement serait pire que le mal --
# le meme verbe sert a une promesse ("il vous rendra vos forces si vous
# revenez"), a un rappel et a un gain reel -- donc on se contente de le DIRE,
# et c'est une main humaine qui tranche.
GAIN_PROSE = re.compile(
    r"\b(?:recuperez|reprenez|regagnez|rendent|rend|redonne\w*|ajoutez"
    r"|recover|recovers|restore\w*|regain|regains|add)\b", re.I)


def warn_mute_luck(body, directives):
    """Signale une page qui ORDONNE un jet de Chance sans directive pour le jouer.

    "Tentez votre CHANCE. Si vous etes malchanceux, cette contusion vous coute
    1 point d'ENDURANCE." Sans CL ni CE, le jet n'est jamais joue et la perte
    tombe de toute facon, sur le chanceux comme sur l'autre : le contraire de
    ce que la page dit. Deux pages sont dans ce cas (058, 190), et c'est le
    meme oubli que celui des lignes ED -- une mecanique restee en prose.
    """
    if any(d.startswith(("CL ", "CE ")) for d in directives):
        return []
    text = " ".join(body)
    if not (LUCKY.search(text) and UNLUCKY.search(text)):
        return []
    return ["jet de Chance annonce par la prose et aucune ligne CL ou CE "
            "pour le jouer : l'effet tombe sur les deux branches"]


def warn_missing_gain(body, directives):
    """Signale une page qui promet un gain sans ligne E pour le donner."""
    # Le garde ne compte PAS "CL " : le jet de Chance porte ses propres deltas
    # d'ENDURANCE, mais rien n'empeche la page d'annoncer en plus un gain a
    # l'entree -- c'est le cas du 289, que derive_effects abandonnait pour
    # cette exacte raison et qui n'apparaissait donc nulle part.
    if any(d.startswith(("E ", "ED ", "CE ", "P ", "PC ")) for d in directives):
        return []
    for sentence in re.split(r"(?<=[.!?])\s+", " ".join(body)):
        if GAIN_PROSE.search(sentence) and EFFECT_VALUE.search(sentence):
            return ["gain annonce par la prose et aucune ligne E pour le "
                    "donner : " + " ".join(sentence.split())[:70]]
    return []


# "Si vous y etes deja venu, rendez-vous au 142. Sinon, lisez ce qui suit."
# Le livre confie ce comptage au joueur ; le moteur le tient, donc la phrase
# n'a plus rien a faire dans le texte -- la laisser demanderait au joueur de
# faire a la main ce que la page vient de faire pour lui.
#
# Tous les blancs sont des \s+ : la phrase enjambe une fin de ligne dans sept
# pages sur quatorze, et une version a espace litteral n'en voyait que la
# moitie -- des deux cotes differents, ce qui a saute aux yeux au recoupement
# FR/EN. Les cesures du scan ont par ailleurs mange des espaces ("au238",
# "rendez- vous").
REVISIT = re.compile(
    r"\s*(?:Si\s+vous\s+(?:y\s+)?etes\s+deja\s+venu[^.]*?,\s*rendez-\s*vous\s*au\s*(\d+)\."
    r"(?:\s*(?:Sinon|Autrement)[^.]*\.)?"
    r"|If\s+you(?:'ve|\s+have)\s+been\s+[^.]*?before,\s*go\s+to\s*(\d+)\."
    r"(?:\s*Otherwise[^.]*\.)?)")

# La meme regle sans son but : il est porte par un choix, que le joueur devait
# prendre lui-meme (N118).
REVISIT_MUTE = re.compile(
    r"\s*(?:Si\s+vous\s+y\s+etes\s+deja\s+venu,\s*ignorez\s+ce\s+passage\."
    r"|If\s+you(?:'ve|\s+have)\s+been\s+here\s+before,\s*ignore\s+this\s+passage\.)")
REVISIT_CHOICE = re.compile(r"deja\s+venu|already\s+been|been\s+here\s+before", re.I)


def _cut(text, m):
    """Retire la phrase et recolle sans laisser la double espace du trou."""
    return text[:m.start()].rstrip() + " " + text[m.end():].lstrip()


def derive_revisit(body, choices, directives):
    """Rend (corps, choix, ligne V) pour une clairiere a description double."""
    if any(d.startswith(("V ", "VR ", "AC")) for d in directives):
        return body, choices, None
    text = "\n".join(body)
    m = REVISIT.search(text)
    if m:
        target = int(m.group(1) or m.group(2))
        return _cut(text, m).split("\n"), choices, f"V {target:03d}"
    m = REVISIT_MUTE.search(text)
    if not m:
        return body, choices, None
    for i, (cid, ctitle) in enumerate(choices):
        if REVISIT_CHOICE.search(ctitle):
            return _cut(text, m).split("\n"), \
                   choices[:i] + choices[i+1:], f"V {cid:03d}"
    return body, choices, None


def derive_flee(choices, directives):
    """Transforme le choix de Fuite en ligne CF. Rend (choix_restants, cf)."""
    if any(d.startswith("CF ") for d in directives):
        return choices, None
    for i, (cid, ctitle) in enumerate(choices):
        if FLEE.search(ctitle):
            return choices[:i] + choices[i+1:], f"CF {cid:03d} {ctitle}"
    return choices, None


def parse(path):
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    title, body, choices, directives = None, [], [], []
    for i, l in enumerate(lines):
        if DIRECTIVE.match(l):
            directives.append(l.rstrip())
        elif l.startswith("T ") and title is None:
            rest = l[2:].strip()
            m = re.match(r"^(\d{1,3})\s+(.*)$", rest)
            title = m.group(2).strip() if m else rest
        elif l.startswith("C "):
            m = re.match(r"^(\d{1,3})\s+(.*)$", l[2:].strip())
            if m:
                choices.append((int(m.group(1)), m.group(2).strip()))
        elif RULE.match(l):
            continue
        elif title is None and not body and LEGACY_TITLE.match(l):
            title = LEGACY_TITLE.match(l).group(2)
        else:
            body.append(l)
    while body and not body[-1].strip(): body.pop()
    while body and not body[0].strip(): body.pop(0)
    return title, body, choices, directives

def _w(text, width, indent=INDENT):
    # Les blancs multiples sont ramenes a un : textwrap les conserve, et le
    # trou laisse par une phrase retiree se voyait a l'ecran.
    text = re.sub(r"\s+", " ", text)
    # break_on_hyphens=False : sinon "spider-shaped" est coupe en deux mots et
    # la ligne se termine sur un tiret orphelin. break_long_words=False : aucun
    # mot n'est jamais casse ; le controle de largeur ci-dessous le verifierait.
    # initial_indent : textwrap DECOMPTE le retrait de la largeur, donc la
    # premiere ligne se remplit a `width - len(indent)` et le mot de trop
    # descend tout seul a la ligne suivante. Coller le retrait apres coup
    # aurait pousse cette ligne a 81 colonnes, et l'Apple II l'aurait
    # enroulee -- en silence, comme toujours.
    return textwrap.wrap(text, width, initial_indent=indent,
                         break_on_hyphens=False, break_long_words=False)

def deindent(body):
    """Retire le retrait canonique pose par la passe precedente.

    Sans ca, le format ne serait pas idempotent : la premiere ligne d'un
    paragraphe deja indente tomberait dans la branche "deja mise en forme" de
    wrap(), le paragraphe se figerait sur la coupe du jour, et les lignes
    suivantes -- elles, non indentees -- se replieraient a part. Le retrait est
    donc de la MISE EN FORME et rien d'autre : on le pose a l'ecriture et on
    l'oublie a la relecture, exactement comme une fin de ligne.

    Seule une premiere ligne de paragraphe est concernee, et seulement avec le
    retrait exact : la ligne de menu du N000 (" [A-E] - Choisir ...") commence
    par UNE espace, garde donc son alignement fait main.
    """
    out, start = [], True
    for l in body:
        if start and l.startswith(INDENT) and not l[len(INDENT):len(INDENT)+1].isspace():
            l = l[len(INDENT):]
        out.append(l)
        start = not l.strip()
    return out

def wrap(body, width=WRAP):
    out, para = [], []
    for l in deindent(body):
        if not l.strip():
            if para: out += _w(" ".join(para), width); para = []
            if out and out[-1] != "": out.append("")
        elif l[0] in " \t":
            # Ligne indentee = deja mise en forme (une liste de commandes, un
            # tableau) : on la garde telle quelle, la replier la collerait en
            # un paragraphe illisible.
            if para: out += _w(" ".join(para), width); para = []
            out.append(l.rstrip()[:width])
        else:
            para.append(l.strip())
    if para: out += _w(" ".join(para), width)
    while out and out[-1] == "": out.pop()
    return out

def choice_rows(choices):
    """Simule le rendu : 2 choix par ligne s'ils tiennent tous deux en COL."""
    i, rows = 0, 0
    while i < len(choices):
        a = 3 + len(choices[i][1])
        if i + 1 < len(choices) and a <= COL and 3 + len(choices[i+1][1]) <= COL:
            i += 2
        else:
            i += 1
        rows += 1
    return rows

def render(scene_id, title, body, choices, directives, mechanics_order=None):
    if mechanics_order is not None:
        # Reflow only the prose. Preserve the relative order of effects and
        # choices, including conditional choices and the flee directive.
        return "\n".join([f"T {scene_id:03d} {title}"] +
                [line for line in mechanics_order if line.startswith(("V ", "VR ", "AC"))] +
                [""] + body + [""] +
                [line for line in mechanics_order if not line.startswith(("V ", "VR ", "AC"))]) + "\n"
    out = [f"T {scene_id:03d} {title}"]
    # La ligne V passe devant tout : le moteur court-circuite la page des
    # qu'il la lit, et une ligne E placee avant elle serait appliquee pour
    # rien -- une seconde fois, en fait, puisqu'on est deja passe par la.
    out += [d for d in directives if d.startswith(("V ", "VR ", "AC"))]
    directives = [d for d in directives if not d.startswith(("V ", "VR ", "AC"))]
    out += [""]
    out += body
    out.append("")
    # ED passe devant les autres directives -- devant les lignes M, surtout.
    # L'ORDRE D'EXECUTION n'en depend pas : load_scene joue le de avant le
    # combat quelle que soit la position de la ligne, parce que c'est lui qui
    # ordonne, pas le fichier. C'est pour l'oeil : sur la page 261 le livre
    # fait tomber le de avant que l'Araignee attaque, et le fichier doit se
    # lire dans cet ordre-la.
    out += [d for d in directives if d.startswith("ED ")]
    out += [d for d in directives if not d.startswith("ED ")]
    out += [f"C {cid:03d} {ctitle}" for cid, ctitle in choices]
    return "\n".join(out) + "\n"

def words(seq):
    return " ".join(" ".join(seq).split())

def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("")
    # Le chemin attendu est le dossier SCOSWAMP, qui contient TEXTFR et TEXTEN :
    # passer TEXTFR lui-meme faisait parcourir zero fichier, et le script
    # repondait "0 / 0" comme si tout allait bien.
    if not (root / "TEXTFR").is_dir() or not (root / "TEXTEN").is_dir():
        sys.exit(f"usage : reflow_txt.py <dossier SCOSWAMP> [--apply] [--derive]\n"
                 f"{root or '(rien)'} ne contient pas TEXTFR et TEXTEN : aucun fichier ne serait lu.")
    apply = "--apply" in sys.argv
    derive = "--derive" in sys.argv
    found = {}          # (lang, id) -> directives, pour le recoupement FR/EN
    mus = {}            # (lang, id) -> lignes MU, pour le croisement avec carte.json
    problems, changed = [], 0
    for lang in ("TEXTFR", "TEXTEN"):
        for f in sorted((root / lang).rglob("N*.TXT")):
            sid = int(f.stem[1:])
            title, body, choices, directives = parse(f)
            if title is None:
                problems.append(f"{f}: pas de titre"); continue

            if derive and not any(d.startswith("M ") for d in directives):
                text, found_dirs, warns = derive_combat("\n".join(body), choices, lang)
                for w in warns:
                    problems.append(f"{f}: {w}")
                if found_dirs:
                    body = text.split("\n")
                    choices, cf = derive_flee(choices, found_dirs)
                    directives = found_dirs + ([cf] if cf else [])
            if derive:
                body, choices, rv = derive_revisit(body, choices, directives)
                if rv:
                    directives = [rv] + directives
            if derive and not any(d.startswith("CL ") for d in directives):
                choices, cl = derive_luck(choices, body)
                if cl:
                    directives = directives + [cl]
            if derive:
                # AVANT derive_effects : le de est deja une perte, et la
                # deriver une seconde fois en ligne E la ferait payer deux
                # fois. derive_effects abandonne toute page portant un ED.
                ed, dwarn = derive_dice(body, directives)
                if ed:
                    directives = directives + [ed]
                for w in dwarn:
                    problems.append(f"{f}: {w}")
            if derive:
                eff, ewarn = derive_effects(body, directives)
                directives = directives + eff
                for w in ewarn:
                    problems.append(f"{f}: {w}")
            if derive:
                for w in warn_missing_gain(body, directives):
                    problems.append(f"{f}: {w}")
                for w in warn_mute_luck(body, directives):
                    problems.append(f"{f}: {w}")
            if derive:
                has_cu = any(d.startswith("CU ") for d in directives)
                choices, cus = derive_stone_use(choices, has_cu)
                directives = directives + cus
            if derive:
                # EN DERNIER : la ligne MV se decide au COMPTE des choix qui
                # restent, donc une fois que la Fuite et les Pierres ont pris
                # les leurs.
                choices, mv, wwarn = derive_win(choices, directives)
                if mv:
                    directives = directives + [mv]
                for w in wwarn:
                    problems.append(f"{f}: {w}")
            if derive and not any(d.startswith("PC ") for d in directives) \
                     and not any(d.startswith("P ") for d in directives) \
                     and not any(d == "TR" for d in directives) \
                     and STONES_GIVEN.search(" ".join(body)) \
                     and not STONES_NOT_GIVEN.search(" ".join(body)):
                problems.append(f"{f}: une Pierre semble remise ici, mais la "
                                f"page n'a ni ligne PC ni ligne P")
            if derive and directives:
                # Tout enregistrer : c'est `mechanics` qui decide ensuite ce
                # qui compte. Filtrer ici avait rendu le recoupement aveugle
                # aux CU, CL et PC -- et il a laisse passer trois pages ou
                # l'anglais depensait une Pierre que le francais ne depensait
                # pas.
                found[(lang, sid)] = list(directives)
            w = wrap(body)
            if len(w) > BODY_ROWS:
                problems.append(f"{f}: corps {len(w)} lignes > {BODY_ROWS}")
            # Le moteur ne lit plus que l'INITIALE du mot de caracteristique
            # (carac_of, scoswamp.c) : quatre strcmp coutaient trop cher pour
            # distinguer ce qu'un octet distingue. La contrepartie est qu'une
            # faute de frappe y passe en silence -- "EDURANCE" serait lue
            # comme ENDURANCE, "OBJET" comme OR -- et c'est ici, du cote ou
            # l'on peut se payer une comparaison de chaines, qu'on la refuse.
            mus[(lang, sid)] = [d for d in directives if d.startswith("MU ")]
            if len(mus[(lang, sid)]) > 1:
                problems.append(f"{f}: plusieurs lignes MU, la derniere gagne")
            for d in directives:
                parts = d.split()
                # MU <NOM>.MB (theme de zone), MU +<NOM>.MB (surcouche), MU -
                # (silence). Le nom tient en 15 caracteres ProDOS et dans le
                # champ music_name[16] du moteur, qui tronque en silence ; et le
                # fichier doit exister, music_load echouant sans un mot.
                if parts[0] == "MU":
                    arg = parts[1] if len(parts) == 2 else ""
                    if not re.fullmatch(r"-|\+?[A-Z0-9]{1,12}\.MB", arg):
                        problems.append(f"{f}: ligne MU mal formee {d!r}")
                    elif arg != "-" and not (root / "MUSIC" / (arg.lstrip("+") + ".BIN")).exists():
                        problems.append(f"{f}: MU {arg} : pas de MUSIC/{arg.lstrip('+')}.BIN")
                # MI <page> : l'image empruntee doit exister, load_foe_image
                # retombant sans un mot sur celle de la page -- c'est-a-dire
                # sur le bug qu'on vient de corriger.
                if parts[0] in ("CG", "CB"):
                    maximum = 1 if parts[0] == "CB" else 255
                    valid = (len(parts) >= 4 and all(v.isdigit() for v in parts[1:3]) and
                             0 <= int(parts[1]) <= maximum and int(parts[2]) < 424)
                    if not valid:
                        problems.append(f"{f}: {parts[0]} attend valeur (0..{maximum}), destination et titre")
                    else:
                        pg = int(parts[2])
                        if not (root / lang / f"N{pg // 50 * 50:03}" / f"N{pg:03}.TXT").exists():
                            problems.append(f"{f}: {parts[0]} reference une page absente : {pg:03}")
                if parts[0] == "CT":
                    valid = (len(parts) >= 5 and all(v.isdigit() for v in parts[1:4]) and
                             0 <= int(parts[1]) <= int(parts[2]) <= 15 and int(parts[3]) < 424)
                    if not valid:
                        problems.append(f"{f}: CT attend min max (0..15), destination et titre")
                    else:
                        pg = int(parts[3])
                        if not (root / lang / f"N{pg // 50 * 50:03}" / f"N{pg:03}.TXT").exists():
                            problems.append(f"{f}: CT reference une page absente : {pg:03}")
                if parts[0] == "MM" and (len(parts) != 2 or parts[1] not in ("0", "1")):
                    problems.append(f"{f}: MM exige 0 ou 1")
                if parts[0] == "MF":
                    if len(parts) != 2 or not parts[1].isdigit() or not 0 <= int(parts[1]) <= 255:
                        problems.append(f"{f}: MF exige un nombre d’assauts entre 0 et 255")
                if parts[0] == "MR":
                    if len(parts) != 3 or not all(v.isdigit() and 0 < int(v) <= 255 for v in parts[1:]):
                        problems.append(f"{f}: MR exige gain et maximum entre 1 et 255")
                if parts[0] == "MI":
                    pg = int(parts[1]) if len(parts) == 2 and parts[1].isdigit() else -1
                    img = root / "DHGR" / ("N%03d" % (pg // 50 * 50)) / ("B%03d.RLE.BIN" % pg)
                    if pg < 0:
                        problems.append(f"{f}: ligne MI mal formee {d!r}")
                    elif not img.exists():
                        problems.append(f"{f}: MI {pg:03d} : pas de "
                                        f"DHGR/N{pg // 50 * 50:03d}/B{pg:03d}.RLE.BIN")
                if parts[0] in ("E", "E0", "CE", "ED") and len(parts) > 1 \
                        and parts[1] not in CARAC_WORDS:
                    problems.append(f"{f}: {parts[0]} sur un mot inconnu "
                                    f"{parts[1]!r} (attendu : "
                                    f"{', '.join(sorted(CARAC_WORDS))})")
                if parts[0] in ("CV", "CX"):
                    refs = parts[1].split(",") if len(parts) > 1 else []
                    valid = (len(parts) >= 4 and refs and
                             all(re.fullmatch(r"!?[0-9]+", v) and int(v.lstrip("!")) < 424 for v in refs) and
                             parts[2].isdigit() and int(parts[2]) < 424)
                    if not valid:
                        problems.append(f"{f}: CV/CX attend des pages separees par virgule (! = non visitee), une destination et un titre")
                    else:
                        for pg in [int(v.lstrip("!")) for v in refs] + [int(parts[2])]:
                            target = root / lang / f"N{pg // 50 * 50:03}" / f"N{pg:03}.TXT"
                            if not target.exists():
                                problems.append(f"{f}: CV/CX reference une page absente : {pg:03}")
                # E0 deplace un TOTAL DE DEPART : l'OR et le BONUS n'en ont
                # pas, et character_shift0 ne verifie rien -- il indexerait
                # hors de sa table. C'est ici qu'on refuse.
                if parts[0] == "E0" and len(parts) > 1 \
                        and parts[1] in ("OR", "BONUS"):
                    problems.append(f"{f}: E0 sur {parts[1]} -- seuls "
                                    "ENDURANCE, HABILETE et CHANCE ont un "
                                    "total de depart")
                if parts[0] in ("G", "GX", "CI", "CN", "GU") and len(parts) > 1:
                    keys = {"ANNEAU", "CAPE", "CH", "AI", "FI", "BA",
                            "EP", "BJ", "CO", "PL", "GR",
                            ".T", ".G", ".P", ".S", ".D", "LOUP", "FLEUR",
                            "OISEAU", "ARAIGNEE", "GRENOUILLE", "FAUX"}
                    if parts[1] not in keys:
                        problems.append(f"{f}: objet/amulette inconnu {parts[1]!r}")
                # `V <cible> [<page> ...]` : la cible, puis les AUTRES pages de
                # la meme clairiere. take_uint lit des chiffres et rien
                # d'autre ; un mot glisse dans la liste serait lu comme un
                # zero et le moteur testerait la page 000. La liste est libre
                # en longueur, mais entierement numerique, sans doublon, et
                # sans la page qui la porte -- que classify_line teste deja.
                if parts[0] in ("V", "VR"):
                    nums = parts[1:]
                    if len(nums) < (2 if parts[0] == "VR" else 1) or not all(x.isdigit() for x in nums):
                        problems.append(f"{f}: ligne V mal formee {d!r} "
                                        "(attendu : des numeros de page)")
                    else:
                        v = [int(x) for x in nums]
                        proofs = v[1:] if parts[0] == "VR" else v
                        if len(set(proofs)) != len(proofs):
                            problems.append(f"{f}: ligne V avec un doublon {d!r}")
                        if sid in v and parts[0] == "V":
                            problems.append(f"{f}: ligne V citant sa propre "
                                            f"page {sid:03d}")
            if len(choices) > MAX_CHOICES:
                problems.append(f"{f}: {len(choices)} choix > {MAX_CHOICES} "
                                f"(MAX_CHOICES)")
            # Une ligne de choix ne doit jamais atteindre la derniere colonne,
            # qui ferait scroller l'Apple II. Les titres pointent directement
            # dans le tampon de scene : aucune troncature intermediaire.
            for cid, ctitle in choices:
                if len(ctitle) > 76:
                    problems.append(f"{f}: titre du choix {cid:03d} "
                                    f"{len(ctitle)} car. > 76")
            r = choice_rows(choices)
            if r > CHOICE_ROWS:
                problems.append(f"{f}: choix sur {r} lignes > {CHOICE_ROWS} "
                                f"({len(choices)} choix)")
            # fread lit FILE_BUFFER_SIZE-1 octets : le dernier est le '\0'.
            if len(new_bytes := render(sid, title, w, choices,
                                       directives).encode("utf-8")) > FILE_BUFFER - 1:
                problems.append(f"{f}: {len(new_bytes)} octets > "
                                f"{FILE_BUFFER - 1} (file_buffer)")
            # L'Apple II n'a ni accents ni guillemets francais : un octet
            # hors ASCII sortirait en glyphe faux, et le corpus est
            # volontairement sans accents depuis le depart.
            for ch in set(re.findall(r"[^\x00-\x7f]", "\n".join(body + [title]))):
                problems.append(f"{f}: caractere non ASCII {ch!r}")
            if len(title) > 60:
                problems.append(f"{f}: titre {len(title)} car. > 60")
            if words(w) != words(body):
                problems.append(f"{f}: LE TEXTE A CHANGE")
            order = None if derive else [line.rstrip() for line in
                    f.read_text(encoding="utf-8").splitlines()
                    if DIRECTIVE.match(line) or CHOICE.match(line)]
            new = render(sid, title, w, choices, directives, order)
            if new != f.read_text(encoding="utf-8", errors="replace"):
                changed += 1
                if apply: f.write_text(new, encoding="utf-8")
    print(f"{'ecrits' if apply else 'a reecrire'} : {changed} fichiers")

    if derive:
        # Le moteur ne lit qu'une langue a la fois, mais le combat doit etre le
        # meme dans les deux : une divergence FR/EN est une erreur de contenu.
        ids = {sid for (_, sid) in found}
        for sid in sorted(ids):
            fr = found.get(("TEXTFR", sid))
            en = found.get(("TEXTEN", sid))
            # Le moteur ne lit qu'une langue, mais les regles doivent etre les
            # memes des deux cotes : on compare la MECANIQUE de chaque
            # directive, pas les titres. C'est ainsi qu'on a vu TEXTEN rester
            # en choix libres pendant que TEXTFR passait au jet de Chance.
            # Combien de champs portent de la mecanique, par directive : le
            # reste est du titre, qui se traduit.
            # None = la ligne entiere est de la mecanique, aucun titre a
            # traduire. MV et ED sont dans ce cas. Une directive ABSENTE de
            # cette table est silencieusement ignoree par mechanics(), et le
            # recoupement devient aveugle a son sujet : c'est exactement le
            # bug corrige le 2026-08-29 pour CU/CL/PC, et le lot pose des MV
            # et des ED dans les deux langues.
            KEEP = {"M": 3, "MD": 2, "MS": 2, "MV": None, "MU": None, "CL": None,
                    "MI": None, "MR": None, "MF": None, "MM": None,
                    "CF": 2, "PC": 3, "CU": 3, "CP": 3, "E": None,
                    "ED": None, "V": None, "VR": None, "E0": None, "CE": None,
                    "CS": None, "DV": None, "MB": None, "G": None,
                    "GX": None, "GA": None, "CI": 3, "CN": 3,
                    "GU": 3, "CA": 4, "CT": 4, "CG": 3, "CB": 3, "PD": None, "PO": None, "PX": None,
                    "TR": None}

            def mechanics(dirs):
                out = []
                for d in (dirs or []):
                    parts = d.split()
                    if parts[0] in KEEP:
                        out.append(" ".join(parts[:KEEP[parts[0]]]))
                return sorted(out)
            if mechanics(fr) != mechanics(en):
                problems.append(f"N{sid:03d}: FR et EN ne disent pas la meme "
                                f"chose ({mechanics(fr)} / {mechanics(en)})")
        for tag, label in (("ED ", "jets de des derives"),
                           ("MV ", "victoires enchainees")):
            hits = sorted(sid for sid in ids
                          if any(d.startswith(tag)
                                 for d in found.get(("TEXTFR", sid), [])))
            print(f"{label} : {len(hits)}")
            for sid in hits:
                line = next(d for d in found[("TEXTFR", sid)] if d.startswith(tag))
                print("   N%03d  %s" % (sid, line))
        combats = sorted(sid for sid in ids
                         if any(d.startswith("M ") for d in found.get(("TEXTFR", sid), [])))
        print(f"combats derives : {len(combats)}")
        for sid in combats:
            print("   N%03d  %s" % (sid, "  ".join(found[("TEXTFR", sid)])))

    # Une clairiere, une musique : toutes ses pages (SCOSWAMP.MORE/carte.json,
    # arbitrages appliques) portent le meme theme de zone, ou une surcouche.
    # Sans cela, entrer par un autre sentier changerait ou couperait la musique
    # au milieu du lieu -- exactement ce que le moteur par clairiere evite.
    carte = root.parent / "SCOSWAMP.MORE" / "carte.json"
    if carte.exists():
        for c in json.loads(carte.read_text())["clairieres"]:
            zones = set()
            for p in c["pages"]:
                m = mus.get(("TEXTFR", p))
                if not m:
                    problems.append(f"clairiere {c['hub']:03d} : page {p:03d} sans ligne MU")
                    continue
                arg = m[-1].split()[1]
                if not arg.startswith("+") and arg != "-": zones.add(arg)
            if len(zones) != 1:
                problems.append(f"clairiere {c['hub']:03d} ({c['titre']}) : "
                                f"themes de zone {sorted(zones)}, il en faut un seul")
    print(f"problemes : {len(problems)}")
    for p in problems[:40]: print("  " + p)

if __name__ == "__main__":
    main()
