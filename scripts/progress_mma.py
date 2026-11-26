#!/usr/bin/env python3
"""Deterministic, reviewable training evidence reports. No model-generated facts."""
import argparse
import hashlib
import json
import re
from collections import defaultdict
from datetime import date, datetime
from zoneinfo import ZoneInfo
from pathlib import Path
import organize_mma as m

BASE = 'MMA Brain/08 Progress'
OUT = BASE + '/Generated'
CORRECTIONS = BASE + '/Evidence Corrections.md'
MARKER = '<!-- mma-progress-generated:v1 -->'
CONTEXTS = {'unknown', 'study', 'drilling', 'positional', 'live', 'competition'}
RESISTING = {'positional', 'live', 'competition'}
STAGES = {'Unknown', 'Learning', 'Developing', 'Reliable', 'Advanced'}
FIELDS = {'Date', 'Context', 'Attempts', 'Successes', 'Problem', 'Diagnosis',
          'Adjustment', 'Retest', 'Issue status', 'Understanding', 'Variation',
          'Safety', 'Self assessment', 'Exclude', 'Skill'}
SPECIAL = {'De La Riva', 'Reverse De La Riva', 'Single Leg X', "D'Arce defense", 'Wrestling posture'}


def norm(s):
    s = m.copyedit(s).replace('’', "'")
    s = re.sub(r"\bd[’']?arce\b", 'darce', s, flags=re.I)
    return ' '.join(re.findall(r'\w+', s.casefold()))


def key(s):
    return hashlib.sha256(norm(s).encode()).hexdigest()[:16]


def esc(s):
    return m.plain(str(s)).replace('\n', '<br>')


def link(path, label=None):
    # Paths originate in the validated catalog or fixed generated paths.
    if re.search(r'[\[\]|\r\n]', path):
        raise ValueError('Unsafe link')
    return '[[' + path.removeprefix('MMA Brain/').removesuffix('.md') + ('|' + esc(label) if label else '') + ']]'


def skills(raw, catalog):
    # Shared canonical names prevent aliases from creating separate skill reports.
    base = m.recognized(raw, catalog)
    for name in sorted(SPECIAL):
        if re.search(r'(?<!\w)' + re.escape(norm(name)) + r'(?!\w)', norm(raw)):
            base.append(name)
    return list(dict.fromkeys(base))


def original(text):
    found = re.search(r'^## Original observation\n\n(`{3,})text\n(.*?)\n\1\n', text, re.M | re.S)
    if not found:
        raise ValueError('Capture has no intact original observation')
    return found[2]


def labelled(raw):
    # Only explicitly labelled facts are quantified. Unstructured speech is preserved.
    out = {}
    for part in re.split(r';|\n', raw):
        match = re.fullmatch(r'\s*([A-Za-z ]+):\s*(.*?)\s*', part)
        if match and match[1].lower() in {f.lower() for f in FIELDS}:
            name = next(f for f in FIELDS if f.lower() == match[1].lower())
            if name in out:
                raise ValueError('Duplicate evidence field: ' + name)
            out[name] = match[2]
    return out


def empty_record(name):
    r = {f: '' for f in FIELDS}
    r.update({'Skill': name, 'Context': 'unknown', 'Issue status': 'unknown',
              'Understanding': 'unknown', 'Safety': 'unknown', 'Exclude': 'no', 'Self assessment': 'Unknown'})
    return r


