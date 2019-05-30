from django.http import JsonResponse


def status_check(request):
    # DRAFT: (Low Priority) Self testing
    return JsonResponse({'OK': True})
