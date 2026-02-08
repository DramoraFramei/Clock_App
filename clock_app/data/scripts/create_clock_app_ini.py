# pylint: disable=line-too-long,unused-import
"""
Create clock_app.ini from default options when the file does not exist.
Output format matches widget_var.option_name keys and [-C-]/[-S-] section headers.
"""

from __future__ import annotations

import os
from typing import Any

from ..defaults.default_options import DefaultOptions

_APP_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CLOCK_APP_INI_PATH: str = os.path.join(_APP_ROOT, "config", "clock_app.ini")


def _value_to_ini(value: Any) -> str:
    """Convert an option value to a string for INI."""
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    if isinstance(value, bool):
        return "True" if value else "False"
    return str(value)


# Section names (ConfigParser-safe: no ']' in name) and (widget_var, option_name) pairs.
# Categories: -C- App Info. Sections: -S- General. Options: widget_var.option_name.
_INI_LAYOUT: tuple[tuple[str, tuple[tuple[str, str], ...]], ...] = (
    ("-C- App Info", (
        ("C", "app_info_comment"), ("L", "app_name"), ("L", "app_version"),
        ("L", "app_version_type"), ("L", "app_description"), ("L", "app_author"),
        ("L", "app_author_github_username"), ("L", "app_github_url"),
        ("L", "app_license"), ("L", "app_license_filename"), ("L", "app_license_url"),
        ("L", "app_steam_id"), ("C", "steam_id_comment"),
    )),
    ("-C- App Settings", ()),
    ("-S- General", (
        ("C", "supported_languages"), ("D", "app_language"),
    )),
    ("-S- Display", (
        ("C", "supported_themes"), ("T", "app_theme"),
        ("C", "supported_timezones"), ("D", "app_timezone"),
        ("C", "supported_time_separators"), ("D", "app_time_separator"),
        ("C", "supported_date_separators"), ("D", "app_date_separator"),
        ("C", "app_time_comment"), ("T", "app_time_12_hour_format"),
        ("C", "supported_date_formats"), ("E", "app_date_format"),
    )),
    ("-S- Behavior", (
        ("C", "supported_clock_colors"), ("D", "app_clock_color"),
        ("C", "supported_clock_fonts"), ("D", "app_clock_font"),
        ("C", "supported_clock_font_sizes"), ("N", "app_clock_font_size"),
    )),
    ("-S- Notifications", (
        ("C", "supported_notification_options"), ("T", "app_notification_option"),
        ("C", "supported_notification_types"), ("D", "app_notification_type"),
    )),
    ("-S- Updates", (
        ("C", "supported_update_options"), ("D", "app_update_option"),
        ("C", "supported_update_channels"), ("D", "app_update_channel"),
        ("C", "supported_update_check_frequencies"), ("D", "app_update_check_frequency"),
        ("C", "update_check_time_comment"), ("L", "app_update_check_time"),
        ("C", "supported_update_sources"), ("D", "app_update_source"),
        ("C", "update_comment"),
    )),
)


class CreateClockAppIni:
    """
    Creates clock_app.ini from default options when the file does not exist.
    Output matches the exact format of the reference clock_app.ini.
    """

    def __init__(self) -> None:
        self.default_options = DefaultOptions()
        self.create_clock_app_ini()

    def create_clock_app_ini(self) -> None:
        """
        Create clock_app.ini from default options if it does not exist.
        Uses widget_var.option_name keys and [-C-]/[-S-] section headers.
        """
        if os.path.exists(CLOCK_APP_INI_PATH):
            return

        wvl = self.default_options.widget_variables_list
        lines: list[str] = []

        for i, (section_name, key_pairs) in enumerate(_INI_LAYOUT):
            if i > 0:
                lines.append("")
            lines.append(f"[{section_name}]")
            for wv, opt in key_pairs:
                if opt in wvl.get(wv, {}):
                    val = wvl[wv][opt]
                    lines.append(f"{wv}.{opt} = {_value_to_ini(val)}")

        content = "\n".join(lines)
        if content and not content.endswith("\n"):
            content += "\n"
        with open(CLOCK_APP_INI_PATH, "w", encoding="utf-8") as f:
            f.write(content)
