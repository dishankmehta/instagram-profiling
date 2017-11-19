import os
from pathlib import Path
from glob import glob
import subprocess


project_path = Path(os.path.abspath(os.curdir))
parent_path = project_path.parent

instagram_images_dir = os.path.join(parent_path.parent, 'instagram')
os.chdir(instagram_images_dir)
image_folders = []

if os.path.exists(instagram_images_dir):
    image_folders = glob('*/')
    print(image_folders)

vedant_folder = image_folders[4]

path_new = os.path.abspath(os.curdir)
vedant_images = os.path.join(path_new, vedant_folder)
os.chdir(vedant_images)
vedant_images_path = os.path.abspath(os.curdir)
print(os.path.abspath(os.curdir))
project_path = 'C:/Users/Dishank/Documents/GitHub/models-master/tutorials/image/imagenet'
print(project_path)

for name in vedant_images_path:
    process = subprocess.Popen('python {}/classify_image.py --imsge_file={}'.format(project_path, name))
    out, err = process.communicate()
    print(out)
    print(err)

#os.chdir(project_path)

