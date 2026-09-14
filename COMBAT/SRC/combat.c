#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <conio.h>
#include <apple2enh.h>

/* Adresse de la page HGR 1 */
#define HGR_PAGE1 ((unsigned char*)0x2000)
#define HGR_SIZE  8192
#define MAX_LINE  120
#define MAX_MONSTERS 10
#define MAX_PATH  64

/* Structure pour le joueur */
typedef struct {
    unsigned char hp;           /* Points de vie actuels */
    unsigned char max_hp;       /* PV maximum */
    unsigned char attack;      /* Force d'attaque */
    unsigned char defense;      /* Defense */
    unsigned char level;        /* Niveau du joueur */
    unsigned int experience;    /* Points d'experience */
} Player;

/* Structure pour les monstres */
typedef struct {
    char name[20];              /* Nom du monstre */
    unsigned char hp;           /* PV du monstre */
    unsigned char max_hp;       /* PV max */
    unsigned char attack;       /* Attaque */
    unsigned char defense;      /* Defense */
    unsigned char xp_reward;    /* XP donnes a la mort */
    unsigned char scene_id;     /* Scene ou il apparait */
    char image_file[20];        /* Nom du fichier image HGR */
} Monster;

/* Variables globales */
Player player;
Monster monsters[MAX_MONSTERS];
int current_monster = -1;
int combat_active = 0;
int display_mode = 0;  /* 0 = mode texte, 1 = mode HGR */
char language[3] = "FR";
char monster_img_path[MAX_PATH];

/* Fonction pour jouer un son */
void play_sound(int type) {
    switch(type) {
        case 0: /* Bip simple */
            __asm__("sta $C030");
            break;
        case 1: /* Son de victoire */
            __asm__("sta $C030");
            __asm__("sta $C030");
            __asm__("sta $C030");
            break;
        case 2: /* Son de défaite */
            __asm__("sta $C030");
            break;
    }
}

/* Fonction utilitaire pour gérer les HP de manière sécurisée */
void safe_hp_subtract(unsigned char* hp, int damage) {
    if (damage >= *hp) {
        *hp = 0;
    } else {
        *hp -= damage;
    }
}

/* Fonction utilitaire pour ajouter des HP de manière sécurisée */
void safe_hp_add(unsigned char* hp, unsigned char* max_hp, int amount) {
    if (*hp + amount > *max_hp) {
        *hp = *max_hp;
    } else {
        *hp += amount;
    }
}

/* Générateur de nombres aléatoires amélioré pour Apple II */
static unsigned int random_seed = 1;

/* Fonction de génération de nombres aléatoires */
int apple_rand(void) {
    /* Générateur linéaire congruentiel simple */
    random_seed = (random_seed * 1103515245U + 12345U) & 0x7FFFFFFFU;
    return (int)(random_seed % 32768U);
}

/* Initialiser le générateur avec une valeur variable */
void init_random(void) {
    /* Utiliser l'adresse mémoire comme graine pour plus de variabilité */
    random_seed = (unsigned int)(0x2000 + (unsigned char)0x00);
}

/* Fonction de test pour vérifier la qualité du générateur aléatoire */
void test_random_generator(void) {
    int i;
    int counts[4] = {0, 0, 0, 0};
    int value;
    
    if (strcmp(language, "FR") == 0) {
        cprintf("=== TEST DU GENERATEUR ALEATOIRE ===\r\n");
    } else {
        cprintf("=== RANDOM GENERATOR TEST ===\r\n");
    }
    
    /* Tester 1000 tirages de 1d4 */
    for (i = 0; i < 1000; i++) {
        value = (apple_rand() % 4) + 1;
        if (value >= 1 && value <= 4) {
            counts[value - 1]++;
        }
    }
    
    /* Afficher les résultats */
    for (i = 0; i < 4; i++) {
        cprintf("Valeur %d: %d fois\r\n", i + 1, counts[i]);
    }
    
    cprintf("Appuyez sur une touche...\r\n");
    cgetc();
}