def validate(record, today):
    if not record['Skill'].strip() or len(record['Skill']) > 120 or re.search(r'[\[\]|\n\r]', record['Skill']):
        raise ValueError('Invalid skill name')
    if record['Date']:
        d = date.fromisoformat(record['Date'])
        if d > today:
            raise ValueError('Practice date is in the future')
    if record['Context'] not in CONTEXTS:
        raise ValueError('Invalid context')
    for f in ('Attempts', 'Successes'):
        v = record[f]
        if v != '' and (not re.fullmatch(r'\d+', v) or int(v) > 10000):
            raise ValueError('Invalid count: ' + f)
    a, s = record['Attempts'], record['Successes']
    if (a == '') != (s == '') or (a and (int(a) < 1 or int(s) > int(a))):
        raise ValueError('Counts require attempts > 0 and successes <= attempts')
    if record['Issue status'] not in ('unknown', 'open', 'testing', 'resolved'):
        raise ValueError('Invalid issue status')
    if record['Understanding'] not in ('unknown', 'demonstrated'):
        raise ValueError('Invalid understanding')
    if record['Safety'] not in ('unknown', 'concern', 'cleared') or record['Exclude'] not in ('no', 'yes'):
        raise ValueError('Invalid safety/exclusion')
    if record['Self assessment'] not in STAGES:
        raise ValueError('Invalid self assessment')
    for f in FIELDS:
        if len(record[f]) > 2000 or '\0' in record[f]:
            raise ValueError('Oversized evidence field')


def extract(root, today):
    catalog = m.catalog_from(root)
    records, unassigned = [], []
    ledger = m.read_ledger(root)
    # Only ledger-backed captures; never sweep the unprocessed inbox/backlog.
    for entry in ledger['processed']:
        text = m.safe_path(root, entry['destination']).read_text()
        raw = original(text)
        c = m.Capture(raw, 0)
        if entry['sha256'] not in (c.sha256, c.legacy_sha256):
            raise ValueError('Original capture does not match ledger fingerprint')
        unclear = bool(re.search(r'^kind: needs_context$', text, re.M))
        named = [] if unclear else skills(raw, catalog)
        raw_warning = ''
        try:
            fields = labelled(raw) if not unclear else {}
        except ValueError as error:
            fields = {}
            raw_warning = str(error)
        if fields.get('Skill'):
            named = [fields['Skill']]
        if not named:
            unassigned.append(entry['destination'])
        for name in named:
            r = empty_record(name)
            # One capture naming multiple skills cannot assign attempts/causes to any one.
            if len(named) == 1:
                r.update(fields)
                dates = set(re.findall(r'\b\d{4}-\d{2}-\d{2}\b', raw))
                if len(dates) == 1 and not r['Date']:
                    r['Date'] = dates.pop()
                if r['Context'] == 'unknown':
                    contexts = {context for pattern, context in [
                        (r'\b(?:live rolls?|live sparring)\b', 'live'),
                        (r'\bpositional (?:sparring|rounds?|drilling)\b', 'positional'),
                        (r'\b(?:cooperative drilling|unresisted drilling)\b', 'drilling'),
                        (r'\b(?:in competition|at a tournament)\b', 'competition')]
                        if re.search(pattern, raw, re.I)}
                    if len(contexts) == 1:
                        r['Context'] = contexts.pop()
                if not r['Attempts'] and not r['Successes']:
                    counts = re.findall(r'\b(?:completed|succeeded in|finished|landed) (\d+) (?:of|out of) (\d+) attempts\b', raw, re.I)
                    if len(counts) == 1 and not re.search(r'\b(?:not|never|almost|about|roughly|maybe)\b', raw, re.I):
                        r['Successes'], r['Attempts'] = counts[0]
                if not r['Problem']:
                    sentences = re.split(r'(?<=[.!?])\s+', raw)
                    difficulties = [sentence for sentence in sentences
                        if re.search(r"\b(?:struggling|difficulty|failed|lost|unable|couldn't)\b", sentence, re.I)
                        and not re.search(r"\b(?:not|never|no longer|didn't)\b", sentence, re.I)]
                    if difficulties:
                        r['Problem'] = ' '.join(difficulties)[:2000]
            if re.search(r'\b(pain|painful|hurt|hurts|injur\w*)\b|\bknee\b.{0,100}\bmesses up\b', raw, re.I):
                r['Safety'] = 'concern'
            try:
                validate(r, today)
            except ValueError as error:
                raw_warning = str(error)
            if raw_warning:
                # An invalid source fact must remain correctable without changing its source.
                safety = r['Safety'] if r['Safety'] == 'concern' else 'unknown'
                r = empty_record(name)
                r['Safety'] = safety
                try:
                    validate(r, today)
                except ValueError:
                    unassigned.append(entry['destination'])
                    continue
                r['raw_warning'] = raw_warning
            r.update(id=entry['sha256'] + ':' + key(name), source=entry['destination'], raw=raw,
                     shared=len(named) > 1, corrections=[])
            validate(r, today)
            records.append(r)
    return records, unassigned, catalog


