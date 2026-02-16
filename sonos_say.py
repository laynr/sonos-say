#!/usr/bin/env python3
import warnings
import sys

# Suppress urllib3 OpenSSL warning immediately
try:
    warnings.filterwarnings("ignore", message="urllib3 v2 only supports OpenSSL")
except Exception:
    pass

import argparse
import socket
import threading
import time
import http.server
import socketserver
import os
from gtts import gTTS
import gtts.lang
import soco

# Use port 0 to let the OS assign an available port
PORT = 0 
AUDIO_FILE = "sonos_speech.mp3"

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def start_server(ready_event, port_container, directory=None):
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            return # suppress logging
        def __init__(self, *args, **kwargs):
             if directory:
                 super().__init__(*args, directory=directory, **kwargs)
             else:
                 super().__init__(*args, **kwargs)

    # Use port 0 for dynamic assignment
    with socketserver.TCPServer(("", 0), Handler) as httpd:
        port = httpd.server_address[1]
        port_container['port'] = port
        ready_event.set()
        httpd.serve_forever()

def turn_off_leds(devices):
    print("Ensuring LED indicators are OFF on all devices...")
    for device in devices:
        try:
            if hasattr(device, 'status_light') and device.status_light:
                 device.status_light = False
        except Exception as e:
            pass

def is_home_theater(device):
    """Check if device is a home theater setup (has bonded speakers)."""
    try:
        return len(device.group.members) > 1 and device.is_coordinator
    except Exception:
        return False

def check_if_grouped(devices):
    """Check if all devices are already in the same group."""
    if not devices:
        return None
    if len(devices) == 1:
        return devices[0]

    # Check if all share the same coordinator UID
    first_coord = devices[0].group.coordinator
    for d in devices[1:]:
        if d.group.coordinator.uid != first_coord.uid:
            return None
    return first_coord

def create_group(devices):
    """Create a group with all devices, preferring theater master."""
    if not devices:
        return None
    if len(devices) == 1:
        return devices[0]

    # Find Coordinator
    coordinator = None
    # 1. Prefer Home Theater
    for d in devices:
        if is_home_theater(d):
            coordinator = d
            print(f"Using {d.player_name} as coordinator (Home Theater detected).")
            break
    
    # 2. Fallback to first
    if not coordinator:
        coordinator = devices[0]
        print(f"Using {coordinator.player_name} as coordinator.")

    # Ensure it's a standalone coordinator if we are building a new group
    if not coordinator.is_coordinator:
        print(f"Unjoining {coordinator.player_name} to prepare...")
        coordinator.unjoin()
        time.sleep(1)

    # Join others
    print("Grouping devices...")
    for d in devices:
        if d.uid != coordinator.uid:
            try:
                # If already joined to this coordinator, skip
                if d.group.coordinator.uid == coordinator.uid:
                    continue
                
                print(f"Joining {d.player_name} to {coordinator.player_name}...")
                d.join(coordinator)
            except Exception as e:
                print(f"Failed to join {d.player_name}: {e}")
    
    # Wait for topology to settle
    time.sleep(1)
    return coordinator

def ungroup_all(devices):
    """Ungroup all devices."""
    print("Restoring/Ungrouping devices...")
    for d in devices:
        try:
            d.unjoin()
        except Exception:
            pass

def list_languages():
    print("Supported Languages:")
    try:
        langs = gtts.lang.tts_langs()
        # Sort by key
        for code in sorted(langs.keys()):
            print(f"  {code}: {langs[code]}")
    except Exception as e:
        print(f"Error fetching languages: {e}")

