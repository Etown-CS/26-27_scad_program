# SCAD Auto Scheduler: Admin Guide

This guide is for the SCAD coordinator. It explains how to use the admin site to set up a SCAD event, review applications, create the schedule, and publish it to the public agenda.

No technical knowledge is needed. Everything is done by clicking through the admin site in a web browser.

---

## Contents

1. [How the system works](#1-how-the-system-works)
2. [Signing in](#2-signing-in)
3. [Finding your way around](#3-finding-your-way-around)
4. [Before registration opens: set up the event](#4-before-registration-opens-set-up-the-event)
5. [During registration: review applications](#5-during-registration-review-applications)
6. [After the deadline: create the draft schedule](#6-after-the-deadline-create-the-draft-schedule)
7. [Review and edit the draft](#7-review-and-edit-the-draft)
8. [Publish the schedule](#8-publish-the-schedule)
9. [Changes after publishing](#9-changes-after-publishing)
10. [The public pages](#10-the-public-pages)
11. [What the system doesn't do yet](#11-what-the-system-doesnt-do-yet)
12. [Getting help](#12-getting-help)

---

## 1. How the system works

```
Application form → Review applications → Generate draft schedule → Edit the draft → Publish → Public agenda
```

1. Students fill out the **application form** on the SCAD website.
2. You **review** each application in the admin site and mark it **Approved** or **Withdrawn**.
3. After the deadline, you click one button to **generate a draft schedule**. The scheduler places approved oral presentations into rooms and time slots. It keeps panels together and avoids putting a student in two places at once.
4. You **review and adjust** the draft.
5. You **publish** it. Only then does it appear on the public agenda page. While it's a draft, nobody else can see it.

---

## 2. Signing in

1. Go to the SCAD website and click **Admin Login** in the top menu. You can also go straight to the website address followed by `/admin/`.
2. Enter the username and password the project team gave you.
3. Click **Log in**.

To sign out, click **Log out** in the top right corner.

---

## 3. Finding your way around

After signing in, the home screen lists every area of the system:

| Area | What it's for |
|---|---|
| **Events** | Each year's SCAD: its name, date, and application deadline. The **Generate draft schedule** button is here. |
| **Submissions** | Every application, one per presentation or poster. This is where you approve or withdraw them. |
| **Raw submissions** | An exact copy of every form as it was submitted. Use it to check what someone typed, or to find applications that need attention. |
| **People** | Every student and faculty mentor in the system. |
| **Panels** | Groups of presentations that should be scheduled together. |
| **Schedules** | One schedule per event. This is where you **publish** it. |
| **Schedule assignments** | Each presentation's room and time on the schedule. This is where you edit the draft. |
| **Sessions** and **Locations** | Session blocks and rooms. The scheduler creates these for you. You usually don't need to change them. |

### Things that work the same on every list page

- **Search box** at the top: type a name, title, or department and press **Search**.
- **Filters** on the right side: narrow the list, for example by status or department.
- **Click a row** to open it, change it, and click **Save**.
- **Action dropdown**: tick the boxes next to rows, choose an action from the **Action** menu above the list, then click **Go**. Actions are how you approve, withdraw, generate, and publish.

---

## 4. Before registration opens: set up the event

The application form needs an event to link applications to.

1. Go to **Events** and click **Add event** in the top right.
2. Fill in:
   - **Event name**, for example `SCAD 2027`
   - **Event date**: the day of SCAD
   - **Registration deadline**: the date and time the form closes (Eastern time)
3. Click **Save**.

**Things to know:**

- The application form always uses the event with the **latest event date**. Make sure the upcoming SCAD has the latest date in the list, and double-check the year. A typo like 2021 instead of 2027 sends applications to the wrong event.
- After the deadline passes, the form automatically tells students: *"Registration is closed. Please contact the SCAD coordinator."*
- To give everyone more time, open the event, change the **Registration deadline**, and click **Save**.

---

## 5. During registration: review applications

### See new applications

Go to **Submissions**. Each row shows the title, type (oral presentation or poster), department, presenters, panel, and status. Click a title to see the full details, including the abstract, mentors, and comments.

Every new application starts as **Submitted**.

### Approve or withdraw

Only **Approved** oral presentations are placed on the schedule.

**One at a time:** change the **Status** dropdown right in the list, then click **Save** at the bottom of the page.

**Several at once:**
1. Tick the boxes next to the applications.
2. Choose **Mark selected as approved** (or **Mark selected as withdrawn**) from the **Action** menu.
3. Click **Go**.

Use the filters on the right (for example **By status: Submitted**) to see only the ones you haven't reviewed yet.

### Applications that need attention

Every form is saved in **Raw submissions** exactly as it was typed, so nothing is ever lost. Usually the system also turns each form into a submission automatically.

If something in a form couldn't be read, its status shows **needs_review** and it won't appear in Submissions. To find these:

1. Go to **Raw submissions**.
2. On the right, filter **By processing status → needs_review**.
3. Click one to see exactly what was submitted, and contact the project team so they can fix it.

### Late applications

The public form closes at the deadline. To accept an approved late application:

1. Open the event and move the **Registration deadline** a little later. Click **Save**.
2. Fill out the application form yourself on the student's behalf, or have the student do it right then.
3. Change the deadline back and click **Save**.

---

## 6. After the deadline: create the draft schedule

1. Make sure every oral presentation that should be on the schedule is marked **Approved**.
2. Go to **Events**.
3. Tick the box next to **one** event.
4. From the **Action** menu choose **Generate draft schedule for the selected event**, then click **Go**.
5. Wait a few seconds. A message appears at the top of the page:

| Message color | Meaning |
|---|---|
| **Green** | The draft was created with no problems. |
| **Yellow** | The draft was created, but some rules couldn't be met (for example, a room double-booked). The message lists them. Fix them while reviewing (Section 7). |
| **Red** | No draft was created. The message says why: no approved oral presentations, not enough time slots, or the schedule is already published or has locked presentations. |

**Things to know:**

- The draft is **not public**. Nobody else can see it until you publish it.
- **Generating again replaces the whole draft**, including any changes you made by hand. Generate first, then make your edits.
- To protect a draft from being replaced by accident, **lock** any presentation (Section 7). The system won't regenerate while anything is locked.
- You can't regenerate a published schedule. Set it back to draft first (Section 8).

---

## 7. Review and edit the draft

Go to **Schedule assignments**. Each row is one presentation, showing its time, room, title, presenters, panel, and session.

**Helpful filters on the right:**
- **By session name**: see Session 1, 2, or 3 on its own
- **By location**: see everything in one room

### Move a presentation

1. Click the presentation's title.
2. Change:
   - **Session**: the session block and room it belongs to (for example *Session 2 (Hoover 211)*)
   - **Start time** and **End time**: its time slot (each presentation is 20 minutes)
3. Click **Save**.

Change the session and the times together. The public agenda groups presentations by session and room, and lists them by start time.

> The system doesn't double-check your manual changes for conflicts. Before publishing, look through each room and session to make sure no two presentations share the same room and time, and no student is in two places at once.

### Remove a presentation from the schedule

Tick its box, choose **Delete selected schedule assignments** from the **Action** menu, click **Go**, then confirm.

This only removes it from the schedule. The application stays in Submissions.

### Lock a presentation

Tick the **Is locked** box in the list and click **Save**. Locked presentations stop the draft from being regenerated by accident, so your edits are safe.

---

## 8. Publish the schedule

When the draft looks right, usually about a week before SCAD:

1. Go to **Schedules**.
2. Tick the box next to the event's schedule.
3. Choose **Publish selected schedule** from the **Action** menu and click **Go**.

The schedule now appears on the public **Public Agenda** page.

**To hide it again**, choose **Set selected schedule back to draft** instead. The public agenda goes back to saying *"The schedule hasn't been published yet."*

---

## 9. Changes after publishing

Edits to a published schedule show up on the public agenda **right away**. There's no need to publish again.

| Situation | What to do |
|---|---|
| **A student withdraws** | In **Submissions**, mark it **Withdrawn**. Then in **Schedule assignments**, delete its row so it disappears from the agenda. |
| **A room or time changes** | In **Schedule assignments**, open the presentation and change its session, start time, and end time (Section 7). |
| **Big changes, or you want a fresh schedule** | Set the schedule back to **draft**, unlock any locked presentations, generate again, review, and publish. This replaces all manual edits. |

---

## 10. The public pages

| Page | Who uses it | What it shows |
|---|---|---|
| **Home** | Everyone | SCAD information, with links to the form and the agenda |
| **Submit Application** | Students | The application form. Closes automatically at the deadline. |
| **Public Agenda** | Everyone | Before publishing: the event date, the application deadline, and an outline of the day. After publishing: every presentation, grouped by session and room. |

On the published agenda, visitors can click **Save as PDF** to print the schedule or save a clean copy.

---

## 11. What the system doesn't do yet

- **Posters aren't placed automatically.** The scheduler only schedules oral presentations. Poster applications are collected and can be reviewed, but poster placement is still done by hand.
- **The room list and session times are set by the project team.** The scheduler currently uses Nicarry 202, 210, 228, 232 and Hoover 211–214, with Session 1 (9:30–10:50 AM), Session 2 (11:00 AM–12:20 PM), and Session 3 (1:15–3:15 PM). Contact the team to change rooms or times.
- **Presenters and mentors can't be changed from the admin site.** They come from the application form. Contact the team if one needs to be corrected.
- **The site isn't online yet.** It currently runs on the project team's computers for development and testing. The team will share the web address once it's hosted.

---

## 12. Getting help

Contact the project team:

- Megan Benson: bensonm@etown.edu (scheduler)
- Anand Bum-Erdene: bumerdenea@etown.edu (database and admin site)
- Isabella Edwards: edwardsi@etown.edu (application form and public agenda)