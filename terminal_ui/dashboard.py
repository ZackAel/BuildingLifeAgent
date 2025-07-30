from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, ListView, ListItem
from textual.containers import Horizontal
from tasks import load_tasks
from goals import load_goals
from mood import get_today_mood, ascii_mood
from energy import compute_energy_index
from streak import get_current_streak

class Dashboard(App):
    """Simple Textual dashboard for BuildingLifeAgent."""

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        tasks = load_tasks()
        tasks_list = ListView(*[ListItem(Static(t)) for t in tasks])
        goals_list = ListView(*[ListItem(Static(g)) for g in load_goals()])

        mood, note = get_today_mood()
        mood_view = Static(f"Mood: {mood or 'None'} {ascii_mood(mood)}")
        energy = compute_energy_index()
        streak = get_current_streak()
        stats_view = Static(f"Streak: {streak}\nEnergy: {energy}")

        container = Horizontal(tasks_list, goals_list, mood_view, stats_view)
        yield container
        yield Footer()

if __name__ == "__main__":
    Dashboard().run()
