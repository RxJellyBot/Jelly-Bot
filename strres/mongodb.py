from typing import List, Union, Dict

from bson import ObjectId
from django.utils.translation import gettext_lazy as _

__all__ = ("Profile",)


class Profile:
    DEFAULT_PROFILE_NAME = _("Default Profile")

    DANGLING_PROF_CONN_DATA = "Possible Data Corruption in user Profile Connection"

    @staticmethod
    def dangling_content(data: Dict[ObjectId, Union[ObjectId, List[ObjectId]]]) -> str:
        s: List[str] = []

        for prof_conn_oid, data in data.items():
            s.append(f"Prof Conn OID <code>{prof_conn_oid}</code>")

            if isinstance(data, ObjectId):
                s.append(f"Channel OID not found: <code>{data}</code>")
            elif isinstance(data, list):
                s.append(f"Profile OID not found: <code>{' & '.join([str(oid) for oid in data])}</code>")

            s.append("<hr>")

        return "<br>".join(s)
