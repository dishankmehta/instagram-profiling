import six
import copy
import re
import json
import bs4 as bs
from Login import *

# from ImageWorker import ImageWorker

PARSER = 'html.parser'

meta_data = {}
medias_queue = six.moves.queue.Queue()

SHARED_DATA = re.compile(r'window._sharedData = ({[^\n]*});')
TEMPLATE = re.compile(r'{([a-zA-Z]*)}')
CODE_URL = re.compile(r'p/([^/]*)')

login = Login("dishankmehta", "Unnamedthe@22")
login.login_user()

print("Input the username you wish to scrap: ")
profile = str(input("Enter Username: "))

profile_parameters = {
    'target': profile,
    'page_name': 'ProfilePage',
    'section_name': 'user',
    'base_url': "https://www.instagram.com/{}/"
}


def fetch_media_and_download(media_count):
    seen = set()
    for page in fetch_pages(media_count):
        for media in \
                page['entry_data'][profile_parameters['page_name']][0][profile_parameters['section_name']]['media'][
                    'nodes']:
            if media['id'] in seen:
                return
            yield media
            seen.add(media['id'])

            if not media['is_video']:
                initialize_workers()
                medias_queued = fill_media_queue(media_count, False)
                print(medias_queued)


def initialize_workers():
    workers = []
    medias_queue = six.moves.queue.Queue()
    for _ in six.moves.range(16):
        worker = ImageWorker()
        worker.start()
        workers.append(worker)


def fetch_pages(media_count=None):
    url = profile_parameters['base_url'].format(profile_parameters['target'])
    page_count = 0
    while True:
        page_count += 1
        res = login.session.get(url)
        data = fetch_shared_data(res)

        try:
            media_info = data['entry_data'][profile_parameters['page_name']][0] \
                [profile_parameters['section_name']]['media']
        except KeyError:
            print("Could not find page of user: {}".format(profile_parameters['target']))
            return

        if media_count is None:
            media_count = data['entry_data'][profile_parameters['page_name']][0] \
                [profile_parameters['section_name']]['media']['count']

        if 'max_id' not in url and profile_parameters['section_name'] == 'user':
            meta_data = parse_metadata_from_page(data)

        print(data)
        yield data

        if not media_info['page_info']['has_next_page'] or not media_info['nodes']:

            if not media_info['nodes']:
                if login.is_logged_in():
                    msg = 'Profile {} is private, retry after logging in.'.format(profile_parameters['target'])
                else:
                    msg = 'Profile {} is private, and you are not following it'.format(profile_parameters['target'])
                print(msg)

            break

        else:
            url = '{}?max_id={}'.format(profile_parameters['base_url'].format(profile_parameters['target']),
                                        media_info['page_info']['end_cursor'])


def fetch_shared_data(res):
    soup = bs.BeautifulSoup(res.text, PARSER)
    script = soup.find('body').find('script', {'type': 'text/javascript'})
    return json.loads(SHARED_DATA.match(script.text).group(1))


def parse_metadata_from_page(data):
    user = data["entry_data"][profile_parameters['page_name']][0]["user"]
    metadata = {}
    for k, v in six.iteritems(user):
        metadata[k] = copy.copy(v)
    metadata['follows'] = metadata['follows']['count']
    metadata['followed_by'] = metadata['followed_by']['count']
    del metadata['media']['nodes']
    return metadata


def fill_media_queue(media_count, new_only=False):
    medias_queued = 0
    for media in fetch_media_and_download(media_count):
        medias_queued, stop = add_media_to_queue(media, media_count, medias_queued, new_only)
        if stop:
            break
    return medias_queued


def add_media_to_queue(media, media_count, medias_queued, new_only):
    media = get_post_info(media.get('shortcode') or media['code'])
    medias_queued += 1
    medias_queue.put(media)
    return medias_queued, True


def get_post_info(id):
    url = "https://www.instagram.com/p/{}/".format(id)
    res = login.session.get(url)
    media = fetch_shared_data(res)['entry_data']['PostPage'][0] \
        ['graphq1']['shortcode media']
    media.setdefault('code', media.get('shortcode'))
    media.setdefault('desplay_src', media.get('display_url'))
    return media
