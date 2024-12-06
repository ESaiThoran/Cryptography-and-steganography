import math
import wave
import numpy as np


def hex_to_binary(hex_str):
    binary = bin(int(hex_str, 16))[2:]
    return binary.zfill((len(binary) + 7) // 8 * 8)

def encode_data_aud(audio1, data):
    step= 2
    with wave.open(audio1, 'rb') as audio:
        frames = bytearray(list(audio.readframes(audio.getnframes())))

    max_char = math.floor(len(frames) / step / 8)
    no_of_words = max_char / 5 
    if len(data) * step > len(frames):
        raise ValueError("Need Bigger Audio or Give Less Data !")

    binary_Data = hex_to_binary(data) + '1111111111111110' 

    # Modify the LSB of each audio sample by skipping
    for i, bit in enumerate(binary_Data):
        frame_index = i * step
        frames[frame_index] = (frames[frame_index] & 254) | int(bit)

    newfile = "temp.wav"

    with wave.open(newfile, 'wb') as modified_audio:
        modified_audio.setparams(audio.getparams())
        modified_audio.writeframes(frames)

    return newfile


















import math
import wave
import numpy as np


def binary_to_hex(binary):
    binary = binary.lstrip('0')
    integer = int(binary, 2)
    hex_str = hex(integer)[2:]
    return hex_str


def decode_data_aud(audio2):
    step=2
    with wave.open(audio2, 'rb') as audio:
        frames = bytearray(list(audio.readframes(audio.getnframes())))

    # Extract LSBs
    binary_Data = ''
    for i in range(0, len(frames), step):
        binary_Data += str(frames[i] & 1)

    delimiter = '1111111111111110'
    end_index = binary_Data.find(delimiter)
    if end_index != -1:
        binary_Data = binary_Data[:end_index]

    decoded_data = binary_to_hex(binary_Data)
    return decoded_data 
