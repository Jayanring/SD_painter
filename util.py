import os
import io
import hashlib
import cv2
import math
import base64
from rembg import remove, new_session
from PIL import Image
from dotenv import load_dotenv
import logging

load_dotenv()


def sd_url():
    return os.environ.get("SD_URL")


def get_task_url():
    return os.environ.get("GET_TASK_URL")


def submit_task_url():
    return os.environ.get("SUBMIT_TASK_URL")


def get_repaint_pixel_sum():
    return int(os.environ.get("REPAINT_PIXEL_SUM"))


def get_merge_background_pixel_sum():
    return int(os.environ.get("MERGE_BACKGROUND_PIXEL_SUM"))


def get_merge_person_ratio():
    return float(os.environ.get("MERGE_PERSON_RATIO"))


def cal_size(sum, image):
    width, height = image.size
    return int(math.sqrt(sum * width / height)), int(math.sqrt(sum * height / width))


def file_to_base64(path):
    img = cv2.imread(path)
    _, bytes = cv2.imencode(".png", img)
    encoded_image = base64.b64encode(bytes).decode("utf-8")
    return encoded_image


def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    encoded_image = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return encoded_image


def base64_to_file(encoded_image, file_name, save_dir="outputs/result/", pnginfo=None):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    image = base64_to_image(encoded_image)
    image_to_file(image, file_name, save_dir, pnginfo)


def image_to_file(image, file_name, save_dir="outputs/result/", pnginfo=None):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    image.save(f"{save_dir}/{file_name}.png", pnginfo=pnginfo)


def base64_to_image(encoded_image):
    return Image.open(io.BytesIO(base64.b64decode(encoded_image.split(",", 1)[0])))


def seg_raw_person(input_image):
    removed = remove(
        input_image, session=new_session("u2net_human_seg"), bgcolor=(0, 0, 0, 0)
    )
    return removed


def seg_repainted_person(input_image):
    removed = remove(input_image, session=new_session("u2net"), bgcolor=(0, 0, 0, 0))
    return removed


def insert_to_background(background: Image.Image, person: Image.Image, position=(0, 0)):
    x, y = position
    background.paste(person, (x, y), person)
    return background


def get_history_seq():
    save_dir = "outputs"
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)

    max_num = 0
    for filename in os.listdir(save_dir):
        seq = int(filename.split("_")[0])
        max_num = max(max_num, seq)

    return max_num


def calculate_md5(data):
    md5_hash = hashlib.md5()

    md5_hash.update(data.encode("utf-8"))

    return md5_hash.hexdigest()


def args_to_task(task_args):
    mode = task_args["drawMode"]
    id = task_args["id"]
    style = task_args["style"]
    pixel = task_args["pixel"]
    if mode == "RepaintTask":
        logging.info(f"get RepaintTask: style: {style}, id: {id}")
        from repaint_task import RepaintTask

        task = RepaintTask(mode, style, task_args["encodedImageBase64"], pixel)

    elif mode == "MergeBuiltinRepaintTask":
        use_image = task_args["presetName"]
        logging.info(
            f"get MergeBuiltinRepaintTask: style: {style}, id: {id}, presetName: {use_image}"
        )
        from merge_task import MergeBuiltinRepaintTask

        task = MergeBuiltinRepaintTask(
            mode, use_image, task_args["encodedImage1Base64"]
        )

    elif mode == "MergeRepaintBothTask":
        logging.info(f"get MergeRepaintBothTask: style: {style}, id: {id}")
        from merge_task import MergeRepaintBothTask

        task = MergeRepaintBothTask(
            mode,
            style,
            task_args["encodedImage1Base64"],
            task_args["encodedImageBase64"],
        )

    elif mode == "PresetBackgroundTask":
        logging.info(f"get PresetBackgroundTask: style: {style}, id: {id}")
        from preset_task import PresetBackgroundTask

        task = PresetBackgroundTask(
            mode, style, task_args["encodedImageBase64"], task_args["presetName"]
        )
    else:
        raise ValueError(f"not support mode: {mode}")

    task._task_id = id + "_" + mode
    task._id = id

    # save raw image
    if "encodedImageBase64" in task_args:
        base64_to_file(
            task_args["encodedImageBase64"],
            task._task_id + "_background",
            "outputs/raw/",
        )
    if "encodedImage1Base64" in task_args:
        base64_to_file(
            task_args["encodedImage1Base64"], task._task_id + "_person", "outputs/raw/"
        )
    return task


if __name__ == "__main__":
    encoded1 = file_to_base64("test/background.png")
    image = base64_to_image(encoded1)
    encoded2 = image_to_base64(image)
    base64_to_file(encoded1, "encoded1", ".")
    base64_to_file(encoded2, "encoded2", ".")
