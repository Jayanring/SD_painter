import util
from PIL import Image
from repaint_task import RepaintTask


class InpaintBackgroundTask(RepaintTask):
    def inpaint(self, input_image: Image.Image, repaint_image: Image.Image):
        # resize
        target_width, target_height = repaint_image.size
        input_image = input_image.resize((target_width, target_height), Image.LANCZOS)

        # segment person
        person = util.seg_raw_person(input_image)

        # insert to background
        inpainted = util.insert_to_background(repaint_image, person)

        return inpainted


class InpaintPersonTask(RepaintTask):
    def inpaint(self, input_image: Image.Image, repaint_image: Image.Image):
        # resize
        target_width, target_height = repaint_image.size
        input_image = input_image.resize((target_width, target_height), Image.LANCZOS)

        # segment person
        person = util.seg_repainted_person(repaint_image)

        # insert to background
        inpainted = util.insert_to_background(input_image, person)

        return inpainted


if __name__ == "__main__":
    path = f"scripts/merge_test/person.png"
    encoded_image = util.file_to_base64(path)

    task = InpaintBackgroundTask(
        "inpaint_background", "anime", encoded_image
    ).rename_task()
    task.process()

    task = InpaintPersonTask("inpaint_person", "anime", encoded_image).rename_task()
    task.process()
