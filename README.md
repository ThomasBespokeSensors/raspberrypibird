# Raspberry Pi Bird Song Recorder & Analyzer

## 🚀 Overview

This project enables your Raspberry Pi to act as a noise-activated recorder for bird noises, saving audio segments for potential future analysis. It leverages the `sounddevice` library for efficient audio input and employs a multi-threaded architecture to ensure smooth, real-time recording without interruption.

## ✨ Program Structure: Two Threads at Work

The application operates using two primary threads to separate audio capture from file saving, preventing performance bottlenecks:

1.  **Audio Callback Thread (Producer):**
    * This thread is managed by the `sounddevice` library. It continuously listens to the microphone input and executes the `audio_callback` function for each block of audio data.
    * Its main responsibilities include:
        * Monitoring audio volume (RMS).
        * Detecting loud sounds to initiate a recording.
        * Appending audio blocks to an in-memory buffer (`recording_buffer`).
        * Monitoring recording duration and silence levels to determine when to stop a recording.
        * **Signaling the main thread** to save the recorded audio by setting a `threading.Event` (`save_recording_flag`). This is crucial because file I/O (saving) can be slow and would disrupt real-time audio processing if done in this thread.

2.  **Main Application Thread (Consumer):**
    * This is the primary thread where your `run_recorder()` function executes.
    * Its main responsibilities include:
        * Initializing the audio stream.
        * **Waiting for a signal** from the audio callback thread (using `save_recording_flag.wait()`) that a recording is complete and ready to be saved.
        * When signaled, it retrieves the recorded audio data from a shared variable.
        * Performs the resource-intensive task of **saving the concatenated audio data to a `.wav` file** on disk.
        * Clears the recording buffer and the `save_recording_flag` to prepare for the next recording cycle.
        * Handles program shutdown via `Ctrl+C`.

This multi-threaded design ensures that the audio input stream remains uninterrupted, providing a robust and responsive recording system.

## ⚙️ Installation

### On the Raspberry Pi

This project is designed to run directly on your Raspberry Pi. It does *not* utilize Docker due to potential complexities with USB microphone access within containerized environments.

1.  **Install Audio Libraries:**
    ```bash
    sudo apt-get update
    sudo apt-get install portaudio19-dev python3-pyaudio
    ```

### GitHub Setup

1.  **Navigate to Home Directory:**
    ```bash
    cd ~
    ```
2.  **Create GitHub Directory:**
    ```bash
    mkdir github
    cd github
    ```
3.  **Install Git:**
    ```bash
    sudo apt update
    sudo apt install git
    ```
4.  **Configure Git (replace with your details):**
    ```bash
    git config --global user.name "Your Name"
    git config --global user.email "your.email@example.com"
    ```
5.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/ThomasBespokeSensors/raspberrypibird](https://github.com/ThomasBespokeSensors/raspberrypibird)
    ```

### Python Virtual Environment

It's highly recommended to use a Python virtual environment to manage project dependencies.

1.  **Navigate to Project Directory:**
    ```bash
    cd ~/github/raspberrypibird
    ```
2.  **Create Virtual Environment (named `.venv`):**
    ```bash
    python3 -m venv .venv
    ```
3.  **Activate Virtual Environment:**
    ```bash
    source .venv/bin/activate
    ```
    (Your terminal prompt should now show `(.venv)` indicating activation.)
4.  **Install Requirements:**
    ```bash
    pip install -r requirements.txt
    ```

## 🚀 Running the Application

1.  **Activate Virtual Environment** (if not already active):
    ```bash
    cd ~/github/raspberrypibird
    source .venv/bin/activate
    ```
2.  **Run the Application:**
    ```bash
    python3 app.py
    ```

    The recorder will start listening for sounds. Press `Ctrl+C` in the terminal to stop the program.