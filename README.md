# Sonos Say

A smart and simple command-line tool to make your Sonos system speak.

It automatically handles device discovery, grouping (including home theater setups), and cleanup, so your messages play synchronously across your home.

## Features

- **Smart Grouping:** Automatically detects Home Theater setups (Arc/Beam) and uses them as the master coordinator.
- **Auto-Sync:** Creates temporary groups to play on all speakers at once, then restores them.
- **LED Control:** Automatically turns off status LEDs on all devices.
- **Flexible Input:** Type a message, pipe text, read from a file, or play your own audio files.
- **Multi-Language:** Supports different languages/accents via Google TTS.
- **Cross-Platform:** Works on Windows, macOS, and Linux.

## Quick Start

### Prerequisites
- Python 3 installed.
- Internet connection (for Google TTS).
- **Windows Users:** You may need to allow "Python" through the Windows Firewall when prompted, as the tool runs a small local web server to send audio to your speakers.

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

3.  **(Optional - macOS/Linux only) Make executable:**
    ```bash
    chmod +x sonos_say.py
    ```

## Usage

Run the script using Python:

### Basic Examples

**Speak a message on all speakers (default):**
```bash
python sonos_say.py "Dinner is ready!"
```

**Speak on a specific device (e.g., Kitchen):**
```bash
python sonos_say.py "Water is boiling" --target Kitchen
```

**Interactive Mode (prompts for text):**
```bash
python sonos_say.py
```

### Advanced Usage

**Read message from a file:**
```bash
python sonos_say.py --file announcement.txt
```

**Play a local audio file:**
```bash
python sonos_say.py --play-file ./my_sound.mp3
```

**Play a remote URL (e.g., radio stream):**
```bash
python sonos_say.py --play-url http://stream.radioparadise.com/aac-320
```

**Speak with an accent or language:**
```bash
python sonos_say.py "Bonjour tout le monde" --lang fr
```

**List supported languages:**
```bash
python sonos_say.py --languages
```
*Common codes:*
- `en`: English
- `es`: Spanish
- `fr`: French
- `de`: German
- `zh-cn`: Chinese (Simplified)
- `zh-tw`: Chinese (Traditional)
- `ja`: Japanese
- `ko`: Korean

**Set Volume:**
```bash
python sonos_say.py "Wake up!" --volume 50
```

**List available devices:**
```bash
python sonos_say.py --list
```

## Troubleshooting

- **No devices found?** Ensure your computer is on the same Wi-Fi network as your Sonos system.
- **Windows Firewall:** If devices are found but audio doesn't play, check your Windows Firewall settings to ensure Python can accept incoming connections (required for the HTTP server).
- **SSL Warning?** The script automatically suppresses common SSL warnings on macOS.