/* Soft switches pour les modes video */
void set_video_mode(int mode) {
    if (mode == 0) {
        /* Mode texte 80 colonnes */
        __asm__("sta $C051");  /* TXTSET */
    } else {
        /* Mode HGR plein écran */
        __asm__("sta $C050");  /* TXTCLR */
        __asm__("sta $C057");  /* HIRES */
        __asm__("sta $C054");  /* LOWSCR */
        __asm__("sta $C052");  /* MIXCLR */
    }
}

/* Charger une image de monstre */
int load_monster_image(const char* filename) {
    FILE* f;
    size_t bytes_read;
    
    /* Construire le chemin complet */
    sprintf(monster_img_path, "IMG/MONSTERS/%s", filename);
    
    /* Ouvrir le fichier HGR */
    f = fopen(monster_img_path, "rb");
    if (!f) {
        return 0;  /* Pas d'image pour ce monstre */
    }
    
    /* Lire exactement 8192 octets dans la page HGR 1 */
    bytes_read = fread(HGR_PAGE1, 1, HGR_SIZE, f);
    fclose(f);
    
    return (bytes_read == HGR_SIZE) ? 1 : 0;
}

/* Initialiser le joueur */
void init_player(void) {
    player.hp = 20;
    player.max_hp = 20;
    player.attack = 5;
    player.defense = 3;
    player.level = 1;
    player.experience = 0;
    
    /* Vérifications de sécurité */
    if (player.hp > player.max_hp) {
        player.hp = player.max_hp;
    }
    if (player.hp == 0 && player.max_hp > 0) {
        player.hp = 1;  /* Éviter HP à 0 au début */
    }
}

/* Initialiser les monstres */
void init_monsters(void) {
    /* Monstre 0: Spore Cosmique */
    strcpy(monsters[0].name, "Spore Cosmique");
    monsters[0].hp = 8;
    monsters[0].max_hp = 8;
    monsters[0].attack = 3;
    monsters[0].defense = 1;
    monsters[0].xp_reward = 10;
    strcpy(monsters[0].image_file, "SPORE01.HGR");
    
    /* Monstre 1: Alien Vortex */
    strcpy(monsters[1].name, "Alien Vortex");
    monsters[1].hp = 18;
    monsters[1].max_hp = 18;
    monsters[1].attack = 6;
    monsters[1].defense = 3;
    monsters[1].xp_reward = 25;
    strcpy(monsters[1].image_file, "ALIEN01.HGR");
    
    /* Monstre 2: Robot Sentinel */
    strcpy(monsters[2].name, "Robot Sentinel");
    monsters[2].hp = 22;
    monsters[2].max_hp = 22;
    monsters[2].attack = 7;
    monsters[2].defense = 5;
    monsters[2].xp_reward = 30;
    strcpy(monsters[2].image_file, "ROBOT01.HGR");
    
    /* Monstre 3: Baleine Celeste */
    strcpy(monsters[3].name, "Baleine Celeste");
    monsters[3].hp = 30;
    monsters[3].max_hp = 30;
    monsters[3].attack = 10;
    monsters[3].defense = 6;
    monsters[3].xp_reward = 50;
    strcpy(monsters[3].image_file, "SPACE01.HGR");
    
    /* Monstre 4: Guardian Magnetar */
    strcpy(monsters[4].name, "Guardian Magnetar");
    monsters[4].hp = 50;
    monsters[4].max_hp = 50;
    monsters[4].attack = 15;
    monsters[4].defense = 10;
    monsters[4].xp_reward = 100;
    strcpy(monsters[4].image_file, "BOSS01.HGR");
}

