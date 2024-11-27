from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Zoom credentials (replace with environment variables in production)
ZOOM_CLIENT_ID = "0IUAcAT0Gxird17oSv7A"
ZOOM_CLIENT_SECRET = "x2gTXuRS3RQiBNgnP4cJv775YOKb5QVJ"

# Function to get an access token from Zoom
def get_access_token():
    url = "https://zoom.us/oauth/token"
    data = {"grant_type": "client_credentials"}
    response = requests.post(url, auth=(ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET), data=data)
    return response.json().get("access_token")

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
            # Add logic to fetch recordings or summaries here
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
