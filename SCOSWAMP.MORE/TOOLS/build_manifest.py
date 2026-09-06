#!/usr/bin/env python3
"""Build the deterministic image-generation manifest for SCOSWAMP."""

from __future__ import annotations

import argparse
import re
import json
from pathlib import Path


STYLE = """Use case: illustration-story
Asset type: native Apple II DHGR scene illustration for SCOSWAMP
Primary request: Illustrate the numbered French gamebook scene below faithfully.
Style/medium: late-1970s sword-and-sorcery pulp ink illustration: smooth confident outlines, bold brush shadows and flat solid fills. This is a high-resolution master, NOT pixel art, but DESIGN IT AT 140x192 FROM THE START: judge every silhouette as if only 140 colour cells existed across the screen.
DHGR readability budget: construct the picture from LARGE CONTIGUOUS FLAT COLOUR MASSES, not from linework. At least 75% of every visible subject must be uninterrupted solid fills; use one broad shadow block instead of many ink marks. Primary outer contours must reduce to 3-6 colour cells thick; eyes, fingers, teeth, blades and facial marks must never be single-cell details. Use at most three depth planes, 6-10 major connected colour shapes and 0-3 broad interior marks per principal figure. Trees are solid trunk silhouettes, reeds are grouped wedges, and water is two or three broad horizontal bands. Prefer one unmistakable gesture over several small actions. No thin branches, loose hair strands, hatching, stippling, tiny foliage, scattered highlights, etched texture or busy backgrounds.
Composition/framing: landscape 35:24; select one decisive visual moment, never a collage; one strong focal action occupying at least half the frame height; essential shapes remain readable at 140x192; keep critical content away from the extreme edges.
Color palette: use ONLY these Apple II DHGR colours: black #000000, dark red #A70B40, dark blue #401CF7, purple #E628FF, dark green #007440, dark gray #808080, medium blue #1990FF, light blue #BF9CFF, brown #406300, orange #E66F00, pink #FF8BBF, light green #19D700, yellow #BFE308, aquamarine #58F4BF, white #FFFFFF. Prefer black, white, orange, purple, green and blue for identity-critical shapes because they remain strongly separated on both composite and Le Chat Mauve RGB displays. Never use gray for a critical boundary: DHGR gray indices are neutral in composite but differently tinted on Le Chat Mauve. Use coherent flat regions; no gradients or invented colours; 30-50% solid black negative space.
Lighting/mood: theatrical menace, adventure, immediate action.
The hero's presence: follow the per-scene HERO DECISION below. Do not add him merely because the prose addresses "vous": gamebook narration uses the second person even when the strongest illustration is the place, object, creature or non-player character alone.
Non-battle staging: place the hero where the narrated action naturally puts him. When he shares the frame with a person or creature, make their attention and eyelines coherent, but do not force a rigid left/right duel layout onto peaceful meetings or exploration.
Battle staging is separate and absolute: in every battle tableau the hero is on the LEFT facing RIGHT, and his opponent is on the RIGHT facing LEFT, with a clear gap between them.
The hero's weapon: his sword stays SHEATHED at his hip and his hands stay empty unless the scene text below actually has him fighting, drawing, threatening or striking. Most pages are a walk, a conversation, a discovery or a bargain, and a hero standing sword in hand through all of them looks like a man who means to kill everyone he meets. Draw the posture the page describes.
Materials/textures: dominant hard-edged flat fills and one or two broad shadow masses; outlines define silhouettes but do not scribble texture inside them. No random grain.
Text (verbatim): ""
Constraints: no visible words, letters, numbers, captions, border, UI, logo, signature, or watermark; no gradients; no anti-aliasing; no photorealistic texture; no tiny decorative detail; one coherent scene, not a collage.
Avoid: glossy modern concept art, modern objects, smooth airbrush shading, comic speech effects, noisy dithering, illegible micro-detail, extra characters or objects not supported by the scene.

French scene source:
"""


# ── Images de bataille ──────────────────────────────────────────────────────
# Le moteur bascule en mode mixte pendant un combat : l'illustration occupe les
# 20 lignes du haut, l'echange d'assauts les 4 du bas. Les 32 dernieres lignes
# de pixels sont donc RECOUVERTES par la fenetre de texte -- c'est la contrainte
# de cadrage qui distingue une image de bataille d'une illustration de scene.
BATTLE_HERO = """The hero, drawn identically in every battle image: a lean, muscular human adventurer with short black hair and an uncovered head, wearing a sleeveless orange leather jerkin, his muscular arms bare, and here -- and only here, because this is a fight -- his sword DRAWN and raised in the right hand, a backpack on the shoulders, seen three-quarters from behind-left so the face stays hidden."""

