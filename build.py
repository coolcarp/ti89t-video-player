#!/usr/bin/env python3
import os
import sys

arg_len = len(sys.argv)
args = [0, 0, 0, 0, ""]
args[0] = arg_len < 2 and 160 or sys.argv[1]    # WIDTH
args[1] = arg_len < 3 and 100 or sys.argv[2]    # HEIGHT
args[2] = arg_len < 4 and 16 or sys.argv[3]     # FPS 
args[3] = arg_len < 5 and 128 or sys.argv[4]    # Threshold for black/white
args[4] = arg_len < 6 and "ba" or sys.argv[5]   # TI Folder name

os.environ["PATH"] += os.pathsep + "./util"

arg_string = " " + str(args[0]) + " " + str(args[1]) + " " + str(args[2]) + " " + str(args[3]) + " " + args[4] # Disregard this mess

# Bin creation
if not os.path.exists("./video/binary_video.bin"):
    print("Creating binary video...")
    os.system("binify.py" + arg_string)
    
# Video compression
if not os.path.exists("./comp"):
    os.makedirs("./comp", exist_ok=True)
    print("Encoding video...")
    os.system("encode.py" + arg_string)

# Compile project with main function
os.makedirs("./output", exist_ok=True)
print("Compiling programs...")
os.system("compile.py" + arg_string)


# Complete
print("Complete!")
