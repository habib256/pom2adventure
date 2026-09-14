## Utiliser ProDOS MLI avec cc65 (Apple II)

Cette documentation explique comment les E/S fichiers sous ProDOS 8 sont gérées par la libc cc65 pour les cibles Apple II/Apple //e Enh., et comment s’en servir efficacement en C (fichiers, répertoires, buffers I/O, types ProDOS, disques, limitations).

### Aperçu

- Le système ProDOS 8 fournit une interface MLI (Machine Language Interface) accessible à l’adresse $BF00.
- La libc cc65 pour Apple II encapsule les appels MLI (OPEN, READ, WRITE, CLOSE, SET/GET_PREFIX, GET/SET_EOF, GET/SET_MARK, etc.). Vous pouvez donc utiliser les fonctions C standard (`fopen`, `fread`, `fwrite`, `fclose`, `open`, `read`, `write`, `chdir`, `getcwd`, `opendir`, …).
- Les fichiers sont résolus via le « prefix » ProDOS (répertoire courant) et/ou des chemins absolus commençant par `/`.

### Chemins et répertoires

- Séparateur: `/`.
- Chemins absolus: commencent par `/` (ex: `/DISK/PROJ/DATA/FILE.BIN`).
- Chemins relatifs: évalués par rapport au préfixe courant (défini par `chdir()` ou par l’environnement ProDOS au lancement).
- ProDOS ne gère pas `.` ni `..`. Pour « remonter », utilisez un chemin absolu explicite dans `chdir()`.
- Contraintes:
  - Longueur maximale de chemin (Apple II): `FILENAME_MAX = 64` caractères.
  - Longueur d’un composant (nom ProDOS): ≤ 15 caractères.

Exemples C simples:

```c
#include <stdio.h>
#include <unistd.h>

int main(void) {
    // Accès direct (absolu)
    FILE* f1 = fopen("/DISK/PROJ/DATA/ASSETS/SPRITE.BIN", "rb");
    if (f1) fclose(f1);

    // Navigation (préfixe) puis relatif
    if (chdir("/DISK/PROJ") != 0) return 1;
    if (chdir("DATA/ASSETS") != 0) return 1;
    FILE* f2 = fopen("SPRITE.BIN", "rb");
    if (f2) fclose(f2);
    return 0;
}
```

Pour obtenir le nom de la « racine » (volume):

```c
#include <unistd.h>
#include <stdio.h>
#include <string.h>

int main(void) {
    char cwd[FILENAME_MAX];
    if (!getcwd(cwd, sizeof(cwd))) { perror("getcwd"); return 1; }
    const char* p = (cwd[0] == '/') ? cwd + 1 : cwd;
    char volume[16]; size_t i = 0;
    while (p[i] && p[i] != '/' && i < sizeof(volume) - 1) volume[i] = p[i++];
    volume[i] = '\0';
    printf("Volume ProDOS: %s\n", volume);
    return 0;
}
```

### Mappage des appels C → ProDOS MLI

- OPEN ($C8), READ ($CA), WRITE ($CB), CLOSE ($CC): implémentent `open/read/write/close` et `fopen/fread/fwrite/fclose`.
- SET_PREFIX ($C6) / GET_PREFIX ($C7): implémentent `chdir()` et `getcwd()` (préfixe ProDOS).
- GET_EOF ($D1) / SET_EOF ($D0): taille du fichier et troncature.
- GET_MARK ($CF) / SET_MARK ($CE): position de fichier (utilisé par `lseek` / positionnement interne de la libc).
- READ_BLOCK ($80) / WRITE_BLOCK ($81): I/O bloc (API DIO de cc65) pour accéder aux blocs d’un périphérique.

Remarques:
- En lecture (`read`/`fread`), un EOF normal retourne simplement « octets lus < demandés ». L’indicateur d’erreur n’est pas activé.
- En écriture vers le « device » console, la libc peut convertir `\n` → `\r` et/ou gérer la casse selon la cible (Apple II non-enh.).

### Buffers I/O ProDOS (1 Ko par fichier)

- ProDOS 8 exige un buffer I/O de 1 KiB aligné par fichier ouvert.
- Par défaut, la libc alloue ces buffers sur le tas (`posix_memalign`).
- Alternative: lier `apple2-iobuf-0800.o` (fourni par cc65) pour placer ces buffers entre $0800 et l’adresse de début du programme; permet jusqu’à ~6 fichiers ouverts simultanément sur un programme « system » (start=$2000).

### Types et aux-types ProDOS lors de la création

Lors d’un `fopen("...", "w"/"wb")` ou `open(..., O_CREAT, ...)`, définissez le type et l’aux-type ProDOS à l’avance:

