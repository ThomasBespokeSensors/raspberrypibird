# config.py

# --- Configuration Constants ---
SAMPLERATE = 44100  # Sample rate in Hz (common for audio)
CHANNELS = 1        # Number of audio channels (1 for mono, 2 for stereo)
THRESHOLD = 0.05    # Volume threshold (RMS value, typically between 0 and 1)
                    # Adjust this value based on your microphone sensitivity and environment noise.
MAX_RECORDING_DURATION = 30  # Maximum recording duration in seconds
SILENCE_DURATION_TO_STOP = 10  # Seconds of silence below threshold to stop recording
BLOCKSIZE = 1024    # Number of frames per buffer block (affects responsiveness)
DEVICE_INDEX = None # Set to None to use the default input device, or an integer
                    # for a specific device (e.g., 0, 1, etc.).
                    # You can find device indices by running: python -m sounddevice

# Directory to save recordings relative to the app.py execution
RECORDINGS_DIR = "recordings"