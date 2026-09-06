#!/usr/bin/env python3
"""Inventory of scene mechanics and checked narrative contracts.

No prose is automatically rewritten. This checks bilingual mechanics and
explicit reviewed contracts; an empty error list is not a narrative proof.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OPS = set("AC T V VR C CF CV CX CI CN CU CP CG CB CT CA GU G GX GA P PC PD PO PS PX TR M MM MF MR MD MS MI MV MB MU E E0 ED EH CE CL CS DV".split())
ARITY = dict(T=1, C=1, CF=1, CX=2, CV=2, CI=2, CN=2, CU=2, CP=2, GU=2, CA=3, CT=3, CG=2, CB=2, M=2)
REQUIRED = {
    382: ["VR 270 421", "CU GLACE 270", "CU CROISSANCE 421", "C 190", "C 223"],
    421: ["MU QUICKSAND.MB", "C 270"],
    44: ['ED ENDURANCE -1', 'C 157', 'C 398'],
    58: ['CE ENDURANCE 0 -1', 'C 398', 'C 105', 'C 208'],
    107: ['ED ENDURANCE -1', 'C 019'],
    135: ['ED OR +1', 'C 309'],
    190: ['CE ENDURANCE 0 -2', 'C 270'],
    216: ['ED ENDURANCE -1', 'C 319'],
    249: ['CE HABILETE 0 -1', 'C 336', 'C 121'],
    252: ['ED ENDURANCE -1', 'C 161'],
    274: ['ED ENDURANCE -1', 'C 375', 'C 298'],
    373: ['CL 402 225'],
    402: ['M 9 8', 'MV 140'],
    225: ['M 9 10', 'MV 140'],
    31: ["VR 364 077 364", "VR 394 394", "C 047", "C 394", "C 077"],
    394: ["C 047", "C 077"],
    77: ["E ENDURANCE +3", "C 047"],
    364: ["C 047"],
    241: ["G EP", "E CHANCE +99", "E BONUS +1", "C 206"],
    140: ["G EP", "E BONUS +2", "C 375", "C 335", "C 027"],
    340: ["G EP", "E BONUS +2", "C 375", "C 298"],
    92: ["VR 108 020 232 389 108", "VR 247 247", "CI LOUP 344", "CN LOUP 068"],
    247: ["G .T", "C 020", "C 232", "C 342"],
    20: ["E ENDURANCE +2", "E CHANCE +1", "C 342"],
    232: ["G BA", "CI .G 389", "CN .G 342"],
    108: ["C 342"],
    29: ['CL 185 378'],
    83: ['CL 035 357'],
    86: ['CL 189 348'],
    118: ['V 303 319', 'CL 070 182'],
    147: ['CL 213 106'],
    231: ['CL 018 259'],
    296: ['CL 272 003'],
    315: ['CL 051 401'],
    359: ['CL 162 016'],
    91: ['CS ENDURANCE 404 405'],
    257: ['CS HABILETE 403 311'],
    377: ['CS ENDURANCE 319 406'],
    35: ['E ENDURANCE -1'],
    357: ['E ENDURANCE -5'],
    189: ['P AMITIE', 'P CHANCE', 'C 348'],
    182: ['ED ENDURANCE -1', 'C 319'],
    106: ['E ENDURANCE -2'],
    405: ['E HABILETE -1'],
    403: ['E CHANCE +2', 'C 153'],
    311: ['E HABILETE -2'],
    406: ['E ENDURANCE -3', 'C 319'],
    24: ["MU WILLOWISP.MB", "CE ENDURANCE 0 -2", "C 336", "C 121"],
    73: ["VR 202 073", "G CH", "CE ENDURANCE 0 -2", "C 202"],
    305: ["V 238 084 117 251 283 396", "CI .G 036", "CI .P 084", "CI .S 334"],
    36: ["CI .T 283", "CN .T 396"],
    84: ["C 363"],
    238: ["C 363"],
    283: ["PC 1 B", "C 363"],
    396: ["PC 1 B", "C 363"],
    334: ["C 379", "C 152", "C 037"],
    152: ["CU FEU 136", "CU FLETRISSURE 264", "CU ILLUSION 347", "CU AMITIE 117", "C 334"],
    136: ["C 379"],
    264: ["E ENDURANCE -2", "C 379"],
    347: ["C 379", "C 363"],
    117: ["C 363"],
    292: ["C 363"],
    37: ["C 292", "C 220"],
    220: ["C 292", "C 334"],
    379: ["M 7 10", "CF 363", "E HABILETE -3", "MV 251"],
    251: ["G FLEUR", "E CHANCE -3", "C 363"],
    144: ["VR 345 113 354", "C 074", "C 026", "C 332"],
    113: ["E ENDURANCE -3", "C 165"],
    345: ["E ENDURANCE -1", "C 165"],
    361: ["MU +DEATH.MB"],
    74: ["CU MALEDICTION 261", "CU FEU 113", "CU AMITIE 361", "C 144"],
    261: ["ED ENDURANCE -1", "M 8 9", "MV 354"],
    354: ["G ARAIGNEE", "C 165"],
    215: ["MM 1", "M 7 6", "MV 247"],
    355: ["MM 1", "M 7 5", "M 8 5", "MV 186"],
    128: ["CB 0 180", "CB 1 407"],
    407: ["PO", "C 019"],
    180: ["C 214"],
    399: ["CU TERREUR 346", "CU ILLUSION 169", "C 309", "C 281"],
    346: ["M 6 7", "M 7 7", "MI 281", "MV 135"],
    34: ["CU FLETRISSURE 237", "CU FEU 291", "CU TERREUR 356", "C 209"],
    374: ["GU GR 228", "CU TERREUR 299", "CU ILLUSION 060", "CU AMITIE 160", "C 011"],
    324: ["C 088", "CU BENEDICTION 383", "C 042"],
    258: ["CU TERREUR 198", "CU AMITIE 127", "C 212"],
    256: ["CU MALEDICTION 274", "CU TERREUR 365", "CU FEU 385", "CU ILLUSION 351", "C 057"],
    145: ["CU FEU 211"],
    211: ["M 6 12", "MV 366"],
    408: ["TR", "C 343"],
    280: ["CG 1 395", "CG 1 078", "CG 1 289", "C 343"],
    289: ["E OR -1", "PD", "E ENDURANCE +2", "CL 150 343"],
    8: ["CT 1 15 141", "CT 0 0 316", "C 341"],
    363: ["CV !378,!219 133", "CV 219 234", "CV 378,!219 306"],
    221: ["M 11 4", "MF 2", "CF 348", "MV 277"],
    181: ["MR 1 8", "C 200"],
    306: ["MR 255 10", "C 378"],
    61: ["C 229", "C 420"],
    420: ["M 9 12", "MD 4", "MI 012", "MV 366"],
    129: ["CV 069 268", "CX 069 181"],
    210: ["CV 125 243", "CX 125 143"],
    342: ["CV 366 197", "CX 366 300"],
    343: ["CV 214 199", "CX 214 301"],
    331: ["CV 392 202", "CX 392 112"],
    330: ["CV 055 129", "CX 055 268"],
    253: ["G .D", "GX FI"],
    371: ["GX .P", "GX .S", "G .G", "PC 6 NB"],
    173: ["GX .G", "GX .S", "G .P", "PC 5 N"],
    206: ["GX .G", "GX .P", "G .S", "PC 6 NM"],
    262: ["CV 280 166", "CX 280 115"],
    266: ["GA 0", "E OR +250"],
    75: ["M 9 10", "MI 028", "MV 362"],
    141: ["PS", "E ENDURANCE +255"],
    285: ["EH"],
    56: ["CV 280 158", "CX 280 008"],
    49: ["GX ANNEAU", "E OR +100"],
    78: ["E OR -1", "E ENDURANCE +2"],
    193: ["E HABILETE +255", "E ENDURANCE +255", "E CHANCE +255"],
    228: ["GX GR"],
    272: ["E CHANCE -2"],
    365: ["E HABILETE -1"],
    395: ["E OR -1", "E ENDURANCE -1", "CG 1 078", "CG 1 289"],
}


for router in (129, 210, 330, 331, 342, 343, 363):
    REQUIRED[router].insert(0, "AC")

# These encounters explicitly require fighting without escape.
FORBIDDEN_OPS = {24: ["CL"],117: ["G"], 292: ["G"], 261: ["CF"], 215: ["CF"], 355: ["CF"]}

def read_scene(path):
    raw = path.read_bytes()
    mechanics = []
    for line in raw.decode("ascii").splitlines():
        if not line or line[0].isspace():
            continue
        parts = line.split()
        if parts[0] in OPS:
            count = ARITY.get(parts[0])
            mechanics.append(" ".join(parts if count is None else parts[:count + 1]))
    return {"path": str(path.relative_to(ROOT)), "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(), "mechanics": mechanics}


def audit():
    corpus = {}
    errors = []
    source = (ROOT / "SCOSWAMP/SRC/scoswamp.c").read_text()
    table_text = re.search(r"static const char kOps\[\] =\s*(.*?);", source, re.S)[1]
    table = "".join(re.findall(r'"([^"]*)"', table_text))
    enum = re.search(r"enum \{ D_AC,.*?D_TEXTE \};", source, re.S)[0]
    names = re.findall(r"\bD_(\w+)", enum)[:-1]
    if len(table) != 4 * len(names):
        errors.append("native opcode table and enum have different lengths")
    project = json.loads((ROOT / "SCOSWAMP.MORE/TOOLS/interpreter/project.scoswamp.json").read_text())
    declared = {d["jeton"]: d for d in project["directives"]}
    for i, name in enumerate(names):
        row = table[i*4:i*4+4]
        if len(row) != 4 or row[:2].strip() != name:
            errors.append(f"native opcode {i}: enum {name} does not match {row!r}")
            continue
        js = declared.get(name)
        if not js or (js["troisieme"], js["effetEntree"]) != (row[2], row[3] == "1"):
            errors.append(f"{name}: native/JavaScript opcode contract differs")
    for language in ("FR", "EN"):
        corpus[language] = {int(p.stem[1:]): read_scene(p)
                            for p in sorted((ROOT / ("SCOSWAMP/TEXT" + language)).rglob("N*.TXT"))}
    for page in sorted(set(corpus["FR"]) | set(corpus["EN"])):
        if page not in corpus["FR"] or page not in corpus["EN"]:
            errors.append(f"{page:03}: missing translation")
            continue
        fr, en = (corpus[lang][page]["mechanics"] for lang in ("FR", "EN"))
        if fr != en:
            errors.append(f"{page:03}: FR/EN mechanics differ: {fr!r} / {en!r}")
        for language in ("FR", "EN"):
            scene = corpus[language][page]
            for op in FORBIDDEN_OPS.get(page, []):
                if any(line.split()[0] == op for line in scene["mechanics"]):
                    errors.append(f"{language} {page:03}: forbidden opcode {op}")
            for required in REQUIRED.get(page, []):
                if required not in scene["mechanics"]:
                    errors.append(f"{language} {page:03}: missing {required}")
    return {"scope": f"{sum(map(len, corpus.values()))} scene inventory; bilingual mechanics; explicitly reviewed contracts only",
            "required": REQUIRED, "forbidden_ops": FORBIDDEN_OPS, "errors": errors, "corpus": corpus}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit()
    if args.output:
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    for error in result["errors"]:
        print(error)
    print(f"{sum(map(len, result['corpus'].values()))} scenes, {len(REQUIRED)} reviewed contracts, "
          f"{len(result['errors'])} errors")
    return bool(result["errors"])


if __name__ == "__main__":
    raise SystemExit(main())
