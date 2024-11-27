from flask import Flask, request, jsonify
import requests
import openai
import smtplib
from email.mime.text import MIMEText
import os

app = Flask(__name__)

# Zoom credentials (read from environment variables)
ZOOM_CLIENT_ID = os.getenv("ZOOM_CLIENT_ID")
ZOOM_CLIENT_SECRET = os.getenv("ZOOM_CLIENT_SECRET")

# OpenAI API Key (read from environment variables)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Email credentials (read from environment variables)
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

# Function to get an access token from Zoom
def get_access_token():
    url = "https://zoom.us/oauth/token"
    data = {"grant_type": "client_credentials"}
    response = requests.post(url, auth=(ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET), data=data)
    return response.json().get("access_token")

# Function to fetch meeting recordings
def get_meeting_recordings(meeting_id, access_token):
    url = f"https://api.zoom.us/v2/meetings/{meeting_id}/recordings"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch recordings: {response.status_code}, {response.text}")
        return None

# Function to generate a summary using OpenAI
def generate_summary(transcript):
    prompt = f"Summarize the following meeting transcript:\n{transcript}"
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=300
    )
    return response["choices"][0]["text"].strip()

# Function to send the summary via email
def send_email_summary(summary, recipient_email):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    msg = MIMEText(summary)
    msg['Subject'] = "Meeting Summary"
    msg['From'] = SENDER_EMAIL
    msg['To'] = recipient_email

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, recipient_email, msg.as_string())

    print(f"Summary sent to {recipient_email}")

# Webhook route to handle validation and events
@app.route('/webhook', methods=['POST'])
def zoom_webhook():
    event_data = request.json  # Get the JSON payload sent by Zoom

    # Handle Zoom URL validation
    if "plainToken" in event_data:
        return jsonify({"plainToken": event_data["plainToken"]})

    # Log the entire event data for debugging purposes
    print("Received Zoom Event:", event_data)

    # Safely handle Zoom events
    event_type = event_data.get("event")  # Get the event type (e.g., meeting.ended)
    if event_type == "meeting.ended":
        # Safely access nested fields
        meeting_id = event_data.get("payload", {}).get("object", {}).get("id")
        if meeting_id:
            print(f"Meeting {meeting_id} ended!")
            # Fetch recordings for the meeting
            access_token = get_access_token()
            recordings = get_meeting_recordings(meeting_id, access_token)

            # Generate a summary (mock transcript for now)
            transcript = "This is a placeholder for the meeting transcript."
            if transcript:
                summary = generate_summary(transcript)
                print(f"Meeting Summary:\n{summary}")
                
                # Send summary via email
                recipient_email = "recipient@example.com"
                send_email_summary(summary, recipient_email)
            else:
                print("No transcript available for this meeting.")
        else:
            print("Meeting ID not found in payload")

    # Respond with success to acknowledge receipt of the event
    return jsonify({"message": "Event received"}), 200

# Optional: Add a simple home route to verify the app is running
@app.route("/", methods=["GET"])
def home():
    return "Zoom Bot is running!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
