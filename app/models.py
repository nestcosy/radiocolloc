from sqlalchemy import (
    MetaData, Table, Column, Integer, String, Text, ForeignKey, Boolean
)
from sqlalchemy import create_engine
from sqlalchemy.sql import func
import os

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./runtime/db.sqlite")

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
    Column("tags", String, default=""),  # CSV of tags
)

user_tracks = Table(
    "user_tracks", metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("track_id", Integer, ForeignKey("tracks.id")),
)

def init_db():
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    metadata.create_all(engine)
    return engine
