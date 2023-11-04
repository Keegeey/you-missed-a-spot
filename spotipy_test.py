# File: spotipy_test.py
# Author: Grant Goode
#
# Experimenting with spotipy library
# TODO: Add comparison of playlists to liked songs to find "unliked" songs in those playlists
# TODO: Add comparison of liked songs to playlists to find liked songs not in any playlists

# Imports
import os
import sys
from datetime import datetime

from dotenv import load_dotenv

import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Determine how many saved songs to print out
if len(sys.argv) > 1:
    NUM_SONGS = ' '.join(sys.argv[1:])
    NUM_SONGS = int(NUM_SONGS)
else:
    while True:
        try:
            NUM_SONGS = int(input('How many songs?  '))
            break
        except:
            print('Please enter an integer')

# Grab start time to calculate total execution time
begin_time = datetime.now()

# Grab environment variables for Spotify API
load_dotenv()

# Use environment variables to get API authorization
scope = "user-library-read"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

# Retrieval is quicker if done in batches, 50 seems to be the max without getting blocked
NUM_BATCH = 50
MODULO = int(NUM_SONGS / NUM_BATCH)

# Column headers
print('#     |  Title                                                                             |  Artist')
print('------+------------------------------------------------------------------------------------+---------------')

# Retrieve and print songs
for x in range(MODULO+1):
    if NUM_SONGS - x * NUM_BATCH > NUM_BATCH:
        NUM_TO_GRAB = NUM_BATCH
    else:
        NUM_TO_GRAB = NUM_SONGS - x * NUM_BATCH
    
    if NUM_TO_GRAB == 0:
            break
    
    try:
        saved = sp.current_user_saved_tracks(NUM_TO_GRAB, x * NUM_BATCH)
    except:
        print() # \n
        print('Something went wrong retrieving your songs.')
        break

    for idx, item in enumerate(saved['items']):
        # Create spaces after song numbers to keep song titles aligned
        SONG_NUM = str(idx + x * NUM_BATCH + 1)
        for y in range(5 - len(SONG_NUM)):
            SONG_NUM += ' '
        track = item['track']

        # Create spaces after song titles to keep artist name aligned
        NAME_SPACES = ''
        for z in range(80 - len(str(track['name']))):
            NAME_SPACES += ' '

        print(SONG_NUM, "| ", track['name'] + NAME_SPACES, " | ", track['artists'][0]['name'])

print() # \n

# Calculate and display total execution time
end_time = datetime.now()
execution_length = end_time - begin_time
print('This took ', execution_length, ' seconds')

# Ask for an input so the window doesn't immediately close
input('Press ENTER to exit.')