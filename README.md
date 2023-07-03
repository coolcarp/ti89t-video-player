# Video player for the Ti89 Titanium

These files generate the Ti-89 program files required to run a video on your calculator.

## Requirements

Python 3 is required to run the encoder and handle compiling. 

The OpenCV python library is required. This is to convert the video frames to black and white binary data. The 4th argument can set the threshhold for this color conversion. 
`pip install opencv-python`

TIGCC is required for the programs to be compiled. Download [gcc4ti](https://github.com/debrouxl/gcc4ti) or [TIGCC](http://tigcc.ticalc.org/download.html).
After installing, be sure it is in your path (environment variables) (ENSURE NO SPACES IN FILEPATH FOR PATH VARIABLE). This is for compiling the main C code to a ti executable. 

This program also uses [TICT](http://tict.ticalc.org/)'s [TI-68k Developer Utilities (download)](http://tict.ticalc.org/downloads/tt140.tar.bz2). It is important that after downloading and extracting this, you add the tt\bin to your path variables. This is solely for converting the bin files to TI readable files. 

FFMPEG is also required. Place it in the util folder (You might just be able to put this in your path variables instead, but both should work). This is for the first step of culling most unnecesary data in the video (1st and 2nd arguments are for width and height respectively, and 3rd is for FPS).

## Usage

Run build.py (16fps) or build32fps.bat (32 fps). Arguments are optional, but default to 160, 100, 16, 128, and ba (5th argument is TI folder name, dont change this). This will create folders comp and output. comp will contain binary data split up to 64kb files, and output will contain all programs you need to copy to the calculator. They should all copy easily using [TILP](http://lpg.ticalc.org/prj_tilp/) (TI's program probably works too), but you may have to garbage collect in between occasionally.

You can also use run in CMD with variables:
`build.py WIDTH HEIGHT FPS COLOR_THRESHOLD TIVARNAME`

I would recommend archiving your other programs/files on your calculator before running this, just in case. I have had issues with low battery, where after execution the home screen would be frozen or address error. This is easily resolved though by holding 2nd, < and >, and then pressin ON. 

## Credit

[Lionel Debroux](https://github.com/debrouxl) for helping me get this working and optimizing the C code. I would not have figured this out without his help.
