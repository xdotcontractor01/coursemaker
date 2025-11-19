"""
Simple launcher script for GDOT Video Generator.
Choose between Streamlit UI or FastAPI server.
"""

import sys
import subprocess
import os
from pathlib import Path


def check_env():
    """Check if .env file exists."""
    if not Path('.env').exists():
        print("⚠️  .env file not found!")
        print("\nCreating .env from template...")
        
        if Path('env.example').exists():
            with open('env.example', 'r') as src:
                content = src.read()
            with open('.env', 'w') as dst:
                dst.write(content)
            
            print("✅ .env file created")
            print("\n⚠️  IMPORTANT: Edit .env and add your API keys before continuing!")
            print("  - GROQ_API_KEY: Get from https://console.groq.com")
            print("  - SERPAPI_KEY: Get from https://serpapi.com")
            print("\nPress Enter when ready...")
            input()
        else:
            print("❌ env.example not found")
            return False
    
    return True


def run_streamlit():
    """Run Streamlit UI."""
    print("\n🚀 Starting Streamlit UI...")
    print("📍 Open browser to: http://localhost:8501")
    print("Press Ctrl+C to stop\n")
    
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])


def run_fastapi():
    """Run FastAPI server."""
    print("\n🚀 Starting FastAPI server...")
    print("📍 API docs at: http://localhost:8000/docs")
    print("Press Ctrl+C to stop\n")
    
    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "api:app",
        "--reload",
        "--host", "0.0.0.0",
        "--port", "8000"
    ])


def run_setup():
    """Run setup script."""
    print("\n🔧 Running setup...")
    subprocess.run([sys.executable, "setup.py"])


def show_menu():
    """Show main menu."""
    print("\n" + "=" * 60)
    print("🎥 GDOT Educational Video Generator")
    print("=" * 60)
    print("\nSelect mode:")
    print("  1. Streamlit UI (recommended for interactive use)")
    print("  2. FastAPI Server (for API/programmatic access)")
    print("  3. Run setup (install dependencies)")
    print("  4. Exit")
    print("\n" + "=" * 60)
    
    choice = input("\nEnter choice (1-4): ").strip()
    return choice


def main():
    """Main launcher."""
    # Check environment
    if not check_env():
        print("\n❌ Setup incomplete. Please fix issues and try again.")
        return
    
    # Show menu
    choice = show_menu()
    
    if choice == "1":
        run_streamlit()
    elif choice == "2":
        run_fastapi()
    elif choice == "3":
        run_setup()
    elif choice == "4":
        print("\n👋 Goodbye!")
    else:
        print("\n❌ Invalid choice")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

