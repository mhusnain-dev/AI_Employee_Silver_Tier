#!/usr/bin/env python
"""
LinkedIn Post Publisher (Agent Skill)

Reads an Approved/LINKEDIN_*.md file and produces the final ready-to-post
LinkedIn artifact in Done/, then archives the approval via the
approval-workflow tracker. No live posting occurs (safe mode).

Usage:
    python .claude/skills/linkedin-poster/publish_post.py LINKEDIN_20260812_launch.md
"""

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


def find_vault_root() -> Path:
    here = Path(__file__).resolve().parent
    for candidate in [here, *here.parents]:
        if (candidate / "Inbox").is_dir() and (candidate / "Dashboard.md").is_file():
            return candidate
    return Path.cwd()


ROOT = find_vault_root()
APPROVED = ROOT / "Approved"
DONE_DIR = ROOT / "Done"
TRACKER = ROOT / ".claude" / "skills" / "approval-workflow" / "approval_tracker.py"


def main():
    parser = argparse.ArgumentParser(description="Publish an approved LinkedIn post (artifact only)")
    parser.add_argument("file", help="Approved/LINKEDIN_*.md filename")
    args = parser.parse_args()

    src = APPROVED / args.file
    if not src.exists():
        print(f"❌ {args.file} not found in Approved/", file=sys.stderr)
        sys.exit(1)

    text = src.read_text(encoding="utf-8")
    m = re.search(r"^# LinkedIn Post Draft: (.+)$", text, re.MULTILINE)
    title = m.group(1).strip() if m else args.file
    body_match = re.search(r"## Post Body\n(.*?)\n\n## To Approve", text, re.DOTALL)
    body = body_match.group(1).strip() if body_match else title

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    artifact = f"""# LinkedIn Post — Ready to Post

> Final artifact generated {now} after human approval. Copy the body into
> LinkedIn's composer (or your scheduler) and publish.

## Title
{title}

## Body
{body}

## Posting checklist
- [ ] Copy body above into LinkedIn composer
- [ ] Publish to your profile (or company page)
- [ ] Add relevant hashtags
- [ ] Engage with comments for ~30 min after posting
"""
    dest = DONE_DIR / f"{args.file.replace('.md', '')}_ready_to_post.md"
    dest.write_text(artifact, encoding="utf-8")
    print(f"✅ Ready-to-post artifact: {dest}")

    if TRACKER.exists():
        import subprocess
        subprocess.run([sys.executable, str(TRACKER), "complete", args.file], check=False)
    else:
        print("⚠️ approval-tracker not found; archive Approved/ file manually.")


if __name__ == "__main__":
    main()