BATTLE_STYLE = """Use case: illustration-story
Asset type: native Apple II DHGR battle tableau for SCOSWAMP
Primary request: One duel, two figures. The hero faces the adversary named below; both are fully visible, mid-action, caught at the moment blades or claws are about to meet.
Setting: the duel happens somewhere, so draw the place behind them -- the swamp clearing, hut, water, tower or garden the scene text names, or plain swamp if it names none: BLACK tree trunks, GREEN reeds, VIOLET mud, standing BLUE water. Keep it BEHIND the fighters and quieter than they are: flat shapes, no detail that competes with the two silhouettes, and nothing between the fighters or overlapping them.
Composition/framing: landscape 35:24 for a 140x192 DHGR colour screen. CRITICAL: during play a text window covers the bottom sixth. Both figures must be COMPLETE within the upper three quarters, each at least half the frame height, and the lowest quarter plain dark ground. Hero left, adversary right, a gap at least one figure-head wide; no weapon, limb or background branch may bridge that gap. Broad readable silhouettes and no fine detail.
Facing -- NON-NEGOTIABLE: the two are fighting EACH OTHER, so each one looks at the other. The hero stands on the left and faces, leans and strikes RIGHTWARD, toward the adversary. The adversary stands on the right and faces, leans and strikes LEFTWARD, toward the hero. Their heads are turned toward one another, their eyes meet, their weapons are aimed at one another. A figure whose head or gaze points away from the other -- outward, toward the edge of the frame, or at the viewer -- is WRONG: two fighters looking in opposite directions are not in a duel.
""" + BATTLE_HERO + """
Style/medium: late-1970s sword-and-sorcery pulp screen illustration built primarily from LARGE CONTIGUOUS FLAT COLOUR MASSES. At least 75% of each fighter is uninterrupted solid fill, with a single broad shadow block and only 0-3 interior marks. Bold outlines define the outer silhouette but never become dense internal pen work. Designed at native 140x192 DHGR logic: contours reduce to 3-6 colour cells; faces and weapons use only broad marks. At most 8 major connected colour shapes per fighter and three quiet, flat background planes.
Color palette: use ONLY black #000000, dark red #A70B40, dark blue #401CF7, purple #E628FF, dark green #007440, dark gray #808080, medium blue #1990FF, light blue #BF9CFF, brown #406300, orange #E66F00, pink #FF8BBF, light green #19D700, yellow #BFE308, aquamarine #58F4BF, white #FFFFFF; no gradients or invented colours. Do not use gray to separate touching fighters or define a weapon edge because its two hardware variants diverge on Le Chat Mauve RGB.
Lighting/mood: theatrical menace, imminent violence.
Materials/textures: hard-edged flat fills and one or two deliberate broad shadow masses only; no etched detail, hatching or random grain.
Text (verbatim): ""
Constraints: no visible words, letters, numbers, captions, border, UI, logo, signature, or watermark; no gradients; no anti-aliasing; no photorealistic texture; no tiny decorative detail; exactly two figures, the hero and the adversary.
Avoid: glossy modern concept art, modern objects, smooth airbrush shading, comic speech effects, noisy dithering, illegible micro-detail, extra creatures or bystanders.

The adversary, and the French scene it comes from:
"""


def battle_refs(text, characters, root):
    """Les planches d'une bataille, decor compris.

    `refs_for` classe les decors en dernier et coupe a quatre : une bataille
    citant deux adversaires perdait donc son fond, et chaque combat inventait
    le sien. Le marais sert de decor par defaut -- c'est ou tout se passe.
    """
    out = refs_for(text, characters, root)
    if not any("/REF/" in r and r.split("/")[-1][:-4] in DECOR_IDS for r in out):
        for fallback in ("CLAIRIERE", "MARAIS"):
            path = root / "SCOSWAMP.MORE" / "REF" / f"{fallback}.png"
            if path.exists():
                out = out[:3] + [str(path.relative_to(root))]
                break
    return out


