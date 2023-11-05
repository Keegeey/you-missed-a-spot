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

# Error handler for when calls to Spotify API fail
def handle_api_error(error):
    match error:
        case 'AUTHENTICATION_ERR':
            print('Couldn\'t authenticate with Spotify.')
        case 'USER_RETRIEVE_ERROR':
            print('Couldn\'t get user profile.')
        case 'PLAYLIST_RETRIEVE_ERROR':
            print('Couldn\'t get playlists.')
        case 'PLAYLIST_ITEM_RETRIEVE_ERROR':
            print('Couldn\'t get playlist items.')
        case 'SAVED_SONGS_ERROR':
            print('Couldn\'t check saved songs.')
        case _:
            print('Unknown error')

    input('Press ENTER to exit.')
    exit()

# Grab start time to calculate total execution time
begin_time = datetime.now()

# Grab environment variables for Spotify API
load_dotenv()

# Use environment variables to get API authorization
scope = 'user-library-read,user-read-private,playlist-read-private'
try:
    spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
except:
    handle_api_error('AUTHENTICATION_ERR')

# Save user since we only check playlists which are owned by the user
try:
    user = spotify.current_user()
except:
    handle_api_error('USER_RETRIEVE_ERROR')

# Retrieve user's playlists
try:
    playlists = spotify.current_user_playlists()
except:
    handle_api_error('PLAYLIST_RETRIEVE_ERROR')

# Iterate through playlists
while playlists:
    for i, playlist in enumerate(playlists['items']):
        # Only check playlists which are owned by the user
        if playlist['owner']['id'] == user['id']:
            print(playlist['name'])

           # Retrieve tracks in current playlist
            try:
                current_playlist_tracks = spotify.playlist_items(playlist_id=playlist['id'], limit=50)
            except:
                handle_api_error('PLAYLIST_ITEM_RETRIEVE_ERROR')
            
            # Iterate through tracks in current playlist
            while current_playlist_tracks:
                # Put track IDs into a list to reduce API calls
                current_tracks = []
                current_track_ids = []
                for j, item in enumerate(current_playlist_tracks['items']):
                    current_tracks.append(item['track'])
                    current_track_ids.append(item['track']['id'])
                
                # Check if tracks are saved
                try:
                    saved = spotify.current_user_saved_tracks_contains(tracks=current_track_ids)
                except:
                    handle_api_error('SAVED_SONGS_ERROR')
                
                # Print non-saved tracks
                for k in saved:
                    if not saved[k]:
                        print(' ', current_tracks[k]['name'], '—', current_tracks[k]['artists'][0]['name'])
                
                # If there are more tracks in playlist, get next page
                if(current_playlist_tracks['next']):
                    try:
                        current_playlist_tracks = spotify.next(current_playlist_tracks)
                    except:
                        handle_api_error('PLAYLIST_ITEM_RETRIEVE_ERROR')
                else:
                    current_playlist_tracks = None

            print()

    # If there are more playlists, get next page
    if playlists['next']:
        try:
            playlists = spotify.next(playlists)
        except:
            handle_api_error('PLAYLIST_RETRIEVE_ERROR')
    else:
        playlists = None

# Calculate and display total execution time
end_time = datetime.now()
execution_minutes = end_time.minute - begin_time.minute
execution_seconds = end_time.second - begin_time.second
print('This took', execution_minutes, 'minutes and', execution_seconds, 'seconds.')

# Ask for an input so the window doesn't immediately close
input('Press ENTER to exit.')
