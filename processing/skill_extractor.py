import spacy
import re
import json

nlp = spacy.load("en_core_web_sm")


def load_skills_from_config():
    with open("telex_config.json", "r") as file:
        config = json.load(file)
    
    return next(
        (setting["default"] for setting in config["data"]["settings"] if setting["label"] == "List of Skills required"),
        []
    )


SKILLS = load_skills_from_config()

def extract_skills(text):
    doc = nlp(text)
    found_skills = [token.text for token in doc if token.text in SKILLS]
    return list(set(found_skills))


def extract_contact_info(text):
    # Regex for extracting email
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    emails = re.findall(email_pattern, text)
    email = emails[0] if emails else "Not Found"

    # Regex for extracting phone number (basic format)
    phone_pattern = r"\+?\d{10,15}"
    phones = re.findall(phone_pattern, text)
    phone = phones[0] if phones else "Not Found"

    # Extracting name (Assuming it's the first two words in the text)
    words = text.split()
    name = " ".join(words[:2]) if len(words) >= 2 else "Unknown Name"

    return name, email, phone