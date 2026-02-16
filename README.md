# Sonos Say

A smart and simple command-line tool to make your Sonos system speak.

It automatically handles device discovery, grouping (including home theater setups), and cleanup, so your messages play synchronously across your home.

## Features

- **Smart Grouping:** Automatically detects Home Theater setups (Arc/Beam) and uses them as the master coordinator.
- **Auto-Sync:** Creates temporary groups to play on all speakers at once, then restores them.
- **LED Control:** Automatically turns off status LEDs on all devices.
- **Flexible Input:** Type a message, pipe text, or read from a file.
- **Multi-Language:** Supports different languages/accents via Google TTS.

## Quick Start

### Prerequisites
- Python 3 installed.
- Internet connection (for Google TTS).

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/laynr/sonos-say.git
    cd sonos-say
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Make executable (optional):**
    ```bash
    chmod +x sonos_say.py
    ```

## Usage

Run the script directly using `./sonos_say.py` (if executable) or `python3 sonos_say.py`.

### Basic Examples

**Speak a message on all speakers (default):**
```bash
./sonos_say.py "Dinner is ready!"
```

**Speak on a specific device (e.g., Kitchen):**
```bash
./sonos_say.py "Water is boiling" --target Kitchen
```

**Interactive Mode (prompts for text):**
```bash
./sonos_say.py
```

### Advanced Usage

**Read message from a file:**
```bash
./sonos_say.py --file announcement.txt
```

**Speak with an accent (e.g., Australian English):**
```bash
./sonos_say.py "G'day mate" --lang en-au
```
*Supports standard language codes: en, en-us, en-uk, en-au, fr, es, de, etc.*

**Set Volume:**
```bash
./sonos_say.py "Wake up!" --volume 50
```

**List available devices:**
```bash
./sonos_say.py --list
```

## Troubleshooting

- **No devices found?** Ensure your computer is on the same Wi-Fi network as your Sonos system.
- **Permission denied?** Run `chmod +x sonos_say.py` to make the script executable.
- **Python not found?** Try running with `python3 sonos_say.py` instead of `./sonos_say.py`.
