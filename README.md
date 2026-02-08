# Clock App

A simple desktop clock application that displays the current time and date. Built with Python and tkinter.

## Overview

- **Version:** 0.0.01 (Pre-Alpha)
- **Author:** Dramora9879
- **License:** All Rights Reserved
- **Repository:** [GitHub - Clock-App](https://github.com/DramoraFramei/Clock_App)

## Features

### Clock Display

- **Digital clock** ? Displays time in 12-hour or 24-hour format
- **Configurable timezone** ? UTC, GMT, EST, CST, MST, PST, or any IANA timezone
- **Customizable formatting** ? Time separator, date separator, and date format
- **Appearance** ? Customizable clock color, font, and font size

### Options

- **Multi-language support** ? English, Arabic, French, German, Italian, Portuguese, Russian, Spanish, Turkish
- **Theme** ? Light or Dark
- **Notifications** ? Vibrate, Sound, or Popup
- **Update settings** ? Automatic or manual updates; Stable, Beta, or Dev channels

### Developer Features

- **Console** ? Toggle with `~` or `` ` `` for debugging
- **Configuration** ? `clock_app.ini` for persistent settings

## Requirements

- Python 3.9+
- Dependencies (see `requirements.txt`):
  - configparser >= 7.2.0
  - deep-translator >= 1.11.0
  - Pillow >= 10.0.0
  - tzdata >= 2024.1

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/DramoraFramei/Clock-App.git
   cd Clock-App
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   source .venv/bin/activate  # macOS/Linux
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

From the `apps` directory (or project root containing `clock_app`):

```bash
python -m clock_app.app
```

Or:

```bash
python -m clock_app
```

### Main Menu

- **Clock** ? View the clock
- **Options** ? Configure language, theme, timezone, time/date format, and more
- **Exit** ? Quit the application

## Configuration

Settings are stored in `clock_app/config/clock_app.ini` and can be edited directly or via the Options menu. Key sections:

| Section       | Options                                                               |
| ------------- | --------------------------------------------------------------------- |
| General       | Language                                                              |
| Display       | Theme, timezone, time/date separators, 12/24-hour format, date format |
| Behavior      | Clock color, font, font size                                          |
| Notifications | Notification option, type (Vibrate/Sound/Popup)                       |
| Updates       | Update option, channel, frequency, source                             |

## Project Structure

```file_structure
apps/
??? clock_app/
?   ??? app.py              # Main application
?   ??? imports.py          # Module imports
?   ??? assets/
?   ?   ??? images/         # Clock face and hand images
?   ?   ??? lib/lang/       # Translation JSON files
?   ??? config/
?   ?   ??? clock_app.ini   # User configuration
?   ??? data/
?       ??? defaults/       # Default option values
?       ??? menus/          # UI screens (clock, main, options, etc.)
?       ??? scripts/        # Utility scripts
??? requirements.txt
??? LICENSE
??? README.md
```

## License

Copyright (c) Dramora9879. All Rights Reserved. See [LICENSE](LICENSE) for details.
