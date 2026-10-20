# CS401 - SCAD Program Auto Scheduler
![Static Badge](https://img.shields.io/badge/etown-capstone-blue)

Elizabethtown College | Computer Science Department | Capstone Projects

## Project Description

An auto scheduler for SCAD Day presentations at Etown College. Users will be directed to a SCAD homepage. On this homepage there will be a link to the public application form. On this form, users will be able to submit student' information, presentation information, group information, mentor information, panel information, etc. After the form is submitted, the information goes to the Supabase database. From here, an auto scheduler will make a SCAD schedule for the admin. This will include preferences and hard constraints to the best of its ability. Admins will be able to see any errors or conflictions within the scheduler. They will also be able to make edits to the schedule afterwards. Schedules will be made in a pdf form, and be shown on the website. 

## External Requirements

In order to build this project you first have to install:

-   [Python 3.10 or newer](https://www.python.org/downloads/) (tested with Python 3.11)
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

The project's Python packages (Django, psycopg, python-dotenv) are installed in the Setup step below.

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

6. Make sure the `event` table in Supabase has at least one event with a registration deadline in the future. Submissions are linked to the current event and will be rejected if no event exists or the deadline has passed.

## Running

1. Activate the virtual environment (every time you open a new terminal):

```bash
venv\Scripts\activate
```

2. Start the server:

```bash
python manage.py runserver
```

3. Open http://127.0.0.1:8000 in your browser to view the public application form.

To exit, press `Ctrl + C` in the terminal.

A red warning about "unapplied migrations" is expected. Our tables are managed in Supabase, so do not run `python manage.py migrate` without checking with the team first.

### Testing

1. Fill out the form with test data and click **Submit**.
2. A "Thank you! Your registration was received." message should appear on the page.
3. The terminal should print `Saved raw submission #... for ...`.
4. In Supabase, open **Table Editor → raw_submission** to confirm the new row was saved.

## Deployment

The project has not been deployed yet and currently runs locally for development and testing. Deployment instructions will be added here once a hosting platform is chosen.

Passwords and database credentials must **not** be put in Git. They belong in the `.env` file locally, or in the hosting platform's environment variable settings when deployed.

## Authors
Megan Benson bensonm@etown.edu
Anand Bum-Erdene bumerdenea@etown.edu
Isabella Edwards edwardsi@etown.edu

## Design ideal 
https://stitch.withgoogle.com/preview/7569896754880462826?node-id=d5b731638d134a9c9fa7dd3123af463b

