"""
Utilies for image processing.
"""
import base64


class ImageContentProcessor:
    """
    Class for processing the image content.
    """

    @staticmethod
    def binary_img_to_base64_str(bin_data: bytes) -> str:
        """
        Convert the image byte data to base64 :class:`str`.

        :param bin_data: binary data to be converted
        :return: converted base64 string
        """
        return base64.b64encode(bin_data).decode("utf-8")

    @staticmethod
    def local_img_to_base64_str(path: str) -> str:
        """
        Read the locally stored image at ``path`` and convert it to base64 :class:`str`.

        :param path: path of the file to be converted
        :return: converted base64 string
        """
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")


class ImageValidator:  # pylint: disable=R0903
    """
    Class for validating the image information.
    """

    @staticmethod
    def is_valid_image_extension(name: str) -> bool:
        """
        Check if the extension of ``name`` is a supported image format.

        Currently supported image format:

        - ``.jpg``

        - ``.png``

        - ``.jpeg``

        This only checks the file extension.

        Does **NOT** check for the magic bytes of the file and the existence of the file.

        :param name: name of the file to be validated
        :return: if the file extension is valid
        """
        return name.endswith(".jpg") or name.endswith(".png") or name.endswith(".jpeg")
