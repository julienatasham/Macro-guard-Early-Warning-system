# main.py
import subprocess
import sys
import os

# Path to scripts folder
scripts_dir = os.path.join(os.path.dirname(__file__), "scripts")

def run_script(script_name):
    script_path = os.path.join(scripts_dir, script_name)
    print(f"🔹 Running {script_name}...")
    result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("⚠️ Errors/warnings:", result.stderr)

if __name__ == "__main__":
    # Run cleaning first
    run_script("cleaning.py")

    # Generate features
    run_script("features.py")

    # Forecast next month
    run_script("forecasting.py")

    # Start the dashboard (will block here)
    run_script("dashboard.py")