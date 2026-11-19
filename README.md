# CS401 - SCAD Program Auto Scheduler
![Static Badge](https://img.shields.io/badge/etown-capstone-blue)

Elizabethtown College | Computer Science Department | Capstone Projects

## Project Description

An auto scheduler for SCAD Day presentations at Etown College. Users start on a SCAD homepage, which links to the public application form and the public agenda. On the form, users submit students' information, presentation information, group information, mentor information, panel information, etc. Submitted forms are saved to the Supabase database and split into the project's tables.

In the admin site, the SCAD coordinator reviews and approves submissions, then generates a draft schedule with the auto scheduler (OR-Tools). The scheduler follows hard constraints and preferences as well as it can, and reports any conflicts it could not resolve. The coordinator can edit the draft and then publish it. Once published, the schedule appears on the public agenda page, where visitors can also save it as a PDF.

For SCAD coordinators, see the [Admin Guide](ADMIN_GUIDE.md).

## External Requirements

In order to build this project you first have to install:

-   [Python 3.13](https://www.python.org/downloads/) (OR-Tools does not support newer versions yet)
-   [Git](https://git-scm.com/downloads)
-   [Visual Studio Code](https://code.visualstudio.com/) (recommended)

When installing Python, check **"Add python.exe to PATH"** on the first screen of the installer.

To confirm Python is installed, run:

```bash
python --version
```

If you installed Python through Anaconda and `python` is not found, use the full path instead:

```bash
& "$env:USERPROFILE\anaconda3\python.exe" --version
```

The project's Python packages (Django, psycopg, python-dotenv, OR-Tools) are installed in the Setup step below.

You will also need access to the team's Supabase project. Ask a team member for the database connection details.

## Setup

These steps only need to be done once after cloning the repo.

1. Clone the repo and open the folder:

```bash
git clone https://github.com/Etown-CS/26-27_scad_program.git
cd 26-27_scad_program
```

2. Create a virtual environment:

```bash
python -m venv venv
```

(Anaconda users: `& "$env:USERPROFILE\anaconda3\python.exe" -m venv venv`)

3. Activate the virtual environment. You should see `(venv)` at the start of the terminal line:

```bash
venv\Scripts\activate
```

If PowerShell says "running scripts is disabled," switch the VS Code terminal to Command Prompt and run the command again.

4. Install the required packages:

```bash
pip install -r requirements.txt
```

5. Create a file named `.env` in the main project folder (the same folder as `manage.py`) with the Supabase connection details:

```
DB_NAME=postgres
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=5432
```

Get these values from a team member or from the Supabase dashboard (**Connect → Direct → Session pooler**). The `.env` file is ignored by Git and should **never** be committed.

6. Make sure the `event` table in Supabase has the upcoming SCAD as the event with the **latest event date**, and that its registration deadline is in the future. The form links every submission to the event with the latest date, and rejects submissions after that event's deadline.

7. Create an admin login for yourself (skip this if you already have one):

```bash
python manage.py createsuperuser
```

Follow the prompts for a username, email, and password. Use the same command to create a login for the SCAD coordinator.

## Running

1. Activate the virtual environment (every time you open a new terminal):

```bash
venv\Scripts\activate
```

2. Start the server:

```bash
python manage.py runserver
```

3. Open the pages in your browser:

| Page | Address |
|---|---|
| Homepage | http://127.0.0.1:8000/ |
| Application form | http://127.0.0.1:8000/register/ |
| Public agenda | http://127.0.0.1:8000/agenda/ |
| Admin site | http://127.0.0.1:8000/admin/ |

To exit, press `Ctrl + C` in the terminal.

A red warning about "unapplied migrations" is expected. Our tables are managed in Supabase, so do not run `python manage.py migrate` without checking with the team first.

### Importing the 2021 test data

The 2021 SCAD data in `scad_2021_scheduler_ready.csv` is used for testing. These scripts load it into Supabase. They have already been run, so only run them again after checking with the team:

- `import_scad.py` and `import_panels.py`: run with `python import_scad.py` or `python import_panels.py`
- `import_mentors.py`: run with `python manage.py shell -c "exec(open('import_mentors.py').read())"` (set `DRY_RUN = False` to actually save)

### Testing

**Application form**

1. Go to `/register/`, fill out the form with test data, and click **Submit**.
2. A "Thank you! Your registration was received." message should appear on the page.
3. The terminal should print `Saved raw submission #...` and `Processed into submission #...`.
4. In Supabase, open **Table Editor** and check `raw_submission`, `submission`, `person`, `submission_presenter`, and `submission_mentor` for the new rows.

**Scheduling and the public agenda**

1. In the admin site, mark some oral submissions as **Approved** in **Submissions**.
2. In **Events**, select the event, choose **Generate draft schedule for the selected event** from the Action menu, and click **Go**.
3. Check the draft in **Schedule assignments**. The public agenda at `/agenda/` should still say the schedule hasn't been published.
4. In **Schedules**, choose **Publish selected schedule**. The agenda should now list the presentations by session and room.
5. Choose **Set selected schedule back to draft** when you're done testing.

Testing writes to the shared Supabase database, so delete test rows afterward and check with the team before changing real data.

## Deployment

The project has not been deployed yet and currently runs locally for development and testing. Deployment instructions will be added here once a hosting platform is chosen.

Passwords and database credentials must **not** be put in Git. They belong in the `.env` file locally, or in the hosting platform's environment variable settings when deployed.

## Authors
Megan Benson bensonm@etown.edu
Anand Bum-Erdene bumerdenea@etown.edu
Isabella Edwards edwardsi@etown.edu

## Design ideal
https://stitch.withgoogle.com/preview/7569896754880462826?node-id=d5b731638d134a9c9fa7dd3123af463b