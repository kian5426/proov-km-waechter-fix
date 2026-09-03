# log_util.py
# A simple homemade logger.

import time

LOG_LINES: list = []   # module-level buffer; call clear_log() between test runs
DEBUG = False


def log(message: str) -> None:
    """Append a timestamped line to the buffer and print it."""
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{stamp}] {message}"
    LOG_LINES.append(line)
    print(line)


def debug(message: str) -> None:
    """Log a debug message (only active when DEBUG is True)."""
    if DEBUG:
        log(f"DEBUG: {message}")


def flush_log(path: str) -> None:
    """Write buffered log lines to a file, then clear the buffer."""
    with open(path, "a") as f:
        for line in LOG_LINES:
            f.write(line + "\n")
    clear_log()


def clear_log() -> None:
    """Clear the in-memory log buffer."""
    del LOG_LINES[:]
