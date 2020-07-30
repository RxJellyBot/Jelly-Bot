import base64

import requests


class ImageContentProcessor:
    @staticmethod
    def online_img_to_base64_str(url: str) -> str:
        return base64.b64encode(requests.get(url).content).decode("utf-8")

    @staticmethod
    def local_img_to_base64_str(path: str) -> str:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
