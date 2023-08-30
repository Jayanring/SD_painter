import util
import sd_api
import time
import json


class PresetBackgroundTask(object):
    def __init__(self, mode, style, encoded_image, preset_name):
        self._mode = mode
        self._style = style
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
        # save image
        util.base64_to_file(self._encoded_image, self._preset_name, "args/merge_args/")

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
        "repaint", "wjj", encoded_image, "duanqiao"
    ).rename_task()
    task.process()
