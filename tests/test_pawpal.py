from datetime import datetime, date

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task, TaskStatus


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def pet():
    return Pet(pet_id="p1", name="Buddy", species="Dog", breed="Labrador", age=3)


@pytest.fixture
def scheduler():
    return Scheduler(scheduler_id="test")


@pytest.fixture
def owner(pet):
    o = Owner(owner_id="o1", name="Jordan")
    o.add_pet(pet)
    return o


# ---------------------------------------------------------------------------
# Task – basic behavior
# ---------------------------------------------------------------------------

def test_complete_changes_status():
    task = Task(name="Morning Walk", date_time=datetime(2026, 3, 30, 9, 0))
    task.complete()
    assert task.status == TaskStatus.COMPLETED


def test_reschedule_updates_datetime():
    task = Task(name="Vet", date_time=datetime(2026, 3, 30, 10, 0))
    new_time = datetime(2026, 4, 1, 14, 0)
    task.reschedule(new_time)
    assert task.date_time == new_time


def test_task_ids_are_unique():
    t1 = Task(name="Walk", date_time=datetime(2026, 3, 30, 9, 0))
    t2 = Task(name="Walk", date_time=datetime(2026, 3, 30, 9, 0))
    assert t1.task_id != t2.task_id


# ---------------------------------------------------------------------------
# Pet – basic behavior
# ---------------------------------------------------------------------------

def test_add_task_increases_pet_task_count(pet):
    task = Task(name="Feeding Time", date_time=datetime(2026, 3, 30, 12, 0))
    pet.add_task(task)
    assert len(pet.tasks) == 1


def test_get_upcoming_tasks_excludes_past(pet):
    past = Task(name="Old Walk", date_time=datetime(2020, 1, 1, 9, 0))
    future = Task(name="Future Walk", date_time=datetime(2099, 1, 1, 9, 0))
    pet.add_task(past)
    pet.add_task(future)
    upcoming = pet.get_upcoming_tasks()
    assert len(upcoming) == 1
    assert upcoming[0].name == "Future Walk"


def test_pet_with_no_tasks_returns_empty_upcoming(pet):
    assert pet.get_upcoming_tasks() == []


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

def test_owner_add_duplicate_pet_raises(owner, pet):
    with pytest.raises(ValueError):
        owner.add_pet(pet)


def test_owner_remove_pet(owner, pet):
    owner.remove_pet(pet.pet_id)
    assert len(owner.pets) == 0


def test_owner_remove_nonexistent_pet_raises(owner):
    with pytest.raises(ValueError):
        owner.remove_pet("does-not-exist")


# ---------------------------------------------------------------------------
# Scheduler – sorting correctness
# ---------------------------------------------------------------------------

def test_tasks_added_out_of_order_are_sorted(scheduler, pet):
    t1 = Task(name="Lunch", date_time=datetime(2026, 3, 30, 12, 0))
    t2 = Task(name="Walk", date_time=datetime(2026, 3, 30, 8, 0))
    t3 = Task(name="Dinner", date_time=datetime(2026, 3, 30, 18, 0))
    for t in [t1, t2, t3]:
        t.add_pet(pet)
        scheduler.add_task(t)
    assert [t.name for t in scheduler.all_tasks] == ["Walk", "Lunch", "Dinner"]


def test_get_tasks_for_day_returns_chronological_order(scheduler, pet):
    t1 = Task(name="Dinner", date_time=datetime(2026, 3, 30, 18, 0))
    t2 = Task(name="Walk", date_time=datetime(2026, 3, 30, 7, 0))
    for t in [t1, t2]:
        t.add_pet(pet)
        scheduler.add_task(t)
    result = scheduler.get_tasks_for_day(date(2026, 3, 30))
    assert result[0].name == "Walk"
    assert result[1].name == "Dinner"


def test_get_tasks_for_day_excludes_other_days(scheduler, pet):
    t = Task(name="Walk", date_time=datetime(2026, 3, 31, 9, 0))
    t.add_pet(pet)
    scheduler.add_task(t)
    assert scheduler.get_tasks_for_day(date(2026, 3, 30)) == []


def test_get_tasks_for_month(scheduler, pet):
    march = Task(name="March Walk", date_time=datetime(2026, 3, 15, 9, 0))
    april = Task(name="April Walk", date_time=datetime(2026, 4, 1, 9, 0))
    for t in [march, april]:
        t.add_pet(pet)
        scheduler.add_task(t)
    result = scheduler.get_tasks_for_month(3, 2026)
    assert len(result) == 1
    assert result[0].name == "March Walk"


