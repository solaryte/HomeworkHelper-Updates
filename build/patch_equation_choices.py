"""Recognise Sparx maths choice cards built from clickable non-button elements.
Only includes visible maths cards with a clickable ancestor; preserves geometry click.
"""
from pathlib import Path
import re
p=Path("app/sparx_engine.py")
s=p.read_text(encoding="utf-8-sig")
old="const els=[...document.querySelectorAll('button,[role=\"button\"],label,[role=\"radio\"],[role=\"option\"],input[type=\"radio\"]')];"
new="""const base=[...document.querySelectorAll('button,[role="button"],label,[role="radio"],[role="option"],input[type="radio"]')];
      // Equation answer cards may be divs with click handlers and MathJax/KaTeX children.
      // Require mathematical content, a pointer cursor, and similarly shaped sibling cards.
      const extra=[...document.querySelectorAll('div,li')].filter(e=>{
        if(!e.querySelector('math,mjx-container,.katex')) return false;
        if(getComputedStyle(e).cursor!=='pointer') return false;
        const parent=e.parentElement;
        if(!parent) return false;
        const siblings=[...parent.children].filter(c=>c.tagName===e.tagName &&
          c.querySelector('math,mjx-container,.katex') && getComputedStyle(c).cursor==='pointer');
        if(siblings.length<2) return false;
        // Keep the smallest matching card to avoid selecting a whole answer row.
        if([...e.children].some(c=>c.querySelector('math,mjx-container,.katex') &&
          getComputedStyle(c).cursor==='pointer')) return false;
        return true;
      });
      const els=[...new Set([...base,...extra])];"""
assert s.count(old)==1, "choice selector hook missing"
s=s.replace(old,new)
# Extract TeX after the original visible label is computed, without assuming
# its exact whitespace-escaping representation in the source.
hook="        if(!t||t.length>260||bad.test(t)) continue;"
insertion="""        const tex=e.querySelector('annotation[encoding="application/x-tex"]');
        if(tex && tex.textContent.trim()) t=tex.textContent.trim();
"""
assert s.count(hook)==1, "choice label filter hook missing"
s=s.replace(hook,insertion+hook)
s=re.sub(r'Homework Helper Engine v25\\.\\d+', 'Homework Helper Engine v25.44', s)
p.write_text(s,encoding="utf-8")
print("Equation choice discovery patch installed")
