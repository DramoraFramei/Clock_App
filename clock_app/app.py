# pylint: disable=line-too-long,unused-import,too-many-instance-attributes,import-outside-toplevel,protected-access
# type: ignore[arg-type]
"""
This is a clock app.
It will display the current time and date.
"""

import configparser
import os
import tkinter as tk
from tkinter import ttk

from .imports import Clock, Console, Loading, MainMenu, Options
from .assets.lib.lang.translator import set_language, t


def _init_translations() -> None:
    """Load language from config, or default to English."""
    from .imports import CLOCK_APP_INI_PATH
    lang = "English"
    if os.path.exists(CLOCK_APP_INI_PATH):
        cfg = configparser.ConfigParser()
        cfg.optionxform = str
        cfg.read(CLOCK_APP_INI_PATH, encoding="utf-8")
        for sect in ["-S- General"]:
            if cfg.has_section(sect) and cfg.has_option(sect, "D.app_language"):
                lang = cfg.get(sect, "D.app_language").strip() or lang
                break
    set_language(lang)


class ClockApp(tk.Tk):
    """
    This is a clock app.
    It will display the current time and date.
    """

    def __init__(self):
        super().__init__()
        _init_translations()
        self.title(t("app.title"))
        self.geometry("400x300")
        self.resizable(True, True)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.time_format = "%H:%M:%S"
        self.date_format = "%d/%m/%Y"
        self.time_label_text = "00:00:00"
        self.date_label_text = "00/00/0000"
        self.options: Options | None = None
        self.main_menu: MainMenu | None = None
        self.clock: Clock | None = None
        self.console: Console | None = None
        self._console_visible = False
        self._console_expanded = False
        self.current_menu: str = ""
        self.loading = Loading(self)
        self.loading.grid(row=0, column=0, sticky="nsew")
        self.current_menu = "loading"
        self.after(50, self._load_step_1)

    def _load_step_1(self) -> None:
        """Step 1: Create ini if needed."""
        from .imports import create_clock_app_ini, CLOCK_APP_INI_PATH

        if not os.path.exists(CLOCK_APP_INI_PATH):
            create_clock_app_ini()
        self.loading.set_progress(10)
        self.after(50, self._load_step_2)

    def _load_step_2(self) -> None:
        """Step 2: Load Options."""
        self.options = Options(self)
        self.loading.set_progress(40)
        self.after(50, self._load_step_3)

    def _load_step_3(self) -> None:
        """Step 3: Load MainMenu and Clock."""
        self.main_menu = MainMenu(self)
        self.clock = Clock(self)
        self.loading.set_progress(70)
        self.after(50, self._load_step_4)

    def _load_step_4(self) -> None:
        """Step 4: Complete and switch to Main Menu."""
        self.loading.set_progress(100)
        self.after(150, self._switch_to_main)

    def _switch_to_main(self) -> None:
        """Hide loading screen and show Main Menu."""
        self.loading.grid_forget()
        self.switch_menu("main")
        self._setup_console()

    def _setup_console(self) -> None:
        """Create console and bind ~ / ` to toggle."""
        self.console = Console(self)
        for key in ("<KeyPress-asciitilde>", "<KeyPress-quoteleft>"):
            self.bind_all(key, self._on_console_key)
        self.bind_all("<Button-1>", self._on_console_click_out)
        for key in ("<KeyPress-equal>", "<KeyPress-plus>", "<KeyPress-minus>",
                    "<KeyPress-underscore>"):
            self.bind_all(key, self._on_resize_key)

    def _is_console_or_descendant(self, widget: tk.Widget) -> bool:
        """Return True if widget is the console or a child of it."""
        w = widget
        while w:
            if w == self.console:
                return True
            try:
                parent = w.nametowidget(w.winfo_parent())
            except (KeyError, tk.TclError):
                break
            if parent == w:
                break
            w = parent
        return False

    def _on_console_click_out(self, event: tk.Event) -> None:
        """When console is visible, clicking outside it moves focus away from entry."""
        if not self._console_visible or not self.console:
            return
        if not self._is_console_or_descendant(event.widget):
            self.focus_set()

    def _on_console_key(self, event: tk.Event) -> None:
        """Toggle console on ~ or ` (only when focus is not in console entry)."""
        if self.console and self._is_console_or_descendant(event.widget):
            return
        self.toggle_console()

    def _on_resize_key(self, event: tk.Event) -> str | None:
        """Handle =/+ (increase) and -/_ (decrease) for resize mode."""
        if self.console and self._is_console_or_descendant(event.widget):
            return None
        if not self.clock or self.clock._resize_mode_element is None:
            return None
        keysym = event.keysym
        if keysym in ("equal", "plus") and self.clock.adjust_resize_scale(0.1):
            return "break"
        if keysym in ("minus", "underscore") and self.clock.adjust_resize_scale(-0.1):
            return "break"
        return None

    def toggle_console(self) -> None:
        """Cycle: closed -> collapsed -> expanded -> closed."""
        if self.console is None:
            return
        if not self._console_visible:
            self._console_visible = True
            self._console_expanded = False
            self.console.grid(row=1, column=0, sticky="nsew")
            self.grid_rowconfigure(1, weight=0)
            self.console.set_collapsed(True)
            self.console.entry.focus_set()
        elif not self._console_expanded:
            self._console_expanded = True
            self.console.set_collapsed(False)
            self.grid_rowconfigure(1, weight=1)
        else:
            self._console_visible = False
            self._console_expanded = False
            self.grid_rowconfigure(1, weight=0)
            self.console.grid_forget()

    def refresh_translations(self) -> None:
        """Reload translated text across the app after language change."""
        self.title(t("app.title"))
        if self.loading and hasattr(self.loading, "refresh_translations"):
            self.loading.refresh_translations()
        if self.main_menu and hasattr(self.main_menu, "refresh_translations"):
            self.main_menu.refresh_translations()
        if self.options and hasattr(self.options, "refresh_translations"):
            self.options.refresh_translations()
        if self.clock and hasattr(self.clock, "refresh_translations"):
            self.clock.refresh_translations()

    def switch_menu(self, menu: str) -> None:
        """
        Switch to the specified menu.
        """
        if self.loading is not None:
            self.loading.grid_forget()
        if self.main_menu is not None:
            self.main_menu.grid_forget()
        if self.options is not None:
            self.options.grid_forget()
        if self.clock is not None:
            self.clock.grid_forget()
        self.current_menu = menu
        if menu == "main":
            assert self.main_menu is not None
            self.main_menu.grid(row=0, column=0, sticky="nsew")
        elif menu == "options":
            assert self.options is not None
            self.options.grid(row=0, column=0, sticky="nsew")
        elif menu == "clock":
            assert self.clock is not None
            self.clock.grid(row=0, column=0, sticky="nsew")
        else:
            raise ValueError(f"Invalid menu: {menu}")

    def quit_app(self) -> None:
        """
        Quit the application.
        """
        super().quit()
        self.destroy()

    def run(self) -> None:
        """
        Run the application.
        """
        self.mainloop()


def main() -> None:
    """
    Main function to run the application.
    """
    app = ClockApp()
    app.run()


if __name__ == "__main__":
    main()
