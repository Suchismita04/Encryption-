import os
import pyzipper
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Define allowed extensions and maximum file size
ALLOWED_EXTENSIONS = {'zip'}
UPLOAD_FOLDER = 'uploads/'
EXTRACT_FOLDER = 'extracted/'
WORDLIST_PATH = 'rockyou.txt'
WORDLIST_URL = "https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt"

# Configure app
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max file size 16MB

# Ensure the required directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(EXTRACT_FOLDER, exist_ok=True)

# Function to download rockyou.txt if it doesn't exist
def download_wordlist():
    if not os.path.exists(WORDLIST_PATH):
        print("Downloading rockyou.txt...")
        response = requests.get(WORDLIST_URL, stream=True)
        with open(WORDLIST_PATH, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)
        print("rockyou.txt downloaded successfully!")

# Check and download the wordlist if missing
download_wordlist()

# Function to check if file is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to try opening the zip file with a given password
def try_password(zip_path, password):
    try:
        with pyzipper.AESZipFile(zip_path) as zf:
            zf.setpassword(password.encode())
            zf.testzip()  # Test if the password works
            return True
    except RuntimeError:
        return False

# Dictionary attack function
def dictionary_attack(zip_path):
    if not os.path.exists(WORDLIST_PATH):
        return None, "Wordlist not found"

    with open(WORDLIST_PATH, "r", encoding="latin-1") as file:
        for password in file:
            password = password.strip()
            if try_password(zip_path, password):
                return password, None
    return None, "Password not found"

# Upload endpoint to handle file uploads
@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return jsonify({"message": f"File {filename} uploaded successfully", "file_path": filepath}), 200

    return jsonify({"error": "File type not allowed. Only .zip files are allowed."}), 400

# Endpoint to start the dictionary attack
@app.route('/api/start-dictionary-attack', methods=['POST'])
def start_dictionary_attack():
    data = request.get_json()

    # Get file path from request
    zip_path = data.get('file_path')

    if not zip_path:
        return jsonify({"error": "File path is required"}), 400

    # Perform dictionary attack
    password, error = dictionary_attack(zip_path)

    if password:
        return jsonify({"message": "Password found", "password": password}), 200
    else:
        return jsonify({"error": error}), 404

# Endpoint to extract files after finding the password
@app.route('/api/extract', methods=['POST'])
def extract_files():
    data = request.get_json()

    zip_path = data.get('file_path')
    password = data.get('password')

    if not zip_path or not password:
        return jsonify({"error": "File path and password are required"}), 400

    try:
        with pyzipper.AESZipFile(zip_path) as zf:
            zf.setpassword(password.encode())
            # Extract the files
            extracted_files = []
            for file_info in zf.infolist():
                extracted_files.append(file_info.filename)
            zf.extractall(EXTRACT_FOLDER)

        return jsonify({"message": "Files extracted successfully", "extracted_files": extracted_files}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Port for Render Deployment
    app.run(host='0.0.0.0', port=port, debug=True)
