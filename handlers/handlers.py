from telegram.ext import (CommandHandler, MessageHandler, Filters, CallbackContext,
                          CallbackQueryHandler, ConversationHandler)
from telegram import (ParseMode, InlineKeyboardButton, InlineKeyboardMarkup, Update)
from backend.parser import parse_data, parse_film_page
from database.tools import store_user
from phrases import info_form, wait_text, no_results_text
from decouple import config
import json


ID = config('ID')
HASH = config('HASH')
PHONE = config('PHONE')
USERBOT_ID = int(config('USERBOT_ID'))

SEARCH, MAIN_MENU, DOWNLOAD = range(3)

def start_callback(update: Update, context: CallbackContext):
    update.message.reply_text(text='Welcome to the FilmBot!')
    store_user(update)

    return SEARCH


start_handler = CommandHandler(command='start',
                               callback=start_callback,
                               pass_chat_data=True,
                               filters=Filters.private)


def query_callback(update: Update, context: CallbackContext):
    cid = update.effective_message.chat.id
    q = update.message.text
    store_user(update)
    message_id = context.bot.send_message(chat_id=cid,
                                          text='Searching film...').message_id
    results = parse_data(q)

    if len(results) == 0:
        context.bot.edit_message_text(chat_id=cid,
                                      message_id=message_id,
                                      text=no_results_text)

        context.chat_data.update({'message_ids': [message_id]})

        return SEARCH

    context.chat_data.update({'results': results})

    download_button = InlineKeyboardButton(text='download',
                                           callback_data='choose_film_quality:0')
    next_button = InlineKeyboardButton(text='next',
                                       callback_data='film:1')

    info_button = InlineKeyboardButton(text='info',
                                       callback_data='info:0')
    all_button = InlineKeyboardButton(text='show all',
                                      callback_data='all:0')

    if len(results) > 1:

        keyboard = InlineKeyboardMarkup([[download_button],
                                         [next_button],
                                         [all_button, info_button]])
    else:
        keyboard = InlineKeyboardMarkup([[download_button, info_button]])

    context.bot.edit_message_text(chat_id=cid,
                                  message_id=message_id,
                                  text=results[0]['title'],
                                  reply_markup=keyboard)

    context.chat_data.update({'message_ids': [message_id]})

    return MAIN_MENU


query_handler = MessageHandler(callback=query_callback,
                               pass_chat_data=True,
                               filters=Filters.text)


def switch_film_callback(update: Update, context: CallbackContext):

    cid = update.effective_message.chat.id
    mid = update.callback_query.message.message_id

    if context.chat_data.get('results') is None:
        context.bot.delete_message(chat_id=cid,
                                   message_id=mid)
        return SEARCH

    current_film = int(update.callback_query.data.split(':')[-1])
    results = context.chat_data['results']

    download_button = InlineKeyboardButton(text='download',
                                           callback_data=f'choose_film_quality:{current_film}')
    next_button = InlineKeyboardButton(text='next',
                                       callback_data=f'film:{current_film + 1}')
    previous_button = InlineKeyboardButton(text='previous',
                                           callback_data=f'film:{current_film - 1}')
    all_button = InlineKeyboardButton(text='show all',
                                      callback_data=f'all:{current_film}')
    info_button = InlineKeyboardButton(text='info',
                                       callback_data=f'info:{current_film}')

    if len(results) - 1 == current_film:
        keyboard = InlineKeyboardMarkup([[download_button],
                                         [previous_button],
                                         [all_button, info_button]])

    elif current_film == 0:
        keyboard = InlineKeyboardMarkup([[download_button],
                                         [next_button],
                                         [all_button, info_button]])

    else:
        keyboard = InlineKeyboardMarkup([[download_button],
                                         [previous_button, next_button],
                                         [all_button, info_button]])

    context.bot.edit_message_text(chat_id=cid,
                                  message_id=mid,
                                  text=results[current_film]['title'],
                                  reply_markup=keyboard)

    return MAIN_MENU


switch_film_handler = CallbackQueryHandler(callback=switch_film_callback,
                                           pattern='film:(.*)',
                                           pass_chat_data=True)


