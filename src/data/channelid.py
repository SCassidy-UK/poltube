from requests import Session
import json
import csv
from bs4 import BeautifulSoup


USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
with open('cookie.json', 'r', encoding='utf8') as f:
    cookie = json.load(f)


with Session() as session:
    channel_page = session.get("https://www.youtube.com/@thephilosophytube",
                               cookies=cookie)

def load_cache(fp):
    # Cache file should be a csv with URL, ID rows
    # Returns a dict of URL-ID pairs
    with open(fp, 'r', encoding='utf8') as cache_file:
        cache = dict(csv.reader(cache_file))
        return cache


def url_to_id(channel_url, session, cache, cookie, failures):
    id_from_cache = check_id_cached(channel_url, cache)
    if id_from_cache:
        channel_id = id_from_cache
    else:
        get_id_from_web(channel_url, session, cookie, failures)
    return channel_id


def get_id_from_web(channel_url, session, cookie):
    channel_response = session.get(channel_url, cookie)
    id_from_web = find_id_in_page(channel_response)
    if not id_from_web:
        add_to_failures(channel_url, failures)
        return None
    else:
        return id_from_web

def check_id_cached(url, cache):
    try:
        return cache[url]
    except KeyError:
        return None


def check_channel_found(page):
    pass

def find_id_in_page(page):
    pass

def add_to_failures(url, error):
    pass

def add_to_cache(url, channel_id):
    pass


def main(channelurls):
    with requests.Session() as session:
        session.headers['User-Agent'] = USER_AGENT
        for url in channelurls:
            channel_id = url_to_id(url, session)

