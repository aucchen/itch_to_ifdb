# 1. read data from an itch.io url
# 2. create an ifiction xml

import datetime
import subprocess

from selectolax.parser import HTMLParser
import requests

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from itch_data import ItchData
from itch_to_ifdb import find_ifdb_id, login_selenium, upload_selenium

def get_cs_data(url, use_short_desc=False, use_api=False, api_token=None):
    """
    Takes in an url of the form https://www.choiceofgames.com/professor-of-magical-studies/
    or https://www.choiceofgames.com/user-contributed/midnight-saga-the-monster/
    , and returns
    an ItchData object.
    """
    r = requests.get(url)
    tree = HTMLParser(r.content.decode('utf-8'))
    # get title and author
    title = tree.head.css_first('title').text()
    author = tree.css_first('h2[id="author"]').text()[3:]
    # TODO: get long description
    desc = tree.head.css_first('meta[name="description"]').attributes['content']
    # get release date, platform
    release_date = None
    platform = 'ChoiceScript'
    # get cover image
    cover_url = tree.head.css_first('meta[property="og:image"]').attributes['content']
    # download cover
    cover_request = requests.get(cover_url)
    image_name = cover_url.split('/')[-1]
    with open(image_name, 'wb') as f:
        f.write(cover_request.content)
    # make the cover smaller
    subprocess.call('convert {0} -resize 400x300 {0}'.format(image_name), shell=True)
    # if cover image is a gif, extract the first frame.
    if image_name.endswith('.gif'):
        subprocess.call('convert {0}[0] {0}'.format(image_name), shell=True)
    data = ItchData(url, title, author, release_date, desc, platform, image_name,
            license='Commercial')
    return data


def run_pipeline_selenium(url=None, destination='https://ifdb.org/', driver=None, login=True):
    if not url:
        url = input('Enter a www.choiceofgames.com URL: ')
    data = get_cs_data(url)
    # search ifdb to see if the game already exists
    ifdb_exists = find_ifdb_id(data)
    if ifdb_exists is not None:
        print('Warning: game may already exist on IFDB - https://ifdb.org/viewgame?id=' + ifdb_exists)
        to_continue = input('Do you still wish to continue uploading? (y/N): ').lower()
        if to_continue != 'y':
            return
    data.correct_data()
    # do the upload
    to_continue = input('Do you wish to upload? (y/N): ').lower()
    if to_continue != 'y':
        print('Data not uploaded.')
        return
    upload_selenium(data, destination, driver=driver, login=login, add_link=False)


def run_pipeline_selenium_loop(destination='https://ifdb.org/'):
    options = Options()
    driver = webdriver.Firefox(options=options)
    login_selenium(driver, destination)
    while True:
        run_pipeline_selenium(destination=destination, driver=driver, login=False)


if __name__ == '__main__':
    run_pipeline_selenium_loop()
