#!/usr/bin/env python3
"""
BuildingLifeAgent Launcher
Run your AI life coach in different modes
"""

import sys
import subprocess
import time
import os
import webbrowser


def _can_launch_browser() -> bool:
    """Return True if the environment likely supports opening a web browser.

    A GUI is considered available when running on Windows or when the DISPLAY
    variable is set on Unix systems. Users can force headless mode by setting
    the ``BUILDINGLIFE_HEADLESS`` environment variable.
    """

    if os.environ.get("BUILDINGLIFE_HEADLESS"):
        return False

    # On non-Windows systems a missing DISPLAY usually indicates no GUI.
    if sys.platform != "win32" and not os.environ.get("DISPLAY"):
        return False

    return True

def print_banner():
    print("""
    🤖 BuildingLifeAgent - Your AI Life Coach
    ========================================
    
    Choose how you want to run your agent:
    """)

def run_web_dashboard():
    """Launch the Streamlit web dashboard"""
    print("🌐 Starting web dashboard...")
    print("This will open in your browser automatically.")
    print("Press Ctrl+C to stop.")

    url = "http://localhost:8501"
    process = None


    try:
        # Streamlit is started in headless mode so we can decide whether to
        # open a browser based on environment detection.
        process = subprocess.Popen(
            ["streamlit", "run", "webapp.py", "--server.headless=true"]
        )
        # Give the server a moment to start before opening the browser
        time.sleep(1)

        if _can_launch_browser():
            try:
                webbrowser.open(url)
            except webbrowser.Error as e:
                print(f"⚠️  Could not open browser automatically: {e}")
                print(f"   Please open {url} manually.")
        else:
            print(f"📝 No GUI detected. Access the dashboard at {url}")

        process.wait()
    except FileNotFoundError:
        print("❌ Streamlit not installed. Install with: pip install streamlit")
    except KeyboardInterrupt:
        if process:
            process.terminate()
        print("\n👋 Web dashboard stopped.")

def run_popup_agent():
    """Launch the popup GUI agent"""
    print("🖥️  Starting popup agent...")
    print("A window will appear with your daily overview.")
    try:
        from popup_agent import run_popup_agent
        run_popup_agent()
    except ImportError as e:
        print(f"❌ Error importing popup agent: {e}")
        print("Make sure tkinter is installed (usually comes with Python)")

def run_background_beast():
    """Start the background beast"""
    print("🔄 Starting background beast...")
    print("This will run in the background and send notifications every hour.")
    try:
        subprocess.run([sys.executable, "agent_beast.py", "start"])
        print("✅ Background beast started!")
        print("Use 'python agent_beast.py stop' to stop it.")
    except Exception as e:
        print(f"❌ Error starting beast: {e}")

def run_terminal_mode():
    """Run the original terminal interface"""
    print("💻 Starting terminal mode...")
    print("This is the original command-line interface.")
    try:
        subprocess.run([sys.executable, "main.py"])
    except KeyboardInterrupt:
        print("\n👋 Terminal mode stopped.")

def run_api_server():
    """Start the FastAPI server"""
    print("🚀 Starting API server...")
    print("This provides a REST API for other integrations.")
    try:
        subprocess.run(["uvicorn", "api_server:app", "--reload"])
    except FileNotFoundError:
        print("❌ uvicorn not installed. Install with: pip install uvicorn")
    except KeyboardInterrupt:
        print("\n👋 API server stopped.")

def check_dependencies():
    """Check if required dependencies are installed"""
    missing = []
    
    try:
        import requests
        import dotenv
    except ImportError:
        missing.append("requests python-dotenv")
    
    try:
        import streamlit
    except ImportError:
        missing.append("streamlit (for web dashboard)")
    
    try:
        import tkinter
    except ImportError:
        missing.append("tkinter (for popup agent)")
    
    try:
        import fastapi
        import uvicorn
    except ImportError:
        missing.append("fastapi uvicorn (for API server)")
    
    if missing:
        print("⚠️  Some optional dependencies are missing:")
        for dep in missing:
            print(f"   pip install {dep}")
        print()

def main():
    print_banner()
    check_dependencies()
    
    options = {
        "1": ("🌐 Web Dashboard (Recommended)", run_web_dashboard),
        "2": ("🖥️  Popup Agent", run_popup_agent),
        "3": ("🔄 Background beast", run_background_beast),
        "4": ("💻 Terminal Mode", run_terminal_mode),
        "5": ("🚀 API Server", run_api_server),
        "q": ("👋 Quit", sys.exit)
    }
    
    for key, (description, _) in options.items():
        print(f"    {key}. {description}")
    
    print("\n" + "="*50)
    
    while True:
        choice = input("\nSelect an option (1-5, or 'q' to quit): ").strip().lower()
        
        if choice in options:
            description, func = options[choice]
            print(f"\n{description}")
            print("-" * 50)
            try:
                func()
            except KeyboardInterrupt:
                print(f"\n👋 {description} stopped.")
            break
        else:
            print("❌ Invalid choice. Please select 1-5 or 'q'.")

if __name__ == "__main__":
    main()