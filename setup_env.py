#!/usr/bin/env python3
"""
Environment setup script for Document Processing Assistant project.
Creates a virtual environment and installs dependencies.
"""

import os
import subprocess
import sys
import platform

# Project configuration
PROJECT_ROOT = "document_processing_assistant"
VENV_NAME = "doc_processing_env"

def check_python_version():
    """Check if Python version is compatible"""
    required_version = (3, 7)
    current_version = sys.version_info
    
    if current_version < required_version:
        print(f"Error: Python {required_version[0]}.{required_version[1]} or higher is required.")
        print(f"Current version: {current_version[0]}.{current_version[1]}")
        sys.exit(1)

def create_virtual_environment():
    """Create a virtual environment"""
    print(f"Creating virtual environment: {VENV_NAME}")
    
    try:
        subprocess.run([sys.executable, "-m", "venv", os.path.join(PROJECT_ROOT, VENV_NAME)], 
                      check=True)
        print("Virtual environment created successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error creating virtual environment: {e}")
        sys.exit(1)

def get_venv_activate_command():
    """Get the appropriate activate command for the current platform"""
    if platform.system() == "Windows":
        return os.path.join(PROJECT_ROOT, VENV_NAME, "Scripts", "activate")
    else:
        return f"source {os.path.join(PROJECT_ROOT, VENV_NAME, 'bin', 'activate')}"

def get_venv_python():
    """Get the path to the Python executable in the virtual environment"""
    if platform.system() == "Windows":
        return os.path.join(PROJECT_ROOT, VENV_NAME, "Scripts", "python")
    else:
        return os.path.join(PROJECT_ROOT, VENV_NAME, "bin", "python")

def install_dependencies():
    """Install dependencies in the virtual environment"""
    print("Installing dependencies...")
    
    requirements_path = os.path.join(PROJECT_ROOT, "requirements.txt")
    venv_python = get_venv_python()
    
    if not os.path.exists(requirements_path):
        print(f"Error: Requirements file not found at {requirements_path}")
        sys.exit(1)
    
    try:
        subprocess.run([venv_python, "-m", "pip", "install", "--upgrade", "pip"], 
                     check=True)
        subprocess.run([venv_python, "-m", "pip", "install", "-r", requirements_path], 
                     check=True)
        print("Dependencies installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        sys.exit(1)

def main():
    """Main execution function"""
    # Check Python version
    check_python_version()
    
    # Check if project directory exists
    if not os.path.exists(PROJECT_ROOT):
        print(f"Error: Project directory '{PROJECT_ROOT}' not found.")
        print("Please run setup_project.py first.")
        sys.exit(1)
    
    # Create virtual environment
    create_virtual_environment()
    
    # Install dependencies
    install_dependencies()
    
    # Print activation instructions
    activate_cmd = get_venv_activate_command()
    print("\nSetup completed successfully!")
    print("\nTo activate the virtual environment, run:")
    if platform.system() == "Windows":
        print(f"{activate_cmd}")
    else:
        print(f"{activate_cmd}")
    
    print("\nNext steps:")
    print("1. Activate the virtual environment using the command above")
    print("2. Run run_app.py to start the application")

if __name__ == "__main__":
    main()