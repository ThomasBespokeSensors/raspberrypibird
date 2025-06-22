# audio_processing/recorder.py

import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wavfile
import time
import collections
import os
import threading

# Import configurations from the project's config.py
from config import (
    SAMPLERATE,
    CHANNELS,
    THRESHOLD,
    MAX_RECORDING_DURATION,
    SILENCE_DURATION_TO_STOP,
    BLOCKSIZE,
    DEVICE_INDEX,
    RECORDINGS_DIR
)

# --- Global State Variables ---
# Use a deque for the recording buffer for efficient appending and clearing
recording_buffer = collections.deque()
recording_active = False          # True if currently recording
recording_start_time = 0.0        # Unix timestamp when current recording started
last_loud_time = 0.0              # Unix timestamp when sound was last above threshold
save_recording_flag = threading.Event() # Event to signal the main thread to save
recorded_audio_data = None        # Stores the audio data to be saved
program_running = True            # Flag to keep the main loop running

# --- Audio Callback Function ---
def audio_callback(indata, frames, time_info, status):
    """
    This function is called by sounddevice for each block of audio input.
    It handles volume monitoring, recording state, and triggering saves.
    """
    global recording_active, recording_start_time, last_loud_time
    global recorded_audio_data, program_running

    if status:
        # Print any warnings from the audio stream
        print(f"Sounddevice status warning: {status}")

    # Calculate RMS (Root Mean Square) volume level
    # Convert stereo to mono if needed for RMS calculation
    if indata.shape[1] > 1:
        mono_data = indata[:, 0] # Use the first channel for RMS if stereo
    else:
        mono_data = indata.flatten()

    # Calculate RMS volume (standard deviation is a good proxy for RMS of a zero-mean signal)
    volume_rms = np.sqrt(np.mean(mono_data**2))

    current_time = time.time()

    # --- Logic for Recording State ---
    if recording_active:
        # If currently recording, add the current audio block to the buffer
        recording_buffer.append(indata.copy())

        # Update last_loud_time if volume is above threshold
        if volume_rms > THRESHOLD:
            last_loud_time = current_time

        # Check stop conditions
        elapsed_recording_time = current_time - recording_start_time
        time_since_last_loud = current_time - last_loud_time

        # Condition 1: Max recording duration reached
        if elapsed_recording_time >= MAX_RECORDING_DURATION:
            print(f"Max recording duration ({MAX_RECORDING_DURATION}s) reached. Stopping recording.")
            recording_active = False
            # Set event to signal main thread to save
            recorded_audio_data = np.concatenate(recording_buffer, axis=0)
            save_recording_flag.set()

        # Condition 2: Silence duration exceeded
        elif time_since_last_loud >= SILENCE_DURATION_TO_STOP:
            print(f"Silence detected for {SILENCE_DURATION_TO_STOP}s. Stopping recording.")
            recording_active = False
            # Set event to signal main thread to save
            recorded_audio_data = np.concatenate(recording_buffer, axis=0)
            save_recording_flag.set()

    else: # Not currently recording, listening for sound
        if volume_rms > THRESHOLD:
            print(f"Loud sound detected (RMS: {volume_rms:.4f}). Starting recording...")
            recording_active = True
            recording_start_time = current_time
            last_loud_time = current_time
            # Clear buffer and start fresh for new recording
            recording_buffer.clear()
            recording_buffer.append(indata.copy()) # Add the current block to start the recording

# --- Main Program Execution ---
def run_recorder(): # Renamed from main() to run_recorder() for clarity when imported
    global recorded_audio_data, program_running

    print("--- Voice Activated Recorder ---")
    print(f"Listening for sounds above RMS threshold: {THRESHOLD}")
    print(f"Max recording duration: {MAX_RECORDING_DURATION} seconds")
    print(f"Stop after {SILENCE_DURATION_TO_STOP} seconds of silence")

    # Ensure the recordings directory exists
    if not os.path.exists(RECORDINGS_DIR):
        os.makedirs(RECORDINGS_DIR)
    print(f"Saving files to: {os.path.abspath(RECORDINGS_DIR)}")

    # Find and set the device if a specific index is provided
    if DEVICE_INDEX is not None:
        try:
            sd.default.device = DEVICE_INDEX
            print(f"Using audio device index: {DEVICE_INDEX}")
        except Exception as e:
            print(f"Error setting device {DEVICE_INDEX}: {e}")
            print("Please ensure the device index is correct. Run 'python -m sounddevice' to list devices.")
            return

    try:
        # Start the audio stream in non-blocking mode with the callback
        with sd.InputStream(samplerate=SAMPLERATE,
                            channels=CHANNELS,
                            callback=audio_callback,
                            blocksize=BLOCKSIZE,
                            device=DEVICE_INDEX):
            print("\nProgram started. Press Ctrl+C to stop.") # Updated message
            # Main loop to keep the program running and handle file saving
            while program_running:
                # Wait for the save_recording_flag to be set by the callback
                # Timeout ensures the loop doesn't block indefinitely
                if save_recording_flag.wait(timeout=0.1): # Wait for 100ms
                    if recorded_audio_data is not None:
                        # Construct filename with timestamp
                        timestamp = time.strftime("%Y%m%d-%H%M%S")
                        filename = f"recording_{timestamp}.wav"
                        filepath = os.path.join(RECORDINGS_DIR, filename) # Save to the recordings directory

                        try:
                            # Ensure the data type is appropriate for WAV saving (e.g., int16 or float32)
                            # Convert to int16 for common WAV compatibility
                            # Scale float data from -1 to 1 to int16 range -32768 to 32767
                            if recorded_audio_data.dtype == np.float32:
                                audio_to_save = (recorded_audio_data * 32767).astype(np.int16)
                            else:
                                audio_to_save = recorded_audio_data.astype(np.int16) # Ensure it's int16

                            # Save the WAV file
                            wavfile.write(filepath, SAMPLERATE, audio_to_save)
                            print(f"Saved recording: {filename}")
                        except Exception as e:
                            print(f"Error saving audio file {filename}: {e}")
                        finally:
                            recorded_audio_data = None # Clear data after saving attempt
                            recording_buffer.clear() # Clear buffer for next recording
                            save_recording_flag.clear() # Reset the event flag

    except KeyboardInterrupt:
        print("\nStopping program via KeyboardInterrupt.")
        program_running = False
    except Exception as e:
        print(f"\nAn error occurred: {e}")
    finally:
        print("Program stopped.")