from __future__ import annotations

import hashlib


TRUE_VALUES = {"1", "true", "yes", "y", "on"}
FALSE_VALUES = {"0", "false", "no", "n", "off"}


def env_flag(raw: str | None, default: bool = False) -> bool:
    if raw is None:
        return default

    value = raw.strip().lower()
    if value in TRUE_VALUES:
        return True
    if value in FALSE_VALUES:
        return False
    return default


def pseudonymize_identifier(value: str | int | None, *, namespace: str, salt: str) -> str | None:
    if value is None:
        return None

    payload = f"{namespace}:{value}:{salt}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()
