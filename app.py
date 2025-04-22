+from flask import Flask, jsonify, send_from_directory, render_template_string
+from flask_cors import CORS
import requests
import uuid
from datetime import datetime
from pytz import timezone

+CORS(app := Flask(
+    __name__,
+    static_folder="static",        # where your player HTML/CSS/JS will go
+    template_folder="static"       # same folder for index.html
+))

SOURCE_EAST = "https://yp.cdnstream1.com/metadata/2632_128/last/12.json"  # East JSON Feed from SoundStack (WFME)
SOURCE_WEST = "https://yp.cdnstream1.com/metadata/2638_128/last/12.json"  # West JSON Feed from SoundStack (KEAR)
SOURCE_THIRD = "https://yp.cdnstream1.com/metadata/2878_128/last/12.json"  # Will be Worship JSON Feed from SoundStack

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Family Radio Feeds</title>
    <style>
        body { font-family: sans-serif; text-align: center; padding-top: 50px; }
        h1 { margin-bottom: 30px; }
        .button {
            display: inline-block;
            margin: 10px;
            padding: 15px 30px;
            font-size: 18px;
            background-color: #0077cc;
            color: white;
            text-decoration: none;
            border-radius: 8px;
        }
        .button:hover {
            background-color: #005fa3;
        }
    </style>
</head>
<body>
    <h1>Family Radio JSON Feeds</h1>
    <a class="button" href="/east-feed.json" target="_blank">East Feed (WFME)</a>
    <a class="button" href="/west-feed.json" target="_blank">West Feed (KEAR)</a>
    <a class="button" href="/worship-feed.json" target="_blank">Worship Feed</a>
</body>
</html>
'''

def fetch_tracks(source_url):
    try:
        response = requests.get(source_url, timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[ERROR] Failed to fetch from {source_url}: {e}")
        return []

def lookup_itunes(artist, title):
    try:
        query = f"{artist} {title}"
        url = "https://itunes.apple.com/search"
        params = {"term": query, "limit": 1}
        r = requests.get(url, params=params)
        results = r.json().get("results", [])
        if results:
            item = results[0]
            return {
                "imageUrl": item.get("artworkUrl100", "").replace("100x100", "450x450"),
                "itunesTrackUrl": item.get("trackViewUrl", ""),
                "previewUrl": item.get("previewUrl", "")
            }
    except Exception as e:
        print(f"[WARN] iTunes lookup failed for {artist} - {title}: {e}")
    return {"imageUrl": "", "itunesTrackUrl": "", "previewUrl": ""}

def to_spec_format(raw_tracks):
    output = []
    central_time = timezone('America/Chicago')

    for idx, track in enumerate(raw_tracks):
        artist = track.get("TPE1") or "Family Radio"
        title = track.get("TIT2") or "FamilyRadio.org"
        album = track.get("TALB", "")
        duration = track.get("duration", "00:03:00")
        start_time = track.get("start_time", datetime.now().timestamp())
        time_str = datetime.fromtimestamp(start_time, tz=central_time).isoformat()

        metadata = lookup_itunes(artist, title)

        track_obj = {
            "id": str(uuid.uuid4()),
            "artist": artist,
            "title": title,
            "album": album,
            "time": time_str,
            "imageUrl": metadata.get("imageUrl", ""),
            "itunesTrackUrl": metadata.get("itunesTrackUrl", ""),
            "previewUrl": metadata.get("previewUrl", ""),
            "duration": duration,
            "status": "playing" if idx == 0 else "history",
            "type": "song"
        }

        output.append(track_obj)
    return output

@app.route("/")
def homepage():
    return render_template_string(HTML_TEMPLATE)

@app.route("/east-feed.json")
def feed_east():
    try:
        raw_tracks = fetch_tracks(SOURCE_EAST)
        return jsonify({"nowPlaying": to_spec_format(raw_tracks)})
    except Exception as e:
        print(f"[ERROR] /east-feed.json failed: {e}")
        return jsonify({"error": "Failed to load EAST feed"}), 500

@app.route("/west-feed.json")
def feed_west():
    try:
        raw_tracks = fetch_tracks(SOURCE_WEST)
        return jsonify({"nowPlaying": to_spec_format(raw_tracks)})
    except Exception as e:
        print(f"[ERROR] /west-feed.json failed: {e}")
        return jsonify({"error": "Failed to load WEST feed"}), 500

@app.route("/worship-feed.json")
def feed_third():
    try:
        raw_tracks = fetch_tracks(SOURCE_THIRD)
        return jsonify({"nowPlaying": to_spec_format(raw_tracks)})
    except Exception as e:
        print(f"[ERROR] /worship-feed.json failed: {e}")
        return jsonify({"error": "Failed to load Worship feed"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
