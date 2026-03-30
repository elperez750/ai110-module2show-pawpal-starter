# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**
    So my initial design for the PawPal+ app included the following classes: Owner, Pet, Schedule, and Task. The Owner class is minimal, since the main focus of the app is scheduling events for pets. The pet class has basic information as well such as name and breed. The Task and Schedule classes are where the main logic of the app is. The Task class represents an individual event, such as a walk or feeding time, and includes information such as the time of the event and any special instructions. The Schedule class manages a list of tasks for each pet owner and includes methods for adding, editing, and deleting tasks, as well as viewing the schedule for a specific day or week.


    Some of the main actions that the pawpaw app must be able to do are:
    - Create a new schedule for a pet owner
    - Create a new event for a pet, such as a walk or a feeding time
    - View the schedule for a pet owner, including all events for their pets (Split into two views: one for the current day, and one for the week)
    - Edit or delete existing events in the schedule
    - Add information on the pet, such as their name, breed, and any special needs or preferences
    



- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