def show_info_about_film_callback(update: Update, context: CallbackContext):
    cid = update.effective_message.chat.id
    mid = update.callback_query.message.message_id

    current_film = int(update.callback_query.data.split(':')[-1])

    results = context.chat_data['results']

    download_button = InlineKeyboardButton(text='download',
                                           callback_data=f'choose_film_quality:{current_film}')
    back_to_slider_button = InlineKeyboardButton(text='back',
                                                 callback_data=f'film:{current_film}')

    keyboard = InlineKeyboardMarkup([[back_to_slider_button, download_button]])

    context.bot.edit_message_text(chat_id=cid,
                                  message_id=mid,
                                  text=info_form.format(results[current_film]['title'],
                                                        results[current_film]['description']),
                                  reply_markup=keyboard,
                                  parse_mode=ParseMode.HTML)

    return MAIN_MENU


show_info_about_film_handler = CallbackQueryHandler(callback=show_info_about_film_callback,
                                                    pattern='info:(.*)',
                                                    pass_chat_data=True)


def show_all_films_callback(update: Update, context: CallbackContext):

    cid = update.effective_message.chat.id
    mid = update.callback_query.message.message_id

    results = context.chat_data['results']

    output_message = ''

    for film in results:
        output_message += film['title'] + '\n'

    back_to_slider_button = InlineKeyboardButton(text='back', callback_data='film:0')
    keyboard = InlineKeyboardMarkup([[back_to_slider_button]])

    context.bot.edit_message_text(chat_id=cid,
                                  message_id=mid,
                                  text=output_message,
                                  reply_markup=keyboard)

    return MAIN_MENU


show_all_films_handler = CallbackQueryHandler(callback=show_all_films_callback,
                                              pattern='all(.*)')


def choose_film_quality_handler(update: Update, context: CallbackContext):

    cid = update.effective_message.chat.id
    mid = update.callback_query.message.message_id

    results = context.chat_data['results']

    current_film = int(update.callback_query.data.split(':')[-1])
    context.chat_data.update({'title': results[current_film]['title']})

    download_urls_list = parse_film_page(results[current_film]['movie_url'], results[current_film]['title'])

    context.chat_data.update({'download_urls': download_urls_list})

    back_to_slider_button = InlineKeyboardButton(text='back', callback_data=f'film:{current_film}')

    button_list = []

    for url in download_urls_list:
        button_list.append(InlineKeyboardButton(text=url['quality'], callback_data=f'download:{url["quality"]}'))

    keyboard = InlineKeyboardMarkup([button_list, [back_to_slider_button]])

    context.bot.edit_message_text(chat_id=cid,
                                  message_id=mid,
                                  text='<b>Choose film quality</b>',
                                  reply_markup=keyboard,
                                  parse_mode=ParseMode.HTML)

    return DOWNLOAD


choose_film_quality_handler = CallbackQueryHandler(callback=choose_film_quality_handler,
                                                   pattern='choose_film_quality:(.*)')


def download_callback(update: Update, context: CallbackContext):
    cid = update.effective_message.chat.id
    mid = update.callback_query.message.message_id

    download_urls_list = context.chat_data['download_urls']

    quality = update.callback_query.data.split(':')[-1]


    download_url = list(filter(lambda film: film['quality'] == quality, download_urls_list))[0]
    download_url.update({'user_id': cid})

    context.bot.send_message(chat_id=USERBOT_ID, text=json.dumps(download_url))

    context.bot.edit_message_text(chat_id=cid,
                                  message_id=mid,
                                  text=wait_text,
                                  parse_mode=ParseMode.HTML)

    return SEARCH


download_handler = CallbackQueryHandler(callback=download_callback,
                                        pass_user_data=True,
                                        pass_update_queue=True,
                                        pattern='download:(.*)')


def userbot_message_callback(update: Update, context: CallbackContext):
    print('Bot got message from userbot')
    data = update.effective_message.caption.split('_')
    fid = update.effective_message.video.file_id
    uid = data[0]
    title = data[1]

    context.bot.send_video(chat_id=uid,
                           caption=title,
                           video=fid,
                           width=1920,
                           height=1080,
                           supports_streaming=True)
    print('Send video to user')


userbot_message_handler = MessageHandler(callback=userbot_message_callback,
                                         pass_chat_data=True,
                                         filters=Filters.chat(chat_id=USERBOT_ID))


def exit_callback(update: Update, context: CallbackContext):
    return ConversationHandler.END


exit_handler = CallbackQueryHandler(callback=exit_callback,
                                    pattern='exit')


