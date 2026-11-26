"""Shared, conservative terminology registry; no fuzzy guessing or proficiency claims."""
import re
from pathlib import Path

# Canonical names followed by unambiguous aliases. These are recognition vocabulary,
# not claims of technical equivalence across every ruleset or school.
GROUPS = {
'Brazilian Jiu-Jitsu': {
'Guard': 'Closed Guard|closed gaurd;Open Guard;Half Guard;Butterfly Guard;De La Riva|delahiva;Reverse De La Riva;Single Leg X|SLX;X Guard;Spider Guard;Lasso Guard;Collar Sleeve Guard;K Guard;Rubber Guard;Williams Guard;Shin to Shin Guard;Seated Guard;Deep Half Guard;Knee Shield;Z Guard;Octopus Guard;Worm Guard;Lapel Guard;50-50 Guard|50/50 guard;Inverted Guard',
'Passing': 'Knee Cut Pass|knee slice pass;Toreando Pass|bullfighter pass;Leg Drag Pass;Over Under Pass;Double Under Pass;Body Lock Pass;Stack Pass;Long Step Pass;Backstep Pass;Smash Pass;Headquarters Position;Leg Pummel;X Pass;Cartwheel Pass',
'Submission': "Armbar|arm bar;Kimura|kimora;Americana|keylock;Omoplata;Triangle Choke;Rear Naked Choke|RNC;Guillotine|guilitine;D'Arce Choke|darce|darce choke;Anaconda Choke;Arm Triangle|head and arm choke;North South Choke;Ezekiel Choke;Bow and Arrow Choke;Cross Collar Choke;Loop Choke;Baseball Bat Choke;Paper Cutter Choke;Straight Ankle Lock|straight foot lock;Heel Hook;Inside Heel Hook;Outside Heel Hook;Kneebar|knee bar;Toe Hold;Calf Slicer;Biceps Slicer;Wrist Lock;Gogoplata;Baratoplata;Tarikoplata;Estima Lock",
'Control': 'Side Control;Mount;Back Control;North South;Knee on Belly;Turtle Position;Seatbelt Grip;Gift Wrap;Crucifix;Ashi Garami|single leg ashi;Outside Ashi;Saddle|inside sankaku|411 position;Double Trouble;Knee Line Control;Hip Clamp;Truck Position',
'Sweep': 'Scissor Sweep;Hip Bump Sweep;Flower Sweep|pendulum sweep;Butterfly Sweep;Sickle Sweep;Tripod Sweep;Lumberjack Sweep;Waiter Sweep;Old School Sweep;Plan B Sweep;Electric Chair Sweep;John Wayne Sweep;Balloon Sweep;Technical Stand-Up Sweep',
'Escape and movement': "Hip Escape|shrimping;Bridge and Roll|upa escape;Elbow Knee Escape;Technical Stand-Up;Granby Roll;Guard Retention;Guard Recovery;Inversion;Back Escape;Side Control Escape;Mount Escape;Kipping Escape;Heel Slip;Boot Defense;Hand Fighting;D'Arce defense|darce defense;Berimbolo;Kiss of the Dragon;Wrestle Up"
},
'Wrestling': {
'Takedown': 'Single Leg|single leg takedown;Double Leg|double leg takedown;High Crotch;Low Single;Sweep Single;Snatch Single;Ankle Pick;Knee Pick;Duck Under;Arm Drag;Slide By;Snapdown|snap down;Fireman Carry;Lateral Drop;Body Lock Takedown;Inside Trip;Outside Trip;Mat Return;Blast Double;Run the Pipe;Cut the Corner;Shelf Finish',
'Control and defense': 'Wrestling posture;Level Change;Penetration Step;Sprawl;Whizzer|overhook;Underhook;Double Underhooks;Collar Tie;Two on One|Russian tie;Front Headlock;Quarter Nelson;Half Nelson;Full Nelson;Cradle;Crossface;Spiral Ride;Tight Waist;Ankle Ride;Leg Ride;Claw Ride;Wrist Ride;Arm Bar Ride;Stand-Up Escape;Sit Out;Switch Reversal;Peek Out;Hip Heist;Head Position;Pummeling'
},
'Judo': {
'Throw': 'De Ashi Barai|de ashi harai;Hiza Guruma;Sasae Tsurikomi Ashi;Uki Goshi;Osoto Gari|o soto gari;O Goshi;Ouchi Gari|o uchi gari;Seoi Nage;Ippon Seoi Nage;Morote Seoi Nage;Seoi Otoshi;Koshi Guruma;Tsurikomi Goshi;Okuri Ashi Harai;Tai Otoshi;Harai Goshi;Uchi Mata;Kosoto Gari;Kouchi Gari;Hane Goshi;Harai Tsurikomi Ashi;Tomoe Nage;Kata Guruma;Sumi Gaeshi;Tani Otoshi;Hane Makikomi;Sukui Nage;Utsuri Goshi;O Guruma;Soto Makikomi;Uki Otoshi;Osoto Guruma;Uki Waza;Yoko Wakare;Yoko Guruma;Ushiro Goshi;Ura Nage;Sumi Otoshi;Yoko Gake;Kibisu Gaeshi;Kuchiki Taoshi;Te Guruma;Obi Otoshi;Kouchi Makikomi;Daki Wakare;Yoko Tomoe Nage',
'Pin and foundation': 'Kesa Gatame;Kuzure Kesa Gatame;Yoko Shiho Gatame;Kami Shiho Gatame;Tate Shiho Gatame;Kata Gatame;Ushiro Kesa Gatame;Ukemi|breakfall;Ushiro Ukemi;Yoko Ukemi;Mae Ukemi;Mae Mawari Ukemi;Kuzushi|off balancing;Tsukuri;Kake;Kumi Kata|grip fighting'
},
'Boxing': {
'Punch': 'Jab|jab boxing;Cross (Boxing)|rear straight|cross boxing;Lead Hook;Rear Hook;Lead Uppercut;Rear Uppercut;Overhand Right;Overhand Left;Shovel Hook;Check Hook;Body Jab;Double Jab;One Two|jab cross combination',
'Defense and footwork': 'High Guard;Long Guard;Shoulder Roll;Slip;Pull Counter;Bob and Weave;Roll Under;Catch and Parry;Pivot;L Step;V Step;Step Drag;Pendulum Step;Angle Exit;Feint;Counter Jab;Catch and Shoot;Head Movement;Distance Management'
},
'Muay Thai': {
'Strike': 'Teep|push kick;Rear Teep;Lead Teep;Roundhouse Kick|round kick;Low Kick|leg kick;Body Kick;Head Kick;Switch Kick;Question Mark Kick;Horizontal Elbow;Diagonal Elbow;Upward Elbow;Spinning Elbow;Downward Elbow;Straight Knee;Diagonal Knee;Curved Knee;Flying Knee;Long Knee',
'Clinch and defense': 'Thai Plum|double collar tie;Single Collar Tie;Clinch Turn;Clinch Swim;Knee Shield Defense;Kick Check;Kick Catch;Kick Return;Teep Parry;Lean Back;Long Guard Frame;Clinch Off Balance'
},
'Kickboxing': {
'Strike and combination': 'Front Kick;Side Kick;Back Kick;Spinning Back Kick;Hook Kick;Spinning Hook Kick;Axe Kick;Crescent Kick;Inside Low Kick;Outside Low Kick;Calf Kick;Dutch Combination;Punch Kick Combination;Kick Punch Combination;Blitz Entry;Switch Step;Cut Kick'
},
'MMA': {
'Integration': 'Cage Wrestling;Wall Walk;Wall Pin;Fence Turn;Wall Takedown;Wall Get-Up;Ground and Pound;Posture Control;Wrist Pin;Dagestani Handcuff;Strike to Shot;Shot to Strike;Sprawl and Brawl;Cage Cut-Off;Standing Guard Pass;Combat Base;Safe Ground Disengagement;Submission to Takedown Chain'
},
'Strength and Conditioning': {
'Movement': 'Back Squat;Front Squat;Goblet Squat;Split Squat;Reverse Lunge;Deadlift;Romanian Deadlift;Trap Bar Deadlift;Hip Thrust;Pull-Up;Chin-Up;Push-Up;Bench Press;Overhead Press;Bent Over Row;Farmer Carry;Suitcase Carry;Turkish Get-Up;Kettlebell Swing;Medicine Ball Throw;Box Jump;Broad Jump;Sled Push;Sled Pull;Pallof Press;Side Plank;Dead Bug;Bird Dog;Aerobic Base Training;Sprint Interval;Isometric Hold'
},
'Mobility': {
'Movement': 'Hip CARs;Shoulder CARs;90-90 Hip Switch;Ankle Dorsiflexion;Thoracic Rotation;Deep Squat Hold;Cossack Squat;Adductor Rockback;Wrist Mobility;Scapular Push-Up;Cat Cow;Controlled Articular Rotation'
},
'Physical Therapy': {
'Logging concept': 'Symptom Tracking;Range of Motion;Load Tolerance;Return to Sport;Rehabilitation Adherence;Pain Response;Exercise Modification;Clinician Clearance'
}}
SOURCES = {
'Brazilian Jiu-Jitsu': ('https://ibjjf.com/books-videos', 'Rules and terminology context; not a complete technique curriculum.'),
'Wrestling': ('https://www.usawmembership.com/usa_wrestling_core_curriculum/1', 'USA Wrestling core curriculum.'),
'Judo': ('https://judo.ijf.org/', 'IJF technique catalogue; names may use different romanization.'),
'Boxing': ('https://www.englandboxing.org/rules-regs-resources/forms-and-resources/', 'Coaching and rules resources.'),
'Muay Thai': ('https://muaythai.sport/about-muaythai/muaythai-rules/', 'Rules and discipline context.'),
'Kickboxing': ('https://www.wako.sport/rules-overview', 'Rules and discipline context.'),
'MMA': ('https://immaf.org/get-involved/participant-pathways/', 'Participant pathway; full technical syllabus is not reproduced.'),
'Strength and Conditioning': ('', 'Vocabulary draft; coach review pending, no exercise prescription.'),
'Mobility': ('', 'Vocabulary draft; coach review pending, no exercise prescription.'),
'Physical Therapy': ('', 'Logging vocabulary only; clinician review required for rehabilitation decisions.')}
# Explicitly uncertain sound-alikes are review suggestions, NEVER substitutions.
REVIEW = {'dad lava': 'De La Riva', 'de la ava': 'De La Riva', 'reverse lava': 'Reverse De La Riva',
          'ex guard': 'X Guard', 'hieu hook': 'Heel Hook', 'hill hook': 'Heel Hook',
          'doris': "D'Arce Choke", 'doors': "D'Arce Choke", 'society': 'Sasae Tsurikomi Ashi'}
