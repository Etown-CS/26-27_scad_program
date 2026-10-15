import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST


def form_page(request):
    """Shows the public application form."""
    return render(request, "registration/index.html")


@require_POST
def create_submission(request):
    """Receives a submission from the form as JSON."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Request body must be JSON."}, status=400)

    # Milestone 1: just print it. Saving to Supabase comes next.
    print("New submission:")
    print(json.dumps(data, indent=2))

    return JsonResponse({"message": "Received"}, status=201)