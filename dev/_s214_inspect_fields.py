import json

FILES = [
    '2026-09-04_s214_gold_expanded_resolved.json',
    '2026-09-04_s214_user_nine_questions.json',
    '2026-09-04_s214_user_nine_atomic_followups.json',
]
for f in FILES:
    d = json.load(open('dev/source/eval_runs/' + f))
    rs = d['results']
    keys = set()
    for r in rs:
        keys |= set(r.keys())
    print('==', f)
    print('   n =', len(rs), ' top-level:', [k for k in d if k != 'results'])
    print('   row keys:', sorted(keys))
    inner = set()
    for r in rs:
        for it in (r.get('results') or []):
            inner |= set(it.keys())
    if inner:
        print('   inner item keys:', sorted(inner))
    print()
