from fastapi import FastAPI, HTTPException
from modules import ytmusic
from pydantic import BaseModel

app = FastAPI()

@app.get("/user")
async def get_user(id: str) -> dict:
  response = await ytmusic.get_user(id)
  return response

@app.get("/user/playlists")
async def get_user_playlists(id: str):
  response = await ytmusic.get_user_playlists(id)
  return response

class Artist(BaseModel):
  name: str
  channelId: str
  subscribers: str
  imageUrl: str

class SimpleArtist(BaseModel):
  name: str
  topicId: str

@app.get("/artist")
async def get_artist(id: str) -> Artist:
  response = await ytmusic.get_artist(id)
  
  return Artist(
    name=response["name"],
    channelId=response["channelId"],
    subscribers=response["subscribers"],
    imageUrl=response["thumbnails"][-1]["url"]
  )

class SimpleAlbumTrack(BaseModel):
  title: str
  artists: list[SimpleArtist]
  videoId: str
  album: str
  durationSeconds: int

class Album(BaseModel):
  title: str
  coverUrl: str
  artists: list[SimpleArtist]
  trackCount: int
  year: str
  playlistId: str
  durationSeconds: int
  tracks: list[SimpleAlbumTrack]

@app.get("/album")
async def get_album(id: str, browse_id: bool=False) -> Album:
  response = await ytmusic.get_album(id, browse_id)
  
  return Album(
    title=response["title"],
    coverUrl=response["thumbnails"][-1]["url"],
    artists=[SimpleArtist(name=artist["name"], topicId=artist["id"]) for artist in response["artists"]],
    trackCount=response["trackCount"],
    year=response["year"],
    playlistId=response["audioPlaylistId"],
    durationSeconds=response["duration_seconds"],
    tracks=[SimpleAlbumTrack(
      title=track["title"],
      artists=[SimpleArtist(name=artist["name"], topicId=artist["id"]) for artist in track["artists"]],
      videoId=track["videoId"],
      album=track["album"],
      durationSeconds=track["duration_seconds"]
    ) for track in response["tracks"]]
  )

class Track(BaseModel):
  title: str
  videoId: str
  durationSeconds: int
  channel: str
  channelId: str
  coverUrl: str
  viewCount: int

@app.get("/song")
async def get_song(id: str) -> Track:
  response = await ytmusic.get_song(id)
  response = response["videoDetails"]
  
  return Track(
    title=response["title"],
    videoId=response["videoId"],
    durationSeconds=int(response["lengthSeconds"]),
    channel=response["author"],
    channelId=response["channelId"],
    coverUrl=response["thumbnail"][-1]["url"],
    viewCount=int(response["viewCount"])
  )

@app.get("/counterpart")
async def get_counterpart(id: str) -> ytmusic.CounterpartSchema:
  response = await ytmusic.get_counterpart(id)
  if response.counterpartId is None:
    raise HTTPException(status_code=404, detail="Counterpart not found")
  return response

class AlbumSearchResult(BaseModel):
  title: str
  artists: list[SimpleArtist]
  coverUrl: str

class SimpleAlbum(BaseModel):
  name: str
  id: str

class SongSearchResult(BaseModel):
  title: str
  artists: list[SimpleArtist]
  album: SimpleAlbum
  videoId: str
  durationSeconds: int
  imageUrl: str

class ArtistSearchResult(BaseModel):
  name: str
  topicId: str
  imageUrl: str

class SearchResponse(BaseModel):
  tracks: list[SongSearchResult]
  albums: list[AlbumSearchResult]
  artists: list[ArtistSearchResult]

@app.get("/search")
async def search(query: str, limit: int|None = 20, filter: ytmusic.SearchFilter = None) -> SearchResponse:
  response = await ytmusic.search(query, filter, limit)
  
  tracks: list[SongSearchResult] = []
  albums: list[AlbumSearchResult] = []
  artists: list[ArtistSearchResult] = []
  
  for res in response:
    if res["category"] == "Top result":
      if res["resultType"] == "album":
        res["category"] = "Albums"
      elif res["resultType"] == "song":
        res["category"] = "Songs"
      elif res["resultType"] == "artist":
        res["category"] = "Artists"
        res["artist"] = res["artists"][0]["name"]
        res["browseId"] = res["artists"][0]["id"]
    
    if res["category"] == "Artists":
      artists.append(ArtistSearchResult(
        name=res["artist"],
        topicId=res["browseId"],
        imageUrl=res["thumbnails"][-1]["url"]
      ))
    elif res["category"] == "Albums":
      albums.append(AlbumSearchResult(
        title=res["title"],
        artists=[SimpleArtist(name=artist["name"], topicId=artist["id"]) for artist in res["artists"]],
        coverUrl=res["thumbnails"][-1]["url"]
      ))
    elif res["category"] == "Songs":
      tracks.append(SongSearchResult(
        title=res["title"],
        artists=[SimpleArtist(name=artist["name"], topicId=artist["id"]) for artist in res["artists"]],
        album=SimpleAlbum(name=res["album"]["name"], id=res["album"]["id"]),
        videoId=res["videoId"],
        durationSeconds=res["duration_seconds"],
        imageUrl=res["thumbnails"][-1]["url"]
      ))
  
  return SearchResponse(
    tracks=tracks,
    albums=albums,
    artists=artists
  )

class SimplePlaylistTrack(BaseModel):
  title: str
  artists: list[SimpleArtist]
  videoId: str
  album: SimpleAlbum
  durationSeconds: int

class Playlist(BaseModel):
  title: str
  description: str
  playlistId: str
  coverUrl: str
  author: SimpleArtist
  trackCount: int
  durationSeconds: int
  tracks: list[SimplePlaylistTrack]

@app.get("/playlist")
async def get_playlist(id: str, limit: int|None = 100) -> Playlist:
  response = await ytmusic.get_playlist(id, limit)
  
  return Playlist(
    title=response["title"],
    description=response["description"],
    playlistId=response["id"],
    coverUrl=response["thumbnails"][-1]["url"],
    author=SimpleArtist(name=response["author"]["name"], topicId=response["author"]["id"]),
    trackCount=response["trackCount"],
    durationSeconds=response["duration_seconds"],
    tracks=[SimplePlaylistTrack(
      title=track["title"],
      artists=[SimpleArtist(name=artist["name"], topicId=artist["id"]) for artist in track["artists"]],
      videoId=track["videoId"],
      album=SimpleAlbum(name=track["album"]["name"], id=track["album"]["id"]),
      durationSeconds=track["duration_seconds"]
    ) for track in response["tracks"]]
  )