PREREQUISITES = {
'Guard': ['Hip Escape', 'Guard Retention'], 'Passing': ['Posture Control', 'Combat Base'],
'Submission': ['Posture Control', 'Hand Fighting'], 'Control': ['Posture Control'],
'Sweep': ['Kuzushi', 'Guard Retention'], 'Escape and movement': ['Hip Escape'],
'Takedown': ['Wrestling posture', 'Level Change'], 'Control and defense': ['Wrestling posture'],
'Throw': ['Ukemi', 'Kuzushi', 'Tsukuri'], 'Pin and foundation': ['Ukemi'],
'Punch': ['Distance Management'], 'Defense and footwork': ['Distance Management'],
'Strike': ['Distance Management'], 'Clinch and defense': ['Pummeling'],
'Strike and combination': ['Distance Management'], 'Integration': ['Posture Control', 'Head Position'],
'Movement': [], 'Logging concept': []}
RELATIONS = {'Single Leg X': ['X Guard', 'Ashi Garami'], 'Reverse De La Riva': ['De La Riva', 'Kiss of the Dragon'],
             "D'Arce Choke": ["D'Arce defense", 'Front Headlock', 'Anaconda Choke'],
             'Heel Hook': ['Inside Heel Hook', 'Outside Heel Hook', 'Knee Line Control'],
             'Half Guard': ['Knee Shield', 'Deep Half Guard', 'Knee Cut Pass'],
             'Single Leg': ['Run the Pipe', 'Whizzer', 'Sprawl'], 'Jab': ['Cross (Boxing)', 'Double Jab']}

