import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time

# Optional voice libraries
try:
    import speech_recognition as sr
except ImportError:  # pragma: no cover - optional dependency
    sr = None

try:
    import pyttsx3
except ImportError:  # pragma: no cover - optional dependency
    pyttsx3 = None

# Import all the agent modules
from tasks import (
    load_tasks,
    save_tasks,
    complete_task,
    record_task_date,
    get_task_age_days,
    load_tasks_with_difficulty,
)
from goals import load_goals, save_goal
from mood import log_mood, get_today_mood, journaling_prompt, ascii_mood
from streak import update_streak, get_current_streak
from energy import compute_energy_index
from relationships import contacts_needing_ping, log_interaction
from learning import skill_progress, skills_from_tasks
from guardrails import burnout_warning
from schedule_utils import intelligent_schedule
from gemini_api import ask_gemini, has_api_key
from motivation import get_motivational_message
from journal import log_entry, load_entries
from game_engine import quest_manager, character_system
from dashboard_widgets import mood_trend_chart


def speak(text: str) -> None:
    """Provide voice feedback if pyttsx3 is available."""
    if pyttsx3 is None:
        return
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


def handle_voice_command(command: str) -> None:
    """Route voice commands to task or mood handlers."""
    if not command:
        return
    cmd = command.lower()

    if cmd.startswith("add task"):
        task = cmd.replace("add task", "", 1).strip()
        if task:
            tasks = load_tasks()
            tasks.append(task)
            save_tasks(tasks)
            record_task_date(task)
            st.success(f"Task added: {task}")
            speak(f"Task added: {task}")
            st.rerun()
    elif cmd.startswith("log mood"):
        mood_text = cmd.replace("log mood", "", 1).strip()
        if mood_text:
            log_mood(mood_text)
            st.success(f"Mood logged: {mood_text}")
            speak(f"Mood logged: {mood_text}")
            st.rerun()
from voice_assistant import VoiceAssistant

# Page config with custom theme
st.set_page_config(
    page_title="AI Life Coach Dashboard", 
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "Your AI-powered personal productivity coach"
    }
)

# Initialize voice assistant
va = VoiceAssistant()

# Determine if AI features are available
AI_AVAILABLE = has_api_key()
if not AI_AVAILABLE:
    st.warning("GEMINI_API_KEY not found. AI-powered features are disabled.")

# Custom CSS for beautiful UI
st.markdown("""
<style>
    /* Glassmorphism effect */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .main-header {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        border: 1px solid rgba(255, 255, 255, 0.18);
    }
    
    .metric-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 0.5rem;
        box-shadow: 0 4px 20px 0 rgba(31, 38, 135, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.18);
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
    }
    
    .task-item {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .task-item:hover {
        transform: translateX(10px);
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
    }
    
    .chat-message {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 15px;
        padding: 1rem;
        margin: 0.5rem 0;
        animation: slideIn 0.3s ease;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .streak-flame {
        display: inline-block;
        animation: flicker 1.5s infinite;
    }
    
    @keyframes flicker {
        0%, 100% { transform: scale(1) rotate(-2deg); }
        50% { transform: scale(1.1) rotate(2deg); }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = datetime.now()
if 'show_schedule' not in st.session_state:
    st.session_state.show_schedule = False

# Load tasks with difficulty metadata
tasks_with_meta = load_tasks_with_difficulty()
tasks = [t["name"] for t in tasks_with_meta]

# Header with real-time stats
st.markdown('<div class="main-header">', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)

with col1:
    streak = get_current_streak()
    st.markdown(f"""
        <div class="metric-card">
            <h3><span class="streak-flame">🔥</span> Streak</h3>
            <h1>{streak} days</h1>
        </div>
    """, unsafe_allow_html=True)

with col2:
    energy = compute_energy_index()
    energy_emoji = "⚡" if energy > 70 else "🔋" if energy > 40 else "🪫"
    st.markdown(f"""
        <div class="metric-card">
            <h3>{energy_emoji} Energy</h3>
            <h1>{energy}%</h1>
        </div>
    """, unsafe_allow_html=True)

with col3:
    mood, _ = get_today_mood()
    mood_emoji = ascii_mood(mood) if mood else "😐"
    st.markdown(f"""
        <div class="metric-card">
            <h3>Mood {mood_emoji}</h3>
            <h1>{mood or 'Not logged'}</h1>
        </div>
    """, unsafe_allow_html=True)

with col4:
    completed_today = 0  # You can track this separately
    st.markdown(f"""
        <div class="metric-card">
            <h3>📋 Tasks</h3>
            <h1>{len(tasks)} pending</h1>
        </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Suggested tasks based on current energy
difficulty_pref = "short" if energy < 40 else "medium" if energy < 70 else "long"
suggested_tasks = [t["name"] for t in tasks_with_meta if t.get("difficulty", "medium") == difficulty_pref]

# Burnout warning if applicable
warning = burnout_warning()
if warning:
    st.error(f"⚠️ **Burnout Alert**: {warning}")

# Main content area with tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🎯 Dashboard", "💬 AI Chat", "📅 Schedule", "🎮 Gamification", 
    "👥 Relationships", "📊 Analytics"
])

