from flask import Flask, request, jsonify, send_file
import yt_dlp
import os
from datetime import datetime

app = Flask(__name__)

TEMP_FOLDER = './temp_mp3s'

if not os.path.exists(TEMP_FOLDER):
    os.makedirs(TEMP_FOLDER)

@app.route('/api/youtube-to-mp3', methods=['GET'])
def youtube_to_mp3():

    video_url = request.args.get('url')
    if not video_url:
        return jsonify({"error": "No URL provided"}), 400

    ydl_opts = {
    'format': 'bestaudio/best',  
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',  
        'preferredquality': '192',  
    }],
    'outtmpl': os.path.join(TEMP_FOLDER, '%(id)s.%(ext)s'),  
    'quiet': True, 
}


    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            video_id = info_dict.get("id")
            mp3_filename = f"{video_id}.mp3"
            mp3_filepath = os.path.join(TEMP_FOLDER, mp3_filename)
            if os.path.exists(mp3_filepath):
                return send_file(mp3_filepath, as_attachment=True, download_name=mp3_filename)
            else:
                return jsonify({"error": "Failed to download and convert video."}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def index():
    return """
    <h1>YouTube to MP3 Converter API</h1>
    <p>Use the following format to request the MP3 file:</p>
    <pre>/api/youtube-to-mp3?url={YOUTUBE_VIDEO_URL}</pre>
    <p>Example: <a href="/api/youtube-to-mp3?url=https://www.youtube.com/watch?v=pRpeEdMmmQ0">
    Convert Example Video</a></p>
    """

if __name__ == '__main__':

    port = int(os.environ.get("PORT", 8000))  
    app.run(host="0.0.0.0", port=port)



