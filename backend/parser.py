from bs4 import BeautifulSoup
import re
import requests
import base64
from decouple import config

kinogo_url = config('KINOGO_URL')


def get_html(url, session, search_query, index=1):

    data = {
        'do': 'search',
        'subaction': 'search',
        'search_start': index,
        'result_from': ((index - 1) * 10 + 1),
        'story': search_query.encode('windows-1251')}
    r = session.post(url, data=data)
    return r.text


def get_total_pages(html):
    soup = BeautifulSoup(html, 'lxml')

    pages_total = soup.find('div', class_='bot-navigation')
    if pages_total is None:
        return 1
    pages_total = pages_total.find_all('a')

    if len(pages_total) < 2:
        return 1
    else:
        pages_total = int(pages_total[-2].text)

    return pages_total


def get_info(soup_object):
    title = soup_object.find('h2').text
    if re.search(r'(.*)сезон\)', title):
        return

    description = soup_object.find('div', {'id': re.compile(r'news-id-\d')}).text
    movie_page_url = soup_object.find('h2').find_all('a')[1]['href']

    return dict(title=title, description=description, movie_url=movie_page_url)


def parse_data(search_query):
    session = requests.Session()

    query_results_html = get_html(kinogo_url, session, search_query)

    total_pages = get_total_pages(query_results_html)

    filtered_data = []

    for i in range(1, total_pages + 1):

        page_html = get_html(kinogo_url, session, search_query, i)

        soup = BeautifulSoup(page_html, 'lxml')
        query_results = soup.find_all('div', class_='shortstory')

        for query_object in query_results:
            info = get_info(query_object)
            if info:
                filtered_data.append(info)

    return filtered_data


def get_html_for_film(url):
    r = requests.get(url)
    return r.text


def parse_film_page(film_url, title):
    film_page_html = get_html_for_film(film_url)
    quality_list = ['240', '360', '720', '1080']
    soup = BeautifulSoup(film_page_html, 'lxml')
    download_url = soup.find_all('a', {'href': re.compile('(.*).mp4')})
    download_list = []

    for count in range(len(download_url)):
        url = download_url[count].get('href')
        quality = re.findall(r'(\d+).mp4', url)[0]
        download_list.append(dict(url=url, title=title, quality=quality))

    return download_list
