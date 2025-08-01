import datetime

try:
    from plyer import notification
except Exception:  # plyer not installed or fails
    notification = None

try:
    import tkinter as tk
except Exception:
    tk = None


class NotificationManager:
    """Manage desktop notifications and interactive popups."""

    def __init__(self) -> None:
        self.snoozed_until: datetime.datetime | None = None

    # --- snooze utilities ---
    def is_snoozed(self) -> bool:
        return self.snoozed_until is not None and datetime.datetime.now() < self.snoozed_until

    def snooze(self, minutes: int) -> None:
        self.snoozed_until = datetime.datetime.now() + datetime.timedelta(minutes=minutes)

    # --- basic alerts ---
    def send_alert(self, message: str) -> None:
        if self.is_snoozed():
            return
        if notification is None:
            return
        try:
            notification.notify(title="AI Agent", message=message)
        except NotImplementedError:
            print(message)
        except Exception:
            pass

    # --- interactive popups ---
    def send_interactive(self, message: str, actions: dict[str, callable] | None = None) -> None:
        if self.is_snoozed():
            return
        if tk is None:
            # fallback to basic alert if tkinter unavailable
            self.send_alert(message)
            return

        root = tk.Tk()
        root.title("AI Agent")
        tk.Label(root, text=message, wraplength=300).pack(padx=10, pady=10)

        if actions:
            for label, callback in actions.items():
                def handler(cb=callback):
                    try:
                        cb()
                    finally:
                        root.destroy()
                tk.Button(root, text=label, command=handler).pack(fill="x", padx=5, pady=2)

        tk.Button(root, text="Snooze 10m", command=lambda: (self.snooze(10), root.destroy())).pack(fill="x", padx=5, pady=2)
        tk.Button(root, text="Dismiss", command=root.destroy).pack(fill="x", padx=5, pady=2)
        root.mainloop()
