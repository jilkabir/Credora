#!/usr/bin/env python3
"""Safe helpers for private Credora user workspaces."""
from __future__ import annotations

import re
from pathlib import Path

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def validate_slug(slug: str) -> str:
    """Validate a workspace slug and reject path traversal or ambiguous paths."""
    if not slug or not SLUG_RE.fullmatch(slug):
        raise ValueError(
            "Invalid user workspace slug. Use lowercase letters, numbers, and single hyphens only."
        )
    return slug


def user_root(root: Path, slug: str) -> Path:
    """Return a resolved users/<slug> path guaranteed to stay inside users/."""
    safe = validate_slug(slug)
    users_root = (root / "users").resolve()
    candidate = (users_root / safe).resolve()
    if candidate.parent != users_root:
        raise ValueError("Invalid user workspace path.")
    return candidate
