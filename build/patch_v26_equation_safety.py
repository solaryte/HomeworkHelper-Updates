"""v26.1 safety: exact mathematical choice mapping, no fuzzy equation fallback.
Never substitute a different displayed equation when the intended answer is absent.
"""
from pathlib import Path
p=Path("app/sparx_engine.py")
s=p.read_text(encoding="utf-8-sig")
needle="def match_option("
assert s.count(needle)==1, "match_option definition missing"
# Rename existing fuzzy resolver, then provide a strict maths resolver.
s=s.replace(needle,"def _hh_legacy_match_option(",1)
strict=r'''
def _hh_math_normalise(value):
    import re
    x=str(value or "").strip()
    x=x.replace("−","-").replace("×",r"\times").replace("÷",r"\div")
    x=re.sub(r"\\(?:left|right)\b","",x)
    x=re.sub(r"\\(?:mathrm|text)\s*\{([^{}]*)\}",r"\1",x)
    x=re.sub(r"\{([A-Za-z0-9]+)\}",r"\1",x)
    x=re.sub(r"\s+","",x)
    return x

def _hh_is_equation(value):
    x=str(value or "")
    return ("=" in x or r"\frac" in x or r"\times" in x
            or "R_" in x or "R{" in x)

def match_option(answer, options):
    # Equation cards must match uniquely and exactly after harmless formatting
    # normalisation. Never use approximate text matching for mathematics.
    if _hh_is_equation(answer) or any(_hh_is_equation(o) for o in options):
        target=_hh_math_normalise(answer)
        matches=[o for o in options if _hh_math_normalise(o)==target]
        if len(matches)!=1:
            print("EQUATION SAFETY: no unique exact equation match; stopping this attempt.",flush=True)
            raise ValueError("Unsafe equation choice mapping: no unique exact match")
        return matches[0]
    return _hh_legacy_match_option(answer,options)

'''
s=s.replace("def _hh_legacy_match_option(",strict+"def _hh_legacy_match_option(",1)
# Existing v25.46 shortcut is only safe when matching is exact; strict match
# applies in both the shortcut and final interaction paths.
p.write_text(s,encoding="utf-8")
print("Exact equation mapping safety guard applied")
