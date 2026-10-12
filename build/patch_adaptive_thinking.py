"""Adaptive Qwen3-VL routing: fast instruct first, thinking model after rejection.
Fails closed on source drift. Applied after the existing v25.42 patches.
"""
from pathlib import Path
import re

p=Path("app/sparx_engine.py")
s=p.read_text(encoding="utf-8-sig")
old='MODEL=os.environ.get("HOMEWORK_HELPER_LOCAL_MODEL","qwen3-vl:8b"); API="http://127.0.0.1:11434/api/chat"'
new='''MODEL=os.environ.get("HOMEWORK_HELPER_LOCAL_MODEL","qwen3-vl:8b-instruct"); API="http://127.0.0.1:11434/api/chat"
DEEP_MODEL=os.environ.get("HOMEWORK_HELPER_DEEP_MODEL","qwen3-vl:8b")
_HH_RETRY_MODE=False'''
assert s.count(old)==1, "model declaration changed"
s=s.replace(old,new)
old='    data=json.dumps({"model":MODEL,"stream":False,"format":"json","messages":m,'
new='''    selected_model=DEEP_MODEL if _HH_RETRY_MODE else MODEL
    print("ADAPTIVE AI:", "deep retry" if _HH_RETRY_MODE else "fast first attempt", selected_model,flush=True)
    data=json.dumps({"model":selected_model,"stream":False,"format":"json","messages":m,'''
assert s.count(old)==1, "Ollama request changed"
s=s.replace(old,new)
old='def solve(page):\n    save_active_task(page)'
new='''def solve(page):
    global _HH_RETRY_MODE
    # Reset before any early helper calls to prevent leaking retry mode across questions.
    _HH_RETRY_MODE=False
    save_active_task(page)'''
assert s.count(old)==1, "solve entry changed"
s=s.replace(old,new)
old='    fp=qfingerprint(page)\n    wrong=KNOWN_WRONG.get(fp,[])\n    visual_primary=vision_first_plan(page,controls,shot,wrong)'
new='''    fp=qfingerprint(page)
    wrong=KNOWN_WRONG.get(fp,[])
    # Only use the thinking model when there is actual rejection/second-chance
    # feedback for this question. Uncertain first attempts stay on the fast model.
    _HH_RETRY_MODE=bool(wrong or visible_feedback or SPARX_FEEDBACK.get(feedback_key(page),""))
    visual_primary=vision_first_plan(page,controls,shot,wrong)'''
assert s.count(old)==1, "vision entry changed"
s=s.replace(old,new)
s=re.sub(r'Homework Helper Engine v25\.\d+', 'Homework Helper Engine v25.43', s)
p.write_text(s,encoding="utf-8")
print("Adaptive fast-first/deep-on-rejection routing installed")
