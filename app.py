from flask import Flask, jsonify
import requests
import uuid
from datetime import datetime
from pytz import timezone

app = Flask(__name__)

SOURCE_EAST = "https://yp.cdnstream1.com/metadata/2632_128/last/12.json"
SOURCE_WEST = "https://yp.cdnstream1.com/metadata/9999_128/last/12.json"  # Replace with actual west feed URL
SOURCE_THIRD = "https://yp.cdnstream1.com/metadata/8888_128/last/12.json"  # Replace with actual third feed URL

def fetch_tracks(source_url):
    response = requests.get(source_url)
    return response.json()

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
    except Exception:
        pass
    return {"imageUrl": "", "itunesTrackUrl": "", "previewUrl": ""}

def to_spec_format(raw_tracks):
    output = []
    central_time = timezone('America/Chicago')

    for idx, track in enumerate(raw_tracks):
        artist = track.get("tpe1") or "Unknown Artist"
        title = track.get("tit2") or "Unknown Title"
        album = track.get("talb", "")
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

@app.route("/feed.json")
def feed_east():
    raw_tracks = fetch_tracks(SOURCE_EAST)
    converted = to_spec_format(raw_tracks)
    return jsonify({"nowPlaying": converted})

@app.route("/feed-west.json")
def feed_west():
    raw_tracks = fetch_tracks(SOURCE_WEST)
    converted = to_spec_format(raw_tracks)
    return jsonify({"nowPlaying": converted})

@app.route("/feed-third.json")
def feed_third():
    raw_tracks = fetch_tracks(SOURCE_THIRD)
    converted = to_spec_format(raw_tracks)
    return jsonify({"nowPlaying": converted})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
