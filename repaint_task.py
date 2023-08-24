import util
import sd_api
import time
import json
import os
from main import app


def get_repaint_pixel_sum():
    return int(os.environ.get('REPAINT_PIXEL_SUM'))


class RepaintTask(object):
    def __init__(self, mode, style, encoded_image, pixel_sum=get_repaint_pixel_sum()):
        self._mode = mode
        self._style = style
        self._encoded_image = encoded_image
        self._pixel_sum = pixel_sum
        self._task_id = util.calculate_md5(
            mode + style + encoded_image[:10] + str(time.time()))

    # just for test
    def rename_task(self):
        self._task_id += '_' + self._mode
        return self

    def get_repaint_config(self):
        with open(f'args/repaint_args/repaint.json', 'r') as file:
            config = json.load(file)
            return config[self._style]

    def interrogate(self, args):
        prompt = sd_api.interrogate(self._encoded_image)
        args['prompt'] += prompt
        return args

    def fill_controlnet_input_image(self, args):
        for controlnet_args in args['alwayson_scripts']['controlnet']['args']:
            controlnet_args['input_image'] = self._encoded_image
        return args

    def inpaint(self, input_image, repaint_image):
        return repaint_image

    def process(self):
        config = self.get_repaint_config()
        sd_api.set_checkpoint(config['checkpoint'])

        args = config['args']
        # cal size
        input_image = util.base64_to_image(self._encoded_image)
        target_width, target_height = util.cal_size(
            self._pixel_sum, input_image)
        args['width'] = target_width
        args['height'] = target_height

        # interrogate prompt
        args = self.interrogate(args)

        # print args
        print(f'repaint args: {args}')

        # input image to controlnet
        args = self.fill_controlnet_input_image(args)

        # repaint
        repaint_image, pnginfo = sd_api.txt2img(args)

        # inpaint
        image = self.inpaint(input_image, repaint_image)

        # save
        util.image_to_file(image, self._task_id, pnginfo=pnginfo)

        return image, pnginfo


if __name__ == '__main__':
    path = f'test/person.png'
    encoded_image = util.file_to_base64(path)

    task = RepaintTask('repaint', 'anime', encoded_image).rename_task()
    task.process()
