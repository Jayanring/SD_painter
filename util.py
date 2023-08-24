import os
import io
import hashlib
import cv2
import math
import base64
from rembg import remove, new_session
from dotenv import load_dotenv
from PIL import Image

load_dotenv()


def get_url():
    return os.environ.get('SD_URL')


def cal_size(sum, image):
    width, height = image.size
    return int(math.sqrt(sum * width / height)), int(math.sqrt(sum * height / width))


def file_to_base64(path):
    img = cv2.imread(path)
    _, bytes = cv2.imencode('.png', img)
    encoded_image = base64.b64encode(bytes).decode('utf-8')
    return encoded_image


def base64_to_file(encoded_image, file_name, save_dir='outputs', pnginfo=None):
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)

    image = base64_to_image(encoded_image)
    image_to_file(image, file_name, save_dir, pnginfo)


def image_to_file(image, file_name, save_dir='outputs', pnginfo=None):
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)

    image.save(f'{save_dir}/{file_name}.png', pnginfo=pnginfo)


def base64_to_image(encoded_image):
    return Image.open(io.BytesIO(base64.b64decode(encoded_image.split(",", 1)[0])))


def seg_raw_person(input_image):
    removed = remove(input_image, session=new_session(
        'u2net_human_seg'), bgcolor=(0, 0, 0, 0))
    return removed


def seg_repainted_person(input_image):
    removed = remove(input_image, session=new_session(
        'u2net'), bgcolor=(0, 0, 0, 0))
    return removed


def insert_to_background(background: Image.Image, person: Image.Image, position=(0, 0)):
    x, y = position
    background.paste(person, (x, y), person)
    return background


def get_history_seq():
    save_dir = 'outputs'
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)

    max_num = 0
    for filename in os.listdir(save_dir):
        seq = int(filename.split('_')[0])
        max_num = max(max_num, seq)

    return max_num


def calculate_md5(data):
    md5_hash = hashlib.md5()

    md5_hash.update(data.encode('utf-8'))

    return md5_hash.hexdigest()


def args_to_task(task_args):
    mode = task_args['mode']
    if mode == 'repaint' or mode == 'imitate':
        from repaint_task import RepaintTask
        task = RepaintTask(
            mode, task_args['style'], task_args['encoded_image'])
    else:
        raise ValueError('not support mode')

    return task
