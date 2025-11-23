"""
Setup script for GDOT Educational Video Generator.
Optional helper for installing additional dependencies.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, description):
    """Run shell command with error handling."""
    print(f"\n{'=' * 60}")
    print(f"📦 {description}")
    print(f"{'=' * 60}")
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print(f"✅ {description} - SUCCESS")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        print(f"Error: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is 3.10+."""
    print("\n🐍 Checking Python version...")
    
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Need 3.10+")
        return False


def install_base_requirements():
    """Install requirements from requirements.txt."""
    if not Path('requirements.txt').exists():
        print("❌ requirements.txt not found")
        return False
    
    return run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing base requirements"
    )


def install_manim():
    """Install Manim Community Edition."""
    return run_command(
        f"{sys.executable} -m pip install manim",
        "Installing Manim Community Edition"
    )


def install_edge_tts():
    """Install edge-tts for text-to-speech."""
    return run_command(
        f"{sys.executable} -m pip install edge-tts",
        "Installing edge-tts"
    )


def check_ffmpeg():
    """Check if FFmpeg is installed."""
    print("\n🎬 Checking FFmpeg...")
    
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("✅ FFmpeg is installed")
            return True
        else:
            print("❌ FFmpeg not found")
            return False
    except FileNotFoundError:
        print("❌ FFmpeg not installed")
        print("\n📝 Install FFmpeg:")
        print("  - Windows: Download from https://ffmpeg.org/download.html")
        print("  - Linux: sudo apt install ffmpeg")
        print("  - macOS: brew install ffmpeg")
        return False


def create_directories():
    """Create necessary directories."""
    print("\n📁 Creating directories...")
    
    directories = [
        'data',
        'data/work',
        'data/outputs',
        'data/checkpoints'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {directory}/")
    
    print("✅ Directories created")
    return True


def create_env_file():
    """Create .env file from template if not exists."""
    print("\n⚙️ Checking .env file...")
    
    if Path('.env').exists():
        print("✅ .env file already exists")
        return True
    
    if Path('env.example').exists():
        print("📝 Creating .env from env.example...")
        
        with open('env.example', 'r') as f:
            content = f.read()
        
        with open('.env', 'w') as f:
            f.write(content)
        
        print("✅ .env file created")
        print("\n⚠️  IMPORTANT: Edit .env and add your API keys!")
        print("  - GROQ_API_KEY: Get from https://console.groq.com")
        print("  - SERPAPI_KEY: Get from https://serpapi.com")
        return True
    else:
        print("⚠️  env.example not found")
        return False


def main():
    """Main setup routine."""
    print("\n" + "=" * 60)
    print("🎥 GDOT Educational Video Generator - Setup")
    print("=" * 60)
    
    # Track setup status
    all_ok = True
    
    # 1. Check Python version
    if not check_python_version():
        print("\n❌ Setup failed: Python 3.10+ required")
        return False
    
    # 2. Install base requirements
    if not install_base_requirements():
        print("\n⚠️  Base requirements installation failed")
        all_ok = False
    
    # 3. Install Manim
    if not install_manim():
        print("\n⚠️  Manim installation failed (may need manual install)")
        all_ok = False
    
    # 4. Install edge-tts
    if not install_edge_tts():
        print("\n⚠️  edge-tts installation failed (may need manual install)")
        all_ok = False
    
    # 5. Check FFmpeg
    if not check_ffmpeg():
        print("\n⚠️  FFmpeg not found (required for video rendering)")
        all_ok = False
    
    # 6. Create directories
    if not create_directories():
        print("\n⚠️  Directory creation failed")
        all_ok = False
    
    # 7. Create .env file
    if not create_env_file():
        print("\n⚠️  .env file creation failed")
        all_ok = False
    
    # Summary
    print("\n" + "=" * 60)
    if all_ok:
        print("✅ Setup completed successfully!")
        print("\n📝 Next steps:")
        print("  1. Edit .env and add your API keys")
        print("  2. Run: streamlit run app.py")
        print("  3. Open browser to http://localhost:8501")
    else:
        print("⚠️  Setup completed with warnings")
        print("\n📝 Please fix the issues above and try again")
    print("=" * 60)
    
    return all_ok


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)




