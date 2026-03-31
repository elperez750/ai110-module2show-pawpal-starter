import bisect
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from enum import Enum
from uuid import uuid4


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    name: str
    date_time: datetime
    task_id: str = field(default_factory=lambda: str(uuid4()))
    description: str = ""
    duration_minutes: int = 30
    location: str = ""
    is_recurring: bool = False
    recurrence_rule: str = ""
    status: TaskStatus = TaskStatus.PENDING
    pets_involved: list = field(default_factory=list)
    owners_involved: list = field(default_factory=list)

    def __lt__(self, other: "Task") -> bool:
        return self.date_time < other.date_time

    def next_occurrence(self) -> "Task | None":
        """Return a new Task for the next occurrence if this task is recurring, else None."""
        if not self.is_recurring:
            return None
        if self.recurrence_rule == "daily":
            delta = timedelta(days=1)
        elif self.recurrence_rule == "weekly":
            delta = timedelta(weeks=1)
        else:
            return None
        return Task(
            name=self.name,
            date_time=self.date_time + delta,
            description=self.description,
            duration_minutes=self.duration_minutes,
            location=self.location,
            is_recurring=self.is_recurring,
            recurrence_rule=self.recurrence_rule,
            pets_involved=list(self.pets_involved),
            owners_involved=list(self.owners_involved),
        )

    def complete(self):
        """Mark this task as completed."""
        self.status = TaskStatus.COMPLETED

    def reschedule(self, new_date_time: datetime):
        """Update the task's scheduled date and time."""
        self.date_time = new_date_time

    def add_pet(self, pet: "Pet"):
        """Add a pet to this task's participants."""
        self.pets_involved.append(pet)

    def add_owner(self, owner: "Owner"):
        """Add an owner to this task's participants."""
        self.owners_involved.append(owner)

    def summary(self) -> str:
        """Return a formatted single-line summary of this task."""
        status_symbols = {
            TaskStatus.PENDING:     "[ ]",
            TaskStatus.IN_PROGRESS: "[~]",
            TaskStatus.COMPLETED:   "[✓]",
            TaskStatus.CANCELLED:   "[✗]",
        }
        symbol = status_symbols[self.status]
        time_str = self.date_time.strftime("%I:%M %p")
        duration = f"{self.duration_minutes} min"
        location = f"  @ {self.location}" if self.location else ""
        pets = f"  Pets: {', '.join(p.name for p in self.pets_involved)}" if self.pets_involved else ""
        return f"  {symbol}  {time_str}  {self.name} ({duration}){location}{pets}"


@dataclass
class Pet:
    pet_id: str
    name: str
    species: str
    breed: str
    age: int
    weight: float = 0.0
    notes: str = ""
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task):
        """Add a task associated with this pet."""
        self.tasks.append(task)

    def get_upcoming_tasks(self) -> list[Task]:
        """Return all tasks scheduled in the future, sorted by date."""
        now = datetime.now()
        return sorted(
            [t for t in self.tasks if t.date_time > now],
            key=lambda t: t.date_time
        )


@dataclass
class Owner:
    owner_id: str
    name: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet):
        """Add a pet to this owner's list of pets."""
        if any(p.pet_id == pet.pet_id for p in self.pets):
            raise ValueError(f"Pet with id '{pet.pet_id}' is already registered to this owner.")
        self.pets.append(pet)

    def remove_pet(self, pet_id: str):
        """Remove a pet from this owner's list by pet ID."""
        for i, pet in enumerate(self.pets):
            if pet.pet_id == pet_id:
                self.pets.pop(i)
                return
        raise ValueError(f"No pet with id '{pet_id}' found for this owner.")


