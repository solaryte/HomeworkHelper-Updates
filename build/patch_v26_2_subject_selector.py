"""v26.2: subject selector with isolated navigation.
Maths opens the requested site; automatic Maths solving remains disabled until
its distinct question handlers are implemented and verified.
Apply after v26 dashboard patch.
"""
from pathlib import Path
gui=Path("app/HomeworkHelper.py")
s=gui.read_text(encoding="utf-8-sig")
needle='self.login.bind("<Button-1>",lambda e:self.command("LOGIN"))'
assert s.count(needle)==1, "GUI login hook changed"
s=s.replace(needle,needle+'''
  self.sparx_subject=tk.StringVar(value="Science")
  self.subject_picker=tk.OptionMenu(self.actionrow,self.sparx_subject,"Science","Maths",
      command=lambda choice:self.select_sparx_subject(choice))
  self.subject_picker.pack(side="left",padx=(0,10))
''',1)
needle=' def toggle(self):'
assert s.count(needle)==1, "GUI toggle hook changed"
s=s.replace(needle,''' def select_sparx_subject(self,choice):
  # Switching sites must stop any active solve before browser navigation.
  self.want_running=False
  self.command("STOP")
  self.command("MODE_MATHS" if choice=="Maths" else "MODE_SCIENCE")
  self.command("LOGIN")
  self.start.config(text="▶  START HELPER")
  self.log.insert("end",f"Selected Sparx {choice}.\\n")
  self.log.see("end")

'''+needle,1)
gui.write_text(s,encoding="utf-8")

engine=Path("app/sparx_engine.py")
s=engine.read_text(encoding="utf-8-sig")
needle='state={"run":False,"shutdown":False,"login":False}'
assert s.count(needle)==1, "engine state hook changed"
s=s.replace(needle,'state={"run":False,"shutdown":False,"login":False,"subject":"science","switch":False}',1)
needle='            elif cmd=="LOGIN": state["login"]=True'
assert s.count(needle)==1, "engine command hook changed"
s=s.replace(needle,'''            elif cmd=="LOGIN": state["login"]=True
            elif cmd in ("MODE_SCIENCE","MODE_MATHS"):
                state["run"]=False
                state["subject"]="maths" if cmd=="MODE_MATHS" else "science"
                state["switch"]=True
                state["login"]=True''',1)
needle='                if state["login"]:\n                    state["login"]=False'
assert s.count(needle)==1, "login loop hook changed"
s=s.replace(needle,'''                if state["switch"]:
                    state["switch"]=False
                    target=("https://maths.sparx-learning.com/student/homework?pkg_type=homework"
                            if state["subject"]=="maths" else "https://science.sparx-learning.com/")
                    # Do not reuse a question tab from the other subject.
                    matches=[x for x in ctx.pages if not x.is_closed() and
                             (("maths.sparx-learning.com" if state["subject"]=="maths"
                               else "science.sparx-learning.com") in (x.url or ""))]
                    page=matches[-1] if matches else ctx.new_page()
                    try:
                        page.goto(target,wait_until="domcontentloaded",timeout=30000)
                        page.bring_to_front()
                        last_signature=None
                        print("STATUS|SUBJECT_"+state["subject"].upper(),flush=True)
                    except Exception as ex:
                        print("Subject navigation error:",repr(ex),flush=True)
                if state["subject"]=="maths" and state["run"]:
                    state["run"]=False
                    print("STATUS|MATHS_SOLVER_PENDING",flush=True)
                    print("Maths browser is available; automatic solving is disabled until Maths controls are tested.",flush=True)
                if state["login"]:
                    state["login"]=False''',1)
# Keep Maths isolated from every Science-specific navigation and recovery handler.
# The mode may open its site, but cannot touch a Maths question with Science logic.
needle='                # Utility overlays/dialogs are never solver states. Close them before any solver action.'
assert s.count(needle)==1, "main loop guard changed"
s=s.replace(needle,'''                if state["subject"]=="maths":
                    # Maths question controls require a separate, tested adapter.
                    # Never run Science overlays, correction flows, or navigation.
                    if state["run"]:
                        state["run"]=False
                        print("STATUS|MATHS_SOLVER_PENDING",flush=True)
                    time.sleep(.25)
                    continue

'''+needle,1)
needle='                        candidates=[x for x in ctx.pages if "sparx-learning.com" in (x.url or "")]'
assert s.count(needle)==1, "login candidate hook changed"
s=s.replace(needle,'''                        domain="maths.sparx-learning.com" if state["subject"]=="maths" else "science.sparx-learning.com"
                        candidates=[x for x in ctx.pages if domain in (x.url or "")]''',1)
needle='                        if "sparx-learning.com" not in (page.url or ""):\n                            page.goto("https://science.sparx-learning.com/",wait_until="domcontentloaded",timeout=30000)'
assert s.count(needle)==1, "login URL hook changed"
s=s.replace(needle,'''                        if domain not in (page.url or ""):
                            target=("https://maths.sparx-learning.com/student/homework?pkg_type=homework"
                                    if state["subject"]=="maths" else "https://science.sparx-learning.com/")
                            page.goto(target,wait_until="domcontentloaded",timeout=30000)''',1)
engine.write_text(s,encoding="utf-8")
print("v26.2 subject selector installed")
