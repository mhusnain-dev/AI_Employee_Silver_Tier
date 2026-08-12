---
name: plan-creator
description: Drive the Claude reasoning loop that creates Plan.md files. Read items in Needs_Action/, write a Plans/PLAN_*.md with checkbox steps, execute each step, then move the item to Done/. Use whenever there are items in Needs_Action/ to process.
---

# Plan Creator (Agent Skill)

The AI Employee's reasoning loop (hackathon doc §B Reasoning and §"End-to-End
Invoice Flow"). Instead of reacting to a prompt once, Claude Code:
**Read → Think → Plan → Execute → Verify → Done**.

## The loop

1. **Read** `Needs_Action/`. List every item (files, emails, drops).
2. **Plan** — for each item, create a plan:
   ```bash
   python .claude/skills/plan-creator/plan_template.py "<Task title>" \
       --source Needs_Action/<item> --description "<what must happen>"
   ```
   Then edit the generated `Plans/PLAN_*.md`: replace the placeholder steps
   with concrete checkbox steps, and mark any step that needs approval.
3. **Execute** each step yourself (file ops, drafting, analysis).
4. **Sensitive steps** — never run them directly. Write a
   `Pending_Approval/` file (see `approval-workflow` skill) and continue with
   the safe steps. Return to the approved action once the human moves the
   file to `Approved/`.
5. **Verify** — check the plan's checkboxes are all ticked.
6. **Move to Done** — rename/move the source item and the plan into `Done/`:
   - `mv Needs_Action/<item> Done/<item>`
   - `mv Plans/PLAN_*.md Done/PLAN_*.md`
7. **Refresh the dashboard**:
   ```bash
   python .claude/skills/dashboard-updater/update_dashboard.py
   ```

## Rules

- Every `Needs_Action/` item gets a `Plans/PLAN_*.md` before you act.
- A plan is complete only when all checkboxes are ticked and its item is in
  `Done/`.
- Never skip approval for sensitive steps.
- If an item cannot be completed, write `status: blocked` in the plan and a
  note explaining why; leave the item in `Needs_Action/`.

## Operating the loop (scheduled / autonomous)

For a persistent loop, run Claude Code with a goal that won't stop until the
inbox is empty, e.g.:

```
/goal Process every item in Needs_Action/: plan each, execute the safe steps,
route sensitive actions to Pending_Approval, move completed items to Done/,
and regenerate Dashboard.md. Stop only when Needs_Action/ is empty.
```
