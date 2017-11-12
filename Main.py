import os
import re
import json
import bs4 as bs
from Login import *

PARSER = 'html.parser'

SHARED_DATA = re.compile(r'window._sharedData = ({[^\n]*});')
TEMPLATE = re.compile(r'{([a-zA-Z]*)}')
CODE_URL = re.compile(r'p/([^/]*)')

login = Login("dishankmehta", "Unnamedthe@22")
login.login_user()

print("Input the username you wish to scrap: ")
profile = str(input())

profile_parameters = {
    'target': profile,
    'page_name': 'ProfilePage',
    'section_name': 'user',
    'base_url': "https://www.instagram.com/{}/"
}


def fetch_pages():
    url = profile_parameters['base_url'].format(profile_parameters['target'])
    page_count = 0
    while True:
        page_count += 1
        res = login.session.get(url)
        data = fetch_shared_data(res)

        try:
            media_info = data['entry_data'][profile_parameters['page_name']][0][profile_parameters['section_name']]['media']
        except KeyError:
            warnings.warn("Could not find page of user: {}".format(profile_parameters['target']), stacklevel=1)
            return


def fetch_shared_data(res):
    soup = bs.BeautifulSoup(res.text, PARSER)
    script = soup.find('body').find('script',{'type' : 'text/javascript'})
    return json.loads(SHARED_DATA.match(script.text).group(1))
