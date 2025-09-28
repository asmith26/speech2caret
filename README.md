# speech2caret

<p align="center">
    <img src="https://github.com/asmith26/speech2caret/raw/refs/heads/main/assets/speech2caret_logo.svg" alt="speech2caret logo" width="250"/>
</p>
<p align="center">
Use your speech to write to the current caret position!
</p>


## Goals

- ✅ **Simple**: A minimalist tool that does one thing well.
- ✅ **Local**: Runs entirely on your machine (uses [Hugging Face models](https://huggingface.co/models) for speech recognition).
- ✅ **Efficient**: Optimised for low CPU and memory usage, thanks to an event-driven architecture that responds instantly to key presses without wasting resources.

**Note**: Tested only on Linux (Ubuntu). Other operating systems are currently unsupported.

**Demo (turn volume on):**

[demo video](https://github.com/user-attachments/assets/6de72da8-0aa2-40c4-802d-82772881c862)

## Installation

### 1. System Dependencies

First, install the required system libraries:

```bash
sudo apt update
sudo apt install libportaudio2 ffmpeg
```

### 2. Grant Permissions

To read keyboard events and simulate key presses, [`evdev`](https://python-evdev.readthedocs.io/en/latest/usage.html#listing-accessible-event-devices) needs access to your keyboard input device. Add your user to the `input` group to grant the necessary permissions:

```bash
sudo usermod -aG input $USER
newgrp input  # or log out and back in 
```
    
### 3. Install and Run

You can install and run `speech2caret` using `pip` or `uv`:

```bash
# Install the package
uv add speech2caret  # or pip install speech2caret

# Run the application
speech2caret
```

Alternatively, you can run it directly without installation using `uvx`(the `--index pytorch-cpu=...` flag ensures only CPU packages are downloaded, avoiding GPU-related dependencies):

```bash
uvx --index pytorch-cpu=https://download.pytorch.org/whl/cpu --from speech2caret speech2caret
```

## Configuration

The first time you run `speech2caret`, it creates a config file at `~/.config/speech2caret/config.ini`.

You’ll need to manually edit it with the following values:

#### `keyboard_device_path`
This is the path to your keyboard input device. You can find the path either following [this](https://python-evdev.readthedocs.io/en/latest/usage.html#listing-accessible-event-devices), or by running the command below and looking for an entry that ends with `-event-kbd`.

```bash
ls /dev/input/by-path/
```

#### `start_stop_key` and `resume_pause_key`
These are the keys you'll use to control the app.

To find the correct name for a key, you can use the provided Python script below. First, ensure you have your `keyboard_device_path` from the step above, then run this command:

```bash
uvx --from evdev python -c '
keyboard_device_path = "PASTE_YOUR_KEYBOARD_DEVICE_PATH_HERE"

from evdev import InputDevice, categorize, ecodes, KeyEvent
dev = InputDevice(keyboard_device_path)
print(f"Listening for key presses on {dev.name}...")
for event in dev.read_loop():
    if event.type == ecodes.EV_KEY:
        key_event = categorize(event)
        if key_event.keystate == KeyEvent.key_down:
            print(f" {key_event.keycode}")
'
```
Press the keys you wish to use, and their names will be printed to the terminal. For a full list of available key names, see [here](https://github.com/torvalds/linux/blob/a79a588fc1761dc12a3064fc2f648ae66cea3c5a/include/uapi/linux/input-event-codes.h#L65).

### Additional (Optional) Configuration

You can configure audio cues to notify when recording has started, stopped, paused, or resumed. To do this, update 
the `start_recording_audio_path`, `stop_recording_audio_path`, `resume_recording_audio_path`, and `pause_recording_audio_path`
config variables in `~/.config/speech2caret/config.ini` with the absolute paths to your choice of audio files.

## How to Use

1.  Run the `speech2caret` command in your terminal.
2.  Press your configured `start_stop_key` to begin recording.
3.  Press the `resume_pause_key` to toggle between pausing and resuming.
4.  When you are finished, press the `start_stop_key` again.
5.  The recorded audio will be transcribed and typed at your current caret position.
