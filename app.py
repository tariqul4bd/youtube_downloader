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

    try:
        ydl_opts = {'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            formats = [
                {
                    'format_id': f['format_id'],
                    'resolution': f.get('height', 'Audio') if f.get('height') else 'Audio',
                    'extension': f['ext'],
                    'filesize': f.get('filesize', 'Unknown'),
                }
                for f in info['formats'] if f.get('filesize') is not None
            ]
            return jsonify({'formats': formats, 'video_url': video_url})

    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/download', methods=['POST'])
def download():
    video_url = request.form.get('url')
    format_id = request.form.get('format_id')

    if not video_url or not format_id:
        return jsonify({'error': 'Missing video URL or format ID'})

    # Ensure download folder exists
    download_folder = "downloads"
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    ydl_opts = {
        'format': format_id,
        'outtmpl': f'{download_folder}/%(title)s.%(ext)s',
        'noplaylist': True,
        'quiet': False,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            file_path = ydl.prepare_filename(info)

            # Debugging: Print the file path
            print(f"🚀 File should be at: {file_path}")

            # Ensure the file actually exists
            if os.path.exists(file_path):
                print("✅ File found. Sending to user.")
                return send_file(file_path, as_attachment=True)
            else:
                print("❌ Download failed: File not found!")
                return jsonify({'error': 'Download failed: File not found'})

    except Exception as e:
        print(f"❌ yt-dlp Error: {e}")  # Debugging
        return jsonify({'error': str(e)})


    except Exception as e:
        print(f"❌ yt-dlp Error: {e}")  # Debugging
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    app.run(debug=True)
