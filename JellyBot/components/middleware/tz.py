from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin

from extutils.locales import DEFAULT_LOCALE
from JellyBot.utils import get_root_oid

from mongodb.factory import RootUserManager


class TimezoneActivator(MiddlewareMixin):
    # noinspection PyMethodMayBeStatic
    def process_request(self, request):
        root_oid = get_root_oid(request)

        if root_oid is None:
            timezone.activate(DEFAULT_LOCALE.to_tzinfo())
        else:
            timezone.activate(RootUserManager.get_tzinfo_root_oid(root_oid))
