import PIL.Image
import requests
import re
import six
import os
import json
import threading


class ImageWorker(threading.Thread):

    def __init__(self):

