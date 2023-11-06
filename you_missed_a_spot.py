## File: you_missed_a_spot.py
## Author: Grant Goode
#
## Description: Currently finds and prints all songs in the user's playlists which are not in their Saved Songs.
## TODO: Add comparison of liked songs to playlists to find liked songs not in any playlists


## Imports
from dotenv import load_dotenv
from time import sleep

import spotipy
from spotipy.oauth2 import SpotifyOAuth


## Functions
# Error handler for when calls to Spotify API fail
def handle_api_error(error):
    match error:
        case 'AUTHENTICATION_ERROR':
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
            print('Unknown error.')

    input('Press ENTER to exit.')
    exit()

# Retrieve tracks in current playlist
def retrieve_playlist_tracks(playlist):
    try:
        current_playlist_tracks = spotify.playlist_items(playlist_id=playlist['id'], limit=50)
    except:
        handle_api_error('PLAYLIST_ITEM_RETRIEVE_ERROR')
    else:
        return current_playlist_tracks

# Put track objects and IDs into lists to reduce API calls
def create_batches(current_playlist_tracks):
    current_tracks = []
    current_track_ids = []

    for item in current_playlist_tracks['items']:
        current_tracks.append(item['track'])
        current_track_ids.append(item['track']['id'])
    
    return current_tracks, current_track_ids

# Check if tracks are saved
def check_if_tracks_saved(current_track_ids):
    try:
        saved = spotify.current_user_saved_tracks_contains(tracks=current_track_ids)
    except:
        handle_api_error('SAVED_SONGS_ERROR')
    else:
        return saved

# If there are more tracks in the current playlist, get next page
def get_more_tracks(current_playlist_tracks):
    if(current_playlist_tracks['next']):
        try:
            current_playlist_tracks = spotify.next(current_playlist_tracks)
        except:
            handle_api_error('PLAYLIST_ITEM_RETRIEVE_ERROR')
    else:
        current_playlist_tracks = None

    return current_playlist_tracks

# If there are more playlists, get next page
def get_more_playlists(playlists):
    if playlists['next']:
        try:
            playlists = spotify.next(playlists)
        except:
            handle_api_error('PLAYLIST_RETRIEVE_ERROR')
    else:
        playlists = None

    return playlists


## Start of Program
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
    for playlist in playlists['items']:
        # Only check playlists which are owned by the user and not collaborative
        if playlist['owner']['id'] == user['id'] and not playlist['collaborative']:
            print(playlist['name'])

            # Retrieve tracks in current playlist
            current_playlist_tracks = retrieve_playlist_tracks(playlist)
            
            # Iterate through tracks in current playlist
            while current_playlist_tracks:
                # Put track objects and IDs into lists to reduce API calls
                current_tracks, current_track_ids = create_batches(current_playlist_tracks)
                
                # Check if tracks are saved
                saved = check_if_tracks_saved(current_track_ids)

                # Slow down repeated API calls
                sleep(0.1)

                # Print non-saved tracks
                for idx, value in enumerate(saved):
                    if not value:
                        print(' ', current_tracks[idx]['name'], '—', current_tracks[idx]['artists'][0]['name'])
                
                # If there are more tracks in the current playlist, get next page
                current_playlist_tracks = get_more_tracks(current_playlist_tracks)
                
                print(' .')

            print()

    # If there are more playlists, get next page
    playlists = get_more_playlists(playlists)

# Ask for an input so the window doesn't immediately close
input('Press ENTER to exit.')
