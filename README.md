# raspberrypibird
Recording and analysing bird noises via microphone and raspberry pi

## Install on the Raspberry Pi

- portaudio19-dev 
- python3-pyaudio

This is not run in a docker because of potential issues accessing the USB mic through the docker container

```sudo apt-get install portaudio19-dev python3-pyaudio```

## Install github

```
cd ~
mkdir github
cd github
```

```
sudo apt update
sudo apt install git
```

Configure git

```
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

Clone the repository
```
git clone https://github.com/ThomasBespokeSensors/raspberrypibird
```

## Create the Python virtual environment

```
cd ~/github/raspberrypibird
```

Create the virtual environment called .venv 
```
python3 -m venv .venv
```

Activate the virtual environment
```
source .venv/bin/activate
```

Install the requirements
```
pip install -r requirements.txt
```

## Run the app
Activate the virtual environment (if not already activitate)
```
source .venv/bin/activate
```
Run the app
```
python3 app.py
```