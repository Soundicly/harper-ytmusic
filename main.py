from fastapi import FastAPI, HTTPException
from modules import ytmusic, parse_utils
from pydantic import BaseModel
import os
import json

USE_REDIS = os.getenv("REDIS_URL") is not None
if USE_REDIS:
  from modules import redis_cache
  print("Using redis as cache")

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
  response = None
  if USE_REDIS:
    response = await redis_cache.get(f"artist:{id}")
  if not response:
    response = await ytmusic.get_artist(id)
    if USE_REDIS:
      await redis_cache.set(f"artist:{id}", response)

  return Artist(
      name=response["name"],
      channelId=response["channelId"],
      subscribers=response["subscribers"],
      imageUrl=response["thumbnails"][-1]["url"],
  )


class SimpleAlbumTrack(BaseModel):
  title: str
  artists: list[SimpleArtist]
  videoId: str
  album: str
  durationSeconds: int

class AlbumBrowseId(BaseModel):
  browseId: str

@app.get("/album/browseId")
async def get_album_browseId(playlist_id: str) -> AlbumBrowseId:
  browse_id = playlist_id
  if not browse_id.startswith("MPREb_"):
    browse_id_redis = None
    if USE_REDIS:
      browse_id_redis = await redis_cache.get(f"album_b:{id}")
    if browse_id_redis:
      browse_id = browse_id_redis
    else:
      browse_id = await ytmusic.get_browse_id(browse_id)
      if USE_REDIS:
        await redis_cache.set(f"album_b:{id}", browse_id)
  
  return AlbumBrowseId(browseId=browse_id)
class Album(BaseModel):
  browseId: str
  title: str
  coverUrl: str
  artists: list[SimpleArtist]
  type: str
  trackCount: int
  year: str
  playlistId: str
  durationSeconds: int
  tracks: list[SimpleAlbumTrack]


