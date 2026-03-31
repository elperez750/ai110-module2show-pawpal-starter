import json
from datetime import date, datetime, time
from pathlib import Path
from uuid import uuid4

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task, TaskStatus

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

DATA_FILE = Path("pawpal_data.json")

# --- Persistence helpers ---

def save_state():
    owner: Owner = st.session_state.owner
    scheduler: Scheduler = st.session_state.scheduler
    if owner is None:
        return
    data = {
        "owner": {"owner_id": owner.owner_id, "name": owner.name},
        "pets": [
            {
                "pet_id": p.pet_id,
                "name": p.name,
                "species": p.species,
                "breed": p.breed,
                "age": p.age,
                "weight": p.weight,
                "notes": p.notes,
            }
            for p in owner.pets
        ],
        "tasks": [
            {
                "task_id": t.task_id,
                "name": t.name,
                "description": t.description,
                "date_time": t.date_time.isoformat(),
                "duration_minutes": t.duration_minutes,
                "location": t.location,
                "is_recurring": t.is_recurring,
                "recurrence_rule": t.recurrence_rule,
                "status": t.status.value,
                "pet_ids": [p.pet_id for p in t.pets_involved],
            }
            for t in scheduler.all_tasks
        ],
    }
    DATA_FILE.write_text(json.dumps(data, indent=2))


def load_state() -> tuple[Owner | None, Scheduler]:
    if not DATA_FILE.exists():
        return None, Scheduler(scheduler_id="main")

    data = json.loads(DATA_FILE.read_text())

    owner_data = data.get("owner")
    if not owner_data:
        return None, Scheduler(scheduler_id="main")

    owner = Owner(owner_id=owner_data["owner_id"], name=owner_data["name"])

    pets_by_id: dict[str, Pet] = {}
    for p in data.get("pets", []):
        pet = Pet(
            pet_id=p["pet_id"],
            name=p["name"],
            species=p["species"],
            breed=p["breed"],
            age=p["age"],
            weight=p.get("weight", 0.0),
            notes=p.get("notes", ""),
        )
        owner.pets.append(pet)
        pets_by_id[pet.pet_id] = pet

    scheduler = Scheduler(scheduler_id="main")
    for t in data.get("tasks", []):
        task = Task(
            name=t["name"],
            date_time=datetime.fromisoformat(t["date_time"]),
            task_id=t["task_id"],
            description=t.get("description", ""),
            duration_minutes=t["duration_minutes"],
            location=t.get("location", ""),
            is_recurring=t.get("is_recurring", False),
            recurrence_rule=t.get("recurrence_rule", ""),
            status=TaskStatus(t["status"]),
        )
        for pet_id in t.get("pet_ids", []):
            if pet_id in pets_by_id:
                pet = pets_by_id[pet_id]
                task.pets_involved.append(pet)
                pet.tasks.append(task)
        task.owners_involved.append(owner)
        scheduler.add_task(task)  # populates _date_index and _pet_index

    return owner, scheduler


# --- Session state init (load from disk on first run) ---
if "scheduler" not in st.session_state:
    loaded_owner, loaded_scheduler = load_state()
    st.session_state.owner = loaded_owner
    st.session_state.scheduler = loaded_scheduler

scheduler: Scheduler = st.session_state.scheduler

# --- Header ---
st.title("🐾 PawPal+")
st.caption("A pet care planner for busy owners.")
st.divider()

# --- Owner setup ---
st.subheader("Owner")
with st.form("owner_form"):
    owner_name = st.text_input(
        "Your name",
        value=st.session_state.owner.name if st.session_state.owner else "",
        placeholder="e.g. Jordan",
    )
    if st.form_submit_button("Set Owner"):
        if owner_name.strip():
            if st.session_state.owner is None:
                st.session_state.owner = Owner(owner_id=str(uuid4()), name=owner_name.strip())
            else:
                st.session_state.owner.name = owner_name.strip()
            save_state()
            st.rerun()
        else:
            st.warning("Please enter a name.")

owner: Owner | None = st.session_state.owner

if owner is None:
    st.info("Set your name above to get started.")
    st.stop()

st.success(f"Welcome, **{owner.name}**!")

# --- Pets ---
st.divider()
st.subheader("Your Pets")

