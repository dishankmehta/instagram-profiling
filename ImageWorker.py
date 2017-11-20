import contextlib
import threading
from Login import *
from Main import *
from urllib.parse import urlparse
import os


DEFAULT_RX = re.compile(r'(https://.*?/.*?/).*(/.*\.jpg)')
NEW_DEFAULT_RX = re.compile(r'(https://.*?/h-ak-igx/).*(/.*\.jpg)')
DIRECTORY = 'C:/Users/malay/Documents/instagram'


class ImageWorker(threading.Thread):

    def __init__(self, parent):
        super(ImageWorker, self).__init__()
        self.medias = parent.medias_queue
        self.target = parent.profile_parameters['target']
        self._killed = False
        self.session = requests.session()
        self.parent = parent
        self.session.cookies = self.parent.login.session.cookies


    #parent = Login()
    def run(self):
        while not self._killed:
            #try:
                media = self.medias.get()
                #print(media)
                if media == None:
                    break
                else:
                    self.download(media)
            #except KeyError:
            #    print('KeyError in Worker')

    def download(self, media):
        source = media['display_src']
        #print(source)
        user_folder = os.path.join(DIRECTORY, self.target)
        if not os.path.exists(user_folder):
            os.mkdir(user_folder)
        parsed_source = urlparse(source)
        #print(parsed_source)
        filename = os.path.join(user_folder, str(os.path.basename(parsed_source.path)))

        #download the photo
        self.session.headers['Accept'] = '*/*'
        with contextlib.closing(self.session.get(source)) as res:
            dest_file = open(filename, 'wb')
            for block in res.iter_content(1024):
                if block:
                    dest_file.write(block)

    def kill(self):
        """kill the thread
        """

        self._killed = True
