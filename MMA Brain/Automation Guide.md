# MMA Brain capture automation

## Capture and sync

Use your existing iPhone dictation shortcut to append to `00 Inbox/Quick Capture.md`. Put each observation on its own line. A consecutive filled capture form (Date, Art, Raw thought, What worked, What failed, Next drill) is treated as one observation. Blank fields and the AI sorting instructions are skipped. Originals are never deleted or rewritten by this automation.

Push the vault with your existing Obsidian Git setup. Cloud processing sees only captures that have reached GitHub. This installation cannot verify your phone shortcut or pull-back settings remotely.

## Run and review

After installation on main, open GitHub Actions → MMA Brain — organize captures → Run workflow → main. Leave “Test synthetic captures” unchecked to propose up to three real observations. Other branches and pull requests run synthetic validation only.

Weekly processing is enabled for Sunday at 8:17 p.m. America/Chicago (Central time, including daylight-saving changes), following approval and the user-confirmed iPhone pull-back sync check. Each run proposes at most three captures and waits for review before another batch. GitHub may delay scheduled runs and disables inactive public-repository schedules after 60 days.

Open the generated draft pull request. Compare every cleaned note against its verbatim original, correct uncertain details, then mark ready and merge only when satisfied. Nothing merges automatically. Pull main back to your phone and open [[Capture Index]] in 05 Practice to find accepted notes and their existing technique links.

An open proposal blocks another batch. Closing without merging also pauses processing; only select “Explicitly retry a previously closed, unmerged proposal” when you intend to retry that batch. Merging permits the next batch. A backlog is processed three at a time, never all at once.

## What the organizer does

Ollama runs Qwen3.5 4B locally on the temporary GitHub Actions runner. No external AI API key is required. It proposes classification, which still requires review. Displayed cleanup uses only a small, reviewed list of spelling substitutions and otherwise keeps the source wording, including uncertainty and pain descriptions. Freeform model rewrites, titles, links and questions are not published. Links require an explicit matching note name in the capture; longer names take precedence, so Single Leg X cannot be linked to Single Leg merely because its own note is missing. A recognized technique without an existing note gets a review question rather than a substitute technique. The model has no tools or access to GitHub credentials. Proposals are not coaching or medical advice.

Generated practice notes retain the original capture, a proposed cleaned version and review questions. Existing technique notes stay untouched. Capture filenames use a stable content fingerprint; their titles appear inside each note and in the index. The processing ledger records proposed captures and supports the first-run ledger format. Repeating an accepted batch produces no duplicates. Whitespace/case-only duplicates are treated as the same capture; add a date when recording a distinct repeated session.

Invalid model output, unsafe paths, collisions, oversized captures, malformed ledgers or source edits during processing stop publication. All responses in a batch are validated before files are written. The workflow independently checks original-file preservation, ledger history, output paths and the three-capture limit before opening a PR.

The synthetic live test checks two martial arts dictations and an instruction-injection example. Regression tests also cover absent technique notes, Single Leg X versus Single Leg, invented symptom descriptions, source uncertainty, and ambiguous body-part titles such as Knee and Elbow (which are not automatically linked to strikes). Whitespace at the edges of cleaned text may be trimmed; originals are still verbatim. This is not a guarantee of classification accuracy; human review remains essential.
