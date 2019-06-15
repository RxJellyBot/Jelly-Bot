from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin


class TimezoneActivator(MiddlewareMixin):
    def process_request(self, request):
        pass
        # TODO: Account management - add timezone to account / append on MixUserData
        # tzname = request.session.get('django_timezone')
        # if tzname:
        #     timezone.activate(pytz.timezone(tzname))
        # else:
        #     timezone.deactivate()
