# config_loader.py
# Reads settings.cfg.

SETTINGS_FILE = "settings.cfg"

KNOWN_KEYS = [
    "service_interval_km",
    "warn_at_percent",
    "report_title",
    "history_file",
    "log_file",
    "mileage_unit",
]


def load_settings(path: str = None) -> dict:
    """Parse settings.cfg and return a dict of known key/value pairs."""
    if path is None:
        path = SETTINGS_FILE
    settings = {}
    with open(path) as f:
        for line in f.readlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            parts = line.split("=")
            key = parts[0].strip()
            value = parts[1].strip()
            if key in KNOWN_KEYS:
                settings[key] = value
            else:
                print(f"Warning: unknown key '{key}' in {path} — possible typo")
    return settings


def get_int(settings: dict, key: str, fallback: int) -> int:
    """Return an integer setting value, or fallback if missing or invalid."""
    if key in settings:
        try:
            return int(settings[key])
        except ValueError:
            return fallback
    return fallback


def get_setting(settings: dict, key: str, fallback: str = "") -> str:
    """Return a string setting value, or fallback if the key is absent."""
    return settings.get(key, fallback)
