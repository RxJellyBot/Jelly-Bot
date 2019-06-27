import os
import sys

# noinspection PyPackageRequirements
from dataclasses import dataclass
# noinspection PyPackageRequirements
from google.oauth2 import id_token
# noinspection PyPackageRequirements
from google.auth.transport import requests


CLIENT_ID = os.environ.get("GI_CLIENT_ID")
if CLIENT_ID is None:
    print("Cannot find GI_CLIENT_ID for Google Identity Service in system variables.")
    sys.exit(1)


class IDIssuerIncorrect(Exception):
    def __init__(self, issuer):
        super().__init__(f'ID issuer is not accounts.google.com. ({issuer})')


@dataclass
class GoogleIdentityUserData:
    aud: str
    issuer: str
    uid: str
    email: str
    skip_check: bool = False

    def __post_init__(self):
        if not self.skip_check and self.aud != CLIENT_ID:
            raise ValueError(f"Audience is not this Google Identity client. aud: {self.aud}, Client ID: {CLIENT_ID}")


def get_identity_data(token) -> GoogleIdentityUserData:
    google_data = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)

    id_data = GoogleIdentityUserData(google_data["aud"], google_data["iss"], google_data["sub"], google_data["email"])

    if id_data.issuer not in ['accounts.google.com', 'https://accounts.google.com']:
        raise IDIssuerIncorrect(id_data.issuer)

    return id_data
