import json
import time
import os

DATA_FILE = 'times.json'
MAX_TAPS = 12

def load_existing_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def get_metadata():
    artist = input("Enter quartet name:\n> ").strip()
    spotify = input("Enter Spotify URL or URI:\n> ").strip()
    track_length = input("Enter track length (as MM:SS):\n> ").strip()
    return artist, spotify, track_length

def collect_timestamps():
    print("\nPress ENTER to mark each timestamp.")
    print(f"Press ENTER {MAX_TAPS} times to complete.\n")

    timestamps = []
    start_time = None

    for i in range(MAX_TAPS):
        input(f"Press ENTER ({i+1}/{MAX_TAPS})")
        now = time.time()
        if start_time is None:
            start_time = now
            timestamps.append(0)
        else:
            timestamps.append(round(now - start_time, 3))

    return timestamps

def main():
    data = load_existing_data()
    while True:
        artist, spotify, track_length = get_metadata()
        timestamps = collect_timestamps()

        data.append({
            "artist": artist,
            "spotify": spotify,
            "track_length": track_length,
            "timestamps": timestamps
        })
        save_data(data)
        print(f"Saved {len(timestamps)} timestamps.\n")

        again = input("Record another? (y/n): ").strip().lower()
        if again != 'y':
            break

if __name__ == "__main__":
    main()
