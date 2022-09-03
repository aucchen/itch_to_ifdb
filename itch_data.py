import datetime
import json


class ItchData():

    FIELDS = {'title', 'author', 'release', 'date', 'description', 'platform',
            'language', 'license', 'genre'}

    GENRES = ['Abuses', 'Adaptation', "Children's", 'Collegiate', 'Educational', 'Espionage', 'Fantasy', 'Historical', 'Horror', 'Humor', 'Mystery', 'Pornographic', 'Religious', 'Romance', 'RPG', 'Science Fiction', 'Seasonal', 'Slice of life', 'Superhero', 'Surreal', 'Travel', 'Western']

    LICENSES = ['Freeware', 'Shareware', 'Public Domain', 'Commercial', 'GPL', 'BSD', 'Creative Commons']

    def __init__(self, url, title, author, release, desc, platform, cover, 
            game_id=None,
            language='en',
            license='Freeware',
            genre=''):
        self.url = url
        self.title = title
        self.author = author
        self.release = release
        self.desc = desc
        self.platform = platform
        self.cover = cover
        self.game_id = game_id
        # TODO: add language (default: en), license (default: Freeware), genre (how???)
        self.language = language
        self.license = license
        self.genre = genre

    def __repr__(self):
        formatting_string = """title: {0}
author: {1}
release: {2}
description: "{3}"
platform: {4}
language: {5}
license: {6}
genre: {7}""".format(self.title, self.author, self.release, self.desc.strip().split('\n')[0] + '...', self.platform, self.language, self.license, self.genre)
        return formatting_string

    def update_field(self, field, val):
        if field in ItchData.FIELDS and field != 'release':
            self.__dict__[field] = val
            return
        if field == 'release date' or field == 'release' or field == 'date':
            self.release = datetime.datetime.strptime(val, '%Y-%m-%d')
            return
        print('Warning: field "{0}" is unknown.'.format(field))
        return

    def correct_data(self):
        """
        Prompts for user correction of the fields.
        """
        print('Data from itch.io: ')
        print(str(self))
        is_correct = input('Is this correct? (Y/N) ').lower()
        while is_correct != 'y':
            field = input('Which field should be corrected? ').lower()
            while field not in self.FIELDS:
                field = input('Error: invalid field. Which field should be corrected? ').lower()
            if field == 'date' or field == 'release':
                val = input('Enter a date (as YYYY-MM-DD): ')
            elif field == 'platform':
                val = input("Enter a platform (Twine, Ink, Unity, ChoiceScript, Ren'Py, etc.): ")
            elif field == 'genre':
                val = input('Possible genres: ' + ', '.join(ItchData.GENRES) + ': ')
            elif field == 'license':
                val = input('Possible licenses: ' + ', '.join(ItchData.LICENSES) + ': ')
            else: 
                val = input('Enter the correct value: ')
            self.update_field(field, val)
            print('Updated self:')
            print(str(self))
            is_correct = input('Is this correct? (Y/N) ').lower()
        return self

    def to_json(self):
        return json.dumps({f: self.__dict__[f] for f in ItchData.FIELDS})

    @classmethod
    def from_json(json_text):
        data = json.loads(json_text)
        itch_data = ItchData(data['url'], data['title'], data['author'], data['release'],
                data['desc'], data['platform'], data['cover'], data['game_id'])
        return itch_data



