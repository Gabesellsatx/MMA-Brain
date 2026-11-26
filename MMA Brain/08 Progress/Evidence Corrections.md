# Evidence corrections

Your edits here are inputs, never overwritten by automation. Reports retain the original observation and show the before/after value and reason for every correction. Append new corrections instead of erasing old ones. Blocks apply from top to bottom; the last explicit value wins.

Copy the exact Evidence ID from a generated skill report. Add a block using the format below, changing the fence label from `text` to `mma-correction` when ready. Include only fields you want to change. An empty value clears a date, count or free-text field; counts must be cleared or supplied together.

```text
Evidence: paste-the-exact-evidence-id-here
Reason: Explain what was wrong and what you remember.
Date: 2026-11-22
Context: positional
Attempts: 8
Successes: 3
Problem: Describe the unresolved problem in your own words.
Diagnosis: Your or your coach's explanation, if known.
Adjustment: The change you actually tried.
Retest: What happened when you tried it again.
Issue status: testing
```

The date and counts above are format examples, not training records. Do not activate them without replacing them with actual results.

Supported fields:

- `Skill`: correct the technique name; the Evidence ID stays stable.
- `Date`: actual YYYY-MM-DD practice date, or blank if unknown. Never the upload date.
- `Context`: unknown, study, drilling, positional, live, competition.
- `Attempts` and `Successes`: exact integers together; successes cannot exceed attempts. Leave both blank for approximate or unknown counts.
- `Problem`, `Diagnosis`, `Adjustment`, `Retest`, `Variation`: your reported details, not an AI diagnosis. Variation describes the task/opponent reaction actually tested.
- `Issue status`: unknown, open, testing, resolved. Resolution is your explicit judgment about this observation's problem; no automatic resolution from a later success.
- `Understanding`: unknown or demonstrated. Use demonstrated only when you can explain the mechanics and decision to use the technique.
- `Safety`: unknown, concern, cleared. A clearance records your correction only; it is not medical clearance.
- `Self assessment`: Unknown, Learning, Developing, Reliable, Advanced. Displayed alongside the calculated assessment, never disguised as a computed fact.
- `Exclude`: no or yes. Excludes evidence from scoring while keeping the source and correction history.

If one session appears in multiple captures, use Exclude to prevent double counting. Multiple captures on the same date count as one dated session for consistency thresholds.

Sync corrections to main before the next batch. If a proposal is already open, review it first; the review gate pauses recalculation until that proposal is merged or explicitly retried. Corrections submitted after a proposal was generated take effect in the following proposal.

## Append corrections below
