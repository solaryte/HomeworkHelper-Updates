"""v26.2: a failed strict option match must not crash the solve loop.
Apply after patch_v26_equation_safety.py.
"""
from pathlib import Path

p = Path("app/sparx_engine.py")
s = p.read_text(encoding="utf-8-sig")
old = '''    _matched_option = (
        match_option(ans.get(_choice_id, ""), controls[0]["options"])
        if _choice_only and isinstance(ans, dict) else None
    )'''
new = '''    # Strict matching can reject ambiguous/stale options. Do not let that
    # exception terminate the entire engine during fast-path evaluation.
    _matched_option = None
    if _choice_only and isinstance(ans, dict):
        try:
            _matched_option = match_option(
                ans.get(_choice_id, ""), controls[0]["options"]
            )
        except (ValueError, TypeError, KeyError) as exc:
            print("CHOICE FAST PATH: unsafe option mapping; refusing shortcut:",
                  repr(exc), flush=True)
'''
assert s.count(old) == 1, "v26.2 choice hook changed; refusing patch"
p.write_text(s.replace(old, new), encoding="utf-8")
print("v26.2 safe choice-fast-path fallback installed")