with tab1:
    # Motivational message
    motivation = get_motivational_message()
    st.info(f"💡 **Daily Motivation**: {motivation}")
    
    # Two-column layout for tasks and goals
    task_col, goal_col = st.columns([2, 1])
    
    with task_col:
        st.subheader("📋 Today's Tasks")
        
        # Task input with quick add
        new_task = st.text_input("Quick add task", placeholder="Type task and press Enter", key="quick_task")
        if new_task:
            tasks.append(new_task)
            save_tasks(tasks)
            record_task_date(new_task)
            st.success(f"✅ Added: {new_task}")
            st.rerun()
        
        # Display tasks with age indicator
        for i, task in enumerate(tasks):
            age = get_task_age_days(task)
            age_indicator = "🔴" if age > 3 else "🟡" if age > 1 else "🟢"
            
            col1, col2, col3 = st.columns([0.1, 3, 0.5])
            with col1:
                if st.checkbox("", key=f"task_{i}"):
                    complete_task(task)
                    tasks.remove(task)
                    save_tasks(tasks)
                    st.balloons()
                    st.rerun()
            with col2:
                st.markdown(f"{age_indicator} {task}")
            with col3:
                st.caption(f"{age}d old")
        
        # AI Task Prioritization
        if AI_AVAILABLE:
            if st.button("🤖 AI Prioritize Tasks"):
                with st.spinner("Analyzing tasks..."):
                    prioritized = ask_gemini(
                        f"Prioritize these tasks considering it's {datetime.now().strftime('%H:%M')} "
                        f"and energy level is {energy}%: {', '.join(tasks)}"
                    )
                    st.markdown("**AI Suggested Order:**")
                    st.write(prioritized)
        else:
            st.button("🤖 AI Prioritize Tasks", disabled=True)
            st.info("Set GEMINI_API_KEY to enable AI prioritization.")

        # Suggested Tasks based on energy
        st.subheader("💡 Suggested Tasks")
        if suggested_tasks:
            for t in suggested_tasks:
                st.markdown(f"- {t}")
        else:
            st.caption("No tasks match your current energy.")
    
    with goal_col:
        st.subheader("🎯 Goals")
        goals = load_goals()
        for goal in goals:
            st.markdown(f"• {goal}")
        
        new_goal = st.text_input("Add goal", key="new_goal")
        if st.button("Save Goal"):
            save_goal(new_goal)
            st.success("Goal saved!")
            st.rerun()
        
        # Journaling prompt
        st.subheader("📝 Quick Reflection")
        prompt = journaling_prompt()
        st.info(prompt)
        reflection = st.text_area("Your thoughts:", key="reflection")
        if st.button("Save Reflection"):
            log_entry(prompt, reflection)
            st.success("Reflection saved!")

with tab2:
    st.subheader("💬 AI Life Coach Chat")

    if not AI_AVAILABLE:
        st.info("Set GEMINI_API_KEY to chat with the AI.")
    else:
        # Chat interface
        chat_container = st.container()

        # Input at the bottom
        user_input = st.text_input("Ask your AI coach anything...", key="chat_input")

        if user_input:
            # Add user message to history
            st.session_state.chat_history.append({"role": "user", "content": user_input})

            # Get AI response
            with st.spinner("Thinking..."):
                # Context-aware response
                context = f"""Current mood: {mood or 'unknown'}
Energy level: {energy}%
Pending tasks: {len(tasks)}
Current streak: {streak} days
Time: {datetime.now().strftime('%H:%M')}

User says: {user_input}"""

                response = ask_gemini(f"As a supportive life coach, respond to: {context}")
                st.session_state.chat_history.append({"role": "assistant", "content": response})

            st.rerun()

        # Display chat history
        with chat_container:
            for message in st.session_state.chat_history[-10:]:  # Show last 10 messages
                if message["role"] == "user":
                    st.markdown(f'<div class="chat-message">👤 **You**: {message["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-message">🤖 **Coach**: {message["content"]}</div>', unsafe_allow_html=True)

