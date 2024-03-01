import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from googleapiclient.discovery import build
import re,os

from dotenv import load_dotenv

load_dotenv()

#creds
spotify_client_id  = os.getenv('SPOTIFY_CLIENT_ID')
spotify_client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

youtube_developer_key = os.getenv('YOUTUBE_DEVELOPER_TOKEN')

# clients
youtube = build("youtube", "v3", developerKey=youtube_developer_key)

# important variables
youtube_music_link = "https://music.youtube.com/watch?v={song_id}"
spotify_music_link = "https://open.spotify.com/track/{song_id}"

youtube_regex = "v=([a-zA-Z0-9\-]{11})" 
spotify_regex = "open.spotify.com/track/([a-zA-Z0-9]{22})"  

client_credentials_manager = SpotifyClientCredentials(client_id=spotify_client_id, client_secret=spotify_client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


def get_spotify_uri(spotify_track_link):
    track_uri = re.search(spotify_regex,spotify_track_link).group(1)
    return track_uri

def get_youtube_uri(youtube_track_link): 
    track_uri = re.search(youtube_regex,youtube_track_link).group(1)
    return track_uri

def spotify_to_youtube(spotify_link):
    spotify_uri = get_spotify_uri(spotify_link)
    song_name = sp.track(spotify_uri)['name']
    artist_name = sp.track(spotify_uri)['album']['artists'][0]['name']
    request = youtube.search().list(part="snippet", q=song_name+' '+artist_name)
    response = request.execute()
    youtube_music_id = response["items"][0]["id"]["videoId"]
    return youtube_music_link.format(song_id=youtube_music_id)

def youtube_to_spotify(youtube_link):
    youtube_video_id = re.search(youtube_regex,youtube_link).group(1)
    request = youtube.videos().list(part="snippet,contentDetails",id=youtube_video_id)
    response = request.execute()
    channel = response["items"][0]['snippet']['channelTitle']
    song_name = response["items"][0]['snippet']['title']
    query = song_name + ' ' + channel
    spotify_uri = sp.search(type="track",q=query)['tracks']['items'][0]['id']
    spotify_song_link = spotify_music_link.format(song_id=spotify_uri)
    return spotify_song_link

def enter_music_link(song_link):
    if "youtube" in song_link:
        return {
            "youtube_music" : song_link,
            "spotify" : youtube_to_spotify(song_link)
        }
    
    else:
        return {
            "youtube_music" : spotify_to_youtube(song_link),
            "spotify" : song_link
        }

from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def html_string(object):
    output = "<html>{}</html>"
    s = ""
    for key in object.keys():
        s+= "<p>"
        s+= "<a href =" + object[key] + "> <h1>"+ key+ "</h1> </a>"
    return output.format(s)

@app.route('/submit', methods=['POST'])
def result():
    link = request.form['song_url']
    return html_string(enter_music_link(link)), 201

@app.route('/musicTranslator', methods=['GET'])
def music():
    link = request.args['song_url']
    return html_string(enter_music_link(link)), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)