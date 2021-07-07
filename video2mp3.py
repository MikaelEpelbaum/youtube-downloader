import os
import pydub

def video_to_mp3(file_name):
    mp3_file = os.path.splitext(file_name)[0] + '.mp3'
    audio = pydub.AudioSegment.from_file(file_name, "webm")
    audio.export(file_name, format="mp3", bitrate="320k")