def correct(root, records, today):
    path = m.safe_path(root, CORRECTIONS)
    if not path.exists():
        return records
    text = path.read_text()
    blocks = re.findall(r'^```mma-correction\n(.*?)\n```\s*$', text, re.M | re.S)
    if len(blocks) != text.count('```mma-correction'):
        raise ValueError('Unclosed correction block')
    lookup = {r['id']: r for r in records}
    if len(lookup) != len(records):
        raise ValueError('Duplicate evidence IDs')
    for number, block in enumerate(blocks, 1):
        fields = {}
        for line in block.splitlines():
            if not line.strip():
                continue
            f, sep, value = line.partition(':')
            if not sep or f in fields or f not in FIELDS | {'Evidence', 'Reason'}:
                raise ValueError('Invalid or duplicate correction field')
            fields[f] = value.strip()
        evidence = fields.pop('Evidence', '')
        reason = fields.pop('Reason', '')
        if evidence not in lookup or not reason or not fields:
            raise ValueError('Correction needs a valid Evidence ID, Reason, and fields')
        r = lookup[evidence]
        changes = {f: {'before': r[f], 'after': value} for f, value in fields.items()}
        r.update(fields)
        validate(r, today)
        r['corrections'].append({'number': number, 'reason': reason, 'changes': changes})
    return records


def assessment(records, today):
    dated = [r for r in records if r['Date']]
    measured = [r for r in dated if r['Attempts'] and r['Context'] in RESISTING]
    dates = sorted({r['Date'] for r in measured})
    attempts = sum(int(r['Attempts']) for r in measured)
    wins = sum(int(r['Successes']) for r in measured)
    understanding = any(r['Understanding'] == 'demonstrated' for r in records)
    execution = any(int(r['Successes']) > 0 for r in measured)
    consistency = len(dates) >= 3 and attempts >= 20 and wins / attempts >= .7
    variations = {norm(r['Variation']) for r in measured if r['Variation'] and int(r['Successes']) > 0}
    adaptation = len(variations) >= 2
    success_dates = sorted({r['Date'] for r in measured if int(r['Successes']) > 0})
    retention = len(success_dates) > 1 and (date.fromisoformat(success_dates[-1])-date.fromisoformat(success_dates[0])).days >= 14
    stage = 'Unknown'
    if any(r['Context'] in ('study', 'drilling') for r in dated) or understanding:
        stage = 'Learning'
    if execution:
        stage = 'Developing'
    if consistency and understanding:
        stage = 'Reliable'
    if stage == 'Reliable' and adaptation and retention:
        stage = 'Advanced'
    latest = max((r['Date'] for r in dated), default='')
    last_performance = max((r['Date'] for r in dated if r['Context'] != 'study'), default='')
    stale = bool(last_performance and (today - date.fromisoformat(last_performance)).days > 30)
    confidence = 'Low' if len(dates) < 3 else 'Moderate'
    if stale:
        confidence = 'Low — retest overdue'
    return dict(stage=stage, confidence=confidence, latest=latest, stale=stale,
                dimensions=dict(Understanding=understanding, Execution=execution, Consistency=consistency,
                                Adaptability=adaptation, Retention=retention), measured=measured,
                attempts=attempts, wins=wins)


