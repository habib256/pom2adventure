#!/usr/bin/env python3
"""Parcours Gayolard par touches uniquement, sans sauvegarde forgee.

python3 -u SCOSWAMP.MORE/TOOLS/win_gayolard.py --only victoire_reelle --port 6523
Les combats restent aleatoires : une mort est un echec, jamais escamotee.
"""
import sys, struct
from playtest import *

@scenario('victoire_reelle', 'Gayolard du debut a la baie, sans teleportation ni modification des statistiques')
def win(g,b):
 def target(n):
  count=g.p.peek(g.A('num_choices'),1)[0]
  ids=[struct.unpack('<h',g.p.peek(g.A('choices')+8*i,2))[0] for i in range(count)]
  if n not in ids: raise AssertionError('page %d: cible %d absente de %r'%(g.scene(),n,ids))
  letter=chr(65+ids.index(n)); print('%03d %s -> %03d'%(g.scene(),letter,n),flush=True)
  rows=g.press(letter)
  if g.hero()['end']==0: raise AssertionError('mort page %d'%g.scene())
  return rows
 def path(ns):
  for n in ns:
   if g.p.peek(g.A('dice_n'),1)==b'\x03' and any('Tentez votre Chance' in r for r in g.p.screen()):
    g.press(' ');g.press(' ')
   if g.scene()!=n: target(n)
 def fight(dest):
  for i in range(160):
   if g.scene()==dest:return
   if g.hero()['end']==0:raise AssertionError('mort au combat %d'%g.scene())
   g.press(' ')
  raise AssertionError('combat interminable')
 g.press('A'); print('Heros tire normalement:',g.hero(),flush=True); g.press(' ')
 path([1,95,240,205,335,371])
 for key in 'EEIBAD':g.press(key) # GLACE x2, BENEDICTION, ENDURANCE, HABILETE, FEU
 print('Pierres:',g.stones(),flush=True)
 path([9,195,58,398,314,90,370,157,28]); fight(362)
 path([22,320,119,381,348,204,269,367,304,131,164]); g.press("I");g.press("A");g.press(" ");g.press("I"); path([410,248,202,14,88,121,275,145,328,244,161,92,68,215]);fight(247)
 path([232,389,342,300,161,121,14,88,331,112,202,138,101,118])
 # Le test CL des scorpions : reponse et accuse de reception.
 g.press(' ');g.press(' ')
 if g.scene()==70:path([110,319])
 elif g.scene()==182:
  g.press(' ');g.press(' ');target(319)
 else:raise AssertionError('branche scorpions %d'%g.scene())
 path([66,147]);g.press(' ');g.press(' ')
 if g.scene()==106:target(179)
 else:
  target(267)
  if g.stones().get('ENDURANCE'):
   g.press('I');g.press('A');g.press(' ');g.press('I') # ENDURANCE premiere pierre restante
  fight(386);target(179)
 path([10,227,320,348,157,28]);fight(362)
 path([22,90,370,398,314,195,58,208,159,6])
 b.check('la baie a ete rapportee', 'BAIE' in g.objects())
 rows=target(175)
 b.eq('la victoire est atteinte',g.scene(),175)
 b.has('le succes est affiche',rows,'SUCCES COMPLET')
 b.eq('la baie a ete remise',g.objects().count('BAIE'),0)
 b.eq('la musique de victoire joue',g.music()['cur'],'VICTORY.MB')
 print('Heros final:',g.hero(),flush=True)
if __name__ == '__main__':
 SCENARIOS[:] = [s for s in SCENARIOS if s['name'] == 'victoire_reelle']
 sys.exit(main())
