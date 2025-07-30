import datetime
import streamlit as st
from collections import defaultdict
import pandas as pd

from streak import get_current_streak
from mood import MOOD_FILE
from energy import compute_energy_index
from tasks import load_tasks, get_task_age_days


def show_streak_progress(target_days: int = 7) -> None:
    """Display a simple progress bar for the current streak."""
    streak = get_current_streak()
    st.subheader("Streak")
    st.progress(min(streak / target_days, 1.0))
    st.write(f"{streak} day streak")


def _mood_score(m: str) -> int:
    m = m.lower()
    if any(w in m for w in ["happy", "great", "good", "motivated", "excited"]):
        return 1
    if any(w in m for w in ["sad", "bad", "tired", "stressed"]):
        return -1
    return 0


def mood_trend_chart(days: int = 7) -> None:
    """Line chart of recent mood scores."""
    try:
        rows = []
        with open(MOOD_FILE, "r") as f:
            for line in f:
                if not line.strip():
                    continue
                ts, mood, _ = line.strip().split(",", 2)
                date = ts.split(" ")[0]
                rows.append((date, _mood_score(mood)))
        if not rows:
            st.info("No mood data available")
            return
        by_date = defaultdict(list)
        for d, score in rows:
            by_date[d].append(score)
        dates = sorted(by_date.keys())[-days:]
        scores = [sum(by_date[d]) / len(by_date[d]) for d in dates]
        df = pd.DataFrame({"date": dates, "score": scores}).set_index("date")
        st.line_chart(df)
    except FileNotFoundError:
        st.info("No mood data available")


def task_completion_heatmap(days: int = 7) -> None:
    """Basic heatmap of task counts by day added."""
    try:
        tasks = load_tasks()
        today = datetime.date.today()
        counts = defaultdict(int)
        for t in tasks:
            age = get_task_age_days(t)
            day = today - datetime.timedelta(days=age)
            counts[day] += 1
        dates = [today - datetime.timedelta(days=i) for i in range(days - 1, -1, -1)]
        vals = [counts.get(d, 0) for d in dates]
        df = pd.DataFrame({"date": [d.isoformat() for d in dates], "tasks": vals}).set_index("date")
        st.bar_chart(df)
    except Exception:
        st.info("No task data available")


def energy_level_gauge() -> None:
    """Display current energy index as a gauge."""
    energy = compute_energy_index()
    st.subheader("Energy")
    st.metric("Energy", energy)
    st.progress(energy / 100)
