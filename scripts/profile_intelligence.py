#!/usr/bin/env python3
"""Build a conservative personal brand brain from a private Credora workspace.

The goal is better writing intelligence: understand the user's professional
positioning, audience, proof, goals, and observable writing rhythm without
inventing facts or inferring sensitive traits.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from scripts.learn_voice import learn
from scripts.workspace import user_root

ROOT = Path(__file__).resolve().parents[1]
PROFILE_FILES = {
    "identity": "identity.md",
    "positioning": "positioning.md",
    "expertise": "expertise.md",
    "audience": "audience.md",
    "goals": "profile-goals.md",
    "voice": "voice.md",
    "writing_rules": "writing-rules.md",
    "forbidden_style": "forbidden-style.md",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip() if path.is_file() else ""


def _initialized(text: str) -> bool:
    return bool(text) and "Status: not initialized" not in text and "- TBD" not in text


def _samples(folder: Path) -> list[str]:
    if not folder.exists():
        return []
    out = []
    for path in sorted(folder.iterdir()):
        if path.is_file() and path.suffix.lower() in {".txt", ".md"}:
            text = _read(path)
            if text:
                out.append(text)
    return out


def _keywords(text: str, limit: int = 16) -> list[str]:
    stop = {
        "about", "after", "again", "also", "and", "are", "been", "being", "but", "can", "for",
        "from", "have", "into", "more", "only", "that", "their", "them", "then", "there", "these",
        "they", "this", "through", "user", "users", "using", "with", "your", "status", "initialized",
        "primary", "secondary", "positioning", "audience", "expertise", "desired", "outcomes", "platform",
    }
    words = re.findall(r"\b[a-zA-Z][a-zA-Z0-9+#.-]{2,}\b", text.lower())
    counts: dict[str, int] = {}
    for word in words:
        if word in stop or word.isdigit():
            continue
        counts[word] = counts.get(word, 0) + 1
    return [word for word, _ in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:limit]]


def build_brand_brain(workspace: Path) -> dict:
    sections = {key: _read(workspace / rel) for key, rel in PROFILE_FILES.items()}
    initialized = {key: _initialized(text) for key, text in sections.items()}
    writing_samples = _samples(workspace / "writing-samples")
    voice = learn(writing_samples)

    core_text = "\n".join(
        sections[key]
        for key in ("positioning", "expertise", "audience", "goals")
        if initialized.get(key)
    )
    signal_count = sum(1 for key in ("identity", "positioning", "expertise", "audience", "goals") if initialized.get(key))
    completeness = round(signal_count / 5 * 100)

    confidence = "high" if completeness >= 80 and voice.get("confidence") in {"medium", "high"} else "medium" if completeness >= 60 else "low"
    warnings = []
    if completeness < 80:
        warnings.append("Profile intelligence is incomplete; missing sections must not be guessed.")
    if voice.get("confidence") in {"none", "low"}:
        warnings.append("Writing voice confidence is low. Add more real writing samples for closer style matching.")

    return {
        "schema_version": 1,
        "status": "ready" if completeness >= 60 else "needs_profile_data",
        "confidence": confidence,
        "profile_completeness": completeness,
        "initialized_sections": initialized,
        "positioning_signals": _keywords(core_text),
        "voice_fingerprint": voice,
        "source_sections": {key: text for key, text in sections.items() if initialized.get(key)},
        "writing_strategy": {
            "north_star": "Write from the user's verified positioning, audience needs, proof, and natural voice instead of generic social-media formulas.",
            "draft_sequence": [
                "Choose one verified positioning angle relevant to the requested platform and topic.",
                "Name the audience tension, question, or practical need before drafting.",
                "Use only proof, examples, metrics, experiences, or claims supported by the workspace or supplied evidence.",
                "Match observable sentence rhythm, paragraph density, person usage, punctuation, and transition habits from real samples when confidence allows.",
                "Prefer the user's own vocabulary and domain terms over generic creator language.",
                "Make one clear point per piece; do not combine unrelated professional identities just to sound impressive.",
                "Adapt the same personal brand nerve to platform norms without changing factual identity or voice.",
                "Run evidence, repetition, anti-slop, voice-fit, and approval checks before finalizing.",
            ],
            "content_modes": {
                "authority": "Teach from verified expertise and proof.",
                "practical": "Give a usable workflow, explanation, checklist, or example tied to audience needs.",
                "perspective": "Offer a reasoned opinion with uncertainty and limitations where appropriate.",
                "story": "Use personal or client stories only when they are explicitly present in source material; never manufacture anecdotes.",
                "research": "Separate evidence, interpretation, and opinion; avoid causal upgrades and unsupported certainty.",
            },
            "anti_generic_rules": [
                "Do not start from a viral-post template if it conflicts with the user's voice.",
                "Do not add fake vulnerability, fake controversy, fake quotes, or invented outcomes.",
                "Do not force a CTA when the user's natural style does not need one.",
                "Do not make every post sound like the same hook-body-CTA pattern.",
                "Do not overstate titles, credentials, seniority, expertise, or results.",
            ],
        },
        "warnings": warnings,
    }


def build_for_user(slug: str, root: Path = ROOT) -> tuple[Path, dict]:
    workspace = user_root(root, slug)
    if not workspace.is_dir():
        raise FileNotFoundError(f"User workspace does not exist: {slug}")
    brain = build_brand_brain(workspace)
    return workspace, brain


def save_for_user(slug: str, root: Path = ROOT) -> dict:
    workspace, brain = build_for_user(slug, root)
    target = workspace / "brand-brain.json"
    target.write_text(json.dumps(brain, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"status": brain["status"], "user": slug, "brand_brain": str(target), "confidence": brain["confidence"], "profile_completeness": brain["profile_completeness"], "warnings": brain["warnings"]}


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Credora personal brand intelligence")
    parser.add_argument("user")
    parser.add_argument("--print", action="store_true", dest="print_json")
    args = parser.parse_args()
    try:
        workspace, brain = build_for_user(args.user)
    except (FileNotFoundError, ValueError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2))
        return 2
    target = workspace / "brand-brain.json"
    target.write_text(json.dumps(brain, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.print_json:
        print(json.dumps(brain, indent=2, ensure_ascii=False))
    else:
        print(json.dumps({"status": brain["status"], "confidence": brain["confidence"], "profile_completeness": brain["profile_completeness"], "brand_brain": str(target), "warnings": brain["warnings"]}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
