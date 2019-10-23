from django.utils.translation import activate, deactivate
from django.utils.deprecation import MiddlewareMixin

from JellyBot.components import get_root_oid

from mongodb.factory import RootUserManager


class TranslationActivator(MiddlewareMixin):
    # noinspection PyMethodMayBeStatic
    def process_request(self, request):
        root_oid = get_root_oid(request)

        if root_oid:
            l_code = RootUserManager.get_lang_code_root_oid(root_oid)

            if l_code:
                activate(l_code)
                return

        deactivate()