def battle_rows(root, characters):
    """Une entree par clairiere portant un adversaire."""
    import re
    game = root / "SCOSWAMP"
    more = root / "SCOSWAMP.MORE"
    stat = re.compile(r"([A-Z\u00c0-\u00dd][A-Z\u00c0-\u00dd' -]{2,30}?)\s*HABILETE\s*:?\s*(\d+)\s*/?\s*ENDURANCE\s*:?\s*(\d+)")
    rows, seen = [], set()
    for path in sorted((game / "TEXTFR").rglob("N*.TXT")):
        scene_id = int(path.stem[1:])
        text = path.read_text(encoding="utf-8")
        names = [m.group(1).strip() for m in stat.finditer(text)]
        if not names and not text.startswith("T ") or scene_id in seen:
            pass
        # une page deja convertie porte une ligne "M <hab> <end> <nom>"
        assigned = []
        for line in text.splitlines():
            if line.startswith("M ") and len(line.split()) >= 4:
                assigned.append([line.split(None, 3)[3].strip(), scene_id])
            elif line.startswith("MI ") and assigned:
                assigned[-1][1] = int(line.split()[1])
        if assigned:
            names = [name for name, image in assigned if image == scene_id]
        if not names or scene_id in seen:
            continue
        seen.add(scene_id)
        sid = f"{scene_id:03d}"
        bucket = f"N{(scene_id // 50) * 50:03d}"
        rows.append({
            "id": scene_id,
            "scene": f"B{sid}",
            "adversaries": names,
            "text_path": str(path.relative_to(root)),
            "source_png": str((more / "GENERATED" / f"B{sid}.png").relative_to(root)),
            "hgr_rle": str((game / "DHGR" / bucket / f"B{sid}.RLE.BIN").relative_to(root)),
            "preview_png": str((more / "HGR-PREVIEW" / f"B{sid}.png").relative_to(root)),
            "prompt": (BATTLE_STYLE + "Adversary: " + ", ".join(names)
                       + "\n\n" + text.strip()
                       + "\n\nIMAGE ASSIGNMENT: depict ONLY " + ", ".join(names)
                       + ". Other monsters assigned an MI image in the source text "
                         "are illustrated separately and MUST NOT appear in this image."
                       + character_block(text + " " + " ".join(names), characters)),
            "refs": battle_refs(text + " " + " ".join(names), characters, root),
            "bible": bible_hash(text + " " + " ".join(names), characters),
            "status": "pending",
        })
    return rows


# ── La bible des personnages ────────────────────────────────────────────────
#
# Chaque image etait generee seule, a partir de sa seule page : rien ne liait
# le Maitre des Loups d'une illustration a celui de la suivante, ni la creature
# d'une scene a celle de son image de bataille. Le heros lui-meme changeait de
# visage. La constance ne s'obtient pas en demandant "le meme personnage" : il
# faut que le MEME TEXTE decrive le personnage dans tous les prompts ou il
# apparait. C'est ce que fait cette injection.

# Trois bibles, un seul mecanisme. L'ordre compte a l'affichage du prompt :
# le decor pose le monde, les personnages et les creatures s'y tiennent.
DECOR_IDS = set()
BIBLES = ("decors.json", "characters.json", "monsters.json", "objects.json")


# Le medium et la palette etaient decrits deux fois, une fois pour les scenes
# et une fois pour les batailles : deux textes qui pouvaient deriver l'un de
# l'autre. Ils n'existent plus qu'ici.
COMMON_STYLE = """Style/medium: late-1970s sword-and-sorcery pulp screen illustration constructed primarily from LARGE CONTIGUOUS FLAT COLOUR MASSES. At least 75% of the subject is uninterrupted solid fill. Use one broad shadow block rather than pen texture; outlines define the outer silhouette but do not fill surfaces with strokes. High-resolution master, NOT pixel art, but composed with a strict 140x192 DHGR shape budget: outer contours 3-6 colour cells thick, no one-cell features, at most 6-10 major connected shapes and 0-3 interior marks per subject.
Color palette: use ONLY black #000000, dark red #A70B40, dark blue #401CF7, purple #E628FF, dark green #007440, dark gray #808080, medium blue #1990FF, light blue #BF9CFF, brown #406300, orange #E66F00, pink #FF8BBF, light green #19D700, yellow #BFE308, aquamarine #58F4BF, white #FFFFFF. Prefer black, white and saturated colours for defining edges; gray is never a critical contour because its two DHGR indices appear differently tinted on Le Chat Mauve RGB. Use coherent flat regions, no gradients or invented colours; 30-50% solid black negative space.
Materials/textures: hard-edged flat fills and one or two broad shadow masses only; no etched detail, hatching or random grain.
Text (verbatim): ""
Constraints: no visible words, letters, numbers, captions, border, UI, logo, signature, or watermark; no anti-aliasing; no photorealistic texture; no tiny decorative detail.
Avoid: glossy modern concept art, modern objects, smooth airbrush shading, comic speech effects, noisy dithering, illegible micro-detail."""


