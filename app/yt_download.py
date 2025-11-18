import yt_dlp
import os

def yt_id_from_url(url: str) -> str:
    ydl_opts = {"quiet": True, "skip_download": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info.get("id")

def download(url: str) -> dict:
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join("/srv/apps/radiocolloc/media", "%(id)s.%(ext)s"),
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
        if "entries" in info:
            results = []
            for e in info["entries"]:
                if not e:
                    continue
                ext = "mp3"
                fid = e.get("id")
                title = e.get("title") or fid
                filepath = os.path.join("/srv/apps/radiocolloc/media", f"{fid}.{ext}")
                results.append({"yt_id": fid, "title": title, "filepath": filepath})
            return {"playlist": True, "entries": results}
        else:
            fid = info.get("id")
            title = info.get("title") or fid
            ext = "mp3"
            filepath = os.path.join("/srv/apps/radiocolloc/media", f"{fid}.{ext}")
            return {"playlist": False, "entry": {"yt_id": fid, "title": title, "filepath": filepath}}
