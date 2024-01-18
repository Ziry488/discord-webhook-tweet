import feedparser
import asyncio
import requests
import os
from datetime import datetime

DATA_FOLDER = "data"
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

#webhook & rss need to have same position in array

WEBHOOK_URLS = [
    "webhook",
]

LAST_ENTRY_IDS = {
    "rss": None,
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

async def send_rss_news(feed_url, webhook_url):
    while True:
        try:
            feed = feedparser.parse(feed_url)
            if len(feed.entries) > 0:
                latest_entry = feed.entries[0]
                last_id = load_last_id(feed_url)
                if latest_entry.id != last_id:
                    news_link = latest_entry.link
                    message = f"{news_link}"

                    payload = {"content": message}

                    response = requests.post(webhook_url, json=payload)
                    if response.status_code == 204:
                        now = datetime.now()
                        current_time = now.strftime("%H:%M:%S")
                        print(current_time + " new message in: " + feed_url)
                    elif response.status_code == 429:
                        print("RATE LIMITED")
                    else:
                        print("WRONG WEBHOOK RESPONSE: " + str(response.status_code))
                    save_last_id(feed_url, latest_entry.id)
                await asyncio.sleep(5)
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            await asyncio.sleep(60)

async def start_webhook_rss():
    tasks = [send_rss_news(feed_url, WEBHOOK_URLS[i]) for i, feed_url in enumerate(LAST_ENTRY_IDS.keys())]
    await asyncio.gather(*tasks)

try:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        print("Running...")
        loop.run_until_complete(start_webhook_rss())
    except KeyboardInterrupt:
        pass
except Exception as e:
    print(f"An error occurred: {e}")
