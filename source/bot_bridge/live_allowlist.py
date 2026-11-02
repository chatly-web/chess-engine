"""Local challenge access only. No token, chess decisions, or Lichess API calls."""
import fcntl
import json
import os
from pathlib import Path
import re
import tempfile

USERNAME = re.compile(r"[A-Za-z0-9_-]{2,30}\Z", re.ASCII)


def validate(names):
    if not isinstance(names, list) or len(names) > 1000:
        raise ValueError("Allowlist must contain at most 1,000 usernames.")
    unique = {}
    for name in names:
        if not isinstance(name, str) or not USERNAME.fullmatch(name):
            raise ValueError("Use a username only: 2–30 letters, digits, underscores or hyphens.")
        unique.setdefault(name.casefold(), name)
    return sorted(unique.values(), key=str.casefold)


def read_usernames(path):
    path = Path(path)
    if path.stat().st_size > 65536:
        raise ValueError("Allowlist is too large.")
    return validate(json.loads(path.read_text(encoding="utf-8")))


def update_usernames(path, username, remove=False):
    """Serialize local editors and atomically replace the owner-only JSON file."""
    path = Path(path)
    validate([username])
    with os.fdopen(os.open(str(path) + ".lock", os.O_CREAT | os.O_RDWR, 0o600), "a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        names = read_usernames(path)
        if remove:
            names = [name for name in names if name.casefold() != username.casefold()]
        elif username.casefold() not in {name.casefold() for name in names}:
            names.append(username)
        names = validate(names)
        fd, temp = tempfile.mkstemp(prefix=".access-", dir=path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                json.dump(names, stream, indent=2)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp, path)
        finally:
            if os.path.exists(temp):
                os.unlink(temp)
        return names
