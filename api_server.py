from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import tasks
import goals
import mood
import energy
import streak
import motivation
import relationships
import learning
import guardrails
import schedule_utils
import journal

app = FastAPI(title="BuildingLifeAgent API")

class TaskItem(BaseModel):
    text: str

class MoodItem(BaseModel):
    mood: str
    note: str = ""

class ContactItem(BaseModel):
    name: str

class JournalItem(BaseModel):
    text: str
    title: str = ""


@app.get("/tasks")
def get_tasks():
    """Return list of tasks."""
    return tasks.load_tasks()

@app.post("/tasks")
def add_task(item: TaskItem):
    task_list = tasks.load_tasks()
    task_list.append(item.text)
    tasks.save_tasks(task_list)
    tasks.record_task_date(item.text)
    return {"status": "added"}

@app.post("/tasks/complete")
def complete_task(item: TaskItem):
    tasks.complete_task(item.text)
    remaining = [t for t in tasks.load_tasks() if t != item.text]
    tasks.save_tasks(remaining)
    return {"status": "completed"}

@app.get("/goals")
def get_goals():
    return goals.load_goals()

@app.post("/goals")
def add_goal(item: TaskItem):
    goals.save_goal(item.text)
    return {"status": "added"}

@app.post("/mood")
def log_mood_entry(entry: MoodItem):
    mood.log_mood(entry.mood, entry.note)
    return {"status": "logged"}

@app.get("/mood/today")
def get_mood_today():
    mood_val, note = mood.get_today_mood()
    return {"mood": mood_val, "note": note}

@app.get("/journaling_prompt")
def get_journaling_prompt():
    return {"prompt": mood.journaling_prompt()}

@app.get("/energy")
def get_energy():
    return {"energy": energy.compute_energy_index()}

@app.get("/energy/last")
def last_energy():
    return {"energy": energy.get_last_energy()}

@app.post("/streak/update")
def update_streak_endpoint():
    streak_val = streak.update_streak()
    return {"streak": streak_val}

@app.get("/streak")
def current_streak():
    return {"streak": streak.get_current_streak()}

@app.get("/motivation")
def motivational_message():
    return {"message": motivation.get_motivational_message()}

@app.post("/relationships/interactions")
def log_contact(item: ContactItem):
    relationships.log_interaction(item.name)
    return {"status": "logged"}

@app.get("/relationships/ping")
def stale_contacts():
    return relationships.contacts_needing_ping()

@app.get("/learning/progress")
def learning_progress():
    return learning.skill_progress()

@app.get("/learning/skills")
def tasks_skills():
    return list(learning.skills_from_tasks())

@app.get("/schedule")
def schedule():
    return schedule_utils.intelligent_schedule(tasks.load_tasks())

@app.get("/guardrails/burnout")
def burnout_check():
    return {"warning": guardrails.burnout_warning()}

@app.post("/journal")
def log_journal(entry: JournalItem):
    journal.log_entry(entry.title, entry.text)
    return {"status": "logged"}

@app.get("/journal")
def get_journal(count: int = 10):
    return journal.load_entries(count)
