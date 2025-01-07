import subprocess
import sys

# List of packages to install
required_packages = [
    "pandas",
    "streamlit",
    "selenium",
    "openpyxl",
    "webdriver-manager"
]

# Path to Streamlit app
script_name = "app.py"

def install_packages():
    """Install required packages using pip."""
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', *required_packages])
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while installing packages: {e}")

def run_streamlit_app():
    """Run the Streamlit app."""
    subprocess.run([sys.executable, "-m", "streamlit", "run", script_name])

if __name__ == "__main__":
    # install_packages()  # Run once
    run_streamlit_app()  # Uncomment to run the Streamlit app
