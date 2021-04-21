from handlers_component.phrases import error_text
from database.tools import store_film, if_film_in_db
from pyrogram import Client, filters
from backend.download_files import download_file
from decouple import config
import logging
import json
import os


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

ID = config('ID')
HASH = config('HASH')
PHONE = config('PHONE')

app = Client('OmgOmg_bot',
             api_id=ID,
             api_hash=HASH,
             phone_number=PHONE)


def progress(current, total):
    print("{:.1f}%".format(current * 100 / total))


@app.on_message(filters.bot)
def download_film(client, message):
    data = json.loads(message.text)
    cid = message.chat.id
    in_db = True
    path_to_film = if_film_in_db(data['title'], data['quality'])

    print('get message from bot')
    if path_to_film is None:
        in_db = False
        path_to_film = download_file(data['title'], data['url'])

    file_id_list = []
    for i in range(len(path_to_film)):
        print('Send video to bot')
        print()
        try:
            caption = f'{data["user_id"]}_{data["title"]}_{data["quality"]}'
            file_id_list.append(app.send_video(chat_id=cid,
                                               video=path_to_film[i],
                                               caption=caption,
                                               supports_streaming=True,
                                               progress=progress,
                                               width=1920,
                                               height=1080).video.file_id)

        except Exception as e:
            print(e)
            app.send_message(chat_id=cid,
                             text=error_text.format(data["user_id"]))

        if not in_db:
            os.remove(path_to_film[i])

    if in_db:
        return
    store_film(title=data['title'],
               file_id=file_id_list,
               download_url=data['url'],
               quality=data['quality'])

app.run()
