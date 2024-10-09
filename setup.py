'''
    rethink
    October 2024

    This is the setup script for the project. 
    It creates a virtual environment and installs all dependencies.
    The script is intended to be run once at the beginning of the project.

'''


import os
import sys
import subprocess
import platform
from pathlib import Path

def create_virtual_env(env_name="autorsa-venv"):
    """
    Creates a virtual environment in the specified directory.
    """
    if not Path(env_name).exists():
        print(f"Creating virtual environment: {env_name}")
        subprocess.check_call([sys.executable, "-m", "venv", env_name])
    else:
        print(f"Virtual environment '{env_name}' already exists.")

def get_activate_script(env_name="autorsa-venv"):
    """
    Returns the path to the activation script based on the operating system.
    """
    system = platform.system()
    if system == "Windows":
        return Path(env_name) / "Scripts" / "activate.bat"
    else:
        return Path(env_name) / "bin" / "activate"

def install_packages(env_name="autorsa-venv"):
    """
    Installs required packages using pip within the virtual environment.
    """
    print("Installing required packages...")
    # Determine the path to the pip executable within the virtual environment
    if platform.system() == "Windows":
        pip_executable = Path(env_name) / "Scripts" / "pip.exe"
    else:
        pip_executable = Path(env_name) / "bin" / "pip"

    subprocess.check_call([str(pip_executable), "install", "-r", "requirements.txt"])

def install_playwright(env_name="autorsa-venv"):
    """
    Installs Playwright's dependencies.
    """
    print("Installing Playwright dependencies...")
    if platform.system() == "Windows":
        pip_executable = Path(env_name) / "Scripts" / "pip.exe"
        playwright_executable = Path(env_name) / "Scripts" / "playwright.exe"
    else:
        pip_executable = Path(env_name) / "bin" / "pip"
        playwright_executable = Path(env_name) / "bin" / "playwright"

    subprocess.check_call([str(pip_executable), "install", "playwright"])
    subprocess.check_call([str(playwright_executable), "install"])

def setup_environment():
    """
    Sets up the virtual environment and installs all dependencies.
    """
    env_name = "autorsa-venv"
    create_virtual_env(env_name)
    install_packages(env_name)
    install_playwright(env_name)
    print("Setup complete.")
    print("\n\nTo activate the virtual environment run:")
    print('source', get_activate_script(env_name))

if __name__ == "__main__":
    setup_environment()