/* Afficher la barre de statut */
void display_status_bar(void) {
    int i;
    int hp_bars;
    
    cprintf("HP: ");
    
    /* Calculer le nombre de barres à afficher */
    if (player.max_hp > 0) {
        hp_bars = (player.hp * 10) / player.max_hp;
    } else {
        hp_bars = 0;
    }
    
    /* S'assurer que hp_bars est dans la plage 0-10 */
    if (hp_bars < 0) hp_bars = 0;
    if (hp_bars > 10) hp_bars = 10;
    
    /* Afficher barre de vie */
    for (i = 0; i < 10; i++) {
        if (i < hp_bars) {
            cprintf("#");  /* Caractère # au lieu de █ */
        } else {
            cprintf(".");  /* Caractère . au lieu de ░ */
        }
    }
    cprintf(" %d/%d  LVL:%d  XP:%d  ATK:%d  DEF:%d\r\n", 
            player.hp, player.max_hp, player.level, 
            player.experience, player.attack, player.defense);
}

/* Basculer entre mode HGR et mode texte */
void toggle_display_mode(void) {
    display_mode = !display_mode;
    
    if (display_mode == 1) {
        /* Mode HGR - afficher l'image du monstre */
        set_video_mode(1);
        
        /* Charger l'image du monstre si disponible */
        if (current_monster >= 0 && current_monster < MAX_MONSTERS) {
            load_monster_image(monsters[current_monster].image_file);
        }
        
        /* Attendre un peu pour l'affichage */
        __asm__("nop");
        __asm__("nop");
    } else {
        /* Mode texte - afficher l'interface de combat */
        set_video_mode(0);
        videomode(VIDEOMODE_80COL);
        clrscr();
        
        /* Afficher les stats du monstre */
        if (current_monster >= 0) {
            int i;
            int monster_hp_bars;
            
            cprintf("=== %s ===\r\n", monsters[current_monster].name);
            cprintf("HP Monstre: ");
            
            /* Calculer le nombre de barres à afficher pour le monstre */
            if (monsters[current_monster].max_hp > 0) {
                monster_hp_bars = (monsters[current_monster].hp * 10) / monsters[current_monster].max_hp;
            } else {
                monster_hp_bars = 0;
            }
            
            /* S'assurer que monster_hp_bars est dans la plage 0-10 */
            if (monster_hp_bars < 0) monster_hp_bars = 0;
            if (monster_hp_bars > 10) monster_hp_bars = 10;
            
            /* Afficher barre de vie du monstre */
            for (i = 0; i < 10; i++) {
                if (i < monster_hp_bars) {
                    cprintf("#");  /* Caractère # au lieu de █ */
                } else {
                    cprintf(".");  /* Caractère . au lieu de ░ */
                }
            }
            cprintf(" %d/%d\r\n", monsters[current_monster].hp, monsters[current_monster].max_hp);
            cprintf("ATK: %d  DEF: %d\r\n", monsters[current_monster].attack, monsters[current_monster].defense);
        }
        
        cprintf("\r\n");
        
        /* Afficher les stats du joueur */
        display_status_bar();
        
        cprintf("\r\n");
        
        /* Afficher les options de combat */
        if (strcmp(language, "FR") == 0) {
            cprintf("=== OPTIONS DE COMBAT ===\r\n");
            cprintf("[A] Attaquer  [D] Defendre  [F] Fuir  [Q] Quitter  [ESPACE] Basculer affichage\r\n");
        } else {
            cprintf("=== COMBAT OPTIONS ===\r\n");
            cprintf("[A] Attack  [D] Defend  [F] Flee  [Q] Quit  [SPACE] Toggle display\r\n");
        }
    }
}

