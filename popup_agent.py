import json
import datetime
import tkinter as tk
from tkinter import ttk

# Import all agent modules
from data_utils import ensure_file
from journal import log_entry, load_entries
from tasks import load_tasks, save_tasks, complete_task, load_completed_tasks
from motivation import get_motivational_message
  

SETTINGS_FILE = ensure_file("settings.json")
GOALS_FILE = ensure_file("goals_extended.json")


class PopupAgent:
    """Minimalist popup dashboard for journaling, tasks and goals."""

    THEMES = {
        "light": {
            "bg": "#f5f5f5",
            "accent": "#1976d2",
            "text": "#222222",
            "secondary": "#e0e0e0",
        },
        "dark": {
            "bg": "#1e1e1e",
            "accent": "#bb86fc",
            "text": "#ffffff",
            "secondary": "#333333",
        },
        "pastel": {
            "bg": "#fdf6f0",
            "accent": "#a3c4f3",
            "text": "#2e2e2e",
            "secondary": "#e3d5ca",
        },
    }

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Life Dashboard")
        self.root.geometry("420x520")
        self.root.resizable(False, False)

        self.settings = self._load_settings()
        self.theme = self.settings.get("theme", "pastel")
        self.apply_theme(self.theme)

        self.tasks = load_tasks()
        self.completed_tasks = load_completed_tasks()
        self.goals = self._load_goals()

        self._build_ui()
        self.refresh_all()



        # Keyboard shortcuts
        self.root.bind("<Control-j>", lambda e: self.notebook.select(self.journal_frame))
        self.root.bind("<Control-t>", lambda e: self.notebook.select(self.tasks_frame))
        self.root.bind("<Control-g>", lambda e: self.notebook.select(self.goals_frame))
    # ------------------------------------------------------------------
    # Data helpers
    def _load_settings(self) -> dict:
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_settings(self) -> None:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.settings, f)

    def _load_goals(self) -> list:
        try:
            with open(GOALS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _save_goals(self) -> None:
        with open(GOALS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.goals, f)

    # ------------------------------------------------------------------
    # UI construction
    def apply_theme(self, name: str) -> None:
        colors = self.THEMES.get(name, self.THEMES["pastel"])
        self.colors = colors
        self.root.configure(bg=colors["bg"])
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background=colors["bg"], borderwidth=0)
        style.configure("TNotebook.Tab", background=colors["secondary"], foreground=colors["text"], padding=[10, 5])
        style.map("TNotebook.Tab", background=[("selected", colors["accent"])] )

    def _build_ui(self) -> None:
        top = tk.Frame(self.root, bg=self.colors["bg"])
        top.pack(fill="x", pady=(10, 0))

        self.time_label = tk.Label(top, bg=self.colors["bg"], fg=self.colors["text"], font=("Arial", 10))
        self.time_label.pack(side="right", padx=10)

        theme_menu = ttk.OptionMenu(top, tk.StringVar(value=self.theme), self.theme,
                                    *self.THEMES.keys(), command=self.switch_theme)
        theme_menu.pack(side="left", padx=10)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.dashboard_frame = tk.Frame(self.notebook, bg=self.colors["bg"])
        self.journal_frame = tk.Frame(self.notebook, bg=self.colors["bg"])
        self.tasks_frame = tk.Frame(self.notebook, bg=self.colors["bg"])
        self.goals_frame = tk.Frame(self.notebook, bg=self.colors["bg"])

        self.notebook.add(self.dashboard_frame, text="Daily")
        self.notebook.add(self.journal_frame, text="Journal")
        self.notebook.add(self.tasks_frame, text="Tasks")
        self.notebook.add(self.goals_frame, text="Goals")

        # Dashboard
        self.dashboard_text = tk.Label(self.dashboard_frame, bg=self.colors["bg"], fg=self.colors["text"], justify="left")
        self.dashboard_text.pack(anchor="nw", padx=10, pady=10)

        # Journal tab
        journal_top = tk.Frame(self.journal_frame, bg=self.colors["bg"])
        journal_top.pack(fill="x", padx=5, pady=5)
        self.journal_entry = ttk.Entry(journal_top)
        self.journal_entry.pack(fill="x", side="left", expand=True)
        self.journal_entry.bind("<Return>", lambda e: self.add_journal())
        add_journal_btn = ttk.Button(journal_top, text="Add", command=self.add_journal)
        add_journal_btn.pack(side="left", padx=5)

        journal_list_frame = tk.Frame(self.journal_frame, bg=self.colors["bg"])
        journal_list_frame.pack(fill="both", expand=True, padx=5, pady=5)
        self.journal_list = tk.Listbox(journal_list_frame)
        scrollbar = ttk.Scrollbar(journal_list_frame, orient="vertical", command=self.journal_list.yview)
        self.journal_list.config(yscrollcommand=scrollbar.set)
        self.journal_list.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Tasks tab
        task_top = tk.Frame(self.tasks_frame, bg=self.colors["bg"])
        task_top.pack(fill="x", padx=5, pady=5)
        self.task_entry = ttk.Entry(task_top)
        self.task_entry.pack(fill="x", side="left", expand=True)
        self.task_entry.bind("<Return>", lambda e: self.add_task())
        add_task_btn = ttk.Button(task_top, text="Add", command=self.add_task)
        add_task_btn.pack(side="left", padx=5)

        task_list_frame = tk.Frame(self.tasks_frame, bg=self.colors["bg"])
        task_list_frame.pack(fill="both", expand=True, padx=5, pady=5)
        self.task_list = tk.Listbox(task_list_frame)
        self.task_list.pack(side="left", fill="both", expand=True)
        task_scroll = ttk.Scrollbar(task_list_frame, orient="vertical", command=self.task_list.yview)
        self.task_list.config(yscrollcommand=task_scroll.set)
        task_scroll.pack(side="right", fill="y")
        self.task_list.bind("<Double-Button-1>", lambda e: self.mark_task_done())

        task_btn_frame = tk.Frame(self.tasks_frame, bg=self.colors["bg"])
        task_btn_frame.pack(pady=5)
        ttk.Button(task_btn_frame, text="Done", command=self.mark_task_done).pack(side="left", padx=5)
        ttk.Button(task_btn_frame, text="Delete", command=self.delete_task).pack(side="left", padx=5)

        # Goals tab
        goal_top = tk.Frame(self.goals_frame, bg=self.colors["bg"])
        goal_top.pack(fill="x", padx=5, pady=5)
        self.goal_entry = ttk.Entry(goal_top, width=20)
        self.goal_entry.pack(side="left", padx=2, expand=True, fill="x")
        self.goal_entry.insert(0, "Goal")
        self.start_entry = ttk.Entry(goal_top, width=10)
        self.start_entry.pack(side="left", padx=2)
        self.start_entry.insert(0, datetime.date.today().isoformat())
        self.target_entry = ttk.Entry(goal_top, width=10)
        self.target_entry.pack(side="left", padx=2)
        self.target_entry.insert(0, (datetime.date.today() + datetime.timedelta(days=7)).isoformat())
        goal_add_btn = ttk.Button(goal_top, text="Add", command=self.add_goal)
        goal_add_btn.pack(side="left", padx=2)
        self.target_entry.bind("<Return>", lambda e: self.add_goal())

        self.goal_tree = ttk.Treeview(self.goals_frame, columns=("start", "target", "done"), show="headings")
        self.goal_tree.heading("start", text="Start")
        self.goal_tree.heading("target", text="Target")
        self.goal_tree.heading("done", text="Done")
        self.goal_tree.pack(fill="both", expand=True, padx=5, pady=5)

        goal_btn_frame = tk.Frame(self.goals_frame, bg=self.colors["bg"])
        goal_btn_frame.pack(pady=5)
        ttk.Button(goal_btn_frame, text="Complete", command=self.complete_goal).pack(side="left", padx=5)
        ttk.Button(goal_btn_frame, text="Delete", command=self.delete_goal).pack(side="left", padx=5)

        # Motivation panel
        self.motivation_label = tk.Label(self.root, bg=self.colors["secondary"], fg=self.colors["text"], wraplength=380)
        self.motivation_label.pack(fill="x", padx=10, pady=(0,10))

    # ------------------------------------------------------------------
    def switch_theme(self, name: str) -> None:
        self.theme = name
        self.settings["theme"] = name
        self._save_settings()
        self.apply_theme(name)

    # ------------------------------------------------------------------
    # Journal handlers
    def add_journal(self) -> None:
        text = self.journal_entry.get().strip()
        if not text:
            return
        log_entry("", text)
        self.journal_entry.delete(0, tk.END)
        self.refresh_journal()
        self.update_dashboard()
        self.update_motivation()

    def refresh_journal(self) -> None:
        self.journal_list.delete(0, tk.END)
        for ts, title, text in reversed(load_entries(50)):
            display = f"{ts} - {text}"
            self.journal_list.insert(tk.END, display)

    # ------------------------------------------------------------------
    # Task handlers
    def add_task(self) -> None:
        task = self.task_entry.get().strip()
        if not task:
            return
        self.tasks.append(task)
        save_tasks(self.tasks)
        self.task_entry.delete(0, tk.END)
        self.refresh_tasks()
        self.update_dashboard()
        self.update_motivation()

    def mark_task_done(self) -> None:
        selection = self.task_list.curselection()
        if not selection:
            return
        idx = selection[0]
        task = self.tasks.pop(idx)
        complete_task(task)
        save_tasks(self.tasks)
        self.refresh_tasks()
        self.completed_tasks.append(task)
        self.update_dashboard()
        self.update_motivation()

    def delete_task(self) -> None:
        selection = self.task_list.curselection()
        if not selection:
            return
        idx = selection[0]
        self.tasks.pop(idx)
        save_tasks(self.tasks)
        self.refresh_tasks()
        self.update_dashboard()
        self.update_motivation()

    def refresh_tasks(self) -> None:
        self.task_list.delete(0, tk.END)
        for t in self.tasks:
            self.task_list.insert(tk.END, t)

    # ------------------------------------------------------------------
    # Goal handlers
    def add_goal(self) -> None:
        name = self.goal_entry.get().strip()
        start = self.start_entry.get().strip()
        target = self.target_entry.get().strip()
        if not name:
            return
        goal = {"name": name, "start": start, "target": target, "done": False}
        self.goals.append(goal)
        self._save_goals()
        self.refresh_goals()
        self.goal_entry.delete(0, tk.END)
        self.update_dashboard()
        self.update_motivation()

    def complete_goal(self) -> None:
        item = self.goal_tree.focus()
        if not item:
            return
        idx = int(self.goal_tree.item(item, 'text'))
        self.goals[idx]["done"] = True
        self._save_goals()
        self.refresh_goals()
        self.update_dashboard()
        self.update_motivation()

    def delete_goal(self) -> None:
        item = self.goal_tree.focus()
        if not item:
            return
        idx = int(self.goal_tree.item(item, 'text'))
        self.goals.pop(idx)
        self._save_goals()
        self.refresh_goals()
        self.update_dashboard()
        self.update_motivation()

    def refresh_goals(self) -> None:
        for item in self.goal_tree.get_children():
            self.goal_tree.delete(item)
        for idx, g in enumerate(self.goals):
            self.goal_tree.insert("", "end", text=str(idx), values=(g["start"], g["target"], "✔" if g.get("done") else ""))

    # ------------------------------------------------------------------
    # Dashboard & motivation
    def update_time(self) -> None:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=now)
        self.root.after(1000, self.update_time)

    def update_dashboard(self) -> None:
        last_entry = load_entries(1)
        journal_text = last_entry[0][2] if last_entry else "No entries yet."
        total_goals = len(self.goals)
        done_goals = len([g for g in self.goals if g.get("done")])
        dash = (
            f"Tasks remaining: {len(self.tasks)}\n"
            f"Completed tasks: {len(self.completed_tasks)}\n"
            f"Goals: {done_goals}/{total_goals} completed\n"
            f"Last journal: {journal_text[:60]}"
        )
        self.dashboard_text.config(text=dash)

    def get_contextual_message(self) -> str:
        if self.completed_tasks:
            return "Great job ticking off tasks! Keep the momentum going."
        if any(g.get("done") for g in self.goals):
            return "You've been making steady progress on your goals!"
        return "Stay focused and keep writing your story."

    def update_motivation(self) -> None:
        try:
            msg = get_motivational_message()
            if not msg:
                raise ValueError
        except Exception:
            msg = self.get_contextual_message()
        self.motivation_label.config(text=msg)
        self.root.after(3600000, self.update_motivation)

        
    def refresh_all(self) -> None:
        self.update_time()
        self.refresh_journal()
        self.refresh_tasks()
        self.refresh_goals()
        self.update_dashboard()
        self.update_motivation()

        
    def run(self) -> None:
        self.root.mainloop()


def run_popup_agent() -> None:
    PopupAgent().run()


if __name__ == "__main__":
    run_popup_agent()