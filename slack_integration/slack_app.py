"""Basic Slack bot using Bolt for Python."""

import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from tasks import load_tasks
from streak import get_current_streak
from mood import log_mood


app = App(token=os.getenv("SLACK_BOT_TOKEN"))


@app.command("/standup")
def handle_standup(ack, body, say):
    """Respond to /standup command with daily question."""
    ack()
    user = body["user_id"]
    say(f"<@{user}> What did you accomplish today?")


@app.command("/tasks")
def handle_tasks(ack, say):
    """List tasks."""
    ack()
    tasks_list = load_tasks()
    if not tasks_list:
        say("No tasks found.")
    else:
        say("\n".join(f"{i+1}. {t}" for i, t in enumerate(tasks_list)))


@app.command("/streak")
def handle_streak(ack, say):
    ack()
    streak = get_current_streak()
    say(f"Current streak: {streak} days")


@app.command("/mood")
def handle_mood(ack, say, command):
    ack()
    mood_text = command.get("text", "")
    log_mood(mood_text)
    say(f"Logged mood: {mood_text}")


def main() -> None:
    handler = SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN"))
    handler.start()


if __name__ == "__main__":
    main()
