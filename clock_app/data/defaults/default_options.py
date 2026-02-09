# pylint: disable=line-too-long,unused-import
"""
This is the default options module for the clock app.
It will contain the default options for the clock app.
"""

from __future__ import annotations

import configparser
from typing import Any


class DefaultOptions(configparser.ConfigParser):
    """
    This is the default options class for the clock app.
    It will contain the default options for the clock app.
    """

    def __init__(self):
        super().__init__()
        self.config = configparser.ConfigParser()
        # Widget type names; options are added per widget in option_format below.
        self.widget_variables_list: dict[str, dict[str, Any]] = {
            "-C-": {"widget_type": "Category"},
            "-S-": {"widget_type": "Section"},
            "L": {"widget_type": "Label"},
            "T": {"widget_type": "ToggleButton"},
            "S": {"widget_type": "Slider"},
            "D": {"widget_type": "Dropdown"},
            "N": {"widget_type": "NumberPicker"},
            "B": {"widget_type": "Button"},
            "E": {"widget_type": "Entry"},
            # Comment: used to display variables that end with _comment.
            "C": {"widget_type": "Comment"}
        }
        self.widget_variables_list_comment = "Widget Variables Do Not Change"
        self.widget_variables_category = self.widget_variables_list["-C-"]["widget_type"]
        self.widget_variables_section = self.widget_variables_list["-S-"]["widget_type"]
        self.widget_variables_label = self.widget_variables_list["L"]["widget_type"]
        self.widget_variables_toggle_button = self.widget_variables_list["T"]["widget_type"]
        self.widget_variables_slider = self.widget_variables_list["S"]["widget_type"]
        self.widget_variables_dropdown = self.widget_variables_list["D"]["widget_type"]
        self.widget_variables_number_picker = self.widget_variables_list["N"]["widget_type"]
        self.widget_variables_button = self.widget_variables_list["B"]["widget_type"]
        self.widget_variables_entry = self.widget_variables_list["E"]["widget_type"]
        self.widget_variables_comment = self.widget_variables_list["C"]["widget_type"]
        self.option_format = (
            "self.widget_variables_list['{widget_variable}']['{option_name}'] = "
            "'{option_value}'"
        )
        self.widget_variables_list["-C-"]["option_categories"] = [
            "App Info", "App Settings"
        ]
        self.widget_variables_list["-S-"]["option_sections"] = [
            "General", "Display", "Behavior", "Notifications", "Updates"
        ]
        self.option_categories = self.widget_variables_list["-C-"]["option_categories"]
        self.option_sections = self.widget_variables_list["-S-"]["option_sections"]

        # --- App Info (option_format: widget_variable, option_name, value) ---
        self.widget_variables_list["C"]["app_info_comment"] = "App Information Do Not Change"
        self.widget_variables_list["L"]["app_name"] = "Clock App"
        self.widget_variables_list["L"]["app_version"] = "0.0.01"
        self.widget_variables_list["L"]["app_version_type"] = "Pre-Alpha"
        self.widget_variables_list["L"]["app_description"] = (
            "A simple clock app that displays the current time and date."
        )
        self.widget_variables_list["L"]["app_author"] = "Dramora9879"
        self.widget_variables_list["L"]["app_author_github_username"] = "DramoraFramei"
        self.widget_variables_list["L"]["app_github_url"] = "https://github.com/DramoraFramei/Clock-App"
        self.widget_variables_list["L"]["app_license"] = "All Rights Reserved"
        self.widget_variables_list["L"]["app_license_filename"] = "LICENSE"
        self.widget_variables_list["L"]["app_license_url"] = (
            "https://github.com/DramoraFramei/Clock-App/blob/main/LICENSE"
        )
        self.widget_variables_list["L"]["app_steam_id"] = "${steam_id}"
        self.widget_variables_list["C"]["steam_id_comment"] = "Steam ID is pulled from a separate file"

        # --- General ---
        self.widget_variables_list["C"]["supported_languages"] = [
            "English",
            "Arabic",
            "French",
            "German",
            "Italian",
            "Portuguese",
            "Russian",
            "Spanish",
            "Turkish"
        ]
        self.widget_variables_list["D"]["app_language"] = "English"

        # --- Display ---
        self.widget_variables_list["C"]["supported_themes"] = ["Light", "Dark"]
        self.widget_variables_list["T"]["app_theme"] = "Light"
        self.widget_variables_list["C"]["supported_timezones"] = [
            "UTC", "GMT", "EST", "CST", "MST", "PST", "etc."
        ]
        self.widget_variables_list["D"]["app_timezone"] = "UTC"
        self.widget_variables_list["C"]["supported_time_separators"] = [
            ":", "-", ".", ":"]
        self.widget_variables_list["D"]["app_time_separator"] = ":"
        self.widget_variables_list["C"]["supported_date_separators"] = [
            "/", "-", ".", ":"]
        self.widget_variables_list["D"]["app_date_separator"] = "/"
        self.widget_variables_list["C"]["app_time_comment"] = (
            "If True, the time will be displayed in 12 hour format, "
            "otherwise in 24 hour format"
        )
        self.widget_variables_list["T"]["app_time_12_hour_format"] = False
        self.widget_variables_list["E"]["app_date_format"] = (
            "Choose a date format from the supported date formats"
        )
        self.widget_variables_list["C"]["supported_date_formats"] = [
            "'dd' {self.app_date_separator} 'mm' {self.app_date_separator} 'yyyy'",
            "'mm' {self.app_date_separator} 'dd' {self.app_date_separator} 'yyyy'",
            "'yyyy' {self.app_date_separator} 'mm' {self.app_date_separator} 'dd'",
        ]

        # --- Behavior ---
        self.widget_variables_list["C"]["supported_clock_animations"] = [
            "On", "Off"]
        self.widget_variables_list["T"]["app_clock_animation"] = "On"
        self.widget_variables_list["C"]["supported_clock_types"] = [
            "Analog", "Digital"]
        self.widget_variables_list["D"]["app_clock_type"] = "Analog"
        self.widget_variables_list["C"]["supported_clock_colors"] = [
            "Red", "Green", "Blue", "Yellow", "Purple", "Orange",
            "Pink", "Brown", "Gray", "Black", "White"
        ]
        self.widget_variables_list["D"]["app_clock_color"] = "Black"
        self.widget_variables_list["C"]["supported_clock_fonts"] = [
            "Arial", "Times New Roman", "Courier New", "Verdana",
        ]
        self.widget_variables_list["D"]["app_clock_font"] = "Arial"
        self.widget_variables_list["C"]["supported_clock_font_sizes"] = (
            "Choose a font size (If you are editing the ini file, you will need to input "
            "the font size instead of using the Number Picker. Minimum font size is 8 "
            "and maximum font size is 30)"
        )
        self.widget_variables_list["N"]["app_clock_font_size"] = 12

        # --- Notifications ---
        self.widget_variables_list["C"]["supported_notification_options"] = [
            "On", "Off"]
        self.widget_variables_list["T"]["app_notification_option"] = "On"
        self.widget_variables_list["C"]["supported_notification_types"] = [
            "Vibrate", "Sound", "Popup"
        ]
        self.widget_variables_list["D"]["app_notification_type"] = "Vibrate"

        # --- Updates ---
        self.widget_variables_list["C"]["supported_update_options"] = [
            "Automatic", "Manual"]
        self.widget_variables_list["D"]["app_update_option"] = "Automatic"
        self.widget_variables_list["C"]["supported_update_channels"] = [
            "Stable", "Beta", "Dev"]
        self.widget_variables_list["D"]["app_update_channel"] = "Stable"
        self.widget_variables_list["C"]["supported_update_check_frequencies"] = [
            "Daily", "Weekly", "Monthly"
        ]
        self.widget_variables_list["D"]["app_update_check_frequency"] = "Daily"
        self.widget_variables_list["C"]["update_check_time_comment"] = (
            "The time at which the update check will be performed (If you are editing "
            "the ini file, you will need to input the time instead of using the Number "
            "Picker. Minimum time is 00:00 if using 24 hour format, 12:00 AM if using "
            "12 hour format and maximum time is 24:00 if using 24 hour format, 12:00 PM "
            "if using 12 hour format)"
        )
        self.widget_variables_list["L"]["app_update_check_time"] = (
            "Input Time in `${time_format}` format"
        )
        self.widget_variables_list["C"]["supported_update_sources"] = [
            "GitHub", "Stream", "Local"]
        self.widget_variables_list["D"]["app_update_source"] = "GitHub"
        self.widget_variables_list["C"]["update_comment"] = "Update Information Do Not Change"

        # Build category dicts and options_dictionary from widget_variables_list.
        def _gather_options(*key_pairs):
            """(widget_var, option_name) -> category dict."""
            out = {}
            for wv, opt in key_pairs:
                if opt in self.widget_variables_list.get(wv, {}):
                    out[opt] = self.widget_variables_list[wv][opt]
            return out

        self.app_info_category = _gather_options(
            ("C", "app_info_comment"), ("L", "app_name"), ("L", "app_version"),
            ("L", "app_version_type"), ("L", "app_description"), ("L", "app_author"),
            ("L", "app_author_github_username"), ("L", "app_github_url"),
            ("L", "app_license"), ("L",
                                   "app_license_filename"), ("L", "app_license_url"),
            ("L", "app_steam_id"), ("C", "steam_id_comment"),
        )
        self.general_category = _gather_options(
            ("C", "supported_languages"), ("D", "app_language"),
        )
        self.display_category = _gather_options(
            ("C", "supported_themes"), ("T", "app_theme"),
            ("C", "supported_timezones"), ("D", "app_timezone"),
            ("C", "supported_time_separators"), ("D", "app_time_separator"),
            ("C", "supported_date_separators"), ("D", "app_date_separator"),
            ("C", "app_time_comment"), ("T", "app_time_12_hour_format"),
            ("E", "app_date_format"), ("C", "supported_date_formats"),
        )
        self.behavior_category = _gather_options(
            ("C", "supported_clock_animations"), ("T", "app_clock_animation"),
            ("C", "supported_clock_types"), ("D", "app_clock_type"),
            ("C", "supported_clock_colors"), ("D", "app_clock_color"),
            ("C", "supported_clock_fonts"), ("D", "app_clock_font"),
            ("C", "supported_clock_font_sizes"), ("N", "app_clock_font_size"),
        )
        self.notifications_category = _gather_options(
            ("C", "supported_notification_options"), ("T", "app_notification_option"),
            ("C", "supported_notification_types"), ("D", "app_notification_type"),
        )
        self.updates_category = _gather_options(
            ("C", "supported_update_options"), ("D", "app_update_option"),
            ("C", "supported_update_channels"), ("D", "app_update_channel"),
            ("C", "supported_update_check_frequencies"), ("D",
                                                          "app_update_check_frequency"),
            ("C", "update_check_time_comment"), ("L", "app_update_check_time"),
            ("C", "supported_update_sources"), ("D", "app_update_source"),
            ("C", "update_comment"),
        )
        self.options_dictionary = [
            self.app_info_category,
            self.general_category,
            self.display_category,
            self.behavior_category,
            self.notifications_category,
            self.updates_category,
        ]
