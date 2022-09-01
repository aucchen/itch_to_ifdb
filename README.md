This is a simple script for uploading itch.io games to ifdb. There are different pipelines that use either selenium or the [putific](https://ifdb.org/api/putific) API; the API does not seem to be working on ifdb.org, so I'm using selenium right now.

## Requirements

- Python 3
- [selenium](https://selenium-python.readthedocs.io/index.html), with [firefox webdriver](https://github.com/mozilla/geckodriver/releases)
- [selectolax](https://github.com/rushter/selectolax)
- [lxml](https://lxml.de/)
- [requests](https://requests.readthedocs.io/en/latest/)
- ImageMagick (for resizing cover images)

## Instructions

`python itch_to_ifdb.py`
