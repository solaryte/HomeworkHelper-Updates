"""v25.45: Preserve mathematical option identity and abort stale solves early.
Applied after v25.44; assertions deliberately stop release on source drift.
"""
from pathlib import Path
import re
p=Path("app/sparx_engine.py")
s=p.read_text(encoding="utf-8-sig")
# Existing v25.44 adds a TeX annotation lookup. Keep it, but prevent a wrong
# card from being clicked when the page has changed during slow inference.
needle='    visual_primary=vision_first_plan(page,controls,shot,wrong)\n'
replacement='''    # Snapshot question identity before vision inference. The URL alone is not enough.
    _hh_solve_identity=(page.url or "", qfingerprint(page))
    def _hh_still_same_question():
        try:
            return (page.url or "", qfingerprint(page)) == _hh_solve_identity
        except Exception:
            return False
    visual_primary=vision_first_plan(page,controls,shot,wrong)
    if not _hh_still_same_question():
        print("QUESTION CHANGED: discarding previous question's vision result.",flush=True)
        return False
'''
assert s.count(needle)==1, "vision checkpoint hook missing"
s=s.replace(needle,replacement)
# Abort before any answer interaction (v25.42 guard already exists), and
# protect the direct-choice click from a manual tab switch.
needle='    for i,g in enumerate(rows):\n        val=ans[f"C{i+1}"]'
replacement='''    if not _hh_still_same_question():
        print("QUESTION CHANGED: cancelling stale choice interaction.",flush=True)
        return False
    for i,g in enumerate(rows):
        if not _hh_still_same_question():
            print("QUESTION CHANGED: stopping stale choice click.",flush=True)
            return False
        val=ans[f"C{i+1}"]'''
assert s.count(needle)==1, "choice interaction hook missing"
s=s.replace(needle,replacement)
# Protect against the previous question carrying a stale retry flag into a
# different page. The earlier adaptive patch resets on solve entry.
s=re.sub(r'Homework Helper Engine v25\.\d+', 'Homework Helper Engine v25.45', s)
p.write_text(s,encoding="utf-8")
print("v25.45 stale-question cancellation installed")
