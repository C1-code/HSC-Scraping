# THSC Scraping Tool

## Overview

The THSC Scraping Tool automates scraping downloadable files from the THSC Online website. It extracts Year 12 Mathematics resources, generates file URLs, and downloads them.

## Features

- ✨ Adjusts year range dynamically.
- 🧹 Parses HTML efficiently with BeautifulSoup.
- 🤖 Automates downloads with Selenium.
- ⚠️ Handles timeout errors gracefully.

## Prerequisites

1. 🐍 **Python 3.8+**
2. 📚 Install libraries:
   - `requests`
   - `beautifulsoup4`
   - `selenium`
3. 🌐 **Chrome WebDriver** matching your browser version.
4. 🌎 **Google Chrome Browser**.

## Installation

1. 📥 Clone/download `THSC-Scraping.py`.
2. 📦 Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. 🖥️ Place `chromedriver.exe` in the project directory.

## Usage

1. ▶️ Run the script:
   ```bash
   python THSC-Scraping.py
   ```
2. The script will:
   - 🔍 Fetch Year 12 Math links.
   - 📋 Generate download URLs.
   - 💾 Download files into your directory.

## File Structure

```
THSC-Scraping/
  |-- THSC-Scraping.py
  |-- chromedriver.exe
  |-- requirements.txt
```

## Key Functions

- 🗓️ **`getYears()`**: Lists years from 2019 to the current year.
- 🌐 **`getResponse(url)`**: Fetches HTML or raises `TimeoutError`.
- 🖇️ **`getLinks()`**: Extracts `.html` links.
- 🔗 **`getFiles()`**: Identifies file URLs for download.
- 💻 **`downloadLinks()`**: Automates downloading.

## Notes

- ✅ Match `chromedriver.exe` to your Chrome version.
- 💾 Ensure enough storage space.
- 🚀 Avoid running multiple script instances.

## Troubleshooting

- ⏳ **Timeout Errors:** Check URL and website access.
- 🛠️ **Selenium Issues:** Verify `chromedriver.exe` setup.
- ❌ **Missing Dependencies:** Install via `pip install`.

## License

Licensed under MIT License.

---

Efficient resource scraping for THSC Online.
