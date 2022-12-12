import os
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


def main(channelurl, key):
    #handle = channelurl.partition('@')[2]
    #channel_id = handle_to_id(handle)
    yt_client = make_api_client(key)
    comments_getter = ChannelDictBuilder(yt_client, channel_id)
    channel_and_comments = comments_getter.make_channel_dict()
    return channel_and_comments
