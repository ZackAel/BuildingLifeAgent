# BuildingLifeAgent

A small productivity assistant that uses the Gemini API for task management and motivation.

## Setup

1. Install dependencies (requires Python 3):
   ```bash
   pip install requests python-dotenv
   ```
2. Create a `.env` file in the project root containing your API key:
   ```bash
   GEMINI_API_KEY=your_key_here
   ```
3. Run the agent:
   ```bash
   python main.py
   ```

# BuildingLifeAgent

BuildingLifeAgent is a simple command line productivity assistant. It keeps track of tasks, goals and mood, then uses Google's Gemini API to generate encouraging messages and scheduling suggestions.

## Setup

1. Install the required packages:

```bash
pip install -r requirements.txt
```

2. Provide your [Gemini API](https://ai.google.dev/) key. The application looks for a `.env` file in the project root with the following line:

```
GEMINI_API_KEY=your_key_here
```

Alternatively, set the `GEMINI_API_KEY` environment variable before running the program.

## Usage

Run the main loop with the default hourly interval:

```bash
python main.py
```

For faster testing you can lower the interval (seconds) using `--interval`:

```bash
python main.py --interval 60
```

The agent will prompt you to add tasks, goals or mood entries and will query the Gemini API to prioritize tasks and give motivational feedback.

## Optional Features

- **Notifications:** Install `plyer` for desktop notifications on Windows.
- **GUI:** You can create a simple interface using `streamlit` or `tkinter`.
- **Speech:** Install `pyttsx3` for text‑to‑speech output and `speechrecognition` for voice commands.

These extras are not required but can enhance the experience.


# BuildingLifeAgent

This project is a simple personal productivity assistant. It stores tasks, goals and mood logs in the `data/` directory and can generate motivational messages via the Gemini API.

## Requirements

- Python 3.8+
- [Streamlit](https://streamlit.io) for the optional web UI
- [plyer](https://github.com/kivy/plyer) for desktop notifications
- [SpeechRecognition](https://github.com/Uberi/speech_recognition) (optional for voice commands)

Install dependencies with:

```bash
pip install streamlit plyer SpeechRecognition pyaudio
```

`pyaudio` is required by SpeechRecognition for microphone input. On some systems you may need additional system packages to build it.

## Command line usage

Run the console agent:

```bash
python main.py
```

Data files will be created in the `data/` folder on first run.

## Web dashboard

A lightweight dashboard built with Streamlit is provided in `webapp.py`. It lets you view and update tasks, goals and mood logs in a browser. To start it run:

```bash
streamlit run webapp.py
```

The dashboard also sends system notifications using plyer when you add tasks or log your mood. Enable voice commands from the sidebar to try simple spoken commands like **"add task ..."** or **"log mood ..."**.
