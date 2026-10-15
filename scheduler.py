from ortools.sat.python import cp_model

model = cp_model.CpModel()

# test data
projects = {
    "Project A": "CS 310",
    "Project B": "CS 310",
    "Project C": "BIO 201"
}

rooms = ["Nicarry 202", "Nicarry 210"]

times = ["9:30 AM", "9:50 AM"]

sessions = ["Session 1", "Session 2", "Session 3"]

# decision variables
schedule = {}

for project in projects:
    for session in sessions:
        for room in rooms:
            for time in times:
                schedule[project, session, room, time] = model.NewBoolVar(
                    f"{project}_{session}_{room}_{time}"
                )

# constraints

# each project can only be scheduled once
for project in projects:
    model.Add(
        sum(
            schedule[project, session, room, time]
            for session in sessions
            for room in rooms
            for time in times
        ) == 1
    )

# each room can only have one project at a time
for session in sessions:
    for room in rooms:
        for time in times:
            model.Add(
                sum(
                    schedule[project, session, room, time]
                    for project in projects
                ) <= 1
            )
# keep projects from the same course in the same session and room
for project1 in projects:
    for project2 in projects:
        if project1 != project2 and projects[project1] == projects[project2]:
            for session in sessions:
                for room in rooms:
                    model.Add(
                        sum(schedule[project1, session, room, time] for time in times)
                        ==
                        sum(schedule[project2, session, room, time] for time in times)
                    )

# create solver and solve
solver = cp_model.CpSolver()

status = solver.Solve(model)

# print schedule
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    for project in projects:
        for session in sessions:
            for room in rooms:
                for time in times:
                    if solver.Value(schedule[project, session, room, time]) == 1:
                        print(
                            f"{project} ({projects[project]}) is scheduled in "
                            f"{session}, {room} at {time}"
                        )
else:
    print("No solution found.")