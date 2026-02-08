# pylint: disable=line-too-long,import-outside-toplevel,broad-exception-caught
# type: ignore[reportAttributeAccessIssue]
"""
Translate all text from clock_app.ini into the language file for the language
set in clock_app.ini (D.app_language). Uses en.json as source and updates the
target language's JSON file with translated values.

Requires: pip install deep-translator
Run: python -m test.apps.clock_app.data.scripts.translate_ini_to_lang
"""

from __future__ import annotations

import configparser
from typing import Callable
import json
import os
import sys
import time

# Resolve paths relative to clock_app root
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_APP_ROOT = os.path.dirname(os.path.dirname(
    _SCRIPT_DIR))  # data/scripts -> clock_app
_CONFIG_PATH = os.path.join(_APP_ROOT, "config", "clock_app.ini")
_LANG_DIR = os.path.join(_APP_ROOT, "assets", "lib", "lang")

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


def _get_target_language() -> str:
    """Read D.app_language from clock_app.ini."""
    if not os.path.exists(_CONFIG_PATH):
        print(f"Config not found: {_CONFIG_PATH}")
        sys.exit(1)
    cfg = configparser.ConfigParser()
    cfg.optionxform = str
    cfg.read(_CONFIG_PATH, encoding="utf-8")
    for section in ["-S- General"]:
        if cfg.has_section(section) and cfg.has_option(section, "D.app_language"):
            return cfg.get(section, "D.app_language").strip()
    return "English"


def _translate_batch(
    texts: list[str],
    source: str,
    target: str,
    progress_callback: Callable[[int, int], None] | None = None,
) -> list[str]:
    """Translate a batch of texts using deep-translator GoogleTranslate."""
    try:
        from deep_translator import GoogleTranslator
    except ImportError:
        print("Install deep-translator: pip install deep-translator")
        sys.exit(1)

    translator = GoogleTranslator(source=source, target=target)
    results: list[str] = []
    total = len(texts)
    done = 0
    for i, text in enumerate(texts):
        if not text or not text.strip():
            results.append(text)
            done += 1
            continue
        try:
            translated = translator.translate(text)
            results.append(translated if translated else text)
        except Exception as e:
            print(f"  Warning: could not translate {text[:50]!r}...: {e}")
            results.append(text)
        done = i + 1
        if progress_callback:
            progress_callback(done, total)
        if (i + 1) % 20 == 0 or i == total - 1:
            print(f"  Progress: {done}/{total}")
        time.sleep(0.15)  # Rate limit to avoid API throttling
    return results


def run(progress_callback: Callable[[int, int], None] | None = None) -> None:
    """
    Translate en.json to the target language and save.
    progress_callback: optional (done, total) callback invoked during translation.
    """
    lang_name = _get_target_language()
    code = LANG_NAME_TO_CODE.get(lang_name, "en")
    if code == "en":
        print("Target language is English; no translation needed.")
        return

    en_path = os.path.join(_LANG_DIR, "en.json")
    out_path = os.path.join(_LANG_DIR, f"{code}.json")

    if not os.path.exists(en_path):
        print(f"Source not found: {en_path}")
        sys.exit(1)

    with open(en_path, encoding="utf-8") as f:
        source_data = json.load(f)

    # Filter to string values only
    items = [(k, v) for k, v in source_data.items() if isinstance(v, str)]
    if not items:
        print("No translatable entries in en.json")
        return

    print(f"Translating {len(items)} entries to {lang_name} ({code})...")
    keys = [k for k, _ in items]
    values = [v for _, v in items]
    translated = _translate_batch(values, "en", code, progress_callback=progress_callback)

    out_data = dict(zip(keys, translated))
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out_data, f, indent=2, ensure_ascii=False)

    print(f"Saved to {out_path}")


if __name__ == "__main__":
    run()
