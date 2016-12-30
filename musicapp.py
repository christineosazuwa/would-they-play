
# coding: utf-8

#Basic Libraries
#get_ipython().magic(u'matplotlib inline')

import requests
import sys
import os
from itertools import islice
import re
from bs4 import BeautifulSoup
import json
import pandas as pd
from time import sleep
import string
from collections import Counter

#Music APIs
import spotipy
import spotipy.util as util
import pylast
import discogs_client
import musicbrainzngs as mb
# import pygn

# Stats Libraries
from sklearn import linear_model as lm
from sklearn import feature_selection as f_select
from sklearn import cross_validation as cv
from sklearn import metrics
from sklearn.linear_model import LinearRegression
from sklearn.cross_validation import cross_val_score
from sklearn.tree import export_graphviz
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
import numpy as np
import statsmodels.formula.api as smf


### GET DATA ###

all_data = pd.read_csv('artist_data.csv').drop(['Unnamed: 0'], axis=1)


### STATSMODELS ###

# create a fitted model
sm_lm = smf.ols(formula='played_warped ~ gracenote_era + member_count + spotify_popularity + spotify_track_popularity + acousticness + danceability + duration_ms + energy + instrumentalness + key + liveness + loudness + mode + speechiness + tempo + time_signature + valence + lastfm_play_count + lastfm_listener_count', data=all_data).fit()


### Spotify Settings ###

import requests

client_id = 'SPOTIFY CLIENT ID'
client_secret = 'SPOTIFY SECRET KEY'

grant_type = 'client_credentials'

#Request based on Client Credentials Flow from https://developer.spotify.com/web-api/authorization-guide/

#Request body parameter: grant_type Value: Required. Set it to client_credentials
body_params = {'grant_type' : grant_type}

url='https://accounts.spotify.com/api/token'

response=requests.post(url, data=body_params, auth = (client_id, client_secret)) 

token = response.text[17:103]

sp = spotipy.Spotify(auth=token)


### Last.FM Settings ###

LASTFM_API_KEY = "LAST FM API KEY"
LASTFM_API_SECRET = "LAST FM SECRET KEY"
lastfm_username = 'LAST FM USERNAME'
lastfm_password_hash = pylast.md5("LAST FM PASSWORD")
lastfm = pylast.LastFMNetwork(api_key=LASTFM_API_KEY, api_secret=LASTFM_API_SECRET, username=lastfm_username, password_hash=lastfm_password_hash)



### Music Brainz Settings ###
mb.set_useragent("MUSICBRAINZ TITLE", "0.1", "MUSICBRAIN URL")



### Gracenote Settings ###
clientID = 'GRACENOTE CLIENT ID'
userID = 'GRACENOTE USER ID'




# define X and y
feature_cols = list(all_data.describe().columns)[:-1]
X = all_data[feature_cols]
y = all_data.played_warped




# get spotify id & musicbrainz id
def get_ids(band1):
        sp_artist_search = sp.search(q=band1, limit=1, type='artist')
        if 'Error' not in sp_artist_search: 
            try:
                yield sp_artist_search['artists']['items'][0]['id']
            except:
                yield '0'
        musicbrain_artist_search = mb.search_artists(query=band1, limit=1)
        if 'Error' not in musicbrain_artist_search: 
            try:
                yield musicbrain_artist_search['artist-list'][0]['id']
            except:
                yield '0'

# get gracenote era
def gn_era(band1):
    try:
        gracenote_artist_search = pygn.search(clientID=clientID, userID=userID, artist=band1)
        return gracenote_artist_search['artist_era']['1']['TEXT']
    except:
        return ('0')
    
# get number of members from musicbrainz
def mb_members(gn_id):
    try:
        musicbrain_id_search = mb.get_artist_by_id(gn_id, includes=['artist-rels'])
        for item in musicbrain_id_search['artist']['artist-relation-list']:
                yield item['artist']['name']
    except:
        yield('0')

#get spotify artist popularity & genre
def sp_popularity_genre(sp_id):
    try:
        spotify_id_search = sp.artist(sp_id)
        return spotify_id_search['popularity'], spotify_id_search['genres'][0]
    except:
        return ('0','0')

#get lastfm popularity:
def lastfm_counts(gn_id):
    try:
        lastfm_artist_id_search = lastfm.get_artist_by_mbid(gn_id)
        return lastfm_artist_id_search.get_playcount(), lastfm_artist_id_search.get_listener_count()
    except:
        return('0', '0')

# get spotify artist top track ids
def spotify_top_tracks(sp_id):
    try:
        spotify_top_tracks_search = sp.artist_top_tracks(sp_id, country='US')['tracks']
        if 'Error' not in spotify_top_tracks_search:
            for tracks in spotify_top_tracks_search:
                yield tracks['id']
    except:
        yield '0'

# get spotify artist top track popularity
def spotify_top_tracks_popularity(sp_id):
    try:
        spotify_top_tracks_search = sp.artist_top_tracks(sp_id, country='US')['tracks']
        if 'Error' not in spotify_top_tracks_search:
            for tracks in spotify_top_tracks_search:
                yield tracks['popularity']
    except:
        yield '0'