def priority(records, a):
    # Undated concerns remain visible; never assume a newer unrelated note resolved them.
    if any(r['Safety'] == 'concern' for r in records):
        return 0, 'Review safety concern', 'Review the reported discomfort before selecting a physical drill. No resistance progression is proposed.'
    open_issues = [r for r in records if r['Problem'] and r['Issue status'] != 'resolved']
    if open_issues:
        return 1, 'Retest unresolved issue', 'Choose one unresolved problem below, record one adjustment, then log attempts and outcomes in a clearly identified context. This is a suggested evidence-gathering test, not a diagnosis.'
    if a['stale']:
        return 2, 'Check retention', 'Repeat a previously successful test with comparable conditions and log the result; the last dated practice was over 30 days ago.'
    if not a['measured']:
        return 3, 'Establish a baseline', 'Confirm the skill and actual practice date. Record context, attempts, successes, and what failed; choose suitable conditions with your coach.'
    return 4, 'Build comparable evidence', 'Repeat the same defined task and record attempts, successes, resistance context, and any variation. Compare like-for-like results below.'


def profile(name, records, catalog, today):
    a = assessment(records, today)
    rank, reason, goal = priority(records, a)
    report = OUT + '/Skills/' + key(name) + '.md'
    lines = [MARKER, '# ' + esc(name), '', '**Provisional evidence assessment: ' + a['stage'] + '**',
             'Evidence confidence: ' + a['confidence'] + '. This is a personal tracking rubric, not a belt rank or a validated mastery percentage.',
             '', 'Last dated practice: ' + (a['latest'] or 'Unknown') + '. Undated observations are listed separately and never ordered as sessions.',
             '', '## What do I know?', 'Existing knowledge notes:']
    matches = [p for p in catalog.values() if norm(Path(p).name) == norm(name)]
    if any(e['name'] == m.glossary.canonical(name) for e in m.glossary.ENTRIES):
        matches.append('11 Glossary/Master Glossary#' + m.glossary.canonical(name))
    lines += ['- ' + link(p) for p in matches] or ['- No exact knowledge-note match. Confirm the name; no substitute technique was linked.']
    lines += ['', '## What can I execute?', '| Dimension | Evidence |', '|---|---|']
    lines += [f'| {dim} | {"Threshold met" if yes else "Not established"} |' for dim, yes in a['dimensions'].items()]
    lines += ['', '## Outcomes by context', '| Context | Successes / attempts | Observed rate | Dated sessions |', '|---|---|---|---|']
    for context in ('drilling', 'positional', 'live', 'competition'):
        rows = [r for r in records if r['Context'] == context and r['Date'] and r['Attempts']]
        total = sum(int(r['Attempts']) for r in rows)
        wins = sum(int(r['Successes']) for r in rows)
        lines.append(f'| {context} | {str(wins)+" / "+str(total) if total else "Unknown"} | {str(round(100*wins/total))+"%" if total else "Unknown"} | {len({r["Date"] for r in rows})} |')
    lines += ['', 'Rates describe logged attempts only, not overall mastery. Different partners, tasks, and resistance can make comparisons invalid.',
              '', '## What should I practice next?', '**' + reason + '**', goal, '', '## Am I improving?',
              'Use the dated timeline to compare the same task and context. A reported improvement or a single successful retest does not automatically resolve an issue.',
              '', '| Date | Context | Attempts / successes | Observe | Diagnose (reported) | Correct | Retest | Issue status | Source |', '|---|---|---|---|---|---|---|---|---|']
    ordered = sorted(records, key=lambda r: (not bool(r['Date']), r['Date'], r['id']))
    for r in ordered:
        lines.append('| ' + ' | '.join([r['Date'] or 'Unknown', r['Context'], (r['Attempts']+' / '+r['Successes']) if r['Attempts'] else 'Unknown',
                     esc(r['Problem'] or 'See verbatim source'), esc(r['Diagnosis'] or 'Unknown'), esc(r['Adjustment'] or 'Unknown'),
                     esc(r['Retest'] or 'Unknown'), r['Issue status'], link(r['source'], 'Original')]) + ' |')
    lines += ['', '## Evidence and corrections']
    for r in ordered:
        lines += ['', '### Evidence ' + r['id'], 'Source: ' + link(r['source']),
                  'Shared capture: ' + ('yes — facts require per-skill confirmation' if r['shared'] else 'no'),
                  'Safety flag: ' + r['Safety'] + '. Self assessment: ' + r['Self assessment'] + ' (user supplied, separate from computed stage).',
                  '', '> ' + esc(r['raw']).rstrip().replace('<br>', '\n> '), '',
                  'To correct this evidence, append a block to ' + link(CORRECTIONS) + ' using this exact Evidence ID.']
        if r.get('raw_warning'):
            lines += ['Source validation: ' + esc(r['raw_warning']) + '. Automatically extracted facts were left unknown. Corrections below apply to those unknown values.']
        for correction in r['corrections']:
            lines += ['- Correction ' + str(correction['number']) + ': ' + esc(correction['reason'])]
            lines += ['  - ' + f + ': ' + esc(v['before'] or '(unknown)') + ' → ' + esc(v['after'] or '(unknown)') for f,v in correction['changes'].items()]
    lines += ['', '## Rubric', 'Learning: dated study/drilling or explicit demonstrated understanding. Developing: at least one dated success under resistance. Reliable: demonstrated understanding plus at least 20 measured attempts over three dates with at least 70% success under resistance. Advanced: Reliable plus successful evidence in two named variations and successes at least 14 days apart. These thresholds are configurable design choices, not scientific mastery claims. Confidence falls after 30 days without dated practice. Failure to meet a threshold means evidence is missing, not that you lack the skill.', '']
    return report, '\n'.join(lines), (rank, name, reason, goal, a, report)


