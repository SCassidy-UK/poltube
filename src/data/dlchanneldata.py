import os
import json
import googleapiclient.discovery


def make_api_client(key):
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = key

    client = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=DEVELOPER_KEY)
    return client

class ChannelCommentsGetter(object):
    def __init__(self, client, channel_id):
        self.client = client
        self.channel_id = channel_id
        self.channel = self.dl_channel_basics()
        self.recentuploads = self.dl_channel_uploads()

    
    def dl_channel_basics(self):
        '''
        Get basic info for a channel (name, desc, subcount etc) for a given channel using
        api's channels().list method
        '''
        request = self.client.channels().list(
            part="snippet,contentDetails,statistics",
            id=self.channel_id
        )
        response = request.execute()
        return response


    def dl_channel_uploads(self):
        '''
        channel = response to a channel request a channel
        return - dictionary with 20 most recent videos
        '''
        uploads_id = self.channel['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        request = self.client.playlistItems().list(
            playlistId=uploads_id,
            part="snippet,contentDetails",
            maxResults=20
        )
        response = request.execute()
        return response


    def dl_video_comments(self, video_id):
        '''
        Get sample of comments from a video given a video id
        '''
        request = self.client.commentThreads().list(
            part="snippet",  # only top-level comments, could also have "replies"
            maxResults=50,
            videoId=video_id,
            order='relevance'
        )
        
        response = request.execute()
        return response


    def make_video_dict(self, video):
        '''
        Given an video item from a playlist, make a more trimmed down dict
        containing just the essentials - title, date, id, description,
        and of course, comments
        '''
        video_dict = {
            'title': video['snippet']['title'],
            'description': video['snippet']['description'],
            'date': video['snippet']['publishedAt'][:10],
        }
        return video_dict



    def make_comments_dict(self, video_id):
        comments_raw = self.dl_video_comments(video_id)
        def commentdata(item): return item['snippet']['topLevelComment']['snippet']
        comments_dict = {item['id']:
                         {'date': commentdata(item)['publishedAt'],
                         'text': commentdata(item)['textOriginal']}
                         for item in comments_raw['items']
                         }
        return comments_dict

    def make_playlist_dict(self):
        playlist = self.recentuploads['items']
        playlist_dict = {}
        for vid in playlist:
            vid_id = vid['contentDetails']['videoId']
            playlist_dict[vid_id] = self.make_video_dict(vid)
            playlist_dict[vid_id]['comments'] = self.make_comments_dict(vid_id)
        return playlist_dict


    def make_channel_dict(self, label=None):
        channel_details = self.channel['items'][0]
        channel_with_comments = {
            'id': channel_details['id'],
            'details': channel_details['snippet'],
            # note each video comes with comments
            'videos': self.make_playlist_dict(),
            'label': label
        }
        return channel_with_comments


def main(channelurl, key):
    handle = channelurl.partition('@')[2]
    channel_id = handle_to_id(handle)
    yt_client = make_api_client(key)
    comments_getter = ChannelCommentsGetter(yt_client, channel_id)
    channel_and_comments = commentsgetter.make_channel_dict()
    return channel_data
