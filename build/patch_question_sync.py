"""Fail-closed question freshness guard for v25.42.
Run after Smart Speed patch. Refuse unknown source layouts.
"""
from pathlib import Path
import re
p=Path('app/sparx_engine.py')
s=p.read_text(encoding='utf-8-sig')
old='    qtext=active_question_text(page)[:15000]\n'
new='''    qtext=active_question_text(page)[:15000]
    # Capture the question BEFORE slow AI calls; Sparx may change question without changing URL.
    _hh_question_start=(page.url or "", qtext.strip())
    def _hh_question_is_current():
        try:
            current=(page.url or "", active_question_text(page)[:15000].strip())
            if current != _hh_question_start:
                print("QUESTION SYNC: active question changed while AI was thinking; discarding stale answer.", flush=True)
                return False
            return True
        except Exception as exc:
            print("QUESTION SYNC: could not verify active question:",repr(exc),flush=True)
            return False
'''
assert s.count(old)==1, 'qtext hook missing'
s=s.replace(old,new)
old='    # Canonicalise model answers to the exact text Sparx displays.\n'
new='''    if not _hh_question_is_current():
        return False

'''+old
assert s.count(old)==1,'canonical hook missing'
s=s.replace(old,new)
old='    LAST_ATTEMPT.clear()\n'
new='''    if not _hh_question_is_current():
        return False
    LAST_ATTEMPT.clear()
'''
assert s.count(old)==1,'interaction hook missing'
s=s.replace(old,new)
s=re.sub(r'Homework Helper Engine v25\.\d+', 'Homework Helper Engine v25.42', s)
p.write_text(s,encoding='utf-8')
print('QUESTION SYNC guard installed')
