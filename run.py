"""
Runner script for AI Resume Assistant.
Provides an easy way to start the Streamlit application.
"""

import os
import sys
import subprocess
from pathlib import Path


def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = [
        'streamlit', 'openai', 'langchain', 'PyMuPDF', 
        'nltk', 'sentence-transformers'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 Install missing packages with:")
        print("   pip install -r requirements.txt")
        return False
    
    return True


def check_environment():
    """Check if environment is properly configured."""
    issues = []
    
    # Check for OpenRouter API key
    if not os.getenv('OPENROUTER_API_KEY'):
        issues.append("OPENROUTER_API_KEY environment variable not set")
    
    if issues:
        print("⚠️  Environment issues:")
        for issue in issues:
            print(f"   - {issue}")
        print("\n💡 Set up your environment variables:")
        print("   export OPENROUTER_API_KEY='your-api-key-here'")
        print("   Or create a .env file with your API key")
        return False
    
    return True


def main():
    """Main function to run the application."""
    print("🤖 AI Resume Assistant")
    print("=" * 40)
    
    # Get the directory of this script
    script_dir = Path(__file__).parent.absolute()
    app_path = script_dir / "app.py"
    
    if not app_path.exists():
        print("❌ app.py not found in the current directory")
        return
    
    print("🔍 Checking dependencies...")
    if not check_dependencies():
        return
    
    print("✅ Dependencies OK")
    
    print("🔍 Checking environment...")
    if not check_environment():
        print("⚠️  Warning: Environment issues detected")
        print("   The app may not work properly without proper configuration")
    else:
        print("✅ Environment OK")
    
    print("\n🚀 Starting AI Resume Assistant...")
    print("   App will open in your default browser")
    print("   Press Ctrl+C to stop the server")
    print("=" * 40)
    
    try:
        # Run Streamlit app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", str(app_path),
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 AI Resume Assistant stopped")
    except Exception as e:
        print(f"❌ Error starting application: {e}")


if __name__ == "__main__":
    main() 