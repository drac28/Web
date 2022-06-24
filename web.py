from requests import get
import os, re
import youtube_dl
import spotipy
from spotipy.oauth2 import SpotifyOAuth

url = input("URL: ")
digits = int(input("Digits of number: "))
track_names = []
track_info = []

def delete_output():
    for file in os.listdir("output"):
        os.remove("output/"+file)

def download_folder(url, digits):
    if "[" in url:
        i_orig = int(re.findall(r'\[.*?\]', url)[0].replace("[", "").replace("]", ""))
        i = i_orig
        while True:
            if digits == 1:
                num = str(i)
            elif digits == 2:
                if i < 10:
                    num = "0"+str(i)
                else:
                    num = str(i)
            elif digits == 3:
                if i < 10:
                    num = "00"+str(i)
                elif i < 100:
                    num = "0"+str(i)
                else:
                    num = str(i)
            request = get(url.replace(f"[{i_orig}]", num))
            if request.status_code != 200:
                print("Stopped at", i-1)
                break
            else:
                open("output/"+str(i)+os.path.splitext(url)[1], "wb").write(request.content)
            i += 1

def show_tracks(results):
    for i, item in enumerate(results['items']):
        track = item['track']
        print(
            "   %d %32.32s %s" %
            (i, track['artists'][0]['name'], track['name']))
        track_info.append([track['artists'][0]['name'], track['name']])
        track_names.append(f"ytsearch:{track['artists'][0]['name']} {track['name']}")

def download_playlist_spotify(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'noplaylist': 'True'
    }
    scope = 'playlist-read-private'
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id="7e45f0a8294c46e98dc18fb5a12dbfb8",
        client_secret="bc856da8f6ae48d496f1b875d1bc624a",
        redirect_uri="http://google.com/",
        scope=scope
    ))
    os.chdir("output")
    results = sp.playlist(url, fields="tracks,next")
    tracks = results['tracks']
    show_tracks(tracks)

    while tracks['next']:
        tracks = sp.next(tracks)
        show_tracks(tracks)
    
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download(track_names)

    for file in os.listdir():
        for track in track_info:
            if track[1] in file:
                os.rename(file, track[0]+" - "+track[1]+".mp3")

def download_favourites_spotify():
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'noplaylist': 'True'
    }
    scope = 'user-library-read'
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id="7e45f0a8294c46e98dc18fb5a12dbfb8",
        client_secret="bc856da8f6ae48d496f1b875d1bc624a",
        redirect_uri="http://google.com/",
        scope=scope
    ))
    os.chdir("output")
    tracks = sp.current_user_saved_tracks()
    show_tracks(tracks)

    while tracks['next']:
        tracks = sp.next(tracks)
        show_tracks(tracks)
    
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download(track_names)

    for file in os.listdir():
        for track in track_info:
            if track[1] in file:
                os.rename(file, track[0]+" - "+track[1]+".mp3")


code = input("Command: ")
if code == "down_pl_spot":
    download_playlist_spotify(url)
elif code == "down_folder":
    download_folder(url, digits)
elif code == "down_fav_spot":
    download_favourites_spotify()
elif code == "del_out":
    delete_output()