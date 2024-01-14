## File: you_missed_a_spot.py
## Author: Grant Goode

###########
## Imports ##
###########
import random
import time
from dotenv import load_dotenv
from time import sleep
import spotipy
from spotipy.oauth2 import SpotifyOAuth

##################
## Helper Functions ##
##################
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

# If there are more saved songs, get next page
def get_more_saved_songs(saved_songs):
    if saved_songs['next']:
        try:
            saved_songs = spotify.next(saved_songs)
        except:
            handle_api_error('SAVED_SONGS_ERROR')
    else:
        saved_songs = None
    
    return saved_songs

def get_more_saved_albums(saved_albums):
    if saved_albums['next']:
        try:
            saved_albums = spotify.next(saved_albums)
        except:
            handle_api_error('SAVED_SONGS_ERROR')
    else:
        saved_albums = None
    
    return saved_albums

################
## Main Functions ##
################
# Check playlists for any unsaved songs
def check_playlists_for_unsaved(user, playlists):

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

# Check for any saved songs that are not in any playlists
def check_saved_not_in_playlists(user, playlists):

    # Retrieve saved songs and save track IDs to a list
    print('Retrieving ALL saved songs...')
    print('This may take a while.')
    saved_songs = spotify.current_user_saved_tracks(limit=50)
    saved_tracks = []
    while(saved_songs):
        for item in saved_songs['items']:
            saved_tracks.append(item['track'])

        # Slow down repeated API calls
        sleep(0.05)
        saved_songs = get_more_saved_songs(saved_songs)
        print('.')
     
    # Iterate through playlists
    print('Checking saved songs against playlists...')
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
                    for current_track_id in current_track_ids:
                        for saved_track in saved_tracks:
                            if current_track_id == saved_track['id']:
                                saved_tracks.remove(saved_track)

                    # Slow down repeated API calls
                    sleep(0.1)
                    
                    # If there are more tracks in the current playlist, get next page
                    current_playlist_tracks = get_more_tracks(current_playlist_tracks)
                    
                    print(' .')

                print()

        # If there are more playlists, get next page
        playlists = get_more_playlists(playlists)

    # Put saved songs not found in any playlists into a text file
    with open('results.txt', 'a', encoding='utf-8') as file:
        for saved_track in saved_tracks:
            formatted_name = str(saved_track['name'] + ' — ' + saved_track['artists'][0]['name'])
            file.write(formatted_name)
            file.write('\n')
        file.close()
    print('Results saved to results.txt')

# Select a random album from the user's saved albums
def random_saved_album():
    #   Seed random number generator
    random.seed(time.time())

    # Save albums to a list
    saved_albums = spotify.current_user_saved_albums(limit=50)
    saved_albums_list = []
    while saved_albums:
        for item in saved_albums['items']:
            saved_albums_list.append(item['album'])

        # Slow down repeated API calls
        sleep(0.05)
        saved_albums = get_more_saved_albums(saved_albums)
        print('.')
    
    # Pick and print random album
    random_album_idx = random.randint(0, len(saved_albums_list) - 1)
    print('Your random album is: ')
    print(saved_albums_list[random_album_idx]['name'], '—', saved_albums_list[random_album_idx]['artists'][0]['name'])
    print()

##################
## Start of Program  ##
##################

# Grab environment variables for Spotify API
load_dotenv()

# Use environment variables to get API authorization
scope = 'user-library-read,user-read-private,playlist-read-private'
try:
    spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
except:
    handle_api_error('AUTHENTICATION_ERR')

# Retrieve user
try:
    user = spotify.current_user()
except:
    handle_api_error('USER_RETRIEVE_ERROR')

# Retrieve user's playlists
try:
    playlists = spotify.current_user_playlists(limit=50)
except:
    handle_api_error('PLAYLIST_RETRIEVE_ERROR')

# Pick which function to perform
choice = 0
while True:
    print('--- Main Menu ---')
    print('1. Find all unsaved songs in playlists')
    print('2. Find all saved songs not in any playlists')
    print('3. Return a random saved album')
    print('Or press ENTER to exit')

    choice = input()
    match choice:
        case '1':
            print('\r\nChecking playlists for unsaved songs...')
            check_playlists_for_unsaved(user, playlists)
        case '2':
            print('\r\nChecking for saved songs not in any playlists...')
            check_saved_not_in_playlists(user, playlists)
        case '3':
            print('\r\nChecking saved albums...')
            random_saved_album()
        case '':
            exit()
        case _:
            print('\r\nPick a valid option or press ENTER to exit.')
