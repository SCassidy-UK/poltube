import requests
from bs4 import BeautifulSoup

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
COOKIE = "CONSENT=PENDING+546;"
with requests.Session() as session:
    session.headers['User-Agent'] = USER_AGENT
    channel_page = session.get("https://www.youtube.com/@thephilosophytube", cookies = {"SOCS":"CAISNQgDEitib3FfaWRlbnRpdHlmcm9udGVuZHVpc2VydmVyXzIwMjIxMjAyLjA0X3AxGgJlbiACGgYIgK-_nAY", "YSC":"4XTPjIZoG3A", "CONSENT":"PENDING+546", "GPS":"1", "VISITOR_INFO1_LIVE":"vm_Ir193dYw"})


page_parsed = BeautifulSoup(channel_page.content, 'html.parser')
with open('id_test.html', 'w', encoding= 'utf8') as f:
    f.write(page_parsed.prettify())
