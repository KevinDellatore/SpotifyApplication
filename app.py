from flask import Flask, redirect, request, session, url_for, render_template

import spotipy 
from spotipy.oauth2 import SpotifyOAuth 

import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')
app.config['SESSION_COOKIE_NAME'] = 'spotify-login-session'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'

SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')

@app.route('/')
def index():
    if 'token_info' in session:
        return redirect(url_for('top_tracks'))
    return render_template('index.html')
    

@app.route('/login')
def login():
    sp_oauth = SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET,redirect_uri=SPOTIPY_REDIRECT_URI, scope="user-top-read")
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


@app.route('/callback')
def callback():
    sp_oauth = SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET,redirect_uri=SPOTIPY_REDIRECT_URI, scope="user-top-read")
    session.clear()
    code=request.args.get('code')
    try:
        token_info = sp_oauth.get_access_token(code)
        session['token_info'] = token_info
        print("Token info:" , token_info)
    except Exception as e:
        print("error during token exchange", str(e))
        return redirect(url_for('index'))
    return redirect(url_for('index'))

@app.route('/top_tracks', methods=['GET' , 'POST'])
def top_tracks():
    if 'token_info' in session: 
        token_info = session.get('token_info')
        sp=spotipy.Spotify(auth=token_info.get('access_token'))
        range = 'medium_term'
        if request.method == 'POST':
            selected_option = request.form['selection']
            if selected_option == 'short_term':
                range = "short_term"
            elif selected_option == 'medium_term':
                range = 'medium_term'
            elif selected_option == 'long_term':
                range = 'long_term'

        top_tracks = sp.current_user_top_tracks(limit=9, offset=0, time_range=range)
        track_info = [
            {
                'art_Urls':track['album']['images'][0]['url'], 
                'track_name':track['name'], 
                'album_name':track['album']['name'],
                'artist_name':', '.join([artist['name'] for artist in track['artists']])
            }
            for track in top_tracks['items']
        ]
        #art_Urls = [track['album']['images'][0]['url'] for track in top_tracks['items']]
        return render_template('trackCollage.html', track_info = track_info)
    else:
        return redirect(url_for('index'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
