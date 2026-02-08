# pylint: disable=line-too-long,unused-import,import-outside-toplevel
# type: ignore[union-attr]
"""
Options module for the clock app.
Dynamically loads configurations from clock_app.ini and displays them
using tkinter widgets based on the widget type (C, L, T, D, E, N).
"""

from __future__ import annotations

import configparser
import os
import threading
import tkinter as tk
from tkinter import ttk
from typing import Any

from ...assets.lib.lang.translator import t


def _parse_option_key(key: str) -> tuple[str, str] | None:
    """Parse 'widget_var.option_name' into (widget_var, option_name)."""
    if "." in key:
        wv, name = key.split(".", 1)
        return (wv.strip(), name.strip())
    return None


# Options that are disabled (not shown in UI, not written to new ini)
_DISABLED_OPTIONS: frozenset[str] = frozenset({
    "app_animation_option", "app_clock_type",
})

_SECTION_TO_KEY: dict[str, str] = {
    "-C- App Info": "ini.section.app_info",
    "-C- App Settings": "ini.section.app_settings",
    "-S- General": "ini.section.general",
    "-S- Display": "ini.section.display",
    "-S- Behavior": "ini.section.behavior",
    "-S- Notifications": "ini.section.notifications",
    "-S- Updates": "ini.section.updates",
}


def _get_supported_list(config: configparser.ConfigParser, section: str, option: str) -> list[str]:
    """Find C.supported_* option for a D.* option to get dropdown choices."""
    stem = option.replace("app_", "")
    if stem.endswith("_type"):
        expected_suffix = stem.replace("_type", "_types")
    elif stem.endswith("_option"):
        expected_suffix = stem.replace("_option", "_options")
    else:
        expected_suffix = stem + "s"
    target = f"supported_{expected_suffix}"
    for key in config.options(section):
        parsed = _parse_option_key(key)
        if parsed and parsed[0] == "C" and parsed[1] == target:
            val = config.get(section, key)
            return [x.strip() for x in val.split(",")]
    return []


