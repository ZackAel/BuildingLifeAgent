import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import threading
import time
from main import run_agent
from tasks import load_tasks, save_tasks, complete_task
from mood import log_mood, get_today_mood
from streak import get_current_streak
from energy import compute_energy_index
from motivation import get_motivational_message
from goals import load_goals
import tkinter.simpledialog

class AgentPopup:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Your AI Life Coach")
        self.root.geometry("450x600")
        self.root.configure(bg='#f0f8ff')
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        
        self.setup_ui()
        self.update_display()
        
        # Auto-refresh every 30 seconds
        self.auto_refresh()
    
    def setup_ui(self):
        # Header
        header_frame = tk.Frame(self.root, bg='#4a90e2', height=80)
        header_frame.pack(fill='x', padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="🤖 Your AI Life Coach", 
                              font=('Arial', 16, 'bold'), 
                              bg='#4a90e2', fg='white')
        title_label.pack(pady=20)
        
        # Main content frame
        main_frame = tk.Frame(self.root, bg='#f0f8ff')
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Streak and Energy
        stats_frame = tk.Frame(main_frame, bg='#f0f8ff')
        stats_frame.pack(fill='x', pady=(0, 15))
        
        self.streak_label = tk.Label(stats_frame, text="🔥 Streak: 0 days", 
                                    font=('Arial', 12, 'bold'), bg='#f0f8ff')
        self.streak_label.pack(side='left')
        
        self.energy_label = tk.Label(stats_frame, text="⚡ Energy: 50%", 
                                    font=('Arial', 12, 'bold'), bg='#f0f8ff')
        self.energy_label.pack(side='right')
        
        # Motivational message
        self.motivation_frame = tk.Frame(main_frame, bg='#e8f4fd', relief='raised', bd=2)
        self.motivation_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(self.motivation_frame, text="💬 Daily Motivation", 
                font=('Arial', 10, 'bold'), bg='#e8f4fd').pack(anchor='w', padx=10, pady=(5,0))
        
        self.motivation_text = tk.Text(self.motivation_frame, height=3, wrap=tk.WORD, 
                                      font=('Arial', 9), bg='#e8f4fd', border=0)
        self.motivation_text.pack(fill='x', padx=10, pady=(0,10))
        
        # Current tasks
        tasks_frame = tk.Frame(main_frame, bg='#f0f8ff')
        tasks_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        tk.Label(tasks_frame, text="📋 Today's Tasks", 
                font=('Arial', 12, 'bold'), bg='#f0f8ff').pack(anchor='w')
        
        # Tasks listbox with scrollbar
        tasks_list_frame = tk.Frame(tasks_frame, bg='#f0f8ff')
        tasks_list_frame.pack(fill='both', expand=True, pady=(5,0))
        
        self.tasks_listbox = tk.Listbox(tasks_list_frame, font=('Arial', 9), 
                                       selectmode=tk.SINGLE, height=6)
        scrollbar = tk.Scrollbar(tasks_list_frame, orient="vertical")
        self.tasks_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tasks_listbox.yview)
        
        self.tasks_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Buttons frame
        buttons_frame = tk.Frame(main_frame, bg='#f0f8ff')
        buttons_frame.pack(fill='x', pady=10)
        
        # Task management buttons
        task_buttons = tk.Frame(buttons_frame, bg='#f0f8ff')
        task_buttons.pack(fill='x', pady=(0, 10))
        
        tk.Button(task_buttons, text="✓ Complete Task", 
                 command=self.complete_selected_task, 
                 bg='#28a745', fg='white', font=('Arial', 9)).pack(side='left', padx=(0, 5))
        
        tk.Button(task_buttons, text="+ Add Task", 
                 command=self.add_task_dialog, 
                 bg='#007bff', fg='white', font=('Arial', 9)).pack(side='left', padx=5)
        
        tk.Button(task_buttons, text="😊 Log Mood", 
                 command=self.log_mood_dialog, 
                 bg='#17a2b8', fg='white', font=('Arial', 9)).pack(side='right')
        
        # Action buttons
        action_buttons = tk.Frame(buttons_frame, bg='#f0f8ff')
        action_buttons.pack(fill='x')
        
        tk.Button(action_buttons, text="🎯 View Goals", 
                 command=self.show_goals, 
                 bg='#6c757d', fg='white', font=('Arial', 9)).pack(side='left', padx=(0, 5))
        
        tk.Button(action_buttons, text="🔄 Refresh", 
                 command=self.update_display, 
                 bg='#fd7e14', fg='white', font=('Arial', 9)).pack(side='left', padx=5)
        
        tk.Button(action_buttons, text="💤 Snooze 1h", 
                 command=self.snooze_hour, 
                 bg='#6f42c1', fg='white', font=('Arial', 9)).pack(side='right')
    
    def update_display(self):
        # Update streak
        streak = get_current_streak()
        self.streak_label.config(text=f"🔥 Streak: {streak} days")
        
        # Update energy
        energy = compute_energy_index()
        self.energy_label.config(text=f"⚡ Energy: {energy}%")
        
        # Update motivation
        try:
            motivation = get_motivational_message()
            self.motivation_text.delete(1.0, tk.END)
            self.motivation_text.insert(1.0, motivation)
        except:
            self.motivation_text.delete(1.0, tk.END)
            self.motivation_text.insert(1.0, "You're doing great! Keep pushing forward! 🚀")
        
        # Update tasks
        tasks = load_tasks()
        self.tasks_listbox.delete(0, tk.END)
        for i, task in enumerate(tasks[:10]):  # Show first 10 tasks
            self.tasks_listbox.insert(tk.END, f"{i+1}. {task}")
        
        # Update window title with current mood
        mood, _ = get_today_mood()
        if mood:
            self.root.title(f"Your AI Life Coach - Feeling {mood}")
        else:
            self.root.title("Your AI Life Coach")
    
    def complete_selected_task(self):
        selection = self.tasks_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a task to complete.")
            return
        
        tasks = load_tasks()
        if selection[0] < len(tasks):
            task = tasks[selection[0]]
            complete_task(task)
            tasks.remove(task)
            save_tasks(tasks)
            messagebox.showinfo("Task Completed", f"Great job completing: {task}")
            self.update_display()
    
    def add_task_dialog(self):
        task = tk.simpledialog.askstring("Add Task", "What would you like to accomplish?")
        if task:
            tasks = load_tasks()
            tasks.append(task.strip())
            save_tasks(tasks)
            messagebox.showinfo("Task Added", f"Added: {task}")
            self.update_display()
    
    def log_mood_dialog(self):
        mood = tk.simpledialog.askstring("Log Mood", 
                                        "How are you feeling? (happy, stressed, calm, tired, etc.)")
        if mood:
            log_mood(mood.strip())
            messagebox.showinfo("Mood Logged", f"Logged mood: {mood}")
            self.update_display()
    
    def show_goals(self):
        goals = load_goals()
        if goals:
            goals_text = "\n".join(f"• {goal}" for goal in goals)
            messagebox.showinfo("Your Goals", goals_text)
        else:
            messagebox.showinfo("Your Goals", "No goals set yet. Add some in the main app!")
    
    def snooze_hour(self):
        messagebox.showinfo("Snoozed", "I'll check back with you in an hour! 😴")
        self.root.after(3600000, self.show_popup)  # 1 hour in milliseconds
        self.root.withdraw()
    
    def show_popup(self):
        self.root.deiconify()
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after_idle(lambda: self.root.attributes('-topmost', False))
        self.update_display()
    
    def auto_refresh(self):
        self.update_display()
        self.root.after(30000, self.auto_refresh)  # Refresh every 30 seconds
    
    def run(self):
        # Import here to avoid circular imports
        global tk, simpledialog
        tk.simpledialog = tkinter.simpledialog
        
        self.root.mainloop()

def run_popup_agent():
    """Run the visual popup agent"""
    app = AgentPopup()
    app.run()

if __name__ == "__main__":
    run_popup_agent()