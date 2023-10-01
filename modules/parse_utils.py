def process_artists(artists: list[dict]) -> list[dict]:
  final_artists = []
  
  for artist in artists:
    if artist["id"] is not None:
      final_artists.append({
          "name": artist["name"],
          "id": artist["id"],
      })
      
    for fixed_artist in parse_wrong_artists(artist["name"]):
      final_artists.append({
          "name": fixed_artist,
          "id": "",
      })
  
  return final_artists

# wrong_artists: Example1, Example2 & Example3
def parse_wrong_artists(wrong_artists: str) -> list[str]:
  artists = []
  cache = []
  
  for artist in wrong_artists.split():
    if artist == "&":
      continue
      
    if artist.endswith(","):
      artist = artist[:-1]
      cache.append(artist)
      artists.append(" ".join(cache))
      cache = []
    else:
      cache.append(artist)
  
  return artists