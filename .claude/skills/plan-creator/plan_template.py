#!/usr/bin/env python
"""
Plan Template Creator (Agent Skill)

Creates a Plans/PLAN_<slug>.md file from a task title so Claude Code can
reason about a multi-step task before acting (hackathon doc §B Reasoning:
Read -> Think -> Plan).

Usage:
    python plan_template.py "Send January invoice to Client A" \
        --source Needs_Action/EMAIL_abc123.md \
        --description "Client asked for the January invoice."
"""

import argparse
import re
from datetime import datetime, timezone
from pathlib import Path


def find_vault_root() -> Path:
    here = Path(__file__).resolve().parent
    for candidate in [here, *here.parents]:
        if (candidate / "Inbox").is_dir() and (candidate / "Dashboard.md").is_file():
            return candidate
    return Path.cwd()


ROOT = find_vault_root()
PLANS_DIR = ROOT / "Plans"


def slugify(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")
    return slug or "task"


def main():
    parser = argparse.ArgumentParser(description="Create a Plan.md template")
    parser.add_argument("title", help="Task title")
    parser.add_argument("--source", default="", help="Source item (e.g. Needs_Action/EMAIL_x.md)")
    parser.add_argument("--description", default="", help="Short task description")
    args = parser.parse_args()

    PLANS_DIR.mkdir(exist_ok=True)
    slug = slugify(args.title)
    now = datetime.now(timezone.utc).isoformat()

    source_note = f"- **Source:** `{args.source}`\n" if args.source else ""
    desc_note = f"\n{args.description}\n" if args.description else ""

    content = f"""---
created: {now}
status: in_progress
source: {args.source}
---

# Plan: {args.title}

{desc_note}
## Objective
{args.title}

{source_note}
## Steps
- [ ] Step 1: <what to do first>
- [ ] Step 2: <next>
- [ ] Step 3: <verify and move item to Done>

## Approval Required
- [ ] None / add here if a sensitive action is needed (see approval-workflow)
"""

    path = PLANS_DIR / f"PLAN_{slug}.md"
    path.write_text(content, encoding="utf-8")
    print(f"✅ Created {path}")


if __name__ == "__main__":
    main()
