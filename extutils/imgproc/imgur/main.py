import os
import sys

import requests

from extutils.logger import SYSTEM

from .endpoints import ImgurEndpoints
from .responses import ImgurUploadResponse


IMGUR_CLIENT_ID = os.environ.get("IMGUR_CLIENT_ID")
if not IMGUR_CLIENT_ID:
    SYSTEM.logger.critical("Specify IMGUR_CLIENT_ID as the client ID of imgur client.")
    sys.exit(1)


class ImgurClient:
    @staticmethod
    def upload_image(content: str, type_: str, title: str = None, description: str = None) -> ImgurUploadResponse:
        """
        Upload an image to Imgur.

        :param content: Binary file, base64 or a URL of an image.
        :param type_: "URL" or "base64"
        :param title: Image title.
        :param description: Image description.
        :return: A reponse body from Imgur API.
        """
        # API Reference: https://apidocs.imgur.com/?version=latest#c85c9dfc-7487-4de2-9ecd-66f727cf3139
        data = {
            "image": content,
            "type": type_
        }

        if title:
            data["title"] = title
        if description:
            data["description"] = description

        response = requests.post(
            ImgurEndpoints.get_endpoint_url(ImgurEndpoints.IMAGE_UPLOAD),
            headers={"Authorization": f"Client-ID {IMGUR_CLIENT_ID}"},
            data=data
        )

        return ImgurUploadResponse(response.json())

    @staticmethod
    def delete_image(delete_hash: str) -> bool:
        # API Reference: https://apidocs.imgur.com/?version=latest#949d6cb0-5e55-45f7-8853-8c44a108399c
        response = requests.delete(
            ImgurEndpoints.get_delete_url(delete_hash),
            headers={"Authorization": f"Client-ID {IMGUR_CLIENT_ID}"}
        )

        return response.ok