/* Afficher l'écran de combat */
void display_combat_screen(void) {
    /* Utiliser le mode d'affichage actuel */
    if (display_mode == 1) {
        /* Mode HGR - afficher l'image du monstre */
        set_video_mode(1);
        
        /* Charger l'image du monstre si disponible */
        if (current_monster >= 0 && current_monster < MAX_MONSTERS) {
            load_monster_image(monsters[current_monster].image_file);
        }
        
        /* Attendre un peu pour l'affichage */
        __asm__("nop");
        __asm__("nop");
    } else {
        /* Mode texte - afficher l'interface de combat */
        set_video_mode(0);
        videomode(VIDEOMODE_80COL);
        clrscr();
        
        /* Afficher les stats du monstre */
        if (current_monster >= 0) {
            int i;
            int monster_hp_bars;
            
            cprintf("=== %s ===\r\n", monsters[current_monster].name);
            cprintf("HP Monstre: ");
            
            /* Calculer le nombre de barres à afficher pour le monstre */
            if (monsters[current_monster].max_hp > 0) {
                monster_hp_bars = (monsters[current_monster].hp * 10) / monsters[current_monster].max_hp;
            } else {
                monster_hp_bars = 0;
            }
            
            /* S'assurer que monster_hp_bars est dans la plage 0-10 */
            if (monster_hp_bars < 0) monster_hp_bars = 0;
            if (monster_hp_bars > 10) monster_hp_bars = 10;
            
            /* Afficher barre de vie du monstre */
            for (i = 0; i < 10; i++) {
                if (i < monster_hp_bars) {
                    cprintf("#");  /* Caractère # au lieu de █ */
                } else {
                    cprintf(".");  /* Caractère . au lieu de ░ */
                }
            }
            cprintf(" %d/%d\r\n", monsters[current_monster].hp, monsters[current_monster].max_hp);
            cprintf("ATK: %d  DEF: %d\r\n", monsters[current_monster].attack, monsters[current_monster].defense);
        }
        
        cprintf("\r\n");
        
        /* Afficher les stats du joueur */
        display_status_bar();
        
        cprintf("\r\n");
        
        /* Afficher les options de combat */
        if (strcmp(language, "FR") == 0) {
            cprintf("=== OPTIONS DE COMBAT ===\r\n");
            cprintf("[A] Attaquer  [D] Defendre  [F] Fuir  [Q] Quitter  [ESPACE] Basculer affichage\r\n");
        } else {
            cprintf("=== COMBAT OPTIONS ===\r\n");
            cprintf("[A] Attack  [D] Defend  [F] Flee  [Q] Quit  [SPACE] Toggle display\r\n");
        }
    }
}

/* Calculer les dégâts */
int calculate_damage(int attacker_atk, int defender_def) {
    int base_damage;
    int random_bonus;
    int damage;
    
    /* Dégâts de base : ATK - DEF/2 */
    base_damage = attacker_atk - (defender_def / 2);
    
    /* Bonus aléatoire : 1d4 (1-4) avec notre générateur */
    random_bonus = (apple_rand() % 4) + 1;
    
    /* Dégâts finaux */
    damage = base_damage + random_bonus;
    
    /* Minimum 1 dégât */
    return (damage > 0) ? damage : 1;
}

/* Attaquer */
void player_attack(void) {
    int damage;
    
    if (current_monster < 0) return;
    
    damage = calculate_damage(player.attack, monsters[current_monster].defense);
    
    /* Utiliser la fonction sécurisée pour les HP du monstre */
    safe_hp_subtract(&monsters[current_monster].hp, damage);
    
    if (strcmp(language, "FR") == 0) {
        cprintf("Vous attaquez pour %d degats !\r\n", damage);
    } else {
        cprintf("You attack for %d damage!\r\n", damage);
    }
    
    play_sound(0);
}

/* Le monstre attaque */
void monster_attack(void) {
    int damage;
    
    if (current_monster < 0) return;
    
    damage = calculate_damage(monsters[current_monster].attack, player.defense);
    
    /* Utiliser la fonction sécurisée pour les HP du joueur */
    safe_hp_subtract(&player.hp, damage);
    
    if (strcmp(language, "FR") == 0) {
        cprintf("%s vous attaque pour %d degats !\r\n", monsters[current_monster].name, damage);
    } else {
        cprintf("%s attacks you for %d damage!\r\n", monsters[current_monster].name, damage);
    }
    
    play_sound(0);
}

