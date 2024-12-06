import cv2
import numpy as np
import random

def hex_to_binary(hex_str):
    binary = bin(int(hex_str, 16))[2:]
    return binary.zfill((len(binary) + 7) // 8 * 8)

def lsb(pixel, r, g, b):
    # Ensure pixel values stay within 0-255 range using np.clip
    return (
        np.clip((pixel[0] & 0xFE) | (r & 1), 0, 255),  # Modify red channel
        np.clip((pixel[1] & 0xFE) | (g & 1), 0, 255),  # Modify green channel
        np.clip((pixel[2] & 0xFE) | (b & 1), 0, 255)   # Modify blue channel
    )

def encode_data_vid(input_video, data, seed):
    try:
        cap = cv2.VideoCapture(input_video)
        if not cap.isOpened():
            raise ValueError("Could not open input video")

        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_pixels = frame_width * frame_height

        # Convert hex data to binary
        binary_data = hex_to_binary(data)
        binary_length = len(binary_data)
        
        # Calculate required pixels
        req_pix = (binary_length + 2) // 3  # Round up division
        
        if req_pix > total_pixels:
            raise ValueError("Data too large for video frame")

        # Generate random pixel coordinates
        random.seed(seed)
        pixel_indices = random.sample(range(total_pixels), req_pix)
        pixel_coords = [(index // frame_width, index % frame_width) for index in pixel_indices]

        # Set up video writer
        newfile = "temp.avi"
        fourcc = cv2.VideoWriter_fourcc(*'FFV1')  # Lossless codec
        out = cv2.VideoWriter(newfile, fourcc, fps, (frame_width, frame_height))
        
        if not out.isOpened():
            raise ValueError("Could not create output video")

        index = 0
        modified_frame = False

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if not modified_frame:
                # Convert frame to proper dtype
                frame = frame.astype(np.uint8)
                
                # Modify pixels in first frame
                for coord in pixel_coords:
                    x, y = coord
                    if index >= binary_length:
                        break

                    # Get next three bits from binary data
                    r = int(binary_data[index % binary_length])
                    g = int(binary_data[(index + 1) % binary_length])
                    b = int(binary_data[(index + 2) % binary_length])
                    index += 3

                    # Apply LSB modification
                    frame[x, y] = lsb(frame[x, y], r, g, b)

                modified_frame = True

            out.write(frame)

    except Exception as e:
        raise Exception(f"Error in video encoding: {str(e)}")
    
    finally:
        # Clean up resources
        if cap is not None:
            cap.release()
        if out is not None:
            out.release()

    return newfile, binary_length























import cv2
import numpy as np
import random

# Function to retrieve the LSB from each RGB channel
def retrieve_lsb(pixel):
    return (pixel[0] & 1, pixel[1] & 1, pixel[2] & 1)  # Red, Green, Blue LSB

def binary_to_hex(binary_str):
    hex_str = hex(int(binary_str, 2))[2:]
    return hex_str.zfill((len(hex_str) + 1) // 2 * 2)

def decode_data_vid(video, seed, tnp):
    cap = cv2.VideoCapture(video)

    # Get video properties
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_pixels = frame_width * frame_height

    # Get user inputs

    # Calculate the required number of pixels to retrieve the data
    req_pix = (tnp + 2) // 3  # Each pixel holds 3 bits (one in each RGB channel)

    # Set the random seed and generate the same pixel coordinates used during encryption
    random.seed(seed)
    pixel_indices = random.sample(range(total_pixels), req_pix)
    pixel_coords = [(index // frame_width, index % frame_width) for index in pixel_indices]

    binary_data = ""
    modified_frame = False

    # Process video frame by frame
    while True:
        ret, frame = cap.read()
        if not ret:
            break  # Break when no more frames are available

        if not modified_frame:
            # Retrieve the binary data from the selected pixels in the first frame
            for coord in pixel_coords:
                x, y = coord
                if len(binary_data) >= tnp:
                    break

                # Retrieve LSBs from the pixel at (x, y)
                r, g, b = retrieve_lsb(frame[x, y])

                # Append retrieved bits to binary data
                binary_data += str(r) + str(g) + str(b)

            modified_frame = True  # Ensure we only read data from the first frame

    # Release video capture resources
    cap.release()

    # Truncate binary data to the original data length
    binary_data = binary_data[:tnp]
    decrypted_hex = binary_to_hex(binary_data)

    return decrypted_hex


