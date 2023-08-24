from repaint_task import RepaintTask
import json
import time
import util
import os
from PIL import Image

# merge two images, one provides person, one provides background


def get_merge_background_pixel_sum():
    return int(os.environ.get('MERGE_BACKGROUND_PIXEL_SUM'))


def get_merge_person_ratio():
    return float(os.environ.get('MERGE_PERSON_RATIO'))


def trim_seg(input_image):
    if input_image.mode in ('RGBA', 'LA'):
        # 获取图像的宽度和高度
        width, height = input_image.size

        # 寻找左边界（第一个 alpha 通道不为 0 的列）
        left_bound = 0
        for x in range(width):
            if any(input_image.getpixel((x, y))[3] != 0 for y in range(height)):
                left_bound = x
                break

        # 寻找上边界（第一个 alpha 通道不为 0 的行）
        top_bound = 0
        for y in range(height):
            if any(input_image.getpixel((x, y))[3] != 0 for x in range(width)):
                top_bound = y
                break

        # 寻找右边界（最后一个 alpha 通道不为 0 的列）
        right_bound = width - 1
        for x in range(width - 1, -1, -1):
            if any(input_image.getpixel((x, y))[3] != 0 for y in range(height)):
                right_bound = x
                break

        # 寻找下边界（最后一个 alpha 通道不为 0 的行）
        bottom_bound = height - 1
        for y in range(height - 1, -1, -1):
            if any(input_image.getpixel((x, y))[3] != 0 for x in range(width)):
                bottom_bound = y
                break

        # 裁剪图像，去掉 alpha 通道全为 0 的行和列
        output_image = input_image.crop(
            (left_bound, top_bound, right_bound + 1, bottom_bound + 1))

        return output_image


def adjust_person_size(background: Image.Image, person: Image.Image):
    ratio = get_merge_person_ratio()

    b_width, b_height = background.size
    p_width, p_height = person.size

    width_ratio = p_width / b_width
    height_ratio = p_height / b_height

    if width_ratio > height_ratio:
        target_width = int(b_width * ratio)
        target_height = int(target_width / p_width * p_height)
    else:
        target_height = int(b_height * ratio)
        target_width = int(target_height / p_height * p_width)

    resized_person = person.resize(
        (target_width, target_height), Image.LANCZOS)

    return resized_person, int(0.5 * (b_width - target_width)), b_height - target_height


class MergeTask(object):
    def __init__(self, mode, style, person_encoded, background_encoded=None):
        self._mode = mode
        self._style = style
        self._person_encoded = person_encoded
        self._background_encoded = background_encoded
        self._task_id = util.calculate_md5(
            mode + style + person_encoded[:10] + str(time.time()))

    # just for test
    def rename_task(self):
        self._task_id += '_' + self._mode
        return self

    def get_repaint_style(self):
        return self._style

    def repaint(self, encoded_image, is_background):
        if is_background:
            repaint_task = RepaintTask('repaint', self.get_repaint_style(
            ), encoded_image, get_merge_background_pixel_sum())
            repaint_task._task_id = self._task_id + '_repaint_background'
        else:
            repaint_task = RepaintTask(
                'repaint', self.get_repaint_style(), encoded_image)
            repaint_task._task_id = self._task_id + '_repaint_person'
        image, _ = repaint_task.process()
        return image

    def process_person(self):
        return util.base64_to_image(self._person_encoded)

    def seg_person(self, person):
        return trim_seg(util.seg_raw_person(person))

    def get_background(self):
        return util.base64_to_image(self._background_encoded)

    def process_background(self):
        background = self.get_background()
        return background

    def process(self):
        # process person
        person = self.process_person()

        # segment person
        person_seg = self.seg_person(person)

        # process background
        background = self.process_background()

        # resize
        resized_person_seg, x, y = adjust_person_size(background, person_seg)

        # insert
        inserted_person = util.insert_to_background(
            background, resized_person_seg, (x, y))

        # todo: img2img to smooth the edge

        # save
        util.image_to_file(inserted_person, self._task_id)


class MergeBuiltinTask(MergeTask):
    def get_background(self):
        return Image.open('args/merge_args/' + self._style + '.png')


class MergeBuiltinRepaintTask(MergeBuiltinTask):
    def get_repaint_style(self):
        with open(f'args/merge_args/style_map.json', 'r') as file:
            config = json.load(file)
            return config[self._style]

    def process_person(self):
        return self.repaint(self._person_encoded, False)

    def seg_person(self, person):
        return trim_seg(util.seg_repainted_person(person))


class MergeRepaintPersonTask(MergeTask):
    def process_person(self):
        return self.repaint(self._person_encoded, False)

    def seg_person(self, person):
        return trim_seg(util.seg_repainted_person(person))


class MergeRepaintBackgroundTask(MergeTask):
    def process_background(self):
        return self.repaint(self._background_encoded, True)


class MergeRepaintBothTask(MergeRepaintPersonTask, MergeRepaintBackgroundTask):
    pass


if __name__ == '__main__':
    path = f'test/person.png'
    encoded_person = util.file_to_base64(path)

    task = MergeBuiltinTask('merge_builtin', 'xihu',
                            encoded_person).rename_task()
    task.process()

    task = MergeBuiltinRepaintTask(
        'merge_builtin_repaint', 'xihu', encoded_person).rename_task()
    task.process()

    background_path = f'test/background.png'
    encoded_background = util.file_to_base64(background_path)

    task = MergeTask('merge', '', encoded_person,
                     encoded_background).rename_task()
    task.process()

    task = MergeRepaintPersonTask(
        'merge_repaint_person', 'anime', encoded_person, encoded_background).rename_task()
    task.process()

    task = MergeRepaintBackgroundTask(
        'merge_repaint_background', 'anime', encoded_person, encoded_background).rename_task()
    task.process()

    task = MergeRepaintBothTask(
        'merge_repaint_both', 'anime', encoded_person, encoded_background).rename_task()
    task.process()
