import yt_dlp
import os
from storage import track_path
import hashlib

def sanitize_title(title: str) -> str:
    # simple sanitize
    return "".join(c for c in title if c.isalnum() or c in " _-").strip()

def yt_id_from_url(url: str) -> str:
    # use yt-dlp to extract info
    ydl_opts = {"quiet": True, "skip_download": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info.get("id")

def download(url: str, out_filename_prefix: str = "") -> dict:
    """
    Télécharge la vidéo/audio et retourne dict {yt_id, title, filepath}
    """
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join("/data/media", "%(id)s.%(ext)s"),
        "quiet": True,
        "noplaylist": False,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        # For playlists, return list of entries; handle single item or playlist
        if "entries" in info:
            results = []
            for e in info["entries"]:
                if not e:
                    continue
                ext = "mp3"
                fid = e.get("id")
                title = e.get("title") or fid
                filepath = os.path.join("/data/media", f"{fid}.{ext}")
                results.append({"yt_id": fid, "title": title, "filepath": filepath})
            return {"playlist": True, "entries": results}
        else:
            fid = info.get("id")
            title = info.get("title") or fid
            ext = "mp3"
            filepath = os.path.join("/data/media", f"{fid}.{ext}")
            return {"playlist": False, "entry": {"yt_id": fid, "title": title, "filepath": filepath}}