def load_characters(root):
    """Les quatre bibles reunies. Les identifiants sont uniques par
    construction : le decor « bassin » et la Bete du Bassin ont porte le meme
    pendant un temps, donc la meme planche de reference -- chacun effacait
    celle de l'autre, et les illustrations de l'etang recevaient la fiche du
    monstre."""
    out = []
    for name in BIBLES:
        data = json.loads((root / "SCOSWAMP.MORE" / name)
                          .read_text(encoding="utf-8"))
        if name == "decors.json":
            kind = "decor"
        elif name == "objects.json":
            kind = "object"
        else:
            kind = "figure"
        if kind == "decor":
            DECOR_IDS.update(c["id"] for c in data["characters"])
        for c in data["characters"]:
            c["kind"] = kind
            out.append(c)
    seen = {}
    for c in out:
        if c["id"] in seen:
            raise SystemExit(f"identifiant en double dans les bibles : {c['id']}")
        seen[c["id"]] = True
    return out


def matching(text, characters, include_hero=True):
    """Les fiches qui concernent cette page, dans l'ordre des bibles."""
    out = []
    for c in characters:
        if c["id"] == "HERO" and not include_hero:
            continue
        if c.get("always"):
            out.append(c); continue
        for alias in c.get("aliases", []):
            if re.search(r"\b" + re.escape(alias) + r"\b", text, re.I):
                out.append(c); break
    return out


def bible_hash(text, characters, include_hero=True):
    """Empreinte des fiches ayant servi a ce prompt.

    Sans elle, modifier une fiche ne dit pas quelles images sont devenues
    perimees : on regenere tout, ou on oublie. Avec elle, `--stale` les nomme.
    """
    import hashlib
    blob = "\u0000".join(c["id"] + c["look"] + c.get("scale", "")
                          for c in matching(text, characters, include_hero))
    return hashlib.sha1(blob.encode("utf-8")).hexdigest()[:12]


# Un nom propre qu'aucune fiche ne couvre est une incoherence en puissance :
# rien ne le decrit, donc chaque image l'inventera.
PROPER = re.compile(r"\b([A-ZÀ-Ý][a-zà-ÿ]{3,}(?:\s+d[eu']\s*[A-ZÀ-Ýa-zà-ÿ]+)?)\b")
COMMON = {"Vous", "Cette", "Cela", "Alors", "Mais", "Dans", "Pour", "Elle",
          "Rendez", "Tentez", "Chaque", "Votre", "Deux", "Trois", "Quand",
          "Apres", "Avant", "Depuis", "Enfin", "Aucun", "Aucune", "Toute",
          "Tous", "Plus", "Bien", "Cependant", "Soudain", "Puis", "Voici"}


def uncovered_names(text, characters):
    known = " ".join(a for c in characters for a in c.get("aliases", [])).lower()
    out = set()
    for m in PROPER.finditer(text):
        name = m.group(1)
        first = name.split()[0]
        if first in COMMON or len(first) < 4:
            continue
        if first.lower() in known:
            continue
        out.add(name)
    return out


def character_block(text, characters, include_hero=True):
    """Le bloc injecte : description, puis echelle.

    L'echelle compte autant que la description : deux images peuvent respecter
    la lettre d'une fiche et montrer le Geant a deux tailles differentes. Elle
    est toujours donnee PAR RAPPORT AU HEROS, seule mesure commune a toutes
    les images.
    """
    present = matching(text, characters, include_hero)
    if not present:
        return ""
    out = []
    for c in present:
        line = "- " + c["look"]
        if c.get("scale"):
            line += " Scale: " + c["scale"] + "."
        out.append(line)
    return ("\n\nRecurring subjects — draw them EXACTLY as described here. "
            "These descriptions are fixed across the whole series; two images "
            "that share one must show the same subject.\n" + "\n".join(out))


