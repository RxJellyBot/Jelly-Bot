"""
Module to get the endpoint URLs of imgur API.
"""


class ImgurEndpoints:
    """
    Class to get the endpoint URLs of imgur API.
    """

    URL = "https://api.imgur.com/3/"

    @staticmethod
    def get_upload_url():
        """
        Get the full URL of the image uploading endpoint.

        :return: full endpoint URL to upload an image
        """
        return ImgurEndpoints.URL + "upload"

    @staticmethod
    def get_delete_url(delete_hash: str):
        """
        Get the full URL of the image deleting endpoint.

        :param delete_hash: image deleting hash
        :return: full URL to delete the image with `delete_hash`
        """
        return ImgurEndpoints.URL + "image/" + delete_hash
