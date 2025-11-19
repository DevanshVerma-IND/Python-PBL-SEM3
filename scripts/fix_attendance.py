#!/usr/bin/env python3
import json
import os
from datetime import date

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'EduTrack-main'))

def load(fname, default=None):
    path = os.path.join(ROOT, fname)
    if not os.path.exists(path):
        return default
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save(fname, data):
    path = os.path.join(ROOT, fname)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def main():
    roll = load('rollnumbers.json', {})
    sections = load('sections.json', {})
    section_subjects = load('sectionsubjects.json', {})
    subjects = load('subjects.json', {}).get('subjects', [])
    studentsubjects = load('studentsubjects.json', {})
    am = load('attendance_master.json', {'attendance_records': {}, 'metadata': {}})

    # build name lookup: roll -> name (first matching key)
    name_for_roll = {}
    for k, v in roll.get('map', {}).get('student', {}).items():
        name_for_roll[v] = k

    # build subject name -> code map
    name_to_code = {s.get('name'): s.get('code') for s in subjects if isinstance(s, dict)}

    updated = 0
    added = 0
    today = date.today().isoformat()

    records = am.setdefault('attendance_records', {})

    for r, name_key in name_for_roll.items():
        if r in records:
            # correct name if stored as roll or differs
            rec = records[r]
            desired_name = name_key.title() if name_key and not name_key.isdigit() else r
            if rec.get('name') != desired_name:
                rec['name'] = desired_name
                updated += 1
            continue
        # create new attendance record for this roll
        sec = sections.get(r, 'Not assigned')
        subj_list = section_subjects.get(sec, None)
        if not subj_list:
            # fallback to student-specific subjects
            st = studentsubjects.get(r, {})
            subj_list = st.get('subjects') if isinstance(st, dict) else None
        if not subj_list:
            # fallback: use all subject names (first 5) to avoid huge lists
            subj_list = [s.get('name') for s in subjects[:5]]
        subjects_dict = {}
        for sname in subj_list:
            code = name_to_code.get(sname) or sname.upper().replace(' ', '_')
            subjects_dict[code] = {
                'subject_name': sname,
                'total_working_days': 0,
                'total_present_days': 0,
                'attendance_percentage': 0.0,
                'last_updated': today
            }
        display_name = name_key.title() if name_key and not name_key.isdigit() else r
        records[r] = {
            'name': display_name,
            'section': sec,
            'subjects': subjects_dict
        }
        added += 1

    if added or updated:
        # update metadata
        md = am.setdefault('metadata', {})
        md['last_updated'] = today
        md['total_students'] = len(records)
        save('attendance_master.json', am)

    print(f'Attendance updated: {updated} names corrected, {added} records added.')

if __name__ == '__main__':
    main()
