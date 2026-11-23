# Living training progress

Open [[08 Progress/Generated/Training Dashboard|What should I train next?]] or [[08 Progress/Generated/Training Progress.canvas|Training Progress canvas]]. Each skill report answers what you know, what you can execute, and what changed. Links connect reported evidence with exact existing knowledge notes; missing technique notes remain explicitly unmatched.

The canvas is an automatically arranged view of the reports. Your existing knowledge maps are preserved. To customize layout, duplicate the generated canvas under another name. Editing generated output directly pauses regeneration rather than silently discarding your changes.

## After training

Keep speaking naturally into Quick Capture. The original words remain untouched. Recognizable skill names create progress reports automatically once their captures are processed. One unambiguous ISO date, explicit phrases such as “during live rolls,” and exact statements such as “completed 3 of 8 attempts” are recognized for a single named skill. Approximate or ambiguous counts stay unknown; natural-language improvement claims remain quoted evidence rather than automatic mastery scores.

For automatic quantitative updates, dictate one skill per capture with explicit labels separated by semicolons. Use this structure, replacing the placeholders with your actual information:

> Date: YYYY-MM-DD; Skill: technique name; Context: positional; Attempts: number; Successes: number; Problem: what failed; Diagnosis: why you think it failed; Adjustment: what you changed; Retest: what happened; Issue status: testing

Use ISO dates. Do not submit placeholders or approximate counts as exact numbers. You can omit any unknown field; supply Attempts and Successes together. For multiple skills in one unstructured capture, the system quotes the shared source but does not attribute its numerical results to a particular skill. You can clarify each skill through [[Evidence Corrections]].

A skill must be explicitly named or supplied through the Skill field. Ambiguous body-part words do not silently become techniques. Unrecognized captures appear in Needs context. The current organizer reads Quick Capture; other session-note folders are not automatically ingested.

If a capture contains invalid facts, such as a future date, impossible counts, or duplicate labels, its extracted facts stay unknown and its report explains the problem. Correct the evidence through Evidence Corrections; the original remains unchanged. Invalid correction blocks stop refresh until you fix the block.

## Observe → Diagnose → Correct → Retest → Retain

- Observe: verbatim source plus your reported problem and outcome.
- Diagnose: your explanation or your coach's explanation, labelled as reported and left unknown when missing.
- Correct: the adjustment you actually tried.
- Retest: the outcome of testing that adjustment. A success never automatically closes an earlier problem.
- Retain: successful dated resistance evidence at least 14 days apart. This is a retention signal, not proof of permanent mastery.

## Honest assessments

The five dimensions are understanding, execution under resistance, consistency, adaptability, and retention. Each shows whether its evidence threshold is met. Missing evidence is not the same as inability.

The stage is a provisional personal rubric:

| Stage | Required evidence |
|---|---|
| Unknown | No qualifying execution/learning evidence |
| Learning | Dated study or drilling, or explicitly demonstrated understanding |
| Developing | At least one dated success in positional, live, or competition context |
| Reliable | Demonstrated understanding, at least 20 measured attempts across three dates, at least 70% success under resistance |
| Advanced | Reliable, plus successful evidence in two named variations and successful dates at least 14 days apart |

These are transparent design thresholds, not a validated martial-arts measurement scale. No overall mastery percentage is invented. Numerical percentages describe logged success rates by context, with their numerator and denominator. The rubric may combine resistance contexts for a coarse stage; inspect the separate context rows before comparing performance. Opponent level, task difficulty and incomplete logging limit comparability. Confidence is Low with fewer than three measured dates and at most Moderate otherwise. A gap over 30 days lowers confidence and raises a retention-check priority; it does not erase prior achievement.

## Choosing the next practice target

The dashboard orders review of reported safety concerns first, unresolved reported problems next, overdue retention checks, then missing baseline measurements and repeated comparable testing. These are evidence-gathering suggestions, not invented technical diagnoses or claims that you should perform painful movements. Your coach determines suitable drills and resistance.

Every report includes its source, evidence identifier, correction history, last dated practice, and a timeline with unknown dates separated. [[Evidence Corrections]] lets you fix facts, explicitly resolve a problem, exclude duplicate evidence, or add a self assessment without rewriting the original capture. Generated files may be proposed alongside newly processed captures and remain provisional until reviewed.

## Automatic updates

The weekly workflow recalculates reports and the canvas from ledger-backed captures and your correction notes. It processes at most three new captures per batch. Existing unprocessed backlog is not swept into scores. Corrections and retention priorities can refresh even when there are no new captures. Updates arrive in the same draft PR and never merge automatically. An open proposal pauses the next batch.

After merging a proposal, pull main to your phone through your existing Obsidian Git setup. The report and canvas require no extra Obsidian plugin.
