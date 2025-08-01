import speech_recognition as sr
import pyttsx3
from difflib import get_close_matches
from tasks import load_tasks, save_tasks
from mood import log_mood
from plyer import notification

class VoiceAssistant:
    """Handle voice input and output for the web dashboard."""

    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()
        try:
            self.engine = pyttsx3.init()
        except Exception:
            self.engine = None
        self.listening = False

    def speak(self, text: str) -> None:
        """Read text aloud if text-to-speech is available."""
        if not self.engine:
            return
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception:
            pass

    def _parse_command(self, text: str):
        """Return (callable, arg) for the best matching command."""
        text = text.lower().strip()
        commands = {
            'add task': self._add_task,
            'log mood': self._log_mood,
        }
        for key in commands:
            if text.startswith(key):
                return commands[key], text[len(key):].strip()

        # fuzzy match first words
        words = text.split()
        if not words:
            return None, None
        for key in commands:
            if get_close_matches(words[0], [key.split()[0]], n=1, cutoff=0.8):
                return commands[key], text[len(key):].strip()
        return None, None

    def _add_task(self, task_text: str) -> None:
        if not task_text:
            self.speak('Please specify a task.')
            return
        tasks = load_tasks()
        tasks.append(task_text)
        save_tasks(tasks)
        try:
            notification.notify(title='Task Added', message=task_text)
        except NotImplementedError:
            print(f"Task added: {task_text}")
        self.speak(f'Task {task_text} added.')

    def _log_mood(self, mood_text: str) -> None:
        if not mood_text:
            self.speak('Please specify your mood.')
            return
        log_mood(mood_text)
        try:
            notification.notify(title='Mood Logged', message=mood_text)
        except NotImplementedError:
            print(f"Mood logged: {mood_text}")
        self.speak('Mood logged.')

    def handle_command(self, text: str) -> None:
        """Process a spoken command string."""
        func, arg = self._parse_command(text)
        if func:
            func(arg)
        else:
            self.speak("Sorry, I didn't understand that command.")

    def listen_once(self) -> str | None:
        """Listen for a single command after the wake word."""
        with self.mic as source:
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source, phrase_time_limit=5)
        try:
            heard = self.recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            return None
        except Exception:
            return None
        if not heard.lower().startswith('hey agent'):
            return None
        command = heard[len('hey agent'):].strip()
        self.handle_command(command)
        return heard

    def listen_continuously(self, max_iterations: int = 20) -> None:
        """Continuously listen until told to stop or max_iterations reached."""
        self.listening = True
        iterations = 0
        while self.listening and iterations < max_iterations:
            result = self.listen_once()
            if result and 'stop listening' in result.lower():
                self.speak('Stopping listening.')
                self.listening = False
                break
            iterations += 1
