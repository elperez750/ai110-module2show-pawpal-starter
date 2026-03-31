# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Features

- **Chronological sorting** — Tasks are kept in sorted order at all times using `bisect.insort`, so every view is always chronologically correct without re-sorting.
- **Day & month schedule views** — Quickly browse what's planned for any day or month, grouped and labeled for readability.
- **Conflict detection** — The scheduler automatically detects when two tasks for the same pet overlap in time (using duration-aware comparison) and displays a warning banner in the UI.
- **Recurring tasks** — Mark a daily or weekly task complete and the next occurrence is automatically scheduled using Python's `timedelta`.
- **Filter by status or pet** — A dedicated Filter tab lets you view tasks by completion status (Pending, In Progress, Completed, Cancelled) or by pet name.
- **Mark complete in-app** — Every task card has a one-click complete button. Recurring tasks show a confirmation message with the next scheduled date.
- **Persistent state** — All data is saved to `pawpal_data.json` so the schedule survives browser refreshes and app restarts.
- **Pet management** — Add or remove pets at any time. Removing a pet cleanly cascades to remove or unlink their tasks from the scheduler.

## 📸 Demo

<a href="/course_images/ai110/pawpal_screenshot.png" target="_blank"><img src='/course_images/ai110/pawpal_screenshot.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

---

## Testing PawPal+

Run the full test suite from the project root:

```bash
python -m pytest tests/test_pawpal.py -v
```

### What the tests cover

| Area | Tests |
|---|---|
| **Task basics** | `complete()` sets status, `reschedule()` updates datetime, UUIDs are unique |
| **Pet basics** | Adding tasks increases count, upcoming tasks exclude past ones, empty pet returns `[]` |
| **Owner** | Duplicate pet raises error, remove works, removing nonexistent pet raises |
| **Sorting correctness** | Tasks inserted out of order are stored chronologically, day/month queries return correct sorted subsets |
| **Recurrence logic** | Daily task spawns next day, weekly spawns next week, non-recurring returns `None`, new task inherits pets |
| **Conflict detection** | Overlapping tasks for same pet flagged, exact same start time flagged, sequential tasks pass, different pets don't conflict, empty scheduler returns no conflicts |

### Confidence level

★★★★☆ — Core scheduling behaviors (sorting, recurrence, conflict detection) are well covered. Edge cases around multi-owner tasks, timezone handling, and the Streamlit persistence layer are not yet tested.
