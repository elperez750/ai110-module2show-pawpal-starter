from pawpal_system import Scheduler, Owner, Pet, Task
from datetime import datetime, date

elliott = Owner(owner_id="1", name="Elliott")
mochi = Pet(pet_id="1", name="Mochi", species="cat", breed="Siamese", age=3)
benji = Pet(pet_id="2", name="Benji", species="dog", breed="Labrador", age=5)
elliott.add_pet(mochi)
elliott.add_pet(benji)
task1 = Task(name="Morning walk", date_time=datetime(2024, 6, 1, 8, 0), duration_minutes=30)
task2 = Task(name="Feed Mochi", date_time=datetime(2024, 6, 1, 9, 0), duration_minutes=15)
task3 = Task(name="Play with Benji", date_time=datetime(2024, 6, 1, 10, 0), duration_minutes=45)
mochi.add_task(task1)
mochi.add_task(task2)
benji.add_task(task3)
scheduler = Scheduler(scheduler_id="1")
scheduler.add_task(task1)
scheduler.add_task(task2)
scheduler.add_task(task3)


print(scheduler.display_for_day(date(2024, 6, 1)))