; Isolated destructive RAM probe, NEVER linked into the game.
; Proves a mirrored trampoline can read AUX $1000-$1DFF without moving
; the executing IRQ handler or changing ALTZP. IRQ concurrency is not tested.
.setcpu "65C02"
.segment "CODE"
ptr = $FC
start:
    sei
    sta $C002
    sta $C004
    stz $0800
    ldx #trampoline_end-trampoline-1
copy:
    lda trampoline,x
    sta $C005
    sta trampoline,x
    sta $C004
    dex
    bpl copy
    stz ptr
    lda #$10
    sta ptr+1
page:
    ldy #0
byte:
    lda #$5a
    sta (ptr),y                 ; main sentinel
    tya
    eor ptr+1
    sta $C005
    sta (ptr),y                 ; address-dependent AUX pattern
    sta $C004
    iny
    bne byte
    inc ptr+1
    lda ptr+1
    cmp #$1e
    bne page
    lda #$10
    sta ptr+1
check_page:
    ldy #0
check_byte:
    jsr trampoline
    sta $0801
    tya
    eor ptr+1
    cmp $0801
    bne fail
    lda (ptr),y
    cmp #$5a
    bne fail
    iny
    bne check_byte
    inc ptr+1
    lda ptr+1
    cmp #$1e
    bne check_page
    lda $C013                  ; RAMRD must be MAIN
    bmi fail
    lda $C014                  ; RAMWRT must be MAIN
    bmi fail
    lda #$a5
    sta $0800
halt:
    jmp halt
fail:
    lda #$ff
    sta $0800
    jmp halt
trampoline:
    sta $C003
    lda (ptr),y
    sta $C002
    rts
trampoline_end:
