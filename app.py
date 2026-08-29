import os
import sqlite3
from flask import Flask, render_template, request, jsonify
import yt_dlp
from pathlib import Path

# Flask ko explicitly bata diya hai taake template folder ka koi error na aaye
app = Flask(__name__, template_folder='templates')

DOWNLOAD_DIR = os.path.join(str(Path.home()), "Downloads", "SocialDown_Pro")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

DB_PATH = "history.db"
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS downloads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            platform TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_media():
    data = request.get_json()
    url = data.get('url', '').strip()
    quality = data.get('quality', '1080')
    platform_type = data.get('type', 'youtube')

    if not url:
        return jsonify({"status": "error", "message": "Please provide a valid URL!"})

    try:
        if quality == 'audio':
            save_path = os.path.join(DOWNLOAD_DIR, 'Audio')
            os.makedirs(save_path, exist_ok=True)
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
                'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}],
                'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
            }
        elif platform_type == 'youtube':
            save_path = os.path.join(DOWNLOAD_DIR, 'YouTube')
            heights = {'4k': '2160', '1080': '1080', '720': '720', '480': '480'}
            h = heights.get(quality, '1080')
            ydl_opts = {
                'format': f'bestvideo[height<={h}]+bestaudio/best[height<={h}]/best',
                'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
                'merge_output_format': 'mp4',
                'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
            }
        else:
            save_path = os.path.join(DOWNLOAD_DIR, 'SocialMedia')
            ydl_opts = {
                'outtmpl': os.path.join(save_path, '%(title).50s.%(ext)s'),
            }

        os.makedirs(save_path, exist_ok=True)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'Media File')

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO downloads (title, platform) VALUES (?, ?)", (title, platform_type))
        conn.commit()
        conn.close()

        return jsonify({"status": "success", "message": f"Successfully downloaded: {title}"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/history', methods=['GET'])
def get_history():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT title, platform, timestamp FROM downloads ORDER BY id DESC LIMIT 10")
    rows = cursor.fetchall()
    conn.close()
    
    history = [{"title": r[0], "platform": r[1], "timestamp": r[2]} for r in rows]
    return jsonify(history)

if __name__ == '__main__':
    print("Starting Advanced SocialDown Pro Server...")
    app.run(debug=True, port=5000)