with st.form("pet_form"):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        pet_name = st.text_input("Name", placeholder="Mochi")
    with col2:
        species = st.selectbox("Species", ["Dog", "Cat", "Bird", "Other"])
    with col3:
        breed = st.text_input("Breed", placeholder="Shiba Inu")
    with col4:
        age = st.number_input("Age", min_value=0, max_value=30, value=1)

    if st.form_submit_button("Add Pet"):
        if pet_name.strip():
            pet = Pet(
                pet_id=str(uuid4()),
                name=pet_name.strip(),
                species=species,
                breed=breed.strip(),
                age=int(age),
            )
            try:
                owner.add_pet(pet)
                save_state()
                st.rerun()
            except ValueError as e:
                st.error(str(e))
        else:
            st.warning("Please enter a pet name.")

if owner.pets:
    cols = st.columns(len(owner.pets))
    for col, pet in zip(cols, owner.pets):
        with col:
            st.markdown(f"**{pet.name}**  \n{pet.species} · {pet.breed}  \nAge: {pet.age}")

    with st.form("remove_pet_form"):
        pet_to_remove = st.selectbox("Remove a pet", [p.name for p in owner.pets])
        if st.form_submit_button("Remove Pet", type="secondary"):
            pet = next(p for p in owner.pets if p.name == pet_to_remove)
            owner.remove_pet(pet.pet_id)
            scheduler.remove_tasks_for_pet(pet.pet_id)
            save_state()
            st.rerun()
else:
    st.info("No pets yet. Add one above.")

# --- Add task ---
if owner.pets:
    st.divider()
    st.subheader("Add a Task")

    with st.form("task_form"):
        col1, col2 = st.columns(2)
        with col1:
            task_name = st.text_input("Task name", value="Morning Walk")
            task_date = st.date_input("Date", value=date.today())
            task_time = st.time_input("Time", value=time(9, 0))
        with col2:
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=480, value=30)
            location = st.text_input("Location (optional)", placeholder="e.g. Local Park")
            selected_pet_name = st.selectbox("Pet", [p.name for p in owner.pets])

        if st.form_submit_button("Add Task"):
            if task_name.strip():
                selected_pet = next(p for p in owner.pets if p.name == selected_pet_name)
                task = Task(
                    name=task_name.strip(),
                    date_time=datetime.combine(task_date, task_time),
                    duration_minutes=int(duration),
                    location=location.strip(),
                )
                task.add_pet(selected_pet)
                task.add_owner(owner)
                selected_pet.add_task(task)
                scheduler.add_task(task)
                save_state()
                st.rerun()
            else:
                st.warning("Please enter a task name.")

# --- View schedule ---
st.divider()
st.subheader("Schedule")

STATUS_ICONS = {
    TaskStatus.PENDING:     "⬜",
    TaskStatus.IN_PROGRESS: "🔄",
    TaskStatus.COMPLETED:   "✅",
    TaskStatus.CANCELLED:   "❌",
}

day_tab, month_tab = st.tabs(["Day View", "Month View"])

with day_tab:
    view_date = st.date_input("Date", value=date.today(), key="day_picker")
    tasks = scheduler.get_tasks_for_day(view_date)
    st.markdown(f"#### {view_date.strftime('%A, %B %d %Y')}")
    if not tasks:
        st.info("No tasks scheduled for this day.")
    else:
        for task in tasks:
            icon = STATUS_ICONS[task.status]
            pets_str = ", ".join(p.name for p in task.pets_involved)
            location_str = f" @ {task.location}" if task.location else ""
            st.markdown(
                f"{icon} **{task.date_time.strftime('%I:%M %p')}** — {task.name} "
                f"({task.duration_minutes} min){location_str}  \n"
                f"*Pets: {pets_str}*"
            )

with month_tab:
    col1, col2 = st.columns(2)
    with col1:
        month = st.selectbox(
            "Month",
            list(range(1, 13)),
            index=date.today().month - 1,
            format_func=lambda m: date(2000, m, 1).strftime("%B"),
        )
    with col2:
        year = st.number_input("Year", min_value=2020, max_value=2035, value=date.today().year)

    tasks = scheduler.get_tasks_for_month(month, int(year))
    if not tasks:
        st.info("No tasks scheduled for this month.")
    else:
        current_day = None
        for task in tasks:
            task_date = task.date_time.date()
            if task_date != current_day:
                current_day = task_date
                st.markdown(f"#### {task_date.strftime('%A, %B %d')}")
            icon = STATUS_ICONS[task.status]
            pets_str = ", ".join(p.name for p in task.pets_involved)
            location_str = f" @ {task.location}" if task.location else ""
            st.markdown(
                f"{icon} **{task.date_time.strftime('%I:%M %p')}** — {task.name} "
                f"({task.duration_minutes} min){location_str}  \n"
                f"*Pets: {pets_str}*"
            )
