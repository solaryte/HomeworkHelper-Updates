"""Patch Homework Helper's extracted v25.40 engine for fast-first, deep-on-retry solving.
Fails closed if the expected source layout changes.
"""
from pathlib import Path
import os
import re

engine = Path("app/sparx_engine.py")
s = engine.read_text(encoding="utf-8-sig")
needle = '    fast_answer=None\n    if fast_answer:'
replacement = '''    # Fast first attempt: one visual solve only when all active controls are covered
    # and the model reports high confidence. Retry/feedback always receives full checks.
    try:
        _fast_confidence = float(r.get("confidence", 0) or 0)
    except (ValueError, TypeError):
        _fast_confidence = 0.0
    _retry_mode = bool(wrong or prior_feedback or visible_feedback)
    _complete = isinstance(ans, dict) and set(ans) == {c["id"] for c in controls}
    fast_answer = dict(ans) if (
        not _retry_mode and not teaching_ans and visual_primary and
        _complete and _fast_confidence >= 0.90 and
        all(str(v).strip() for v in ans.values())
    ) else None
    if fast_answer:
        print("SMART SPEED: high-confidence first attempt; skipping extra AI verifier calls.", flush=True)
    else:
        print("SMART SPEED: deep checks enabled (retry, uncertainty or missing controls).", flush=True)
    if fast_answer:'''
if s.count(needle) != 1:
    raise SystemExit("Expected first-attempt hook missing; refusing to publish.")
s = s.replace(needle, replacement)
# Preserve deterministic guards and choice mapping; skip only redundant AI calls.
# The existing solve() already uses fast_answer to skip verify_solution,
# feedback_compliance and deep_preflight.
s = re.sub(r'Homework Helper Engine v25\.\d+', 'Homework Helper Engine v25.41', s)
engine.write_text(s, encoding="utf-8")
print("Applied v25.41 fast-first/deep-on-retry patch")
