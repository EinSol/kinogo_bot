import logging
from handlers.handlers import (start_handler, query_handler, switch_film_handler,
                               show_all_films_handler, show_info_about_film_handler, download_handler,
                               choose_film_quality_handler, exit_handler, userbot_message_handler,
                               SEARCH, MAIN_MENU, DOWNLOAD)
from telegram.ext import Updater, ConversationHandler
from decouple import config

TOKEN = config('BOT_TOKEN')

upd = Updater(token=TOKEN, use_context=True)
dp = upd.dispatcher


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def main():
    dp.add_handler(userbot_message_handler)
    conv_handler = ConversationHandler(
        entry_points=[start_handler],
        states={
            SEARCH: [
                query_handler
            ],
            MAIN_MENU: [
                query_handler,
                switch_film_handler,
                show_all_films_handler,
                show_info_about_film_handler,
                choose_film_quality_handler

            ],
            DOWNLOAD: [
                download_handler,
                switch_film_handler
            ],
        },
        fallbacks=[exit_handler],
    )
    dp.add_handler(conv_handler)

    upd.start_polling()

    logging.info("Ready and listening for updates...")
    upd.idle()


if __name__ == '__main__':
    main()
