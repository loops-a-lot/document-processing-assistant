#!/usr/bin/env python3
"""
Application runner for Document Processing Assistant project.
Starts the Streamlit application and can run tests.
"""

import os
import sys
import subprocess
import platform
import argparse

# Project configuration
PROJECT_ROOT = "document_processing_assistant"
VENV_NAME = "doc_processing_env"

def get_venv_python():
    """Get the path to the Python executable in the virtual environment"""
    if platform.system() == "Windows":
        return os.path.join(PROJECT_ROOT, VENV_NAME, "Scripts", "python")
    else:
        return os.path.join(PROJECT_ROOT, VENV_NAME, "bin", "python")

def get_venv_streamlit():
    """Get the path to the Streamlit executable in the virtual environment"""
    if platform.system() == "Windows":
        return os.path.join(PROJECT_ROOT, VENV_NAME, "Scripts", "streamlit")
    else:
        return os.path.join(PROJECT_ROOT, VENV_NAME, "bin", "streamlit")

def check_environment():
    """Check if the environment is set up correctly"""
    if not os.path.exists(PROJECT_ROOT):
        print(f"Error: Project directory '{PROJECT_ROOT}' not found.")
        print("Please run setup_env.py first to create the project structure.")
        return False
    
    venv_python = get_venv_python()
    if not os.path.exists(venv_python):
        print(f"Error: Virtual environment not found at {os.path.join(PROJECT_ROOT, VENV_NAME)}")
        print("Please run setup_env.py first.")
        return False
    
    return True

def run_streamlit_app():
    """Run the Streamlit application"""
    print("Starting Streamlit application...")
    
    app_path = os.path.join(PROJECT_ROOT, "app", "main.py")
    streamlit_path = get_venv_streamlit()
    
    if not os.path.exists(app_path):
        print(f"Error: Application file not found at {app_path}")
        return False
    
    try:
        subprocess.run([streamlit_path, "run", app_path], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running Streamlit application: {e}")
        return False
    except KeyboardInterrupt:
        print("\nApplication stopped.")
        return True

def run_tests():
    """Run the test suite"""
    print("Running tests...")
    
    tests_dir = os.path.join(PROJECT_ROOT, "tests")
    venv_python = get_venv_python()
    
    if not os.path.exists(tests_dir):
        print(f"Error: Tests directory not found at {tests_dir}")
        return False
    
    try:
        subprocess.run([venv_python, "-m", "pytest", tests_dir, "-v"], check=True)
        print("All tests passed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: Some tests failed. Return code: {e.returncode}")
        return False

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="Run Document Processing Assistant application or tests")
    parser.add_argument("--test", action="store_true", help="Run tests instead of the application")
    args = parser.parse_args()
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    if args.test:
        # Run tests
        if not run_tests():
            sys.exit(1)
    else:
        # Run application
        if not run_streamlit_app():
            sys.exit(1)
    
    sys.exit(0)

if __name__ == "__main__":
    main()