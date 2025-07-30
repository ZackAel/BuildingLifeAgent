# BuildingLifeAgent

BuildingLifeAgent is a small command line productivity assistant. It keeps track of tasks, goals and mood logs in the `data/` directory and uses Google's Gemini API to generate motivational messages and task suggestions.

## Setup

1. Install the required packages (Python 3.8+):
   ```bash
   pip install -r requirements.txt
   ```
   To enable the optional GUI, notifications and voice features also install:
   ```bash
   pip install streamlit plyer pyttsx3 SpeechRecognition pyaudio
   ```
2. Provide your [Gemini API](https://ai.google.dev/) key in a `.env` file at the project root:
   ```bash
   GEMINI_API_KEY=your_key_here
   ```
   Alternatively, set `GEMINI_API_KEY` in your environment before running the program.

## Usage

Run the console agent with the default hourly interval:
```bash
python main.py
```
For faster testing, lower the check-in interval (seconds):
```bash
python main.py --interval 60
```
The program will prompt you to add tasks, goals or mood entries and then query the Gemini API for supportive feedback.

## Optional Features

 - **Notifications:** install `plyer` for cross-platform desktop alerts (macOS, Linux and Windows).
- **Voice & speech:** install `pyttsx3` for text-to-speech and `SpeechRecognition` (requires `pyaudio`) for voice commands.
- **GUI:** install `streamlit` to use the included web dashboard.

These packages are listed under `# Optional extras` in `requirements.txt` and can be installed with:
```bash
pip install streamlit plyer pyttsx3 SpeechRecognition pyaudio
```
They are optional but can enhance the experience.

## Chat Platform Bots

BuildingLifeAgent includes integrations for Discord and Slack.

### Discord

Run the bot with:
```bash
export DISCORD_TOKEN=your_token
export DISCORD_USER_ID=your_user_id
python -m discord_bot.bot
```
Use commands like `!tasks`, `!addtask`, `!complete`, `!streak`, `!mood` and `!pomodoro <channel_id>`.

### Slack

Create a Slack app with Socket Mode enabled and set the tokens:
```bash
export SLACK_BOT_TOKEN=xoxb-...
export SLACK_APP_TOKEN=xapp-...
python -m slack_integration.slack_app
```
Slash commands `/tasks`, `/streak`, `/mood` and `/standup` will respond.


## Web dashboard

A lightweight dashboard (`webapp.py`) lets you manage tasks, goals, mood logs and journal entries in a browser. Start it with:
```bash
streamlit run webapp.py
```
Journal notes are saved to `data/journal.txt` alongside the other data files. The dashboard can also send notifications using plyer and, if enabled in the sidebar, respond to basic voice commands.

## Audio Interface

The optional `audio_interface` package provides a screenless workflow:
- `podcast_generator.generate_briefing()` reads a short morning summary.
- `ambient_engine.play_mode()` plays ambient background sounds.
- `voice_journal.record_entry()` lets you dictate a journal entry and `voice_journal.analyze_entry()` asks Gemini for a short reflection.
- `ambient_engine.suggest_playlist()` creates task-based playlist ideas.

## Running Tests

Install the requirements and run `pytest` from the project root:

```bash
pip install -r requirements.txt
pytest
```
## CLI Dashboard and Integrations

- **Textual dashboard:** run `python -m terminal_ui.dashboard` for a TUI overview of tasks, goals and mood.
- **Shell prompt:** source `shell_integration/agent_prompt.sh` to show your current mood, streak and next task in the prompt.
- **Vim plugin:** copy `editor_plugins/vim_agent.vim` to your Vim plugin directory to add `:AgentAddTask`, `:AgentCompleteTask` and `:AgentLogMood` commands inside the editor.