# get spotify artist top track attributes
def spotify_top_tracks_attributes(tracks):
    acousticness = []
    danceability = []
    duration_ms = [] 
    energy = [] 
    instrumentalness = []
    key = []
    liveness = [] 
    loudness = []
    mode = []
    speechiness = [] 
    tempo = [] 
    time_signature = [] 
    valence = []
    spotify_tracks_search = sp.audio_features(tracks)
    try:
        if 'Error' not in spotify_tracks_search:
            for tracks in spotify_tracks_search:
                acousticness.append(tracks['acousticness'])
                danceability.append(tracks['danceability'])
                duration_ms.append(tracks['duration_ms'])
                energy.append(tracks['energy'])
                instrumentalness.append(tracks['instrumentalness'])
                key.append(tracks['key'])
                liveness.append(tracks['liveness'])
                loudness.append(tracks['loudness'])
                mode.append(tracks['mode'])
                speechiness.append(tracks['speechiness'])
                tempo.append(tracks['tempo'])
                time_signature.append(tracks['time_signature'])
                valence.append(tracks['valence'])
            yield sum(acousticness)/len(acousticness), sum(danceability)/len(danceability), sum(duration_ms)/len(duration_ms), sum(energy)/len(energy), sum(
                instrumentalness)/len(instrumentalness), sum(key)/len(key), sum(liveness)/len(liveness), sum(
                loudness)/len(loudness),sum(mode)/len(mode), sum(speechiness)/len(speechiness), sum(tempo)/len(tempo), sum(
                time_signature)/len(time_signature), sum(valence)/len(valence)
    except:
        yield zeros23[0:12]




def get_data2(band5):
    band5_name = band5
    band5_spotify_id = list(get_ids(band5))[0]
    band5_musicbrainz_id = list(get_ids(band5))[1]
    band5_era = int(gn_era(band5)[0:4])
    band5_member_count = len(set(mb_members(list(get_ids(band5))[1])))
    band5_popularity = sp_popularity_genre(list(get_ids(band5))[0])[0]
    band5_genre = sp_popularity_genre(list(get_ids(band5))[0])[1]
    band5_populary_tracks_avg = sum(list(spotify_top_tracks_popularity(list(get_ids(band5))[0])))/len(list(spotify_top_tracks_popularity(list(get_ids(band5))[0])))
    band5_acousticness = list(spotify_top_tracks_attributes(spotify_top_tracks(list(get_ids(band5))[0])))[0][0]
    band5_danceability = list(spotify_top_tracks_attributes(spotify_top_tracks(list(get_ids(band5))[0])))[0][1]
    band5_duration_ms = list(spotify_top_tracks_attributes(spotify_top_tracks(list(get_ids(band5))[0])))[0][2]
    band5_energy = list(spotify_top_tracks_attributes(spotify_top_tracks(list(get_ids(band5))[0])))[0][3] 
    band5_instrumentalness = list(spotify_top_tracks_attributes(spotify_top_tracks(list(get_ids(band5))[0])))[0][4]
    band5_key = list(spotify_top_tracks_attributes(spotify_top_tracks(list(get_ids(band5))[0])))[0][5]
    band5_liveness = list(spotify_top_tracks_attributes(spotify_top_tracks(list(get_ids(band5))[0])))[0][6]
    band5_loudness = list(spotify_top_tracks_attributes(spotify_top_tracks(list(get_ids(band5))[0])))[0][7]
    band5_mode = list(spotify_top_tracks_attributes(spotify_top_tracks(list(get_ids(band5))[0])))[0][8]
    band5_speechiness = list(spotify_top_tracks_attributes(spotify_top_tracks(list(get_ids(band5))[0])))[0][9]
    band5_tempo = list(spotify_top_tracks_attributes(spotify_top_tracks(list(get_ids(band5))[0])))[0][10]
    band5_time_signature = list(spotify_top_tracks_attributes(spotify_top_tracks(list(get_ids(band5))[0])))[0][11]
    band5_valence = list(spotify_top_tracks_attributes(spotify_top_tracks(list(get_ids(band5))[0])))[0][12]
    band5_lastfm_play_count = lastfm_counts(list(get_ids(band5))[1])[0]
    band5_lastfm_listener_count = lastfm_counts(list(get_ids(band5))[1])[1]
    band5_search = [band5_era, band5_member_count, band5_popularity,  band5_populary_tracks_avg, band5_acousticness, 
                    band5_danceability, band5_duration_ms, band5_energy, band5_instrumentalness, band5_key, 
                    band5_liveness, band5_loudness, band5_mode, band5_speechiness, band5_tempo, 
                    band5_time_signature, band5_valence, band5_lastfm_play_count, band5_lastfm_listener_count]
    band5_search_pd = pd.DataFrame(band5_search).transpose()
    band5_search_pd.columns = all_data.describe().columns[:-1]
    if round(sm_lm.predict(band5_search_pd),0) == 0:
        return band5 + ' is not likely to play Warped Tour.'
    else:
        return band5 + ' is likely to play Warped Tour!'