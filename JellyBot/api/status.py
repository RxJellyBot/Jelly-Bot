from django.http import JsonResponse


# noinspection PyUnusedLocal
def status_check(request):
    # DRAFT: System: Self testing
    return JsonResponse({'OK': True})
