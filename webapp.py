import streamlit as st
from plyer import notification
import speech_recognition as sr
from tasks import load_tasks, save_tasks, complete_task
from goals import load_goals, save_goal
from mood import log_mood, get_today_mood

st.title("BuildingLifeAgent Dashboard")

# --- TASKS SECTION ---
st.header("Tasks")
tasks = load_tasks()
for i, task in enumerate(tasks, 1):
    if st.checkbox(task, key=f"task_{i}"):
        complete_task(task)
        tasks.remove(task)
        save_tasks(tasks)
        notification.notify(title="Task Completed", message=task)
        st.experimental_rerun()

new_task = st.text_input("Add Task")
if st.button("Add Task") and new_task:
    tasks.append(new_task)
    save_tasks(tasks)
    notification.notify(title="New Task Added", message=new_task)
    st.experimental_rerun()

# --- GOALS SECTION ---
st.header("Goals")
for goal in load_goals():
    st.write("- ", goal)
new_goal = st.text_input("Add Goal")
if st.button("Save Goal") and new_goal:
    save_goal(new_goal)
    notification.notify(title="Goal Saved", message=new_goal)
    st.experimental_rerun()

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
    notification.notify(title="Mood Logged", message=mood_entry)
    st.experimental_rerun()

# --- VOICE COMMANDS ---
if st.sidebar.checkbox("Enable Voice Commands"):
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    if st.sidebar.button("Listen"):
        with mic as source:
            audio = recognizer.listen(source, phrase_time_limit=5)
        try:
            command = recognizer.recognize_google(audio)
            st.sidebar.write("You said:", command)
            if command.lower().startswith("add task"):
                task_text = command[8:].strip()
                if task_text:
                    tasks = load_tasks()
                    tasks.append(task_text)
                    save_tasks(tasks)
                    notification.notify(title="Task Added", message=task_text)
                    st.experimental_rerun()
            elif command.lower().startswith("log mood"):
                mood_text = command[8:].strip()
                if mood_text:
                    log_mood(mood_text)
                    notification.notify(title="Mood Logged", message=mood_text)
                    st.experimental_rerun()
        except sr.UnknownValueError:
            st.sidebar.write("Could not understand audio")
        except Exception as e:
            st.sidebar.write("Error:", e)
