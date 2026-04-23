#include "stdlib.h"
#include "unistd.h"
#include "stdio.h"
#include "time.h"

typedef struct _simple_chunk {
    char type;
    unsigned char x; unsigned char y; unsigned char z;
} simple_chunk;

typedef struct _treasure_chunk {
    char type;
    unsigned char x; unsigned char y; unsigned char z;
    unsigned char tx; unsigned char ty; unsigned char tz;
} treasure_chunk;

void *name;
void *chunk;
unsigned char posX; unsigned char posY; unsigned char posZ;
unsigned char TposX; unsigned char TposY; unsigned char TposZ;

void menu() {
    printf("[nick] %s\n", name);
    printf("[coords]  (%d, %d, %d)\n", posX, posY, posZ);
    printf("[treasure] (%hhu, %hhu, %hhu)\n", TposX, TposY, TposZ);
    puts("                  ");
    puts("   IliI11fffff1|  ");
    puts("   !IilI11ff0qo1  ");
    puts("   iliIw8BB%88W*  ");
    puts("   llOZ8Um8#b$%*  ");
    puts("   mZwm*MCwwCpb#M ");
    puts(" MMW88mob1f10M*#oo");
    puts("doM888WWa8W*W#*o#b");
    puts("pb@$$%8WWWaWWkMha ");
    puts("qq#a#o##MWaWWkMo  ");
    puts(" bB8#B#WW#o##aMM  ");
    puts(" bbBBB#a#aWWWaMa  ");
    puts(" dpBBBBaZOQkhk    ");
    puts(" bqBB8##ZQZmmm    ");
    puts("   pfJOOOLCZmm    ");
    puts("   JfJOO0fJZ0Om   ");
    puts("   JJO0OOJfZmmm   ");
    puts("   TfO0L fJQOmm   ");
    puts("    f0O   Jf0pmm  ");
    puts("          1T0mO   ");
    puts("                  ");
    printf("1) move player\n");
    printf("2) find treasure\n");
    printf("3) introduce yourself\n");
    printf("4) exit\n");
    printf("> ");
}

int count(char *string, char c) {
    int amount = 0;
    for (int i = 0; string[i] != '\0'; i++) {
        if (string[i] == c) {
            amount++;
        }
    }
    return amount;
}

void move_player() {
    char input[768];
    unsigned char posx = posX;
    unsigned char posy = posY;
    unsigned char posz = posZ;
    
    puts("r - right"); puts("l - left"); puts("u - up"); puts("d - down"); puts("w - z++"); puts("s - z--"); puts(""); puts("yeah i'm- ");
    puts("your instructions");
    printf("> ");
    read(0, input, 767);
    free(chunk); // HINT.
    
    posx += count(input, 'r'); posx -= count(input, 'l');
    posy += count(input, 'u'); posy -= count(input, 'd');
    posz += count(input, 'w'); posz -= count(input, 's');

    if (posx <= 255 && posy <= 255 && posz < 255 && posx >= 0 && posy >= 0 && posz >= 0) {
        posX = posx; posY = posy; posZ = posz;
        if (posx != TposX && posy != TposY && posz != TposZ) {
            chunk = (simple_chunk *)malloc(sizeof(simple_chunk));
            ((simple_chunk *)chunk)->type = 'S';
            ((simple_chunk *)chunk)->x = posX; ((simple_chunk *)chunk)->y = posY; ((simple_chunk *)chunk)->z = posZ;
        }
        else {
            chunk = (treasure_chunk *)malloc(sizeof(treasure_chunk));
            ((treasure_chunk *)chunk)->type = 'T';
            ((treasure_chunk *)chunk)->x = posX; ((treasure_chunk *)chunk)->y = posY; ((treasure_chunk *)chunk)->z = posZ;
            ((treasure_chunk *)chunk)->tx = 37; ((treasure_chunk *)chunk)->ty = 37; ((treasure_chunk *)chunk)->tz = 37; // HM.
        }
    }
}

void find_treasure() {
    if (*(char *)chunk == 'T') {
        if (((treasure_chunk *)chunk)->tx == 9 && ((treasure_chunk *)chunk)->ty == 4 && ((treasure_chunk *)chunk)->tz == 9) {
            system("cat flag.txt");
            exit(0);
        } else {
            puts("invalid treasure block coords :("); // treasure chunk is somewhere else..
        }
    } else {
        puts("NOT a treasure chunk..");
    }
}

void malloc_name() {
    unsigned int size;
    puts("size of your nickname");
    printf("> ");
    if (scanf("%u", &size) != 1) exit(1);
    name = malloc(size);

    puts("your nickname");
    printf("> ");
    read(0, name, size);
}

int main() {
    chunk = (simple_chunk *)malloc(sizeof(simple_chunk));
    posX = 0; posY = 0; posZ = 0;
    srand(time(0));
    TposX = rand() % 256; TposY = rand() % 256; TposZ = rand() % 256;
    unsigned int choice;
    
    while (1) {
        menu();
        if (scanf("%u", &choice) != 1) exit(1);
        switch (choice) {
            case 1:
                move_player();
                break;
            case 2: 
                find_treasure();
                break;
            case 3:
                malloc_name();
                break;
            case 4:
                exit(0);
            default: 
                break;
        }
    }
}

__attribute__((constructor))
void setup(void) {
    setvbuf(stdin, 0, _IONBF, 0);
    setvbuf(stdout, 0, _IONBF, 0);
    setvbuf(stderr, 0, _IONBF, 0);
}