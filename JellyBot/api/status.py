from django.http import JsonResponse


# noinspection PyUnusedLocal
def status_check(request):
    # DRAFT: (Low Priority) Self testing
    return JsonResponse({'OK': True})
