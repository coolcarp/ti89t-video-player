import os
import sys

WIDTH = int(sys.argv[1])
HEIGHT = int(sys.argv[2])

def vee_encode(data): # Vertical edge encoding, only keep track of starting color, then measure x pos where color changes. Store 255 if no change on the row. 
    result = [] # (RLE SUCKS COMPARED TO THIS in terms of file size)
    color = 0 # Assume start of black
    for i in range(len(data)): # 0-15999
        if data[i] != color:
            cur = i % WIDTH
            if len(result) > 2 and result[-1] == 255 and result[-2] > cur and result[-2] != 255: 
                result.pop() # 255 is only necessary when the previous X value is less than the current x value
            result.append(cur)
            color = data[i]
        if (i+1) % WIDTH == 0:
            result.append(255) # 255 indicates new line
    return result
  
def handle_duplicates(vee_frames): # Compares vee encoded frames, if they are the same, 254 will replace the frame. 
    for i in range(len(vee_frames) - 1, 0, -1):
        if len(vee_frames[i-1]) == len(vee_frames[i]):
            equal = True
            for x in range(len(vee_frames[i-1])):
                if vee_frames[i-1][x] != vee_frames[i][x]:
                    equal = False
                    break
            if equal:
                vee_frames[i] = [254]
    return vee_frames

"""
repeatsEncoded = 0
def delta_encdoe(frames): # Go through both at once. Keep track of length of same pixels. When #pixels is 255, or the data is no longer the same, and there is more than 1 similarity, RLE encode it with 180 and #pixels
    result = []
    current = frames[-1] # THIS function IS FUCKED UP
    repeats = 1

    def encode_repeats(repeats):
        global repeatsEncoded
        if repeats > 2:
            repeatsEncoded += 1
            if repeats >= 255:
                result[:0] = [180, 255]
                repeats -= 255
                while repeats >= 255:
                    result[:0] = [180, 255]
                    repeats -= 255
                if repeats > 0:
                    result[:0] = [180, repeats]
            else:
                result[:0] = [180, repeats]
        else:
            for i in range(repeats):
                result[:0] = current

    for prev in reversed(frames[:-1]):
        if prev == current and repeats < 255:
            repeats += 1
        else:
            encode_repeats(repeats)
            result[:0] = current
            current = prev
            repeats = 1

    encode_repeats(repeats)
    result[:0] = current

    return result
"""

def rle_encode(data): # Specialized RLE to only encode 255 repeats with the number 250 and the N repeats. 
    current_value = None
    current_count = 0
    result = []
    for value in data:
        if value != current_value:
            # If the value has changed, add the current run to the result
            if current_value is not None:
                if current_value == 255 and current_count > 1:
                    result.append(250)
                    result.append(current_count)
                else:
                    result.extend([current_value] * current_count)
            # Start a new run
            current_value = value
            current_count = 1
        else:
            # Increment the current run
            current_count += 1
    # Add the final run to the result
    if current_value is not None:
        if current_value == 255 and current_count > 1:
            result.append(250)
            result.append(current_count)
        else:
            result.extend([current_value] * current_count)
    return result

def assign_codes(vee_frames): # If the frame is all black, it will be 253. If the frame is all white, 252. 
    #TODO: If >3 bytes are repeated, rle them, and indicate with code 250 (do this last)
    """for i in range(len(vee_frames)):
        frame_black = False
        frame_white = False
        if len(vee_frames[i]) == 100:
            frame_black = True
            for x in range(len(vee_frames[i])):  # Check if frame is black
                if vee_frames[i][x] != 255: # (all 255s)
                    frame_black = False
                    break
        if not frame_black and vee_frames[i][0] == 1 and len(vee_frames[i]) == 101: # Check if frame is white
            frame_white = True
            for x in range(2, len(vee_frames[i])):
                if vee_frames[i][x] != 255: # (all 255s, except first one)
                    frame_white = False
                    break
        if frame_black:
            vee_frames[i] = [253]
        elif frame_white:
            vee_frames[i] = [252]"""
    for i in range(len(vee_frames)):
        vee_frames[i] = rle_encode(vee_frames[i])
    #delta_encdoe(vee_frames)   
    return vee_frames 

def areEqual(arr1, arr2):
    for i in range(0, len(arr1)):
        if (arr1[i] != arr2[i]):
            return False
    return True

# THOUGHTS: maybe assume frame is same as last, then encode with (startX, startY, width, height) + (data), only drawing in this space.

def deltaEncode(frames): #TODO:implement this encoding, even if it takes more space. (save line drawing = faster) 
    print("NOT DONE") #if taking VEE frames, then add each value-last to count. otherwise, just += 1.
    
def checkDelta(frames): # savings: ~25% for 15fps, ~23% for 10fps 
    rowsSaved = 0
    rows = 0
    for i in range(len(frames) - 1, 0, -1):
        prev = frames[i-1]
        cur = frames[i]
        for x in range(160, len(cur), 160):
            rows += 1
            if areEqual(prev[x-160:x], cur[x-160:x]):
                rowsSaved += 1
    print("Rows saved: " + str(rowsSaved) + "/" + str(rows) + " (" + str(rowsSaved/rows) + ")")
    
    
def write_binary(file_path, data, length):
    with open(file_path + ".bin", "wb") as f:
        f.write(length.to_bytes(2, byteorder="big"))
        f.write(bytes(data))

binary_file_path = "./video/binary_video.bin"
with open(binary_file_path, "rb") as f:
    data = f.read()
    NUM_PIX = WIDTH * HEIGHT
    frames = [data[i:i+NUM_PIX] for i in range(0, len(data), NUM_PIX)] # [data[0:16000]] #
    vee_frames = assign_codes(handle_duplicates([vee_encode(frame) for frame in frames]))
    #delta_encdoe(frames)
    #checkDelta(frames)
    #print("Repeats encoded:" + str(repeatsEncoded))
    chunk_size = 65500 #os.path.getsize("./main.c") # 64 KB limit for programs
    chunk_num = 0
    chunk_data = []
    for vee_frame in vee_frames:
        if len(chunk_data) + len(vee_frame) > chunk_size:
            chunk_num += 1
            chunk_filename = "px{0:02d}".format(chunk_num)
            chunk_file_path = os.path.join("./comp/", chunk_filename)
            write_binary(chunk_file_path, chunk_data, len(chunk_data))
            chunk_data = vee_frame
        else:
            chunk_data += vee_frame
    if len(chunk_data) > 0:
        chunk_num += 1
        chunk_filename = "px{0:02d}".format(chunk_num)
        chunk_file_path = os.path.join("./comp/", chunk_filename)
        write_binary(chunk_file_path, chunk_data, len(chunk_data))