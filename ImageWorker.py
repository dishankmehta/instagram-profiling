import PIL.Image
import requests
import re
import six
import os
import json
import threading
from Login import *
import Main
import urllib


DEFAULT_RX = re.compile(r'(https://.*?/.*?/).*(/.*\.jpg)')
NEW_DEFAULT_RX = re.compile(r'(https://.*?/h-ak-igx/).*(/.*\.jpg)')
DIRECTORY = 'C:/users/malay/Documents/instagram/'


class ImageWorker(threading.Thread):

    def __init__(self):
        super(ImageWorker,self).__init__()
        self.medias = Main.medias_queue
        self.target = Main.profile_parameters['target']
        self._killed = False
        self.session = requests.session()
        self.cookies = self.session.cookies

    count = 1
    parent = Login()
    def run(self):
        while not self._killed:
            try:
                media = self.medias.get(timeout = 1)
                if media == None:
                    break
                else:
                    self.download(media)

    def download(self,media):
        source = NEW_DEFAULT_RX.search(media['display_src'])
        dest = DIRECTORY + self.target + '/'
        filename = os.path.join(dest,str(self.count)+'.jpg')
        self.count = self.count + 1

        #download the photo
        self.session.headers['Accept'] = '*/*'
        with open(filename, 'wb') as f:
            f.write(urllib.urlopen(source).read())
            f.close()

    def kill(self):
        """kill the thread
        """

        self._killed = True
        