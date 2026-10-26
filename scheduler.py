import os
import django
from collections import defaultdict

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "scad.settings")
django.setup()

from django.db import connection
from ortools.sat.python import cp_model

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

sessions = {
    "Session 1": ["9:30 AM", "9:50 AM", "10:10 AM", "10:30 AM"],
    "Session 2": ["11:00 AM", "11:20 AM", "11:40 AM", "12:00 PM"],
    "Session 3": ["1:15 PM", "1:35 PM", "1:55 PM", "2:15 PM", "2:35 PM", "2:55 PM"]
}


def get_submissions():
    # get approved oral presentations from supabase
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
            LEFT JOIN panel p ON s.panel_id = p.panel_id
            WHERE s.status = %s
            AND s.submission_type = %s
            AND s.event_id = %s
            ORDER BY s.submission_id
        """, ["approved", "oral", 2])

        submissions = cursor.fetchall()

    projects = {}

    for submission_id, title, department, panel_id, panel_order, panel_title in submissions:
        projects[submission_id] = {
            "title": title,
            "department": department,
            "panel_id": panel_id,
            "panel_order": panel_order,
            "panel_title": panel_title
        }

    return projects


def generate_schedule(projects):
    # make all available presentation slots
    slots = [
        (session, room, time)
        for session, times in sessions.items()
        for room in rooms
        for time in times
    ]

    print("Available slots:", len(slots))

    if len(projects) > len(slots):
        print("Not enough presentation slots.")
        return None

    model = cp_model.CpModel()
    schedule = {}

    # create a variable for each presentation and slot
    for project in projects:
        for slot_index in range(len(slots)):
            schedule[project, slot_index] = model.NewBoolVar(
                f"project_{project}_slot_{slot_index}"
            )

    # each presentation gets one slot
    for project in projects:
        model.Add(
            sum(
                schedule[project, slot_index]
                for slot_index in range(len(slots))
            ) == 1
        )

    # only one presentation can use a slot
    for slot_index in range(len(slots)):
        model.Add(
            sum(
                schedule[project, slot_index]
                for project in projects
            ) <= 1
        )

    # group presentations by panel
    panels = defaultdict(list)

    for project_id, project in projects.items():
        if project["panel_id"] is not None:
            panels[project["panel_id"]].append(project_id)

    panel_rooms = {}

    # presentations in the same panel use the same room
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
                    i for i, slot in enumerate(slots)
                    if slot[1] == room
                ]

                model.Add(
                    sum(schedule[project_id, i] for i in room_slots)
                    == panel_rooms[panel_id][room]
                )

    # try to keep each panel within as few sessions as possible
    session_used = {}

    for panel_id, panel_projects in panels.items():
        if len(panel_projects) < 2:
            continue

        for session in sessions:
            session_used[panel_id, session] = model.NewBoolVar(
                f"panel_{panel_id}_{session.replace(' ', '_')}"
            )

            session_slots = [
                i for i, slot in enumerate(slots)
                if slot[0] == session
            ]

            count = sum(
                schedule[project_id, i]
                for project_id in panel_projects
                for i in session_slots
            )

            model.Add(count >= session_used[panel_id, session])
            model.Add(
                count <= len(panel_projects) * session_used[panel_id, session]
            )

    # Require panel presentations to be consecutive
    # within each session

    for panel_id, panel_projects in panels.items():
        if len(panel_projects) < 2:
            continue

        for session, times in sessions.items():
            for room in rooms:

                # Track whether this panel occupies each time slot
                occupied = []

                for time in times:
                    slot_index = slots.index((session, room, time))

                    occupied.append(
                        sum(
                            schedule[project_id, slot_index]
                            for project_id in panel_projects
                        )
                    )

                # If a panel occupies the first and last
                # slots of a range, it must occupy
                # every slot between them.
                for start in range(len(times)):
                    for end in range(start + 2, len(times)):
                        for middle in range(start + 1, end):

                            model.Add(
                                occupied[start] + occupied[end] - 1
                                <= occupied[middle]
                            )


    # minimize the number of sessions used by panels
    # presentations to happen earlier in each session
    gap_penalty = []

    for panel_id, panel_projects in panels.items():
        if len(panel_projects) < 2:
            continue

        for session, times in sessions.items():
            for time_index, time in enumerate(times):
                for room in rooms:
                    slot_index = slots.index((session, room, time))

                    for project_id in panel_projects:
                        gap_penalty.append(
                            time_index * schedule[project_id, slot_index]
                        )

    model.Minimize(
        1000 * sum(session_used.values())
        + sum(gap_penalty)
    )

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 60
    solver.parameters.num_search_workers = 8

    status = solver.Solve(model)

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        print("No valid schedule could be generated.")
        print("Solver status:", solver.StatusName(status))
        return None

    results = []

    # get the final assignments
    for project_id, project in projects.items():
        for slot_index, (session, room, time) in enumerate(slots):
            if solver.Value(schedule[project_id, slot_index]) == 1:
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

    # check which rooms each panel was assigned to
    panel_assignments = defaultdict(list)

    for item in results:
        if item["panel_id"] is not None:
            panel_assignments[item["panel_title"]].append(item)

    print("\nPANEL ASSIGNMENTS")
    print("=" * 100)

    for panel_title, presentations in sorted(panel_assignments.items()):
        panel_rooms = sorted(set(p["room"] for p in presentations))
        panel_sessions = sorted(set(p["session"] for p in presentations))

        print(
            f"{panel_title}: "
            f"{len(presentations)} presentations | "
            f"Rooms: {', '.join(panel_rooms)} | "
            f"Sessions: {', '.join(panel_sessions)}"
        )


if __name__ == "__main__":
    projects = get_submissions()

    print("Oral presentations from Supabase:", len(projects))

    results = generate_schedule(projects)

    display_schedule(results)