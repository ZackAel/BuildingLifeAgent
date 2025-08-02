import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import threading
import time
from tkinter import font as tkfont
import math

# Import all agent modules
from main import run_agent
from tasks import load_tasks, save_tasks, complete_task, get_task_age_days, record_task_date
from mood import log_mood, get_today_mood, journaling_prompt, ascii_mood, MOOD_FILE
from streak import get_current_streak, update_streak
from energy import compute_energy_index
from motivation import get_motivational_message
from goals import load_goals, save_goal
from relationships import contacts_needing_ping, log_interaction
from schedule_utils import intelligent_schedule
from gemini_api import ask_gemini, has_api_key
from guardrails import burnout_warning
from game_engine import quest_manager, character_system
import tkinter.simpledialog

AI_AVAILABLE = has_api_key()

def _mood_score(m: str) -> int:
    """Return a numeric mood score for plotting."""
    m = m.lower()
    if any(w in m for w in ["happy", "great", "good", "motivated", "excited"]):
        return 1
    if any(w in m for w in ["sad", "bad", "tired", "stressed"]):
        return -1
    return 0



class EnhancedAgentPopup:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AI Life Coach")
        self.root.geometry("500x700")
        self.root.resizable(False, False)
        
        # Modern color scheme
        self.colors = {
            'bg': '#1a1a2e',
            'primary': '#16213e',
            'secondary': '#0f3460',
            'accent': '#e94560',
            'text': '#f5f5f5',
            'success': '#00b894',
            'warning': '#fdcb6e',
            'danger': '#d63031'
        }
        
        self.root.configure(bg=self.colors['bg'])
        
        if not AI_AVAILABLE:
            messagebox.showwarning(
                "AI Disabled",
                "GEMINI_API_KEY not found. AI features are disabled.",
            )

        # Initialize state
        self.pomodoro_running = False
        self.pomodoro_time = 25 * 60
        self.chat_messages = []
        # Flag indicating whether we're showing the 3-hour preview
        self.schedule_preview_mode = True
        
        self.setup_ui()
        self.update_display()
        self.auto_refresh()
        
        # Make window stay on top initially
        self.root.attributes('-topmost', True)
        self.root.after(2000, lambda: self.root.attributes('-topmost', False))
    
    def create_rounded_button(self, parent, text, command, bg_color, width=15):
        """Create a modern rounded button"""
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg_color,
            fg=self.colors['text'],
            font=('Arial', 10, 'bold'),
            relief=tk.FLAT,
            width=width,
            pady=8,
            cursor='hand2',
            activebackground=bg_color,
            activeforeground=self.colors['text']
        )
        return btn
    
    def setup_ui(self):
        # Main container with padding
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header with glassmorphism effect
        header_frame = tk.Frame(main_container, bg=self.colors['primary'], height=100)
        header_frame.pack(fill='x', pady=(0, 15))
        header_frame.pack_propagate(False)
        
        # Title with gradient effect
        title_label = tk.Label(
            header_frame, 
            text="🤖 AI Life Coach",
            font=('Arial', 20, 'bold'),
            bg=self.colors['primary'],
            fg=self.colors['text']
        )
        title_label.pack(pady=15)
        
        # Time and date
        self.time_label = tk.Label(
            header_frame,
            font=('Arial', 10),
            bg=self.colors['primary'],
            fg=self.colors['text']
        )
        self.time_label.pack()
        self.update_time()
        
        # Stats cards in grid
        stats_frame = tk.Frame(main_container, bg=self.colors['bg'])
        stats_frame.pack(fill='x', pady=(0, 15))
        
        # Create 2x2 grid of stats
        self.create_stat_card(stats_frame, "streak", "🔥 Streak", 0, 0)
        self.create_stat_card(stats_frame, "energy", "⚡ Energy", 0, 1)
        self.create_stat_card(stats_frame, "mood", "😊 Mood", 1, 0)
        self.create_stat_card(stats_frame, "tasks", "📋 Tasks", 1, 1)
        
        # Burnout warning (hidden by default)
        self.warning_frame = tk.Frame(main_container, bg=self.colors['danger'])
        self.warning_label = tk.Label(
            self.warning_frame,
            text="",
            font=('Arial', 9, 'bold'),
            bg=self.colors['danger'],
            fg=self.colors['text'],
            wraplength=450
        )
        self.warning_label.pack(padx=10, pady=5)
        
        # Tabbed interface
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill='both', expand=True, pady=(0, 15))
        
        # Configure ttk style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background=self.colors['bg'])
        style.configure('TNotebook.Tab', padding=[20, 10])
        
        # Create tabs
        self.create_dashboard_tab()
        self.create_schedule_tab()
        self.create_chat_tab()
        self.create_quick_actions_tab()
        
        # Bottom action buttons
        action_frame = tk.Frame(main_container, bg=self.colors['bg'])
        action_frame.pack(fill='x')
        
        btn_frame = tk.Frame(action_frame, bg=self.colors['bg'])
        btn_frame.pack()
        
        self.create_rounded_button(
            btn_frame, "🔄 Refresh", self.update_display, 
            self.colors['secondary'], width=10
        ).pack(side='left', padx=5)
        
        self.create_rounded_button(
            btn_frame, "🧘 Break", self.take_break,
            self.colors['accent'], width=10
        ).pack(side='left', padx=5)
        
        self.create_rounded_button(
            btn_frame, "💤 Snooze", self.snooze_hour,
            self.colors['primary'], width=10
        ).pack(side='left', padx=5)
    
    def create_stat_card(self, parent, name, label, row, col):
        """Create a modern stat card"""
        frame = tk.Frame(parent, bg=self.colors['secondary'], relief=tk.FLAT)
        frame.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
        parent.grid_columnconfigure(col, weight=1)
        
        # Add hover effect
        def on_enter(e):
            frame.config(bg=self.colors['accent'])
        def on_leave(e):
            frame.config(bg=self.colors['secondary'])
        
        frame.bind("<Enter>", on_enter)
        frame.bind("<Leave>", on_leave)
        
        label_widget = tk.Label(
            frame, text=label, font=('Arial', 10),
            bg=self.colors['secondary'], fg=self.colors['text']
        )
        label_widget.pack(padx=15, pady=(10, 5))
        
        value_widget = tk.Label(
            frame, text="--", font=('Arial', 14, 'bold'),
            bg=self.colors['secondary'], fg=self.colors['text']
        )
        value_widget.pack(padx=15, pady=(0, 10))
        
        # Store reference
        setattr(self, f"{name}_label", value_widget)
        
        # Make labels follow hover
        label_widget.bind("<Enter>", on_enter)
        label_widget.bind("<Leave>", on_leave)
        value_widget.bind("<Enter>", on_enter)
        value_widget.bind("<Leave>", on_leave)
    
    def create_dashboard_tab(self):
        """Create the main dashboard tab"""
        dashboard_frame = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(dashboard_frame, text="Dashboard")
        
        # Motivational message
        self.motivation_frame = tk.Frame(dashboard_frame, bg=self.colors['accent'])
        self.motivation_frame.pack(fill='x', padx=10, pady=10)
        
        self.motivation_text = tk.Text(
            self.motivation_frame, 
            height=3, 
            wrap=tk.WORD,
            font=('Arial', 10),
            bg=self.colors['accent'],
            fg=self.colors['text'],
            border=0,
            padx=10,
            pady=10
        )
        self.motivation_text.pack(fill='x')
     
        # Mood trend chart
        self.mood_chart_frame = tk.Frame(dashboard_frame, bg=self.colors['bg'])
        self.mood_chart_frame.pack(fill='x', padx=10, pady=(0, 10))
        self.mood_chart_widget = None
        self.mood_chart_canvas = None
        self.update_mood_chart()
   
        # Tasks with progress indicators
        tasks_label = tk.Label(
            dashboard_frame,
            text="📋 Today's Tasks",
            font=('Arial', 12, 'bold'),
            bg=self.colors['bg'],
            fg=self.colors['text']
        )
        tasks_label.pack(anchor='w', padx=10, pady=(10, 5))
        
        # Task list with custom scrollbar
        task_frame = tk.Frame(dashboard_frame, bg=self.colors['bg'])
        task_frame.pack(fill='both', expand=True, padx=10)
        
        self.tasks_canvas = tk.Canvas(
            task_frame,
            bg=self.colors['primary'],
            highlightthickness=0,
            height=200
        )
        scrollbar = tk.Scrollbar(task_frame, orient="vertical", command=self.tasks_canvas.yview)
        self.tasks_inner_frame = tk.Frame(self.tasks_canvas, bg=self.colors['primary'])
        
        self.tasks_canvas.configure(yscrollcommand=scrollbar.set)
        self.tasks_canvas_window = self.tasks_canvas.create_window(
            (0, 0), 
            window=self.tasks_inner_frame, 
            anchor="nw"
        )
        
        self.tasks_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Quick add task
        add_frame = tk.Frame(dashboard_frame, bg=self.colors['bg'])
        add_frame.pack(fill='x', padx=10, pady=10)
        
        self.task_entry = tk.Entry(
            add_frame,
            font=('Arial', 10),
            bg=self.colors['primary'],
            fg=self.colors['text'],
            insertbackground=self.colors['text']
        )
        self.task_entry.pack(side='left', fill='x', expand=True)
        
        self.create_rounded_button(
            add_frame, "+ Add", self.add_task_from_entry,
            self.colors['success'], width=8
        ).pack(side='right', padx=(5, 0))
        
        # Bind Enter key
        self.task_entry.bind('<Return>', lambda e: self.add_task_from_entry())
    
    def update_mood_chart(self):
        """Render a simple line chart of recent mood entries."""
        try:
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            from matplotlib.figure import Figure
        except Exception:
            return

        try:
            with open(MOOD_FILE, "r") as f:
                lines = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            lines = []

        if self.mood_chart_widget:
            self.mood_chart_widget.destroy()
            self.mood_chart_widget = None

        if not lines:
            self.mood_chart_widget = tk.Label(
                self.mood_chart_frame,
                text="No mood data",
                bg=self.colors['bg'],
                fg=self.colors['text'],
            )
            self.mood_chart_widget.pack()
            return

        last = lines[-7:]
        dates = []
        scores = []
        for line in last:
            ts, mood, _ = line.split(",", 2)
            dates.append(ts.split(" ")[0])
            scores.append(_mood_score(mood))

        fig = Figure(figsize=(4, 2), dpi=100)
        ax = fig.add_subplot(111)
        ax.plot(range(len(scores)), scores, marker="o")
        ax.set_xticks(range(len(dates)))
        ax.set_xticklabels(dates, rotation=45, ha="right")
        ax.set_ylim(-1, 1)
        ax.set_title("Mood Trend")
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.mood_chart_frame)
        canvas.draw()
        widget = canvas.get_tk_widget()
        widget.pack(fill='x')
        self.mood_chart_canvas = canvas
        self.mood_chart_widget = widget


    def create_schedule_tab(self):
        """Create the schedule tab"""
        schedule_frame = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(schedule_frame, text="Schedule")
        
        # Generate schedule button
        self.create_rounded_button(
            schedule_frame, "🔄 Generate Optimal Schedule",
            self.generate_schedule, self.colors['accent']
        ).pack(pady=10)
        
        # Schedule display
        self.schedule_text = tk.Text(
            schedule_frame,
            font=('Arial', 10),
            bg=self.colors['primary'],
            fg=self.colors['text'],
            wrap=tk.WORD,
            padx=10,
            pady=10
        )
        self.schedule_text.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        # Show initial 3-hour schedule preview
        self.update_schedule_preview()
        
        # Pomodoro timer
        timer_frame = tk.Frame(schedule_frame, bg=self.colors['secondary'])
        timer_frame.pack(fill='x', padx=10, pady=10)
        
        self.timer_label = tk.Label(
            timer_frame,
            text="25:00",
            font=('Arial', 24, 'bold'),
            bg=self.colors['secondary'],
            fg=self.colors['text']
        )
        self.timer_label.pack(pady=10)
        
        timer_btn_frame = tk.Frame(timer_frame, bg=self.colors['secondary'])
        timer_btn_frame.pack(pady=(0, 10))
        
        self.pomodoro_btn = self.create_rounded_button(
            timer_btn_frame, "▶️ Start", self.toggle_pomodoro,
            self.colors['success'], width=10
        )
        self.pomodoro_btn.pack(side='left', padx=5)
        
        self.create_rounded_button(
            timer_btn_frame, "🔄 Reset", self.reset_pomodoro,
            self.colors['warning'], width=10
        ).pack(side='left', padx=5)
    
    def create_chat_tab(self):
        """Create the AI chat tab"""
        chat_frame = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(chat_frame, text="AI Chat")
        
        if not AI_AVAILABLE:
            tk.Label(
                chat_frame,
                text="GEMINI_API_KEY not found. AI chat disabled.",
                bg=self.colors['bg'],
                fg=self.colors['text'],
                wraplength=450,
            ).pack(padx=10, pady=10)
            return

        # Chat display
        self.chat_display = tk.Text(
            chat_frame,
            font=('Arial', 10),
            bg=self.colors['primary'],
            fg=self.colors['text'],
            wrap=tk.WORD,
            padx=10,
            pady=10,
            height=15
        )
        self.chat_display.pack(fill='both', expand=True, padx=10, pady=(10, 5))
        self.chat_display.config(state=tk.DISABLED)
        
        # Chat input
        input_frame = tk.Frame(chat_frame, bg=self.colors['bg'])
        input_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        self.chat_entry = tk.Entry(
            input_frame,
            font=('Arial', 10),
            bg=self.colors['primary'],
            fg=self.colors['text'],
            insertbackground=self.colors['text']
        )
        self.chat_entry.pack(side='left', fill='x', expand=True)
        self.chat_entry.bind('<Return>', lambda e: self.send_chat_message())
        
        self.create_rounded_button(
            input_frame, "Send", self.send_chat_message,
            self.colors['accent'], width=8
        ).pack(side='right', padx=(5, 0))
        
        # Quick prompts
        prompts_frame = tk.Frame(chat_frame, bg=self.colors['bg'])
        prompts_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        prompts = [
            ("😰 Feeling stuck", "I'm feeling stuck with my tasks"),
            ("💡 Need motivation", "I need some motivation right now"),
            ("🎯 Goal advice", "How can I better achieve my goals?")
        ]
        
        for text, prompt in prompts:
            self.create_rounded_button(
                prompts_frame, text,
                lambda p=prompt: self.quick_chat(p),
                self.colors['secondary'], width=12
            ).pack(side='left', padx=2)
    
    def create_quick_actions_tab(self):
        """Create quick actions tab"""
        actions_frame = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(actions_frame, text="Quick Actions")
        
        # Mood logging
        mood_frame = tk.LabelFrame(
            actions_frame, 
            text="Log Mood",
            font=('Arial', 10, 'bold'),
            bg=self.colors['bg'],
            fg=self.colors['text']
        )
        mood_frame.pack(fill='x', padx=10, pady=10)
        
        mood_buttons_frame = tk.Frame(mood_frame, bg=self.colors['bg'])
        mood_buttons_frame.pack(pady=10)
        
        moods = [
            ("😊 Happy", "happy"),
            ("😰 Stressed", "stressed"),
            ("😴 Tired", "tired"),
            ("😌 Calm", "calm"),
            ("🚀 Motivated", "motivated")
        ]
        
        for i, (label, mood) in enumerate(moods):
            if i % 3 == 0:
                row_frame = tk.Frame(mood_buttons_frame, bg=self.colors['bg'])
                row_frame.pack()
            
            self.create_rounded_button(
                row_frame, label,
                lambda m=mood: self.quick_log_mood(m),
                self.colors['secondary'], width=10
            ).pack(side='left', padx=2, pady=2)
        
        # Relationships
        rel_frame = tk.LabelFrame(
            actions_frame,
            text="Relationships",
            font=('Arial', 10, 'bold'),
            bg=self.colors['bg'],
            fg=self.colors['text']
        )
        rel_frame.pack(fill='x', padx=10, pady=10)
        
        self.contacts_label = tk.Label(
            rel_frame,
            text="Loading contacts...",
            font=('Arial', 9),
            bg=self.colors['bg'],
            fg=self.colors['warning'],
            wraplength=400
        )
        self.contacts_label.pack(padx=10, pady=10)
        
        contact_input_frame = tk.Frame(rel_frame, bg=self.colors['bg'])
        contact_input_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        self.contact_entry = tk.Entry(
            contact_input_frame,
            font=('Arial', 10),
            bg=self.colors['primary'],
            fg=self.colors['text']
        )
        self.contact_entry.pack(side='left', fill='x', expand=True)
        
        self.create_rounded_button(
            contact_input_frame, "Log Contact",
            self.log_contact_interaction,
            self.colors['success'], width=10
        ).pack(side='right', padx=(5, 0))
        
        # Journal
        journal_frame = tk.LabelFrame(
            actions_frame,
            text="Quick Journal",
            font=('Arial', 10, 'bold'),
            bg=self.colors['bg'],
            fg=self.colors['text']
        )
        journal_frame.pack(fill='x', padx=10, pady=10)
        
        self.journal_prompt_label = tk.Label(
            journal_frame,
            text="",
            font=('Arial', 9, 'italic'),
            bg=self.colors['bg'],
            fg=self.colors['text'],
            wraplength=400
        )
        self.journal_prompt_label.pack(padx=10, pady=(10, 5))
        
        self.journal_text = tk.Text(
            journal_frame,
            height=3,
            font=('Arial', 10),
            bg=self.colors['primary'],
            fg=self.colors['text'],
            wrap=tk.WORD
        )
        self.journal_text.pack(fill='x', padx=10, pady=(0, 10))
        
        self.create_rounded_button(
            journal_frame, "💾 Save Entry",
            self.save_journal_entry,
            self.colors['accent']
        ).pack(pady=(0, 10))
    
        # Motivation and energy quick actions
        wellness_frame = tk.LabelFrame(
            actions_frame,
            text="Motivation & Energy",
            font=('Arial', 10, 'bold'),
            bg=self.colors['bg'],
            fg=self.colors['text']
        )
        wellness_frame.pack(fill='x', padx=10, pady=10)

        self.create_rounded_button(
            wellness_frame, "Request Motivation",
            self.request_motivation,
            self.colors['secondary']
        ).pack(side='left', padx=5, pady=5)

        self.create_rounded_button(
            wellness_frame, "Energy Check-in",
            self.energy_check_in,
            self.colors['secondary']
        ).pack(side='left', padx=5, pady=5)

    def update_display(self):
        """Update all displayed information"""
        # Update stats
        streak = get_current_streak()
        self.streak_label.config(text=f"{streak} days")
        
        energy = compute_energy_index()
        self.energy_label.config(text=f"{energy}%")
        
        mood, _ = get_today_mood()
        mood_display = f"{mood} {ascii_mood(mood)}" if mood else "Not logged"
        self.mood_label.config(text=mood_display)
        
        tasks = load_tasks()
        self.tasks_label.config(text=f"{len(tasks)} pending")
        
        # Update burnout warning
        warning = burnout_warning()
        if warning:
            self.warning_label.config(text=f"⚠️ {warning}")
            self.warning_frame.pack(fill='x', pady=(0, 10))
        else:
            self.warning_frame.pack_forget()
        
        # Update motivation
        try:
            motivation = get_motivational_message()
            self.motivation_text.config(state=tk.NORMAL)
            self.motivation_text.delete(1.0, tk.END)
            self.motivation_text.insert(1.0, motivation)
            self.motivation_text.config(state=tk.DISABLED)
        except:
            pass
  
        # Update mood trend chart
        self.update_mood_chart()
      
        # Update tasks display
        self.display_tasks()
        
        # Update contacts
        self.update_contacts()
        
        # Update journal prompt
        self.journal_prompt_label.config(text=journaling_prompt())
    
        # Update schedule preview if we're in preview mode
        if self.schedule_preview_mode:
            self.update_schedule_preview()

    def display_tasks(self):
        """Display tasks with visual indicators"""
        # Clear existing tasks
        for widget in self.tasks_inner_frame.winfo_children():
            widget.destroy()
        
        tasks = load_tasks()
        for i, task in enumerate(tasks[:10]):  # Show first 10
            age = get_task_age_days(task)
            
            task_frame = tk.Frame(
                self.tasks_inner_frame,
                bg=self.colors['primary'],
                pady=5
            )
            task_frame.pack(fill='x', padx=5, pady=2)
            
            # Age indicator
            age_color = self.colors['danger'] if age > 3 else self.colors['warning'] if age > 1 else self.colors['success']
            age_indicator = tk.Label(
                task_frame,
                text="●",
                font=('Arial', 12),
                bg=self.colors['primary'],
                fg=age_color
            )
            age_indicator.pack(side='left', padx=(5, 10))
            
            # Task checkbox
            var = tk.BooleanVar()
            check = tk.Checkbutton(
                task_frame,
                text=task[:40] + "..." if len(task) > 40 else task,
                variable=var,
                font=('Arial', 10),
                bg=self.colors['primary'],
                fg=self.colors['text'],
                selectcolor=self.colors['primary'],
                activebackground=self.colors['primary'],
                command=lambda t=task, v=var: self.complete_task_action(t, v)
            )
            check.pack(side='left', fill='x', expand=True)
            
            # Age label
            age_label = tk.Label(
                task_frame,
                text=f"{age}d",
                font=('Arial', 8),
                bg=self.colors['primary'],
                fg=self.colors['text']
            )
            age_label.pack(side='right', padx=5)
        
        # Update scroll region
        self.tasks_inner_frame.update_idletasks()
        self.tasks_canvas.configure(scrollregion=self.tasks_canvas.bbox("all"))
    
    # Action methods
    def complete_task_action(self, task, var):
        """Handle task completion"""
        if var.get():
            complete_task(task)
            tasks = load_tasks()
            tasks.remove(task)
            save_tasks(tasks)
            
            # Show celebration
            messagebox.showinfo("🎉 Great Job!", f"Completed: {task}")
            
            # Update XP if using gamification
            try:
                quest_manager.add_xp(10)
            except:
                pass
            
            self.update_display()
    
    def add_task_from_entry(self):
        """Add task from entry widget"""
        task = self.task_entry.get().strip()
        if task:
            tasks = load_tasks()
            tasks.append(task)
            save_tasks(tasks)
            record_task_date(task)
            self.task_entry.delete(0, tk.END)
            self.update_display()
            messagebox.showinfo("✅ Success", f"Added: {task}")

    def update_schedule_preview(self):
        """Compute and display the next 3 hours of schedule"""
        tasks = load_tasks()
        schedule = intelligent_schedule(tasks)
        now = datetime.datetime.now()
        end = now + datetime.timedelta(hours=3)
        lines = []
        for line in schedule.split('\n'):
            if not line.strip():
                continue
            try:
                start_str = line.split(' - ')[0]
                start_dt = datetime.datetime.combine(
                    now.date(), datetime.datetime.strptime(start_str, '%H:%M').time()
                )
                if now <= start_dt < end:
                    lines.append(line)
            except Exception:
                continue

        self.schedule_preview_mode = True
        if lines:
            self.display_schedule('\n'.join(lines))
        else:
            self.schedule_text.delete(1.0, tk.END)
            self.schedule_text.insert(1.0, "No events scheduled in the next 3 hours.")
    
    def generate_schedule(self):
        """Generate intelligent schedule"""
        tasks = load_tasks()
        if not tasks:
            self.schedule_text.delete(1.0, tk.END)
            self.schedule_text.insert(1.0, "No tasks to schedule!")
            return
        
        self.schedule_text.delete(1.0, tk.END)
        self.schedule_text.insert(1.0, "Generating optimal schedule...")
        self.schedule_preview_mode = False

        
        # Run in thread to avoid freezing UI
        def generate():
            schedule = intelligent_schedule(tasks)
            self.root.after(0, lambda: self.display_schedule(schedule))
        
        threading.Thread(target=generate, daemon=True).start()
    
    def display_schedule(self, schedule):
        """Display the generated schedule"""
        self.schedule_text.delete(1.0, tk.END)
        lines = schedule.split('\n')
        
        for line in lines:
            if line.strip():
                # Color code different activities
                if "Break" in line:
                    self.schedule_text.insert(tk.END, f"☕ {line}\n", "break")
                elif "Lunch" in line:
                    self.schedule_text.insert(tk.END, f"🍽️ {line}\n", "lunch")
                else:
                    self.schedule_text.insert(tk.END, f"📌 {line}\n", "task")
        
        # Configure tags for colors
        self.schedule_text.tag_config("break", foreground=self.colors['success'])
        self.schedule_text.tag_config("lunch", foreground=self.colors['warning'])
        self.schedule_text.tag_config("task", foreground=self.colors['text'])
    
    def toggle_pomodoro(self):
        """Start/pause pomodoro timer"""
        self.pomodoro_running = not self.pomodoro_running
        if self.pomodoro_running:
            self.pomodoro_btn.config(text="⏸️ Pause")
            self.run_pomodoro()
        else:
            self.pomodoro_btn.config(text="▶️ Resume")
    
    def run_pomodoro(self):
        """Run the pomodoro timer"""
        if self.pomodoro_running and self.pomodoro_time > 0:
            self.pomodoro_time -= 1
            mins, secs = divmod(self.pomodoro_time, 60)
            self.timer_label.config(text=f"{mins:02d}:{secs:02d}")
            
            # Change color as time runs out
            if self.pomodoro_time < 60:
                self.timer_label.config(fg=self.colors['danger'])
            elif self.pomodoro_time < 300:
                self.timer_label.config(fg=self.colors['warning'])
            
            self.root.after(1000, self.run_pomodoro)
        elif self.pomodoro_time == 0:
            self.pomodoro_complete()
    
    def pomodoro_complete(self):
        """Handle pomodoro completion"""
        self.pomodoro_running = False
        self.timer_label.config(text="00:00", fg=self.colors['success'])
        messagebox.showinfo("🍅 Pomodoro Complete!", "Great job! Time for a break.")
        self.reset_pomodoro()
    
    def reset_pomodoro(self):
        """Reset pomodoro timer"""
        self.pomodoro_running = False
        self.pomodoro_time = 25 * 60
        self.timer_label.config(text="25:00", fg=self.colors['text'])
        self.pomodoro_btn.config(text="▶️ Start")
    
    def send_chat_message(self):
        """Send message to AI chat"""
        if not AI_AVAILABLE:
            messagebox.showwarning(
                "AI Disabled",
                "GEMINI_API_KEY not found. AI chat disabled.",
            )
            return

        
        message = self.chat_entry.get().strip()
        if not message:
            return
        
        # Add to chat display
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"You: {message}\n", "user")
        self.chat_entry.delete(0, tk.END)
        
        # Get AI response in thread
        def get_response():
            try:
                mood, _ = get_today_mood()
                energy = compute_energy_index()
                context = f"Mood: {mood}, Energy: {energy}%, Message: {message}"
                response = ask_gemini(f"As a supportive life coach, respond briefly to: {context}")
                self.root.after(0, lambda: self.display_ai_response(response))
            except Exception as e:
                self.root.after(0, lambda: self.display_ai_response("I'm here to support you! How can I help?"))
        
        threading.Thread(target=get_response, daemon=True).start()
        
        # Show typing indicator
        self.chat_display.insert(tk.END, "AI: Thinking...\n", "ai")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def display_ai_response(self, response):
        """Display AI response in chat"""
        self.chat_display.config(state=tk.NORMAL)
        # Remove typing indicator
        self.chat_display.delete("end-2l", "end-1l")
        # Add actual response
        self.chat_display.insert(tk.END, f"AI: {response}\n\n", "ai")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
        
        # Configure tags
        self.chat_display.tag_config("user", foreground=self.colors['accent'])
        self.chat_display.tag_config("ai", foreground=self.colors['success'])
    
    def quick_chat(self, prompt):
        """Send a quick prompt to chat"""
        self.chat_entry.insert(0, prompt)
        self.send_chat_message()
    
    def quick_log_mood(self, mood):
        """Quick mood logging"""
        log_mood(mood)
        messagebox.showinfo("😊 Mood Logged", f"Logged mood: {mood}")
        self.update_display()
    
    def update_contacts(self):
        """Update contacts needing attention"""
        try:
            stale = contacts_needing_ping()
            if stale:
                self.contacts_label.config(
                    text=f"📱 Reach out to: {', '.join(stale[:3])}",
                    fg=self.colors['warning']
                )
            else:
                self.contacts_label.config(
                    text="✅ All contacts up to date!",
                    fg=self.colors['success']
                )
        except:
            self.contacts_label.config(text="No contact data")
    
    def log_contact_interaction(self):
        """Log interaction with contact"""
        name = self.contact_entry.get().strip()
        if name:
            log_interaction(name)
            self.contact_entry.delete(0, tk.END)
            messagebox.showinfo("✅ Success", f"Logged interaction with {name}")
            self.update_contacts()
    
    def save_journal_entry(self):
        """Save journal entry"""
        text = self.journal_text.get(1.0, tk.END).strip()
        if text:
            from journal import log_entry
            prompt = self.journal_prompt_label.cget("text")
            log_entry(prompt, text)
            self.journal_text.delete(1.0, tk.END)
            messagebox.showinfo("📝 Saved", "Journal entry saved!")
    
    def request_motivation(self):
        """Fetch and display a motivational message"""
        try:
            message = get_motivational_message()
            messagebox.showinfo("💡 Motivation", message)
        except Exception as e:
            messagebox.showerror("Error", f"Could not retrieve motivation: {e}")

    def energy_check_in(self):
        """Compute energy index and show result"""
        try:
            energy = compute_energy_index()
            messagebox.showinfo("⚡ Energy Check", f"Your energy level is {energy}%")
        except Exception as e:
            messagebox.showerror("Error", f"Could not compute energy: {e}")

    def take_break(self):
        """Initiate mindfulness break"""
        self.root.withdraw()
        
        # Create break window
        break_window = tk.Toplevel()
        break_window.title("Mindfulness Break")
        break_window.geometry("400x300")
        break_window.configure(bg=self.colors['primary'])
        
        # Breathing animation
        canvas = tk.Canvas(
            break_window,
            width=200,
            height=200,
            bg=self.colors['primary'],
            highlightthickness=0
        )
        canvas.pack(pady=20)
        
        circle = canvas.create_oval(50, 50, 150, 150, fill=self.colors['accent'], outline="")
        
        instruction = tk.Label(
            break_window,
            text="Breathe in...",
            font=('Arial', 14),
            bg=self.colors['primary'],
            fg=self.colors['text']
        )
        instruction.pack()
        
        def animate_breathing(size=50, growing=True, count=0):
            if count >= 6:  # 3 breath cycles
                break_window.destroy()
                self.root.deiconify()
                return
            
            if growing:
                size += 2
                if size >= 80:
                    growing = False
                    instruction.config(text="Breathe out...")
            else:
                size -= 2
                if size <= 50:
                    growing = True
                    instruction.config(text="Breathe in...")
                    count += 1
            
            x1, y1 = 100 - size, 100 - size
            x2, y2 = 100 + size, 100 + size
            canvas.coords(circle, x1, y1, x2, y2)
            
            break_window.after(50, lambda: animate_breathing(size, growing, count))
        
        animate_breathing()
    
    def snooze_hour(self):
        """Snooze notifications for an hour"""
        messagebox.showinfo("💤 Snoozed", "I'll check back in an hour!")
        self.root.after(3600000, self.show_popup)
        self.root.withdraw()
    
    def show_popup(self):
        """Show the popup window"""
        self.root.deiconify()
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after_idle(lambda: self.root.attributes('-topmost', False))
        self.update_display()
    
    def update_time(self):
        """Update time display"""
        now = datetime.datetime.now()
        time_str = now.strftime("%I:%M %p")
        date_str = now.strftime("%A, %B %d")
        self.time_label.config(text=f"{time_str} • {date_str}")
        self.root.after(1000, self.update_time)
    
    def auto_refresh(self):
        """Auto refresh display every 30 seconds"""
        # update_display will refresh the schedule preview when in preview mode
        self.update_display()
        self.root.after(30000, self.auto_refresh)
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

def run_popup_agent():
    """Run the visual popup agent"""
    app = EnhancedAgentPopup()
    app.run()

if __name__ == "__main__":
    run_popup_agent()