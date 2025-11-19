#!/usr/bin/env python3
import json,os
root = os.path.dirname(os.path.dirname(__file__))
rollf = os.path.join(root,'EduTrack-main','rollnumbers.json')
secf = os.path.join(root,'EduTrack-main','sectionlist.json')
studentsf = os.path.join(root,'EduTrack-main','studentsubjects.json')
backup = studentsf + '.bak'

with open(rollf) as f:
    rolldata = json.load(f)
student_map = rolldata.get('map',{}).get('student',{})
rolls = list(student_map.values())

with open(secf) as f:
    sections = json.load(f)
if not sections:
    raise SystemExit('no sections available')

if os.path.exists(studentsf):
    with open(studentsf) as f:
        sdata = json.load(f)
else:
    sdata = {}

# backup
with open(backup,'w') as f:
    json.dump(sdata,f,indent=2)

# assign round-robin
sections_cycle = sections
idx = 0
for r in sorted(rolls):
    if r in sdata and isinstance(sdata[r], dict) and sdata[r].get('section'):
        continue
    sec = sections_cycle[idx % len(sections_cycle)]
    # preserve existing subjects if any
    subjs = sdata.get(r,{}).get('subjects', []) if isinstance(sdata.get(r), dict) else []
    sdata[r] = {'section': sec, 'subjects': subjs}
    idx += 1

# write back
with open(studentsf,'w') as f:
    json.dump(sdata,f,indent=2)

print('assigned sections to', len(rolls), 'rolls, updated', studentsf)
print('backup saved to', backup)
