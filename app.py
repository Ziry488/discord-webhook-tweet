import feedparser
import asyncio
import requests
import os

DATA_FOLDER = "data"
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

WEBHOOK_URL = "WEBHOOK_URL"

#edit ACCOUNT_NAME to Twitter username
LAST_ENTRY_IDS = {
    "https://nitter.poast.org/ACCOUNT_NAME/rss": None,
}

def load_last_id(feed_url):
    safe_filename = feed_url.replace("/", "_").replace("?", "_")
    file_path = os.path.join(DATA_FOLDER, f"{safe_filename}_last_id.txt")
    try:
        with open(file_path, "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        return None

def save_last_id(feed_url, last_id):
    safe_filename = feed_url.replace("/", "_").replace("?", "_")
    file_path = os.path.join(DATA_FOLDER, f"{safe_filename}_last_id.txt")
    with open(file_path, "w") as file:
        file.write(last_id)

async def send_rss_news(feed_url):
    while True:
        feed = feedparser.parse(feed_url)
        if len(feed.entries) > 0:
            latest_entry = feed.entries[0]
            last_id = load_last_id(feed_url)
            if latest_entry.id != last_id:
                news_link = latest_entry.link
                message = f"{news_link}"

                payload = {"content": message}

                response = requests.post(WEBHOOK_URL, json=payload)
                if response.status_code == 204:
                    print("++++++++++++++++")

                save_last_id(feed_url, latest_entry.id)

        await asyncio.sleep(3)

async def start_webhook_rss():
    tasks = [send_rss_news(feed_url) for feed_url in LAST_ENTRY_IDS.keys()]
    await asyncio.gather(*tasks)

loop = asyncio.get_event_loop()
loop.run_until_complete(start_webhook_rss())
