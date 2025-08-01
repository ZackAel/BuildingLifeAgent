import streamlit as st
from plyer import notification
from voice_assistant import VoiceAssistant
from tasks import load_tasks, save_tasks, complete_task, record_task_date
from goals import load_goals, save_goal
from mood import log_mood, get_today_mood
from streak import update_streak
from energy import compute_energy_index
from dashboard_widgets import (
    show_streak_progress,
    mood_trend_chart,
    task_completion_heatmap,
    energy_level_gauge,
)
import pandas as pd

st.set_page_config(page_title="BuildingLifeAgent Dashboard", layout="wide")
st.title("BuildingLifeAgent Dashboard")

with st.sidebar:
    st.header("Quick Actions")
    if st.button("Refresh Data"):
        st.rerun()
    if st.button("Update Streak"):
        update_streak()
        st.rerun()
    if st.button("Show Energy Index"):
        st.write(f"Energy: {compute_energy_index()}")

# --- TASKS SECTION ---
st.header("Tasks")
tasks = load_tasks()

df = pd.DataFrame({"Task": tasks})
edited = st.data_editor(
    df, num_rows="dynamic", use_container_width=True, key="task_editor"
)
updated_tasks = [t for t in edited["Task"].tolist() if t]
if updated_tasks != tasks:
    save_tasks(updated_tasks)
    tasks = updated_tasks
    st.rerun()

for i, task in enumerate(tasks, 1):
    if st.checkbox(task, key=f"task_{i}"):
        complete_task(task)
        tasks.remove(task)
        save_tasks(tasks)
        try:
            notification.notify(title="Task Completed", message=task)
        except NotImplementedError:
            st.toast(f"Task completed: {task}")
        st.rerun()

new_task = st.text_input("Add Task", key="add_task_input")
if st.button("Add Task", key="add_task_btn") and new_task:
    tasks.append(new_task)
    save_tasks(tasks)
    record_task_date(new_task)
    try:
        notification.notify(title="New Task Added", message=new_task)
    except NotImplementedError:
        st.toast(f"New task added: {new_task}")
    st.rerun()

# --- GOALS SECTION ---
st.header("Goals")
for goal in load_goals():
    st.write("- ", goal)
new_goal = st.text_input("Add Goal")
if st.button("Save Goal") and new_goal:
    save_goal(new_goal)
    try:
        notification.notify(title="Goal Saved", message=new_goal)
    except NotImplementedError:
        st.toast("Goal saved")
    st.rerun()

# --- MOOD SECTION ---
st.header("Mood Log")
current_mood, note = get_today_mood()
if current_mood:
    st.write(f"Today's mood: {current_mood} {note}")
else:
    st.write("No mood logged today.")

mood_entry = st.text_input("Log Mood")
if st.button("Log Mood") and mood_entry:
    log_mood(mood_entry)
    try:
        notification.notify(title="Mood Logged", message=mood_entry)
    except NotImplementedError:
        st.toast("Mood logged")
    st.rerun()

mood_trend_chart()
energy_level_gauge()
show_streak_progress()
task_completion_heatmap()

# --- VOICE COMMANDS ---
if st.sidebar.checkbox("Enable Voice Commands"):
    if 'voice_assistant' not in st.session_state:
        st.session_state.voice_assistant = VoiceAssistant()
    va: VoiceAssistant = st.session_state.voice_assistant
    continuous = st.sidebar.checkbox("Continuous Listening")
    if st.sidebar.button("Listen"):
        heard = va.listen_once()
        if heard:
            st.sidebar.write("Heard:", heard)
        else:
            st.sidebar.write("No command detected")
    if continuous:
        va.listen_continuously()


# --- JOURNAL SECTION ---
st.header("Journal")
recent_entries = []
try:
    from journal import log_entry, load_entries
    recent_entries = load_entries(5)
except Exception:
    log_entry = None

if recent_entries:
    st.subheader("Recent Entries")
    for timestamp, title, text in recent_entries:
        display_title = f" | {title}" if title else ""
        st.write(f"- {timestamp}{display_title} | {text}")

journal_title = st.text_input("Entry Title")
journal_text = st.text_area("New Entry")
if st.button("Save Entry") and journal_text:
    if log_entry:
        log_entry(journal_title, journal_text)
        notification.notify(title="Entry Saved", message=journal_text[:20])
    st.rerun()


fab_html = """
<style>
#fab {
  position: fixed;
  bottom: 40px;
  right: 40px;
  background-color: #6200ee;
  color: white;
  border-radius: 50%;
  width: 56px;
  height: 56px;
  font-size: 32px;
  text-align: center;
  line-height: 56px;
  text-decoration: none;
}
</style>
<a id="fab" href="#add_task_input">+</a>
"""
st.markdown(fab_html, unsafe_allow_html=True)