```c
#include <apple2_filetype.h>

unsigned char _filetype = PRODOS_T_TXT;  // ex: texte ASCII
unsigned int  _auxtype  = 0;             // selon le type (0 par défaut)
```

Référez-vous à `include/apple2_filetype.h` pour la liste complète des types (ex: `PRODOS_T_BIN`, `PRODOS_T_TXT`, etc.). Par défaut, `_filetype = PRODOS_T_BIN`.

### Exemple complet: lire un fichier ProDOS

```c
#include <stdio.h>
#include <errno.h>

int main(void) {
    FILE* f = fopen("/DISK/PROJ/DATA/LEVEL1.MAP", "rb");
    if (!f) { perror("fopen"); return 1; }
    unsigned char buf[256];
    size_t n = fread(buf, 1, sizeof(buf), f);
    fclose(f);
    printf("lus=%u\n", (unsigned)n);
    return 0;
}
```

### Exemple DIO (I/O bloc)

L’API DIO de cc65 permet d’appeler READ_BLOCK/WRITE_BLOCK pour des accès au niveau bloc (périphériques ProDOS). Utile pour chargements bruts:

```c
#include <dio.h>
#include <stdio.h>

int main(void) {
    unsigned char buffer[512];
    unsigned handle = dio_open(/* device = */ 6 /* ex: slot 6 drv 1 → 6 */);
    if (!handle) { puts("dio_open failed"); return 1; }

    if (dio_read(handle, /* block */ 2, buffer) != 0) {
        puts("dio_read failed");
    }
    dio_close(handle);
    return 0;
}
```

Notes:
- La numérotation `device` suit: `device = slot + (drive - 1) * 8` (ex: slot 6, drive 2 → 14).
- `dio_query_sectcount()` retourne la taille correcte pour les disques ProDOS; sur non-ProDOS, renvoie 280 et `_oserror=82`.

### Construction et disquettes ProDOS

Compiler un programme Apple II:

```bash
cl65 -t apple2 -O -o myprog myprog.c
```

Placer le binaire sur une image ProDOS (avec AppleCommander `ac.jar`) à partir d’un gabarit `prodos.dsk`:

```bash
cp prodos.dsk out.dsk
java -jar ac.jar -as out.dsk MYPROG <myprog      # AppleSingle → ProDOS
```

Pour des programmes volumineux (ou pour profiter de $0800–$1FFF), utilisez LOADER.SYSTEM: copiez LOADER.SYSTEM sous le nom `MYPROG.SYSTEM` dans le même dossier que `MYPROG`. Au chargement, LOADER va lire `MYPROG` en mémoire.

```bash
# Exemple d’ajout de LOADER.SYSTEM (fourni par cc65 dans les utilitaires de cible)
java -jar ac.jar -p out.dsk MYPROG.SYSTEM sys <LOADER.SYSTEM
```

Astuce: si vous n’avez pas installé cc65, exportez `CC65_HOME` pour que les samples/utilitaires retrouvent `target/` et `lib/`:

```bash
export CC65_HOME=$(pwd)
```

### Limitations importantes

- Offsets de fichiers: ProDOS (Apple II) supporte des positions sur 24 bits; au-delà, erreur.
- Nombre de fichiers ouverts simultanément limité par la mémoire et les buffers 1 KiB.
- Pas de `.`/`..` dans les chemins; utilisez des absolus pour naviguer « en arrière ».
- `FILENAME_MAX = 64` (chemin complet) sur Apple II; respecter ≤ 15 caractères par composant ProDOS.

### Références (dans ce dépôt)

- Appels MLI et wrapper: `libsrc/apple2/mli.inc`, `libsrc/apple2/mli.s`.
- Ouverture/lecture/écriture: `libsrc/apple2/open.s`, `libsrc/apple2/read.s`, `libsrc/apple2/write.s`, commun: `libsrc/apple2/rwcommon.s`.
- Préfixe/CWD: `libsrc/apple2/initcwd.s`, `libsrc/apple2/syschdir.s`.
- LOADER.SYSTEM: `libsrc/apple2/targetutil/loader.s`, `libsrc/apple2/targetutil/loader.cfg`.
- Types ProDOS: `include/apple2_filetype.h`.
- Docs Apple II: `doc/apple2.sgml`, `doc/apple2enh.sgml`.

---

Si vous avez un cas d’usage précis (ex: créer des fichiers texte ProDOS, ou charger de gros segments via LOADER.SYSTEM), ajoutez un exemple à la fin de ce document et indiquez la configuration ld65 utilisée (`cfg/apple2*.cfg`).


