import os
from pathlib import Path
from glob import glob
import subprocess
import re
import json
from Main import *


project_path = Path(os.path.abspath(os.curdir))
parent_path = project_path.parent

instagram_images_dir = os.path.join(str(parent_path.parent), 'instagram')
os.chdir(instagram_images_dir)
image_folders = []

main = Main()
"""
main.fetch_media_and_download()
"""
if os.path.exists(instagram_images_dir):
    image_folders = glob('*/')

target = main.profile_parameters['target']
s = target + "\\"
for item in image_folders:
    if str(item) == s:
        vedant_folder = item

path_new = os.path.abspath(os.curdir)
vedant_images = os.path.join(path_new, vedant_folder)
os.chdir(vedant_images)
vedant_images_path = os.path.abspath(os.curdir)
print(os.path.abspath(os.curdir))
project_path = 'C:/Users/malay/Documents/GitHub/models-master/tutorials/image/imagenet'
#command = 'python ' + project_path = '/classify_image.py'
with open('C:/Users/malay/Documents/GitHub/instagram-profiling/classes.txt' , 'a') as f:
    for name in os.listdir(vedant_images_path):
        print(name)
        process = subprocess.check_output('python {}/classify_image.py --image_file={}'.format(project_path, name))
        process = process.decode("utf-8")
        list_objects = process.split("\n")
        label = []
        score = []
        num_pattern = re.compile(r'\d+\.\d+')
        for item in list_objects:
            item1 = item.split('(')
            label.append(item1[0])
            score.append(num_pattern.findall(item))
        objects = dict(zip(label,score))
        f.write(str(objects)+"\n")
    f.close()
    #print(err)
#os.chdir(project_path)

