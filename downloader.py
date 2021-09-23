import youtube_dl
import eyed3
import os
import urllib.request
import shutil
import re
from pathlib import Path
from album import getItunesBody
from video2mp3 import video_to_mp3
from mp3_tagger import MP3File, VERSION_BOTH

def songDownloader(video_info, location, artist=None, album=None):
    song = {'name':''}
    song['title'] = nameCleaner(video_info['title'])
    if song['title'].find('- ') > 0 or '(' in song['title'] or '[' in song['title']:
        temp =''
        if song['title'].find('- ')>0:
            temp = song['title'][song['title'].find('- ') + 2:].replace('.mp3', '')
        else:
            temp = song['title'].replace('.mp3', '')
        if '(' in temp:
            song['name'] = temp[:temp.find('(')-1]
        elif '[' in temp:
            song['name'] = temp[:temp.find('[')-1]
        else:
            song['name'] = temp
    elif song['title'].find('– ') > 0:
        temp = song['title'][song['title'].find('– ') + 2:].replace(
            '.mp3', '')
        song['name'] = re.sub(r'\([^)]*\)', '', temp).rstrip()
    else:
        song['name'] = re.sub(r'\([^)]*\)', '', song['title']).replace('.mp3', '')
    if song['title'].find(' -') > 0:
        temp = song['title'][:song['title'].find(' -')]
    if not artist:
        if video_info.get('creator'):
            song['artist'] = video_info['creator']
        elif song['title'].find('ft.')> 0:
            song['artist'] = song['title'][:song['title'].find('ft.')].rstrip()
        elif '–' in song['title']:
            song['artist'] = song['title'][:song['title'].find(' –')]
        else:
            song['artist'] = song['title'][:song['title'].find(' -')]
    elif artist.find('–') > 0:
        artist = artist[:artist.find('-')].rstrip(' ')
        song['artist'] = artist
    else:
        try:
            if temp.replace(' ', '') in artist:
                song['artist'] = temp
        finally:
            pass
    itunes_data = getItunesBody(song['artist'], song['name'])
    if itunes_data:
        if not album:
            song['album'] = itunes_data['collectionName']
        else:
            song['album'] = album
        if itunes_data['artworkUrl100']:
            song['image-url'] = itunes_data['artworkUrl100'].replace(
                '100x100', '500x500')
    path = ''
    if song.get('album') == None:
        song['album'] = song['name'] + ' - Single'
        path = os.path.join(location,
                            removeWinForbiden(song['artist']),
                            removeWinForbiden(song['album']))
    else:
        path = os.path.join(location,
                            removeWinForbiden(song['artist']),
                            removeWinForbiden(song['album']))
    print(path)
    song['folder'] = path
    song['address'] = path + "\\" + removeWinForbiden(
        song['name']) + '.mp3'

    Path(path).mkdir(parents=True, exist_ok=True)
    date = video_info['upload_date']
    song['date'] = date[:4] + '-' + date[4:6] + '-' + date[6:]
    options = getOps(song['address'])
    with youtube_dl.YoutubeDL(options) as ydl:
        ydl.download([video_info['webpage_url']])

    if os.listdir(song['folder']) == None:
        repairIssue(song['folder'])

    setValues(song)


def download_url(video_url: str, location: str):
    video_info = youtube_dl.YoutubeDL().extract_info(
        url=video_url, download=False
    )

    # if it's a playlist
    if video_info.get('entries'):
        for i in range(len(video_info['entries'])):
            print(i)
            try: songDownloader(video_info['entries'][i], location, video_info['uploader'], video_info['title'])
            except: songDownloader(video_info['entries'][i],location,  video_info['entries'][0]['uploader'], video_info['title'])
    else:
        songDownloader(video_info, location)

def repairIssue(folder: str):
    if os.path.exists(folder+'#'):
        for file in os.listdir(folder):
           shutil.move(folder+'#'+file, folder+file)
        os.remove(folder+'#')


def getOps(path):
    return {
        'format': 'bestaudio/best',
        'keepvideo': False,
        'outtmpl': path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    }

def setValues(song):
    path = song['address']
    with open(path) as file:
        audio = eyed3.load(path)
        if audio is None:
            return
        if 'webm' in eyed3.mimetype.guessMimetype(song['address']):
            video_to_mp3(path)
            audio = eyed3.load(path)
        if audio.tag == None:
            audio.initTag()

        audio.tag.artist = song['artist']
        audio.tag.title = song['name']
        audio.tag.release_date = song['date']
        audio.tag.album = song['album']

        song['cover-path'] = os.path.join(song['folder'], removeWinForbiden(song['album'])+'.jpg')
        try:
            urllib.request.urlretrieve(song['image-url'], song['cover-path'])
            imageData = open(song['cover-path'], "rb").read()
            audio.tag.images.set(3, imageData, "image/jpeg")
            audio.tag.save(version=eyed3.id3.ID3_V2_3)
            os.remove(song['cover-path'])
        except:
            audio.tag.save()


def nameCleaner(name):
    name = f"{name.replace(' (Official Music Video)', '')}"
    name = f"{name.replace(' Official Music Video', '')}"
    name = f"{name.replace(' Official music video', '')}"
    name = f"{name.replace(' (Official music video)', '')}"
    name = f"{name.replace(' Clip officiel', '')}"
    name = f"{name.replace(' (Clip officiel)', '')}.mp3"
    return name

def removeWinForbiden(str: str):
    new = ""
    forbidens = ["\\", "/", ":", "*", "?", "\"", "<", ">", "|"]
    for c in str:
        if c not in forbidens:
            new+= c
    return new.rstrip()