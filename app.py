from flask import Flask, render_template, request, jsonify
import http.client
import os
import json

app = Flask(__name__)

# Load API Key from Render Environment Variable
API_KEY = os.getenv("RAPIDAPI_KEY")  # Securely fetch API Key
API_HOST = "youtube-media-downloader.p.rapidapi.com"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fetch-formats', methods=['POST'])
def fetch_formats():
    video_url = request.form.get('url')

    if not video_url:
        return jsonify({'error': 'No URL provided!'})

    try:
        # Establish API connection
        conn = http.client.HTTPSConnection(API_HOST)
        payload = f"url={video_url}"

        headers = {
            "x-rapidapi-key": API_KEY,  # Using the secure API Key from Render
            "x-rapidapi-host": API_HOST,
            "Content-Type": "application/x-www-form-urlencoded"
        }

        # Send API request
        conn.request("POST", "/v2/misc/list-items", payload, headers)
        res = conn.getresponse()
        data = res.read().decode("utf-8")

        # Parse JSON response
        video_data = json.loads(data)

        # Debugging output (Remove this in production)
        print("API Response:", video_data)

        # Check if response contains an error
        if "error" in video_data:
            return jsonify({'error': video_data['error']})

        return jsonify({'formats': video_data})  # Return formats to frontend

    except Exception as e:
        print(f"API Error: {e}")  # Debugging
        return jsonify({'error': 'Failed to fetch video formats. Please try again later.'})

if __name__ == '__main__':
    app.run(debug=True)
