#!/usr/bin/env python3
"""Rejoue les trois missions au clavier dans POM2, sans ecriture en RAM.

Chaque tentative part d'une copie du disque et d'un nouveau personnage.
Les morts restent dans le rapport ; seuls les echecs de jeu autorisent une
nouvelle tentative. Une erreur de parcours interrompt la mission concernee.
"""
import argparse
import hashlib
import json
import shutil
import struct
import tempfile
import time
from pathlib import Path

import playtest as pt


class DuplicateRun(Exception):
    pass


class LostRun(Exception):
    pass


class KeyboardOnlyPom2(pt.Pom2):
    def rq(self, path, body=None, timeout=10):
        if body is not None and path != '/keyboard':
            raise AssertionError('Mutation interdite : ' + path)
        return super().rq(path, body, timeout)

    def poke(self, *args, **kwargs):
        raise AssertionError('Ecriture RAM interdite')


class Route:
    def __init__(self, game, report):
        self.g, self.report = game, report
        self.seen = set()

    def press(self, key):
        before = self.g.scene()
        rows = self.g.press(key)
        page = self.g.scene()
        hero = self.g.hero()
        self.seen.add(page)
        self.report['events'].append(dict(key=key, before=before, page=page, hero=hero))
        if hero['end'] == 0:
            raise LostRun('Mort page %d' % page)
        return rows

    def targets(self):
        count = self.g.p.peek(self.g.A('num_choices'), 1)[0]
        return [struct.unpack('<h', self.g.p.peek(self.g.A('choices') + 8*i, 2))[0]
                for i in range(count)]

    def go(self, *pages):
        rows = None
        for target in pages:
            if self.g.p.peek(self.g.A('dice_n'),1)==b'\x03' and any('Tentez votre Chance' in r for r in self.g.p.screen()):
                self.press(' '); self.press(' ')  # visible CE prompt and result
            if self.g.scene() == target:  # reached by automatic history routing
                continue
            ids = self.targets()
            if target not in ids:
                raise AssertionError('Page %d : cible %d absente de %s' %
                                     (self.g.scene(), target, ids))
            key = chr(65 + ids.index(target))
            print('%03d %s -> %03d' % (self.g.scene(), key, target), flush=True)
            rows = self.press(key)
            if self.g.scene() == self.report['events'][-1]['before']:
                raise AssertionError('Choix sans effet : page %d, cible %d' %
                                     (self.g.scene(), target))
        return rows

    def use(self, stone):
        names = list(self.g.stones())
        if stone not in names:
            return False
        index = names.index(stone)
        before = self.g.stones()[stone]
        self.press('I')
        self.press(chr(65 + index + (index >= 8)))
        self.press(' ')
        self.press('I')
        assert self.g.stones().get(stone, 0) == before - 1, 'Pierre non consommee'
        return True

    def fight(self, target, heal=True):
        if heal and self.g.scene() != target and self.g.hero()['end'] <= 8:
            # ENDURANCE n'est utilisable qu'avant le premier assaut.
            self.use('ENDURANCE')
        for _ in range(200):
            if self.g.scene() == target:
                return
            self.press(' ')
        raise AssertionError('Combat sans issue vers %d' % target)

    def begin(self, employer, stones):
        assert self.g.scene() == 0
        self.press('A')
        self.report['initial'] = self.g.hero()
        print('Personnage naturel :', self.report['initial'], flush=True)
        self.press(' ')
        self.go(1, 95, 240, 205)
        if employer == 'gayolard':
            self.go(335, 371)
        elif employer == 'pompatarte':
            self.go(27, 173)
        else:
            self.go(255, 40, 97, 284)
            self.fight(156, heal=False)
            target = self.targets()[0]
            if target == 326:
                raise LostRun('Recrutement refuse : blessures de la statue')
            assert target in (241, 193)
            self.go(target, 206)
        # Le menu PC retire les categories interdites et conserve l'ordre.
        allowed = pt.STONES[:6] + (pt.STONES[6:9] if employer == 'gayolard'
                                   else pt.STONES[9:] if employer == 'stratagus' else [])
        for name in stones:
            self.press(chr(65 + allowed.index(name)))
        assert sum(self.g.stones().values()) == len(stones)
        self.report['stones'] = self.g.stones()
        self.go(9, 195, 58)

    def east_return(self):
        self.go(14, 88, 331, 112, 202, 138, 101, 118)
        self.press(' ')
        self.press(' ')
        if self.g.scene() == 70:
            if self.g.stones().get('FEU'):
                self.go(110, 319)
            else:
                self.go(377)
                self.press(' ')
                self.press(' ')
                if self.g.scene() == 406:
                    self.go(319)
                assert self.g.scene() == 319
        else:
            assert self.g.scene() == 182
            self.press(' ')
            self.press(' ')
            self.go(319)
        self.go(66, 147)
        self.press(' ')
        self.press(' ')
        if self.g.scene() == 106:
            self.go(179)
        else:
            assert self.g.scene() == 213
            self.go(267)
            self.use('ENDURANCE')
            self.fight(386)
            self.go(179)
        self.go(10, 227, 320, 348, 157, 28)
        self.fight(362)
        self.go(22, 90, 370, 398, 314, 195, 58, 208, 159)

    def finish(self, page, text):
        assert self.g.scene() == page
        assert text in self.g.text()
        assert not self.g.choices()
        assert self.g.music()['slot'] == 2
        self.report.update(final=self.g.hero(), visited=sorted(self.seen),
                           final_page=page, music=self.g.music(), status='success')


