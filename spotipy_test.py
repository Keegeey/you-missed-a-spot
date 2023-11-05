# File: spotipy_test.py
# Author: Grant Goode
#
# Experimenting with spotipy library
# TODO: Add comparison of liked songs to playlists to find liked songs not in any playlists

# Imports
from datetime import datetime

from dotenv import load_dotenv

import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Retrieval is quicker if done in batches, 50 seems to be the max without getting blocked
BATCH_SIZE = 50

# Grab start time to calculate total execution time
begin_time = datetime.now()

# Grab environment variables for Spotify API
load_dotenv()

# Use environment variables to get API authorization
scope = 'user-library-read,user-read-private,playlist-read-private'
spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

# Save user id
user = spotify.current_user()

#Retrieve playlists
playlists = spotify.current_user_playlists()
while playlists:
    for i, playlist in enumerate(playlists['items']):
        # Only check playlists which are owned by the user
        if playlist['owner']['id'] == user['id']:
            print(playlist['name'])
            # Go through all tracks in current playlist
            current_playlist_tracks = spotify.playlist_items(playlist['id'])
            while current_playlist_tracks:
                for j, item in enumerate(current_playlist_tracks['items']):
                    # If track is saved
                    current_track_id = item['track']['id']
                    saved = spotify.current_user_saved_tracks_contains(tracks=[current_track_id])
                    if not saved[0]:
                        print(' ', item['track']['name'])
                if(current_playlist_tracks['next']):
                    current_playlist_tracks = spotify.next(current_playlist_tracks)
                else:
                    current_playlist_tracks = None
            print() # \n
    if playlists['next']:
        playlists = spotify.next(playlists)
    else:
        playlists = None

# Calculate and display total execution time
end_time = datetime.now()
execution_minutes = end_time.minute - begin_time.minute
exeuction_seconds = end_time.second - begin_time.second
print('This took', execution_minutes, 'minutes and', exeuction_seconds, 'seconds.')

# Ask for an input so the window doesn't immediately close
input('Press ENTER to exit.')