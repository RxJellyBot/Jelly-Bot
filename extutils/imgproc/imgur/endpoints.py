class ImgurEndpoints:
    URL = "https://api.imgur.com/3/"

    IMAGE_UPLOAD = "upload"

    @staticmethod
    def get_endpoint_url(endpoint: str):
        return ImgurEndpoints.URL + endpoint

    @staticmethod
    def get_delete_url(delete_hash: str):
        return ImgurEndpoints.URL + "image/" + delete_hash
