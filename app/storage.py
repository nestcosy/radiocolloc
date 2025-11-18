import os
from pathlib import Path

MEDIA_ROOT = os.environ.get("MEDIA_ROOT", "/data/media")

Path(MEDIA_ROOT).mkdir(parents=True, exist_ok=True)

def track_path(filename: str) -> str:
    return str(Path(MEDIA_ROOT) / filename)
