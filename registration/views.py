import json

from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Event, RawSubmission

REQUIRED_FIELDS = [
    "first_name", "last_name", "email", "submission_type",
    "title", "abstract", "department",
    "mentor1_first_name", "mentor1_last_name", "mentor1_email",
]


def form_page(request):
    """Shows the public application form."""
    return render(request, "registration/index.html")


@require_POST
def create_submission(request):
    """Receives a submission from the form as JSON and saves it to Supabase."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Request body must be JSON."}, status=400)

    # Check required fields on the server too (the browser's checks can be skipped)
    missing = [field for field in REQUIRED_FIELDS if not str(data.get(field, "")).strip()]
    if missing:
        return JsonResponse({"error": "Missing required fields: " + ", ".join(missing)}, status=400)

    # Link the submission to the current SCAD event and enforce the deadline
    event = Event.objects.order_by("-event_date").first()
    if event is None:
        return JsonResponse({"error": "No SCAD event has been set up yet."}, status=500)
    if timezone.now() > event.registration_deadline:
        return JsonResponse({"error": "Registration is closed. Please contact the SCAD coordinator."}, status=403)

    # Save the whole form as JSON in raw_submission
    try:
        raw = RawSubmission.objects.create(
            event=event,
            submitted_at=timezone.now(),
            submitter_email=data["email"],
            form_data=data,
            processing_status="pending",
        )
    except Exception as error:
        print("Could not save submission:", error)
        return JsonResponse({"error": "Could not save your registration. Please try again later."}, status=500)

    print(f"Saved raw submission #{raw.raw_submission_id} for {data['email']}")
    return JsonResponse({"message": "Received", "id": raw.raw_submission_id}, status=201)