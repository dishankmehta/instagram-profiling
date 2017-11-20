import six
import copy
import re
import json
import bs4 as bs
from Login import Login
from ImageWorker import ImageWorker


class Main:
    PARSER = 'html.parser'

    meta_data = {}
    medias_queue = six.moves.queue.Queue()
    workers = []
    media_count = None
    global_medias_queued = 0

    SHARED_DATA = re.compile(r'window._sharedData = ({[^\n]*});')
    TEMPLATE = re.compile(r'{([a-zA-Z]*)}')
    CODE_URL = re.compile(r'p/([^/]*)')

    login = Login("malay1995", "mmhh1814")
    login.login_user()

    print("Input the username you wish to scrap: ")
    profile = str(input("Enter Username: "))

    profile_parameters = {
        'target': profile,
        'page_name': 'ProfilePage',
        'section_name': 'user',
        'base_url': "https://www.instagram.com/{}/"
    }

    #print(profile_parameters)

    def fetch_media_and_download(self):
        self.initialize_workers()
        medias_queued = self.fill_media_queue(False)
        print("Medias Queued: " + str(medias_queued))
        self.remove_worker()

    def media_iterator(self):
        seen = set()
        for page in self.fetch_pages():
            for media in page['entry_data'][self.profile_parameters['page_name']][0] \
                    [self.profile_parameters['section_name']]['media']['nodes']:
                if media['id'] in seen:
                    return
                yield media
                seen.add(media['id'])

    def return_medias(self):
        return self.media_iterator()

    def initialize_workers(self):
        self.workers = []
        self.medias_queue = six.moves.queue.Queue()
        for _ in six.moves.range(16):
            worker = ImageWorker(self)
            worker.start()
            self.workers.append(worker)

    def fetch_pages(self):
        url = self.profile_parameters['base_url'].format(self.profile_parameters['target'])
        page_count = 0
        while True:
            page_count += 1
            res = self.login.session.get(url)
            data = self.fetch_shared_data(res)
            try:
                media_info = data['entry_data'][self.profile_parameters['page_name']][0] \
                    [self.profile_parameters['section_name']]['media']
            except KeyError:
                print("Could not find page of user: {}".format(self.profile_parameters['target']))
                return

            if self.media_count is None:
                self.media_count = data['entry_data'][self.profile_parameters['page_name']][0] \
                    [self.profile_parameters['section_name']]['media']['count']
                print("Media count: " + str(self.media_count))

            if 'max_id' not in url and self.profile_parameters['section_name'] == 'user':
                meta_data = self.parse_metadata_from_page(data)

            yield data

            if not media_info['page_info']['has_next_page'] or not media_info['nodes']:

                if not media_info['nodes']:
                    if self.login.is_logged_in():
                        msg = 'Profile {} is private, retry after logging in.'.format(self.profile_parameters['target'])
                    else:
                        msg = 'Profile {} is private, and you are not following it'.format(
                            self.profile_parameters['target'])
                    print(msg)
                print('Breaking')
                break

            else:
                url = '{}?max_id={}'.format(
                    self.profile_parameters['base_url'].format(self.profile_parameters['target']),
                    media_info['page_info']['end_cursor'])
                print("Else url: " + url)

    def fetch_shared_data(self, res):
        soup = bs.BeautifulSoup(res.text, self.PARSER)
        script = soup.find('body').find('script', {'type': 'text/javascript'})
        return json.loads(self.SHARED_DATA.match(script.text).group(1))

    def parse_metadata_from_page(self, data):
        user = data["entry_data"][self.profile_parameters['page_name']][0]["user"]
        metadata = {}
        for k, v in six.iteritems(user):
            metadata[k] = copy.copy(v)
        metadata['follows'] = metadata['follows']['count']
        metadata['followed_by'] = metadata['followed_by']['count']
        del metadata['media']['nodes']
        return metadata

    def fill_media_queue(self, new_only=False):
        medias_queued = 0
        for media in self.return_medias():
            medias_queued, stop = self.add_media_to_queue(media, medias_queued, new_only)
            if stop:
                break
        return medias_queued

    def add_media_to_queue(self, media, medias_queued, new_only):
        media = self.get_post_info(media.get('shortcode') or media['code'])
        medias_queued += 1
        self.medias_queue.put(media)
        if medias_queued == self.media_count:
            return medias_queued, True
        return medias_queued, False

    def get_post_info(self, id):
        url = "https://www.instagram.com/p/{}/".format(id)
        res = self.login.session.get(url)
        media = self.fetch_shared_data(res)['entry_data']['PostPage'][0] \
            ['graphql']['shortcode_media']
        media.setdefault('code', media.get('shortcode'))
        media.setdefault('display_src', media.get('display_url'))
        return media

    def remove_worker(self):
        for _ in self.workers:
            self.medias_queue.put(None)
