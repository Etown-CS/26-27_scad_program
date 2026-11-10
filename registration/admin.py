import json

from django.contrib import admin, messages
from django.db.models import Count
from django.utils import timezone
from django.utils.html import format_html, format_html_join

from .models import (
    Event, Location, Panel, Person, RawSubmission, Schedule,
    ScheduleAssignment, Session, Submission,
)

# Site titles (replace the default "Django administration")
admin.site.site_header = "SCAD Administration"
admin.site.site_title = "SCAD Admin"
admin.site.index_title = "Manage submissions and the schedule"


def people_list(links):
    """Show a list of people as one name per line."""
    names = [(str(link.person),) for link in links]
    if not names:
        return "—"
    return format_html_join(format_html("<br>"), "{}", names)


# Events (with the "Generate draft schedule" button)
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("event_name", "event_date", "registration_deadline", "submission_count")
    ordering = ("-event_date",)
    actions = ["generate_schedule"]

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_submissions=Count("submission"))

    @admin.display(description="Submissions", ordering="_submissions")
    def submission_count(self, obj):
        return obj._submissions

    @admin.action(description="Generate draft schedule for the selected event")
    def generate_schedule(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, "Select exactly one event to schedule.", messages.WARNING)
            return
        from .scheduling import generate_draft_schedule

        result = generate_draft_schedule(queryset.first())
        if not result.ok:
            level = messages.ERROR
        elif result.conflicts:
            level = messages.WARNING
        else:
            level = messages.SUCCESS
        self.message_user(request, result.message, level)


# Raw form submissions
@admin.register(RawSubmission)
class RawSubmissionAdmin(admin.ModelAdmin):
    list_display = ("raw_submission_id", "submitter_email", "event", "processing_status", "submitted_at")
    list_filter = ("processing_status", "event")
    search_fields = ("submitter_email",)
    ordering = ("-submitted_at",)
    date_hierarchy = "submitted_at"
    readonly_fields = ("submitted_at", "pretty_form_data")
    exclude = ("form_data",)
    actions = ["mark_processed", "mark_needs_review"]

    @admin.display(description="Form data (as submitted)")
    def pretty_form_data(self, obj):
        return format_html(
            '<pre style="white-space: pre-wrap; max-width: 900px;">{}</pre>',
            json.dumps(obj.form_data, indent=2, ensure_ascii=False),
        )

    @admin.action(description="Mark selected as processed")
    def mark_processed(self, request, queryset):
        updated = queryset.update(processing_status="processed")
        self.message_user(request, f"{updated} submission(s) marked as processed.")

    @admin.action(description="Mark selected as needs review")
    def mark_needs_review(self, request, queryset):
        updated = queryset.update(processing_status="needs_review")
        self.message_user(request, f"{updated} submission(s) marked as needs review.")


# Submissions (with presenters and mentors shown on each one)
@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("title", "submission_type", "department", "presenter_names", "panel", "status")
    list_display_links = ("title",)
    list_editable = ("status",)
    list_filter = ("event", "submission_type", "status", "department")
    search_fields = ("title", "abstract", "department",
                     "presenters__person__first_name", "presenters__person__last_name")
    list_per_page = 50
    readonly_fields = ("presenter_list", "mentor_list")
    fieldsets = (
        (None, {"fields": ("event", "title", "submission_type", "department", "status")}),
        ("People", {"fields": ("presenter_list", "mentor_list")}),
        ("Panel", {"fields": ("panel", "panel_order")}),
        ("Details", {"fields": ("abstract", "comments")}),
    )
    actions = ["mark_approved", "mark_withdrawn"]

    def get_queryset(self, request):
        return (super().get_queryset(request)
                .select_related("panel", "event")
                .prefetch_related("presenters__person", "mentors__person")
                .distinct())

    @admin.display(description="Presenters")
    def presenter_names(self, obj):
        return people_list(obj.presenters.all())

    @admin.display(description="Presenters")
    def presenter_list(self, obj):
        return people_list(obj.presenters.all())

    @admin.display(description="Mentors")
    def mentor_list(self, obj):
        links = obj.mentors.all()
        if not links:
            return "—"
        rows = [(str(m.person), m.get_mentor_role_display()) for m in links]
        return format_html_join(format_html("<br>"), "{} ({})", rows)

    @admin.action(description="Mark selected as approved")
    def mark_approved(self, request, queryset):
        updated = queryset.update(status="approved")
        self.message_user(request, f"{updated} submission(s) approved.")

    @admin.action(description="Mark selected as withdrawn")
    def mark_withdrawn(self, request, queryset):
        updated = queryset.update(status="withdrawn")
        self.message_user(request, f"{updated} submission(s) withdrawn.")


# People
@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "email")
    search_fields = ("first_name", "last_name", "email")


# Panels, locations, sessions
@admin.register(Panel)
class PanelAdmin(admin.ModelAdmin):
    list_display = ("panel_title", "event", "moderator", "talk_count")
    list_filter = ("event",)
    search_fields = ("panel_title",)
    autocomplete_fields = ("moderator",)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_talks=Count("submissions"))

    @admin.display(description="Presentations", ordering="_talks")
    def talk_count(self, obj):
        return obj._talks


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("building", "room_name", "capacity")
    search_fields = ("building", "room_name")


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ("session_name", "session_type", "location", "start_time", "end_time", "moderator")
    list_filter = ("event", "session_type", "location")
    search_fields = ("session_name",)
    autocomplete_fields = ("moderator",)


# Schedule (with Publish / back to draft buttons)
@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ("event", "status", "assignment_count", "generated_at", "published_at")
    list_filter = ("status",)
    actions = ["publish", "back_to_draft"]

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_assignments=Count("assignments"))

    @admin.display(description="Presentations", ordering="_assignments")
    def assignment_count(self, obj):
        return obj._assignments

    @admin.action(description="Publish selected schedule")
    def publish(self, request, queryset):
        updated = queryset.update(status="published", published_at=timezone.now())
        self.message_user(request, f"{updated} schedule(s) published.", messages.SUCCESS)

    @admin.action(description="Set selected schedule back to draft")
    def back_to_draft(self, request, queryset):
        updated = queryset.update(status="draft", published_at=None)
        self.message_user(request, f"{updated} schedule(s) set back to draft.")


@admin.register(ScheduleAssignment)
class ScheduleAssignmentAdmin(admin.ModelAdmin):
    list_display = ("start_time", "room", "submission", "panel", "session", "is_locked")
    list_display_links = ("submission",)
    list_editable = ("is_locked",)
    list_filter = ("schedule", "session__session_name", "session__location", "is_locked")
    search_fields = ("submission__title",)
    autocomplete_fields = ("submission", "session")
    list_per_page = 100

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "submission__panel", "session__location"
        )

    @admin.display(description="Room", ordering="session__location")
    def room(self, obj):
        return obj.session.location

    @admin.display(description="Panel")
    def panel(self, obj):
        return obj.submission.panel or "—"