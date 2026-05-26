#!/usr/bin/env python3
import math
import os
import subprocess
import sys
import time


def prompt_minutes() -> float:
    while True:
        raw = input("Enter countdown minutes: ").strip()
        if not raw:
            print("Please enter a number of minutes.")
            continue
        try:
            minutes = float(raw)
        except ValueError:
            print("Invalid number. Try again.")
            continue
        if minutes <= 0:
            print("Minutes must be greater than 0.")
            continue
        return minutes


def format_remaining(total_seconds: int) -> str:
    minutes, seconds = divmod(total_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"


def countdown(total_seconds: int) -> None:
    end_time = time.monotonic() + total_seconds
    while True:
        remaining = int(end_time - time.monotonic())
        if remaining < 0:
            break
        print(f"\rShutdown in {format_remaining(remaining)}", end="", flush=True)
        time.sleep(1)
    print()


def shutdown_now() -> None:
    # On macOS prefer asking the logged-in user session to shut down via AppleScript.
    # This avoids prompting for a sudo password in many cases.
    if sys.platform == "darwin":
        try:
            subprocess.run(["osascript", "-e", 'tell application "System Events" to shut down'], check=True)
            return
        except subprocess.CalledProcessError:
            # Fall back to the system shutdown command if AppleScript fails.
            pass

    command = ["/sbin/shutdown", "-h", "now"]
    if os.geteuid() == 0:
        subprocess.run(command, check=True)
        return
    subprocess.run(["sudo", *command], check=True)


def main() -> int:
    print("Press Ctrl+C to cancel.")
    minutes = prompt_minutes()
    total_seconds = math.ceil(minutes * 60)
    countdown(total_seconds)
    shutdown_now()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nCanceled.")
