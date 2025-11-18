from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from models import init_db, users, tracks, user_tracks
from storage import MEDIA_ROOT, track_path
from yt_download import download, yt_id_from_url
from sqlalchemy import select, insert
import os
from starlette.responses import Response
from uuid import uuid4

# init
engine = init_db()
app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# simple in-memory sessions (for demo). In production, use redis or signed cookies.
sessions = {}

def get_current_user(request: Request):
    sid = request.cookies.get("sid")
    if not sid:
        return None
    return sessions.get(sid)

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    # list tags from tracks
    with engine.connect() as conn:
        res = conn.execute(select(tracks)).fetchall()
        tags = set()
        for r in res:
            t = r["tags"] or ""
            for tag in [x.strip() for x in t.split(",") if x.strip()]:
                tags.add(tag)
    return templates.TemplateResponse("index.html", {"request": request, "tags": sorted(tags), "user": get_current_user(request)})

@app.post("/login")
def login(response: Response, username: str = Form(...)):
    username = username.strip()
    if not username:
        raise HTTPException(status_code=400, detail="username required")
    with engine.connect() as conn:
        r = conn.execute(select(users).where(users.c.username == username)).first()
        if not r:
            result = conn.execute(insert(users).values(username=username))
            conn.commit()
            user_id = result.inserted_primary_key[0]
        else:
            user_id = r["id"]
    sid = str(uuid4())
    sessions[sid] = {"id": user_id, "username": username}
    response = RedirectResponse("/", status_code=303)
    response.set_cookie("sid", sid, httponly=True)
    return response

@app.post("/logout")
def logout(response: Response, request: Request):
    sid = request.cookies.get("sid")
    if sid and sid in sessions:
        del sessions[sid]
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie("sid")
    return response

@app.post("/add")
async def add_track(request: Request, url: str = Form(...)):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="must be logged in")
    # get yt id first
    try:
        info = download(url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"download error: {e}")
    added = []
    with engine.connect() as conn:
        if info.get("playlist"):
            for e in info["entries"]:
                yt_id = e["yt_id"]
                title = e["title"]
                filepath = e["filepath"]
                existing = conn.execute(select(tracks).where(tracks.c.yt_id == yt_id)).first()
                if not existing:
                    res = conn.execute(insert(tracks).values(yt_id=yt_id, title=title, filepath=filepath))
                    conn.commit()
                    track_id = res.inserted_primary_key[0]
                else:
                    track_id = existing["id"]
                # link to user
                already = conn.execute(select(user_tracks).where(user_tracks.c.user_id==user["id"]).where(user_tracks.c.track_id==track_id)).first()
                if not already:
                    conn.execute(insert(user_tracks).values(user_id=user["id"], track_id=track_id))
                    conn.commit()
                added.append({"yt_id": yt_id, "title": title})
        else:
            e = info["entry"]
            yt_id = e["yt_id"]
            title = e["title"]
            filepath = e["filepath"]
            existing = conn.execute(select(tracks).where(tracks.c.yt_id == yt_id)).first()
            if not existing:
                res = conn.execute(insert(tracks).values(yt_id=yt_id, title=title, filepath=filepath))
                conn.commit()
                track_id = res.inserted_primary_key[0]
            else:
                track_id = existing["id"]
            already = conn.execute(select(user_tracks).where(user_tracks.c.user_id==user["id"]).where(user_tracks.c.track_id==track_id)).first()
            if not already:
                conn.execute(insert(user_tracks).values(user_id=user["id"], track_id=track_id))
                conn.commit()
            added.append({"yt_id": yt_id, "title": title})
    return JSONResponse({"added": added})

@app.get("/tracks/random")
def random_track():
    with engine.connect() as conn:
        res = conn.execute(select(tracks)).fetchall()
        if not res:
            raise HTTPException(status_code=404, detail="no tracks")
        import random
        t = random.choice(res)
        return {"id": t["id"], "title": t["title"], "filepath": t["filepath"], "tags": t["tags"]}

@app.get("/tracks/by_tag/{tag}")
def tracks_by_tag(tag: str):
    with engine.connect() as conn:
        res = conn.execute(select(tracks)).fetchall()
        matches = [dict(r) for r in res if tag in ((r["tags"] or "").split(","))]
        if not matches:
            raise HTTPException(status_code=404, detail="no tracks for tag")
        import random
        t = random.choice(matches)
        return {"id": t["id"], "title": t["title"], "filepath": t["filepath"], "tags": t["tags"]}

@app.get("/media/{filename}")
def media_file(filename: str):
    path = os.path.join("/data/media", filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404)
    return FileResponse(path, media_type="audio/mpeg")
