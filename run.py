#!/usr/bin/env python3
"""
Diablo 4 Overlay - Runner Script
Scrapes build data and launches the overlay in one command.
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Run scraper and then launch overlay."""
    print("Diablo 4 Build Overlay - Starting...")
    print("=" * 50)

    # Step 1: Run scraper
    print("\n[1/2] Scraping build data from maxroll.gg...")
    scraper_result = subprocess.run(
        [sys.executable, "scraper_maxroll.py"] + sys.argv[1:],
        capture_output=True,
        text=True
    )

    if scraper_result.returncode != 0:
        print(f"Scraper error: {scraper_result.stderr}")
        print("Continuing with existing data (if any)...")
    else:
        print(scraper_result.stdout)

    # Step 2: Launch overlay
    print("\n[2/2] Launching overlay...")
    print("Press Ctrl+C in this window to exit the overlay.")
    print("-" * 50)

    overlay_result = subprocess.run(
        [sys.executable, "main.py"]
    )

    if overlay_result.returncode != 0:
        print(f"Overlay exited with error code: {overlay_result.returncode}")
    else:
        print("\nOverlay closed successfully.")

if __name__ == "__main__":
    main()