# Une page peut citer jusqu'a dix fiches. Les joindre toutes noierait le
# modele : au-dela de quelques planches il moyenne au lieu de copier. On garde
# le heros — present partout, donc le sujet dont l'incoherence se verrait le
# plus — puis les figures nommees, puis le decor, et on s'arrete la.
REF_ATTACH_MAX = 4


def refs_for(text, characters, root, include_hero=True):
    """Les planches a joindre au prompt, les plus utiles d'abord."""
    def rank(c):
        return 0 if c.get("always") else (1 if c["kind"] == "figure" else 2)

    out = []
    for c in sorted(matching(text, characters, include_hero), key=rank):
        ref = c.get("ref")
        if ref and (root / ref).exists():
            out.append(ref)
        if len(out) == REF_ATTACH_MAX:
            break
    return out


REF_FIGURE = """Use case: reference sheet
Asset type: a single character reference for an Apple II DHGR gamebook
Primary request: ONE subject alone, full figure head to foot, standing still, on a plain solid black background. Even when its description uses a plural or compares its scale to the hero, draw ONE representative subject only: never add the hero, a handler, companions or a scale figure. No scene, no ground.
Composition/framing: the subject centered and complete, filling most of the frame, nothing cropped.
Checklist: EVERY garment, weapon and ornament named in the description below must be clearly visible and identifiable in the drawing, and carried EXACTLY as the description words it -- clothing worn rather than implied; a sword described as SHEATHED shown hanging in its scabbard at the hip with the hand empty, never held; a weapon described as raised or drawn shown in the hand. Add nothing the description does not name, and change nothing it does.
"""

REF_DECOR = """Use case: reference sheet
Asset type: a location reference for an Apple II DHGR gamebook
Primary request: the place itself, empty of people and creatures, seen wide at eye level. It is the stage other illustrations will be set on, so its shapes and colours must read at a glance.
Composition/framing: a wide establishing view, horizon roughly a third from the top.
The sky: follow the subject's description; when it says nothing, keep the sky simple and moody -- dark tones or a few flat clouds, never a large empty WHITE sky.
"""

REF_OBJECT = """Use case: reference sheet
Asset type: a single object reference for an Apple II DHGR gamebook
Primary request: ONE object alone, completely visible, centered on a plain solid black background. No hand, wearer, person, creature, scene or ground.
Composition/framing: close enough for its defining silhouette and ornament to remain unmistakable after reduction to 140x192 DHGR colour pixels; nothing cropped.
"""

REF_TAIL = COMMON_STYLE + """

DHGR DETAIL TARGET — NON-NEGOTIABLE: balanced intermediate detail, neither a pictogram nor dense concept art. The image reads first as broad flat colour areas; detail is subordinate. Primary silhouettes are bold; any secondary line remains 3-5 colour pixels thick after reduction to 140x192. Use no more than three broad meaningful interior marks. No hairlines, fine hatching, stippling, micro-texture, gradients or decorative noise.

This sheet is the CANON. Every later illustration of this subject will be drawn
from it, so the shapes and colours chosen here must be unambiguous.

The subject:
"""


def ref_rows(root, characters):
    """Une planche de reference par sujet des bibles."""
    rows = []
    for c in characters:
        look = c["look"]
        if c.get("scale"):
            look += " Scale: " + c["scale"] + "."
        if c["kind"] == "decor":
            base = REF_DECOR
        elif c["kind"] == "object":
            base = REF_OBJECT
        elif c["id"] == "HERO":
            base = (REF_FIGURE + "Orientation — ABSOLUTE CANON: show the HERO FROM "
                    "BEHIND in a rear three-quarter pose, with his uncovered head, "
                    "gaze, shoulders, hips and feet unmistakably pointing toward "
                    "IMAGE-RIGHT. He has no cape, cloak or hood.\n")
        else:
            base = (REF_FIGURE + "Orientation — ABSOLUTE CANON: show the subject "
                    "from the front or front three-quarter view, but turn its head, "
                    "eyes, nose, muzzle or beak unmistakably toward IMAGE-LEFT. "
                    "Never stare straight at the viewer and never look right.\n")
        rows.append({
            "id": c["id"],
            "source_png": c["ref"],
            "prompt": base + REF_TAIL + look,
            "status": "pending",
        })
    return rows


