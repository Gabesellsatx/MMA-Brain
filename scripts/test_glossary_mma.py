import unittest
import tempfile
import shutil
from pathlib import Path
from datetime import date
import glossary_mma as g
import organize_mma as m
import progress_mma as p

class GlossaryTests(unittest.TestCase):
    def test_registry_integrity(self):
        names = [e['name'] for e in g.ENTRIES]
        self.assertEqual(len(names), len(set(names)))
        self.assertGreater(len(names), 350)
        for e in g.ENTRIES:
            for target in e['related'] + e['prerequisites']:
                self.assertIn(target, names)
        aliases = {}
        for e in g.ENTRIES:
            for alias in [e['name'], *e['aliases']]:
                key = g.norm(alias)
                self.assertIn(aliases.get(key, e['name']), [e['name']])
                aliases[key] = e['name']
    def test_longest_and_separate_mentions(self):
        self.assertEqual(g.mentions('reverse de la riva'), ['Reverse De La Riva'])
        self.assertEqual(g.mentions('single leg x then single leg'), ['Single Leg X', 'Single Leg'])
    def test_aliases_group_without_rewriting_source(self):
        self.assertEqual(g.canonical('RNC'), 'Rear Naked Choke')
        self.assertEqual(p.skills('SLX', {}), ['Single Leg X'])
        self.assertEqual(p.skills('Darce', {}), ["D'Arce Choke"])
    def test_soundalikes_are_questions(self):
        raw = 'My dad lava and Doris and society'
        self.assertEqual(g.mentions(raw), [])
        self.assertEqual(len(g.questions(raw)), 3)
        self.assertEqual(m.copyedit(raw), raw)
    def test_no_injury_as_strike(self):
        self.assertEqual(g.mentions('My knee and elbow hurt, my back is sore'), [])
    def test_pending_capture_classification(self):
        raw = 'reverse De La Ava into ex guard and heel hook'
        data = m.classify_local(raw, {})
        self.assertEqual(data['art'], 'Brazilian Jiu-Jitsu')
        self.assertIn('Heel Hook', p.skills(raw, {}))
        self.assertNotIn('Reverse De La Riva', p.skills(raw, {}))
    def test_local_end_to_end_preserves_originals_and_repeat(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inbox = root / m.INBOX
            inbox.parent.mkdir(parents=True)
            inbox.write_text('Date: 2026-11-20; Skill: RNC; Context: live; Attempts: 5; Successes: 2\nMy single leg X feels weak\nHey Siri add to notes\n')
            before = inbox.read_bytes()
            result = m.verified_apply(root, model=m.classify_local)
            self.assertEqual(result['processed'], 3)
            self.assertEqual(inbox.read_bytes(), before)
            outputs = p.build(root, date(2026,11,26))
            self.assertIn('Rear Naked Choke', str(outputs))
            self.assertIn('Single Leg X', str(outputs))
            self.assertEqual(m.verified_apply(root, model=m.classify_local)['processed'], 0)
    def test_render_is_current(self):
        path = Path(__file__).resolve().parents[1] / 'MMA Brain/11 Glossary/Master Glossary.md'
        self.assertEqual(path.read_text(), g.render())

if __name__ == '__main__':
    unittest.main()
