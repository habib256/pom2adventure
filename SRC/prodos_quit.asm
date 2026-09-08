;
; prodos_quit.asm - Sortie propre vers ProDOS 8
;
; Nécessaire pour tout binaire lié avec SRC/apple2enh-game.cfg.
;
; Cette configuration porte __HIMEM__ à $BF00 pour récupérer les 10 496 octets
; que BASIC.SYSTEM occupe en $9600-$BEFF. La BSS et le tas s'y étendent et le
; détruisent en cours d'exécution.
;
; exit() rendrait donc la main à un BASIC.SYSTEM qui n'existe plus : la machine
; part dans le décor. Il faut demander à ProDOS de relancer son propre sélecteur
; de programme, via l'appel MLI QUIT.
;
; Écrit en assembleur et non en C : l'appel MLI place ses arguments DANS le flux
; d'instructions, juste après le JSR. Le __asm__ de cc65 n'accepte pas les
; pseudo-instructions .byte / .word nécessaires pour cela.
;
; Extension .asm et non .s : le .gitignore écarte les *.s, qui sont les fichiers
; intermédiaires produits par cc65 à partir des .c.
;
; Auteur  : Arnaud VERHILLE (@habib256)
; Licence : GNU GPL v3.0
;

        .export         _prodos_quit

MLI     = $BF00                 ; point d'entrée ProDOS 8, page globale
QUIT    = $65                   ; code de commande QUIT

        .code

; void prodos_quit(void);
;
; Séquence d'appel MLI ProDOS 8 :
;     JSR MLI
;     DFB commande
;     DW  table_de_parametres
; L'appel rend la main à l'instruction suivant le mot de 16 bits — sauf QUIT,
; qui ne revient jamais.
_prodos_quit:
        jsr     MLI
        .byte   QUIT
        .word   quit_parms

; Inatteignable. Boucle de sécurité : si QUIT échouait, mieux vaut figer la
; machine que d'exécuter les octets suivants comme du code.
:       bra     :-

        .rodata

; Table de paramètres QUIT : 7 octets.
;   +0  nombre de paramètres = 4
;   +1  type de quit         = 0  (retour au sélecteur standard)
;   +2  réservé (mot)        = 0
;   +4  réservé              = 0
;   +5  réservé (mot)        = 0
quit_parms:
        .byte   4               ; nombre de paramètres
        .byte   0               ; type de quit
        .word   0               ; réservé
        .byte   0               ; réservé
        .word   0               ; réservé