# Une scene narrative n'est pas un portrait automatique du joueur. Le heros
# n'est indispensable que lorsque son corps accomplit l'action qui fait
# l'image (chute, saut, nage, escalade, coup, manipulation dangereuse, etc.).
# Les combats ont leur manifeste Bxxx et leur regle absolue distincte.
HERO_ACTION = re.compile(
    r"\b(vous (?:tombez|chutez|sautez|bondissez|grimpez|escaladez|nagez|"
    r"plongez|rampez|frappez|attaquez|combattez|brandissez|tirez|lancez|"
    r"poussez|soulevez|ouvrez|buvez|mangez|avalez|etes blesse|etes pris|"
    r"etes attaque)|votre (?:main|bras|jambe|corps)\b)", re.I)


def hero_required(scene):
    """Vrai seulement si retirer le corps du heros ferait perdre l'action."""
    # Le portrait de la page "Qui vous etes" presente explicitement le
    # protagoniste, meme sans verbe d'action dans le texte.
    return scene.lstrip().startswith("T 419") or bool(HERO_ACTION.search(scene))


def scene_rows(root, characters, all_pages):
    """Une illustration par clairiere. Par defaut, seulement les manquantes."""
    game = root / "SCOSWAMP"
    more = root / "SCOSWAMP.MORE"
    rows = []
    # 402-406 : la page jumelle du Stratagus affaibli et les relais d'effets
    # (chute, piqure, bond parfait) -- voir TODO, "six pages inexprimables".
    # Le corpus contient aussi la page 419 "Qui vous etes", atteinte apres la
    # creation du personnage ; les pages 407-418 sont des numeros absents.
    for scene_id in range(420):
        sid = f"{scene_id:03d}"
        bucket = f"N{(scene_id // 50) * 50:03d}"
        text_path = game / "TEXTFR" / bucket / f"N{sid}.TXT"
        rle_path = game / "DHGR" / bucket / f"N{sid}.RLE.BIN"
        # --all les demande toutes : c'est ce qu'il faut apres une modification
        # des bibles, sans quoi les anciennes images gardent leur ancienne
        # interpretation.
        if not text_path.exists():
            continue
        if rle_path.exists() and not all_pages:
            continue
        scene = text_path.read_text(encoding="utf-8").strip()
        with_hero = hero_required(scene)
        hero_decision = ("\n\nHERO DECISION — INCLUDE HIM: the page contains an essential "
                         "physical action or bodily peril. Show the hero large enough "
                         "to read, from rear three-quarter view, acting exactly as the "
                         "text says; do not turn this into a posed portrait."
                         if with_hero else
                         "\n\nHERO DECISION — OMIT HIM: the protagonist is not visually "
                         "necessary in this scene. Do not show the hero, his back, a "
                         "traveller silhouette, or an orange-clad stand-in. Give the "
                         "frame to the location, object, creature or NPC that makes "
                         "this page distinct.")
        title_note = ("\n\nTITLE OVERRIDE — this is the cover image only: place the exact words "
                      "Scorpion's Swamp in very large, bold, readable pulp-gamebook "
                      "title lettering across the upper third. The title is part of "
                      "the artwork, not a UI caption; no other words or numbers."
                      if scene_id == 0 else "")
        rows.append({
            "id": scene_id,
            "scene": f"N{sid}",
            "text_path": str(text_path.relative_to(root)),
            "source_png": str((more / "GENERATED" / f"N{sid}.png").relative_to(root)),
            "hgr_rle": str(rle_path.relative_to(root)),
            "preview_png": str((more / "HGR-PREVIEW" / f"N{sid}.png").relative_to(root)),
            "prompt": STYLE + hero_decision + title_note + "\n\n" + scene
                      + character_block(scene, characters, with_hero),
            "refs": refs_for(scene, characters, root, with_hero),
            "bible": bible_hash(scene, characters, with_hero),
            "hero_required": with_hero,
            "status": "pending",
        })
    return rows


# Ce que le CORPUS dit de l'apparence d'un sujet. Le corpus est la verite du
# jeu : une fiche qui le contredit fait dessiner autre chose que ce que le
# joueur lit. C'est arrive deux fois -- la fiche du Maitre des Loups lui otait
# l'epee et les habits de Garde Forestier que la page 398 lui donne, et celle
# de Gayolard en faisait un vieillard barbu en robe bleue la ou la page 371
# decrit un petit homme replet en tunique blanche, au tour de potier.
DESCRIBES = re.compile(r"\b(porte|portant|vetu|vetue|couvert\w*|habill\w+"
                       r"|pend|arbore|tient|ressemble)\b", re.I)


