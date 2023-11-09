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
  artist = []
  last = False
  
  for i, word in enumerate(wrong_artists.split()):
    if last:
      artist.append(word)
      if i == len(wrong_artists.split()) - 1:
        artists.append(" ".join(artist))
    if word == "&":
      artists.append(" ".join(artist))
      artist = []
      last = True
      continue
      
    if word.endswith(","):
      word = word[:-1]
      artist.append(word)
      artists.append(" ".join(artist))
      artist = []
    else:
      artist.append(word)
  
  return artists

def get_type(album) -> str|None:
  return album["type"] if "type" in album else None
