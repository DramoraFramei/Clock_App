# pylint: disable=line-too-long,broad-exception-caught,too-many-return-statements
# type: ignore[assignment]
"""
Update checker for Clock App. Uses GitHub Releases API when source is GitHub.
"""

from __future__ import annotations

import configparser
import json
import os
import re
import ssl
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

from ..imports import CLOCK_APP_INI_PATH


@dataclass
class UpdateResult:
    """Result of an update check."""

    has_update: bool
    current_version: str
    latest_version: str
    release_url: str
    release_notes: str
    error: str | None = None


def _parse_version(version_str: str) -> list[int]:
    """Parse version string like '0.0.01' or 'v0.0.02-dev' into comparable parts."""
    # Strip leading 'v' and any suffix (-dev, -beta, etc.)
    cleaned = re.sub(r"^v", "", str(version_str).strip().lower())
    cleaned = re.split(r"[-_a-z]", cleaned, maxsplit=1)[0]
    parts: list[int] = []
    for p in cleaned.split("."):
        try:
            parts.append(int(p))
        except ValueError:
            parts.append(0)
    return parts if parts else [0]


def _version_less_than(current: str, latest: str) -> bool:
    """Return True if current < latest."""
    cur_parts = _parse_version(current)
    lat_parts = _parse_version(latest)
    max_len = max(len(cur_parts), len(lat_parts))
    for i in range(max_len):
        c = cur_parts[i] if i < len(cur_parts) else 0
        l_ = lat_parts[i] if i < len(lat_parts) else 0
        if c < l_:
            return True
        if c > l_:
            return False
    return False


def _extract_repo_from_github_url(url: str) -> str | None:
    """Extract 'owner/repo' from https://github.com/owner/repo or similar."""
    if not url or "github.com" not in url:
        return None
    url = url.strip().rstrip("/")
    # Handle optional .git suffix
    if url.endswith(".git"):
        url = url[:-4]
    parts = url.split("github.com/")
    if len(parts) < 2:
        return None
    repo_path = parts[-1].strip().rstrip("/")
    if "/" in repo_path and not repo_path.startswith("/"):
        return repo_path
    return None


def _release_matches_channel(release: dict[str, Any], channel: str) -> bool:
    """Return True if release matches the update channel (Stable, Beta, Dev)."""
    channel = (channel or "Stable").strip().lower()
    prerelease = release.get("prerelease", False)
    tag = (release.get("tag_name") or "").lower()
    name = (release.get("name") or "").lower()
    combined = f"{tag} {name}"

    if channel == "stable":
        return not prerelease
    if channel == "beta":
        return prerelease and ("beta" in combined)
    if channel == "dev":
        return prerelease and ("dev" in combined or "pre-alpha" in combined)
    return not prerelease


def _load_update_config() -> dict[str, Any]:
    """Load update-related config from clock_app.ini."""
    out: dict[str, Any] = {
        "update_option": "Automatic",
        "channel": "Stable",
        "frequency": "Daily",
        "check_time": "12:00",
        "source": "GitHub",
        "github_url": "",
        "current_version": "0.0.01",
    }
    if not os.path.exists(CLOCK_APP_INI_PATH):
        return out
    cfg = configparser.ConfigParser()
    cfg.optionxform = str
    cfg.read(CLOCK_APP_INI_PATH, encoding="utf-8")

    for sect in ["-C- App Info", "-S- Updates"]:
        if not cfg.has_section(sect):
            continue
        for key in cfg.options(sect):
            name = key.split(".", 1)[-1] if "." in key else key
            val = cfg.get(sect, key).strip()
            if name == "app_github_url":
                out["github_url"] = val
            elif name == "app_version":
                out["current_version"] = val
            elif name == "app_update_option":
                out["update_option"] = val
            elif name == "app_update_channel":
                out["channel"] = val
            elif name == "app_update_check_frequency":
                out["frequency"] = val
            elif name == "app_update_check_time":
                out["check_time"] = val
            elif name == "app_update_source":
                out["source"] = val
    return out


def check_for_updates() -> UpdateResult:
    """
    Check for updates using the configured source (GitHub only for now).
    Returns UpdateResult with has_update, latest_version, release_url, etc.
    """
    config = _load_update_config()
    current = config.get("current_version", "0.0.01")
    source = (config.get("source") or "GitHub").strip()
    channel = config.get("channel", "Stable")

    if source.lower() != "github":
        return UpdateResult(
            has_update=False,
            current_version=current,
            latest_version=current,
            release_url="",
            release_notes="",
            error=None,
        )

    repo = _extract_repo_from_github_url(config.get("github_url", ""))
    if not repo:
        return UpdateResult(
            has_update=False,
            current_version=current,
            latest_version=current,
            release_url="",
            release_notes="",
            error="Invalid GitHub URL in config",
        )

    api_url = f"https://api.github.com/repos/{repo}/releases"
    try:
        ctx = ssl.create_default_context()
        req = urllib.request.Request(
            api_url,
            headers={"Accept": "application/vnd.github.v3+json",
                     "User-Agent": "Clock-App"},
        )
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            data = resp.read().decode("utf-8")
    except Exception as e:
        return UpdateResult(
            has_update=False,
            current_version=current,
            latest_version=current,
            release_url="",
            release_notes="",
            error=str(e),
        )

    try:
        releases = json.loads(data)
    except json.JSONDecodeError as e:
        return UpdateResult(
            has_update=False,
            current_version=current,
            latest_version=current,
            release_url="",
            release_notes="",
            error=str(e),
        )

    if not isinstance(releases, list):
        return UpdateResult(
            has_update=False,
            current_version=current,
            latest_version=current,
            release_url="",
            release_notes="",
            error="Invalid API response",
        )

    for rel in releases:
        if not _release_matches_channel(rel, channel):
            continue
        tag = rel.get("tag_name") or ""
        tag_clean = re.sub(r"^v", "", tag)
        if _version_less_than(current, tag_clean):
            return UpdateResult(
                has_update=True,
                current_version=current,
                latest_version=tag_clean or tag,
                release_url=rel.get(
                    "html_url", f"https://github.com/{repo}/releases"),
                release_notes=rel.get("body", "") or "",
                error=None,
            )

    return UpdateResult(
        has_update=False,
        current_version=current,
        latest_version=current,
        release_url=f"https://github.com/{repo}/releases",
        release_notes="",
        error=None,
    )
