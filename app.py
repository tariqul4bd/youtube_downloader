from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fetch-formats', methods=['POST'])
def fetch_formats():
    video_url = request.form.get('url')

    if not video_url:
        return jsonify({'error': 'No URL provided!'})

    # yt-dlp options to focus on publicly accessible formats
    ydl_opts = {
        'quiet': True,
        'noplaylist': True,  # Avoid fetching entire playlists
        'extract_flat': False,  # Avoid metadata-only extraction
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            formats = [
                {
                    'format_id': f['format_id'],
                    'resolution': f.get('height', 'Audio') if f.get('height') else 'Audio',
                    'extension': f['ext'],
                    'filesize': f.get('filesize', 'Unknown'),
                }
                for f in info['formats']
                if f.get('acodec') != 'none' and f.get('vcodec') != 'none'  # Ensure both audio and video are included
            ]
            return jsonify({'formats': formats})
    except Exception as e:
        return jsonify({'error': f"Failed to fetch formats: {str(e)}"})

@app.route('/download', methods=['POST'])
def download():
    video_url = request.form.get('url')
    format_id = request.form.get('format_id')

    if not video_url or not format_id:
        return "Error: URL or Format ID missing!"

    ydl_opts = {
        'format': format_id,
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'merge_output_format': 'mp4',  # Ensure final file is MP4
        'noplaylist': True,  # Avoid downloading playlists
        'no_warnings': True,  # Suppress warnings for cleaner logs
        'ignoreerrors': True,  # Ignore minor errors and continue
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            file_path = ydl.prepare_filename(info)

            return send_file(file_path, as_attachment=True)

    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