with tab3:
    st.subheader("📅 Intelligent Schedule")
    
    # Generate schedule button
    if st.button("🔄 Generate Optimal Schedule"):
        with st.spinner("Creating your perfect day..."):
            schedule = intelligent_schedule(tasks)
            st.session_state.show_schedule = True
            st.session_state.schedule = schedule
    
    # Display schedule
    if st.session_state.get('show_schedule'):
        st.markdown("### Your Optimized Day")
        
        # Parse schedule into interactive table for reordering
        raw_lines = [line for line in st.session_state.schedule.split('\n') if line.strip()]
        display_lines = []
        for line in raw_lines:
            if "Break" in line:
                display_lines.append(f"☕ {line}")
            elif "Lunch" in line:
                display_lines.append(f"🍽️ {line}")
            elif any(task in line for task in tasks):
                display_lines.append(f"📌 {line}")
            else:
                display_lines.append(f"📅 {line}")

        df_schedule = pd.DataFrame({"Schedule": display_lines})
        edited_df = st.data_editor(
            df_schedule,
            hide_index=True,
            use_container_width=True,
            key="schedule_editor",
        )

        if st.button("Save Schedule Order"):
            new_display = edited_df["Schedule"].tolist()
            stripped_lines = [
                line.split(" ", 1)[1] if line.startswith(("☕", "🍽️", "📌", "📅")) else line
                for line in new_display
            ]
            st.session_state.schedule = "\n".join(stripped_lines)

            # Update task order based on new schedule
            scheduled_tasks = []
            for line in stripped_lines:
                for task in tasks:
                    if task in line and task not in scheduled_tasks:
                        scheduled_tasks.append(task)
            remaining_tasks = [t for t in tasks if t not in scheduled_tasks]
            new_task_order = scheduled_tasks + remaining_tasks
            if new_task_order != tasks:
                save_tasks(new_task_order)
                tasks = new_task_order
            st.success("Schedule updated!")
            st.rerun()
        
        # Energy-based suggestions
        st.markdown("### ⚡ Energy-Based Recommendations")
        if energy >= 70:
            st.success("High energy! Perfect for deep work and challenging tasks.")
        elif energy >= 40:
            st.info("Moderate energy. Good for regular tasks and meetings.")
        else:
            st.warning("Low energy. Consider easy tasks or taking a break.")

with tab4:
    st.subheader("🎮 Gamification")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # XP and Level
        xp = quest_manager.get_xp()
        level = xp // 100
        progress = xp % 100
        
        st.markdown("### 📊 Experience Points")
        st.progress(progress / 100)
        st.metric("Level", level, f"{progress}/100 XP")
        
        # Virtual Pet
        st.markdown("### 🐾 Your Companion")
        pet_stage = character_system.get_pet_stage(streak)
        pet_emojis = {"egg": "🥚", "baby": "🐣", "teen": "🐥", "adult": "🐤", "legendary": "🦅"}
        st.markdown(f"**{pet_stage.title()}** {pet_emojis.get(pet_stage, '🐾')}")
        
        # Skills
        st.markdown("### 🎯 Unlocked Skills")
        skills = character_system.unlocked_skills(streak)
        for skill in skills:
            st.markdown(f"✅ {skill}")
    
    with col2:
        # Active Quests
        st.markdown("### 📜 Active Quests")
        quests = quest_manager.load_quests()
        for desc, xp in quests:
            st.markdown(f"• {desc} (+{xp} XP)")
        
        # Add quest
        quest_desc = st.text_input("New quest")
        quest_xp = st.number_input("XP reward", min_value=10, max_value=100, step=10)
        if st.button("Add Quest"):
            quest_manager.add_quest(quest_desc, quest_xp)
            st.success("Quest added!")
            st.rerun()

