"""
Connects scheduler (scheduler.py) to the database.

scheduler.py itself is not changed.
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from django.db import transaction
from django.utils import timezone

from .models import Location, Schedule, ScheduleAssignment, Session

SLOT_MINUTES = 20
CAMPUS_TZ = ZoneInfo("America/New_York")


@dataclass
class ScheduleResult:
    ok: bool
    message: str
    scheduled: int = 0
    conflicts: list = field(default_factory=list)


def _slot_datetime(event_date, time_text):
    """Turn the event date + a time like '9:30 AM' into a datetime."""
    clock = datetime.strptime(time_text.strip(), "%I:%M %p").time()
    return datetime.combine(event_date, clock, tzinfo=CAMPUS_TZ)


def _get_location(room_text):
    """'Nicarry 202' -> Location(building='Nicarry', room_name='202')."""
    building, _, room_name = room_text.rpartition(" ")
    building = building or room_text
    location = Location.objects.filter(building=building, room_name=room_name).first()
    if location is None:
        location = Location.objects.create(building=building, room_name=room_name)
    return location


def _get_session(event, location, session_name, times):
    """One session row = one session block in one room."""
    session = Session.objects.filter(
        event=event, location=location, session_name=session_name
    ).first()
    if session is None:
        start = _slot_datetime(event.event_date, times[0])
        end = _slot_datetime(event.event_date, times[-1]) + timedelta(minutes=SLOT_MINUTES)
        session = Session.objects.create(
            event=event, location=location, session_name=session_name,
            session_type="oral", start_time=start, end_time=end,
        )
    return session


def generate_draft_schedule(event):
    """Run the scheduler for one event and save it as the draft schedule."""
    import scheduler  # Megan's scheduler.py in the project root (imported here, not at startup)

    schedule = Schedule.objects.filter(event=event).first()

    if schedule and schedule.status == "published":
        return ScheduleResult(False, f"{event} already has a published schedule. "
                                     f"Set it back to draft before generating a new one.")
    if schedule and schedule.assignments.filter(is_locked=True).exists():
        return ScheduleResult(False, f"{event} has locked assignments. The scheduler can't keep "
                                     f"locked presentations in place yet, so unlock them first.")

    # Point the scheduler at this event, run it, then put the setting back.
    original_event_id = scheduler.EVENT_ID
    scheduler.EVENT_ID = event.event_id
    try:
        projects = scheduler.get_submissions()
        if not projects:
            return ScheduleResult(False, f"No approved oral presentations found for {event}.")
        results = scheduler.generate_schedule(projects)
        if results is None:
            return ScheduleResult(False, "The scheduler could not find a valid schedule "
                                         "(not enough slots, or the rules conflict).")
        conflicts = scheduler.check_schedule_conflicts(results, projects)
    finally:
        scheduler.EVENT_ID = original_event_id

    with transaction.atomic():
        if schedule is None:
            schedule = Schedule.objects.create(event=event, status="draft")
        schedule.assignments.all().delete()

        locations = {}
        sessions = {}
        for order, item in enumerate(results, start=1):
            room = item["room"]
            if room not in locations:
                locations[room] = _get_location(room)

            key = (item["session"], room)
            if key not in sessions:
                sessions[key] = _get_session(
                    event, locations[room], item["session"], scheduler.sessions[item["session"]]
                )

            start = _slot_datetime(event.event_date, item["time"])
            ScheduleAssignment.objects.create(
                schedule=schedule,
                submission_id=item["submission_id"],
                session=sessions[key],
                start_time=start,
                end_time=start + timedelta(minutes=SLOT_MINUTES),
                placement_order=order,
            )

        # Remove scheduler-made session blocks that no longer have any presentations.
        Session.objects.filter(
            event=event, session_type="oral",
            session_name__in=list(scheduler.sessions), assignments__isnull=True,
        ).delete()

        schedule.status = "draft"
        schedule.generated_at = timezone.now()
        schedule.published_at = None
        schedule.save()

    message = f"Draft schedule for {event}: {len(results)} of {len(projects)} presentations scheduled."
    if conflicts:
        message += f" WARNING: {len(conflicts)} conflict(s) found: " + "; ".join(conflicts[:5])
    return ScheduleResult(True, message, scheduled=len(results), conflicts=conflicts)