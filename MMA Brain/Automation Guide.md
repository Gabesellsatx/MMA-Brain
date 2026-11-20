# MMA Brain capture automation

## Capture and sync

Use your existing iPhone dictation shortcut to append to `00 Inbox/Quick Capture.md`. Put each observation on its own line. A consecutive filled capture form (Date, Art, Raw thought, What worked, What failed, Next drill) is treated as one observation. Blank fields and the AI sorting instructions are skipped. Originals are never deleted or rewritten by this automation.

Push the vault with your existing Obsidian Git setup. Cloud processing sees only captures that have reached GitHub. This installation cannot verify your phone shortcut or pull-back settings remotely.

## Run and review

After installation on main, open GitHub Actions → MMA Brain — organize captures → Run workflow → main. Leave “Test synthetic captures” unchecked to propose up to three real observations. Other branches and pull requests run synthetic validation only.

Weekly processing is currently disabled. The prepared schedule is Sunday at 8:17 p.m. America/Chicago and needs explicit activation. GitHub may delay scheduled runs and disables inactive public-repository schedules after 60 days.

Open the generated draft pull request. Compare every cleaned note against its verbatim original, correct uncertain details, then mark ready and merge only when satisfied. Nothing merges automatically. Pull main back to your phone and open [[Capture Index]] in 05 Practice to find accepted notes and their existing technique links.

An open proposal blocks another batch. Closing without merging also pauses processing; only select “Explicitly retry a previously closed, unmerged proposal” when you intend to retry that batch. Merging permits the next batch. A backlog is processed three at a time, never all at once.

## What the organizer does

Ollama runs Qwen3.5 4B locally on the temporary GitHub Actions runner. No external AI API key is required. It proposes spelling corrections, classification, existing-note links and clarification questions. It has no tools or access to GitHub credentials. AI text is unverified and is not coaching or medical advice.

Generated practice notes retain the original capture, a proposed cleaned version and review questions. Existing technique notes stay untouched. Capture filenames use a stable content fingerprint; their titles appear inside each note and in the index. The processing ledger records proposed captures and supports the first-run ledger format. Repeating an accepted batch produces no duplicates. Whitespace/case-only duplicates are treated as the same capture; add a date when recording a distinct repeated session.

Invalid model output, unsafe paths, collisions, oversized captures, malformed ledgers or source edits during processing stop publication. All responses in a batch are validated before files are written. The workflow independently checks original-file preservation, ledger history, output paths and the three-capture limit before opening a PR.

The synthetic live test checks two martial arts dictations and an instruction-injection example. It is a smoke test, not a guarantee of semantic accuracy; human review remains essential.