def describe(root, characters):
    """Les phrases du corpus qui decrivent chaque sujet, pour relire sa fiche."""
    pages = sorted((root / "SCOSWAMP" / "TEXTFR").rglob("N*.TXT"))
    texts = [p.read_text(encoding="utf-8") for p in pages]
    for c in characters:
        if c.get("always"):
            continue
        seen = []
        for t in texts:
            for alias in c.get("aliases", []):
                for m in re.finditer(r"[^.]*\b" + re.escape(alias) + r"\b[^.]*\.",
                                     t, re.I):
                    line = " ".join(m.group(0).split())
                    if DESCRIBES.search(line) and line not in seen:
                        seen.append(line)
        if seen:
            print(f"--- {c['id']}")
            print(f"    FICHE : {c['look']}")
            for line in seen[:3]:
                print(f"    TEXTE : {line[:150]}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True,
                        help="apple2adventure directory")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--describe", action="store_true",
                        help="ce que le corpus dit de chaque sujet, en regard "
                             "de sa fiche : a relire avant de modifier une bible")
    parser.add_argument("--stale", action="store_true",
                        help="liste les images qu'un changement de fiche a "
                             "rendues perimees")
    parser.add_argument("--record", action="store_true",
                        help="enregistre l'empreinte des fiches pour les "
                             "images presentes, apres une generation")
    parser.add_argument("--refs", action="store_true",
                        help="les planches de reference, une par sujet des "
                             "bibles : le canon dont tout le reste decoule")
    parser.add_argument("--all", action="store_true",
                        help="toutes les pages, pas seulement celles dont "
                             "l'image manque (apres un changement de bible)")
    parser.add_argument("--battle", action="store_true",
                        help="manifeste des illustrations de bataille (une par "
                             "clairiere avec adversaire) au lieu des scenes")
    args = parser.parse_args()
    characters = load_characters(args.root)

    # ── Perimees ────────────────────────────────────────────────────────
    # Modifier une fiche change le prompt de toutes les images qui la citent.
    # Sans trace, on regenere tout ou on oublie ; avec, on nomme exactement
    # celles qui ont vieilli.
    # A cote des manifestes, pas dans GENERATED/ : ce dossier est ignore par
    # git, et un registre que le depot ne garde pas ne sert a rien.
    stamp = args.root / "SCOSWAMP.MORE" / "bible.stamp.json"

    if args.describe:
        describe(args.root, characters)
        return 0

    if args.stale or args.record:
        current = {}
        for rows in (battle_rows(args.root, characters),
                     scene_rows(args.root, characters, all_pages=True)):
            for r in rows:
                current[r["source_png"]] = r["bible"]
        known = json.loads(stamp.read_text(encoding="utf-8")) if stamp.exists() else {}
        if args.record:
            kept = {k: v for k, v in current.items() if (args.root / k).exists()}
            stamp.parent.mkdir(parents=True, exist_ok=True)
            stamp.write_text(json.dumps(kept, indent=1, sort_keys=True) + "\n",
                             encoding="utf-8")
            print(f"empreinte enregistree pour {len(kept)} images")
            return 0
        stale = [k for k, v in sorted(current.items())
                 if (args.root / k).exists() and known.get(k) != v]
        never = [k for k in sorted(current) if not (args.root / k).exists()]
        print(f"{len(stale)} image(s) perimee(s) par un changement de fiche, "
              f"{len(never)} jamais generee(s)")
        for k in stale[:20]:
            print("   " + k)
        return 0

    if args.refs:
        rows = ref_rows(args.root, characters)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        (args.root / "SCOSWAMP.MORE" / "REF").mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8") as stream:
            for row in rows:
                stream.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(f"wrote {len(rows)} reference prompts to {args.output}")
        return 0

    if args.battle:
        rows = battle_rows(args.root, characters)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8") as stream:
            for row in rows:
                stream.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(f"wrote {len(rows)} battle prompts to {args.output}")
        return 0

    rows = scene_rows(args.root, characters, args.all)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"wrote {len(rows)} scene prompts to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
