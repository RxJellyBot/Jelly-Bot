import os
import sys

import requests

from .endpoints import ImgurEndpoints
from .responses import ImgurUploadResponse


IMGUR_CLIENT_ID = os.environ.get("IMGUR_CLIENT_ID")
if not IMGUR_CLIENT_ID:
    print("Specify IMGUR_CLIENT_ID as the client ID of imgur client.")
    sys.exit(1)


class ImgurClient:
    @staticmethod
    def upload_image(content: str, type_: str, title: str = None, description: str = None) -> ImgurUploadResponse:
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
