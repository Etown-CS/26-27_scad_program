"""
Turns a raw_submission (the whole form saved as JSON) into rows in
person, panel, submission, submission_presenter and submission_mentor.
"""
from django.db import transaction
from django.utils import timezone

from .models import Panel, Person, Submission, SubmissionMentor, SubmissionPresenter

# Values that match the choices in models.py
SUBMISSION_STATUS = "submitted"          # an admin changes this to "approved" later
PARTICIPATION_STATUS = "active"
MENTOR_ROLE_PRIMARY = "primary"
MENTOR_ROLE_SECONDARY = "secondary"
PROCESSED = "processed"
NEEDS_REVIEW = "needs_review"


def clean(value):
    """Turns None into "" and trims spaces."""
    return (value or "").strip()


def yes_no(value):
    """Turns the form's "yes"/"no" into True/False (None if not answered)."""
    if value == "yes":
        return True
    if value == "no":
        return False
    return None


def to_int(value):
    """Turns "2" into 2 (None if blank or not a number)."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def find_or_create_person(first_name, last_name, email):
    """Reuses the person with this email if they already exist, so nobody is added twice."""
    email = clean(email).lower()
    if not email:
        raise ValueError(f"Missing email for {clean(first_name)} {clean(last_name)}".strip())

    existing = Person.objects.filter(email__iexact=email).first()
    if existing:
        return existing
    return Person.objects.create(
        first_name=clean(first_name),
        last_name=clean(last_name),
        email=email,
    )


def find_or_create_panel(event_id, data):
    """Returns the panel this presentation belongs to, creating it if needed (None if not on a panel)."""
    title = clean(data.get("panel_title"))
    if data.get("submission_type") != "oral" or data.get("is_panel") != "yes" or not title:
        return None

    panel = Panel.objects.filter(event_id=event_id, panel_title__iexact=title).first()
    if panel is None:
        panel = Panel.objects.create(event_id=event_id, panel_title=title)

    # Add the moderator if one was given and the panel doesn't have one yet
    if panel.moderator_id is None and clean(data.get("moderator_email")):
        panel.moderator = find_or_create_person(
            data.get("moderator_first_name"),
            data.get("moderator_last_name"),
            data.get("moderator_email"),
        )
        panel.save(update_fields=["moderator"])

    return panel


def process_raw_submission(raw):
    """Creates the submission and its people. All or nothing: if any step fails, nothing is saved."""
    data = raw.form_data

    with transaction.atomic():
        # 1. Panel (oral presentations only)
        panel = find_or_create_panel(raw.event_id, data)

        # 2. The submission itself
        submission = Submission.objects.create(
            event_id=raw.event_id,
            title=clean(data.get("title")),
            abstract=clean(data.get("abstract")) or None,
            submission_type=clean(data.get("submission_type")),
            department=clean(data.get("department")) or None,
            status=SUBMISSION_STATUS,
            panel=panel,
            panel_order=to_int(data.get("panel_order")) if panel else None,
            comments=clean(data.get("comments")) or None,
        )

        # 3. Presenters: the submitter is #1, then each group member
        presenters = [{
            "first_name": data.get("first_name"),
            "last_name": data.get("last_name"),
            "email": data.get("email"),
        }]
        if data.get("is_group") == "yes":
            presenters += data.get("group_members") or []

        added_presenters = set()
        order = 1
        for p in presenters:
            if not clean(p.get("first_name")) and not clean(p.get("email")):
                continue  # skip empty rows
            person = find_or_create_person(p.get("first_name"), p.get("last_name"), p.get("email"))
            if person.person_id in added_presenters:
                continue  # same person listed twice
            SubmissionPresenter.objects.create(
                submission=submission,
                person=person,
                presenter_order=order,
                participation_status=PARTICIPATION_STATUS,
            )
            added_presenters.add(person.person_id)
            order += 1

        # 4. Mentors: primary is required, secondary only if filled in
        added_mentors = set()
        for prefix, role in [("mentor1", MENTOR_ROLE_PRIMARY), ("mentor2", MENTOR_ROLE_SECONDARY)]:
            first = clean(data.get(f"{prefix}_first_name"))
            email = clean(data.get(f"{prefix}_email"))
            if not first and not email:
                continue
            person = find_or_create_person(first, data.get(f"{prefix}_last_name"), email)
            if person.person_id in added_mentors:
                continue  # same mentor entered twice
            SubmissionMentor.objects.create(
                submission=submission,
                person=person,
                mentor_role=role,
                willing_to_moderate=yes_no(data.get(f"{prefix}_willing_to_moderate")),
            )
            added_mentors.add(person.person_id)

        # 5. Mark the raw submission as done and link it to the new submission
        raw.submission_id = submission.submission_id
        raw.processing_status = PROCESSED
        raw.processed_at = timezone.now()
        raw.save(update_fields=["submission_id", "processing_status", "processed_at"])

    return submission


def mark_needs_review(raw, error):
    """Keeps the raw submission and records what went wrong, so an admin can fix it."""
    raw.processing_status = NEEDS_REVIEW
    raw.processing_notes = str(error)[:1000]
    raw.save(update_fields=["processing_status", "processing_notes"])