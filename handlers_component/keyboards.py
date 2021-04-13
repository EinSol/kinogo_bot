from telegram import (InlineKeyboardButton, InlineKeyboardMarkup)


def main_kb_state(current_film, result_len):
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

    if result_len == 1 and current_film == 0:
        one_film_kb = InlineKeyboardMarkup([[download_button, info_button]])
        return one_film_kb

    elif result_len > 1 and current_film == 0:
        more_film_kb = InlineKeyboardMarkup([[download_button],
                                             [next_button],
                                             [all_button, info_button]])
        return more_film_kb

    elif result_len - 1 == current_film:
        last_film_kb = InlineKeyboardMarkup([[download_button],
                                             [previous_button],
                                             [all_button, info_button]])
        return last_film_kb

    else:
        film_kb = InlineKeyboardMarkup([[download_button],
                                             [previous_button, next_button],
                                             [all_button, info_button]])
        return film_kb


def current_film_kb(current_film, result_len, state):
    download_button = InlineKeyboardButton(text='download',
                                           callback_data=f'choose_film_quality:{current_film}')
    back_to_slider_button = InlineKeyboardButton(text='back',
                                                 callback_data=f'film:{current_film}')

    if state == 'about':
        about_kb = InlineKeyboardMarkup([[back_to_slider_button, download_button]])
        return about_kb

    if state == 'all':
        all_kb = InlineKeyboardMarkup([[back_to_slider_button]])
        return all_kb


def get_quality_kb(current_film, url_list):
    button_list = []
    back_to_slider_button = InlineKeyboardButton(text='back',
                                                 callback_data=f'film:{current_film}')

    for url in url_list:
        button_list.append(InlineKeyboardButton(text=url['quality'], callback_data=f'download:{url["quality"]}'))

    url_kb = InlineKeyboardMarkup([button_list, [back_to_slider_button]])

    return url_kb