with tab5:
    st.subheader("👥 Relationship Manager")
    
    # Contacts needing attention
    stale_contacts = contacts_needing_ping()
    if stale_contacts:
        st.warning(f"📱 Reach out to: {', '.join(stale_contacts)}")
    
    # Log interaction
    contact_name = st.text_input("Who did you connect with?")
    if st.button("Log Interaction"):
        log_interaction(contact_name)
        st.success(f"Logged interaction with {contact_name}")
        st.rerun()
    
    # Skill progress from tasks
    st.markdown("### 📚 Skill Development")
    skills = skill_progress()
    if skills:
        df = pd.DataFrame(list(skills.items()), columns=['Skill', 'Tasks Completed'])
        fig = px.bar(df, x='Skill', y='Tasks Completed', title="Skills Progress")
        st.plotly_chart(fig)

with tab6:
    st.subheader("📊 Analytics & Insights")
    
    # Mood trend chart
    st.markdown("### 😊 Mood Trends")
    mood_trend_chart()
    
    # Task completion heatmap
    st.markdown("### 📅 Activity Heatmap")
    # You can implement a proper heatmap here
    
    # Weekly insights
    if AI_AVAILABLE and st.button("Generate Weekly Insights"):
        with st.spinner("Analyzing your week..."):
            insights_prompt = f"""Generate insights for:
- Streak: {streak} days
- Average energy: {energy}%
- Tasks completed: {completed_today}
- Current mood: {mood}
Provide actionable recommendations."""

            insights = ask_gemini(insights_prompt)
            st.markdown("### 🔍 AI Insights")
            st.write(insights)
    elif not AI_AVAILABLE:
        st.button("Generate Weekly Insights", disabled=True)
        st.info("Set GEMINI_API_KEY to enable AI insights.")

# Sidebar enhancements
with st.sidebar:
    st.markdown("### ⚡ Quick Actions")

    if va.mic:
        if st.button("🎤 Voice Command"):
            va.listen_once()
    else:
        st.warning("No microphone detected. Voice commands disabled.")

    # Mood logging
    mood_input = st.text_input("Log mood", placeholder="How are you feeling?")
    if st.button("Save Mood"):
        log_mood(mood_input)
        st.success("Mood logged!")
        st.rerun()
    
    # Quick timer
    if st.button("🍅 Start Pomodoro"):
        st.info("25-minute timer started!")
        # You can implement actual timer logic
    
    # Energy check-in
    if st.button("⚡ Energy Check-in"):
        current_energy = compute_energy_index()
        st.metric("Current Energy", f"{current_energy}%")
    
    # Mindfulness break
    if st.button("🧘 Mindfulness Break"):
        st.info("Take 3 deep breaths...")
        time.sleep(2)
        st.success("Great job! Feel refreshed?")

    # Voice control
    voice_enabled = st.checkbox("🎤 Voice Control")
    if voice_enabled:
        if sr is None:
            st.warning("SpeechRecognition not installed.")
        else:
            if st.button("Start Listening"):
                recognizer = sr.Recognizer()
                try:
                    with sr.Microphone() as source:
                        st.info("Listening for command...")
                        audio = recognizer.listen(source, phrase_time_limit=5)
                    phrase = recognizer.recognize_google(audio)
                    st.success(f"Heard: {phrase}")
                    handle_voice_command(phrase)
                except sr.UnknownValueError:
                    st.error("Sorry, I couldn't understand.")
                except sr.RequestError:
                    st.error("Speech service unavailable.")
                except OSError:
                    st.error("Microphone not found.")

    # Voice assistant toggle
    enable_voice = st.checkbox("🎙️ Enable Voice Assistant")
    if enable_voice:
        if 'voice_assistant' not in st.session_state:
            try:
                st.session_state.voice_assistant = VoiceAssistant()
            except Exception:
                st.session_state.voice_assistant = None
                st.warning("Microphone not available.")
        assistant = st.session_state.get('voice_assistant')
        if assistant:
            if st.button("🎧 Start Listening"):
                assistant.listen_continuously()
    else:
        st.session_state.pop('voice_assistant', None)
    
    # Settings
    st.markdown("### ⚙️ Settings")
    notification_enabled = st.checkbox("Enable notifications", value=True)
    theme = st.selectbox("Theme", ["Auto", "Light", "Dark"])
    
    # About
    st.markdown("### 📖 About")
    st.info("Your AI Life Coach v2.0\nBuilt with ❤️ for productivity")

# Auto-refresh every 30 seconds
if (datetime.now() - st.session_state.last_refresh).seconds > 30:
    st.session_state.last_refresh = datetime.now()
    st.rerun()