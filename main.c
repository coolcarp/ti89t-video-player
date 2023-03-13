#define USE_TI89
#define SAVE_SCREEN

#include <tigcclib.h>
#include "extgraph.h" // Made by TICT. Thank you TICT HQ and Lionel Debroux :)

#define WIDTH 160
#define HEIGHT 100
#define FPS 16 
#define TOTAL_STR 15

SYM_ENTRY* openBinVAT(char *varName) { // Quicker file reader than default fopen. Thanks Lionel 
	SYM_ENTRY *symptr = DerefSym(SymFind(SYMSTR(varName)));
	if (!symptr) {
		printf("%s not found\n", varName);
		ngetchx();
	}
  return symptr;
}

volatile unsigned int i = 0, currentFile = 0;
unsigned char* datas[TOTAL_STR];
unsigned int dataLengths[TOTAL_STR];

DEFINE_INT_HANDLER(BreakDrawInt) {
	SetIntVec(AUTO_INT_5, DUMMY_HANDLER);
	currentFile = -1; // Only needed because of while loop.
}

DEFINE_INT_HANDLER(DrawFrameInt) {
	unsigned char x0 = 0, x1 = 0, y0 = 0, currentColor = 0, lastByte = 0; // Initialize vars for writing
	unsigned char *data = datas[currentFile];
	unsigned int dataLength = dataLengths[currentFile];
	while(i < dataLength) { // Draw a frame (essentially copied from for loop, with breaks instead of wait for frame)
		unsigned char nextByte = data[i];
		if (y0 == HEIGHT) {
			break;
		}
		unsigned char newColor = !currentColor; // Defined here so it doesnt have to be recalculated.
		if (nextByte == 255 || nextByte == 250 || (lastByte < WIDTH && nextByte < lastByte)) { // New horizontal line? Then finish the previous row.
			FastDrawHLine_R(LCD_MEM, x0, WIDTH - 1, y0, newColor);
			x0 = 0;
			y0++;
			x1 = 0;
		}
		if (nextByte < WIDTH) { // This is the normal line draw. Majority
			x1 = nextByte;
			FastDrawHLine_R(LCD_MEM, x0, x1, y0, newColor);
			currentColor = newColor;
			x0 = x1;
		} else if (nextByte == 254) { // This is if the frame has not changed. Just wait.
			i++;
			break;
		} else if (nextByte == 250) { // Next byte will be repeats of 255
			// minus 1 since the unfinished line is finished above.
			unsigned char repeats = y0 + data[++i] - 1; // Relative to y0
			for (; y0 < repeats; y0++) {
				FastDrawHLine_R(LCD_MEM, 0, WIDTH - 1, y0, newColor);
			}
			//break;
		}
		lastByte = nextByte;
		i++;
	}
	short row = _rowread(0x0000); // Read input row
	if(i >= dataLength || row == 8) { // Is the file done OR right arrow key, skipping ahead
		currentFile++;
		i = 0;
	} else if(row == 2) { // Left arrow key, going backwords
		currentFile--;
		i = 0;
	} else if(row == 1) { // pressing enter, pause
		SetIntVec(AUTO_INT_5, DUMMY_HANDLER);
		while(_rowread(0x0000)); // Wait to let go of key.
		while(_rowread(0x0000) != 1); // Wait for second press.
		while(_rowread(0x0000)); // Wait to let go of key.
		SetIntVec(AUTO_INT_5, DrawFrameInt);
	}
}

void _main(void) {
	const char *VARNAME_STRS[] = {"ba\\px1","ba\\px2","ba\\px3","ba\\px4","ba\\px5","ba\\px6","ba\\px7","ba\\px8","ba\\px9","ba\\px10","ba\\px11","ba\\px12","ba\\px13","ba\\px14","ba\\px15"}; 
	SYM_ENTRY *symPtrs[TOTAL_STR];

	int fileI;
	for(fileI = 0; fileI < TOTAL_STR; fileI++) { // alloc
		symPtrs[fileI] = openBinVAT(VARNAME_STRS[fileI]); // Define the data using the vat
		unsigned char* data = HLock(symPtrs[fileI]->handle); 
		data+=2; // Offset from VAT length data
		
		unsigned int dataLength = 0; // Define the length of the data
		memcpy(&dataLength, data, sizeof(unsigned int));
		
		data+=2; // Offset from real length data
		datas[fileI] = data;
		dataLengths[fileI] = dataLength;
	}
  
	ClrScr(); // Initial setup
	
	i = 0; // It seems volatile is persistent between program runs (or maybe only on tiemu?)
	currentFile = 0; // ^
	
	INT_HANDLER oldInt5 = GetIntVec(AUTO_INT_5); // Save default stuff
	INT_HANDLER onInt = GetIntVec(INT_VEC_ON_KEY_PRESS);
	unsigned char oldStart = PRG_getStart();
	unsigned char oldRate = PRG_getRate();
	unsigned char oldFont = FontSetSys(F_4x6);
	
	while(_rowread(0x0000)); // Wait to let go of program run button (enter)
	
	asm volatile("move.w #0x0200,%d0; trap #1"); // Set defaults to new stuff
	SetIntVec(AUTO_INT_5, DrawFrameInt);//SetIntVec(AUTO_INT_5, DrawFrameInt);
	SetIntVec(INT_VEC_ON_KEY_PRESS, BreakDrawInt);
	PRG_setStart(196); // If start was 196 for all frames, actual playback speed: 16hz * 1.0069 (found by experiment)
	PRG_setRate(1);
	
	unsigned char frameCounter = 0;
	while (currentFile < TOTAL_STR) {
		asm volatile("move.b #0b10000,0x600005;");
		frameCounter++;
		if(frameCounter == 73) { // Calculated by: (1/(1.0068 - 1)) / 2 = ~73.5 (note: i dont know why divide by 2 shows up)
			PRG_setStart(195);
		} else if(frameCounter == 74) {
			frameCounter = 0;
			PRG_setStart(196);
		}
	}
	GKeyFlush();
  
	asm volatile("move.w #0x0000,%d0; trap #1"); // Restore the program / defaults
	SetIntVec(AUTO_INT_5, oldInt5); 
	SetIntVec(INT_VEC_ON_KEY_PRESS, onInt);
	PRG_setStart(oldStart);
	PRG_setRate(oldRate);
	FontSetSys(oldFont);
	
	for(fileI = 0; fileI < TOTAL_STR; fileI++) { // dealoc 
		HeapUnlock(symPtrs[fileI]->handle);
	}
	
	return;
}
