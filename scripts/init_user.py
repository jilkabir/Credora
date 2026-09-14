#!/usr/bin/env python3
"""Create a private plug-and-play Credora workspace for one user."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
USERS_ROOT = ROOT / "users"

FILES = {
    "identity.md": "# Identity\n\nStatus: not initialized\n\nAdd only user-confirmed public/professional facts. Never infer missing credentials, employers, awards, metrics, clients, publications, or personal details.\n",
    "positioning.md": "# Positioning\n\nStatus: not initialized\n\nPrimary positioning:\n- TBD\n\nSecondary positioning:\n- TBD\n\nDo not position the user beyond verified experience.\n",
    "expertise.md": "# Expertise\n\nStatus: not initialized\n\nAdd only verified expertise areas and proof.\n",
    "audience.md": "# Audience\n\nStatus: not initialized\n\nPrimary audience:\n- TBD\n\nSecondary audience:\n- TBD\n",
    "voice.md": "# Writing Voice\n\nStatus: not initialized\n\nLearn from real user writing samples. Do not imitate unverifiable traits or invent a voice profile without samples.\n",
    "talking-style.md": "# Talking Style\n\nStatus: not initialized\n\nLearn separately from real transcripts or voice-note transcripts. Writing voice and speaking voice are not assumed to be the same.\n",
    "writing-rules.md": "# Writing Rules\n\n- Be clear, specific, and useful.\n- Prefer natural paragraphs over forced one-line fragments.\n- Explain why a point matters.\n- Never invent facts, quotes, metrics, stories, clients, or outcomes.\n",
    "forbidden-style.md": "# Forbidden Style\n\n- No decorative em dashes by default.\n- No emoji bullet spam.\n- No fake vulnerability or fabricated anecdotes.\n- No generic engagement bait such as forced 'Thoughts?' or 'Agree?'.\n- No hype phrases such as 'game-changer', 'unlock your potential', or 'let\'s dive in' unless the user explicitly wants them.\n",
    "profile-goals.md": "# Profile Goals\n\nStatus: not initialized\n\nDesired outcomes:\n- TBD\n\nPlatform priorities:\n- TBD\n",
    "platforms/linkedin.md": "# LinkedIn\n\nGoal: credible professional positioning and useful content.\n\nUse verified positioning, one clear idea, natural professional language, supported claims, and user approval before finalizing. Avoid engagement bait, fake stories, and unsupported growth/algorithm claims.\n",
    "platforms/facebook.md": "# Facebook\n\nUse a warmer contextual voice when appropriate. Never fabricate personal stories, emotions, relationships, or events. User approval is required.\n",
    "platforms/instagram.md": "# Instagram\n\nKeep captions concise, natural, and visually contextual. Avoid emoji clutter, hashtag stuffing, generic inspiration, and fabricated reactions. User approval is required.\n",
    "platforms/youtube.md": "# YouTube\n\nUse talking-style rather than article voice alone. Write for listening. Do not invent tool capabilities, numbers, urgency, or controversy. User approval is required.\n",
}

DEFAULT_STYLE = {
    "profile": "user-default",
    "version": 1,
    "voice_fit_threshold": 65,
    "hard_banned_phrases": [
        "game-changer", "unlock your potential", "delve into", "let's dive in",
        "here's the thing", "in today's fast-paced world", "elevate your game", "supercharge",
    ],
    "generic_ctas": ["thoughts?", "agree?", "what do you think?"],
    "limits": {
        "max_emojis_per_300_words": 2,
        "max_em_dash_per_300_words": 1,
        "max_single_sentence_paragraph_ratio": 0.55,
    },
    "notes": [
        "Start conservative. Learn personal style from real user writing samples and explicit feedback.",
        "Do not invent personal stories, metrics, quotes, credentials, clients, or outcomes.",
    ],
}


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "user"


def init_user(name: str, slug: str | None = None, force: bool = False) -> dict:
    user_slug = slugify(slug or name)
    root = USERS_ROOT / user_slug
    if root.exists() and not force:
        raise FileExistsError(f"Workspace already exists: {root}")
    root.mkdir(parents=True, exist_ok=True)
    created = []
    for rel, content in FILES.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if force or not path.exists():
            path.write_text(content, encoding="utf-8")
            created.append(rel)
    style_path = root / "style.json"
    if force or not style_path.exists():
        style = dict(DEFAULT_STYLE)
        style["profile"] = f"{user_slug}-default"
        style_path.write_text(json.dumps(style, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        created.append("style.json")
    for folder in ["writing-samples", "speaking-samples", "content-history", "performance"]:
        (root / folder).mkdir(exist_ok=True)
    manifest = {
        "name": name,
        "slug": user_slug,
        "schema_version": 2,
        "private_workspace": True,
        "approval_required": True,
        "auto_publish": False,
    }
    (root / "credora.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    pref = root / "preferences.jsonl"
    if force or not pref.exists():
        pref.write_text("", encoding="utf-8")
    return {"status": "created", "workspace": str(root), "slug": user_slug, "files_created": created}


def main() -> int:
    p = argparse.ArgumentParser(description="Create a private Credora user workspace")
    p.add_argument("name")
    p.add_argument("--slug")
    p.add_argument("--force", action="store_true")
    args = p.parse_args()
    try:
        result = init_user(args.name, args.slug, args.force)
    except FileExistsError as exc:
        print(json.dumps({"status": "exists", "error": str(exc)}, indent=2))
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