/* Vérifier la montée de niveau */
void check_level_up(void) {
    int xp_required;
    
    /* Calculer XP requis pour le niveau suivant */
    xp_required = 50 * player.level * (player.level + 1) / 2;
    
    if (player.experience >= xp_required) {
        player.level++;
        
        /* Gestion sécurisée des HP max */
        if (player.max_hp < 255 - 5) {
            player.max_hp += 5;
        } else {
            player.max_hp = 255;  /* Limite maximale */
        }
        
        /* Restaurer complètement les HP de manière sécurisée */
        if (player.max_hp > 0) {
            player.hp = player.max_hp;
        } else {
            player.hp = 1;  /* Éviter HP à 0 */
        }
        
        /* Gestion sécurisée des stats */
        if (player.attack < 255 - 2) {
            player.attack += 2;
        } else {
            player.attack = 255;
        }
        
        if (player.defense < 255 - 1) {
            player.defense += 1;
        } else {
            player.defense = 255;
        }
        
        if (strcmp(language, "FR") == 0) {
            cprintf("\r\n*** NIVEAU SUPERIEUR ! ***\r\n");
            cprintf("Niveau %d atteint !\r\n", player.level);
            cprintf("HP max +5, ATK +2, DEF +1\r\n");
        } else {
            cprintf("\r\n*** LEVEL UP ! ***\r\n");
            cprintf("Level %d reached!\r\n", player.level);
            cprintf("Max HP +5, ATK +2, DEF +1\r\n");
        }
        
        play_sound(1);
        cprintf("Appuyez sur une touche...\r\n");
        cgetc();
    }
}

/* Gérer la victoire */
void handle_victory(void) {
    if (current_monster < 0) return;
    
    player.experience += monsters[current_monster].xp_reward;
    
    if (strcmp(language, "FR") == 0) {
        cprintf("\r\n*** VICTOIRE ! ***\r\n");
        cprintf("Vous avez vaincu %s !\r\n", monsters[current_monster].name);
        cprintf("+%d XP gagne !\r\n", monsters[current_monster].xp_reward);
    } else {
        cprintf("\r\n*** VICTORY ! ***\r\n");
        cprintf("You defeated %s !\r\n", monsters[current_monster].name);
        cprintf("+%d XP gained!\r\n", monsters[current_monster].xp_reward);
    }
    
    play_sound(1);
    cprintf("Appuyez sur une touche...\r\n");
    cgetc();
    
    check_level_up();
    combat_active = 0;
}

/* Gérer la défaite */
void handle_defeat(void) {
    if (strcmp(language, "FR") == 0) {
        cprintf("\r\n*** GAME OVER ***\r\n");
        cprintf("Vous avez ete vaincu par %s !\r\n", monsters[current_monster].name);
        cprintf("Niveau atteint: %d\r\n", player.level);
        cprintf("XP final: %d\r\n", player.experience);
    } else {
        cprintf("\r\n*** GAME OVER ***\r\n");
        cprintf("You were defeated by %s !\r\n", monsters[current_monster].name);
        cprintf("Level reached: %d\r\n", player.level);
        cprintf("Final XP: %d\r\n", player.experience);
    }
    
    play_sound(2);
    cprintf("Appuyez sur une touche...\r\n");
    cgetc();
    
    /* Réinitialiser le joueur */
    init_player();
    combat_active = 0;
}

/* Tenter de fuir */
int try_flee(void) {
    int flee_chance;
    int roll;
    
    flee_chance = 50 + (player.level * 5);
    if (flee_chance > 95) flee_chance = 95;
    
    roll = apple_rand() % 100;
    
    if (roll < flee_chance) {
        if (strcmp(language, "FR") == 0) {
            cprintf("Vous reussissez a fuir !\r\n");
        } else {
            cprintf("You successfully flee!\r\n");
        }
        combat_active = 0;
        return 1;
    } else {
        if (strcmp(language, "FR") == 0) {
            cprintf("Echec de la fuite !\r\n");
        } else {
            cprintf("Flee failed!\r\n");
        }
        return 0;
    }
}