class Options(ttk.Frame):
    """
    Options module that dynamically loads clock_app.ini and displays
    options with appropriate tkinter widgets.
    """

    def __init__(self, parent: tk.Misc) -> None:  # parent is ClockApp
        super().__init__(parent)
        from ...imports import create_clock_app_ini, CLOCK_APP_INI_PATH

        self.parent = parent
        self.config = configparser.ConfigParser()
        # Preserve option name case (C.app_name not c.app_name)
        self.config.optionxform = str
        if not os.path.exists(CLOCK_APP_INI_PATH):
            create_clock_app_ini()

        self.config.read(CLOCK_APP_INI_PATH, encoding="utf-8")
        self._ini_path = CLOCK_APP_INI_PATH
        self._widget_vars: dict[str, tk.Variable] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        """Build the options UI from loaded config."""
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.title_label = ttk.Label(
            self, text=t("options.title"), font=("", 14, "bold"))
        self.title_label.grid(row=0, column=0, pady=(10, 5), sticky="w")

        self._scroll_canvas = tk.Canvas(self, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self)
        self.scroll_frame = ttk.Frame(self._scroll_canvas)

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self._scroll_canvas.configure(
                scrollregion=self._scroll_canvas.bbox("all"))
        )
        self._scroll_canvas.create_window(
            (0, 0), window=self.scroll_frame, anchor="nw")
        self._scroll_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.configure(command=self._scroll_canvas.yview)

        self._scroll_canvas.grid(row=1, column=0, sticky="nsew")
        scrollbar.grid(row=1, column=1, sticky="ns")

        self._populate_options()
        self._scroll_canvas.bind("<MouseWheel>", self._on_mousewheel)
        self._scroll_canvas.bind(
            "<Button-4>", lambda e: self._on_mousewheel_linux(e, -3))
        self._scroll_canvas.bind(
            "<Button-5>", lambda e: self._on_mousewheel_linux(e, 3))
        self._bind_mousewheel()

        self.back_button = ttk.Button(
            self, text=t("common.back"),
            command=lambda: self.parent.switch_menu("main")
        )
        self.back_button.grid(row=2, column=0, pady=10)

    def _on_mousewheel(self, event: tk.Event) -> None:
        """Scroll the options canvas with mouse wheel (Windows/macOS)."""
        self._scroll_canvas.yview_scroll(
            int(-1 * (event.delta / 120)), "units")

    def _on_mousewheel_linux(
        self, _event: tk.Event, direction: int
    ) -> None:
        """Scroll the options canvas with mouse wheel (Linux Button-4/5)."""
        self._scroll_canvas.yview_scroll(direction, "units")

    def _bind_mousewheel(self, widget: tk.Widget | None = None) -> None:
        """Bind mouse wheel to widget and all descendants for scrolling."""
        w = widget if widget is not None else self.scroll_frame
        w.bind("<MouseWheel>", self._on_mousewheel)
        w.bind("<Button-4>", lambda e: self._on_mousewheel_linux(e, -3))
        w.bind("<Button-5>", lambda e: self._on_mousewheel_linux(e, 3))
        for child in w.winfo_children():
            self._bind_mousewheel(child)

    def refresh_translations(self) -> None:
        """Update labels, buttons, and rebuild option widgets with current language."""
        self.title_label.config(text=t("options.title"))
        self.back_button.config(text=t("common.back"))
        for child in self.scroll_frame.winfo_children():
            child.destroy()
        self._widget_vars.clear()
        self._populate_options()
        self._bind_mousewheel()

    def _populate_options(self) -> None:
        """Populate the scroll frame with options from each section."""
        row = 0
        section_order = [
            "-C- App Info", "-C- App Settings",
            "-S- General", "-S- Display", "-S- Behavior",
            "-S- Notifications", "-S- Updates"
        ]
        for section in section_order:
            if not self.config.has_section(section):
                continue
            sect_text = t(_SECTION_TO_KEY.get(section, section), section)
            sect_frame = ttk.LabelFrame(self.scroll_frame, text=sect_text)
            sect_frame.grid(row=row, column=0, sticky="ew", padx=10, pady=5)
            sect_frame.grid_columnconfigure(1, weight=1)
            srow = 0
            for key in self.config.options(section):
                parsed = _parse_option_key(key)
                if not parsed:
                    continue
                wv, opt_name = parsed
                if opt_name in _DISABLED_OPTIONS:
                    continue
                value = self.config.get(section, key)
                widget_row = self._add_option_widget(
                    sect_frame, srow, wv, opt_name, value, section)
                if widget_row is not None:
                    srow = widget_row + 1
            row += 1

    def _add_option_widget(
        self,
        parent: ttk.Frame | ttk.LabelFrame,
        row: int,
        widget_var: str,
        opt_name: str,
        value: str,
        section: str,
    ) -> int | None:
        """Add a widget for the option; returns next row or None if skipped."""
        var_key = f"{section}::{opt_name}"
        if widget_var == "C":
            comment_text = t(f"ini.comment.{opt_name}", value)
            ttk.Label(parent, text=comment_text, foreground="gray").grid(
                row=row, column=0, columnspan=2, sticky="w", padx=5, pady=2
            )
            return row + 1
        opt_label = t(f"ini.opt.{opt_name}",
                      opt_name.replace("_", " ").title())
        if widget_var == "L":
            ttk.Label(parent, text=opt_label).grid(
                row=row, column=0, sticky="w", padx=5, pady=2
            )
            ttk.Label(parent, text=value).grid(
                row=row, column=1, sticky="w", padx=5, pady=2)
            return row + 1
        if widget_var == "T":
            ttk.Label(parent, text=opt_label).grid(
                row=row, column=0, sticky="w", padx=5, pady=2
            )
            v = tk.BooleanVar(value=value.strip().lower()
                              in ("true", "1", "yes"))
            self._widget_vars[var_key] = v
            full_key = f"{widget_var}.{opt_name}"
            cb = ttk.Checkbutton(
                parent, variable=v,
                command=lambda s=section, k=full_key: self._save_option(
                    s, k, "True" if v.get() else "False")
            )
            cb.grid(row=row, column=1, sticky="w", padx=5, pady=2)
            return row + 1
        if widget_var == "D":
            ttk.Label(parent, text=opt_label).grid(
                row=row, column=0, sticky="w", padx=5, pady=2
            )
            choices_raw = [c.strip() for c in _get_supported_list(
                self.config, section, opt_name)]
            if not choices_raw:
                choices_raw = [value.strip()]
            choices_display = [t(f"ini.val.{c}", c) for c in choices_raw]
            current_display = t(
                f"ini.val.{value.strip()}", value.strip()) if value.strip() else value
            v = tk.StringVar(value=current_display)
            self._widget_vars[var_key] = v
            self._widget_vars[f"{var_key}::raw"] = choices_raw
            cb = ttk.Combobox(
                parent, textvariable=v, values=choices_display, state="readonly", width=30
            )
            cb.grid(row=row, column=1, sticky="w", padx=5, pady=2)
            full_key = f"{widget_var}.{opt_name}"

            def _on_dropdown_select(
                _e: tk.Event, s: str, k: str, vr: tk.StringVar, oname: str
            ) -> None:
                sel = vr.get()
                raw_choices = self._widget_vars.get(
                    f"{s}::{oname}::raw", [sel])
                raw_val = sel
                for rc in raw_choices:
                    if t(f"ini.val.{rc}", rc) == sel:
                        raw_val = rc
                        break
                self._save_option(s, k, raw_val)

            cb.bind(
                "<<ComboboxSelected>>",
                lambda e, s=section, k=full_key: _on_dropdown_select(
                    e, s, k, v, opt_name),
            )
            return row + 1
        if widget_var == "E":
            ttk.Label(parent, text=opt_label).grid(
                row=row, column=0, sticky="w", padx=5, pady=2
            )
            v = tk.StringVar(value=value)
            self._widget_vars[var_key] = v
            e = ttk.Entry(parent, textvariable=v, width=40)
            e.grid(row=row, column=1, sticky="ew", padx=5, pady=2)
            full_key = f"{widget_var}.{opt_name}"
            e.bind("<FocusOut>", lambda e, s=section,
                   k=full_key: self._save_option(s, k, v.get()))
            return row + 1
        if widget_var == "N":
            ttk.Label(parent, text=opt_label).grid(
                row=row, column=0, sticky="w", padx=5, pady=2
            )
            try:
                num_val = int(float(value))
            except (ValueError, TypeError):
                num_val = 0
            v = tk.StringVar(value=str(num_val))
            self._widget_vars[var_key] = v
            sp = ttk.Spinbox(parent, from_=0, to=999, textvariable=v, width=10)
            sp.grid(row=row, column=1, sticky="w", padx=5, pady=2)
            full_key = f"{widget_var}.{opt_name}"
            sp.bind("<FocusOut>", lambda e, s=section,
                    k=full_key: self._save_option(s, k, v.get()))
            return row + 1
        return None

    def _save_option(self, section: str, full_key: str, value: str) -> None:
        """Save an option value back to the INI file."""
        self.config.set(section, full_key, value)
        with open(self._ini_path, "w", encoding="utf-8") as f:
            self.config.write(f)
        if full_key == "D.app_language":
            self._on_language_changed(value)

    def _on_language_changed(self, lang_name: str) -> None:
        """Reload translations and refresh all UI when language changes."""
        from ...assets.lib.lang.translator import set_language
        from ..scripts.translate_ini_to_lang import run

        lang_name = lang_name.strip()
        set_language(lang_name)
        parent = getattr(self, "parent", None)
        if not parent or not hasattr(parent, "refresh_translations"):
            return

        # Show loading screen first so user sees feedback immediately
        self.grid_forget()
        parent.loading.grid(row=0, column=0, sticky="nsew")
        parent.loading.set_message(t("loading.translating", "Translating..."))
        parent.loading.set_progress(0)
        parent.update_idletasks()  # Force loading screen to render before thread starts

        def _on_progress(done: int, total: int) -> None:
            pct = 100.0 * done / total if total else 0
            parent.after(0, lambda p=pct: parent.loading.set_progress(p))

        def _worker() -> None:
            run(progress_callback=_on_progress)
            parent.after(0, lambda: self._on_translate_done(lang_name))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_translate_done(self, lang_name: str) -> None:
        """Called on main thread after translation completes."""
        from ...assets.lib.lang.translator import set_language

        set_language(lang_name)
        parent = getattr(self, "parent", None)
        if parent:
            parent.loading.grid_forget()
            parent.refresh_translations()
            parent.switch_menu("options")
