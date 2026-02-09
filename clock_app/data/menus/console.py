# pylint: disable=line-too-long,protected-access,unused-argument,attribute-defined-outside-init
# type: ignore[return-value]
"""
Console menu for Clock App. Toggle with ~ or ` key.
Supports commands: clock.{element}.drag&drop, clock.analog_animation, etc.
"""

from __future__ import annotations

import re
import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ...imports import ClockApp

from ...assets.lib.lang.translator import t


COMMANDS_LIST = """Available commands:
  list_commands
    Show this list of commands

  clock.{element}.drag&drop = true|false
    Enable/disable drag for face, hour_hand, minute_hand, second_hand

  clock.analog_animation = true|false
    Toggle analog clock hand animation

  clock.{element}.resize = true|false
    Toggle resize mode; when on, use =/+ to increase, -/_ to decrease size

  clock.{element}.scale = value
    Set scale directly (1.0 = default)

  clock.{element}.rotate = degrees
    Add rotation offset (degrees)

  clock.{element}.pivot = center|bottom|x,y
    Set hand pivot: center, bottom, or x,y ratios (0-1)

  Elements: face, hour_hand, minute_hand, second_hand
  (Aliases: analog_clock, analog_clock_hour_hand, etc.)"""


ELEMENT_ALIASES: dict[str, str] = {
    "face": "face",
    "analog_clock": "face",
    "hour_hand": "hour",
    "analog_clock_hour_hand": "hour",
    "minute_hand": "minute",
    "analog_clock_minute_hand": "minute",
    "second_hand": "second",
    "analog_clock_second_hand": "second",
}


def _normalize_element(name: str) -> str | None:
    """Map user input to internal element key."""
    key = name.strip().lower().replace(" ", "_")
    return ELEMENT_ALIASES.get(key)


