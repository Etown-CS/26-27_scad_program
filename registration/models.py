# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Event(models.Model):
    event_id = models.AutoField(primary_key=True)
    event_name = models.CharField(max_length=150)
    event_date = models.DateField()
    registration_deadline = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'event'


class RawSubmission(models.Model):
    raw_submission_id = models.AutoField(primary_key=True)
    event = models.ForeignKey(Event, models.DO_NOTHING)
    submitted_at = models.DateTimeField()
    submitter_email = models.CharField(max_length=254, blank=True, null=True)
    form_data = models.JSONField()
    processing_status = models.TextField()
    processing_notes = models.TextField(blank=True, null=True)
    processed_at = models.DateTimeField(blank=True, null=True)
    submission_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'raw_submission'