/* Boucle de combat principale */
void combat_loop(void) {
    char key;
    
    while (combat_active) {
        display_combat_screen();
        
        /* Vérifier les conditions de fin */
        if (player.hp <= 0) {
            handle_defeat();
            return;
        }
        
        if (current_monster >= 0 && monsters[current_monster].hp <= 0) {
            handle_victory();
            return;
        }
        
        key = cgetc();
        
        switch (key) {
            case 'A':
            case 'a':
                player_attack();
                if (current_monster >= 0 && monsters[current_monster].hp > 0) {
                    monster_attack();
                }
                break;
                
            case 'D':
            case 'd':
                if (strcmp(language, "FR") == 0) {
                    cprintf("Vous vous defendez ! (Defense x2 pour 1 tour)\r\n");
                } else {
                    cprintf("You defend! (Defense x2 for 1 turn)\r\n");
                }
                /* La défense double pour ce tour */
                player.defense *= 2;
                monster_attack();
                player.defense /= 2;  /* Restaurer */
                break;
                
            case 'F':
            case 'f':
                if (try_flee()) {
                    return;
                }
                monster_attack();
                break;
                
            case 'Q':
            case 'q':
                combat_active = 0;
                return;
                
            case ' ':  /* Touche espace */
                toggle_display_mode();
                break;
        }
        
        cprintf("Appuyez sur une touche...\r\n");
        cgetc();
    }
}

/* Démarrer un combat */
void start_combat(int monster_id) {
    if (monster_id < 0 || monster_id >= MAX_MONSTERS) return;
    
    current_monster = monster_id;
    combat_active = 1;
    display_mode = 0;  /* Commencer en mode texte */
    
    /* Restaurer les HP du monstre */
    monsters[current_monster].hp = monsters[current_monster].max_hp;
    
    if (strcmp(language, "FR") == 0) {
        cprintf("Un %s sauvage apparait !\r\n", monsters[current_monster].name);
    } else {
        cprintf("A wild %s appears!\r\n", monsters[current_monster].name);
    }
    
    cprintf("Appuyez sur une touche pour commencer le combat...\r\n");
    cgetc();
    
    combat_loop();
}

/* Afficher le menu principal */
void display_main_menu(void) {
    clrscr();
    
    if (strcmp(language, "FR") == 0) {
        cprintf("          ====================================================\r\n");
        cprintf("                     SYSTEME DE COMBAT APPLE II\r\n");
        cprintf("          ====================================================\r\n");
        cprintf("\r\n");
        cprintf("  [A] Combattre Spore Cosmique (Facile)\r\n");
        cprintf("  [B] Combattre Alien Vortex (Moyen)\r\n");
        cprintf("  [C] Combattre Robot Sentinel (Moyen)\r\n");
        cprintf("  [D] Combattre Baleine Celeste (Difficile)\r\n");
        cprintf("  [E] Combattre Guardian Magnetar (BOSS)\r\n");
        cprintf("  [S] Afficher les statistiques\r\n");
        cprintf("  [T] Test du generateur aleatoire\r\n");
        cprintf("  [L] Changer la langue\r\n");
        cprintf("  [Q] Quitter\r\n");
        cprintf("\r\n");
        display_status_bar();
    } else {
        cprintf("          ====================================================\r\n");
        cprintf("                     APPLE II COMBAT SYSTEM\r\n");
        cprintf("          ====================================================\r\n");
        cprintf("\r\n");
        cprintf("  [A] Fight Cosmic Spore (Easy)\r\n");
        cprintf("  [B] Fight Alien Vortex (Medium)\r\n");
        cprintf("  [C] Fight Robot Sentinel (Medium)\r\n");
        cprintf("  [D] Fight Celestial Whale (Hard)\r\n");
        cprintf("  [E] Fight Guardian Magnetar (BOSS)\r\n");
        cprintf("  [S] Show statistics\r\n");
        cprintf("  [T] Test random generator\r\n");
        cprintf("  [L] Change language\r\n");
        cprintf("  [Q] Quit\r\n");
        cprintf("\r\n");
        display_status_bar();
    }
}

