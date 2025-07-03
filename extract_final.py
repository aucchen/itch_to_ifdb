import datetime

from bs4 import BeautifulSoup
import urllib.request

import ifdb

old_url = 'https://ifcomp.org/comp/2023'

end_date = datetime.datetime(2023, 11, 15)

with urllib.request.urlopen(old_url) as fp:
    data = fp.read()
    html = data.decode("utf8")

soup = BeautifulSoup(html, 'html.parser')

rows = soup.find_all('div', attrs={'class': 'row'}) 
mode = 'title'
games = []
current_game = {}
for i, row in enumerate(rows):
    print(i, row)
    if mode == 'title':
        mode = 'info'
        title = row.find_all('h2')[1].text.strip().split('\n')[0]
        current_game['title'] = title
    elif mode == 'info':
        mode = 'rank'
        # TODO: this part doesn't work
        author = next(row.find_all('strong')[0].children, None)
        if hasattr(author, 'text'):
            current_game['author'] = author.text.strip()
        else:
            current_game['author'] = author.strip()
        entries = row.find_all('td')
        current_game['score'] = float(entries[0].text.strip())
        current_game['rating_count'] = int(entries[1].text.strip())
        current_game['stdev'] = float(entries[2].text.strip())
        current_game['is_parser'] = int('Parser' in row.text)
        if 'Two hours' in row.text:
            current_game['time'] = 120
        elif 'An hour and a half' in row.text:
            current_game['time'] = 90
        elif 'One hour' in row.text:
            current_game['time'] = 60
        elif 'Longer than two hours' in row.text:
            current_game['time'] = 150
        elif 'Half an hour' in row.text:
            current_game['time'] = 30
        elif '15 minutes or less' in row.text:
            current_game['time'] = 15
        else:
            current_game['time'] = 0
        """
        refs = row.find_all('a')
        for ref in refs:
            if 'ifdb' in ref['href']:
                ifdb_id = ref['href'].split('=')[1]
                current_game['ifdb_id'] = ifdb_id
                print(ifdb_id)
                rating, count = ifdb.get_ratings(ifdb_id, end_date)
                current_game['ifdb_rating'] = rating
                current_game['ifdb_rating_count'] = count
                system = ifdb.get_system(ifdb_id)
                current_game['system'] = system
                break
        """
    elif mode == 'rank':
        print(current_game)
        mode = 'title'
        games.append(current_game)
        current_game = {}

import pandas as pd
df = pd.DataFrame(games)
df.to_csv('data_2023_final.tsv', sep='\t', index=None) 