def norm(s):
    return ' '.join(re.findall(r'\w+', s.casefold().replace('’', "'")))

ENTRIES = []
for art, categories in GROUPS.items():
    for category, rows in categories.items():
        for row in rows.split(';'):
            name, *aliases = row.split('|')
            ENTRIES.append(dict(name=name, aliases=aliases, art=art, category=category,
                prerequisites=[p for p in PREREQUISITES[category] if p != name], related=RELATIONS.get(name, [])))

# Only explicit phrases, longest match first. Ambiguous generic vocabulary does
# not automatically become technique evidence without a labelled Skill field.
AMBIGUOUS = {'slip', 'pivot', 'feint', 'switch reversal', 'inversion', 'range of motion', 'pain response', 'head movement'}

def canonical(name):
    targets = {e['name'] for e in ENTRIES if norm(name) in [norm(e['name']), *map(norm, e['aliases'])]}
    return next(iter(targets)) if len(targets) == 1 else name

def mentions(raw, extra=()):
    text = norm(raw)
    spans = []
    for e in ENTRIES:
        for alias in [e['name'], *e['aliases']]:
            term = norm(alias)
            if term in AMBIGUOUS:
                continue
            spans.extend((m.start(), m.end(), e['name']) for m in re.finditer(r'(?<!\w)' + re.escape(term) + r'(?!\w)', text))
    for name in extra:
        spans.extend((m.start(), m.end(), canonical(name)) for m in re.finditer(r'(?<!\w)' + re.escape(norm(name)) + r'(?!\w)', text))
    longest = [m for m in spans if not any(n[0] <= m[0] and m[1] <= n[1] and n[1]-n[0] > m[1]-m[0] for n in spans)]
    return list(dict.fromkeys(m[2] for m in sorted(longest)))

