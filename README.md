# Video player for the Ti89 Titanium

These files generate the Ti-89 program files required to run a video on your calculator.

## Requirements

Python 3 is required to run the encoder and handle compiling. 

The OpenCV python library is required.
`pip install opencv-python`

TIGCC is required for the programs to be compiled. Download [gcc4ti](https://github.com/debrouxl/gcc4ti) or [TIGCC](http://tigcc.ticalc.org/download.html).
After installing, be sure it is in your path (environment variables). (ENSURE NO SPACES IN FILEPATH FOR PATH VARIABLE)

FFMPEG is also required. Place it in the util folder. 

## Usage

Run build.py. This will create folders comp, mains, and output. output will contain all programs.

You can also use run in CMD with variables:
`build.py WIDTH HEIGHT FPS COLOR_THRESHOLD TIVARNAME`

## Credit

[Lionel Debroux](https://github.com/debrouxl) for helping me get this working and optimizing the C code. I would not have figured this out without his help.