# pylint: disable=line-too-long,unused-import,import-outside-toplevel,too-many-instance-attributes,attribute-defined-outside-init,nested-min-max,no-member,too-many-locals
# type: ignore[attr-defined]
"""
Clock display for Clock App.
Shows analog or digital clock based on clock_app.ini configuration.
"""

from __future__ import annotations

import configparser
import json
import math
import os
import tkinter as tk
from datetime import datetime
from tkinter import ttk
from typing import TYPE_CHECKING, Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from ...assets.lib.lang.translator import t

if TYPE_CHECKING:
    from ...imports import ClockApp


try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


# Map common timezone abbreviations to IANA zone names
_TZ_ABBREV_TO_IANA: dict[str, str] = {
    "UTC": "UTC",
    "GMT": "Etc/GMT",
    "EST": "America/New_York",
    "CST": "America/Chicago",
    "MST": "America/Denver",
    "PST": "America/Los_Angeles",
}


def _resolve_timezone(abbrev: str) -> ZoneInfo | None:
    """Resolve timezone abbreviation or IANA name to ZoneInfo."""
    if not abbrev or not abbrev.strip():
        return None
    key = abbrev.strip().upper()
    iana = _TZ_ABBREV_TO_IANA.get(key)
    if iana:
        return ZoneInfo(iana)
    try:
        return ZoneInfo(abbrev.strip())
    except ZoneInfoNotFoundError:
        return None


def _load_clock_config(ini_path: str) -> dict[str, Any]:
    """Load clock-related config from clock_app.ini."""
    cfg = configparser.ConfigParser()
    cfg.optionxform = str
    cfg.read(ini_path, encoding="utf-8")
    out: dict[str, Any] = {
        "animation": False,
        "clock_type": "Digital",
        "clock_color": "Black",
        "use_12_hour": False,
        "time_separator": ":",
        "timezone": None,
        "clock_font": "Arial",
        "clock_font_size": 12,
    }
    for sect in ["-S- Display", "-S- Behavior"]:
        if not cfg.has_section(sect):
            continue
        for key in cfg.options(sect):
            name = key.split(".", 1)[-1] if "." in key else key
            val = cfg.get(sect, key).strip()
            if name in ("app_animation_option", "app_clock_animation"):
                out["animation"] = val.lower() in ("true", "1", "yes", "on")
            elif name == "app_clock_type":
                out["clock_type"] = val
            elif name == "app_clock_color":
                out["clock_color"] = val
            elif name == "app_time_12_hour_format":
                out["use_12_hour"] = val.lower() in ("true", "1", "yes", "on")
            elif name == "app_time_separator":
                out["time_separator"] = val
            elif name == "app_timezone":
                tz = _resolve_timezone(val)
                out["timezone"] = tz
            elif name == "app_clock_font":
                out["clock_font"] = val
            elif name == "app_clock_font_size":
                try:
                    out["clock_font_size"] = int(float(val))
                except (ValueError, TypeError):
                    pass
    return out


# Default pivots: hour/minute = center of white circle, aligned with clock face center
# (~82% from top, per hand image layout); second = bottom
DEFAULT_HAND_PIVOTS: dict[str, str | tuple[float, float]] = {
    "hour": (0.5, 0.82),
    "minute": (0.5, 0.82),
    "second": "bottom",
}


