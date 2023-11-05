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
try:
    spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
except:
    print('Couldn\'t authenticate with Spotify.')
    input('Press ENTER to exit.')
    exit()
else:
    print('Authenticated with Spotify.')
    print()

# Save user since we only check playlists which are owned by the user
try:
    user = spotify.current_user()
except:
    print('Couldn\'t get user profile.')
    input('Press ENTER to exit.')
    exit()
else:
    print('Successfully retrieved user.')
    print()

#Retrieve playlists
try:
    playlists = spotify.current_user_playlists()
except:
    print('Couldn\'t get playlists')
    input('Press ENTER to exit.')
    exit()
else:
    print('Successfully retrieved playlists.')
    print()

print('Analyzing playlists...')
print()

while playlists:
    for i, playlist in enumerate(playlists['items']):
        # Only check playlists which are owned by the user
        if playlist['owner']['id'] == user['id']:
            print(playlist['name'])
            # Go through all tracks in current playlist
            current_playlist_tracks = spotify.playlist_items(playlist_id=playlist['id'], limit=BATCH_SIZE)
            while current_playlist_tracks:
                # Put every track ID into a list to reduce API calls
                current_track_ids = []
                for j, item in enumerate(current_playlist_tracks['items']):
                    current_track_ids.append(item['track']['id'])
                saved = spotify.current_user_saved_tracks_contains(tracks=current_track_ids)
                for k in saved:
                    if not saved[k]:
                        print(' ', item['track']['name'])
                if(current_playlist_tracks['next']):
                    current_playlist_tracks = spotify.next(current_playlist_tracks)
                else:
                    current_playlist_tracks = None
            print()
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