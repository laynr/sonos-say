# Sonos Say

A Python script to make your Sonos system speak text messages.

## Features
- **Generic:** Works on any network with Sonos devices.
- **Smart Grouping:** Automatically identifies home theater setups (e.g., Arc, Beam) and uses them as the master for synchronized playback.
- **LED Control:** Automatically turns off status LEDs on all devices.
- **Temporary Grouping:** Creates a temporary group for playback and restores (ungroups) afterwards if needed.
- **Interactive:** Prompts for text if not provided as an argument.

## Usage

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the script:
   ```bash
   python sonos_say.py "Hello World"
   ```

   Or run without arguments for interactive mode:
   ```bash
   python sonos_say.py
   ```

   List available devices:
   ```bash
   python sonos_say.py --list
   ```

   Play on a specific device (e.g., "Kitchen"):
   ```bash
   python sonos_say.py "Dinner is ready" --device Kitchen
   ```
