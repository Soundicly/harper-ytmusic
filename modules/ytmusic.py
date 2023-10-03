from ytmusicapi import YTMusic
from enum import Enum
from pydantic import BaseModel

#############################
# LEAVING ALL METHODS ASYNC #
# FOR A FUTURE :D           #
#############################

class SearchFilter(str, Enum):
  SONGS = "songs"
  VIDEOS = "videos"
  ALBUMS = "albums"
  ARTISTS = "artists"
  PLAYLISTS = "playlists"
  COMMUNITY_PLAYLISTS = "community_playlists"
  FEATURED_PLAYLISTS = "featured_playlists"
  UPLOADS = "uploads"

authorized_ytmusic = None

async def get_ytmusic() -> YTMusic:
  global authorized_ytmusic
  if not authorized_ytmusic:
    authorized_ytmusic = await YTMusic.create("oauth.json")
  
  return authorized_ytmusic

async def get_user(user_id: str):
  authorized_ytmusic = await get_ytmusic()
  return await authorized_ytmusic.get_user(user_id)

async def get_user_playlists(user_id: str):
  authorized_ytmusic = await get_ytmusic()
  return await authorized_ytmusic.get_user_playlists(user_id)

async def get_album(album_id: str):
  authorized_ytmusic = await get_ytmusic()
  if not album_id.startswith("MPREb_"):
    album_id = await authorized_ytmusic.get_album_browse_id(album_id)
    
  return await authorized_ytmusic.get_album(album_id)

async def get_playlist(playlist_id: str, limit: int = 100):
  authorized_ytmusic = await get_ytmusic()
  return await authorized_ytmusic.get_playlist(playlist_id, limit)

async def get_song(song_id: str):
  authorized_ytmusic = await get_ytmusic()
  return await authorized_ytmusic.get_song(song_id)

async def get_counterpart(song_id: str):
  authorized_ytmusic = await get_ytmusic()
  return await authorized_ytmusic.get_watch_playlist(song_id, limit=5)

async def get_watchlist_of_playlist(playlist_id: str):
  authorized_ytmusic = await get_ytmusic()
  return await authorized_ytmusic.get_watch_playlist(playlistId=playlist_id, limit=100)

async def get_artist(artist_id: str):
  authorized_ytmusic = await get_ytmusic()
  return await authorized_ytmusic.get_artist(artist_id)

async def search(query: str, filter: SearchFilter = None, limit: int = 20):
  authorized_ytmusic = await get_ytmusic()
  return await authorized_ytmusic.search(query, filter=filter.value if filter else None, limit=limit)
