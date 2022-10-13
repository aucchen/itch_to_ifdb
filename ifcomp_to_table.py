import datetime

from bs4 import BeautifulSoup
import urllib.request


new_url = 'https://ifcomp.org/ballot?alphabetize=1'

end_date = datetime.datetime(2022, 11, 15)

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
    game_id = row.attrs['id'].split('-')[1]
    title = row.find('h2').text.strip().split('\n')[0]
    current_game['title'] = title
    # get bg
    """
    try:
        img_url = row.find('img').attrs['src']
        with urllib.request.urlopen(img_url) as fp:
            data = fp.read()
            with open('ifcomp_2022_covers/' + title + '.jpg', 'wb') as f:
                f.write(data)
    except:
        pass
    """
    try:
        author = row.find('div', attrs={'class': 'col-xs-8'}).find('strong').text.strip()
    except:
        author = row.find('strong').text.strip()
    current_game['author'] = author
    current_game['url'] = 'https://ifcomp.org/play/{0}/play_online'.format(game_id)
    current_game['dl_url'] = 'https://ifcomp.org/play/{0}/play_online'.format(game_id)
    # get desc
    try:
        desc_col = row.find('div', attrs={'class': 'col-xs-8'})
        desc = '\n\n'.join(x.text.strip() for x in desc_col.find_all('p')[1:-1])
    except:
        desc_col = row.find('div', attrs={'class': 'col-xs-12'})
        desc = '\n\n'.join(x.text.strip() for x in desc_col.find_all('p')[1:-1])
    current_game['desc'] = desc
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
    # TODO: find type
    ems = row.find('em').text
    if 'Twine' in ems:
        current_game['platform'] = 'Twine'
    elif 'Ink ' in ems:
        current_game['platform'] = 'Ink'
    elif 'Glulx ' in ems or 'Z-code' in ems:
        current_game['platform'] = 'Inform 7'
    elif 'TADS' in ems:
        current_game['platform'] = 'TADS'
    elif 'ChoiceScript' in ems:
        current_game['platform'] = 'ChoiceScript'
    elif 'Texture' in ems:
        current_game['platform'] = 'Texture'
    else:
        current_game['platform'] = ''
    print(current_game)
    games.append(current_game)
    current_game = {}

import pandas as pd
df = pd.DataFrame(games)
df.to_csv('data_2022.tsv', sep='\t', index=None) 
