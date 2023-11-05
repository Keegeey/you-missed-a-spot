# File: spotipy_test.py
# Author: Grant Goode
#
# Currently, spotipy_test.py finds and prints all songs in the user's playlists which are not in their Saved Songs.
# TODO: Add comparison of liked songs to playlists to find liked songs not in any playlists

# Imports
from datetime import datetime
from dotenv import load_dotenv

import spotipy
from spotipy.oauth2 import SpotifyOAuth

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

# Retrieve user's playlists
try:
    playlists = spotify.current_user_playlists()
except:
    print('Couldn\'t get playlists.')
    input('Press ENTER to exit.')
    exit()
else:
    print('Successfully retrieved playlists.')
    print()

while playlists:
    # Iterate through playlists
    for i, playlist in enumerate(playlists['items']):
        # Only check playlists which are owned by the user
        if playlist['owner']['id'] == user['id']:
            print(playlist['name'])

           # Retrieve tracks in current playlist
            try:
                current_playlist_tracks = spotify.playlist_items(playlist_id=playlist['id'])
            except:
                print('Couldn\'t get playlist items.')
                input('Press ENTER to exit.')
                exit()
            
            # Iterate through tracks in current playlist
            while current_playlist_tracks:
                # Put track IDs into a list to reduce API calls
                current_tracks = []
                current_track_ids = []
                for j, item in enumerate(current_playlist_tracks['items']):
                    current_track_ids.append(item['track']['id'])
                
                # Check if tracks are saved
                try:
                    saved = spotify.current_user_saved_tracks_contains(tracks=current_track_ids)
                except:
                    print('Couldn\'t check saved songs.')
                    input('Press ENTER to exit.')
                    exit()
                
                # Print non-saved tracks
                for k in saved:
                    if not saved[k]:
                        print(' ', current_tracks['name'])
                
                # If there are more tracks in playlist, get next page
                if(current_playlist_tracks['next']):
                    try:
                        current_playlist_tracks = spotify.next(current_playlist_tracks)
                    except:
                        print('Couldn\'t get next set of playlist items.')
                        input('Press ENTER to exit.')
                        exit()
                else:
                    current_playlist_tracks = None

            print()

    # If there are more playlists, get next page
    if playlists['next']:
        try:
            playlists = spotify.next(playlists)
        except:
            print('Couldn\'t get next set of playlists.')
            input('Press ENTER to exit.')
            exit()
    else:
        playlists = None

# Calculate and display total execution time
end_time = datetime.now()
execution_minutes = end_time.minute - begin_time.minute
execution_seconds = end_time.second - begin_time.second
print('This took', execution_minutes, 'minutes and', execution_seconds, 'seconds.')

# Ask for an input so the window doesn't immediately close
input('Press ENTER to exit.')