# ---------------------------------------------------------------------------
# Recurrence logic
# ---------------------------------------------------------------------------

def test_daily_recurrence_spawns_next_day(scheduler, pet):
    task = Task(
        name="Daily Walk",
        date_time=datetime(2026, 3, 30, 9, 0),
        is_recurring=True,
        recurrence_rule="daily",
    )
    task.add_pet(pet)
    pet.add_task(task)
    scheduler.add_task(task)

    next_task = scheduler.mark_task_complete(task.task_id)

    assert next_task is not None
    assert next_task.date_time == datetime(2026, 3, 31, 9, 0)
    assert next_task.status == TaskStatus.PENDING


def test_weekly_recurrence_spawns_next_week(scheduler, pet):
    task = Task(
        name="Weekly Grooming",
        date_time=datetime(2026, 3, 30, 10, 0),
        is_recurring=True,
        recurrence_rule="weekly",
    )
    task.add_pet(pet)
    pet.add_task(task)
    scheduler.add_task(task)

    next_task = scheduler.mark_task_complete(task.task_id)

    assert next_task is not None
    assert next_task.date_time == datetime(2026, 4, 6, 10, 0)


def test_non_recurring_task_does_not_spawn(scheduler, pet):
    task = Task(name="One-off Vet", date_time=datetime(2026, 3, 30, 11, 0))
    task.add_pet(pet)
    pet.add_task(task)
    scheduler.add_task(task)

    next_task = scheduler.mark_task_complete(task.task_id)

    assert next_task is None
    assert task.status == TaskStatus.COMPLETED


def test_recurring_task_inherits_pets(scheduler, pet):
    task = Task(
        name="Daily Feed",
        date_time=datetime(2026, 3, 30, 8, 0),
        is_recurring=True,
        recurrence_rule="daily",
    )
    task.add_pet(pet)
    pet.add_task(task)
    scheduler.add_task(task)

    next_task = scheduler.mark_task_complete(task.task_id)

    assert any(p.pet_id == pet.pet_id for p in next_task.pets_involved)


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

def test_overlapping_tasks_same_pet_detected(scheduler, pet):
    t1 = Task(name="Walk", date_time=datetime(2026, 3, 30, 9, 0), duration_minutes=60)
    t2 = Task(name="Feeding", date_time=datetime(2026, 3, 30, 9, 30), duration_minutes=15)
    for t in [t1, t2]:
        t.add_pet(pet)
        scheduler.add_task(t)
    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 1
    assert "Buddy" in conflicts[0]


def test_exact_same_start_time_detected(scheduler, pet):
    t1 = Task(name="Walk", date_time=datetime(2026, 3, 30, 9, 0), duration_minutes=30)
    t2 = Task(name="Feeding", date_time=datetime(2026, 3, 30, 9, 0), duration_minutes=15)
    for t in [t1, t2]:
        t.add_pet(pet)
        scheduler.add_task(t)
    assert len(scheduler.detect_conflicts()) == 1


def test_sequential_tasks_no_conflict(scheduler, pet):
    t1 = Task(name="Walk", date_time=datetime(2026, 3, 30, 9, 0), duration_minutes=30)
    t2 = Task(name="Feeding", date_time=datetime(2026, 3, 30, 9, 30), duration_minutes=15)
    for t in [t1, t2]:
        t.add_pet(pet)
        scheduler.add_task(t)
    assert scheduler.detect_conflicts() == []


def test_different_pets_no_conflict(scheduler):
    pet_a = Pet(pet_id="pa", name="Buddy", species="Dog", breed="Lab", age=2)
    pet_b = Pet(pet_id="pb", name="Mochi", species="Cat", breed="Siamese", age=1)
    t1 = Task(name="Walk", date_time=datetime(2026, 3, 30, 9, 0), duration_minutes=60)
    t2 = Task(name="Feed", date_time=datetime(2026, 3, 30, 9, 30), duration_minutes=15)
    t1.add_pet(pet_a)
    t2.add_pet(pet_b)
    scheduler.add_task(t1)
    scheduler.add_task(t2)
    assert scheduler.detect_conflicts() == []


def test_no_tasks_no_conflicts(scheduler):
    assert scheduler.detect_conflicts() == []
