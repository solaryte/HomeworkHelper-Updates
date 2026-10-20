"""v26.2: collect accessible popup choices and select them by role first."""
from pathlib import Path
p=Path("app/sparx_engine.py")
s=p.read_text(encoding="utf-8-sig")
old='''    page.mouse.click(b["x"]+b["w"]/2,b["y"]+b["h"]/2);time.sleep(.15)
    vals=[]'''
new='''    page.mouse.click(b["x"]+b["w"]/2,b["y"]+b["h"]/2);time.sleep(.2)
    vals=[]
    # Some options repeat text already visible in the question, so a
    # text-difference scan alone can miss them.
    for selector in ('[role="option"]','[role="listbox"] [role="button"]'):
        try:
            for el in page.locator(selector).all():
                if el.is_visible():
                    t=el.inner_text(timeout=400).strip()
                    if t and len(t)<100: vals.append(t)
        except Exception: pass
    if not vals:'''
assert s.count(old)==1,"popup hook changed"
s=s.replace(old,new,1)
old='''        page.mouse.click(b["x"]+b["w"]/2,b["y"]+b["h"]/2);time.sleep(.1)
        if not click_text(page,val):page.keyboard.press("Escape");return False'''
new='''        page.mouse.click(b["x"]+b["w"]/2,b["y"]+b["h"]/2);time.sleep(.2)
        clicked=False
        for role in ("option","menuitem"):
            try:
                options=page.get_by_role(role,name=str(val),exact=True)
                for j in range(min(options.count(),12)):
                    if options.nth(j).is_visible():
                        options.nth(j).click(timeout=1200)
                        clicked=True
                        break
            except Exception: pass
            if clicked: break
        if not clicked: clicked=click_text(page,val)
        if not clicked:
            page.keyboard.press("Escape")
            print("Dropdown option not selected:",repr(val),flush=True)
            return False'''
assert s.count(old)==1,"dropdown click hook changed"
s=s.replace(old,new,1)
p.write_text(s,encoding="utf-8")
print("v26.2 dropdown reliability patch installed")
