# pylint: disable=line-too-long,unused-import
"""
Main Menu for Clock App.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ...imports import ClockApp

from ...assets.lib.lang.translator import t


class MainMenu(ttk.Frame):
    """
    Main Menu for Clock App.
    """

    def __init__(self, parent: "ClockApp", *args: Any, **kwargs: Any) -> None:
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.label = ttk.Label(self, text=t("main_menu.label"))
        self.label.grid(row=1, column=0, pady=10)
        self.clock_button = ttk.Button(
            self, text=t("main_menu.clock"), command=self.open_clock)
        self.clock_button.grid(row=2, column=0, pady=5)
        self.options_button = ttk.Button(
            self, text=t("main_menu.options"), command=self.open_options)
        self.options_button.grid(row=3, column=0, pady=5)
        self.exit_button = ttk.Button(
            self, text=t("main_menu.exit"), command=self.parent.quit)
        self.exit_button.grid(row=4, column=0, pady=5)

    def refresh_translations(self) -> None:
        """Update labels and buttons with current language."""
        self.label.config(text=t("main_menu.label"))
        self.clock_button.config(text=t("main_menu.clock"))
        self.options_button.config(text=t("main_menu.options"))
        self.exit_button.config(text=t("main_menu.exit"))

    def open_clock(self) -> None:
        """
        Open the clock window.
        """
        self.parent.switch_menu("clock")

    def open_options(self) -> None:
        """
        Open the options window by calling the switch_menu method.
        """
        self.parent.switch_menu("options")