class Console(ttk.Frame):
    """Console panel for entering commands. Toggle with ~ or `."""

    def __init__(self, parent: "ClockApp", *args: Any, **kwargs: Any) -> None:
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self._build_ui()

    def _theme_colors(self) -> tuple[str, str]:
        """Current theme (bg, fg). Uses parent.get_theme_colors() if available."""
        if hasattr(self.parent, "get_theme_colors"):
            return self.parent.get_theme_colors()
        return "#f0f0f0", "#000000"

    def _build_ui(self) -> None:
        """Build console input area."""
        self.grid_columnconfigure(0, weight=1)
        bg, fg = self._theme_colors()
        self._output = tk.Text(
            self, height=4, wrap=tk.WORD, state=tk.DISABLED,
            font=("Consolas", 9), bg=bg, fg=fg,
            insertbackground=fg,
        )
        self._output.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.entry = ttk.Entry(self, font=("Consolas", 10))
        self.entry.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 5))
        self._history: list[str] = []
        self._history_index = -1
        self.entry.bind("<Return>", self._on_enter)
        self.entry.bind("<Escape>", self._on_escape)
        self.entry.bind("<Up>", self._on_history_up)
        self.entry.bind("<Down>", self._on_history_down)

    def refresh_theme_colors(self) -> None:
        """Apply current app theme colors (bg/fg only)."""
        bg, fg = self._theme_colors()
        self._output.configure(bg=bg, fg=fg, insertbackground=fg)

    def _on_escape(self, _event: tk.Event) -> None:
        """Escape: collapse if expanded, close if collapsed."""
        if self.parent._console_expanded:
            self.parent._console_expanded = False
            self.parent.grid_rowconfigure(1, weight=0)
            self.set_collapsed(True)
        else:
            self.parent._console_visible = False
            self.parent._console_expanded = False
            self.parent.console.grid_forget()

    def set_collapsed(self, collapsed: bool) -> None:
        """Show collapsed (entry only) or expanded (output + entry)."""
        if collapsed:
            self._output.grid_remove()
            self.grid_rowconfigure(0, weight=0)
        else:
            self._output.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
            self.grid_rowconfigure(0, weight=1)

    def _log(self, msg: str) -> None:
        """Append to console output."""
        self._output.config(state=tk.NORMAL)
        self._output.insert(tk.END, msg + "\n")
        self._output.see(tk.END)
        self._output.config(state=tk.DISABLED)

    def _on_history_up(self, event: tk.Event) -> None:
        """Cycle to previous command in history."""
        if not self._history:
            return
        if self._history_index < len(self._history) - 1:
            self._history_index += 1
            self.entry.delete(0, tk.END)
            self.entry.insert(0, self._history[-(1 + self._history_index)])
        return "break"

    def _on_history_down(self, event: tk.Event) -> None:
        """Cycle to next command in history."""
        if not self._history:
            return
        if self._history_index > 0:
            self._history_index -= 1
            self.entry.delete(0, tk.END)
            self.entry.insert(0, self._history[-(1 + self._history_index)])
        else:
            self._history_index = -1
            self.entry.delete(0, tk.END)
        return "break"

    def _on_enter(self, event: tk.Event) -> None:
        """Execute command on Enter, or load history item if browsing."""
        cmd = self.entry.get().strip()
        if self._history_index >= 0:
            self.entry.delete(0, tk.END)
            self.entry.insert(0, self._history[-(1 + self._history_index)])
            self._history_index = -1
            return "break"
        self.entry.delete(0, tk.END)
        self._history_index = -1
        if not cmd:
            return
        self._history.append(cmd)
        self._log(f"> {cmd}")
        result = self._execute(cmd)
        if result is not None:
            self._log(str(result))

    def _execute(self, cmd: str) -> str | None:
        """Parse and execute command. Returns message or None."""
        cmd = cmd.strip()
        if cmd.lower() == "list_commands":
            return t("console.commands_list")
        # clock.{element}.drag&drop = true|false
        m = re.match(
            r"clock\.([^.]+)\.drag\s*&\s*drop\s*=\s*(true|false)",
            cmd, re.IGNORECASE
        )
        if m:
            elem = _normalize_element(m.group(1))
            if elem and self.parent.clock:
                val = m.group(2).lower() == "true"
                self.parent.clock.set_drag_drop(elem, val)
                return f"clock.{elem}.drag&drop = {val}"
            return t("console.unknown_element", m.group(1))

        # clock.analog_animation = true|false
        m = re.match(r"clock\.analog_animation\s*=\s*(true|false)",
                     cmd, re.IGNORECASE)
        if m:
            if self.parent.clock:
                val = m.group(1).lower() == "true"
                self.parent.clock.set_analog_animation(val)
                return f"clock.analog_animation = {val}"
            return t("console.clock_not_ready")

        # clock.{element}.resize = true|false (toggle resize mode with =/+ and -/_)
        m = re.match(
            r"clock\.([^.]+)\.resize\s*=\s*(true|false)",
            cmd, re.IGNORECASE
        )
        if m:
            elem = _normalize_element(m.group(1))
            if elem and self.parent.clock:
                val = m.group(2).lower() == "true"
                self.parent.clock.set_resize_mode(elem, val)
                return f"clock.{elem}.resize = {val} (use =/+ to increase, -/_ to decrease)"
            return t("console.unknown_element", m.group(1))

        # clock.{element}.scale = value
        m = re.match(
            r"clock\.([^.]+)\.scale\s*=\s*([\d.]+)",
            cmd, re.IGNORECASE
        )
        if m:
            elem = _normalize_element(m.group(1))
            if elem and self.parent.clock:
                try:
                    val = float(m.group(2))
                    self.parent.clock.set_element_scale(elem, val)
                    return f"clock.{elem}.scale = {val}"
                except ValueError:
                    return t("console.invalid_scale")
            return t("console.unknown_element", m.group(1))

        # clock.{element}.rotate = degrees
        m = re.match(
            r"clock\.([^.]+)\.rotate\s*=\s*([\d.-]+)", cmd, re.IGNORECASE)
        if m:
            elem = _normalize_element(m.group(1))
            if elem and self.parent.clock:
                try:
                    val = float(m.group(2))
                    self.parent.clock.set_element_rotation(elem, val)
                    return f"clock.{elem}.rotate = {val}°"
                except ValueError:
                    return t("console.invalid_rotation")
            return t("console.unknown_element", m.group(1))

        # clock.{element}.pivot = center|bottom|x,y
        m = re.match(
            r"clock\.([^.]+)\.pivot\s*=\s*(center|bottom|[\d.]+\s*,\s*[\d.]+)",
            cmd, re.IGNORECASE
        )
        if m:
            elem = _normalize_element(m.group(1))
            if elem and self.parent.clock:
                p = m.group(2).strip().lower()
                if p == "center":
                    self.parent.clock.set_hand_pivot(elem, "center")
                    return f"clock.{elem}.pivot = center"
                if p == "bottom":
                    self.parent.clock.set_hand_pivot(elem, "bottom")
                    return f"clock.{elem}.pivot = bottom"
                parts = [x.strip() for x in p.split(",")]
                if len(parts) == 2:
                    try:
                        xr, yr = float(parts[0]), float(parts[1])
                        self.parent.clock.set_hand_pivot(elem, (xr, yr))
                        return f"clock.{elem}.pivot = ({xr}, {yr})"
                    except ValueError:
                        pass
            return t("console.invalid_pivot", m.group(1))

        return t("console.unknown_command", cmd)
