from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
from dotenv import load_dotenv
import json
import requests

# Load environment variables from .env file
load_dotenv()

TELEX_WEBHOOK_URL = os.getenv("TELEX_WEBHOOK_URL")

# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from parsers.pdf_parser import extract_text_from_pdf
from processing.skill_extractor import extract_skills, extract_contact_info
from database.db import save_to_db


app = Flask(__name__)
CORS(app)


UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"pdf"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/upload", methods=["POST"])
def upload_resume():
    print("Request Headers:", request.headers)
    print("Request Form Data:", request.form)
    print("Request Files:", request.files)

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Only PDFs are allowed."}), 400

    print(f"Received file: {file.filename}, Content-Type: {file.content_type}")

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)


    text = extract_text_from_pdf(file_path)
    skills = extract_skills(text)

    name, email, phone = extract_contact_info(text) or ("", "", "")

    save_to_db(name, email, phone, skills)

    response_data = {"name": name, "email": email, "phone": phone, "skills": skills}

    if TELEX_WEBHOOK_URL and skills:
        headers = {"Content-Type": "application/json"}

        skills_text = "\n".join(skills)

        telex_payload = {
            "event_name": "Resume Processed",
            "username": name or "Unknown",
            "status": "success",
            "message": f"New resume processed for {name}\n\nMATCHING SKILLS:\n{skills_text}",
        }

        print("Sending payload to Telex:", json.dumps(telex_payload, indent=2))

        try:
            telex_response = requests.post(TELEX_WEBHOOK_URL, json=telex_payload, headers=headers)
            print(f"Telex Response: {telex_response.status_code}, {telex_response.text}")

            return jsonify({
                "status": "success",
                "message": "Resume processed and data sent to Telex",
                "received_data": response_data,
            }), 200

        except requests.RequestException as e:
            print(f"Error sending data to Telex: {e}")
            return jsonify({
                "status": "success",
                "message": "Resume processed but failed to send data to Telex",
                "received_data": response_data,
            }), 500

    return jsonify(response_data), 200



try:
    with open("telex_config.json", "r") as config_file:
        telex_config = json.load(config_file)
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"Error loading Telex config: {e}")
    telex_config = {}


@app.route("/integration-config", methods=["GET", "POST"])
def get_integration_config():
    return jsonify(telex_config), 200


if __name__ == "__main__":
    host = os.getenv("FLASK_RUN_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_RUN_PORT", "5000"))
    app.run(debug=True, host=host, port=port)
