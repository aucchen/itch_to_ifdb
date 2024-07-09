import time

from bs4 import BeautifulSoup
import urllib.request

import pandas as pd


page = 1
year = 2023
url = f'https://ifdb.org/search?searchfor=published%3A{year}&sortby=&pg={page}'



def parse_search_result(url):
    with urllib.request.urlopen(url) as fp:
        data = fp.read()
        html = data.decode("ISO-8859-1")

    soup = BeautifulSoup(html, 'lxml')
    all_results = soup.find_all('h3', attrs={'class': 'result'})
    all_game_info = []
    # get all titles and tuids
    for result in all_results:
        link = result.find('a')
        href = link.attrs['href']
        tuid = href.split('=')[1]
        game_info = get_game_info(tuid)
        print(game_info)
        all_game_info.append(game_info)
        time.sleep(0.1)
    return all_results

def get_game_info(tuid):
    url = 'https://ifdb.org/viewgame?ifiction&id=' + tuid
    with urllib.request.urlopen(url) as fp:
        data = fp.read()
    xml = BeautifulSoup(data, features='xml')
    title = xml.find('title').text
    author = xml.find('author').text
    game_url = ''
    play_url = ''
    # TODO: this is messy
    urls = xml.find_all('url')
    if len(urls) >= 1:
        game_url = urls[0].text
    if len(urls) >= 2:
        if not urls[1].text.startswith('https://ifdb.org'):
            play_url = urls[1].text
    base_url = 'https://ifdb.org/viewgame?id=' + tuid
    # website?
    return {'title': title, 'author': author, 'IFDB-link': base_url, 'game-url': game_url, 'playonline-url': play_url}

def get_all_data(year):
    page = 1
    url = f'https://ifdb.org/search?searchfor=published%3A{year}&sortby=old&pg={page}'
    all_results = []
    results = parse_search_result(url)
    all_results += results
    while results:
        page += 1
        url = f'https://ifdb.org/search?searchfor=published%3A{year}&sortby=old&pg={page}'
        results = parse_search_result(url)
        all_results += results
        time.sleep(0.5)
    return all_results

if __name__ == '__main__':
    all_results = get_all_data(2023)
    df = pd.DataFrame(all_results)
    df.to_csv('ifdb_2023_all.csv', sep='\t', index=None)

# select all h3 class="result"
