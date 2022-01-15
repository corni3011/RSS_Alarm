import feedparser
import time
import datetime
import re
import logging
import requests
from Database import Data
from Update import get_update, send_message, send_message_to_chats

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


api_key = ""
refresh = 15 # refresh interval in minutes

def get_config():
    with open("config.txt", "r") as conf:
        news_links = []
        for line in conf:
            config = line.split(" ")
            link = config[config.index("Link:") + 1]
            tags = re.split('[()]', line)[1].split(", ")
            keywords = re.split('[()]', line)[3].split(", ")
            news_links.append((link, tags, keywords))
        return news_links
    

def determine_send(link, entry):
    keyword_matches = []
    tag_matches = []
    
    #if link[2][0] == '' and link[1][0] == '':
    #    return True
    return False
    if hasattr(entry, 'tags') and link[1][0] != '':
        tag_matches = [i for i in link[1] if i in [x.term for x in entry.tags]]
    if link[2][0] != '':
        keyword_matches = [i for i in link[2] if i in str(entry.title)]

    if len(keyword_matches) > 0 and link[1][0] == '':
        return True

    if len(tag_matches) > 0 and link[2][0] == '':
        return True

    if link[1][0] != '' and len(tag_matches) > 0 and link[2][0] != '' and len(keyword_matches) > 0:
        return True

    return False

def process_news(news_links, data):
    for link in news_links:
        news_content = data.get_RSS_News(link[0], link[1])
        NewsFeed = feedparser.parse(link[0])
        for entry in NewsFeed.entries:
            if str(entry.title).replace("'", "") not in news_content:
                id = data.add_RSS_News(link[0], str(entry.title).replace("'", ""), str(entry.summary), time.time(), -1)
                if determine_send(link, entry):
                    print(entry.title)
                    send_message_to_chats(entry.title + "\n\n" + entry.summary + "\n\n" + str(entry.link), data.get_chats(), api_key, id, "RSS")

if __name__=="__main__":
    data = Data()
    while True:
        news_links = []
        try:
            news_links = get_config()
        except Exception as e:
            print(e)
        now = datetime.datetime.now()
        if now.hour > 7 and now.hour < 22:
            get_update(data, api_key)
            process_news(news_links, data)
            print("Checked", now)
        time.sleep(refresh * 60)
