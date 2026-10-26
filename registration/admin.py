from django.contrib import admin
from .models import Event, RawSubmission

@admin.register(RawSubmission)
class RawSubmissionAdmin(admin.ModelAdmin):
    list_display = ("raw_submission_id", "submitter_email", "processing_status", "submitted_at")
    list_filter = ("processing_status",)
    search_fields = ("submitter_email",)
    ordering = ("-submitted_at",)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("event_name", "event_date", "registration_deadline")
# Register your models here.
