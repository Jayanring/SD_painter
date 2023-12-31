import requests
import util
from PIL import PngImagePlugin


def set_checkpoint(model):

    option_payload = {"sd_model_checkpoint": model, "CLIP_stop_at_last_layers": 2}
    requests.post(url=f"{util.sd_url()}/sdapi/v1/options", json=option_payload)


def interrogate(encoded_image):
    interrogate_payload = {"image": encoded_image, "model": "deepdanbooru"}
    result: str = requests.post(
        url=f"{util.sd_url()}/sdapi/v1/interrogate", json=interrogate_payload
    ).json()["caption"]
    result = ", " + result
    result = (
        result.replace(", beard", "")
        .replace(", mustache", "")
        .replace(", facial hair", "")
        .replace(", old", "")
        .replace(", old man", "")
        .replace(", 1girl", "")
        .replace(", 1boy", "")
        .replace(", lips", "")
    )

    return result


def get_pnginfo(encoded_image):
    png_payload = {"image": "data:image/png;base64," + encoded_image}
    response2 = requests.post(
        url=f"{util.sd_url()}/sdapi/v1/png-info", json=png_payload
    )
    pnginfo = PngImagePlugin.PngInfo()
    pnginfo.add_text("parameters", response2.json().get("info"))

    return pnginfo


def txt2img(args):
    response = requests.post(url=f"{util.sd_url()}/sdapi/v1/txt2img", json=args)

    r = response.json()
    encoded_image = r["images"][0]

    pnginfo = get_pnginfo(encoded_image)

    return encoded_image, pnginfo
