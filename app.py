# app.py

import os
# Import the main recording function from your audio_processing package
from audio_processing.recorder import run_recorder

if __name__ == "__main__":
    # Ensure the recordings directory exists relative to app.py
    recordings_path = os.path.join(os.path.dirname(__file__), "recordings")
    if not os.path.exists(recordings_path):
        os.makedirs(recordings_path)

    # Call the main recorder function
    run_recorder()
