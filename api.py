from downloader import download_url

youtube_url = input("input youtube URL")

#location gets the address written in music_dir.txt
with open('music_dir.txt', 'r') as file:
    location = file.read().replace('\n', '')
    download_url(youtube_url, location)