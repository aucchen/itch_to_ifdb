import datetime
import re

from bs4 import BeautifulSoup
import urllib.request

# TODO: find ifdb data

def find_ifdb_id(game_name):
    """
    Returns the ifdb id corresponding to a game name.
    """
    game_name = game_name.replace(' ', '+').replace('/', '%2F')
    url = 'https://ifdb.org/search?searchbar={0}'.format(game_name)
    print(url)
    with urllib.request.urlopen(url) as fp:
        data = fp.read()
        html = data.decode("ISO-8859-1")
    soup = BeautifulSoup(html, 'lxml')
    if 'TUID' in soup.text:
        spans = soup.find_all('span', attrs={'class': 'notes'})
        for span in spans:
            if 'TUID' in span.text:
                tuid = span.text.split(':')[-1].strip()
                return tuid
    else:
        try:
            url = soup.find('td').find('a')['href']
            return url.split('=')[-1]
        except:
            print('Game not found')
            return None

def get_ratings(ifdb_id, end_date=None):
    """
    Given an IFDB game id, returns the game's rating and number of ratings (as of end_date)
    """
    url = 'https://ifdb.org/viewgame?id={0}&reviews&sortby=&ratings&pg=all'.format(ifdb_id)
    with urllib.request.urlopen(url) as fp:
        data = fp.read()
        html = data.decode("ISO-8859-1")
    soup = BeautifulSoup(html, 'lxml')
    indented_div = soup.find_all('div', attrs={'class': 'indented'})[0]
    all_stars = []
    current_stars = 0
    current_date = datetime.datetime(2010, 1, 1)
    for child in indented_div.children:
        if child.name == 'p':
            image = child.find('img')
            if image:
                current_stars = int(image['title'][0])
                if end_date is not None:
                    try:
                        text = ','.join(child.text.split(',')[-2:]).strip()
                        current_date = datetime.datetime.strptime(text, '%B %d, %Y')
                        if current_date > end_date:
                            continue
                    except:
                        continue
                all_stars.append(current_stars)
        elif child.name == 'img':
            current_stars = int(child['title'][0])
            if end_date is None:
                all_stars.append(current_stars)
        elif child.name == 'span' and end_date != None:
            text = child.text.strip(', ')
            try:
                current_date = datetime.datetime.strptime(text, '%B %d, %Y')
                if current_date > end_date:
                    continue
                all_stars.append(current_stars)
            except:
                pass
    count = len(all_stars)
    mean = 0
    if count > 0:
        mean = float(sum(all_stars))/count
    return mean, count


def get_rankings(tag="IFComp 2021"):
    """
    Returns a list of games sorted by their rank.
    """
    tag = tag.replace(' ', '+')
    url = 'https://ifdb.org/search?searchfor=tag%3A{0}&sortby=&pg=all'.format(tag)
    with urllib.request.urlopen(url) as fp:
        data = fp.read()
        html = data.decode("ISO-8859-1")
    soup = BeautifulSoup(html, 'lxml')
    main = soup.find('div', attrs={'class':'main'})
    all_links = main.find_all('a')
    games = []
    for link in all_links:
        bold = link.find('b')
        if bold:
            print(link.text)
            games.append(link.text)
    return games


def get_system(ifdb_id):
    """
    Returns the development system.
    """
    url = 'https://ifdb.org/viewgame?id={0}'.format(ifdb_id)
    with urllib.request.urlopen(url) as fp:
        data = fp.read()
        html = data.decode("ISO-8859-1")
    soup = BeautifulSoup(html, 'lxml')
    notes = soup.find('span', attrs={'class':'notes'})
    dev_system = None
    in_dev = False
    for el in notes:
        if in_dev:
            dev_system = el.text
            in_dev = False
            break
        if 'Development System' in el:
            in_dev = True
    return dev_system


def get_ifwiki_game_info(ifdb_id):
    """
    Returns a dict for the given game containing the default info for an ifwiki stub.
    """
    # TODO
    url = 'https://ifdb.org/viewgame?id={0}'.format(ifdb_id)
    with urllib.request.urlopen(url) as fp:
        data = fp.read()
        html = data.decode("ISO-8859-1")
    soup = BeautifulSoup(html, 'lxml')
    # Fields we need:
    # - name
    # - author
    # - release/version
    # - release date
    # - system/platform
    # - ifid
    # - tuid
    # - genre


def get_ifcomp_results(comp_url='https://ifdb.org/viewcomp?id=rniofn8a8pnivk86'):
    """
    Returns a list of (rank, name, author) containing the ifcomp results. 
    """
    with urllib.request.urlopen(comp_url) as fp:
        data = fp.read()
        html = data.decode("ISO-8859-1")
    soup = BeautifulSoup(html, 'lxml')
    # TODO: get list of games and authors
    indented_div = soup.find_all('div', attrs={'class': 'indented'})[0]
    games = []
    current_place = ''
    current_game_name = ''
    current_game_author = ''
    n_re = r'[0-9]+'
    for child in indented_div.children:
        if child.name is None:
            text = str(child).strip()
            if text.endswith(':'):
                current_place = re.match(n_re, text).group()
            elif text.startswith(', by'):
                current_game_author = text.strip(', by ')
                games.append((current_place, current_game_name, current_game_author))
        elif child.name == 'a':
            current_game_name = child.text
    return games


def format_ifcomp_results(games, filename='data_2021_final.tsv'):
    """
    Takes the output of get_ifcomp_results, and formats them for ifwiki.
    """
    import pandas as pd
    output_lines = ['<ol>']
    data = pd.read_csv(filename, index_col=None, delimiter='\t')
    data_dict = {}
    for i, row in data.iterrows():
        data_dict[i] = row
    for i, game in enumerate(games):
        system = data_dict[i].system
        line = '<li value="{0}">\'\'[[{1}]]\'\' ([[{2}]]; {3}).'.format(*game, system)
        output_lines.append(line)
    output = '\n'.join(output_lines)
    return output


def get_reviews(table):
    """
    Using a pandas table, creates a dict of game : review
    """ 

if __name__ == '__main__':
    games = get_ifcomp_results()
    print(format_ifcomp_results(games))
