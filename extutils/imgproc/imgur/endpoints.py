class ImgurEndpoints:
    URL = "https://api.imgur.com/3/"

    IMAGE_UPLOAD = "upload"

    @staticmethod
    def get_endpoint_url(endpoint: str):
        return ImgurEndpoints.URL + endpoint
