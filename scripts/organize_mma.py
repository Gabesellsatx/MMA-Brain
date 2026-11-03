#!/usr/bin/env python3
"""Conservative first-run processor. Does not modify Quick Capture.md."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INBOX = ROOT / 'MMA Brain/00 Inbox/Quick Capture.md'
TECHNIQUE = ROOT / 'MMA Brain/02 Techniques/Open Guard.md'
PROBLEMS = ROOT / 'MMA Brain/06 Problems/Problem Tracker.md'
LEDGER = ROOT / 'MMA Brain/00 Inbox/Processing Ledger.json'

OBSERVATION = ('Today in jujitsu, I practiced the Delahiva, and I was struggling '
               'with being able to off-balance in regular Delahiva and switch '
               'stances. The torque on my knee hurt.')

def main():
    raw = INBOX.read_bytes()
    if OBSERVATION not in raw.decode('utf-8'):
        raise SystemExit('Expected first-run observation missing; no changes made.')
    fingerprint = hashlib.sha256(OBSERVATION.encode('utf-8')).hexdigest()
    ledger = json.loads(LEDGER.read_text(encoding='utf-8')) if LEDGER.exists() else {'schema_version': 1, 'processed': []}
    if (not isinstance(ledger, dict) or ledger.get('schema_version') != 1
            or not isinstance(ledger.get('processed'), list)
            or not all(isinstance(item, dict) for item in ledger['processed'])):
        raise SystemExit('Unexpected processing ledger structure; no changes made.')
    if any(item.get('sha256') == fingerprint for item in ledger['processed']):
        print('Observation already processed; no changes.')
        return
    technique = TECHNIQUE.read_bytes().decode('utf-8')
    problem = PROBLEMS.read_bytes().decode('utf-8')
    if '### De La Riva guard — initial capture' in technique:
        raise SystemExit('Technique note already contains this capture; ledger not updated. Review manually.')
    if '## De La Riva capture' in problem:
        raise SystemExit('Problem tracker already contains this capture; review the ledger manually.')
    addition = '''\n### De La Riva guard — initial capture\n\n**Original observation (verbatim):**\n> ''' + OBSERVATION + '''\n\n**Cleaned observation (proposed; verify meaning):**\nToday in Brazilian Jiu-Jitsu, I practiced De La Riva guard. I struggled to off-balance my partner from regular De La Riva guard and to switch stances. The torque on my knee caused pain.\n\n**Needs review:** What did “switch stances” mean? Which knee hurt and during which movement? No grips, controls, or causes were specified. Do not force a painful movement.\n\n**Related:** [[Guard Retention]] · [[Base and Balance]]\n'''
    if '## My observations\n' not in technique:
        raise SystemExit('Unexpected Open Guard note structure; no changes made.')
    technique = technique.replace('## My observations\n', '## My observations\n' + addition, 1)
    problem_addition = '''\n- [[Open Guard]] — De La Riva: difficulty off-balancing and switching stances; knee pain with torque. **Unverified details:** movement, side, grips, and cause. See the initial capture in [[Open Guard]].\n'''
    if '## De La Riva capture' not in problem:
        problem += '\n## De La Riva capture\n' + problem_addition
    ledger['processed'].append({'sha256': fingerprint, 'source': 'MMA Brain/00 Inbox/Quick Capture.md', 'destination': 'MMA Brain/02 Techniques/Open Guard.md', 'status': 'proposed_for_review'})
    if INBOX.read_bytes() != raw:
        raise SystemExit('Inbox changed during processing; no changes made.')
    TECHNIQUE.write_text(technique, encoding='utf-8')
    PROBLEMS.write_text(problem, encoding='utf-8')
    LEDGER.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    if INBOX.read_bytes() != raw:
        raise SystemExit('Inbox must remain byte-for-byte unchanged.')
    print('Prepared one conservative observation for PR review; inbox unchanged.')

if __name__ == '__main__':
    main()
