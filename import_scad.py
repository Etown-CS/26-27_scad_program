
import os
import sys
import csv
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "scad.settings")
django.setup()

from django.db import connection, transaction

CSV_FILE = "scad_2021_scheduler_ready.csv"
EVENT_ID = 2

TYPE_MAPPING = {
    "Paper/Oral Presentation": "oral",
    "Poster": "poster",
    "Reading": "oral",
    "Podcast": "oral",
    "Art Work": "poster",
}


def load_presentations():
    presentations = {}

    with open(CSV_FILE, encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        for row in reader:
            title = row["title"].strip()

            if not title:
                continue

            source_row = row["source_row"]
            original_type = row["submission_type"].strip()
            mapped_type = TYPE_MAPPING.get(original_type)

            if 62 <= int(source_row) <= 78:
                key = ("marietta_group", "poster")
                mapped_type = "poster"
            else:
                key = (title.casefold(), mapped_type)

            if key not in presentations:
                presentations[key] = {
                    "title": title,
                    "abstract": row.get("abstract", "").strip(),
                    "department": row.get("department", "").strip(),
                    "type": mapped_type,
                    "presenters": [],
                    "source_rows": [],
                }

            presentation = presentations[key]

            if not presentation["abstract"]:
                presentation["abstract"] = row.get(
                    "abstract", ""
                ).strip()

            if not presentation["department"]:
                presentation["department"] = row.get(
                    "department", ""
                ).strip()

            presentation["source_rows"].append(source_row)

            presenter = row.get("presenters", "").strip()

            if presenter and presenter not in presentation["presenters"]:
                presentation["presenters"].append(presenter)

    return list(presentations.values())


def split_name(full_name):
    """Split a presenter's name into first and last names."""
    parts = full_name.strip().split()

    if len(parts) < 2:
        return parts[0], "(Unknown)"

    return parts[0], " ".join(parts[1:])


def preview_import(presentations):
    print("\nSCAD IMPORT PREVIEW")
    print("------------------------------")
    print("Total presentations:", len(presentations))
    print("Oral presentations:", sum(
        p["type"] == "oral" for p in presentations
    ))
    print("Poster presentations:", sum(
        p["type"] == "poster" for p in presentations
    ))
    print("Presenter links:", sum(
        len(p["presenters"]) for p in presentations
    ))
    print("\nNo database changes made.")


def import_to_database(presentations):
    """Import all records in one transaction."""

    with transaction.atomic():
        with connection.cursor() as cursor:

            cursor.execute(
                "SELECT COUNT(*) FROM submission WHERE event_id = %s",
                [EVENT_ID]
            )

            if cursor.fetchone()[0] != 0:
                raise RuntimeError(
                    "This event already has submissions. "
                    "Import cancelled to prevent duplicates."
                )

            cursor.execute(
                "SELECT 1 FROM event WHERE event_id = %s",
                [EVENT_ID]
            )

            if cursor.fetchone() is None:
                raise RuntimeError(
                    f"Event {EVENT_ID} does not exist."
                )

            cursor.execute(
                "SELECT COALESCE(MAX(submission_id), 0) FROM submission"
            )
            next_submission_id = cursor.fetchone()[0] + 1

            cursor.execute(
                "SELECT COALESCE(MAX(person_id), 0) FROM person"
            )
            next_person_id = cursor.fetchone()[0] + 1

            # Reuse people within this import.
            people = {}
            submission_count = 0
            link_count = 0

            for presentation in presentations:
                submission_id = next_submission_id
                next_submission_id += 1

                cursor.execute(
                    """
                    INSERT INTO submission
                    (submission_id, event_id, title, abstract,
                     submission_type, department, status, comments)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    [
                        submission_id,
                        EVENT_ID,
                        presentation["title"],
                        presentation["abstract"] or None,
                        presentation["type"],
                        presentation["department"] or None,
                        "submitted",
                        "Historical SCAD 2021 test import; CSV rows: "
                        + ", ".join(presentation["source_rows"]),
                    ]
                )

                submission_count += 1

                for order, full_name in enumerate(
                    presentation["presenters"], start=1
                ):
                    normalized_name = " ".join(
                        full_name.split()
                    ).casefold()

                    if normalized_name not in people:
                        first_name, last_name = split_name(
                            full_name
                        )

                        person_id = next_person_id
                        next_person_id += 1

                        cursor.execute(
                            """
                            INSERT INTO person
                            (person_id, first_name, last_name, email)
                            VALUES (%s, %s, %s, NULL)
                            """,
                            [person_id, first_name, last_name]
                        )

                        people[normalized_name] = person_id

                    person_id = people[normalized_name]

                    cursor.execute(
                        """
                        INSERT INTO submission_presenter
                        (submission_id, person_id,
                         presenter_order, participation_status)
                        VALUES (%s, %s, %s, %s)
                        """,
                        [submission_id, person_id, order, "active"]
                    )

                    link_count += 1

    print("\nIMPORT SUCCESSFUL!")
    print("Submissions created:", submission_count)
    print("People created:", len(people))
    print("Presenter links created:", link_count)


def main():
    presentations = load_presentations()

    if len(presentations) != 117:
        raise RuntimeError(
            f"Expected 117 presentations, got {len(presentations)}."
        )

    if any(p["type"] not in ("oral", "poster") for p in presentations):
        raise RuntimeError("Unrecognized presentation type.")

    preview_import(presentations)

    if "--import" not in sys.argv:
        print("\nTo import, run: python import_scad.py --import")
        return

    confirmation = input(
        "\nType IMPORT to write these records to Supabase: "
    )

    if confirmation != "IMPORT":
        print("Import cancelled.")
        return

    import_to_database(presentations)


if __name__ == "__main__":
    main()
