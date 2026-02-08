# pylint: disable=line-too-long,unused-import,import-outside-toplevel,import-error,no-name-in-module
"""
This is the imports module for the clock app.
It will contain the imports for the clock app.
"""

import os
from importlib import import_module
from types import ModuleType

# Use __file__ to avoid circular import during package load
_IMPORTS_DIR: str = os.path.dirname(os.path.abspath(__file__))
APP_ROOT: str = _IMPORTS_DIR
# The config folder is the folder called config in the clock app folder
CONFIG_FOLDER: str = os.path.join(APP_ROOT, "config")
# Path to the clock app config file (used for create-if-missing and loading)
CLOCK_APP_INI_PATH: str = os.path.join(CONFIG_FOLDER, "clock_app.ini")
# The assets folder is the folder called assets in the clock app folder
ASSETS_FOLDER: str = os.path.join(APP_ROOT, "assets")
# The images folder is the folder called images in the assets folder
IMAGES_FOLDER: str = os.path.join(ASSETS_FOLDER, "images")
# The lang folder for translation JSON files
LANG_FOLDER: str = os.path.join(ASSETS_FOLDER, "lib", "lang")
# The data folder is the folder called data in the clock app folder
DATA_FOLDER: str = os.path.join(APP_ROOT, "data")
# The scripts folder is the folder called scripts in the data folder
SCRIPTS_FOLDER: str = os.path.join(DATA_FOLDER, "scripts")
# The menus folder is the folder called menus in the data folder
MENUS_FOLDER: str = os.path.join(DATA_FOLDER, "menus")
DEFAULT_FOLDER: str = os.path.join(DATA_FOLDER, "defaults")
# Load modules in dependency order to avoid circular imports
_CLOCK_APP_PKG: str = "clock_app"
DEFAULT_OPTIONS_MODULE: ModuleType = import_module(
    f"{_CLOCK_APP_PKG}.data.defaults.default_options")
default_options = DEFAULT_OPTIONS_MODULE.DefaultOptions
CREATE_CLOCK_APP_INI_MODULE: ModuleType = import_module(
    f"{_CLOCK_APP_PKG}.data.scripts.create_clock_app_ini")
create_clock_app_ini = CREATE_CLOCK_APP_INI_MODULE.CreateClockAppIni
OPTIONS_MODULE: ModuleType = import_module(
    f"{_CLOCK_APP_PKG}.data.menus.options")
Options = OPTIONS_MODULE.Options
LOADING_FILE_MODULE: ModuleType = import_module(
    f"{_CLOCK_APP_PKG}.data.menus.loading")
Loading = LOADING_FILE_MODULE.Loading
CONSOLE_FILE_MODULE: ModuleType = import_module(
    f"{_CLOCK_APP_PKG}.data.menus.console")
Console = CONSOLE_FILE_MODULE.Console
MAIN_MENU_FILE_MODULE: ModuleType = import_module(
    f"{_CLOCK_APP_PKG}.data.menus.main")
MainMenu = MAIN_MENU_FILE_MODULE.MainMenu
CLOCK_FILE_MODULE: ModuleType = import_module(
    f"{_CLOCK_APP_PKG}.data.menus.clock")
Clock = CLOCK_FILE_MODULE.Clock
ANALOG_CLOCK_IMAGE: str = os.path.join(IMAGES_FOLDER, "analog_clock.png")
analog_clock_image = ANALOG_CLOCK_IMAGE
HOUR_HAND_IMAGE: str = os.path.join(
    IMAGES_FOLDER, "analog_clock_hour_hand.png")
hour_hand_image = HOUR_HAND_IMAGE
MINUTE_HAND_IMAGE: str = os.path.join(
    IMAGES_FOLDER, "analog_clock_minute_hand.png")
minute_hand_image = MINUTE_HAND_IMAGE
SECOND_HAND_IMAGE: str = os.path.join(
    IMAGES_FOLDER, "analog_clock_second_hand.png")
second_hand_image = SECOND_HAND_IMAGE


def __getattr__(name: str):
    """Lazy-load ClockApp to avoid circular import with app.py."""
    if name == "ClockApp":
        from clock_app.app import ClockApp
        return ClockApp
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
