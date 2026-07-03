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


## Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
2. Scrape Build Data
# Run the scraper (default: Dance of Knives Rogue)
python scraper_maxroll.py

# Or specify a custom build URL
python scraper_maxroll.py https://maxroll.gg/d4/build-guides/your-build-guide
3. Run the Overlay
python main.py
Or use the runner script:
python run.py
Configuration
Change the Build URL
Edit scraper_maxroll.py and modify the MAXROLL_URL constant:
MAXROLL_URL = "https://maxroll.gg/d4/build-guides/your-build-guide"
License
MIT License

---
---
**Besoin d'explications sur une part
