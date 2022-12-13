from requests import Session
import json
import csv
from bs4 import BeautifulSoup


USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
with open('cookie.json', 'r', encoding='utf8') as f:
    cookie = json.load(f)


class UrlIdFinder():
    def __init__(self, session, cache_path, cookie):
        self.session = Session()
        self.cache_path = cache_path
        self.cache = self.load_cache(cache_path)
        self.cookie = cookie

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.session.close()
        self.write_out_cache()

    def load_cache(self, fp):
        # Cache file should be a csv with URL, ID rows
        # Returns a dict of URL-ID pairs
        with open(fp, 'r', encoding='utf8') as cache_file:
            cache = dict(csv.reader(cache_file))
            return cache

    def url_to_id(self, channel_url):
        '''
        Return a channel's ID from its url. Uses cached IDs if
        possible, else downloads the channel page and looks for it
        there.
        '''

        id_from_cache = self.check_id_cached(channel_url)
        if id_from_cache:
            channel_id = id_from_cache
        else:
            channel_id = self.get_id_from_web(channel_url)
        # if an id was found, add it to the cache
        if channel_id:
            self.cache[channel_url] = channel_id
        return channel_id

    def get_id_from_web(self, channel_url):
        channel_response = self.session.get(channel_url, cookies=self.cookie)
        page_source = channel_response.content
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
            writer = csv.writer(cache_file)
            writer.writerows(self.cache)

    def find_id_in_page(self, page):
        id_start = page.find('externalId') + 13  # the id starts 13 chars later
        id_end = page.find('",', id_start)
        return page[id_start:id_end]
        


