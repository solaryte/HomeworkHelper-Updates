"""v25.46: skip redundant AI verifier passes for grounded, high-confidence choice answers.
Only applies to a complete single choice control, never written/numeric answers.
Preserves deterministic canonicalisation, feedback rejection and question sync.
"""
from pathlib import Path
import re
p=Path("app/sparx_engine.py")
s=p.read_text(encoding="utf-8-sig")
old='''    fast_answer = dict(ans) if (
        not _retry_mode and not teaching_ans and visual_primary and
        _complete and _fast_confidence >= 0.90 and
        all(str(v).strip() for v in ans.values())
    ) else None'''
new='''    # A single high-confidence choice already has an explicit displayed option.
    # On retries, permit skipping duplicate AI passes only when the proposal is
    # not the previously rejected answer or a per-control rejected option.
    _choice_only = (
        len(controls) == 1 and controls[0].get("kind") == "choice" and
        len(controls[0].get("options", [])) >= 2
    )
    _choice_id = controls[0]["id"] if _choice_only else None
    _matched_option = (
        match_option(ans.get(_choice_id, ""), controls[0]["options"])
        if _choice_only and isinstance(ans, dict) else None
    )
    _rejected_choice = (
        any(isinstance(bad, dict) and
            canon(bad.get(_choice_id, "")) == canon(_matched_option)
            for bad in wrong)
        or canon(_matched_option) in WRONG_BY_CONTROL.get(fp, {}).get(_choice_id, set())
    ) if _matched_option else True
    _grounded_choice = bool(
        _choice_only and _matched_option and not _rejected_choice and
        _fast_confidence >= 0.90 and visual_primary
    )
    fast_answer = dict(ans) if (
        not teaching_ans and _complete and
        all(str(v).strip() for v in ans.values()) and
        (_grounded_choice or (not _retry_mode and visual_primary and
         _fast_confidence >= 0.90))
    ) else None
    if _grounded_choice:
        print("CHOICE FAST PATH: matched displayed option; skipping duplicate AI verification.",flush=True)'''
assert s.count(old)==1, "Smart Speed block changed; refusing unsafe release"
s=s.replace(old,new)
s=re.sub(r'Homework Helper Engine v25\.\d+', 'Homework Helper Engine v25.46', s)
p.write_text(s,encoding="utf-8")
print("v25.46 high-confidence choice fast path installed")
