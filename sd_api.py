import io
import base64
import requests
import util
from PIL import Image, PngImagePlugin


def set_checkpoint(model):
    result = requests.get(url=f'{util.get_url()}/sdapi/v1/options').json()
    if result['sd_model_checkpoint'] == model:
        return
    option_payload = {
        "sd_model_checkpoint": model
    }
    requests.post(url=f'{util.get_url()}/sdapi/v1/options',
                  json=option_payload)


def interrogate(encoded_image):
    interrogate_payload = {
        "image": encoded_image,
        "model": "deepdanbooru"
    }
    result: str = requests.post(
        url=f'{util.get_url()}/sdapi/v1/interrogate', json=interrogate_payload).json()['caption']
    result = ', ' + result
    result = result.replace(', beard', '').replace(', mustache', '').replace(
        ', facial hair', '').replace(', old', '').replace(', old man', '')

    return result


def get_pnginfo(encoded_image):
    png_payload = {
        "image": "data:image/png;base64," + encoded_image
    }
    response2 = requests.post(
        url=f'{util.get_url()}/sdapi/v1/png-info', json=png_payload)
    pnginfo = PngImagePlugin.PngInfo()
    pnginfo.add_text("parameters", response2.json().get("info"))

    return pnginfo


def txt2img(args):
    response = requests.post(
        url=f'{util.get_url()}/sdapi/v1/txt2img', json=args)

    r = response.json()
    encoded_image = r['images'][0]

    image = util.base64_to_image(encoded_image)
    pnginfo = get_pnginfo(encoded_image)

    return image, pnginfo
