# 1. read data from an itch.io url
# 2. create an ifiction xml

import datetime
import json
import os
import subprocess
import time

from selectolax.parser import HTMLParser
import lxml.etree as etree
import requests

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from itch_data import ItchData

def get_itch_data(url, use_short_desc=False, use_api=False, api_token=None):
    """
    Takes in an url of the form https://red-autumn.itch.io/pageant, and returns
    an ItchData object.
    """
    r = requests.get(url)
    tree = HTMLParser(r.content.decode('utf-8'))
    # 1. get game ID
    # <meta content="games/[id]" name="itch:path">
    game_id = tree.head.css_first('meta[name="itch:path"]').attributes['content'] 
    game_id = game_id.split('/')[1]
    # there's a json at https://api.itch.io/games/[id], but maybe we should just parse all the info from the html to avoid making another request.
    # also, using the api endpoint requires an api token
    # get title and author
    title_author = tree.head.css_first('title').text()
    title, author = title_author.split(' by ')
    # get full description
    desc = tree.css_first('div.formatted_description')
    # TODO: better formatting for the description?
    desc = desc.text()
    # get release date, platform
    rows = tree.css('tr')
    release_date = None
    platform = None
    for row in rows:
        entries = list(row.iter(False))
        if entries[0].text() == 'Made with':
            platform = entries[1].text()
        if entries[0].text() == 'Release date' or entries[0].text() == 'Published':
            date = entries[1].css_first('abbr').attributes['title']
            release_date = datetime.datetime.strptime(date, '%d %B %Y @ %H:%M')
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
    data = ItchData(url, title, author, release_date, desc, platform, image_name, game_id)
    return data


def get_itch_json(game_id, api_token):
    json_url = 'https://api.itch.io/games/' + game_id
    r_json = requests.get(json_url, headers={'Authorization': api_token})
    data = json.loads(r_json.content)
    data = data['game']
    return ItchData(
            data['url'],
            data['title'],
            data['user']['display_name'],
            datetime.datetime.strptime(data['published_at'], '%Y-%m-%dT%H:%M:%S.%f'),
            data['short_text'],
            None, # the field isn't here :(
            data['cover_url'],
            data['id']
            )


def create_xml(data):
    """
    Creates an ifiction XML using an ItchData object.
    """
    nsmap = {None: 'http://babel.ifarchive.org/protocol/iFiction/'}
    root = etree.Element('ifindex', nsmap=nsmap)
    story = etree.SubElement(root, 'story')
    # identification
    iden = etree.SubElement(story, 'identification')
    format = etree.SubElement(iden, 'format')
    format.text = data.platform

    # bibliographic
    bibliographic = etree.SubElement(story, 'bibliographic')
    title = etree.SubElement(bibliographic, 'title')
    title.text = data.title
    author = etree.SubElement(bibliographic, 'author')
    author.text = data.author
    desc = etree.SubElement(bibliographic, 'description')
    desc.text = data.desc.replace('\n', '<br/>')
    if data.release:
        firstpublished = etree.SubElement(bibliographic, 'firstpublished')
        firstpublished.text = data.release.strftime('%Y-%m-%d')

    # contacts
    contacts = etree.SubElement(story, 'contacts')
    url = etree.SubElement(contacts, 'url')
    url.text = data.url

    xml = etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8')
    print(xml.decode('utf-8'))
    return root

def find_ifdb_id(data):
    """
    Returns the ifdb id corresponding to a game name, or None if one doesn't exist.
    """
    game_name = data.title
    game_name = game_name.replace(' ', '+').replace('/', '%2F')
    url = 'https://ifdb.org/search?searchbar="{0}"'.format(game_name)
    print(url)
    r = requests.get(url)
    tree = HTMLParser(r.content.decode("ISO-8859-1"), 'lxml')
    if 'TUID' in tree.html:
        spans = tree.css('span#notes')
        for span in spans:
            if 'TUID' in span.text:
                tuid = span.text.split(':')[-1].strip()
                return tuid
    else:
        try:
            url = tree.css_first('td').css_first('a').attrs['href']
            return url.split('=')[-1]
        except:
            return None


