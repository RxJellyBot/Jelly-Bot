import os
import sys

# noinspection PyPackageRequirements
from google.oauth2 import id_token
# noinspection PyPackageRequirements
from google.auth.transport import requests


class IDIssuerIncorrect(Exception):
    def __init__(self, issuer):
        super().__init__(f'ID issuer is not accounts.google.com. ({issuer})')


class GoogleIdentityUserData:
    def __init__(self, data):
        self.aud = data["aud"]
        self.issuer = data["iss"]
        self.uid = data["sub"]
        self.email = data.get("email")
        if self.aud != CLIENT_ID:
            raise ValueError(f"Unmatched aud field and sub field. aud: {self.aud}, sub: {self.uid}")


CLIENT_ID = os.environ.get("GI_CLIENT_ID")
if CLIENT_ID is None:
    print("Cannot find GI_CLIENT_ID for Google Identity Service in system variables.")
    sys.exit(1)


def get_identity_data(token) -> GoogleIdentityUserData:
    id_data = GoogleIdentityUserData(id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID))

    if id_data.issuer not in ['accounts.google.com', 'https://accounts.google.com']:
        raise IDIssuerIncorrect(id_data.issuer)

    return id_data
