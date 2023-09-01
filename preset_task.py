import util
import time
import json
from PIL import Image


class PresetBackgroundTask(object):
    def __init__(self, mode, style, pixel, encoded_image, preset_name):
        self._mode = mode
        self._style = style
        self._pixel = pixel
        self._encoded_image = encoded_image
        self._preset_name = preset_name
        self._task_id = util.calculate_md5(
            mode + style + encoded_image[:10] + str(time.time())
        )

    # just for test
    def rename_task(self):
        self._task_id += "_" + self._mode
        return self

    def process(self):
        # resize
        target_width, target_height = util.split_pixel(self._pixel)
        image = util.base64_to_image(self._encoded_image)
        image = image.resize((target_width, target_height), Image.LANCZOS)

        # save image
        util.image_to_file(image, self._preset_name, "args/merge_args/")

        # write json
        with open(f"args/merge_args/style_map.json", "r") as file:
            config = json.load(file)

        config[f"{self._preset_name}"] = f"{self._style}"

        with open(f"args/merge_args/style_map.json", "w") as file:
            json.dump(config, file, indent=4)

        return None


if __name__ == "__main__":
    path = f"test/background.png"
    encoded_image = util.file_to_base64(path)

    task = PresetBackgroundTask(
        "repaint", "wjj", "300*300", encoded_image, "duanqiao"
    ).rename_task()
    task.process()
