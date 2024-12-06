from flask import Flask, render_template, request, jsonify, send_file
import os
from werkzeug.utils import secure_filename
import cv2
import numpy as np
from encryption import encryptor
from decryption import decryptor
from image_steganography import encode_data_img, decode_data_img
from video_steganography import encode_data_vid, decode_data_vid
from audio_steganography import encode_data_aud, decode_data_aud
from text_steganography import encode_data_txt, decode_data_txt
import shutil

app = Flask(__name__)

# Get the absolute path of the current directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Create 'uploads' directory in the same folder as app.py
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')

# Configure Flask app
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 300 * 1024 * 1024  # 16MB max file size

# Create necessary directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'templates'), exist_ok=True)

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi'}
ALLOWED_AUDIO_EXTENSIONS = {'wav', 'mp3'}
ALLOWED_TEXT_EXTENSIONS = {'txt', 'doc', 'docx'}

def allowed_image_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

def allowed_video_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_VIDEO_EXTENSIONS

def allowed_audio_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_AUDIO_EXTENSIONS

def allowed_text_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_TEXT_EXTENSIONS

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/hide/image', methods=['POST'])
def hide_in_image():
    try:
        if 'coverImage' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
            
        cover_image = request.files['coverImage']
        if cover_image.filename == '':
            return jsonify({'error': 'No file selected'}), 400
            
        text_data = request.form.get('textData')
        seed = request.form.get('seed')

        if not all([cover_image, text_data, seed]):
            return jsonify({'error': 'Missing required data'}), 400

        if not allowed_image_file(cover_image.filename):
            return jsonify({'error': 'Invalid file format. Please use PNG, JPG, or JPEG'}), 400

        filename = secure_filename(cover_image.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        cover_image.save(file_path)

        image = cv2.imread(file_path)
        encrypted_data, key = encryptor(text_data)
        encoded_image, tnp = encode_data_img(image, encrypted_data, seed)
        
        encoded_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'encoded_image.png')
        cv2.imwrite(encoded_image_path, encoded_image)

        return jsonify({
            'success': True,
            'message': 'Data hidden successfully',
            'key': key,
            'tnp': tnp,
            'encoded_image_path': '/download/encoded/image'
        })

    except Exception as e:
        print(f"Error in hide_in_image: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/hide/video', methods=['POST'])
def hide_in_video():
    try:
        if 'coverVideo' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
            
        cover_video = request.files['coverVideo']
        if cover_video.filename == '':
            return jsonify({'error': 'No file selected'}), 400
            
        text_data = request.form.get('textData')
        seed = request.form.get('seed')

        if not all([cover_video, text_data, seed]):
            return jsonify({'error': 'Missing required data'}), 400

        if not allowed_video_file(cover_video.filename):
            return jsonify({'error': 'Invalid file format. Please use MP4 or AVI'}), 400

        filename = secure_filename(cover_video.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        cover_video.save(file_path)

        print(f"Cover video saved at: {file_path}")  # Debugging line

        encrypted_data, key = encryptor(text_data)
        encoded_video, tnp = encode_data_vid(file_path, encrypted_data, seed)
        
        encoded_video_path = os.path.join(app.config['UPLOAD_FOLDER'], "encoded_video.avi")
        shutil.move(encoded_video, encoded_video_path)

        return jsonify({
            'success': True,
            'message': 'Data hidden successfully',
            'key': key,
            'tnp': tnp,
            'encoded_video_path': '/download/encoded/video'
        })

    except Exception as e:
        print(f"Error in hide_in_video: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/reveal/image', methods=['POST'])
def reveal_from_image():
    try:
        if 'encodedImage' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
            
        encoded_image = request.files['encodedImage']
        if encoded_image.filename == '':
            return jsonify({'error': 'No file selected'}), 400
            
        key = request.form.get('key')
        seed = request.form.get('seed')
        tnp = request.form.get('tnp')

        if not all([encoded_image, key, seed, tnp]):
            return jsonify({'error': 'Missing required data'}), 400

        filename = secure_filename(encoded_image.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        encoded_image.save(file_path)
        image = cv2.imread(file_path)

        extracted_data = decode_data_img(image, seed, int(tnp))
        decrypted_text = decryptor(extracted_data, key)

        return jsonify({
            'success': True,
            'message': 'Data revealed successfully',
            'text': decrypted_text
        })

    except Exception as e:
        print(f"Error in reveal_from_image: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/reveal/video', methods=['POST'])
def reveal_from_video():
    try:
        if 'encodedVideo' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
            
        encoded_video = request.files['encodedVideo']
        if encoded_video.filename == '':
            return jsonify({'error': 'No file selected'}), 400
            
        key = request.form.get('key')
        seed = request.form.get('seed')
        tnp = request.form.get('tnp')

        if not all([encoded_video, key, seed, tnp]):
            return jsonify({'error': 'Missing required data'}), 400

        filename = secure_filename(encoded_video.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        encoded_video.save(file_path)

        extracted_data = decode_data_vid(file_path, seed, int(tnp))
        decrypted_text = decryptor(extracted_data, key)

        return jsonify({
            'success': True,
            'message': 'Data revealed successfully',
            'text': decrypted_text
        })

    except Exception as e:
        print(f"Error in reveal_from_video: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
    ###################################################################################
    

@app.route('/hide/audio', methods=['POST'])
def hide_in_audio():
    try:
        if 'coverAudio' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
            
        cover_audio = request.files['coverAudio']
        if cover_audio.filename == '':
            return jsonify({'error': 'No file selected'}), 400
            
        text_data = request.form.get('textData')
        if not all([cover_audio, text_data]):
            return jsonify({'error': 'Missing required data'}), 400

        if not allowed_audio_file(cover_audio.filename):
            return jsonify({'error': 'Invalid file format. Please use WAV or MP3'}), 400

        filename = secure_filename(cover_audio.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        cover_audio.save(file_path)

        encrypted_data, key = encryptor(text_data)
        encoded_audio = encode_data_aud(file_path, encrypted_data)
        encoded_audio_path = os.path.join(app.config['UPLOAD_FOLDER'], "encoded_audio.wav")
        shutil.move(encoded_audio, encoded_audio_path)

        return jsonify({
            'success': True,
            'message': 'Data hidden successfully',
            'key': key,
            'encoded_audio_path': '/download/encoded/audio'
        })

    except Exception as e:
        print(f"Error in hide_in_audio: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/reveal/audio', methods=['POST'])
def reveal_from_audio():
    try:
        if 'encodedAudio' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
            
        encoded_audio = request.files['encodedAudio']
        if encoded_audio.filename == '':
            return jsonify({'error': 'No file selected'}), 400
            
        key = request.form.get('key')
        if not all([encoded_audio, key]):
            return jsonify({'error': 'Missing required data'}), 400

        filename = secure_filename(encoded_audio.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        encoded_audio.save(file_path)

        decoded_text = decode_data_aud(file_path)
        revealed_text = decryptor(decoded_text, key)

        return jsonify({
            'success': True,
            'message': 'Data revealed successfully',
            'text': revealed_text
        })

    except Exception as e:
        print(f"Error in reveal_from_audio: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/hide/text', methods=['POST'])
def hide_in_text():
    try:
        if 'coverText' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
            
        cover_text = request.files['coverText']
        if cover_text.filename == '':
            return jsonify({'error': 'No file selected'}), 400
            
        text_data = request.form.get('textData')
        if not all([cover_text, text_data]):
            return jsonify({'error': 'Missing required data'}), 400

        if not allowed_text_file(cover_text.filename):
            return jsonify({'error': 'Invalid file format. Please use TXT, DOC, or DOCX'}), 400

        filename = secure_filename(cover_text.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        cover_text.save(file_path)

        encrypted_data, key = encryptor(text_data)
        encoded_text = encode_data_txt(file_path, encrypted_data)
        encoded_text_path = os.path.join(app.config['UPLOAD_FOLDER'], 'encoded_text.txt')
        shutil.move(encoded_text, encoded_text_path)

        return jsonify({
            'success': True,
            'message': 'Data hidden successfully',
            'key': key,
            'encoded_text_path': '/download/encoded/text'
        })

    except Exception as e:
        print(f"Error in hide_in_text: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/reveal/text', methods=['POST'])
def reveal_from_text():
    try:
        if 'encodedText' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
            
        encoded_text = request.files['encodedText']
        if encoded_text.filename == '':
            return jsonify({'error': 'No file selected'}), 400
            
        key = request.form.get('key')
        if not all([encoded_text, key]):
            return jsonify({'error': 'Missing required data'}), 400

        filename = secure_filename(encoded_text.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        encoded_text.save(file_path)

        decoded_text = decode_data_txt(file_path)
        revealed_text = decryptor(decoded_text, key)

        return jsonify({
            'success': True,
            'message': 'Data revealed successfully',
            'text': revealed_text
        })

    except Exception as e:
        print(f"Error in reveal_from_text: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/download/encoded/audio')
def download_encoded_audio():
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'encoded_audio.wav')
        if not os.path.exists(file_path):
            return jsonify({'error': 'Encoded audio not found'}), 404
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        print(f"Error in download_encoded_audio: {str(e)}")
        return jsonify({'error': 'Failed to download file'}), 500

@app.route('/download/encoded/text')
def download_encoded_text():
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'encoded_text.txt')
        if not os.path.exists(file_path):
            return jsonify({'error': 'Encoded text file not found'}), 404
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        print(f"Error in download_encoded_text: {str(e)}")
        return jsonify({'error': 'Failed to download file'}), 500
    
    ###################################################################################


@app.route('/download/encoded/image')
def download_encoded_image():
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'encoded_image.png')
        if not os.path.exists(file_path):
            return jsonify({'error': 'Encoded image not found'}), 404
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        print(f"Error in download_encoded_image: {str(e)}")
        return jsonify({'error': 'Failed to download file'}), 500

@app.route('/download/encoded/video')
def download_encoded_video():
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'encoded_video.avi')
        if not os.path.exists(file_path):
            return jsonify({'error': 'Encoded video not found'}), 404
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        print(f"Error in download_encoded_video: {str(e)}")
        return jsonify({'error': 'Failed to download file'}), 500

if __name__ == '__main__':
    app.run(debug=True)