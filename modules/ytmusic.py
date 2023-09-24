from ytmusicapi import YTMusic
from enum import Enum

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

ytmusic = YTMusic()
authorized_ytmusic = YTMusic("oauth.json")

async def get_user(user_id: str):
  return ytmusic.get_user(user_id)

async def get_user_playlists(user_id: str):
  return ytmusic.get_user_playlists(user_id)

async def get_album(album_id: str):
  browse_id = ytmusic.get_album_browse_id(album_id)
  return ytmusic.get_album(browse_id)

async def get_album_noauth(album_id: str):
  browse_id = authorized_ytmusic.get_album_browse_id(album_id)
  return authorized_ytmusic.get_album(browse_id)

async def get_playlist(playlist_id: str, limit: int = 100):
  return ytmusic.get_playlist(playlist_id, limit)

async def get_song(song_id: str):
  return ytmusic.get_song(song_id)

async def get_artist(artist_id: str):
  return ytmusic.get_artist(artist_id)

async def search(query: str, filter: SearchFilter = None, limit: int = 20):
  return ytmusic.search(query, filter=filter.value if filter else None, limit=limit)