def upload_selenium(data, destination='https://ifdb.org'):
    # destination could be http://localhost:8080
    # admin email/password for test: ifdbadmin@ifdb.org, secret
    # 1. log in
    username = input('IFDB email: ')
    password = input('IFDB password: ')
    options = Options()
    # options.headless = True
    driver = webdriver.Firefox(options=options)
    driver.get(destination + '/login')
    driver.find_element(By.ID, 'userid').send_keys(username)
    driver.find_element(By.ID, 'password').send_keys(password)
    driver.find_element(By.XPATH, "//input[@type='submit']").click()
    # 2. fill in game stuff
    driver.get(destination + '/editgame?id=new')
    driver.find_element(By.ID, 'title').send_keys(data.title)
    driver.find_element(By.ID, 'eAuthor').send_keys(data.author)
    # upload cover art (why is it so complicated???)
    driver.execute_script('document.getElementById("coverart-iframe").style.display = "block";')
    driver.switch_to.frame('coverart-iframe')
    cover_art = driver.find_element(By.ID, 'uplFile')
    art_url = os.path.join(os.getcwd(), data.cover)
    cover_art.send_keys(art_url)
    driver.switch_to.default_content()
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.NAME, 'okbtn'))).click()
    time.sleep(1)
    # click on the most recently updated cover image
    cover_checks = driver.find_elements(By.XPATH, '//input[@name="coverart"]')
    highest_cover_check = None
    for c in cover_checks:
        c_id = c.get_attribute('id')
        if 'none' not in c_id:
            highest_cover_check = c
    highest_cover_check.click()
    # set release date
    # first publication date: dd-Mon-yyyy
    if data.release:
        month_shortened = data.release.strftime('%B')[:3]
        release_time = data.release.strftime('%d-{0}-%Y'.format(month_shortened))
        driver.find_element(By.ID, 'published').send_keys(release_time)
    # other fields
    if data.platform:
        driver.find_element(By.ID, 'system').send_keys(data.platform)
    if data.desc:
        driver.find_element(By.ID, 'desc').send_keys(data.desc)
    if data.language:
        driver.find_element(By.ID, 'language').send_keys(data.language)
    if data.license:
        driver.find_element(By.ID, 'license').send_keys(data.license)
    if data.genre:
        driver.find_element(By.ID, 'genre').send_keys(data.genre)
    driver.find_element(By.ID, 'website').send_keys(data.url)
    # submit
    driver.find_element(By.ID, 'editgame-save-button').click()
    driver.close()


def create_links(data):
    nsmap = {None: 'http://ifdb.org/api/xmlns'}
    root = etree.Element('downloads', nsmap=nsmap)
    links = etree.SubElement(root, 'links')
    link = etree.SubElement(links, 'link')
    link_url = etree.SubElement(link, 'url')
    link_url.text = data.url
    title = etree.SubElement(link, 'title')
    title.text = 'itch.io'
    desc = etree.SubElement(link, 'desc')
    desc.text = 'Play on itch.io'
    format = etree.SubElement(link, 'format')
    format.text = 'html'
    return root


def run_pipeline(url=None, destination='http://ifdb.org/putific'):
    if not url:
        url = input('Enter an itch.io URL: ')
    data = get_itch_data(url)
    data.correct_data()
    print('\nCreating xml for ifdb upload...\n')
    xml_root = create_xml(data)
    links = create_links(data)
    # TODO: create the wrapped file
    # get ifdb username/password
    ifdb_username = input('Enter your IFDB email: ')
    ifdb_password = input('Enter your IFDB password: ')
    upload_url = destination
    upload_data = {'username': ifdb_username, 'password': ifdb_password}
    output_etree = etree.tostring(xml_root, pretty_print=True, xml_declaration=True, encoding='utf-8')
    output_etree = output_etree.replace(b'&lt;br/&gt;', b'<br/>')
    params = {'username': ('', ifdb_username),
              'password': ('', ifdb_password),
              'ifiction': ('ifiction.xml', output_etree, 'text/xml'),
              'links': ('links.xml', etree.tostring(links, encoding='utf-8'), 'text/xml'),
              'coverart': (data.cover, open(data.cover, 'rb')),
              'requireIFID': ('', 'no')}
    r = requests.post(upload_url, data=upload_data, files=params)
    print()
    print('Response: ', r.content)
    return r

def run_pipeline_selenium(url=None, destination='https://ifdb.org/'):
    if not url:
        url = input('Enter an itch.io URL: ')
    data = get_itch_data(url)
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
    upload_selenium(data, destination)


if __name__ == '__main__':
    run_pipeline_selenium()