def gayolard(r):
    r.begin('gayolard', ['GLACE', 'GLACE', 'BENEDICTION', 'ENDURANCE', 'HABILETE', 'FEU'])
    r.go(398, 314, 90, 370, 157, 28)
    r.fight(362)
    r.go(22, 320, 119, 381, 348, 204, 269, 367, 304, 131, 164)
    r.use('HABILETE')
    r.go(410, 248, 202, 14, 88, 121, 275, 145, 328, 244, 161, 92, 68, 215)
    r.fight(247)
    r.go(232, 389, 342, 300, 161, 121)
    r.east_return()
    r.go(6)
    assert 'BAIE' in r.g.objects()
    r.go(175)
    assert 'BAIE' not in r.g.objects()
    r.finish(175, 'SUCCES COMPLET')
    assert r.g.music()['cur'] == 'VICTORY.MB'


def pompatarte(r):
    r.begin('pompatarte', ['GLACE', 'GLACE', 'HABILETE', 'ENDURANCE', 'FEU'])
    r.go(398, 314, 90, 370, 157, 28)
    r.fight(362)
    r.go(22, 320, 368, 348, 204, 269, 367, 304, 131, 23)
    r.use('HABILETE')
    r.go(248, 202, 14, 88, 121, 218, 336, 85, 153, 65, 163, 79)
    for _ in range(40):
        if r.g.scene() in (360, 128):
            break
        r.press(' ')
    friendly = r.g.scene() == 360
    if friendly:
        r.go(214, 19)
    else:
        assert r.g.scene() == 128
        r.go(407, 19)
    r.go(280, 78, 343)
    assert 280 in r.seen and 78 in r.seen
    if friendly:
        r.go(199, 19)
    else:
        r.go(301)
        r.fight(246)
        r.go(19)
    r.go(137, 153, 218, 121)
    r.east_return()
    r.go(56, 158)
    r.finish(158, 'la carte est complete')
    assert r.g.music()['cur'] == 'VICTORY.MB'


