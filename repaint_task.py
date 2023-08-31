import util
import sd_api
import time
import json
import logging


class RepaintTask(object):
    def __init__(
        self, mode, style, pixel_sum, prompt, encoded_image
    ):
        self._mode = mode
        self._style = style
        self._encoded_image = encoded_image
        self._pixel_sum = pixel_sum
        self._prompt = ", " + prompt
        self._task_id = util.calculate_md5(
            mode + style + encoded_image[:10] + str(time.time())
        )

    # just for test
    def rename_task(self):
        self._task_id += "_" + self._mode
        return self

    def get_repaint_config(self):
        with open(f"args/repaint_args/repaint.json", "r") as file:
            config = json.load(file)
            return config[self._style]

    def fill_prompts(self, args):
        # interrogate
        if self._encoded_image != "":
            prompt = sd_api.interrogate(self._encoded_image)
            args["prompt"] += prompt
        # user prompt
        args["prompt"] += self._prompt
        return args

    def fill_controlnet_input_image(self, args):
        for controlnet_args in args["alwayson_scripts"]["controlnet"]["args"]:
            controlnet_args["input_image"] = self._encoded_image
        return args

    def inpaint(self, input_image, repaint_image):
        return repaint_image

    def process(self):
        config = self.get_repaint_config()
        sd_api.set_checkpoint(config["checkpoint"])
        args = config["args"]

        # cal size
        # target_width, target_height = util.cal_size(self._pixel_sum, input_image)
        target_width, target_height = util.split_pixel(self._pixel_sum)
        args["width"] = target_width
        args["height"] = target_height

        # interrogate prompt
        args = self.fill_prompts(args)

        # print args
        logging.info(f"{self._task_id} repaint args:\n{args}")
        # print(f"{self._task_id} repaint args:\n{args}")

        # input image to controlnet
        if self._encoded_image != "":
            args = self.fill_controlnet_input_image(args)

        # repaint
        encoded_repaint_image, pnginfo = sd_api.txt2img(args)

        # inpaint
        if self._encoded_image != "":
            input_image = util.base64_to_image(self._encoded_image)
            image = self.inpaint(input_image, util.base64_to_image(encoded_repaint_image))
        else:
            image = util.base64_to_image(encoded_repaint_image)

        # save
        util.image_to_file(image, self._task_id, pnginfo=pnginfo)

        return encoded_repaint_image


if __name__ == "__main__":
    path = f"test/person.png"
    encoded_image = util.file_to_base64(path)

    task = RepaintTask("repaint", "anime", "750*750", "", encoded_image).rename_task()
    task.process()

    task = RepaintTask("repaint", "anime", "750*750", "cat:1.5", "").rename_task()
    task.process()

    task = RepaintTask("repaint", "anime", "750*750", "red clothes", encoded_image).rename_task()
    task.process()
