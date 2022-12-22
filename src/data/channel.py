import os
import googleapiclient.discovery
from requests import Session
import csv
import json
from time import sleep
from random import randint


def make_api_client(key):
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=key)
    return client


class ChannelDictBuilder(object):
    def __init__(self, client, channel_id):
        self.client = client
        self.channel_id = channel_id
        self.channel = self.request_channel_basics()
        self.recentuploads = self.request_channel_uploads()

    def request_channel_basics(self):
        request = self.client.channels().list(
            part="snippet,contentDetails,statistics",
            id=self.channel_id)
        response = request.execute()
        return response

    def request_channel_uploads(self):
        uploads_id = self.channel['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        request = self.client.playlistItems().list(
            playlistId=uploads_id,
            part="snippet,contentDetails",
            maxResults=20)
        response = request.execute()
        return response

    def make_channel_dict(self, label=None):
        channel_details = self.channel['items'][0]
        channel_with_comments = {
            'id': channel_details['id'],
            'details': channel_details['snippet'],
            # each video in 'videos' comes with comments
            'videos': self.make_playlist_dict(),
            'label': label
        }
        return channel_with_comments

    def make_playlist_dict(self):
        playlist = self.recentuploads['items']
        playlist_dict = {}
        for vid in playlist:
            vid_id = vid['contentDetails']['videoId']
            playlist_dict[vid_id] = self.make_video_dict(vid)
            playlist_dict[vid_id]['comments'] = self.make_comments_dict(vid_id)
        return playlist_dict

    def make_video_dict(self, video):
        video_dict = {
            'title': video['snippet']['title'],
            'description': video['snippet']['description'],
            'date': video['snippet']['publishedAt'][:10]
            }
        return video_dict

    def make_comments_dict(self, video_id):
        comments_response = self.request_video_comments(video_id)
        # Shorten the chain of keys
        def short(item): return item['snippet']['topLevelComment']['snippet']
        comments_dict = {}
        for comment in comments_response['items']:
            comment['id'] = {'date': short(comment)['publishedAt'],
                             'text': short(comment)['textOriginal']}
        return comments_dict

    def request_video_comments(self, video_id):
        request = self.client.commentThreads().list(
            part="snippet",  # for only top-level comments
            maxResults=50,
            videoId=video_id,
            order='relevance')
        response = request.execute()
        return response


class UrlIdFinder():
    '''
    A web scraper that takes YouTube channel URLs and returns
    the channel's unique ID. Reads from and updates a cache file
    that should be provided to reduce numbers of requests made
    Recommended usage:
        with UrlIdFinder(path, cookie) as idfinder:
            idfinder.url_to_id({url})
    '''
    def __init__(self, cache_path, cookie_path):
        self.session = Session()
        self.cache_path = cache_path
        self.cache = self.load_cache(cache_path)
        self.cookie = self.read_cookie(cookie_path)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.session.close()
        self.write_out_cache(self.cache_path)

    def load_cache(self, fp):
        # Cache file should be a csv with URL, ID rows
        # Returns a dict of URL-ID pairs
        with open(fp, 'r', encoding='utf8') as cache_file:
            cache = dict(csv.reader(cache_file))
            return cache

    def read_cookie(self, cookie_path):
        with open(cookie_path, 'r', encoding='utf8') as cookief:
            return json.load(cookief)

    def url_to_id(self, channel_url):
        '''
        example
        In: 'https://youtube.com/@JordanBPeterson'
        Out: 'UCL_f53ZEJxp8TtlOkHwMV9Q'
        Return a channel's ID from its url. Uses cached IDs if
        possible, else requests the channel page and looks for it
        there.
        '''
        id_from_cache = self.check_id_cached(channel_url)
        if id_from_cache:
            channel_id = id_from_cache
            print("Found ID in cache.")
        else:
            print("Trying to get ID from web.")
            channel_id = self.get_id_from_web(channel_url)
            sleep(randint(2, 5))
        # if an id was found, add it to the cache
        if channel_id:
            self.cache[channel_url] = channel_id
        return channel_id

    def get_id_from_web(self, channel_url):
        channel_response = self.session.get(channel_url, cookies=self.cookie)
        page_source = str(channel_response.content)
        id_from_web = self.find_id_in_page(page_source)
        if not id_from_web:
            return None
        else:
            return id_from_web

    def check_id_cached(self, url):
        if url in self.cache:
            return self.cache[url]
        else:
            return None

    def write_out_cache(self, fp):
        with open(fp, 'w', encoding='utf8') as cache_file:
            rows = [(url, Id) for url, Id in self.cache.items()]
            writer = csv.writer(cache_file)
            writer.writerows(rows)

    def find_id_in_page(self, page):
        id_start = page.find('externalId') + 13  # the id starts 13 chars later
        id_end = page.find('",', id_start)
        return page[id_start:id_end]


def main(channel_id, key):
    #handle = channelurl.partition('@')[2]
    #channel_id = handle_to_id(handle)
    yt_client = make_api_client(key)
    comments_getter = ChannelDictBuilder(yt_client, channel_id)
    channel_and_comments = comments_getter.make_channel_dict()
    return channel_and_comments
