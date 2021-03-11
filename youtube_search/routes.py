import requests
from isodate import parse_duration
import time
import json
import os
from googleapiclient.discovery import build
from flask import Flask, render_template, current_app, request, redirect, url_for

app = Flask(__name__)
ts = time.gmtime()

@app.route('/', methods=['GET', 'POST'])
def index():
    search_url = 'https://www.googleapis.com/youtube/v3/search'
    video_url = 'https://www.googleapis.com/youtube/v3/videos'

    video_ids = []

    if request.method == 'POST':
        search_params = {
            'key': current_app.config['YOUTUBE_API_KEY'],
            'q': request.form.get('query'),
            'part': 'snippet',
            'maxResults': 9,
            'type': 'video',
            'videoEmbeddable': 'true'
        }
        r_s = requests.get(search_url, params=search_params)
        results = r_s.json()['items']

        for result in results:
            video_ids.append(result['id']['videoId'])

        if request.form.get('submit') == 'lucky':
            return redirect(f'https://www.youtube.com/watch?v={video_ids[0]}')

        video_params = {
            'key': current_app.config['YOUTUBE_API_KEY'],
            'id': ','.join(video_ids),
            'part': 'snippet, contentDetails',
            'maxResults': 9,
        }
        r_v = requests.get(video_url, params=video_params)
        results_v = r_v.json()['items']

        for result in results_v:
            video_data = {
                'id': result['id'],
                'url': f'https://www.youtube.com/watch?v={ result["id"]}',
                'thumbnail': result['snippet']['thumbnails']['high']['url'],
                'duration': int(parse_duration(result['contentDetails']['duration']).total_seconds() // 60),
                'title': result['snippet']['title']
            }
            video_ids.append(video_data)
    return render_template('index.html', videos=video_ids)


@app.route('/channels/<channel>', methods=['GET', 'POST'])
def channelss(channel):
    channels_url = 'https://www.googleapis.com/youtube/v3/channels'
    query = channel
    channels_ids = []

    channel_params = {
            'key': os.environ.get('YOUTUBE_API_KEY'),
            'id': query,
            'part': 'statistics, contentDetails, id, status, snippet'
        }
    ch_s = requests.get(channels_url, params=channel_params)
    results_ch = ch_s.json()['items']

    for result in results_ch:
        channel_data = {
            'id': result['id'],
            'url': f'https://www.youtube.com/channel/{result["id"]}',
            'thumbnail': result['snippet']['thumbnails']['high']['url'],
            'title': result['snippet']['title'],
            'channel_description': result['snippet']['description'],
            # 'channel_country': result['snippet']['country'],
            'channel_creation_day': str(result['snippet']['publishedAt']).split('T')[0],
            'channel_likes': result['contentDetails']['relatedPlaylists']['likes'],
            'channel_profile': result['snippet']['thumbnails']['high']['url'],  # can be 'medium', 'high'
            'channel_views': result['statistics']['viewCount'],
            'channel_subscribers': result['statistics']['subscriberCount'],
            'channel_videos': result['statistics']['videoCount'],
            'channel_status': result['status']['privacyStatus'],
        }
        channels_ids.append(channel_data)

        return render_template('channels.html', channels=channels_ids)
    return redirect(url_for('channelss_search'))


@app.route('/channels', methods=['GET', 'POST'])
def channelss_search():

    if request.method == 'POST':
        search_params = {
            'key': os.environ.get('YOUTUBE_API_KEY'),
            'q': request.form.get('query'),
            'part': 'snippet',
        }
        query = search_params['q'].split('/')[-1]
        return redirect(url_for('channelss', channel=query))
    return render_template('channels.html')

##############################################################



@app.route('/playlists/<playlist>', methods=['GET', 'POST'])
def playlists(playlist):
    playlists_url = 'https://www.googleapis.com/youtube/v3/playlists'
    query = playlist
    playlists_ids = []
#https://www.youtube.com/watch?v=xC-c7E5PK0Y&list=PL0BAwa0pBqg6dr_DfCL3DmeSLtFoAq7UR
    playlist_params = {
            'key': os.environ.get('YOUTUBE_API_KEY'),
            'id': query,
            'part': 'contentDetails, status, snippet'
        }
    pl_s = requests.get(playlists_url, params=playlist_params)
    results_pl = pl_s.json()['items']

    for result in results_pl:
        playlist_data = {
            'title': result['snippet']['title'],
            'playlist_description': result['snippet']['description'],
            # 'channel_country': result['snippet']['country'],
            'playlist_creation_day': str(result['snippet']['publishedAt']).split('T')[0],
            # 'channel_likes': result['contentDetails']['relatedPlaylists']['likes'],
            # 'channel_profile': result['snippet']['thumbnails']['high']['url'],  # can be 'medium', 'high'
            'playlist_status': result['status']['privacyStatus'],
            'playlist_videos': result['contentDetails']['itemCount']
        }

        playlists_ids.append(playlist_data)
    # playlists_ids.append(results_pl)

        return render_template('playlists.html', playlists=playlists_ids)
    return redirect(url_for('playlists_search'))


@app.route('/playlists', methods=['GET', 'POST'])
def playlists_search():

    if request.method == 'POST':
        search_params = {
            'key': os.environ.get('YOUTUBE_API_KEY'),
            'q': request.form.get('query'),
            'part': 'snippet',
        }
        query = search_params['q'].split('=')[-1]
        return redirect(url_for('playlists', playlist=query))
    return render_template('playlists.html')