def stratagus(r):
    r.begin('stratagus', ['MALEDICTION', 'FLETRISSURE', 'FLETRISSURE',
                         'GLACE', 'HABILETE', 'ENDURANCE'])
    r.go(398, 191, 93)
    # ED : jet de contrecoup, puis son accuse de reception.
    r.press(' ')
    r.press(' ')
    r.fight(154)
    assert 'LOUP' in r.g.amulets()
    r.go(46, 314, 195, 58, 105, 390, 144, 26)
    r.fight(354)
    assert 'ARAIGNEE' in r.g.amulets()
    r.go(165, 388, 167, 322, 81, 187, 10, 227, 320, 368, 348, 204, 80, 196)
    r.use('HABILETE')
    r.go(367, 304, 131, 288, 184)
    assert set(r.g.amulets()) == {'LOUP', 'ARAIGNEE', 'FAUSSE_OISEAU'}
    r.go(217, 250, 367, 265, 348, 157, 28)
    r.fight(362)
    r.go(22, 90, 370, 398, 314, 195, 58, 208, 159, 226, 194)
    gold = r.g.hero()['gold']
    r.go(207)
    assert r.g.hero()['gold'] == gold + 1500
    assert not r.g.amulets()
    r.go(358)
    r.finish(358, 'Mission accomplie')


ROUTES = dict(gayolard=gayolard, pompatarte=pompatarte, stratagus=stratagus)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--only', choices=ROUTES)
    ap.add_argument('--attempts', type=int, default=12)
    ap.add_argument('--port', type=int, default=6523)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    sym = pt.Symbols(pt.SRCDIR)
    baseline = Path(pt.HDV_SRC).read_bytes()
    sha = hashlib.sha256(baseline).hexdigest()
    failed = False
    for name in ([args.only] if args.only else ROUTES):
        success = False
        boot_states = set()
        for attempt in range(1, args.attempts + 1):
            stem = args.output / ('%s-%02d' % (name, attempt))
            if stem.with_suffix('.json').exists():
                raise RuntimeError('Rapport deja present : ' + str(stem))
            result = dict(route=name, attempt=attempt, disk_sha256=sha,
                          started=time.strftime('%Y-%m-%dT%H:%M:%S%z'), events=[])
            print('\n%s tentative %d/%d' % (name, attempt, args.attempts), flush=True)
            with tempfile.TemporaryDirectory(prefix='scoswamp-route-') as work:
                hdv = Path(work) / 'SCOSWAMP.hdv'
                hdv.write_bytes(baseline)
                pom = KeyboardOnlyPom2(str(hdv), port=args.port)
                g = pt.Game(pom, sym)
                r = Route(g, result)
                started = time.monotonic()
                try:
                    pom.start()
                    # Vary only the physical wait before the language key.
                    # Fast headless starts can repeatedly hit the same spin
                    # counter; replaying that seed is not another random trial.
                    pom.wait_for('LANGUE')
                    delay = .137 * attempt
                    result['language_wait_seconds'] = delay
                    time.sleep(delay)
                    g.boot('F')
                    state = pom.peek(sym['_state'], 4).hex()
                    result['boot_rng_state_le'] = state
                    if state in boot_states:
                        raise DuplicateRun('Graine deja testee : ' + state)
                    boot_states.add(state)
                    ROUTES[name](r)
                    success = True
                except DuplicateRun as exc:
                    result.update(status='duplicate', error=str(exc))
                except KeyboardInterrupt:
                    result.update(status='interrupted', error='Interruption du banc')
                    raise
                except LostRun as exc:
                    result.update(status='lost', error=str(exc))
                except Exception as exc:
                    result.update(status='error', error=repr(exc))
                finally:
                    result['seconds'] = round(time.monotonic() - started, 1)
                    try:
                        result['screen'] = g.screen()
                        result['last_hero'] = g.hero()
                        result['last_page'] = g.scene()
                    except Exception:
                        pass
                    pom.stop()
                    logfile = Path(work) / 'pom2.log'
                    if logfile.exists():
                        shutil.copyfile(logfile, stem.with_suffix('.log'))
                    stem.with_suffix('.json').write_text(json.dumps(result, indent=2) + '\n')
            print(name, result['status'], result.get('error', ''), flush=True)
            if success or result['status'] == 'error':
                break
        failed |= not success
    return int(failed)


if __name__ == '__main__':
    raise SystemExit(main())
