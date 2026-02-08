# pylint: disable=line-too-long,global-statement,keyword-arg-before-vararg
"""
Translation loader for Clock App.
Loads language files from assets/lib/lang/*.json and provides t(key) for lookups.
"""

from __future__ import annotations

import json
import os
from typing import Any

# Map config language names to ISO 639-1 codes (file names)
LANG_NAME_TO_CODE: dict[str, str] = {
    "English": "en",
    "Arabic": "ar",
    "French": "fr",
    "German": "de",
    "Italian": "it",
    "Portuguese": "pt",
    "Russian": "ru",
    "Spanish": "es",
    "Turkish": "tr",
}

# Default fallback when no translation exists
_FALLBACK: dict[str, str] = {}


def _lang_dir() -> str:
    """Return the directory containing language JSON files."""
    return os.path.dirname(os.path.abspath(__file__))


def _load_json(code: str) -> dict[str, str]:
    """Load translations from lang/{code}.json. Returns empty dict on error."""
    path = os.path.join(_lang_dir(), f"{code}.json")
    if not os.path.exists(path):
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return {str(k): str(v) for k, v in data.items() if isinstance(v, str)}
    except (json.JSONDecodeError, OSError):
        return {}


def set_language(lang_name: str) -> None:
    """Load translations for the given language (e.g. 'English', 'French')."""
    global _FALLBACK
    code = LANG_NAME_TO_CODE.get(lang_name, "en")
    _FALLBACK = _load_json(code)
    if not _FALLBACK and code != "en":
        _FALLBACK = _load_json("en")


def t(key: str, default: str | None = None, *args: Any, **kwargs: Any) -> str:
    """
    Return translation for key. Uses default if provided, else the key itself.
    Call set_language() first to load a language.
    Pass format args: t("key", "default", "val") or t("key", foo="val").
    """
    out = _FALLBACK.get(key)
    if out is None:
        out = default if default is not None else key
    if args or kwargs:
        try:
            out = out.format(*args, **kwargs)
        except (KeyError, ValueError):
            pass
    return out


def get_available_codes() -> list[str]:
    """Return list of language codes that have JSON files."""
    return [
        name[:-5] for name in os.listdir(_lang_dir())
        if name.endswith(".json")
    ]
