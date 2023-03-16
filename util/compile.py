#This file will compile each frame file, and the main.c
import os
import struct
import subprocess
import sys 
import shutil

WIDTH = int(sys.argv[1])
HEIGHT = int(sys.argv[2])
FPS = float(sys.argv[3])
NAME = sys.argv[5]

def archiveVar(program_path):
    with open(program_path, "r+b") as f:
        f.seek(0x49)
        f.write(struct.pack("B", 0x03)) # archive the file

main_ti_folder = NAME
output = "output"

length_comp = 0
for filename in os.listdir("comp"):
    length_comp += 1
    nam = "px{0:02d}".format(length_comp)
    subprocess.run(["ttbin2oth", "-89", "BIN", os.path.join("comp", nam + ".bin"), nam, main_ti_folder])
    archiveVar(nam + ".89y") # IT is output to main dir.
    os.rename(nam + ".89y", os.path.join(output, nam + ".89y"))

main_file_name = "play"
c_path = "main.c"
os.chdir(output) # Must change directory, so that the VARNAME does not have path :/ ???
with open(os.path.join("..", c_path), "r") as f_main: # Clone main for number of files.
    main_data = f_main.read().replace("{", "{{").replace("}", "}}").replace("{{}}", "{}") # Ew, but it works.
    with open(main_file_name + ".c", "w") as f:
        str2darr = "{" + (("\"\\0" + main_ti_folder + "\\\\px{:02d}\",") * length_comp).format(*[i for i in range(1, length_comp+1)]) +"}"
        f.write(main_data.format(WIDTH, HEIGHT, FPS, length_comp, str2darr))
    #shutil.copy("..\\extgraph.h", "extgraph.h")
    #shutil.copy("..\\extgraph.a", "extgraph.a")
    #subprocess.run(["..\\util\\tigcc.exe", main_file_name + ".c", "extgraph.a", "--varname", main_ti_folder + "\\" + main_file_name, "-Os", "-w", "-ffunction-sections", "-fdata-sections"])
    subprocess.run(["tigcc", main_file_name + ".c", "--varname", main_ti_folder + "\\" + main_file_name, "-std=gnu99", "-Os", "-Wall", "-W", "-Wwrite-strings", "-fomit-frame-pointer", "-mregparm=5", "-ffunction-sections", "-fdata-sections", "-mno-bss", "-Wa,-l", "-mpcrel",])# "--optimize-code", "--cut-ranges", "--remove-sections"])
    archiveVar(main_file_name + ".89z")
    #os.remove("extgraph.a") 
    #os.remove("extgraph.h")
    #os.remove("play.c") # Get rid of this line if you want to see the final source. 