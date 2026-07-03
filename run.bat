@echo off
:: Diablo 4 Overlay - Windows Batch Runner
:: Scrapes build data and launches the overlay

python scraper_maxroll.py %*
echo.
echo Launching overlay...
echo Press Ctrl+C in this window to exit
python main.py