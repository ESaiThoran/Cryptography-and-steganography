# backend/steganography.py
import numpy as np
import random
import cv2
import pandas as pand
import os
from matplotlib import pyplot as plt

import numpy as np
import random
import cv2

# Function to convert a message to binary format
def hex_to_binary(hex_str):
    binary = bin(int(hex_str, 16))[2:]
    return binary.zfill((len(binary) + 7) // 8 * 8)

# Function to generate pseudo-random sequence based on seed
def pseudo_random_sequence(seed, length):
    random.seed(seed)  # Initialize the random generator with the provided seed
    sequence = list(range(length))  # Create a sequence of numbers from 0 to length-1 (pixel indices)
    random.shuffle(sequence)  # Shuffle the sequence randomly based on the seed
    return sequence

# Function to convert pixel to binary
def msgtobinary(pixel):
    return (bin(pixel[0])[2:].zfill(8), bin(pixel[1])[2:].zfill(8), bin(pixel[2])[2:].zfill(8))

# Function to determine the seed based on binary data length
def tp_count(len_data):
    tp = len_data // 3
    if len_data % 3 != 0:
        tp += 1
    return tp

# Main encoding function to hide data in the image
def encode_data_img(image, data, seed):
    if len(data) == 0:
        raise ValueError('Data entered to ENCRYPT is Empty')

    # Convert the encrypted data to binary
    bin_data = hex_to_binary(data)
    binary_data = bin_data + '1111111111111110'  # End-of-data marker
    length_data = len(binary_data)

    # Calculate tnp based on binary data length
    tnp = tp_count(length_data)

    # Generate pseudo-random sequence for encoding
    prng_sequence = pseudo_random_sequence(seed, len(image.flatten()) // 3)
    prng_sequence1 = prng_sequence[:tnp]

    # Embed data in the image
    index_data = 0
    for pix_index in prng_sequence1:
        if index_data >= length_data:
            break

        # Get row and column based on pixel index
        row = pix_index // image.shape[1]
        col = pix_index % image.shape[1]
        pixel = image[row, col]
        
        # Convert pixel RGB values to binary
        r, g, b = msgtobinary(pixel)

        # Modify R, G, and B channels of the pixel
        if index_data < length_data:
            pixel[0] = int(r[:-1] + binary_data[index_data], 2)
            index_data += 1
        if index_data < length_data:
            pixel[1] = int(g[:-1] + binary_data[index_data], 2)
            index_data += 1
        if index_data < length_data:
            pixel[2] = int(b[:-1] + binary_data[index_data], 2)
            index_data += 1
        
        # Update pixel back in the image
        image[row, col] = pixel

    return image, tnp



import random
import cv2

# Function to convert a binary string to hex
def binary_to_hex(binary_str):
    return hex(int(binary_str, 2))[2:]

# Function to generate pseudo-random sequence based on seed
def pseudo_random_sequence(seed, length):
    random.seed(seed)  # Initialize the random generator with the provided seed
    sequence = list(range(length))  # Create a sequence of numbers from 0 to length-1 (pixel indices)
    random.shuffle(sequence)  # Shuffle the sequence randomly based on the seed
    return sequence

# Function to convert pixel to binary
def msgtobinary(pixel):
    return (bin(pixel[0])[2:].zfill(8), bin(pixel[1])[2:].zfill(8), bin(pixel[2])[2:].zfill(8))

# Main function to reveal hidden data in the image
def decode_data_img(image, seed, tnp):
    # Get seed from user for PRNG
    # Generate pseudo-random sequence based on the image size
    prng_sequence = pseudo_random_sequence(seed, len(image.flatten()) // 3)  # PRNG sequence for pixels
    prng_sequence1 = prng_sequence[:tnp]
    # Variables to hold the retrieved binary data
    binary_data = ''
    delimiter = '1111111111111110'  # Define the delimiter

    # Retrieve data from pixels in the image based on PRNG sequence
    for pix_index in prng_sequence1:
        # Get row and column based on pixel index
        row = pix_index // image.shape[1]
        col = pix_index % image.shape[1]

        pixel = image[row, col]
        r, g, b = msgtobinary(pixel)
    
        # Extract the least significant bits (LSB) from R, G, and B channels
        binary_data += r[-1]
        binary_data += g[-1]
        binary_data += b[-1]
    
        # Check for the delimiter
        if delimiter in binary_data:
            binary_data = binary_data.split(delimiter)[0]  # Remove the delimiter and anything after it
            break
    
    # Convert the binary data back to hexadecimal
    hex_data = binary_to_hex(binary_data)

    return hex_data