class Clock(ttk.Frame):
    """
    Clock display: analog with rotating hands, or digital based on config.
    """

    def __init__(self, parent: "ClockApp", *args: Any, **kwargs: Any) -> None:
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        from ...imports import CLOCK_APP_INI_PATH, IMAGES_FOLDER

        self._ini_path = CLOCK_APP_INI_PATH
        self._images_folder = IMAGES_FOLDER
        self._config = _load_clock_config(self._ini_path)
        self._use_digital = (
            not self._config.get("animation", True)
            and self._config.get("clock_type", "Analog") == "Digital"
        )
        self._clock_color = self._config.get("clock_color", "Black")
        self._use_12_hour = self._config.get("use_12_hour", False)
        self._time_sep = self._config.get("time_separator", ":")
        self._font_name = self._config.get("clock_font", "Arial")
        self._font_size = self._config.get("clock_font_size", 12)
        self._tz = self._config.get("timezone")
        self._analog_animation_enabled = self._config.get("animation", True)
        self._photo_refs: list[Any] = []
        self._drag_drop: dict[str, bool] = {}
        self._element_offsets: dict[str, tuple[int, int]] = {}
        self._element_scale_override: dict[str, float] = {}
        self._element_rotation_override: dict[str, float] = {}
        self._hand_pivots: dict[str, str | tuple[float, float]] = {}
        self._pivots_path = os.path.join(
            os.path.dirname(self._ini_path), "clock_pivots.json"
        )
        self._resize_mode_element: str | None = None
        self._drag_target: str | None = None
        self._drag_start: tuple[int, int] = (0, 0)
        self._last_canvas_size: tuple[int, int] | None = None
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._load_hand_pivots()
        self._build_ui()
        self._update_time()
        self.bind("<Map>", self._on_map)

    def _build_ui(self) -> None:
        """Build analog or digital clock display."""
        self.back_button = ttk.Button(
            self, text=t("common.back"),
            command=lambda: self.parent.switch_menu("main")
        )
        self.back_button.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self._build_clock_display()

    def refresh_translations(self) -> None:
        """Update labels and canvas text with current language."""
        self.back_button.config(text=t("common.back"))
        if not self._use_digital and hasattr(self, "_clock_canvas"):
            self._draw_analog_clock()

    def _find_image_path(self, base_name: str) -> str | None:
        """Return path to image; prefer jpg then tif then png for analog assets."""
        for ext in (".jpg", ".jpeg", ".tif", ".tiff", ".png"):
            path = os.path.join(self._images_folder, base_name + ext)
            if os.path.exists(path):
                return path
        return None

    def _load_analog_assets(self) -> None:
        """Load analog clock face and hand images once; reuse for drawing."""
        if not HAS_PIL:
            return
        names = ("analog_clock", "analog_clock_hour_hand",
                 "analog_clock_minute_hand", "analog_clock_second_hand")
        keys = ("face", "hour", "minute", "second")
        self._hand_images: dict[str, Image.Image] = {}
        for key, base in zip(keys, names):
            path = self._find_image_path(base)
            if path:
                self._hand_images[key] = Image.open(path).convert("RGBA")
            else:
                self._hand_images[key] = None
        self._face_cache: dict[int, Image.Image] = {}

    def _get_clock_dimensions(self) -> tuple[int, int, int]:
        """Return (radius, center_x, center_y) to fit the clock in the canvas."""
        self._clock_canvas.update_idletasks()
        w = self._clock_canvas.winfo_width()
        h = self._clock_canvas.winfo_height()
        if w <= 1 or h <= 1:
            w, h = 300, 300
        size = min(w, h)
        radius = max(20, size // 2)
        center_x = w // 2
        center_y = h // 2
        return radius, center_x, center_y

    def _rotated_hand(
        self, name: str, angle_deg: float, radius: int
    ) -> tuple[ImageTk.PhotoImage, int, int] | None:
        """Return (rotated hand photo, pivot_x, pivot_y) in rotated image. Pivot at clock center."""
        img = self._hand_images.get(name)
        if img is None:
            return None
        scale_factors = {"hour": 0.4, "minute": 0.5, "second": 0.55}
        base_scale = radius * scale_factors.get(name, 0.5)
        override = self._element_scale_override.get(name, 1.0)
        target_len = base_scale * override
        scale = target_len / max(1, max(img.width, img.height))
        new_w = max(1, int(img.width * scale))
        new_h = max(1, int(img.height * scale))
        scaled = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        pivot_spec = self._hand_pivots.get(name) or DEFAULT_HAND_PIVOTS.get(
            name, "center"
        )
        if pivot_spec == "bottom":
            px, py = new_w // 2, new_h - 1
        elif isinstance(pivot_spec, tuple):
            xr, yr = pivot_spec
            px, py = int(new_w * xr), int(new_h * yr)
        else:
            px, py = new_w // 2, new_h // 2
        rotated = scaled.rotate(
            -angle_deg,
            resample=Image.BICUBIC,
            expand=True,
            center=(px, py),
            fillcolor=(0, 0, 0, 0),
        )
        # Pivot in rotated image: bbox of rotated corners
        corners = [(0, 0), (new_w, 0), (new_w, new_h), (0, new_h)]
        cos_a = math.cos(math.radians(angle_deg))
        sin_a = math.sin(math.radians(angle_deg))
        rx = [int((c[0] - px) * cos_a - (c[1] - py) * sin_a + px) for c in corners]
        ry = [int((c[0] - px) * sin_a + (c[1] - py) * cos_a + py) for c in corners]
        min_x, min_y = min(rx), min(ry)
        pivot_out_x = px - min_x
        pivot_out_y = py - min_y
        return ImageTk.PhotoImage(rotated), pivot_out_x, pivot_out_y

    def _get_hand_transform_info(
        self, name: str, radius: int
    ) -> tuple[int, int, int, int, float] | None:
        """Return (new_w, new_h, pivot_x, pivot_y, angle_deg) for a hand."""
        img = self._hand_images.get(name) if hasattr(
            self, "_hand_images") else None
        if img is None:
            return None
        scale_factors = {"hour": 0.4, "minute": 0.5, "second": 0.55}
        base_scale = radius * scale_factors.get(name, 0.5)
        override = self._element_scale_override.get(name, 1.0)
        target_len = base_scale * override
        scale = target_len / max(1, max(img.width, img.height))
        new_w = max(1, int(img.width * scale))
        new_h = max(1, int(img.height * scale))
        pivot_spec = self._hand_pivots.get(name) or DEFAULT_HAND_PIVOTS.get(
            name, "center"
        )
        if pivot_spec == "bottom":
            pivot = (new_w // 2, new_h - 1)
        elif isinstance(pivot_spec, tuple):
            xr, yr = pivot_spec
            pivot = (int(new_w * xr), int(new_h * yr))
        else:
            pivot = (new_w // 2, new_h // 2)
        now = datetime.now(self._tz) if self._tz else datetime.now()
        sec = now.second + now.microsecond / 1_000_000
        min_val = now.minute + sec / 60
        if self._use_12_hour:
            hr = (now.hour % 12) + min_val / 60
            hr = hr % 12
        else:
            hr = (now.hour % 24) + min_val / 60
        sec_angle = sec * 6
        min_angle = min_val * 6
        hr_angle = hr * 30 if self._use_12_hour else hr * 15
        angles = {"hour": hr_angle, "minute": min_angle, "second": sec_angle}
        angle = angles.get(name, 0) + self._element_rotation_override.get(
            name, 0
        )
        return (new_w, new_h, pivot[0], pivot[1], angle)

    def _compute_pivot_from_offset(
        self, name: str, dx: int, dy: int
    ) -> tuple[float, float] | None:
        """Compute new pivot so the point at clock center becomes the pivot."""
        radius, _, _ = self._get_clock_dimensions()
        info = self._get_hand_transform_info(name, radius)
        if info is None:
            return None
        new_w, new_h, pivot_x, pivot_y, angle_deg = info
        # Vector from hand center to clock center in canvas coords: (-dx, -dy)
        # PIL rotates by -angle; inverse is +angle
        angle_rad = math.radians(angle_deg)
        off_x = -dx * math.cos(angle_rad) - dy * math.sin(angle_rad)
        off_y = dx * math.sin(angle_rad) - dy * math.cos(angle_rad)
        new_pivot_x = pivot_x + off_x
        new_pivot_y = pivot_y + off_y
        xr = max(0.001, min(0.999, new_pivot_x / new_w))
        yr = max(0.001, min(0.999, new_pivot_y / new_h))
        return (xr, yr)

    def _load_hand_pivots(self) -> None:
        """Load hand pivots and offsets from clock_pivots.json."""
        if not os.path.exists(self._pivots_path):
            return
        try:
            with open(self._pivots_path, encoding="utf-8") as f:
                data = json.load(f)
            for key in ("hour", "minute", "second"):
                if key in data:
                    val = data[key]
                    if isinstance(val, list) and len(val) == 2:
                        self._hand_pivots[key] = (float(val[0]), float(val[1]))
                    elif isinstance(val, str) and val.lower() in ("center", "bottom"):
                        self._hand_pivots[key] = val.lower()
            # Load persisted offsets so hands stay where user placed them
            offsets = data.get("offsets", {})
            for key in ("hour", "minute", "second"):
                if key in offsets and isinstance(offsets[key], list) and len(offsets[key]) == 2:
                    self._element_offsets[key] = (
                        int(offsets[key][0]),
                        int(offsets[key][1]),
                    )
        except (json.JSONDecodeError, OSError):
            pass

    def _save_hand_pivots(self) -> None:
        """Save hand pivots and offsets to clock_pivots.json."""
        data: dict[str, Any] = {}
        for key in ("hour", "minute", "second"):
            spec = self._hand_pivots.get(key)
            if isinstance(spec, tuple):
                data[key] = [round(spec[0], 4), round(spec[1], 4)]
            elif isinstance(spec, str):
                data[key] = spec
        # Persist offsets so hands remain where user placed them
        data["offsets"] = {
            key: list(self._element_offsets.get(key, (0, 0)))
            for key in ("hour", "minute", "second")
        }
        try:
            with open(self._pivots_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except OSError:
            pass

    def _on_canvas_configure(self, event: tk.Event) -> None:
        """Scale offsets on resize so pivots stay aligned; redraw; persist."""
        new_w = max(1, event.width)
        new_h = max(1, event.height)
        if self._last_canvas_size is not None:
            old_w, old_h = self._last_canvas_size
            if old_w > 0 and old_h > 0:
                scale_x = new_w / old_w
                scale_y = new_h / old_h
                for key in ("face", "hour", "minute", "second"):
                    dx, dy = self._element_offsets.get(key, (0, 0))
                    if (dx, dy) != (0, 0):
                        self._element_offsets[key] = (
                            int(round(dx * scale_x)),
                            int(round(dy * scale_y)),
                        )
                self._save_hand_pivots()
        self._last_canvas_size = (new_w, new_h)
        self._draw_analog_clock()

    def _on_canvas_click(self, event: tk.Event) -> None:
        """Start drag if clicking on a draggable element."""
        items = self._clock_canvas.find_overlapping(
            event.x, event.y, event.x, event.y)
        for iid in reversed(items):
            tags = self._clock_canvas.gettags(iid)
            for tag in tags:
                if tag in ("face", "hour", "minute", "second"):
                    if self._drag_drop.get(tag, False):
                        self._drag_target = tag
                        self._drag_start = (event.x, event.y)
                        ox, oy = self._element_offsets.get(tag, (0, 0))
                        self._element_offsets[tag] = (ox, oy)
                    return

    def _on_canvas_drag(self, event: tk.Event) -> None:
        """Update offset and move item during drag."""
        if self._drag_target is None:
            return
        dx = event.x - self._drag_start[0]
        dy = event.y - self._drag_start[1]
        ox, oy = self._element_offsets.get(self._drag_target, (0, 0))
        self._element_offsets[self._drag_target] = (ox + dx, oy + dy)
        self._drag_start = (event.x, event.y)
        _r, center_x, center_y = self._get_clock_dimensions()
        nx = center_x + ox + dx
        ny = center_y + oy + dy
        for iid in self._clock_canvas.find_withtag(self._drag_target):
            self._clock_canvas.coords(iid, nx, ny)

    def _on_canvas_release(self, _event: tk.Event) -> None:
        """End drag."""
        self._drag_target = None

    def set_drag_drop(self, element: str, enabled: bool) -> None:
        """Enable/disable drag for an element (face, hour, minute, second)."""
        self._drag_drop[element] = enabled
        if not enabled and element in ("hour", "minute", "second"):
            dx, dy = self._element_offsets.get(element, (0, 0))
            if (dx, dy) != (0, 0) and not self._use_digital:
                if hasattr(self, "_clock_canvas") and hasattr(
                    self, "_hand_images"
                ):
                    new_pivot = self._compute_pivot_from_offset(
                        element, dx, dy)
                    if new_pivot is not None:
                        self._hand_pivots[element] = new_pivot
                        self._element_offsets[element] = (0, 0)  # reset offset
            if not self._use_digital:
                self._save_hand_pivots()
                if hasattr(self, "_clock_canvas"):
                    self._draw_analog_clock()

    def set_analog_animation(self, enabled: bool) -> None:
        """Enable/disable analog clock hand animation."""
        self._analog_animation_enabled = enabled

    def set_element_scale(self, element: str, scale: float) -> None:
        """Set scale multiplier for an element (1.0 = default)."""
        self._element_scale_override[element] = max(0.1, scale)

    def set_element_rotation(self, element: str, degrees: float) -> None:
        """Set rotation override for an element (added to time-based rotation)."""
        self._element_rotation_override[element] = degrees

    def set_hand_pivot(
        self, element: str, pivot: str | tuple[float, float]
    ) -> None:
        """Set pivot for hand: 'center', 'bottom', or (x_ratio, y_ratio) 0-1."""
        self._hand_pivots[element] = pivot

    def set_resize_mode(self, element: str, enabled: bool) -> None:
        """Enable/disable resize mode for element. Use =/+ and -/_ keys when enabled."""
        self._resize_mode_element = element if enabled else None

    def adjust_resize_scale(self, delta: float) -> bool:
        """Adjust scale of element in resize mode. Returns True if handled."""
        if self._resize_mode_element is None:
            return False
        elem = self._resize_mode_element
        current = self._element_scale_override.get(elem, 1.0)
        new_val = max(0.1, min(5.0, current + delta))
        self._element_scale_override[elem] = new_val
        if not self._use_digital and hasattr(self, "_clock_canvas"):
            self._draw_analog_clock()
        return True

    def _on_map(self, _event: tk.Event) -> None:
        """Reload config when Clock becomes visible; rebuild if D.app_clock_type changed."""
        self._refresh_on_show()

    def _refresh_on_show(self) -> None:
        """Reload config from ini; rebuild display if clock type (analog/digital) changed."""
        self._config = _load_clock_config(self._ini_path)
        new_use_digital = (
            not self._config.get("animation", True)
            and self._config.get("clock_type", "Analog") == "Digital"
        )
        self._clock_color = self._config.get("clock_color", "Black")
        self._use_12_hour = self._config.get("use_12_hour", False)
        self._time_sep = self._config.get("time_separator", ":")
        self._font_name = self._config.get("clock_font", "Arial")
        self._font_size = self._config.get("clock_font_size", 12)
        self._tz = self._config.get("timezone")
        self._analog_animation_enabled = self._config.get("animation", True)
        if new_use_digital != self._use_digital:
            self._use_digital = new_use_digital
            self._destroy_clock_display()
            self._build_clock_display()
        elif self._use_digital and hasattr(self, "_time_label"):
            self._time_label.config(
                font=(self._font_name, self._font_size, "bold"),
                fg=self._clock_color,
            )
        elif not self._use_digital and hasattr(self, "_clock_canvas"):
            self._draw_analog_clock()

    def refresh_theme_colors(self) -> None:
        """Apply current app theme colors (bg/fg only)."""
        bg = self._theme_bg()
        if hasattr(self, "_time_label") and self._time_label.winfo_exists():
            self._time_label.configure(bg=bg)
        if hasattr(self, "_clock_canvas") and self._clock_canvas.winfo_exists():
            self._clock_canvas.configure(bg=bg)

    def _destroy_clock_display(self) -> None:
        """Destroy the current clock display widget (analog canvas or digital label)."""
        if hasattr(self, "_clock_canvas") and self._clock_canvas.winfo_exists():
            self._clock_canvas.destroy()
            del self._clock_canvas
        if hasattr(self, "_time_label") and self._time_label.winfo_exists():
            self._time_label.destroy()
            del self._time_label

    def _theme_bg(self) -> str:
        """Current theme background (for canvas and digital label)."""
        if hasattr(self.parent, "get_theme_colors"):
            return self.parent.get_theme_colors()[0]
        try:
            return self.cget("background")
        except tk.TclError:
            return "SystemButtonFace"

    def _build_clock_display(self) -> None:
        """Build analog or digital clock display in row 1."""
        bg = self._theme_bg()
        if self._use_digital:
            self._time_label = tk.Label(
                self,
                text="00:00:00",
                font=(self._font_name, self._font_size, "bold"),
                fg=self._clock_color,
                bg=bg,
            )
            self._time_label.grid(row=1, column=0, sticky="nsew")
        else:
            self._clock_canvas = tk.Canvas(
                self, highlightthickness=0, bg=bg,
            )
            self._clock_canvas.grid(row=1, column=0, sticky="nsew")
            self._clock_canvas.bind("<Configure>", self._on_canvas_configure)
            self._clock_canvas.bind("<Button-1>", self._on_canvas_click)
            self._clock_canvas.bind("<B1-Motion>", self._on_canvas_drag)
            self._clock_canvas.bind(
                "<ButtonRelease-1>", self._on_canvas_release)
            self._load_analog_assets()
            self._draw_analog_clock()

    def _draw_analog_clock(self, force_full: bool = True) -> None:
        """
        Draw analog clock face and hands. Uses Pillow to rotate hand images;
        pivot is at bottom-center (circular base) for natural rotation.
        Rotation: second 6°/sec, minute 6°/min + 0.1°/sec, hour 30°/hr + 0.5°/min.
        """
        radius, center_x, center_y = self._get_clock_dimensions()
        if not HAS_PIL:
            self._clock_canvas.delete("all")
            fill_color = (
                self.parent.get_theme_colors()[1]
                if hasattr(self.parent, "get_theme_colors")
                else "gray"
            )
            self._clock_canvas.create_text(
                center_x, center_y,
                text=t("clock.pillow_required"), fill=fill_color,
            )
            return
        if "face" not in self._hand_images or self._hand_images["face"] is None:
            return
        # When only time changed, redraw only hands (keeps face, avoids flicker)
        if not force_full and self._clock_canvas.find_withtag("face"):
            self._draw_analog_hands_only(radius, center_x, center_y)
            return
        self._clock_canvas.delete("all")
        new_refs: list[Any] = []
        face_img = self._hand_images["face"]
        face_scale = self._element_scale_override.get("face", 1.0)
        size = max(10, int(2 * radius * face_scale))
        if not hasattr(self, "_face_cache"):
            self._face_cache = {}
        if size not in self._face_cache:
            self._face_cache[size] = face_img.resize(
                (size, size), Image.Resampling.LANCZOS
            )
        face_photo = ImageTk.PhotoImage(self._face_cache[size])
        new_refs.append(face_photo)
        fx, fy = center_x, center_y
        if "face" in self._element_offsets:
            dx, dy = self._element_offsets["face"]
            fx, fy = center_x + dx, center_y + dy
        self._clock_canvas.create_image(
            fx, fy, image=face_photo, anchor=tk.CENTER, tags=("face",)
        )
        self._draw_analog_hands_only(radius, center_x, center_y, new_refs)
        self._photo_refs[:] = new_refs

    def _draw_analog_hands_only(
        self,
        radius: int,
        center_x: int,
        center_y: int,
        refs_list: list[Any] | None = None,
    ) -> None:
        """Draw or redraw only the hour/minute/second hands (clear old hands first)."""
        self._clock_canvas.delete("hands")
        refs_owned = refs_list is None
        if refs_owned:
            refs_list = list(self._photo_refs[:1])
        # Clock animation angles: 6° per second, 6° per min + 0.1° per sec, 30° per hr + 0.5° per min
        if self._analog_animation_enabled:
            now = datetime.now(self._tz) if self._tz else datetime.now()
            sec = now.second + now.microsecond / 1_000_000
            min_val = now.minute + sec / 60
            hr = (now.hour % 12) + min_val / 60 if self._use_12_hour else (now.hour % 24) + min_val / 60
            if self._use_12_hour:
                hr = hr % 12
            sec_angle = sec * 6
            min_angle = min_val * 6
            hr_angle = hr * 30 if self._use_12_hour else hr * 15
        else:
            sec_angle = min_angle = hr_angle = 0
        for name, angle in [("hour", hr_angle), ("minute", min_angle), ("second", sec_angle)]:
            rot_add = self._element_rotation_override.get(name, 0)
            result = self._rotated_hand(name, angle + rot_add, radius)
            if result is None:
                continue
            photo, pivot_out_x, pivot_out_y = result
            refs_list.append(photo)
            px, py = center_x, center_y
            if name in self._element_offsets:
                dx, dy = self._element_offsets[name]
                px, py = center_x + dx, center_y + dy
            self._clock_canvas.create_image(
                px - pivot_out_x, py - pivot_out_y,
                image=photo, anchor=tk.NW, tags=("hands", name)
            )
        if refs_owned:
            self._photo_refs[:] = refs_list

    def _update_time(self) -> None:
        """Update displayed time (called every second)."""
        now = datetime.now(self._tz) if self._tz else datetime.now()
        if self._use_digital:
            if self._use_12_hour:
                h = now.hour % 12 or 12
                ampm = " AM" if now.hour < 12 else " PM"
                time_str = f"{h:02d}{self._time_sep}{now.minute:02d}{self._time_sep}{now.second:02d}{ampm}"
            else:
                time_str = f"{now.hour:02d}{self._time_sep}{now.minute:02d}{self._time_sep}{now.second:02d}"
            self._time_label.config(text=time_str)
        else:
            if self._analog_animation_enabled:
                self._draw_analog_clock(force_full=False)
        self.after(1000, self._update_time)
