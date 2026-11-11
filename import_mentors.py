# ONE-TIME SCRIPT: imports the 2021 mentors from scad_2021_scheduler_ready.csv
# into person + submission_mentor. Delete this file after running it.
#
# Run from the project folder (next to manage.py):
#   python manage.py shell -c "exec(open('import_mentors.py').read())"
#
# Set DRY_RUN = False to actually save. Safe to run more than once.

import csv
import re

from django.db import transaction

from registration.models import Person, Submission, SubmissionMentor

DRY_RUN = True
CSV_FILE = "scad_2021_scheduler_ready.csv"
TITLES = {"dr", "dr.", "ms", "ms.", "mr", "mr.", "mrs", "mrs.", "prof", "prof."}


def split_name(full_name):
    """Turns 'Dr. Matthew W Telleen' into ('Matthew W', 'Telleen')."""
    words = [word for word in full_name.split() if word.lower() not in TITLES]
    if not words:
        return "", ""
    if len(words) == 1:
        return words[0], ""
    return " ".join(words[:-1]), words[-1]


# Match each CSV row number to its submission, using the "CSV rows: 2, 3" note
row_to_submission = {}
for submission in Submission.objects.filter(comments__contains="CSV rows:"):
    for number in re.findall(r"\d+", submission.comments.split("CSV rows:", 1)[1]):
        row_to_submission[number] = submission

people_created = 0
links_created = 0
no_name = set()
unmatched_rows = []

with transaction.atomic():
    with open(CSV_FILE, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            submission = row_to_submission.get(row["source_row"].strip())
            if submission is None:
                unmatched_rows.append(row["source_row"])
                continue

            for name_column, email_column, role in [
                ("mentor_name", "mentor_email", "primary"),
                ("secondary_mentor_name", "secondary_mentor_email", "secondary"),
            ]:
                name = (row.get(name_column) or "").strip()
                email = (row.get(email_column) or "").strip().lower()
                if "@" not in email:
                    continue  # no usable email
                if not name:
                    no_name.add(email)  # email with no name: usually a data entry mistake
                    continue

                # Add the mentor once, no matter how many submissions they mentored
                person = Person.objects.filter(email__iexact=email).first()
                if person is None:
                    first_name, last_name = split_name(name)
                    person = Person.objects.create(first_name=first_name, last_name=last_name, email=email)
                    people_created += 1

                # Link them to this submission (skip if already linked)
                if SubmissionMentor.objects.filter(submission=submission, person=person).exists():
                    continue

                # Group projects span several CSV rows; keep one primary mentor
                if role == "primary" and SubmissionMentor.objects.filter(
                    submission=submission, mentor_role="primary"
                ).exists():
                    role = "secondary"

                SubmissionMentor.objects.create(submission=submission, person=person, mentor_role=role)
                links_created += 1

    print("Mentors added to person:", people_created)
    print("Mentor links added:", links_created)
    if no_name:
        print("Emails skipped (no name, check by hand):", ", ".join(sorted(no_name)))
    if unmatched_rows:
        print("CSV rows with no matching submission:", ", ".join(unmatched_rows))

    if DRY_RUN:
        transaction.set_rollback(True)
        print("DRY RUN: nothing was saved. Set DRY_RUN = False to import.")
    else:
        print("Import complete.")