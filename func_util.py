import streamlit as st
import spotipy
import spotipy.util as util

class Func:
    def __init__(self, user_id):
            self.user_id = user_id
            self.client_id = st.secrets['CLIENT_ID']
            self.client_secret = st.secrets['CLIENT_SECRET']
            self.redirect_uri = st.secrets['REDIRECT_URI']
            self.scope = 'user-read-recently-played user-top-read user-read-playback-position user-read-playback-state user-modify-playback-state user-read-currently-playing app-remote-control streaming playlist-modify-public playlist-modify-private playlist-read-private playlist-read-collaborative user-follow-modify user-follow-read user-library-modify user-library-read user-read-private'
            token = util.prompt_for_user_token(self.user_id, self.scope, self.client_id, self.client_secret, self.redirect_uri)
            self.spotify = spotipy.Spotify(auth=token)

    def spotify_auth(self):
        return self.spotify

    def user_playlists(self):
        user_playlist_dict = {}
        user = self.user_id
        json_playlists = self.spotify.user_playlists(user=user)
        for playlist in json_playlists['items']:
            if playlist['owner']['id'] == self.user_id:
                user_playlist_dict[playlist['name']] = playlist['id']
        return user_playlist_dict

    @st.cache(allow_output_mutation=True, show_spinner=False)
    def artist_top_tracks(self, artist_id):
        track_dict = {}
        json_tracks = self.spotify.artist_top_tracks(artist_id)
        for track in json_tracks['tracks']:
            track_dict[track['name']] = {'uri':track['uri'], 'preview':track['preview_url']}
        return track_dict

    @st.cache(allow_output_mutation=True, show_spinner=False)
    def artist_search(self, artist_name):
        return self.spotify.search(q='artist:' + artist_name, type='artist', limit=5)

    @st.cache(allow_output_mutation=True, show_spinner=False)
    def artist_related_artists(self, artist_id):
        return self.spotify.artist_related_artists(artist_id)

    
