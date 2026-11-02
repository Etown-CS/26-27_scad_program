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

class Person(models.Model):
    person_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.CharField(max_length=254, unique=True)
 
    class Meta:
        managed = False
        db_table = 'person'
        ordering = ['last_name', 'first_name']
        verbose_name_plural = 'people'
 
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
 
 
class Location(models.Model):
    location_id = models.AutoField(primary_key=True)
    building = models.CharField(max_length=150)
    room_name = models.CharField(max_length=100)
    capacity = models.IntegerField(blank=True, null=True)
 
    class Meta:
        managed = False
        db_table = 'location'
        ordering = ['building', 'room_name']
 
    def __str__(self):
        return f"{self.building} {self.room_name}"
 
 
class Panel(models.Model):
    panel_id = models.AutoField(primary_key=True)
    event = models.ForeignKey(Event, models.DO_NOTHING)
    panel_title = models.CharField(max_length=250)
    moderator = models.ForeignKey(
        Person, models.DO_NOTHING, db_column='moderator_person_id',
        blank=True, null=True, related_name='moderated_panels',
    )
 
    class Meta:
        managed = False
        db_table = 'panel'
        ordering = ['panel_title']
 
    def __str__(self):
        return self.panel_title
 
 
class Submission(models.Model):
    TYPE_CHOICES = [('oral', 'Oral presentation'), ('poster', 'Poster')]
    STATUS_CHOICES = [('submitted', 'Submitted'), ('approved', 'Approved'), ('withdrawn', 'Withdrawn')]
 
    submission_id = models.AutoField(primary_key=True)
    event = models.ForeignKey(Event, models.DO_NOTHING)
    title = models.CharField(max_length=500)
    abstract = models.TextField(blank=True, null=True)
    submission_type = models.TextField(choices=TYPE_CHOICES)
    department = models.CharField(max_length=150, blank=True, null=True)
    status = models.TextField(choices=STATUS_CHOICES, default='submitted')
    panel = models.ForeignKey(Panel, models.DO_NOTHING, blank=True, null=True, related_name='submissions')
    panel_order = models.IntegerField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
 
    class Meta:
        managed = False
        db_table = 'submission'
        ordering = ['submission_id']
 
    def __str__(self):
        return self.title
 
 
class SubmissionPresenter(models.Model):
    pk = models.CompositePrimaryKey('submission_id', 'person_id')
    submission = models.ForeignKey(Submission, models.DO_NOTHING, related_name='presenters')
    person = models.ForeignKey(Person, models.DO_NOTHING, related_name='presentations')
    presenter_order = models.IntegerField()
    participation_status = models.TextField(default='active')
 
    class Meta:
        managed = False
        db_table = 'submission_presenter'
        ordering = ['presenter_order']
 
 
class SubmissionMentor(models.Model):
    ROLE_CHOICES = [('primary', 'Primary'), ('secondary', 'Secondary')]
 
    pk = models.CompositePrimaryKey('submission_id', 'person_id')
    submission = models.ForeignKey(Submission, models.DO_NOTHING, related_name='mentors')
    person = models.ForeignKey(Person, models.DO_NOTHING, related_name='mentorships')
    mentor_role = models.TextField(choices=ROLE_CHOICES)
    willing_to_moderate = models.BooleanField(blank=True, null=True)
 
    class Meta:
        managed = False
        db_table = 'submission_mentor'
 
 
class Session(models.Model):
    TYPE_CHOICES = [('oral', 'Oral'), ('poster', 'Poster')]
 
    session_id = models.AutoField(primary_key=True)
    event = models.ForeignKey(Event, models.DO_NOTHING)
    location = models.ForeignKey(Location, models.DO_NOTHING)
    session_name = models.CharField(max_length=150)
    session_type = models.TextField(choices=TYPE_CHOICES)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    moderator = models.ForeignKey(
        Person, models.DO_NOTHING, db_column='moderator_person_id',
        blank=True, null=True, related_name='moderated_sessions',
    )
 
    class Meta:
        managed = False
        db_table = 'session'
        ordering = ['start_time', 'session_name']
 
    def __str__(self):
        return f"{self.session_name} ({self.location})"
 
 
class Schedule(models.Model):
    STATUS_CHOICES = [('draft', 'Draft'), ('published', 'Published')]
 
    schedule_id = models.AutoField(primary_key=True)
    event = models.OneToOneField(Event, models.DO_NOTHING)
    status = models.TextField(choices=STATUS_CHOICES, default='draft')
    generated_at = models.DateTimeField(blank=True, null=True)
    published_at = models.DateTimeField(blank=True, null=True)
 
    class Meta:
        managed = False
        db_table = 'schedule'
 
    def __str__(self):
        return f"{self.event} schedule ({self.status})"
 
 
class ScheduleAssignment(models.Model):
    assignment_id = models.AutoField(primary_key=True)
    schedule = models.ForeignKey(Schedule, models.DO_NOTHING, related_name='assignments')
    submission = models.ForeignKey(Submission, models.DO_NOTHING, related_name='assignments')
    session = models.ForeignKey(Session, models.DO_NOTHING, related_name='assignments')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    poster_number = models.CharField(max_length=20, blank=True, null=True)
    placement_order = models.IntegerField(blank=True, null=True)
    is_locked = models.BooleanField(default=False)
 
    class Meta:
        managed = False
        db_table = 'schedule_assignment'
        ordering = ['start_time', 'placement_order']
 
    def __str__(self):
        return f"{self.submission} @ {self.session}"