/* Afficher les statistiques */
void display_statistics(void) {
    clrscr();
    
    if (strcmp(language, "FR") == 0) {
        cprintf("=== STATISTIQUES DU JOUEUR ===\r\n");
        cprintf("Niveau: %d\r\n", player.level);
        cprintf("Points de vie: %d/%d\r\n", player.hp, player.max_hp);
        cprintf("Attaque: %d\r\n", player.attack);
        cprintf("Defense: %d\r\n", player.defense);
        cprintf("Experience: %d\r\n", player.experience);
        cprintf("\r\n");
        cprintf("XP requis pour niveau %d: %d\r\n", 
                player.level + 1, 
                50 * (player.level + 1) * (player.level + 2) / 2);
    } else {
        cprintf("=== PLAYER STATISTICS ===\r\n");
        cprintf("Level: %d\r\n", player.level);
        cprintf("Hit Points: %d/%d\r\n", player.hp, player.max_hp);
        cprintf("Attack: %d\r\n", player.attack);
        cprintf("Defense: %d\r\n", player.defense);
        cprintf("Experience: %d\r\n", player.experience);
        cprintf("\r\n");
        cprintf("XP required for level %d: %d\r\n", 
                player.level + 1, 
                50 * (player.level + 1) * (player.level + 2) / 2);
    }
    
    cprintf("\r\nAppuyez sur une touche...\r\n");
    cgetc();
}

/* Changer la langue */
void change_language(void) {
    char key;
    
    clrscr();
    
    cprintf("=== SELECT LANGUAGE / LANGUE ===\r\n");
    cprintf("\r\n");
    cprintf("  [F] - Francais\r\n");
    cprintf("  [E] - English\r\n");
    cprintf("\r\n");
    
    key = cgetc();
    if (key == 'F' || key == 'f') {
        strcpy(language, "FR");
    } else if (key == 'E' || key == 'e') {
        strcpy(language, "EN");
    }
}

void main(void) {
    char key;
    
    /* Initialiser notre générateur de nombres aléatoires amélioré */
    init_random();
    
    /* Initialiser le joueur et les monstres */
    init_player();
    init_monsters();
    
    /* Écran de titre */
    videomode(VIDEOMODE_80COL);
    clrscr();
    
    cprintf("\r\n\r\n");
    cprintf("          ====================================================\r\n");
    cprintf("                     SYSTEME DE COMBAT APPLE II\r\n");
    cprintf("          ====================================================\r\n");
    cprintf("\r\n");
    cprintf("                    Un RPG de Combat Spatial\r\n");
    cprintf("                         Combat RPG System\r\n");
    cprintf("\r\n");
    cprintf("               2025 Apple II Port by : Arnaud VERHILLE\r\n");
    cprintf("                                  (@habib256)\r\n");
    cprintf("\r\n\r\n");
    cprintf("          ====================================================\r\n");
    
    cprintf("Appuyez sur une touche pour commencer...\r\n");
    cgetc();
    
    /* Boucle principale */
    while (1) {
        display_main_menu();
        
        key = cgetc();
        
        switch (key) {
            case 'A':
            case 'a':
                start_combat(0);
                break;
            case 'B':
            case 'b':
                start_combat(1);
                break;
            case 'C':
            case 'c':
                start_combat(2);
                break;
            case 'D':
            case 'd':
                start_combat(3);
                break;
            case 'E':
            case 'e':
                start_combat(4);
                break;
            case 'S':
            case 's':
                display_statistics();
                break;
            case 'T':
            case 't':
                test_random_generator();
                break;
            case 'L':
            case 'l':
                change_language();
                break;
            case 'Q':
            case 'q':
                set_video_mode(0);
                videomode(VIDEOMODE_40COL);
                clrscr();
                if (strcmp(language, "FR") == 0) {
                    cprintf("Au revoir!\r\n");
                } else {
                    cprintf("Goodbye!\r\n");
                }
                return;
        }
    }
}
