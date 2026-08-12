---
name: linkedin-poster
description: Create business sales posts for LinkedIn. Drafts a post to Pending_Approval/, and after human approval produces a final ready-to-post LinkedIn artifact. Never posts live (safe mode). Use for generating business/sales content for LinkedIn.
---

# LinkedIn Poster (Agent Skill)

Generates business sales posts for LinkedIn, gated behind human approval
(hackathon doc Silver Tier: "Automatically Post on LinkedIn about business to
generate sales"). **Safe mode:** no live posting — approval produces a final
ready-to-post artifact. Live posting is out of scope (LinkedIn ToS/ban risk).

## Workflow

1. **Draft** a post (you or Claude run):
   ```bash
   python .claude/skills/linkedin-poster/create_post.py \
       "We now help SMBs automate their admin work" \
       --hashtags "#AI #Automation #SMB"
   ```
   → creates `Pending_Approval/LINKEDIN_<date>_<slug>.md`

2. **Human approves** by moving the file to `Approved/` (or `Rejected/`).

3. **Publish (artifact only):**
   ```bash
   python .claude/skills/linkedin-poster/publish_post.py LINKEDIN_<date>_<slug>.md
   ```
   → writes `Done/LINKEDIN_<date>_<slug>_ready_to_post.md` with the final body
   and a posting checklist, and logs the action via the approval tracker.

## Rules

- Never post to LinkedIn programmatically.
- A post is only generated/executed after the human moves the approval file.
- If a draft is rejected, run:
  ```bash
  python .claude/skills/approval-workflow/approval_tracker.py cancel <file>
  ```

## For Claude

When the user asks for a LinkedIn post "about business to generate sales",
check `Business_Goals.md` for context, draft a compelling post (hook, value,
call-to-action, hashtags), write it via `create_post.py`, and tell the user
where the approval file is.
