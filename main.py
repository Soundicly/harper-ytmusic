from fastapi import FastAPI, HTTPException
from modules import ytmusic

app = FastAPI()

@app.get("/user")
async def get_user(id: str):
  response = await ytmusic.get_artist(id)
  return response

@app.get("/user/playlists")
async def get_user_playlists(id: str):
  response = await ytmusic.get_user_playlists(id)
  return response

@app.get("/artist")
async def get_artist(id: str):
  response = await ytmusic.get_artist(id)
  return response

@app.get("/album")
async def get_album(id: str):
  response = await ytmusic.get_album(id)
  return response

@app.get("/playlist")
async def get_playlist(id: str, limit: int|None = 100):
  response = await ytmusic.get_playlist(id, limit)
  return response

@app.get("/song")
async def get_song(id: str):
  response = await ytmusic.get_song(id)
  return response

@app.get("/counterpart")
async def get_counterpart(id: str) -> ytmusic.CounterpartSchema:
  response = await ytmusic.get_counterpart(id)
  if response.counterpartId is None:
    raise HTTPException(status_code=404, detail="Counterpart not found")
  return response

@app.get("/search")
async def search(query: str, limit: int|None = 20, filter: ytmusic.SearchFilter = None) -> dict:
  response = await ytmusic.search(query, filter, limit)
  return response