from __future__ import annotations
import argparse
import datetime
import json
import os
import signal
import subprocess
import sys
import time

from main import run_agent, ensure_data_files, countdown
from scheduler_config import load_config, get_adjusted_interval

PID_FILE = os.path.join("data", "agent_daemon.pid")
STATE_FILE = os.path.join("data", "daemon_state.json")


def _load_state() -> dict:
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _save_state(state: dict) -> None:
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def _loop() -> None:
    ensure_data_files()
    state = _load_state()
    while True:
        run_agent()
        state["last_run"] = datetime.datetime.now().isoformat()
        _save_state(state)
        cfg = load_config()
        interval = get_adjusted_interval(cfg)
        countdown(interval)


def start() -> None:
    if os.path.exists(PID_FILE):
        print("Agent daemon already running.")
        return
    process = subprocess.Popen([
        sys.executable,
        os.path.abspath(__file__),
        "run",
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    with open(PID_FILE, "w") as f:
        f.write(str(process.pid))
    print("Agent daemon started.")


def stop() -> None:
    if not os.path.exists(PID_FILE):
        print("Agent daemon not running.")
        return
    pid = int(open(PID_FILE).read())
    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    os.remove(PID_FILE)
    print("Agent daemon stopped.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Background service for the AI agent")
    parser.add_argument("command", choices=["start", "stop", "run"], help="Control the daemon")
    args = parser.parse_args()

    if args.command == "start":
        start()
    elif args.command == "stop":
        stop()
    else:
        _loop()


if __name__ == "__main__":
    main()
