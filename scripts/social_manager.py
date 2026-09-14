#!/usr/bin/env python3
"""Credora social-manager planning and approval queue foundation."""
from __future__ import annotations

import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from scripts.workspace import user_root

VALID_STATUSES = {"planned", "drafting", "waiting_approval", "approved", "scheduled", "published", "rejected"}
DEFAULT_PILLARS = ["educational", "authority", "personal insight", "conversation"]
DEFAULT_FORMATS = ["text", "image", "text", "document"]


def _manager_dir(root: Path, slug: str) -> Path:
    ws = user_root(root, slug)
    if not ws.is_dir():
        raise FileNotFoundError(f"User workspace does not exist: {slug}")
    target = ws / "social-manager"
    target.mkdir(exist_ok=True)
    return target


def _read_json(path: Path, default):
    if not path.exists():
        return default
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path}: {exc.msg}") from exc
    return value


def _write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def create_calendar(slug: str, root: Path, *, month: str | None = None, posts: int = 12, platform: str = "linkedin") -> dict:
    if posts < 1 or posts > 62:
        raise ValueError("posts must be between 1 and 62")
    if month:
        try:
            first = datetime.strptime(month, "%Y-%m").date().replace(day=1)
        except ValueError as exc:
            raise ValueError("month must use YYYY-MM format") from exc
    else:
        today = date.today()
        first = today.replace(day=1)
    next_month = (first.replace(day=28) + timedelta(days=4)).replace(day=1)
    days = max(1, (next_month - first).days)
    manager = _manager_dir(root, slug)
    calendar_path = manager / "calendar.json"
    existing = _read_json(calendar_path, {"version": 1, "items": []})
    if not isinstance(existing, dict) or not isinstance(existing.get("items", []), list):
        raise ValueError("Invalid social-manager calendar structure")
    month_key = first.strftime("%Y-%m")
    existing["items"] = [item for item in existing.get("items", []) if item.get("month") != month_key or item.get("platform") != platform]
    created = []
    for i in range(posts):
        day = 1 + round(i * (days - 1) / max(posts - 1, 1))
        scheduled = first.replace(day=min(day, days))
        item = {
            "id": f"{month_key}-{platform}-{i + 1:02d}",
            "month": month_key,
            "date": scheduled.isoformat(),
            "platform": platform,
            "pillar": DEFAULT_PILLARS[i % len(DEFAULT_PILLARS)],
            "format": DEFAULT_FORMATS[i % len(DEFAULT_FORMATS)],
            "objective": "build trust and relevant audience growth",
            "topic": "to be selected from the user's Brand Brain and current goals",
            "status": "planned",
            "approval_required": True,
            "auto_publish": False,
        }
        created.append(item)
    existing["version"] = 1
    existing["items"].extend(created)
    _write_json(calendar_path, existing)
    return {"status": "ok", "user": slug, "month": month_key, "platform": platform, "posts": len(created), "calendar": str(calendar_path), "items": created}


def queue_draft(slug: str, root: Path, *, calendar_id: str, draft_file: Path) -> dict:
    manager = _manager_dir(root, slug)
    if not draft_file.is_file():
        raise FileNotFoundError(f"Draft file does not exist: {draft_file}")
    text = draft_file.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError("Draft cannot be empty")
    calendar = _read_json(manager / "calendar.json", {"items": []})
    item = next((x for x in calendar.get("items", []) if x.get("id") == calendar_id), None)
    if item is None:
        raise ValueError(f"Calendar item does not exist: {calendar_id}")
    queue_path = manager / "approval-queue.json"
    queue = _read_json(queue_path, {"version": 1, "items": []})
    if not isinstance(queue, dict) or not isinstance(queue.get("items", []), list):
        raise ValueError("Invalid approval queue structure")
    record = {
        "id": calendar_id,
        "platform": item.get("platform"),
        "scheduled_date": item.get("date"),
        "draft": text,
        "status": "waiting_approval",
        "approval_required": True,
        "approved_at": None,
        "published_at": None,
    }
    queue["items"] = [x for x in queue.get("items", []) if x.get("id") != calendar_id] + [record]
    _write_json(queue_path, queue)
    item["status"] = "waiting_approval"
    _write_json(manager / "calendar.json", calendar)
    return record


def set_approval(slug: str, root: Path, item_id: str, approved: bool) -> dict:
    manager = _manager_dir(root, slug)
    queue_path = manager / "approval-queue.json"
    queue = _read_json(queue_path, {"version": 1, "items": []})
    record = next((x for x in queue.get("items", []) if x.get("id") == item_id), None)
    if record is None:
        raise ValueError(f"Approval item does not exist: {item_id}")
    record["status"] = "approved" if approved else "rejected"
    record["approved_at"] = datetime.now(timezone.utc).isoformat() if approved else None
    _write_json(queue_path, queue)
    calendar_path = manager / "calendar.json"
    calendar = _read_json(calendar_path, {"items": []})
    for item in calendar.get("items", []):
        if item.get("id") == item_id:
            item["status"] = record["status"]
    _write_json(calendar_path, calendar)
    return record


def manager_status(slug: str, root: Path) -> dict:
    manager = _manager_dir(root, slug)
    calendar = _read_json(manager / "calendar.json", {"items": []})
    queue = _read_json(manager / "approval-queue.json", {"items": []})
    items = calendar.get("items", []) if isinstance(calendar, dict) else []
    approvals = queue.get("items", []) if isinstance(queue, dict) else []
    counts = {status: sum(1 for x in items if x.get("status") == status) for status in VALID_STATUSES}
    return {
        "user": slug,
        "calendar_items": len(items),
        "waiting_approval": sum(1 for x in approvals if x.get("status") == "waiting_approval"),
        "approved": sum(1 for x in approvals if x.get("status") == "approved"),
        "counts": counts,
        "publishing_connected": False,
        "auto_publish": False,
    }
