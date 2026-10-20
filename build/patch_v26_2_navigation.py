"""v26.2: conservative completed-table navigation and ordering safety.
Applied to extracted engine after existing v26 patches.
"""
from pathlib import Path
p=Path("app/sparx_engine.py")
s=p.read_text(encoding="utf-8-sig")

needle='def confirmed_result_ready_for_next(page):'
assert s.count(needle)==1, "completion hook missing"
helper=r'''
def _hh_completed_table_ready(page):
    """A fully green-marked matrix with a visible enabled Next control."""
    try:
        return bool(page.evaluate("""() => {
          const next=[...document.querySelectorAll('button,[role="button"],a')]
            .find(e=>/^next(?: question)?$/i.test((e.innerText||e.textContent||'').trim())
              && !e.disabled && e.getBoundingClientRect().width>0);
          if(!next) return false;
          const tables=[...document.querySelectorAll('table')];
          return tables.some(t=>{
            const rows=[...t.querySelectorAll('tr')].filter(r=>r.querySelectorAll('td').length>=2);
            if(rows.length<2) return false;
            return rows.every(r=>{
              const text=(r.innerText||'').toLowerCase();
              const green=[...r.querySelectorAll('*')].filter(e=>{
                const c=getComputedStyle(e).color;
                return /rgb\\((?:0, ?(?:1[3-9]\\d|2\\d\\d)|(?:1[0-4]\\d), ?(?:1[2-9]\\d|2\\d\\d))/.test(c);
              });
              const checked=r.querySelector('input:checked,[aria-checked="true"]');
              return !!checked && green.length>0;
            });
          });
        }"""))
    except Exception:
        return False

def _hh_is_ordering_question(page):
    """Recognise up/down reorder controls; never treat rows as MCQ options."""
    try:
        txt=question_text(page).lower()
        if not any(x in txt for x in ("order the statements","put the statements in order",
                                       "correct order","rearrange the")):
            return False
        return bool(page.evaluate("""() => {
          const labels=[...document.querySelectorAll('button,[role="button"],[aria-label], [title]')]
            .map(e=>((e.getAttribute('aria-label')||e.getAttribute('title')||e.innerText||'')+'').trim().toLowerCase());
          return labels.some(x=>/^(move )?up$/.test(x)||/move.*up/.test(x))
              && labels.some(x=>/^(move )?down$/.test(x)||/move.*down/.test(x));
        }"""))
    except Exception:
        return False

'''
s=s.replace(needle,helper+needle,1)
needle='    if current_attempt_rejected(page):\n        return False\n    grade=match_grade_feedback(page)'
assert s.count(needle)==1,"completion guard changed"
s=s.replace(needle,'''    if current_attempt_rejected(page):
        return False
    if _hh_completed_table_ready(page):
        print("COMPLETION GATE: green-marked table with Next available.",flush=True)
        return True
    grade=match_grade_feedback(page)''',1)
needle='    ins=get_inputs(page); rows=choices(page); sels=native_selects(page); ds=dashed(page)'
assert s.count(needle)==1,"solve controls hook changed"
s=s.replace(needle,'''    if _hh_is_ordering_question(page):
        print("STATUS|ORDERING_UNSUPPORTED",flush=True)
        print("ORDERING SAFETY: up/down reorder question detected; refusing to misclick a statement as a multiple-choice answer.",flush=True)
        return False
'''+needle,1)
p.write_text(s,encoding="utf-8")
print("v26.2 navigation guard installed")
