import requests
import json

BASE = 'https://itunes.apple.com/search?term={}'

def getItunesBody(artist: str, song: str):
    translationTable = str.maketrans("éàáèùâêîôûç", "eaaeuaeiouc")
    artist = artist.translate(translationTable)
    song = song.translate(translationTable)
    if ',' in artist:
        artist = artist[:artist.find(',')]
    elif '&' in artist:
        artist = artist[:artist.find('&')]
    url = BASE.format(artist.replace(' ', '+')+'+'+song.replace(' ', '+')+'&entity=song')
    response = requests.get(url)
    lst = json.loads(response.content)['results']
    for item in lst:
        if artist.lower() in str(item['artistName']).lower().translate(translationTable):
            return item