def build(root, today):
    root = Path(root).resolve()
    records, unassigned, catalog = extract(root, today)
    records = correct(root, records, today)
    groups = defaultdict(list)
    canonical = {norm(name): name for name in sorted(SPECIAL | {Path(v).name for v in catalog.values()})}
    excluded = []
    for r in records:
        if r['Exclude'] == 'yes':
            excluded.append(r)
        else:
            canonical_name = m.glossary.canonical(r['Skill'])
            normalized = norm(canonical_name)
            canonical.setdefault(normalized, canonical_name)
            groups[canonical[normalized]].append(r)
    outputs, summaries = {}, []
    for name in sorted(groups):
        path, content, summary = profile(name, groups[name], catalog, today)
        outputs[path] = content
        summaries.append(summary)
    summaries.sort(key=lambda s: (s[0], s[1]))
    dashboard = OUT + '/Training Dashboard.md'
    lines = [MARKER, '# What should I train next?', '',
             'Built from ledger-backed capture proposals only. Includes provisional evidence; review before merging. The unprocessed inbox is not scored.',
             '', '## Next priorities', '| Skill | Next action | Stage | Confidence | Last dated practice |', '|---|---|---|---|---|']
    for _, name, reason, goal, a, path in summaries:
        lines.append('| ' + ' | '.join([link(path,name), reason, a['stage'], a['confidence'], a['latest'] or 'Unknown']) + ' |')
    lines += ['', '## Today’s review', 'Start with the first unresolved priority above. Safety concerns are review tasks, not physical drill recommendations. Unknown proficiency is intentional when dates and results are missing.',
              '', '## Capture → assess → correct → retest → retain',
              'Use ' + link(BASE + '/Progress Guide.md') + ' for a short dictation format and the rubric. Append factual corrections to ' + link(CORRECTIONS) + '. Reports and the linked canvas refresh together in the next review proposal.',
              '', '## Needs context', *['- ' + link(p) for p in unassigned],
              *(['- None.'] if not unassigned else []), '', '## Excluded evidence',
              *['- ' + r['id'] + ': ' + link(r['source']) + ' (see corrections)' for r in excluded],
              *(['- None.'] if not excluded else []), '', '## Scope',
              f'{len(records)} skill observations across {len(groups)} skill reports; {len(unassigned)} captures require context. No undated capture is assigned a processing date as its practice date.', '']
    outputs[dashboard] = '\n'.join(lines)
    nodes = [dict(id='dashboard', type='file', file=dashboard.removeprefix('MMA Brain/'), x=0,y=0,width=560,height=360)]
    edges = []
    for i, (_,name,reason,goal,a,path) in enumerate(summaries):
        node_id = 'skill-' + key(name)
        nodes.append(dict(id=node_id,type='file',file=path.removeprefix('MMA Brain/'),x=(i%3)*600,y=460+(i//3)*420,width=560,height=360,
                          color='1' if reason=='Review safety concern' else ('3' if a['stage']=='Unknown' else '4')))
        edges.append(dict(id='edge-'+key(name),fromNode='dashboard',toNode=node_id,label=reason))
    canvas = {'nodes':nodes,'edges':edges}
    ids = {n['id'] for n in nodes}
    assert len(ids) == len(nodes) and all(e['fromNode'] in ids and e['toNode'] in ids for e in edges)
    assert all('MMA Brain/'+n['file'] in outputs for n in nodes)
    outputs[OUT+'/Training Progress.canvas'] = json.dumps(canvas,indent=2)+'\n'
    outputs[OUT+'/Evidence.json'] = json.dumps({'schema_version':1,'records':records},indent=2,ensure_ascii=False,sort_keys=True)+'\n'
    # Retired reports keep valid links after a correction renames/excludes a skill.
    folder = m.safe_path(root, OUT+'/Skills')
    if folder.exists():
        for old in folder.glob('*.md'):
            rel = old.relative_to(root).as_posix()
            if rel not in outputs:
                outputs[rel] = MARKER+'\n# No active evidence\n\nThis report was superseded by corrections. See '+link(dashboard)+'.\n'
    return outputs


def apply(root, today, check=False):
    root = Path(root).resolve()
    outputs = build(root, today)
    manifest = OUT + '/Manifest.json'
    path = m.safe_path(root, manifest)
    previous = json.loads(path.read_text()) if path.exists() else {}
    if not isinstance(previous, dict):
        raise ValueError('Malformed output manifest')
    # Never overwrite hand edits, even inside generated files. Corrections live outside.
    for name, expected in previous.items():
        if not name.startswith(OUT+'/') or not re.fullmatch('[0-9a-f]{64}', expected):
            raise ValueError('Invalid manifest entry')
        p = m.safe_path(root, name)
        if not p.is_file() or m.digest(p.read_bytes()) != expected:
            raise ValueError('Generated output was edited; preserve the edit and move the intended correction to Evidence Corrections.md: '+name)
    for name in outputs:
        p = m.safe_path(root, name)
        if p.exists() and name not in previous:
            raise ValueError('Refusing to overwrite an unowned file: '+name)
    hashes = {name:m.digest(content.encode()) for name,content in outputs.items()}
    outputs[manifest] = json.dumps(hashes,indent=2,sort_keys=True)+'\n'
    changed = []
    for name, content in outputs.items():
        p = m.safe_path(root,name)
        if not p.exists() or p.read_bytes() != content.encode():
            changed.append(name)
    if check:
        return {'changed_paths': changed, 'reports': sum('/Skills/' in p for p in outputs)}
    for name in changed:
        p=m.safe_path(root,name);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(outputs[name].encode())
    return {'changed_paths':changed,'reports':sum('/Skills/' in p for p in outputs)}


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--date',default=datetime.now(ZoneInfo('America/Chicago')).date().isoformat(),help='As-of date, never used as an inferred practice date')
    parser.add_argument('--check',action='store_true',help='Validate without writing')
    args=parser.parse_args()
    result=apply(m.ROOT,date.fromisoformat(args.date),args.check)
    print(json.dumps(result,indent=2))
    if m.os.environ.get('GITHUB_OUTPUT'):
        with open(m.os.environ['GITHUB_OUTPUT'],'a') as stream:
            stream.write('changed='+str(bool(result['changed_paths'])).lower()+'\n')
