
import os
import django
from collections import defaultdict

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "scad.settings")
django.setup()

from django.db import connection
from ortools.sat.python import cp_model


# SCAD presentation rooms
rooms = [
    "Nicarry 202",
    "Nicarry 210",
    "Nicarry 228",
    "Nicarry 232",
    "Hoover 211",
    "Hoover 212",
    "Hoover 213",
    "Hoover 214"
]

# SCAD presentation sessions
sessions = {
    "Session 1": [
        "9:30 AM", "9:50 AM", "10:10 AM", "10:30 AM"
    ],
    "Session 2": [
        "11:00 AM", "11:20 AM", "11:40 AM", "12:00 PM"
    ],
    "Session 3": [
        "1:15 PM", "1:35 PM", "1:55 PM",
        "2:15 PM", "2:35 PM", "2:55 PM"
    ]
}

EVENT_ID = 1


def get_submissions():
    """Retrieve approved oral presentations from Supabase."""

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                s.submission_id,
                s.title,
                s.department,
                s.panel_id,
                s.panel_order,
                p.panel_title
            FROM submission s
            LEFT JOIN panel p
                ON s.panel_id = p.panel_id
            WHERE s.status = %s
              AND s.submission_type = %s
              AND s.event_id = %s
            ORDER BY s.submission_id
        """, ["approved", "oral", EVENT_ID])

        submissions = cursor.fetchall()

    projects = {}

    for (
        submission_id,
        title,
        department,
        panel_id,
        panel_order,
        panel_title
    ) in submissions:

        projects[submission_id] = {
            "title": title,
            "department": department,
            "panel_id": panel_id,
            "panel_order": panel_order,
            "panel_title": panel_title,
            "presenters": [],
            "mentors": []
        }

    # Retrieve presenters
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT submission_id, person_id
            FROM submission_presenter
        """)

        for submission_id, person_id in cursor.fetchall():
            if submission_id in projects:
                projects[submission_id]["presenters"].append(
                    person_id
                )

    # Retrieve faculty mentors
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT submission_id, person_id
            FROM submission_mentor
        """)

        for submission_id, person_id in cursor.fetchall():
            if submission_id in projects:
                projects[submission_id]["mentors"].append(
                    person_id
                )

    return projects


def generate_schedule(projects):
    """Generate a conflict-free oral presentation schedule."""

    # Create all available room/time slots
    slots = [
        (session, room, time)
        for session, times in sessions.items()
        for room in rooms
        for time in times
    ]

    print("Available slots:", len(slots))

    if not projects:
        print(
            "No approved oral presentations found. "
            "Check the event ID and database."
        )
        return None

    if len(projects) > len(slots):
        print("Not enough presentation slots.")
        return None

    model = cp_model.CpModel()

    schedule = {}

    # Create a Boolean variable for each
    # presentation and available slot
    for project_id in projects:
        for slot_index in range(len(slots)):
            schedule[project_id, slot_index] = (
                model.NewBoolVar(
                    f"project_{project_id}_slot_{slot_index}"
                )
            )

    # CONSTRAINT 1:
    # Each presentation must be scheduled exactly once
    for project_id in projects:
        model.Add(
            sum(
                schedule[project_id, i]
                for i in range(len(slots))
            ) == 1
        )

    # CONSTRAINT 2:
    # Only one presentation per room/time slot
    for slot_index in range(len(slots)):
        model.Add(
            sum(
                schedule[project_id, slot_index]
                for project_id in projects
            ) <= 1
        )

    # Group slots by session and time
    time_slots = defaultdict(list)

    for slot_index, (session, room, time) in enumerate(slots):
        time_slots[session, time].append(slot_index)

    # CONSTRAINT 3:
    # Presenters cannot be double-booked
    presenter_projects = defaultdict(set)

    for project_id, project in projects.items():
        for presenter_id in project["presenters"]:
            presenter_projects[presenter_id].add(project_id)

    for presenter_id, project_ids in presenter_projects.items():
        if len(project_ids) < 2:
            continue

        for slot_indices in time_slots.values():
            model.Add(
                sum(
                    schedule[project_id, i]
                    for project_id in project_ids
                    for i in slot_indices
                ) <= 1
            )

    # CONSTRAINT 4:
    # Faculty mentors cannot be double-booked
    mentor_projects = defaultdict(set)

    for project_id, project in projects.items():
        for mentor_id in project["mentors"]:
            mentor_projects[mentor_id].add(project_id)

    for mentor_id, project_ids in mentor_projects.items():
        if len(project_ids) < 2:
            continue

        for slot_indices in time_slots.values():
            model.Add(
                sum(
                    schedule[project_id, i]
                    for project_id in project_ids
                    for i in slot_indices
                ) <= 1
            )

    # Group presentations by panel
    panels = defaultdict(list)

    for project_id, project in projects.items():
        panel_id = project["panel_id"]

        if panel_id is not None:
            panels[panel_id].append(project_id)

    # CONSTRAINT 5:
    # Presentations in the same panel use the same room
    panel_rooms = {}

    for panel_id, panel_projects in panels.items():
        if len(panel_projects) < 2:
            continue

        panel_rooms[panel_id] = {}

        for room in rooms:
            panel_rooms[panel_id][room] = model.NewBoolVar(
                f"panel_{panel_id}_room_{room.replace(' ', '_')}"
            )

        model.Add(
            sum(panel_rooms[panel_id].values()) == 1
        )

        for project_id in panel_projects:
            for room in rooms:
                room_slots = [
                    i
                    for i, slot in enumerate(slots)
                    if slot[1] == room
                ]

                model.Add(
                    sum(
                        schedule[project_id, i]
                        for i in room_slots
                    ) == panel_rooms[panel_id][room]
                )

    # CONSTRAINT 6:
    # Track which sessions each panel uses
    session_used = {}

    for panel_id, panel_projects in panels.items():
        for session in sessions:

            session_used[panel_id, session] = model.NewBoolVar(
                f"panel_{panel_id}_{session.replace(' ', '_')}"
            )

            session_slots = [
                i
                for i, slot in enumerate(slots)
                if slot[0] == session
            ]

            count = sum(
                schedule[project_id, i]
                for project_id in panel_projects
                for i in session_slots
            )

            model.Add(
                count >= session_used[panel_id, session]
            )

            model.Add(
                count <= (
                    len(panel_projects)
                    * session_used[panel_id, session]
                )
            )

    # CONSTRAINT 7:
    # A panel cannot use Sessions 1 and 3
    # without also using Session 2
    for panel_id, panel_projects in panels.items():
        if len(panel_projects) < 2:
            continue

        model.Add(
            session_used[panel_id, "Session 1"]
            + session_used[panel_id, "Session 3"]
            <= 1 + session_used[panel_id, "Session 2"]
        )

    # CONSTRAINT 8:
    # Panel presentations must be consecutive
    # within each session
    for panel_id, panel_projects in panels.items():
        if len(panel_projects) < 2:
            continue

        for session, times in sessions.items():
            for room in rooms:

                occupied = []

                for time in times:
                    slot_index = slots.index(
                        (session, room, time)
                    )

                    occupied.append(
                        sum(
                            schedule[project_id, slot_index]
                            for project_id in panel_projects
                        )
                    )

                for start in range(len(times)):
                    for end in range(start + 2, len(times)):
                        for middle in range(start + 1, end):

                            model.Add(
                                occupied[start]
                                + occupied[end]
                                - 1
                                <= occupied[middle]
                            )

    # Create chronological positions independent
    # of the ordering of rooms in the slots list
    chronological_positions = {}

    position = 0

    for session, times in sessions.items():
        for time in times:
            chronological_positions[session, time] = position
            position += 1

    # CONSTRAINT 9:
    # Respect presentation order within each panel
    for panel_id, panel_projects in panels.items():

        ordered_projects = [
            project_id
            for project_id in panel_projects
            if projects[project_id]["panel_order"] is not None
        ]

        ordered_projects.sort(
            key=lambda project_id: (
                projects[project_id]["panel_order"],
                project_id
            )
        )

        for first, second in zip(
            ordered_projects,
            ordered_projects[1:]
        ):

            first_position = sum(
                chronological_positions[
                    slots[i][0], slots[i][2]
                ] * schedule[first, i]
                for i in range(len(slots))
            )

            second_position = sum(
                chronological_positions[
                    slots[i][0], slots[i][2]
                ] * schedule[second, i]
                for i in range(len(slots))
            )

            model.Add(
                first_position < second_position
            )

    # OBJECTIVE:
    # Minimize the number of sessions used by panels
    # and favor earlier slots within each session
    gap_penalty = []

    for panel_id, panel_projects in panels.items():
        if len(panel_projects) < 2:
            continue

        for session, times in sessions.items():
            for time_index, time in enumerate(times):
                for room in rooms:

                    slot_index = slots.index(
                        (session, room, time)
                    )

                    for project_id in panel_projects:
                        gap_penalty.append(
                            time_index
                            * schedule[project_id, slot_index]
                        )

    model.Minimize(
        1000 * sum(session_used.values())
        + sum(gap_penalty)
    )

    # Solve the scheduling problem
    solver = cp_model.CpSolver()

    solver.parameters.max_time_in_seconds = 60
    solver.parameters.num_search_workers = 8

    status = solver.Solve(model)

    print("Solver status:", solver.StatusName(status))

    if status not in (
        cp_model.OPTIMAL,
        cp_model.FEASIBLE
    ):
        print("No valid schedule could be generated.")
        return None

    # Extract final assignments
    results = []

    for project_id, project in projects.items():
        for slot_index, (session, room, time) in enumerate(slots):

            if solver.Value(
                schedule[project_id, slot_index]
            ) == 1:

                results.append({
                    "submission_id": project_id,
                    "title": project["title"],
                    "department": project["department"],
                    "panel_id": project["panel_id"],
                    "panel_title": project["panel_title"],
                    "panel_order": project["panel_order"],
                    "session": session,
                    "room": room,
                    "time": time
                })

    # Sort schedule chronologically
    session_order = list(sessions)

    results.sort(
        key=lambda item: (
            session_order.index(item["session"]),
            sessions[item["session"]].index(item["time"]),
            rooms.index(item["room"])
        )
    )

    return results


def display_schedule(results):
    """Display the generated presentation schedule."""

    if results is None:
        return

    print("\nSCAD PRESENTATION SCHEDULE")
    print("=" * 100)

    current_session = None

    for item in results:

        if item["session"] != current_session:
            current_session = item["session"]

            print(f"\n{current_session}")
            print("-" * 100)

        panel = item["panel_title"] or "No panel"

        print(
            f'{item["time"]:<10} | '
            f'{item["room"]:<15} | '
            f'{item["title"]} | '
            f'{panel}'
        )

    print("\nTotal presentations scheduled:", len(results))

    # Display panel assignments
    panel_assignments = defaultdict(list)

    for item in results:
        if item["panel_id"] is not None:
            panel_assignments[
                (item["panel_id"], item["panel_title"])
            ].append(item)

    print("\nPANEL ASSIGNMENTS")
    print("=" * 100)

    for (
        panel_id,
        panel_title
    ), presentations in sorted(
        panel_assignments.items(),
        key=lambda entry: entry[0][0]
    ):

        assigned_rooms = sorted(
            set(p["room"] for p in presentations)
        )

        assigned_sessions = sorted(
            set(p["session"] for p in presentations)
        )

        print(
            f"{panel_title or 'Unnamed panel'} "
            f"(ID {panel_id}): "
            f"{len(presentations)} presentations | "
            f"Rooms: {', '.join(assigned_rooms)} | "
            f"Sessions: {', '.join(assigned_sessions)}"
        )


def check_schedule_conflicts(results, projects):
    """Check for room, presenter, and mentor conflicts."""

    conflicts = []

    occupied_rooms = {}
    occupied_presenters = {}
    occupied_mentors = {}

    for item in results:

        project_id = item["submission_id"]
        time_key = (item["session"], item["time"])

        # Check room conflicts
        room_key = (*time_key, item["room"])

        if room_key in occupied_rooms:
            conflicts.append(
                f"Room conflict: {item['room']} at {time_key}"
            )

        occupied_rooms[room_key] = project_id

        # Check presenter conflicts
        for presenter_id in set(
            projects[project_id]["presenters"]
        ):

            key = (*time_key, presenter_id)

            if key in occupied_presenters:
                conflicts.append(
                    f"Presenter conflict: "
                    f"{presenter_id} at {time_key}"
                )

            occupied_presenters[key] = project_id

        # Check mentor conflicts
        for mentor_id in set(
            projects[project_id]["mentors"]
        ):

            key = (*time_key, mentor_id)

            if key in occupied_mentors:
                conflicts.append(
                    f"Mentor conflict: "
                    f"{mentor_id} at {time_key}"
                )

            occupied_mentors[key] = project_id

    print("\nSCHEDULE CONFLICT CHECK")
    print("=" * 50)

    if conflicts:
        for conflict in conflicts:
            print(conflict)
    else:
        print(
            "No room, presenter, or mentor conflicts found."
        )

    return conflicts


if __name__ == "__main__":

    projects = get_submissions()

    print(
        "Oral presentations from Supabase:",
        len(projects)
    )

    results = generate_schedule(projects)

    display_schedule(results)

    if results is not None:

        print("\nTotal scheduled:", len(results))

        conflicts = check_schedule_conflicts(
            results,
            projects
        )

        if len(results) != len(projects):
            print(
                "WARNING: Not all presentations "
                "were scheduled."
            )

        elif not conflicts:
            print(
                "\nSUCCESS: All approved oral "
                "presentations are scheduled "
                "without detected conflicts."
            )
