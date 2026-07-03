# Diablo 4 Build Overlay

A local Windows overlay for displaying Diablo 4 build data from [maxroll.gg](https://maxroll.gg).
Supports multiple build versions (Starter, Midgame, Endgame, Endgame Mythic Seal) and
displays equipment, aspects, skills, gems, and paragon board data.

## Features

- ✅ **Multi-version support**: Switch between Starter, Midgame, Endgame, and Endgame Mythic Seal builds
- ✅ **Complete data extraction**: Equipment with aspects, skills, gems, and paragon boards with stats
- ✅ **No webview dependency**: Uses `requests` + `BeautifulSoup` for reliable scraping
- ✅ **Tkinter-based overlay**: Lightweight, always-on-top window
- ✅ **Responsive design**: Scrollable tabs for each data category

## Project Structure
diablo4-overlay/
├── scraper_maxroll.py    # Main scraper script
├── main.py               # Tkinter overlay application
├── requirements.txt      # Python dependencies
├── builds.json           # Generated build data (output)
├── builds.json.example   # Example output format
└── README.md             # This file
