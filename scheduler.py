from ortools.sat.python import cp_model
model = cp_model.CpModel()

#test data
projects = ["Project A", "Project B", "Project C"]

rooms = ["Nicarry 202", "Nicarry 210"]

times = ["9:30 AM", "9:50 AM"]

#decision variables
schedule = {}

for project in projects:
    for room in rooms:
        for time in times:
            schedule[project, room, time] = model.NewBoolVar(
                f"{project}_{room}_{time}"
            )

#constraints
# Each project can only be scheduled once
for project in projects:
    model.Add(sum(schedule[project, room, time] 
    for room in rooms 
    for time in times) 
    == 1)
# Each room can only have one project scheduled at a time
for room in rooms:
    for time in times:
        model.Add(sum(schedule[project, room, time] 
        for project in projects) 
        <= 1)
#create solver and solve
solver = cp_model.CpSolver()
status = solver.Solve(model)
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    for project in projects:
        for room in rooms:
            for time in times:
                if solver.Value(schedule[project, room, time]) == 1:
                    print(f"{project} is scheduled in {room} at {time}")
else:
    print("No solution found.")