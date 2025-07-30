#!/usr/bin/env python3
"""
BuildingLifeAgent Launcher
Run your AI life coach in different modes
"""

import sys
import subprocess
import time
import os

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
    try:
        subprocess.run(["streamlit", "run", "webapp.py"])
    except FileNotFoundError:
        print("❌ Streamlit not installed. Install with: pip install streamlit")
    except KeyboardInterrupt:
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

def run_background_daemon():
    """Start the background daemon"""
    print("🔄 Starting background daemon...")
    print("This will run in the background and send notifications every hour.")
    try:
        subprocess.run([sys.executable, "agent_beast.py", "start"])
        print("✅ Background daemon started!")
        print("Use 'python agent_beast.py stop' to stop it.")
    except Exception as e:
        print(f"❌ Error starting daemon: {e}")

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
        "3": ("🔄 Background Daemon", run_background_daemon),
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