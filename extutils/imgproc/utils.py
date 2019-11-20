import base64

import requests


class ImageContentProcessor:
    @staticmethod
    def online_img_to_base64(url: str) -> str:
        return base64.b64encode(requests.get(url).content)
