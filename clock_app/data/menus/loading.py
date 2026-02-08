# pylint: disable=line-too-long
"""
Loading screen menu for Clock App.
Shows animated progress bar as the app loads.
"""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from typing import Any, TYPE_CHECKING

from ...assets.lib.lang.translator import t

if TYPE_CHECKING:
    from ...imports import ClockApp


class Loading(ttk.Frame):
    """
    Loading screen with black background and animated blue/green progress bar.
    """

    BAR_WIDTH = 300
    BAR_HEIGHT = 24

    def __init__(self, parent: "ClockApp", *args: Any, **kwargs: Any) -> None:
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self._progress_pct: float = 0.0
        self._target_pct: float = 0.0
        self._animate_job: str | None = None
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._build_ui()

    def _build_ui(self) -> None:
        """Build loading screen UI."""
        self._container = tk.Frame(self, bg="black")
        self._container.grid(row=0, column=0, sticky="nsew")
        self._container.grid_rowconfigure(0, weight=1)
        self._container.grid_columnconfigure(0, weight=1)
        self._container.grid_rowconfigure(2, weight=1)
        self._container.grid_columnconfigure(0, weight=1)

        self._inner = tk.Frame(self._container, bg="black")
        self._inner.grid(row=0, column=0)
        self._inner.grid_rowconfigure(2, weight=1)
        self._inner.grid_columnconfigure(0, weight=1)

        self._loading_label = tk.Label(
            self._inner,
            text=t("loading.text"),
            font=("", 14),
            fg="white",
            bg="black",
        )
        self._loading_label.grid(row=0, column=0, pady=(40, 20))

        self._progress_canvas = tk.Canvas(
            self._inner,
            width=self.BAR_WIDTH,
            height=self.BAR_HEIGHT,
            bg="black",
            highlightthickness=0,
        )
        self._progress_canvas.grid(row=1, column=0, pady=10)

        self._progress_bg = self._progress_canvas.create_rectangle(
            0, 0, self.BAR_WIDTH, self.BAR_HEIGHT,
            fill="blue", outline="blue"
        )
        self._progress_fill = self._progress_canvas.create_rectangle(
            0, 0, 0, self.BAR_HEIGHT,
            fill="green", outline="green"
        )

    def refresh_translations(self) -> None:
        """Update labels with current language."""
        self._loading_label.config(text=t("loading.text"))

    def set_message(self, text: str) -> None:
        """Set the loading label text (e.g. for 'Translating...')."""
        self._loading_label.config(text=text)

    def set_progress(self, target_pct: float) -> None:
        """
        Set target progress (0-100). Animates the green bar filling the blue bar.
        """
        self._target_pct = min(100.0, max(0.0, target_pct))
        self._animate_progress()

    def _animate_progress(self) -> None:
        """Animate progress bar toward target."""
        if self._animate_job:
            self.after_cancel(self._animate_job)
            self._animate_job = None

        step = 3.0
        if self._progress_pct < self._target_pct:
            self._progress_pct = min(
                self._progress_pct + step,
                self._target_pct
            )
        else:
            self._progress_pct = self._target_pct

        fill_width = self.BAR_WIDTH * self._progress_pct / 100
        self._progress_canvas.coords(
            self._progress_fill,
            0, 0, fill_width, self.BAR_HEIGHT
        )
        self.update_idletasks()

        if self._progress_pct < self._target_pct:
            self._animate_job = self.after(20, self._animate_progress)
