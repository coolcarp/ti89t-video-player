#This file will compile each frame file, and the main.c
import os
import struct
import subprocess
import sys 
import shutil

WIDTH = int(sys.argv[1])
HEIGHT = int(sys.argv[2])
FPS = int(sys.argv[3])
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

def toFps(prgStart):
    return 1024 / (257 - prgStart)

def toStart(fps):
    return -(1024/fps - 257)

max_seconds = 60
start_range = 10
err_thresh = 0.03
def calculate_prg_values(target_fps):
    info_dict = [None] * 255
    around = range(-start_range + round(toStart(target_fps)), start_range + round(toStart(target_fps)))
    for i in around:
        current = toFps(i)
        if current == target_fps:
            return ((i, 0), (i, 0))
        info_dict[i] = [None] * max_seconds
        for x in range(1, max_seconds):
            frames = current * x
            if abs(frames - round(frames)) < err_thresh:
                info_dict[i][x] = round(frames)
    pairs = []
    for i in around:
        for x in range(1, max_seconds):
            frames = info_dict[i][x]
            if frames:
                expected_frames = target_fps * x
                diff = frames - expected_frames
                # Try to find -diff
                best_prg = 0
                best_frames = 0
                for i2 in around:
                    if i == i2: continue
                    for x2 in range(1, max_seconds):
                        if x == x2: continue
                        frames_2 = info_dict[i2][x2]
                        if frames_2:
                            expected_frames_2 = target_fps * x2
                            diff_2 = frames_2 - expected_frames_2
                            if abs(i2 - i) < abs(best_prg - i) and diff_2 == -diff: #if abs(frames_2 - frames) < abs(best_frames - frames) and diff_2 == -diff: #
                                best_prg = i2
                                best_frames = frames_2
                if best_prg != 0:
                    pairs.append(((i, frames), (best_prg, best_frames)))
    # Prioritize based on frame length
    best_pair = ()
    greatest_product = 0
    least_diff_start = 1000009
    least_diff_len = 1000009
    for pair in pairs:
        #product = pair[0][1] * pair[1][1]
        diff_start = abs(pair[0][0] - pair[1][0])
        #diff_len = abs(pair[0][1] - pair[1][1])
        if diff_start < least_diff_start:
            #greatest_product = product
            #least_diff_len = diff_len
            least_diff_start = diff_start
            best_pair = pair 
    return best_pair  

main_file_name = "play"
c_path = "main.c"
os.chdir(output) # Must change directory, so that the VARNAME does not have path :/ ???
with open(os.path.join("..", c_path), "r") as f_main: # Clone main for number of files.
    main_data = f_main.read().replace("{", "{{").replace("}", "}}").replace("{{}}", "{}") # Ew, but it works.
    with open(main_file_name + ".c", "w") as f:
        str2darr = "{" + (("\"\\0" + main_ti_folder + "\\\\px{:02d}\",") * length_comp).format(*[i for i in range(1, length_comp+1)]) +"}"
        maincode = ""
        if 1024 % FPS == 0:
            maincode = """PRG_setStart({}); while (currentFile < TOTAL_STR) {{asm volatile("move.b #0b10000,0x600005");}}""".format(round(257 - 1024 / FPS))
        else:
            best_pair = calculate_prg_values(FPS)
            maincode = """unsigned short frameCounter = {};
            PRG_setStart({}); 
            while (currentFile < TOTAL_STR) {{
                if(frameCounter == {}) {{
                PRG_setStart({});
                }} else if(frameCounter == {}) {{
                PRG_setStart({});
                frameCounter = 0;
                }}
                asm volatile("move.b #0b10000,0x600005");
                frameCounter++;
            }}""".format(round(best_pair[0][1] / 2), best_pair[0][0], best_pair[0][1], best_pair[1][0], best_pair[0][1] + best_pair[1][1], best_pair[0][0])
        f.write(main_data.format(WIDTH, HEIGHT, FPS, length_comp, str2darr, maincode))
    subprocess.run(["tigcc", main_file_name + ".c", "--varname", main_ti_folder + "\\" + main_file_name, "-std=gnu99", "-Os", "-Wall", "-W", "-Wwrite-strings", "-fomit-frame-pointer", "-mregparm=5", "-ffunction-sections", "-fdata-sections", "-mno-bss", "-Wa,-l", "-mpcrel", "--optimize-code", "--cut-ranges", "--remove-unused"])
    #subprocess.run(["tigcc", main_file_name + ".c", "--varname", main_ti_folder + "\\" + main_file_name, "-std=gnu99", "-O3", "-Wall", "-W", "-Wwrite-strings", "-fomit-frame-pointer", "-mregparm=5", "-ffunction-sections", "-fdata-sections", "-mno-bss", "-Wa,-l", "-mpcrel", "--optimize-code", "--cut-ranges"])
    archiveVar(main_file_name + ".89z")