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

def assign_codes(vee_frames): 
    for i in range(len(vee_frames)):
        vee_frames[i] = rle_encode(vee_frames[i]) 
    return vee_frames 

# THOUGHTS: maybe assume frame is same as last, then encode with (startX, startY, width, height) + (data), only drawing in this space.
    
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