@app.get("/album")
async def get_album(id: str) -> Album:
  browse_id = id
  if not browse_id.startswith("MPREb_"):
    browse_id_redis = None
    if USE_REDIS:
      browse_id_redis = await redis_cache.get(f"album_b:{id}")
    if browse_id_redis:
      browse_id = browse_id_redis
    else:
      browse_id = await ytmusic.get_browse_id(browse_id)
      if USE_REDIS:
        await redis_cache.set(f"album_b:{id}", browse_id)
  
  response = None
  response_watchlist = None
  if USE_REDIS:
    response = await redis_cache.get(f"album:{browse_id}")
    response_watchlist = await redis_cache.get(f"album_w:{browse_id}")
  if not response:
    response = await ytmusic.get_album(browse_id)
    if USE_REDIS:
      await redis_cache.set(f"album:{browse_id}", response)

  audio_playlist_id = response["audioPlaylistId"]
  if not response_watchlist:
    response_watchlist = await ytmusic.get_watchlist_of_playlist(audio_playlist_id)
    if USE_REDIS:
      await redis_cache.set(f"album_w:{audio_playlist_id}", response_watchlist)


  return Album(
      browseId=browse_id,
      title=response["title"],
      coverUrl=response["thumbnails"][-1]["url"],
      artists=[
          SimpleArtist(name=artist["name"], topicId=artist["id"])
          for artist in parse_utils.process_artists(response["artists"])
      ],
      type=response["type"],
      trackCount=response["trackCount"],
      year=response["year"],
      playlistId=response["audioPlaylistId"],
      durationSeconds=response["duration_seconds"],
      tracks=[
          SimpleAlbumTrack(
              title=track["title"],
              artists=[
                  SimpleArtist(name=artist["name"], topicId=artist["id"])
                  for artist in parse_utils.process_artists(track["artists"])
              ],
              videoId=track["videoId"],
              album=track["album"]["name"],
              durationSeconds=response["tracks"][i]["duration_seconds"] if "duration_seconds" in response["tracks"][i] else -1,
          )
          for i, track in enumerate(response_watchlist["tracks"])
      ],
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
  response = None
  if USE_REDIS:
    response = await redis_cache.get(f"song:{id}")
  if not response:
    response = await ytmusic.get_song(id)
    if USE_REDIS:
      await redis_cache.set(f"song:{id}", response)
    
  response = response["videoDetails"]

  return Track(
      title=response["title"],
      videoId=response["videoId"],
      durationSeconds=int(response["lengthSeconds"]),
      channel=response["author"],
      channelId=response["channelId"],
      coverUrl=response["thumbnail"]["thumbnails"][-1]["url"],
      viewCount=int(response["viewCount"]),
  )

class CounterpartSchema(BaseModel):
  counterpartId: str|None


@app.get("/counterpart")
async def get_counterpart(id: str) -> CounterpartSchema:
  response = None
  if USE_REDIS:
    response = await redis_cache.get(f"counterpart:{id}")
  if not response:
    response = await ytmusic.get_counterpart(id)
    if USE_REDIS:
      await redis_cache.set(f"counterpart:{id}", response)
    
  video_info = response["tracks"][0]
  
  if "counterpart" not in video_info:
    raise HTTPException(status_code=404, detail="Counterpart not found")
  
  return CounterpartSchema(counterpartId=video_info["counterpart"]["videoId"])

class AlbumSearchResult(BaseModel):
  title: str
  browseId: str
  type: str
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
async def search(
  query: str, limit: int | None = 20, filter: ytmusic.SearchFilter = None
) -> SearchResponse:
  response = await ytmusic.search(query, filter, limit)

  tracks: list[SongSearchResult] = []
  albums: list[AlbumSearchResult] = []
  artists: list[ArtistSearchResult] = []

  with open("search.json", "w") as f:
    json.dump(response, f, indent=2)

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
          artists.append(
              ArtistSearchResult(
                  name=res["artist"],
                  topicId=res["browseId"],
                  imageUrl=res["thumbnails"][-1]["url"],
              )
          )
      elif res["category"] == "Albums":
          if "browserId" not in res:
            print(f"Weird album: {res}")
            continue
          
          albums.append(
              AlbumSearchResult(
                  title=res["title"],
                  browseId=res["browseId"],
                  type=res["type"],
                  artists=[
                      SimpleArtist(name=artist["name"], topicId=artist["id"])
                      for artist in parse_utils.process_artists(res["artists"])
                  ],
                  coverUrl=res["thumbnails"][-1]["url"],
              )
          )
      elif res["category"] == "Songs":
          tracks.append(
              SongSearchResult(
                  title=res["title"],
                  artists=[
                      SimpleArtist(name=artist["name"], topicId=artist["id"])
                      for artist in parse_utils.process_artists(res["artists"])
                  ],
                  album=SimpleAlbum(name=res["album"]["name"], id=res["album"]["id"]),
                  videoId=res["videoId"],
                  durationSeconds=res["duration_seconds"],
                  imageUrl=res["thumbnails"][-1]["url"],
              )
          )

  if filter and filter.value == "albums" and len(albums) == 0:
    songs = await search(query, limit, ytmusic.SearchFilter.SONGS)
    for song in songs.tracks:
      if not song.album:
        continue
      
      albumid = song.album.id
      albumfromsong = await ytmusic.get_album(albumid)

      albums.append(
        AlbumSearchResult(
          title=albumfromsong["title"],
          browseId=albumid,
          type=albumfromsong["type"],
          artists=[
            SimpleArtist(name=artist["name"], topicId=artist["id"])
            for artist in parse_utils.process_artists(albumfromsong["artists"])
          ],
          coverUrl=albumfromsong["thumbnails"][-1]["url"],
        )
      )
      
  return SearchResponse(tracks=tracks, albums=albums, artists=artists)


class SimplePlaylistTrack(BaseModel):
  title: str
  artists: list[SimpleArtist]
  videoId: str
  album: SimpleAlbum
  durationSeconds: int
  explicit: bool


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
async def get_playlist(id: str, limit: int | None = 100) -> Playlist:
  response = await ytmusic.get_playlist(id, limit)

  return Playlist(
      title=response["title"],
      description=response["description"] if response["description"] else "",
      playlistId=response["id"],
      coverUrl=response["thumbnails"][-1]["url"],
      author=SimpleArtist(
          name=response["author"]["name"], topicId=response["author"]["id"]
      ),
      trackCount=response["trackCount"],
      durationSeconds=response["duration_seconds"],
      tracks=[
          SimplePlaylistTrack(
              title=track["title"],
              artists=[
                  SimpleArtist(name=artist["name"], topicId=artist["id"])
                  for artist in parse_utils.process_artists(track["artists"])
              ],
              videoId=track["videoId"],
              album=SimpleAlbum(name=track["album"]["name"], id=track["album"]["id"]),
              durationSeconds=track["duration_seconds"],
              explicit=track["isExplicit"],
          )
          for track in response["tracks"]
      ],
  )
