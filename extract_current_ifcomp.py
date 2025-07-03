# Extracts the current ifcomp games, and tries to link them to ifdb entries.
# also updates the current reviews and review count.
import datetime
import time

from bs4 import BeautifulSoup
import urllib.request

import ifdb

new_url = 'https://ifcomp.org/ballot?alphabetize=1'

end_date = datetime.datetime(2024, 11, 15)

with urllib.request.urlopen(new_url) as fp:
    data = fp.read()
    html = data.decode("utf8")

soup = BeautifulSoup(html, 'html.parser')

rows = soup.find_all('div', attrs={'class': 'well'}) 
games = []
current_game = {}
for i, row in enumerate(rows):
    print(i)
    if len(row.find_all('h2')) == 0:
        continue
    title = row.find('h2').text.strip().split('\n')[0]
    current_game['title'] = title
    current_game['is_parser'] = int(row['ifcomp-style'] == 'parser')
    playtime = row['ifcomp-playtime']
    if 'two hours' in playtime:
        current_game['time'] = 120
    elif 'an hour and a half' in playtime:
        current_game['time'] = 90
    elif 'one hour' in playtime:
        current_game['time'] = 60
    elif 'longer than two hours' in playtime:
        current_game['time'] = 150
    elif 'half an hour' in playtime:
        current_game['time'] = 30
    elif '15 minutes or less' in playtime:
        current_game['time'] = 15
    else:
        current_game['time'] = 0
    # TODO: find ifdb refs
    try:
        ifdb_id = ifdb.find_ifdb_id(title)
        time.sleep(0.5)
        current_game['ifdb_id'] = ifdb_id
        print(ifdb_id)
        rating, count = ifdb.get_ratings(ifdb_id, end_date)
        time.sleep(0.5)
        current_game['ifdb_rating'] = rating
        current_game['ifdb_rating_count'] = count
    except:
        current_game['ifdb_id'] = '???'
        current_game['ifdb_rating'] = 0
        current_game['ifdb_rating_count'] = 0
    print(current_game)
    games.append(current_game)
    current_game = {}

import pandas as pd
df = pd.DataFrame(games)
df.to_csv('data_2024.tsv', sep='\t', index=None) 
