#define USE_TI89
#define SAVE_SCREEN
#define MIN_AMS 100
#define OPTIMIZE_ROM_CALLS

#include <tigcclib.h>

#define WIDTH {}
#define HEIGHT {}
#define FPS {}
#define TOTAL_STR {}

// A derivative of FastDrawHLine_R from ExtGraph by TICT.
void SpecialFastDrawHLine_R(void* line asm("a0"), unsigned short x1 asm("d0"), unsigned short x2 asm("d1"), unsigned short mode asm("d3"));
asm ("
| Valid values for mode are: A_REVERSE, A_NORMAL, A_REPLACE, A_OR (A_XOR removed).
|
| This routine draws a horizontal line from (x1) to (x2) on the given line address.

.text
.even
0:
.word 0xFFFF,0x7FFF,0x3FFF,0x1FFF,0x0FFF,0x07FF,0x03FF,0x01FF,0x00FF,0x007F,0x003F,0x001F,0x000F,0x0007,0x0003,0x0001

1:
.word 0x8000,0xC000,0xE000,0xF000,0xF800,0xFC00,0xFE00,0xFF00,0xFF80,0xFFC0,0xFFE0,0xFFF0,0xFFF8,0xFFFC,0xFFFE,0xFFFF

.globl SpecialFastDrawHLine_R
SpecialFastDrawHLine_R:
    move.l   %d4,%a1                         | d4 mustn't be destroyed.

    | Removed: test and fix for reversed x1 and x2.

    | Largely optimized: line address computation.
    move.w   %d0,%d4
    lsr.w    #4,%d4
    adda.w   %d4,%a0
    adda.w   %d4,%a0

| d4 = 8 * (x1/16 + x1/16) + 16. We add 1 before shifting instead of adding 16
| after shifting (gain: 4 clocks and 2 bytes).
    addq.w   #1,%d4                          | d4 = 8 * (x1/16 + x1/16) + 16.
    lsl.w    #4,%d4

    move.w   %d1,%d2                         | x2 is stored in d2.
    andi.w   #0xF,%d0

    add.w    %d0,%d0
    move.w   0b(%pc,%d0.w),%d0 | d0 = mask of first pixels.
    andi.w   #0xF,%d1

    add.w    %d1,%d1
    move.w   1b(%pc,%d1.w),%d1   | d1 = mask of last pixels.
    cmp.w    %d4,%d2                         | All pixels in the same word ?
    blt.s    4f
    sub.w    %d4,%d2                         | d2 = x2 - x.
    moveq.l  #32,%d4
    tst.w    %d3
    beq.s    0f

| A_NORMAL / A_OR / A_REPLACE.
    or.w     %d0,(%a0)+
    moveq    #-1,%d0
    sub.w    %d4,%d2
    blt.s    5f
6:
    move.l   %d0,(%a0)+
    sub.w    %d4,%d2
    bge.s    6b
5:
    cmpi.w   #-16,%d2
    blt.s    7f
    move.w   %d0,(%a0)+
7:
    or.w     %d1,(%a0)
    move.l   %a1,%d4
    rts

| A_REVERSE.
0:
    not.w    %d0
    and.w    %d0,(%a0)+
    moveq    #0,%d0
    sub.w    %d4,%d2
    blt.s    5f
6:
    move.l   %d0,(%a0)+
    sub.w    %d4,%d2
    bge.s    6b
5:
    cmpi.w   #-16,%d2
    blt.s    8f
    move.w   %d0,(%a0)+
8:
    not.w    %d1
    and.w    %d1,(%a0)
    move.l   %a1,%d4
    rts

4:
    and.w    %d0,%d1
    tst.w    %d3
    beq.s    8b
    or.w     %d1,(%a0)
    move.l   %a1,%d4
    rts
");

#define ECHO_PREVENTION_DELAY 150
void WaitForMillis(register unsigned short asm("%d2"));

asm("xdef WaitForMillis\n"
"WaitForMillis:  move.l %d3,-(%sp)\n"
"           moveq  #31,%d1\n"
"           moveq  #31,%d3\n"
"_wl2_:     move.w #132,%d0    /* modify this value for exact timing !!! */\n"
"_wl1_:     rol.l  %d3,%d1\n"
"           dbf    %d0,_wl1_\n"
"           dbf    %d2,_wl2_\n"
"           move.l (%sp)+,%d3\n"
"           rts");


static inline SYM_ENTRY * openBinVAT(const char *symptrName) { // Quicker file reader than default fopen.
   return DerefSym(SymFind(symptrName));
}

volatile unsigned short currentFile = 0;
unsigned char * gdataPtr;
unsigned char * gdataBlockEndPtr;
unsigned char * datas[TOTAL_STR];
unsigned short dataLengths[TOTAL_STR];

DEFINE_INT_HANDLER(BreakDrawInt) {
   SetIntVec(AUTO_INT_5, DUMMY_HANDLER);
   currentFile = TOTAL_STR; // Only needed because of while loop.
}

DEFINE_INT_HANDLER(DrawFrameInt) {
	unsigned char x0 = 0, x1 = 0, lastByte = 0; // Initialize vars for writing
	unsigned short currentColor = 0;
	unsigned char * line = LCD_MEM;
	unsigned char *dataPtr = gdataPtr;
	unsigned char *dataBlockEndPtr = gdataBlockEndPtr;

	while (dataPtr < dataBlockEndPtr) { // Draw a frame (essentially copied from for loop, with breaks instead of wait for frame)
		unsigned char nextByte = *dataPtr;
		if (line >= (unsigned char *)LCD_MEM + 30 * HEIGHT) {
			break;
		}
		dataPtr++;
		unsigned short newColor = ~currentColor; // Defined here so it doesnt have to be recalculated.
		if (nextByte == 255 || nextByte == 250 || (lastByte < WIDTH && nextByte < lastByte)) { // New horizontal line? Then finish the previous row.
			SpecialFastDrawHLine_R(line, x0, WIDTH - 1, newColor);
			x0 = 0;
			x1 = 0;
			line += 30; // The screen buffer is 240 pixels wide.
		}
		if (nextByte < WIDTH) { // This is the normal line draw. Majority
			x1 = nextByte;
			SpecialFastDrawHLine_R(line, x0, x1, newColor);
			currentColor = newColor;
			x0 = x1;
		} else if (nextByte == 254) { // This is if the frame has not changed. Just wait.
			break;
		} else if (nextByte == 250) { // Next byte will be repeats of 255
			unsigned char repeats = (*dataPtr) - 1;
			unsigned long value = newColor ? 0xFFFFFFFF : 0;
			for (unsigned char i = 0; i < repeats; i++) {
				asm volatile("move.l %1,(%0)+; move.l %1,(%0)+; move.l %1,(%0)+; move.l %1,(%0)+; move.l %1,(%0)+; lea 10(%0),%0" : "=a" (line) : "d" (value) : "cc");
			}
			dataPtr++;
		}
		lastByte = nextByte;
	}
	short row = _rowread(0x0000);
	if (dataPtr >= dataBlockEndPtr || row == 8) { // TODO portable row reading.
		if (currentFile < sizeof(datas) / sizeof(datas[0])) {
		 currentFile++;
		}
		dataPtr = datas[currentFile];
		dataBlockEndPtr = dataPtr + dataLengths[currentFile];
	} else if (row == 2) { // TODO portable row reading.
		if (currentFile > 0) {
		 currentFile--;
		}
		dataPtr = datas[currentFile];
		dataBlockEndPtr = dataPtr + dataLengths[currentFile];
	} else if(row == 1) { // pressing enter, pause
		SetIntVec(AUTO_INT_5, DUMMY_HANDLER);
		while(_rowread(0x0000)); // Wait to let go of key.
		WaitForMillis(ECHO_PREVENTION_DELAY);
		while(_rowread(0x0000) != 1); // Wait for second press.
		while(_rowread(0x0000)); // Wait to let go of key.
		WaitForMillis(ECHO_PREVENTION_DELAY);
		SetIntVec(AUTO_INT_5, DrawFrameInt);
	}

	gdataPtr = dataPtr;
	gdataBlockEndPtr = dataBlockEndPtr;
}

void _main(void) {
	static const char VARNAME_STRS[TOTAL_STR][9] = {};
	SYM_ENTRY *symPtrs[TOTAL_STR];
	unsigned short missingfile = 0;

	while(_rowread(0x0000)); // Wait to let go of program run button (enter)
	clrscr(); // Initial setup

	for (unsigned short fileI = 0; fileI < TOTAL_STR; fileI++) { // Set up direct pointers to data while locking memory blocks.
		SYM_ENTRY * symPtr = openBinVAT(VARNAME_STRS[fileI] + sizeof(VARNAME_STRS[0]) - 1); // Define the data using the vat
		if (symPtr == NULL) {
			missingfile = fileI;
			break;
		}
		unsigned char* data = HLock(symPtr->handle);
		data += 2; // Offset from VAT length data

		dataLengths[fileI] = *(unsigned short *)data; // Define the length of the data
		datas[fileI] = data + 2; // Offset from real length data
		symPtrs[fileI] = symPtr;
	}

	if (missingfile) {
		for (unsigned short fileI = 0; fileI < missingfile; fileI++) { // Unlock memory blocks.
			HeapUnlock(symPtrs[fileI]->handle);
		}
		printf("Missing file index: %u\nMissing file name: %s", missingfile, VARNAME_STRS[missingfile]+1); // Get rid of \0
		GKeyIn(NULL, 0);
		return;
	}

	// Reinitialize global variables.
	gdataPtr = datas[0];
	gdataBlockEndPtr = datas[0] + dataLengths[0];
	currentFile = 0;

	INT_HANDLER oldInt5 = GetIntVec(AUTO_INT_5); // Save default stuff
	INT_HANDLER onInt = GetIntVec(INT_VEC_ON_KEY_PRESS);
	unsigned char oldStart = PRG_getStart();

	asm volatile("trap #12; move.w #0x0200,%sr"); // Set defaults to new stuff
	SetIntVec(AUTO_INT_5, DrawFrameInt);
	SetIntVec(INT_VEC_ON_KEY_PRESS, BreakDrawInt);

	{}
	
	SetIntVec(AUTO_INT_5, DUMMY_HANDLER);
	
	WaitForMillis(ECHO_PREVENTION_DELAY);

	asm volatile("trap #12; move.w #0x0000,%sr"); // Restore the program / defaults
	SetIntVec(INT_VEC_ON_KEY_PRESS, onInt);
	SetIntVec(AUTO_INT_5, oldInt5);
	PRG_setStart(oldStart);

	for (unsigned short fileI = 0; fileI < TOTAL_STR; fileI++) { // Unlock memory blocks.
		HeapUnlock(symPtrs[fileI]->handle);
	}
	
	GKeyFlush();
	if(OSCheckBreak()) {
		OSClearBreak();
	}
	
	return;
}