@dataclass
class Scheduler:
    scheduler_id: str
    all_tasks: list[Task] = field(default_factory=list)
    _date_index: dict = field(
        default_factory=lambda: defaultdict(list),
        init=False, repr=False, compare=False
    )
    _pet_index: dict = field(
        default_factory=lambda: defaultdict(list),
        init=False, repr=False, compare=False
    )

    def add_task(self, task: Task):
        """Insert a task in chronological order and update all indexes."""
        bisect.insort(self.all_tasks, task)
        self._date_index[task.date_time.date()].append(task)
        for pet in task.pets_involved:
            self._pet_index[pet.pet_id].append(task)

    def remove_task(self, task_id: str):
        """Remove a task from the scheduler and all indexes by task ID."""
        for i, task in enumerate(self.all_tasks):
            if task.task_id == task_id:
                self.all_tasks.pop(i)
                self._date_index[task.date_time.date()].remove(task)
                for pet in task.pets_involved:
                    self._pet_index[pet.pet_id].remove(task)
                return
        raise ValueError(f"No task with id '{task_id}' found in scheduler.")

    def remove_tasks_for_pet(self, pet_id: str):
        """Remove all tasks involving a pet and clean up orphaned tasks."""
        tasks_to_remove = self._pet_index.pop(pet_id, [])
        for task in tasks_to_remove:
            task.pets_involved = [p for p in task.pets_involved if p.pet_id != pet_id]
            self._date_index[task.date_time.date()].remove(task)
            if not task.pets_involved:
                self.all_tasks.remove(task)

    def get_tasks_for_day(self, target_date: date) -> list[Task]:
        """Return all tasks scheduled on the given date, sorted by time."""
        return sorted(self._date_index[target_date], key=lambda t: t.date_time)

    def get_tasks_for_month(self, month: int, year: int) -> list[Task]:
        """Return all tasks in the given month and year, sorted by date."""
        matching_dates = [
            d for d in self._date_index if d.month == month and d.year == year
        ]
        tasks = [t for d in matching_dates for t in self._date_index[d]]
        return sorted(tasks, key=lambda t: t.date_time)

    def get_tasks_for_pet(self, pet_id: str) -> list[Task]:
        """Return all tasks that involve the pet with the given ID."""
        return sorted(self._pet_index[pet_id], key=lambda t: t.date_time)

    def filter_by_status(self, status: TaskStatus) -> list[Task]:
        """Return all tasks matching the given status, in chronological order."""
        return [t for t in self.all_tasks if t.status == status]

    def filter_by_pet_name(self, pet_name: str) -> list[Task]:
        """Return all tasks involving a pet with the given name, in chronological order."""
        pet_name_lower = pet_name.lower()
        return [
            t for t in self.all_tasks
            if any(p.name.lower() == pet_name_lower for p in t.pets_involved)
        ]

    def mark_task_complete(self, task_id: str) -> "Task | None":
        """Mark a task complete and schedule the next occurrence if it is recurring.

        Returns the newly created Task if one was spawned, otherwise None.
        """
        for task in self.all_tasks:
            if task.task_id == task_id:
                task.complete()
                next_task = task.next_occurrence()
                if next_task is not None:
                    for pet in next_task.pets_involved:
                        pet.add_task(next_task)
                    self.add_task(next_task)
                return next_task
        raise ValueError(f"No task with id '{task_id}' found in scheduler.")

    def detect_conflicts(self) -> list[str]:
        """Return warning messages for tasks that overlap in time for the same pet.

        Overlap is detected when two tasks share a pet and their time windows intersect.
        """
        warnings = []
        tasks = self.all_tasks
        for i, a in enumerate(tasks):
            a_end = a.date_time + timedelta(minutes=a.duration_minutes)
            for b in tasks[i + 1:]:
                if b.date_time >= a_end:
                    break  # all_tasks is sorted, no later task can overlap with a
                shared_pets = [
                    p.name for p in a.pets_involved
                    if any(p.pet_id == q.pet_id for q in b.pets_involved)
                ]
                if shared_pets:
                    pets_str = ", ".join(shared_pets)
                    warnings.append(
                        f"Conflict: '{a.name}' ({a.date_time.strftime('%I:%M %p')}) and "
                        f"'{b.name}' ({b.date_time.strftime('%I:%M %p')}) "
                        f"overlap for {pets_str}."
                    )
        return warnings

    def get_overdue_tasks(self) -> list[Task]:
        """Return all pending/in-progress tasks whose date_time has passed."""
        now = datetime.now()
        overdue_statuses = {TaskStatus.PENDING, TaskStatus.IN_PROGRESS}
        return [
            t for t in self.all_tasks
            if t.date_time < now and t.status in overdue_statuses
        ]

    def display_for_day(self, target_date: date):
        """Print all tasks for a given day in an organized format."""
        tasks = self.get_tasks_for_day(target_date)
        header = target_date.strftime("%A, %B %d %Y")
        print(f"\n=== Tasks for {header} ===")
        if not tasks:
            print("  No tasks scheduled.")
        else:
            for task in tasks:
                print(task.summary())
        print()

    def display_for_month(self, month: int, year: int):
        """Print all tasks for a given month grouped by day."""
        tasks = self.get_tasks_for_month(month, year)
        month_label = date(year, month, 1).strftime("%B %Y")
        print(f"\n=== Tasks for {month_label} ===")
        if not tasks:
            print("  No tasks scheduled.")
            print()
            return
        current_day = None
        for task in tasks:
            task_date = task.date_time.date()
            if task_date != current_day:
                current_day = task_date
                print(f"\n  {task_date.strftime('%A, %B %d')}")
            print(task.summary())
        print()
