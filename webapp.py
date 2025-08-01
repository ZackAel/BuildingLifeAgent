import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time

# Import all the agent modules
from tasks import load_tasks, save_tasks, complete_task, record_task_date, get_task_age_days
from goals import load_goals, save_goal
from mood import log_mood, get_today_mood, journaling_prompt, ascii_mood
from streak import update_streak, get_current_streak
from energy import compute_energy_index
from relationships import contacts_needing_ping, log_interaction
from learning import skill_progress, skills_from_tasks
from guardrails import burnout_warning
from schedule_utils import intelligent_schedule
from gemini_api import ask_gemini
from motivation import get_motivational_message
from journal import log_entry, load_entries
from game_engine import quest_manager, character_system
from dashboard_widgets import mood_trend_chart

# Page config with custom theme
st.set_page_config(
    page_title="AI Life Coach Dashboard", 
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "Your AI-powered personal productivity coach"
    }
)

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
    tasks = load_tasks()
    completed_today = 0  # You can track this separately
    st.markdown(f"""
        <div class="metric-card">
            <h3>📋 Tasks</h3>
            <h1>{len(tasks)} pending</h1>
        </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

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
        if st.button("🤖 AI Prioritize Tasks"):
            with st.spinner("Analyzing tasks..."):
                prioritized = ask_gemini(
                    f"Prioritize these tasks considering it's {datetime.now().strftime('%H:%M')} "
                    f"and energy level is {energy}%: {', '.join(tasks)}"
                )
                st.markdown("**AI Suggested Order:**")
                st.write(prioritized)
    
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
        
        # Parse and display schedule
        schedule_lines = st.session_state.schedule.split('\n')
        for line in schedule_lines:
            if line.strip():
                # Color code different types of activities
                if "Break" in line:
                    st.markdown(f"☕ {line}")
                elif "Lunch" in line:
                    st.markdown(f"🍽️ {line}")
                elif any(task in line for task in tasks):
                    st.markdown(f"📌 {line}")
                else:
                    st.markdown(f"📅 {line}")
        
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
    if st.button("Generate Weekly Insights"):
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

# Sidebar enhancements
with st.sidebar:
    st.markdown("### ⚡ Quick Actions")
    
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