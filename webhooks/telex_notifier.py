import requests

TELEX_WEBHOOK_URL = "https://telex-api.com/notify"

def send_telex_notification(candidate_name, skills):
    payload = {
        "title": "New Resume Match",
        "message": f"Candidate {candidate_name} has skills: {', '.join(skills)}",
        "priority": "high"
    }
    response = requests.post(TELEX_WEBHOOK_URL, json=payload)
    return response.status_code
