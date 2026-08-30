import os
import sqlite3
import base64
from flask import Flask, render_template, request, jsonify
import yt_dlp
from pathlib import Path

app = Flask(__name__, template_folder='templates')

# Download directory setup
DOWNLOAD_DIR = os.path.join(str(Path.home()), "Downloads", "SocialDown_Pro")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Safe Base64 Cookie Decoder for Render / PythonAnywhere Environment Variable
COOKIE_FILE_PATH = 'cookies.txt'
env_cookies = os.environ.get('YOUTUBE_COOKIES')
if env_cookies:
    try:
        with open(COOKIE_FILE_PATH, 'wb') as f:
            f.write(base64.b64decode(env_cookies.strip()))
    except Exception as e:
        print(f"Cookie decode error: {e}")

# Initialize SQLite Database for History
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
        cookie_path = COOKIE_FILE_PATH if os.path.exists(COOKIE_FILE_PATH) else None

        # Common headers and options to bypass 403 / IP block errors on cloud servers
        common_ydl_opts = {
            'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
            }
        }

        if quality == 'audio':
            save_path = os.path.join(DOWNLOAD_DIR, 'Audio')
            os.makedirs(save_path, exist_ok=True)
            ydl_opts = {
                **common_ydl_opts,
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
                'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}],
            }
        else:
            save_path = os.path.join(DOWNLOAD_DIR, 'YouTube')
            os.makedirs(save_path, exist_ok=True)
            ydl_opts = {
                **common_ydl_opts,
                'format': 'best',
                'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
            }

        if cookie_path:
            ydl_opts['cookiefile'] = cookie_path

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = yt_dlp.YoutubeDL(common_ydl_opts).extract_info(url, download=False) # Quick info fetch
            title = info.get('title', 'Media File')
            ydl.download([url])

        # Save to History Database
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