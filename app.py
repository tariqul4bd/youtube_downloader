from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# RapidAPI configuration
API_URL = "https://youtube-media-downloader.p.rapidapi.com/v2/misc/list-items"
HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded",
    "x-rapidapi-host": "youtube-media-downloader.p.rapidapi.com",
    "x-rapidapi-key": "db929b91c2msha86c7dcd3aca467p1f7132jsneb2a58ec28fa"  # Replace with your API key
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fetch-formats', methods=['POST'])
def fetch_formats():
    video_url = request.form.get('url')

    if not video_url:
        return jsonify({'error': 'No URL provided!'})

    # POST data
    data = {"url": video_url}

    try:
        # Send POST request to RapidAPI
        response = requests.post(API_URL, headers=HEADERS, data=data)
        response.raise_for_status()  # Raise exception for HTTP errors
        video_data = response.json()

        # Handle API response
        if "error" in video_data:
            return jsonify({'error': video_data['error']})
        
        return jsonify({'formats': video_data})  # Return formats to the frontend
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
