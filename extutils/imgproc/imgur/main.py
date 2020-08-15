"""
Main implementations to interact with imgur API.
"""
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
    """
    Imgur API wrapper.
    """

    @staticmethod
    def upload_image(content: str, type_: str, title: str = None, description: str = None) -> ImgurUploadResponse:
        """
        Upload an image to Imgur.

        API Reference: https://apidocs.imgur.com/?version=latest#c85c9dfc-7487-4de2-9ecd-66f727cf3139

        :param content: image content based on the `type_`
        :param type_: "URL" or "base64"
        :param title: image title
        :param description: image description
        :return: response body of the upload result wrapped as `ImgurUploadResponse`
        """
        data = {
            "image": content,
            "type": type_
        }

        if title:
            data["title"] = title

        if description:
            data["description"] = description

        response = requests.post(
            ImgurEndpoints.get_upload_url(),
            headers={"Authorization": f"Client-ID {IMGUR_CLIENT_ID}"},
            data=data
        )

        return ImgurUploadResponse(response.json())

    @staticmethod
    def delete_image(delete_hash: str) -> bool:
        """
        Delete an image with ``delete_hash`` which is given when an image is upload
        and return if the deletion succeed.

        API Reference: https://apidocs.imgur.com/?version=latest#949d6cb0-5e55-45f7-8853-8c44a108399c

        :param delete_hash: image delete hash
        :return: if the deletion succeed
        """
        response = requests.delete(
            ImgurEndpoints.get_delete_url(delete_hash),
            headers={"Authorization": f"Client-ID {IMGUR_CLIENT_ID}"}
        )

        return response.ok