def main():
    parser = argparse.ArgumentParser(description="Make Sonos say something.")
    
    # Content Source
    # Note: text is positional, others are optional. We handle exclusivity manually.
    parser.add_argument("text", nargs="*", help="Text to speak")
    parser.add_argument("--file", "-f", help="Read text from this file")
    parser.add_argument("--play-file", "-pf", help="Play local audio file directly")
    parser.add_argument("--play-url", "-pu", help="Play remote audio URL directly")
    parser.add_argument("--languages", action="store_true", help="List supported TTS languages and exit")

    # Target Selection
    parser.add_argument("--device", "-d", "--target", "-t", dest="device", help="Target device name (e.g. 'Kitchen')")
    parser.add_argument("--list", "-l", action="store_true", help="List available devices and exit")
    
    # Playback Options
    parser.add_argument("--volume", "-v", type=int, help="Volume to set (0-100)")
    parser.add_argument("--lang", "-L", default="en", help="Language code for TTS (default: en). See --languages.")
    
    args = parser.parse_args()

    # Handle --languages
    if args.languages:
        list_languages()
        return

    # Discover Sonos
    print("Discovering Sonos devices...")
    try:
        # Suppress soco logging if any
        # logging.getLogger("soco").setLevel(logging.WARNING) 
        devices = list(soco.discover(timeout=2))
    except Exception as e:
        print(f"Discovery failed: {e}")
        return

    if not devices:
        print("No Sonos devices found on the network.")
        return

    # List devices if requested
    if args.list:
        print("Available Sonos devices:")
        for d in devices:
            print(f"- {d.player_name} ({d.ip_address})")
        return

    # Turn off LEDs on all found devices
    turn_off_leds(devices)

    # Determine Audio Source
    audio_url = None
    server_thread = None
    ready_event = None
    port_container = {}
    temp_files_to_cleanup = []

    if args.play_url:
        audio_url = args.play_url
        print(f"Playing URL: {audio_url}")
    elif args.play_file:
        file_path = os.path.abspath(args.play_file)
        if not os.path.exists(file_path):
            print(f"Error: File '{args.play_file}' not found.")
            return
        
        # Start server serving the directory of the file
        directory = os.path.dirname(file_path)
        filename = os.path.basename(file_path)
        
        ready_event = threading.Event()
        server_thread = threading.Thread(target=start_server, args=(ready_event, port_container, directory), daemon=True)
        server_thread.start()
        
        if not ready_event.wait(timeout=5):
            print("Error: Server failed to start.")
            return
        
        local_ip = get_local_ip()
        server_port = port_container.get('port')
        audio_url = f"http://{local_ip}:{server_port}/{filename}"
        print(f"Serving local file: {audio_url}")

    else:
        # TTS mode
        text_to_say = ""
        if args.file:
            try:
                with open(args.file, 'r') as f:
                    text_to_say = f.read().strip()
                print(f"Read {len(text_to_say)} characters from {args.file}")
            except Exception as e:
                print(f"Error reading file: {e}")
                return
        else:
            text_to_say = " ".join(args.text)

        # Interactive Fallback (only if no text and no file provided)
        if not text_to_say:
            try:
                text_to_say = input("Enter text to say: ").strip()
            except KeyboardInterrupt:
                print("\nCancelled.")
                return

        if not text_to_say:
            print("Nothing to say.")
            return
            
        print(f"Preparing to say: '{text_to_say[:50]}...'")

        # Generate Audio
        try:
            tts = gTTS(text_to_say, lang=args.lang)
            tts.save(AUDIO_FILE)
            temp_files_to_cleanup.append(AUDIO_FILE)
        except ValueError as e:
             print(f"Error generating audio: {e}")
             print("Tip: Use --languages to see supported language codes.")
             return
        except Exception as e:
            print(f"Error generating audio: {e}")
            return
        
        # Start Server (current dir)
        ready_event = threading.Event()
        server_thread = threading.Thread(target=start_server, args=(ready_event, port_container), daemon=True)
        server_thread.start()
        
        if not ready_event.wait(timeout=5):
            print("Error: Server failed to start.")
            return

        server_port = port_container.get('port')
        local_ip = get_local_ip()
        audio_url = f"http://{local_ip}:{server_port}/{AUDIO_FILE}"


    # Select target devices
    target_devices = []
    
    if args.device:
        search_term = args.device.lower()
        target_devices = [d for d in devices if search_term in d.player_name.lower()]
        if not target_devices:
            print(f"No device found matching '{args.device}'.")
            return
        elif len(target_devices) > 1:
            print(f"Multiple devices found matching '{args.device}'. Playing on all of them.")
    else:
        # Default to ALL
        target_devices = devices

    # Group management
    coordinator = None
    needs_ungroup = False

    if len(target_devices) > 1:
        # Check if already grouped
        existing_coord = check_if_grouped(target_devices)
        if existing_coord:
            print(f"Devices already grouped under {existing_coord.player_name}.")
            coordinator = existing_coord
        else:
            # Create temp group
            print("Creating temporary group...")
            coordinator = create_group(target_devices)
            needs_ungroup = True
    else:
        coordinator = target_devices[0]

    # Set Volume
    if args.volume is not None:
        try:
            print(f"Setting volume to {args.volume}...")
            coordinator.group.volume = args.volume
        except Exception as e:
            print(f"Warning: Could not set volume: {e}")

    # Play
    print(f"Playing...")
    try:
        coordinator.play_uri(audio_url)
        
        # Wait for playback (heuristic or fixed)
        wait_time = 5
        if args.play_url or args.play_file:
            wait_time = 10 # Default wait for custom files
        elif 'text_to_say' in locals():
             wait_time = 3 + (len(text_to_say) * 0.1)
             
        time.sleep(wait_time) 
        
    except Exception as e:
        print(f"Error playing audio: {e}")
    finally:
        if needs_ungroup:
            ungroup_all(target_devices)
        
        # Cleanup
        for f in temp_files_to_cleanup:
            if os.path.exists(f):
                 os.remove(f)

if __name__ == "__main__":
    main()
