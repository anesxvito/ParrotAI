from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Zoom credentials (replace with environment variables in production for security)
ZOOM_CLIENT_ID = "0IUAcAT0Gxird17oSv7A"
ZOOM_CLIENT_SECRET = "x2gTXuRS3RQiBNgnP4cJv775YOKb5QVJ"

# Function to get an access token
def get_access_token():
    url = "https://zoom.us/oauth/token"
    data = {"grant_type": "client_credentials"}
    response = requests.post(url, auth=(ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET), data=data)
    return response.json().get("access_token")

# Webhook route
@app.route('/webhook', methods=['POST'])
def zoom_webhook():
    event_data = request.json

    # Handle Zoom URL validation
    if "plainToken" in event_data:
        # Respond with the plainToken for validation
        return jsonify({"plainToken": event_data["plainToken"]})

    # Handle Zoom events
    print("Received Zoom Event:", event_data)
    if event_data.get("event") == "meeting.ended":
        meeting_id = event_data['payload']['object']['id']
        print(f"Meeting {meeting_id} ended!")
        # Add logic to fetch recordings or summaries here

    # Return a success response for other events
    return jsonify({"message": "Event received"}), 200

# Optional: Add a home route for testing
@app.route("/", methods=["GET"])
def home():
    return "Zoom Bot is running!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
