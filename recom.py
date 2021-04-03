import h5py #external
import pandas as pd #external
from glob import glob #external
import numpy as np #external
import spotipy #external
from spotipy.oauth2 import SpotifyOAuth
from collections import OrderedDict
from random import random, randint
import sys

print("Running python script...")

def get_dataset(files): #turns an array of HDF files into a one hot encoded song dataframe
    df = pd.DataFrame(np.asarray([h5py.File(file, "r").get("analysis/songs")[0] for file in files]))["track_id"]
    df = pd.DataFrame(df.str.decode("utf-8"))
    title_df = pd.DataFrame(np.asarray([h5py.File(file, "r").get("metadata/songs")[0] for file in files]))["title"]
    title_df = pd.DataFrame(title_df.str.decode("utf-8"))
    df = df.merge(title_df, on=df.index)
    df = df.iloc[:,1:]
    genres = []
    with open("genres.txt", "r") as f:
        lines = f.read().split("\n")
        for line in lines:
            split_line = line.split("\t")
            genres.append(split_line)
    genre_df = pd.DataFrame(genres)
    genre_df.columns = ["track_id", "genre"]
    df = df.merge(genre_df, on="track_id") #filters out the songs for which we can't find the genre
    one_hot = pd.get_dummies(df["genre"]) #one hot encodes the genres
    df = df.merge(one_hot, on=df.index)
    df = df.iloc[:,1:]
    df.columns = df.columns.str.lower()
    return df

def get_genre_scores(sp): #computes the number of songs for each genre on the user's library
    tracks = sp.current_user_saved_tracks()
    artists = [tracks["items"][i]["track"]["album"]["artists"][0]["external_urls"]["spotify"] for i in range(len(tracks["items"]))]
    genre_list = [sp.artist(artists[i])["genres"] for i in range(len(artists))]
    genres = set()
    for genre in genre_list:
        genres = genres.union(set(genre))
    genres = list(genres)
    genre_dict = dict()
    for genre in genres:
        genre_dict[genre] = sum(genre_list[i].count(genre) for i in range(len(genre_list)))
    return {k: v for k, v in sorted(genre_dict.items(), key=lambda item: item[1], reverse=True)} #orders it by decreasing occurences

def get_genre_probs(d, dataset_genres): #replaces occurences by probabilities
    keys = list(d.keys())
    for key in keys: #makes it impossible to get a song whose genre isn't in our dataset
        if key not in dataset_genres:
            d[key] = 0.0
    total = sum(d.values())
    for k, v in d.items():
        d[k] = v / total
    for genre in dataset_genres: #adds the dataset's genres that aren't present in the user's library
        if genre not in keys:
            d[genre] = 0.0
    return d

def get_songs_from_duration(sp, d, duration): #content-based recommandation system: returns a playlist based on genre probabilities
    song_uris = []
    total_duration = 0
    index = 0
    n_errors = 0
    while total_duration < duration: #we keep adding songs until we reach the given playlist duration
        index = randint(0, 200)
        r = random()
        total = 0
        current_genre = ""
        for k, v in d.items(): #computes a genre to choose based on the probability dictionary
            total += v
            if r <= total:
                current_genre = k
        try:
            response = sp.search("genre:" + current_genre, type="track", limit=1, offset=index) #searches for a song for this genre
            song_uris.append(response["tracks"]["items"][0]["uri"])
            total_duration += int(response["tracks"]["items"][0]["duration_ms"]) / 60000
        except:
            n_errors += 1
            print(f"Couldn't search for song {n_errors}, retrying with a different one")
    return song_uris
    
def main():
    print("Running Python script...")
    pkey = "3687892771ef476f8b497d740c6c2408" #default values
    skey = "99026e5bffae4711b3f209123ab1df56"
    playlistID = "https://open.spotify.com/playlist/0Mtvm4D0laomvp7pgfMTHa?si=73c75935991641c4"
    duration = 100
    try:
        pkey, skey, playlistID, duration = sys.argv[1:] #the python code should be run with the arguments in this order
        duration = int(duration)
    except:
        print("Error while reading arguments: using default values instead")
    files = glob("C:/Backups/MillionSongSubset/A/A/*/*.h5") #fetches a large sample of songs from our full dataset (fetching any more would take too much RAM)
    files.extend(glob("C:/Backups/MillionSongSubset/A/B/*/*.h5"))
    files.extend(glob("C:/Backups/MillionSongSubset/A/C/*/*.h5"))
    df = get_dataset(files)
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=pkey, client_secret=skey, redirect_uri="http://localhost:1234/", scope="user-library-read"))
    genre_scores = get_genre_scores(sp)
    genre_probs = get_genre_probs(genre_scores, list(df.columns)[3:])
    songs = get_songs_from_duration(sp, genre_probs, duration)
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=pkey, client_secret=skey, redirect_uri="http://localhost:1234/", scope="playlist-modify-private"))
    sp.user_playlist_add_tracks(pkey, playlistID, songs) #finally, the tracks are added to the playlist
    print("Finished!")

if __name__=="__main__":
    main()
