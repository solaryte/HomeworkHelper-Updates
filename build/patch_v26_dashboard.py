from pathlib import Path
p=Path("app/HomeworkHelper.py")
s=p.read_text(encoding="utf-8-sig")
s=s.replace('"window":"1120x720"','"window":"1280x760"')
s=s.replace('self.minsize(950,620)','self.minsize(1050,660)')
s=s.replace('self.side=tk.Frame(self.shell,width=232)','self.side=tk.Frame(self.shell,width=208)')
s=s.replace('self.logo=tk.Label(self.side,text="Homework\\nHelper",justify="center");self.logo.pack(pady=(0,34))','self.logo=tk.Label(self.side,text="Your study space",anchor="w");self.logo.pack(fill="x",padx=24,pady=(0,30))')
s=s.replace('self.top=tk.Frame(self.main,height=70)','self.top=tk.Frame(self.main,height=82)')
start=s.index('  h=self.frames["home"];self.hero_card=')
end=s.index('  a=self.frames["activity"];',start)
home='''  h=self.frames["home"]
  self.eyebrow=tk.Label(h,text="LET'S MAKE PROGRESS",anchor="w");self.eyebrow.pack(fill="x",padx=32,pady=(28,5))
  self.home_title=tk.Label(h,text="One question at a time.",anchor="w");self.home_title.pack(fill="x",padx=32,pady=(0,20))
  self.hero_card=RoundedCard(h,height=260);self.hero_card.pack(fill="x",padx=32,pady=(0,16));self.hero=self.hero_card.content
  self.card_caption=tk.Label(self.hero,text="CONNECTED STUDY WORKSPACE",anchor="w");self.card_caption.pack(fill="x",padx=24,pady=(22,12))
  self.welcome=tk.Label(self.hero,text="Homework Helper",anchor="w");self.welcome.pack(fill="x",padx=24,pady=(0,7))
  self.sub=tk.Label(self.hero,text="Open your Sparx browser, then start your study session.",anchor="w");self.sub.pack(fill="x",padx=24)
  self.actionrow=tk.Frame(self.hero);self.actionrow.pack(fill="x",padx=24,pady=(22,15))
  self.login=tk.Label(self.actionrow,text="↗  Open Sparx browser",cursor="hand2",padx=20,pady=13);self.login.pack(side="left",padx=(0,12));self.login.bind("<Button-1>",lambda e:self.command("LOGIN"))
  self.start=tk.Label(self.actionrow,text="▶  Start helper",cursor="hand2",padx=20,pady=13);self.start.pack(side="left");self.start.bind("<Button-1>",lambda e:self.toggle())
  self.hero_hint=tk.Label(self.hero,text="●  Live browser connection  •  Question progress is checked before moving on",anchor="w");self.hero_hint.pack(fill="x",padx=24,pady=(0,12))
  self.decor=tk.Canvas(h,height=108,highlightthickness=0,bd=0);self.decor.pack(fill="x",padx=32,pady=(0,10));self.decor.bind("<Configure>",lambda e:self.draw_decor())
  self.note_card=RoundedCard(h,height=105);self.note_card.pack(fill="x",padx=32,pady=(0,12));self.note=self.note_card.content
  self.notet=tk.Label(self.note,text="●   LIVE SESSION",anchor="w");self.notet.pack(fill="x",padx=24,pady=(17,7))
  self.noteb=tk.Label(self.note,text="Your browser, login and preferences stay saved between updates.",anchor="w");self.noteb.pack(fill="x",padx=24)
'''
s=s[:start]+home+s[end:]
s=s.replace('(("01  CONNECT","Open your browser"),("02  LEARN","Review each question"),("03  PROGRESS","Keep your session"))','(("01  READ","Question and screenshot"),("02  VERIFY","Check the reasoning"),("03  ACT","Submit and confirm"))')
s=s.replace('  self.actionrow.configure(bg=c["panel"]);self.welcome.configure','''  self.eyebrow.configure(bg=c["bg"],fg=c["accent"],font=(f,9,"bold"))
  self.home_title.configure(bg=c["bg"],fg=c["text"],font=(f,s+12,"bold"))
  self.card_caption.configure(bg=c["panel"],fg=c["muted"],font=(f,9,"bold"))
  self.hero_hint.configure(bg=c["panel"],fg=c["muted"],font=(f,9))
  self.actionrow.configure(bg=c["panel"]);self.welcome.configure''')
s=s.replace('  self.logo.configure(bg=c["side"],fg=c["text"],font=(f,17,"bold"))','  self.logo.configure(bg=c["side"],fg=c["text"],font=(f,12,"bold"))')
s=s.replace('for k,b in self.nav.items():b.configure(bg=c["accent"] if k==self.page else c["panel2"] if k==self._hover_nav else c["side"],fg="#10242b" if k==self.page else c["text"],font=(f,s,"bold"))','for k,b in self.nav.items():b.configure(bg=c["panel2"] if k==self.page else c["panel"] if k==self._hover_nav else c["side"],fg=c["accent"] if k==self.page else c["muted"],font=(f,s,"bold" if k==self.page else "normal"))')
s=s.replace('self.login.configure(bg=c["accent2"],fg="white",font=(f,s,"bold"))','self.login.configure(bg=c["panel2"],fg=c["text"],font=(f,s,"bold"))')
s=s.replace('THEMES={','''THEMES={
 "V26":{"Dark":{"bg":"#101019","side":"#15151f","panel":"#1b1a28","panel2":"#2b2541","log":"#0c0c14","accent":"#ad91fa","accent2":"#342d4c"},
        "Light":{"bg":"#f6f5fb","side":"#eeecf6","panel":"#ffffff","panel2":"#e8e1f7","log":"#ffffff","accent":"#8159cf","accent2":"#d7c8ee"}},
''',1)
s=s.replace('DEFAULT={"palette":"Teal"','DEFAULT={"palette":"V26"')
s=s.replace('super().__init__(); self.cfg=self.load_settings()','''super().__init__(); self.cfg=self.load_settings()
  if not self.cfg.get("v26_design_migrated"):
   self.cfg["palette"]="V26";self.cfg["mode"]="Dark";self.cfg["v26_design_migrated"]=True''')
p.write_text(s,encoding="utf-8")
print("v26 modern dashboard applied")
