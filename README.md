# speech2caret

Use your speech to write to the current caret position!

Goals:

- ✅ Simple, minimalist.
- ✅ Local transcription.
- ✅ CPU Optimized.

Note: this has only been tested on Linux (Ubuntu), and it is unlikely to (currently) support other operating systems. 

## Setup

### Prerequisites

Before installing `speech2caret`, you need to ensure that the following system libraries are installed:

```bash
sudo apt install libportaudio2 ffmpeg
```

For evdev (which is used to read keyboard events and write to the current caret position), you may need to add your user to the input group (typically "input") to have read/write access.

```bash
sudo usermod -aG input $USER
```

### Installation

Once the prerequisites are installed, you can run `speech2caret` (from PyPI) with:

```bash
uvx --from speech2caret speech2caret
```

Or install it:

```bash
uv add speech2caret
# or 
pip install speech2caret
```

## Usage

1.  **Configure the application**:
    *   The first time you run `speech2caret`, it will create a configuration file at `~/.config/speech2caret/config.ini`.
    *   You will need to edit this file to set `keyboard_device_path`, `start_stop_key`, and `resume_pause_key`. 
        * `keyboard_device_path`: Specifies the path to the keyboard device to listen for key presses. You can find the correct path by running `ls /dev/input/by-path/` and looking for the ones ending in `-event-kbd`.
        * `start_stop_key` and `resume_pause_key`: The keyboard keycodes you want to use to start/stop and resume/pause recording. A list of valid keycode names can be found online (e.g. [here](https://github.com/torvalds/linux/blob/a79a588fc1761dc12a3064fc2f648ae66cea3c5a/include/uapi/linux/input-event-codes.h#L65)).
          Equally you should be able to run the following to determine the keycode name when you press keys on your keyboard:
```python
# You can create a suitable python environment to run this with: uvx --from speech2caret python
from evdev import InputDevice, categorize, ecodes, KeyEvent

keyboard_device_path = "ADD_YOUR_KEYBOARD_DEVICE_PATH_HERE"
dev = InputDevice(keyboard_device_path)

for event in dev.read_loop():
    if event.type == ecodes.EV_KEY:
        key_event = categorize(event)
        if key_event.keystate == KeyEvent.key_down:
            print(key_event.keycode)
```

2.  **Run the application**:

```bash
speech2caret
```

3.  **Start/Stop and Pause/Resume**:
    *   Press the keyboard keys you specified in the configuration file to start/stop and resume/pause recording.
