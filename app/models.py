from sqlalchemy import (
    MetaData, Table, Column, Integer, String, ForeignKey
)
from sqlalchemy import create_engine
import os

# Absolute DB path in container
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:////srv/apps/radiocolloc/runtime/db.sqlite")

metadata = MetaData()

users = Table(
    "users", metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String, unique=True, nullable=False),
)

tracks = Table(
    "tracks", metadata,
    Column("id", Integer, primary_key=True),
    Column("yt_id", String, unique=True, nullable=False),
    Column("title", String, nullable=False),
    Column("filepath", String, nullable=False),
    Column("tags", String, default=""),
)

user_tracks = Table(
    "user_tracks", metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("track_id", Integer, ForeignKey("tracks.id")),
)

def init_db():
    # ensure runtime dir exists
    runtime_dir = os.path.dirname(DATABASE_URL.replace("sqlite:", ""))
    if runtime_dir and not os.path.exists(runtime_dir):
        os.makedirs(runtime_dir, exist_ok=True)
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    metadata.create_all(engine)
    return engine
