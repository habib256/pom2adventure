#!/usr/bin/env python3
"""Lance les bancs du dépôt depuis n'importe quel répertoire, sans dépendance Python."""
import argparse
import json
import shlex
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
INTEGRATION = {"test_localized_layout.mjs", "test_workshop_browser.mjs"}
SUITES = {
    "python": "outils SCOSWAMP, mémoire, musique et harnais (bibliothèque standard)",
    "node": "moteur ADVKIT, sans serveur ni navigateur",
    "native": "règles C, RLE et analyseur SPACETRIP, sans POM2 ni cc65",
    "images": "convertisseurs, atelier et métriques (POM2, NumPy, Pillow)",
    "integrity": "intégrité des données et binaires présents (check-project.sh)",
    "http": "volume et données FR/EN (serveur 8765 et HDV à jour)",
    "browser": "atelier Chrome (serveur 8765, CDP 9228, WebSocket Node)",
}
PROFILES = {
    "quick": ("python", "node", "native"),
    "all": ("python", "node", "native", "images", "integrity"),
}


def scripts(directory, pattern):
    paths = sorted(directory.glob(pattern))
    if not paths:
        raise ValueError(f"aucun test : {directory / pattern}")
    return [str(p.relative_to(ROOT)) for p in paths]


def commands(suite, python, pom2_src=None):
    """Chaque tuple contient la commande et son rôle de prérequis bloquant."""
    if suite == "python":
        paths = []
        for directory in (ROOT / "SCOSWAMP.MORE/TOOLS", ROOT / "SCOSWAMP.MORE/MUSIC", HERE):
            paths.extend(p for p in scripts(directory, "test_*.py")
                         if not Path(p).name.startswith("test_image_"))
        return [([python, p], False) for p in paths]
    if suite == "node":
        return [(["node", p], False) for p in scripts(HERE, "test_*.mjs")
                if Path(p).name not in INTEGRATION]
    if suite == "native":
        build = "ADVKIT/TOOLS/build-host"
        return [(["cmake", "-S", "ADVKIT/TOOLS", "-B", build,
                  "-DADVKIT_BUILD_TOOLS=OFF"], True),
                (["cmake", "--build", build], True),
                (["ctest", "--test-dir", build, "--output-on-failure"], False)]
    if suite == "images":
        configure = ["cmake", "-S", "ADVKIT/TOOLS", "-B", "ADVKIT/TOOLS/build",
                     "-DADVKIT_BUILD_TOOLS=ON"]
        if pom2_src:
            configure.append(f"-DPOM2_SRC={pom2_src}")
        return [([python, "-c", "import numpy; from PIL import Image"], True),
                (configure, True),
                (["cmake", "--build", "ADVKIT/TOOLS/build", "--target",
                  "scoswamp_hgr", "scoswamp_dhgr", "build_prodos_volume"], True),
                *[([python, p], False) for p in scripts(HERE, "test_image_*.py")]]
    if suite == "integrity":
        return [(["bash", "check-project.sh"], False)]
    name = "test_localized_layout.mjs" if suite == "http" else "test_workshop_browser.mjs"
    flags = ["--experimental-websocket"] if suite == "browser" else []
    return [(["node", *flags, f"ADVKIT/TESTS/{name}"], False)]


def select(names):
    return list(dict.fromkeys(s for name in names for s in PROFILES.get(name, (name,))))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("suites", nargs="*", metavar="SUITE", help="défaut : quick")
    parser.add_argument("--list", action="store_true", help="lister les suites et prérequis")
    parser.add_argument("--dry-run", action="store_true", help="afficher sans exécuter ni écrire")
    parser.add_argument("--report", type=Path, help="bilan JSON, chemin relatif à la racine du dépôt")
    parser.add_argument("--pom2-src", type=Path, help="sources POM2 pour la suite images")
    parser.add_argument("--timeout", type=float, default=300, help="secondes par commande (défaut : 300)")
    args = parser.parse_args(argv)
    if args.timeout <= 0:
        parser.error("--timeout doit être positif")
    for name in args.suites:
        if name not in SUITES and name not in PROFILES:
            parser.error(f"suite inconnue : {name} (voir --list)")
    if args.list:
        for name, members in PROFILES.items():
            print(f"{name:10} {' + '.join(members)}")
        for name, description in SUITES.items():
            print(f"{name:10} {description}")
        return 0
    selected = select(args.suites or ["quick"])
    results = []
    failed = []
    pom2_src = args.pom2_src.resolve() if args.pom2_src else None
    for suite in selected:
        print(f"\n=== {suite} : {SUITES[suite]} ===", flush=True)
        for command, prerequisite in commands(suite, sys.executable, pom2_src):
            print(f"+ {shlex.join(command)}", flush=True)
            if args.dry_run:
                continue
            started = time.monotonic()
            try:
                code = subprocess.run(command, cwd=ROOT, timeout=args.timeout).returncode
            except subprocess.TimeoutExpired:
                print(f"Délai dépassé ({args.timeout:g} s)", file=sys.stderr)
                code = 124
            except OSError as exc:
                print(f"Commande indisponible : {exc}", file=sys.stderr)
                code = 127
            results.append(dict(suite=suite, command=command, returncode=code,
                                seconds=round(time.monotonic() - started, 3)))
            if code:
                if suite not in failed:
                    failed.append(suite)
                if prerequisite:
                    print(f"Suite {suite} interrompue : prérequis en échec.", flush=True)
                    break
    if args.dry_run:
        return 0
    if args.report:
        report = ROOT / args.report
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(json.dumps(dict(
            schema=1, date=datetime.now(timezone.utc).isoformat(),
            suites=selected, failed=failed, commands=results,
        ), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\nBilan : {len(selected) - len(failed)}/{len(selected)} suites réussies."
          + (f" Échecs : {', '.join(failed)}." if failed else ""), flush=True)
    return int(bool(failed))


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
