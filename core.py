from handlers_component.handlers import (start_handler, query_handler, switch_film_handler,
                                         show_all_films_handler, show_info_about_film_handler, download_handler,
                                         choose_film_quality_handler, exit_handler, userbot_message_handler,
                                         SEARCH, MAIN_MENU, DOWNLOAD)
from telegram.ext import Updater, ConversationHandler
from decouple import config
import sentry_sdk
import logging
from logdna import LogDNAHandler
from sentry_sdk.integrations.logging import LoggingIntegration

TOKEN = config('BOT_TOKEN')

upd = Updater(token=TOKEN, use_context=True)
dp = upd.dispatcher

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(message)s')

logDNAoptions = dict()
logDNAoptions['index_meta'] = True
logDNAoptions['hostname'] = config('HOSTNAME', default='localhost')
logDNAhandler = LogDNAHandler(config('LOGDNA_KEY'), options=logDNAoptions)

logger = logging.getLogger()
logger.addHandler(logDNAhandler)

sentry_logging = LoggingIntegration(
    level=logging.DEBUG,
    event_level=logging.ERROR
)

sentry_sdk.init(
    config('SENTRY_URL'),
    traces_sample_rate=1.0,
    integrations=[sentry_logging]
)


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
