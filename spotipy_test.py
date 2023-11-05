# File: spotipy_test.py
# Author: Grant Goode
#
# Experimenting with spotipy library
# TODO: Add comparison of playlists to liked songs to find "unliked" songs in those playlists
# TODO: Add comparison of liked songs to playlists to find liked songs not in any playlists

# Imports
import sys
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
scope = 'user-library-read,user-read-private'
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

    if playlists['next']:
        playlists = spotify.next(playlists)
    else:
        playlists = None

print() # \n

# Calculate and display total execution time
end_time = datetime.now()
execution_length = end_time - begin_time
print('This took', execution_length, 'seconds')

# Ask for an input so the window doesn't immediately close
input('Press ENTER to exit.')