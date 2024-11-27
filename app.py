from flask import Flask, request, jsonify 
import requests

app = Flask(__name__)

ZOOM_CLIENT_ID = "0IUAcAT0Gxird17oSv7A"
ZOOM_CLIENT_SECRET = "x2gTXuRS3RQiBNgnP4cJv775YOKb5QVJ"

def get_access_token():
    url = "https://zoom.us/oauth/token"
    data = {"grant_type": "client_credentials"}
    response = requests.post(url, auth=(ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET), data=data)
    return response.json().get("access_token")

@app.route('/webhook', methods=['POST'])
def zoom_webhook():
    event_data = request.json
    if event_data['event'] == 'meeting.ended':
        print(f"Meeting Ended: {event_data['payload']['object']['id']}")
        # Add logic to fetch recordings or summaries here.
    return jsonify({"message": "Event received"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