def questions(raw):
    text = norm(raw)
    return [f'Confirm whether "{a}" means {b}; original wording is retained.' for a,b in REVIEW.items()
            if re.search(r'(?<!\w)' + re.escape(norm(a)) + r'(?!\w)', text)]

def link(name):
    return '[[11 Glossary/Master Glossary#' + name + '|' + name + ']]'

def render():
    out = ['# MMA Brain Master Glossary', '', f'{len(ENTRIES)} canonical entries across {len(GROUPS)} disciplines. A broad, expandable vocabulary, not every move ever named.', '',
           'Names and aliases support capture recognition and shared progress grouping. A mention is not evidence of successful execution. Original notes are never rewritten.', '',
           'Prerequisites below are suggested learning foundations, not mandatory gates or individualized coaching. Relationships are editorial suggestions. Source links are discipline reference starting points, not verification of every entry. Entries remain vocabulary drafts pending coach/source review. Physical therapy entries are logging concepts, not treatment instructions.', '',
           '## Transcription review', '', 'Uncertain sound-alikes are flagged for confirmation, never automatically replaced.', '']
    out += [f'- `{a}` → possible **{b}**' for a,b in REVIEW.items()]
    for art, cats in GROUPS.items():
        url, scope = SOURCES[art]
        out += ['', '## ' + art, '', (f'Reference: {url}. ' if url else '') + scope, '']
        for e in [e for e in ENTRIES if e['art'] == art]:
            out += ['### '+e['name'], '', f"Category: {e['category']}. Aliases: {', '.join(e['aliases']) or 'none registered'}.",
                    'Suggested foundations: ' + (', '.join(link(p) for p in e['prerequisites']) or 'individual coach/clinician assessment') + '.',
                    'Related: ' + (', '.join(link(p) for p in e['related']) or 'see discipline and category above') + '.', '']
    return '\n'.join(out)

if __name__ == '__main__':
    path = Path(__file__).resolve().parents[1] / 'MMA Brain/11 Glossary/Master Glossary.md'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render())
    print(f'{len(ENTRIES)} glossary entries')
