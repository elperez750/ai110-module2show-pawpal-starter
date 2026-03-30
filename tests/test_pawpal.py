from datetime import datetime
from pawpal_system import Task, Pet, TaskStatus


def test_complete_changes_status():
    task = Task(name="Morning Walk", date_time=datetime(2026, 3, 30, 9, 0))
    task.complete()
    assert task.status == TaskStatus.COMPLETED


def test_add_task_increases_pet_task_count():
    pet = Pet(pet_id="p1", name="Buddy", species="Dog", breed="Labrador", age=3)
    task = Task(name="Feeding Time", date_time=datetime(2026, 3, 30, 12, 0))
    pet.add_task(task)
    assert len(pet.tasks) == 1
