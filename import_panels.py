import os
import csv
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "scad.settings")
django.setup()

from django.db import connection, transaction

EVENT_ID = 2
CSV_FILE = "scad_2021_scheduler_ready.csv"


def get_panel_data():
    panels = {}

    with open(CSV_FILE, encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        for row in reader:
            title = row["title"].strip()
            panel_title = row["panel_title"].strip()

            # skip empty submissions and missing panel names
            if not title or not panel_title or panel_title == "0":
                continue

            if panel_title not in panels:
                panels[panel_title] = []

            panels[panel_title].append({
                "title": title,
                "panel_order": row["panel_order"].strip()
            })

    return panels


def import_panels(panels):
    created = 0
    linked = 0
    skipped = []

    with transaction.atomic():
        with connection.cursor() as cursor:

            # find the next available panel id
            cursor.execute("SELECT COALESCE(MAX(panel_id), 0) FROM panel")
            next_id = cursor.fetchone()[0] + 1

            for panel_title, presentations in panels.items():

                # check if this panel already exists
                cursor.execute("""
                    SELECT panel_id
                    FROM panel
                    WHERE event_id = %s AND panel_title = %s
                """, [EVENT_ID, panel_title])

                existing = cursor.fetchone()

                if existing:
                    panel_id = existing[0]
                else:
                    panel_id = next_id
                    next_id += 1

                    cursor.execute("""
                        INSERT INTO panel (panel_id, event_id, panel_title)
                        VALUES (%s, %s, %s)
                    """, [panel_id, EVENT_ID, panel_title])

                    created += 1

                for presentation in presentations:

                    # match the CSV title to a submission
                    cursor.execute("""
                        SELECT submission_id
                        FROM submission
                        WHERE event_id = %s AND title = %s
                    """, [EVENT_ID, presentation["title"]])

                    matches = cursor.fetchall()

                    if len(matches) != 1:
                        skipped.append(presentation["title"])
                        continue

                    submission_id = matches[0][0]

                    # only use panel order when it is a number
                    order_text = presentation["panel_order"]
                    order_number = None

                    if order_text.isdigit():
                        order_number = int(order_text)
                    elif " of " in order_text:
                        first = order_text.split(" of ")[0]
                        if first.isdigit():
                            order_number = int(first)

                    cursor.execute("""
                        UPDATE submission
                        SET panel_id = %s, panel_order = %s
                        WHERE submission_id = %s AND event_id = %s
                    """, [panel_id, order_number, submission_id, EVENT_ID])

                    linked += 1

    print("Panels created:", created)
    print("Presentations linked:", linked)
    print("Presentations skipped:", len(skipped))

    for title in skipped:
        print("Skipped:", title)


if __name__ == "__main__":
    panels = get_panel_data()

    print("Panels found in CSV:", len(panels))

    import_panels(panels)