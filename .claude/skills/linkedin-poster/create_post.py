#!/usr/bin/env python
"""
LinkedIn Post Creator (Agent Skill)

Drafts a business sales post and files it under Pending_Approval/ so a human
can approve it before publishing. Never publishes live (LinkedIn ToS/ban risk
out of scope) — an approved post is turned into a ready-to-post artifact by
publish_post.py.

Usage:
    python create_post.py "We now help SMBs automate admin work" \
        --hashtags "#AI #Automation #SMB"
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
PENDING = ROOT / "Pending_Approval"
BUSINESS_GOALS = ROOT / "Business_Goals.md"


def slugify(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_") or "post"


def main():
    parser = argparse.ArgumentParser(description="Create a LinkedIn post draft for approval")
    parser.add_argument("topic", help="What the post is about")
    parser.add_argument("--hashtags", default="", help="Comma/space separated hashtags")
    args = parser.parse_args()

    PENDING.mkdir(exist_ok=True)
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y%m%d")
    slug = slugify(args.topic)
    filename = f"LINKEDIN_{date_str}_{slug}.md"
    path = PENDING / filename

    goal_context = ""
    if BUSINESS_GOALS.exists():
        goal_context = BUSINESS_GOALS.read_text(encoding="utf-8")[:500]
        goal_context = f"\nContext from Business_Goals.md:\n{goal_context}\n"

    content = f"""---
type: approval_request
action: linkedin_post
target: linkedin.com
created: {now.isoformat()}
status: pending
---

# LinkedIn Post Draft: {args.topic}

{goal_context}
## Post Body
{args.topic}

<draft body — Claude/you can expand this into a compelling sales post>

{args.hashtags}

## To Approve
Move this file to `/Approved` to generate the ready-to-post artifact.

## To Reject
Move this file to `/Rejected` to cancel.
"""
    path.write_text(content, encoding="utf-8")
    print(f"✅ Draft created: {path}")


if __name__ == "__main__":
    main()
