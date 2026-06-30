# -*- coding: utf-8 -*-
"""aurora-neon-glow HTML 슬라이드 생성기 (slides-grab용). 실행: python build.py"""
import os, html
HERE = os.path.dirname(os.path.abspath(__file__))

GREEN, CYAN, VIOLET = "#00FF88", "#00B4FF", "#7B00FF"

CSS = """
* { margin:0; padding:0; box-sizing:border-box; }
body { width:720pt; height:405pt; font-family:'Pretendard',sans-serif; background:#050510; color:#D0D0F0; position:relative; overflow:hidden; }
.bg { position:absolute; inset:0; overflow:hidden; z-index:0; }
.blob { position:absolute; border-radius:50%; }
.b1 { width:160pt; height:160pt; background:#00FF88; top:0; left:0; opacity:.16; filter:blur(58pt); }
.b2 { width:200pt; height:200pt; background:#7B00FF; bottom:0; right:0; opacity:.22; filter:blur(60pt); }
.b3 { width:120pt; height:120pt; background:#00B4FF; top:18pt; right:150pt; opacity:.13; filter:blur(55pt); }
.scan { position:absolute; inset:0; background:repeating-linear-gradient(0deg, rgba(255,255,255,.035) 0, rgba(255,255,255,.035) 1px, transparent 1px, transparent 4px); opacity:.5; }
.frame { position:absolute; inset:0; z-index:2; padding:34pt 48pt; display:flex; flex-direction:column; }
.pagenum { position:absolute; right:22pt; bottom:14pt; z-index:3; font-size:10pt; color:#3c3c55; }
.kicker { font-size:12pt; font-weight:700; letter-spacing:2pt; color:#00B4FF; }
.h1 { font-size:30pt; font-weight:800; color:#fff; margin-top:3pt; line-height:1.18; }
.rule { width:78pt; height:3pt; border-radius:2pt; background:linear-gradient(90deg,#00FF88,#00B4FF); box-shadow:0 0 12pt #00B4FF; margin-top:10pt; }
.grad { background:linear-gradient(100deg,#00FF88,#00B4FF 50%,#7B00FF); -webkit-background-clip:text; background-clip:text; color:transparent; }
/* cover */
.cv-title { font-size:84pt; font-weight:800; line-height:1.02; letter-spacing:-1pt; margin-top:12pt; }
.cv-sub { font-size:21pt; font-weight:600; color:#9fe7ff; margin-top:14pt; }
.cv-kick { font-size:12pt; font-weight:700; letter-spacing:3pt; color:#00B4FF; }
.cv-foot { position:absolute; left:54pt; bottom:30pt; z-index:2; font-size:12.5pt; color:#6b6b8c; }
.dot { position:absolute; width:15pt; height:15pt; border-radius:50%; background:#00FF88; box-shadow:0 0 22pt 4pt #00FF88; z-index:2; }
/* section */
.sec-num { font-size:150pt; font-weight:800; line-height:1; color:rgba(255,255,255,.05); position:absolute; right:40pt; top:60pt; z-index:1; }
.sec-kick { font-size:18pt; font-weight:700; letter-spacing:3pt; }
.sec-title { font-size:48pt; font-weight:800; color:#fff; margin-top:8pt; }
.sec-sub { font-size:16pt; color:#9aa0c0; margin-top:14pt; }
/* statement */
.st-big { font-size:40pt; font-weight:800; line-height:1.2; text-align:center; }
.st-small { font-size:18pt; color:#9aa0c0; text-align:center; margin-top:20pt; }
/* bullets */
.li { font-size:16.5pt; line-height:1.5; margin-bottom:12pt; padding-left:20pt; position:relative; color:#D8DCF0; }
.li::before { content:""; position:absolute; left:0; top:8pt; width:7pt; height:7pt; border-radius:50%; background:#00FF88; box-shadow:0 0 8pt #00FF88; }
.li.c::before { background:#00B4FF; box-shadow:0 0 8pt #00B4FF; }
.li.v::before { background:#7B00FF; box-shadow:0 0 8pt #7B00FF; }
.li .mute { color:#7d83a3; }
.li b { color:#fff; }
/* panels / category */
.cols { display:flex; gap:16pt; margin-top:20pt; flex:1; }
.panel { flex:1; background:rgba(255,255,255,.04); border:1px solid rgba(255,255,255,.10); border-radius:13pt; padding:16pt 18pt; }
.panel .lab { font-size:12pt; font-weight:800; letter-spacing:1pt; margin-bottom:11pt; }
.badge { width:38pt; height:38pt; border-radius:9pt; display:flex; align-items:center; justify-content:center; font-size:20pt; font-weight:800; color:#050510; background:linear-gradient(135deg,#00FF88,#00B4FF); box-shadow:0 0 16pt rgba(0,180,255,.55); }
.toprow { display:flex; align-items:center; gap:13pt; }
.tag { font-size:10.5pt; font-weight:700; padding:4pt 10pt; border-radius:16pt; }
.ex { margin-top:14pt; display:flex; align-items:center; gap:9pt; }
.ex .extag { font-size:10.5pt; font-weight:700; color:#7B00FF; background:rgba(123,0,255,.14); border:1px solid rgba(123,0,255,.4); padding:4pt 10pt; border-radius:16pt; }
.ex .extxt { font-size:12.5pt; color:#b9b9d8; }
/* steps (loop) */
.steps { display:flex; gap:8pt; margin-top:26pt; align-items:stretch; }
.step { flex:1; background:rgba(255,255,255,.04); border:1px solid rgba(255,255,255,.10); border-radius:12pt; padding:14pt 8pt; text-align:center; position:relative; }
.step .n { width:30pt; height:30pt; border-radius:50%; margin:0 auto 8pt; display:flex; align-items:center; justify-content:center; font-size:14pt; font-weight:800; color:#00B4FF; border:1.5pt solid #00B4FF; box-shadow:0 0 12pt rgba(0,180,255,.5); }
.step .t { font-size:14pt; font-weight:700; color:#fff; }
.arrow { align-self:center; color:#00B4FF; font-size:20pt; font-weight:800; }
/* ladder */
.ladder { display:flex; flex-direction:column; gap:12pt; margin-top:22pt; }
.rung { display:flex; align-items:center; gap:16pt; background:rgba(255,255,255,.04); border:1px solid rgba(255,255,255,.10); border-radius:13pt; padding:13pt 18pt; }
.rung .lv { font-size:13pt; font-weight:800; padding:5pt 12pt; border-radius:18pt; white-space:nowrap; }
.rung .rt { font-size:16pt; font-weight:700; color:#fff; }
.rung .rd { font-size:13pt; color:#9aa0c0; margin-left:auto; }
/* quad */
.quad { display:grid; grid-template-columns:1fr 1fr; gap:13pt; margin-top:20pt; flex:1; }
.qcard { background:rgba(255,255,255,.04); border:1px solid rgba(255,255,255,.10); border-radius:13pt; padding:14pt 16pt; }
.qcard .qn { font-size:13pt; font-weight:800; }
.qcard .qt { font-size:17pt; font-weight:800; color:#fff; margin:3pt 0 5pt; }
.qcard .qd { font-size:13pt; color:#9aa0c0; line-height:1.4; }
/* diagram */
.center-pill { align-self:center; margin-top:6pt; padding:10pt 26pt; border-radius:30pt; font-size:18pt; font-weight:800; color:#fff; border:2pt solid #00B4FF; box-shadow:0 0 20pt rgba(0,180,255,.5); background:rgba(0,180,255,.08); }
.parts { display:grid; grid-template-columns:repeat(4,1fr); gap:11pt; margin-top:18pt; }
.part { background:rgba(255,255,255,.04); border:1px solid rgba(255,255,255,.10); border-radius:11pt; padding:11pt; text-align:center; }
.part .pl { font-size:15pt; font-weight:800; }
.part .pt { font-size:11pt; color:#7d83a3; margin-top:2pt; }
/* table */
.tbl { margin-top:16pt; }
.trow { display:grid; grid-template-columns:1.3fr 1fr 1.4fr; padding:8pt 12pt; border-radius:8pt; align-items:center; }
.trow.head { color:#00B4FF; font-weight:800; font-size:12pt; }
.trow.alt { background:rgba(255,255,255,.04); }
.trow .a { font-size:15pt; font-weight:700; color:#fff; }
.trow .b { font-size:13pt; color:#9b7bff; }
.trow .c { font-size:13pt; color:#9aa0c0; }
/* explain (용어 풀이) */
.exg { display:grid; grid-template-columns:1fr 1fr; gap:12pt; margin-top:16pt; flex:1; }
.exc { background:rgba(255,255,255,.04); border:1px solid rgba(255,255,255,.10); border-radius:13pt; padding:12pt 15pt; display:flex; flex-direction:column; }
.exc .eh { display:flex; align-items:baseline; gap:8pt; }
.exc .en { font-size:16pt; font-weight:800; }
.exc .er { font-size:11pt; color:#7d83a3; font-weight:700; }
.exc .ed { font-size:12.5pt; color:#cdd1ea; line-height:1.42; margin-top:6pt; }
.exc .ea { font-size:11.5pt; color:#9aa0c0; line-height:1.36; margin-top:auto; padding-top:7pt; }
.exc .ea b { color:#9b7bff; font-weight:700; }
/* glossary2 (기법 2단 한 줄 풀이) */
.gg { display:grid; grid-template-columns:1fr 1fr; gap:12pt 26pt; margin-top:18pt; }
.gi .gt { font-size:14.5pt; font-weight:800; }
.gi .gd { font-size:12.5pt; color:#9aa0c0; line-height:1.3; margin-top:2pt; }
/* termpage (용어 한 장씩) */
.th { display:flex; align-items:baseline; gap:14pt; margin-top:6pt; }
.th .te { font-size:42pt; font-weight:800; }
.th .tr { font-size:19pt; font-weight:700; color:#7d83a3; }
.tdef { font-size:22pt; font-weight:700; color:#fff; line-height:1.46; margin-top:22pt; }
.tdef b { color:#9fe7ff; }
.tinfo { margin-top:auto; display:flex; flex-direction:column; gap:10pt; padding-bottom:2pt; }
.tib { background:rgba(255,255,255,.04); border:1px solid rgba(255,255,255,.10); border-radius:12pt; padding:12pt 16pt; font-size:15pt; color:#cdd1ea; line-height:1.4; }
.tib .til { font-weight:800; font-size:12pt; margin-right:11pt; letter-spacing:.5pt; }
/* chat (대화 데모) */
.chat { margin-top:11pt; display:flex; flex-direction:column; gap:5pt; }
.crow { display:flex; }
.crow.me { justify-content:flex-end; }
.crow.ai { justify-content:flex-start; }
.bub { max-width:82%; padding:7pt 12pt; border-radius:13pt; }
.bub .txt { font-size:12.5pt; line-height:1.27; }
.bub .txt b { color:#fff; }
.crow.me .bub { background:rgba(0,180,255,.13); border:1px solid rgba(0,180,255,.38); color:#dbeeff; border-bottom-right-radius:4pt; }
.crow.ai .bub { background:rgba(255,255,255,.05); border:1px solid rgba(255,255,255,.12); color:#e6e8f6; border-bottom-left-radius:4pt; }
.bub .cnote { display:block; margin-top:4pt; font-size:10pt; font-weight:700; color:#00FF88; }
.cpunch { margin-top:9pt; text-align:center; font-size:15pt; font-weight:800; }
/* contrast (보통 직원 vs AI 직원) */
.clanes { margin-top:22pt; display:flex; flex-direction:column; gap:15pt; }
.clane { border-radius:14pt; padding:15pt 18pt; border:1px solid rgba(255,255,255,.10); background:rgba(255,255,255,.04); }
.clane.hot { border-color:rgba(0,255,136,.5); background:rgba(0,255,136,.06); }
.clabel { font-size:14pt; font-weight:800; margin-bottom:11pt; }
.clane.cold .clabel { color:#7d83a3; }
.clane.hot .clabel { color:#00FF88; }
.cflow { display:flex; align-items:center; gap:9pt; }
.cstep { flex:1; text-align:center; font-size:14pt; font-weight:700; padding:10pt 7pt; border-radius:10pt; background:rgba(255,255,255,.05); }
.clane.cold .cstep { color:#9aa0c0; }
.clane.hot .cstep { color:#eafff4; background:rgba(0,255,136,.1); }
.cstep.key { outline:1.5pt solid; }
.clane.cold .cstep.key { color:#cfcf9a; outline-color:rgba(251,191,36,.5); }
.clane.hot .cstep.key { color:#bfffe0; outline-color:rgba(0,255,136,.6); }
.carrow { font-size:16pt; font-weight:800; color:#5a6080; }
.clane.hot .carrow { color:#00B4FF; }
.ctpunch { margin-top:17pt; text-align:center; font-size:16pt; font-weight:800; }
/* team */
.tgroup { margin-top:12pt; }
.gname { font-size:12pt; font-weight:800; color:#00B4FF; margin-bottom:6pt; }
.chips { display:flex; flex-wrap:wrap; gap:7pt; margin-bottom:9pt; }
.chip { font-size:12.5pt; font-weight:600; color:#D8DCF0; background:rgba(255,255,255,.05); border:1px solid rgba(255,255,255,.12); border-radius:18pt; padding:6pt 13pt; }
.chip.star { border-color:#00FF88; color:#bfffe0; }
.chip.master { border-color:#00B4FF; color:#bfeaff; font-weight:800; }
/* quote */
.qmark { font-size:120pt; font-weight:800; color:rgba(255,255,255,.06); position:absolute; left:40pt; top:30pt; }
.qtext { font-size:30pt; font-weight:700; font-style:italic; text-align:center; line-height:1.3; }
.qwho { font-size:16pt; color:#00B4FF; text-align:center; margin-top:22pt; }
/* closing */
.cl-title { font-size:46pt; font-weight:800; text-align:center; line-height:1.15; }
.cl-sub { font-size:18pt; color:#9aa0c0; text-align:center; margin-top:18pt; }
"""

HEAD = ('<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8">'
        '<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">'
        '<style>%s</style></head>') % CSS

BG = ('<div class="bg"><div class="blob b1"></div><div class="blob b2"></div>'
      '<div class="blob b3"></div><div class="scan"></div></div>')

slides = []
def page(inner, foot=True):
    n = len(slides) + 1
    pg = '' if not foot else '<div class="pagenum">%02d</div>' % n
    slides.append('%s<body>%s%s%s</body></html>' % (HEAD, BG, inner, pg))

def esc(s): return html.escape(s)

# ---- 템플릿 ----
def cover():
    inner = ('<div class="dot" style="right:56pt;top:50pt;"></div>'
             '<div class="frame" style="justify-content:center;">'
             '<div class="cv-kick">AI 직원 만들기 · 마스터클래스</div>'
             '<div class="cv-title grad">AI와 일하는 법</div>'
             '<div class="rule" style="margin-top:20pt;"></div>'
             '<div class="cv-sub">AI를 만드는 법이 아니라, AI와 함께 일하는 법</div></div>'
             '<div class="cv-foot">코딩 없이 AI 직원 채용하기 · 실전 가이드</div>')
    page(inner, foot=False)

def section(num, kick, title, sub, color=CYAN):
    inner = ('<div class="sec-num">%s</div>'
             '<div class="frame" style="justify-content:center;">'
             '<div class="sec-kick" style="color:%s;">%s</div>'
             '<div class="sec-title">%s</div><div class="rule"></div>'
             '<div class="sec-sub">%s</div></div>') % (num, color, esc(kick), esc(title).replace("\n","<br>"), esc(sub))
    page(inner)

def statement(big, small="", grad=False):
    cls = "st-big grad" if grad else "st-big"
    s = '<div class="st-small">%s</div>' % esc(small) if small else ""
    inner = ('<div class="frame" style="justify-content:center;">'
             '<div class="%s">%s</div>%s</div>') % (cls, esc(big).replace("\n","<br>"), s)
    page(inner)

def wall(kick, title, chips, foot):
    ch = "".join('<span class="chip">%s</span>' % esc(c) for c in chips)
    inner = ('<div class="frame"><div class="kicker">%s</div>'
             '<div class="h1">%s</div><div class="rule"></div>'
             '<div class="chips" style="margin-top:22pt;">%s</div>'
             '<div style="margin-top:18pt;font-size:15pt;color:#7d83a3;">%s</div></div>'
             ) % (esc(kick), esc(title), ch, esc(foot))
    page(inner)

def bullets(kick, title, items):
    lis = ""
    for text, cls in items:
        lis += '<div class="li %s">%s</div>' % (cls, text)
    inner = ('<div class="frame"><div class="kicker">%s</div><div class="h1">%s</div>'
             '<div class="rule"></div><div style="margin-top:22pt;">%s</div></div>') % (esc(kick), esc(title), lis)
    page(inner)

def category(letter, title, when, how, ex, tag=None):
    wlis = "".join('<div class="li c">%s</div>' % t for t in when)
    hlis = "".join('<div class="li">%s</div>' % t for t in how)
    tagh = ('<span class="tag" style="color:#00FF88;background:rgba(0,255,136,.12);border:1px solid rgba(0,255,136,.4);margin-left:10pt;">%s</span>' % esc(tag)) if tag else ""
    inner = ('<div class="frame">'
             '<div class="toprow"><div class="badge">%s</div>'
             '<div><div class="kicker">PART 2 · 이렇게 한다%s</div>'
             '<div class="h1" style="font-size:27pt;margin-top:2pt;">%s</div></div></div>'
             '<div class="cols">'
             '<div class="panel"><div class="lab" style="color:#00B4FF;">언제</div>%s</div>'
             '<div class="panel"><div class="lab" style="color:#00FF88;">나라면 이렇게</div>%s</div></div>'
             '<div class="ex"><span class="extag">예시</span><span class="extxt">%s</span></div></div>'
             ) % (letter, tagh, esc(title), wlis, hlis, esc(ex))
    page(inner)

def recipe(kick, title, leftlab, leftitems, rightlab, rightitems, ex):
    llis = "".join('<div class="li">%s</div>' % t for t in leftitems)
    rlis = "".join('<div class="li c">%s</div>' % t for t in rightitems)
    inner = ('<div class="frame"><div class="kicker">%s</div>'
             '<div class="h1" style="font-size:27pt;">%s</div><div class="rule"></div>'
             '<div class="cols">'
             '<div class="panel"><div class="lab" style="color:#00FF88;">%s</div>%s</div>'
             '<div class="panel"><div class="lab" style="color:#00B4FF;">%s</div>%s</div></div>'
             '<div class="ex"><span class="extag">예시</span><span class="extxt">%s</span></div></div>'
             ) % (esc(kick), esc(title), esc(leftlab), llis, esc(rightlab), rlis, esc(ex))
    page(inner)

def loop(kick, title, steps):
    cells = ""
    for i, t in enumerate(steps):
        cells += '<div class="step"><div class="n">%d</div><div class="t">%s</div></div>' % (i+1, esc(t).replace("\n","<br>"))
        if i < len(steps)-1: cells += '<div class="arrow">›</div>'
    inner = ('<div class="frame"><div class="kicker">%s</div><div class="h1">%s</div><div class="rule"></div>'
             '<div class="steps">%s</div></div>') % (esc(kick), esc(title), cells)
    page(inner)

def ladder(kick, title, rungs, footer):
    rh = ""
    cols = [GREEN, CYAN, VIOLET]
    for i,(lv, t, d) in enumerate(rungs):
        c = cols[i]
        rh += ('<div class="rung"><span class="lv" style="color:%s;background:%s22;border:1px solid %s66;">%s</span>'
               '<span class="rt">%s</span><span class="rd">%s</span></div>') % (c, c, c, esc(lv), esc(t), esc(d))
    inner = ('<div class="frame"><div class="kicker">%s</div><div class="h1">%s</div><div class="rule"></div>'
             '<div class="ladder">%s</div>'
             '<div style="margin-top:14pt;font-size:15pt;color:#00FF88;font-weight:700;">%s</div></div>'
             ) % (esc(kick), esc(title), rh, esc(footer))
    page(inner)

def quad(kick, title, cards):
    cs = ""
    cols=[GREEN,CYAN,VIOLET,"#FBBF24"]
    for i,(n,t,d) in enumerate(cards):
        cs += ('<div class="qcard"><div class="qn" style="color:%s;">%s</div>'
               '<div class="qt">%s</div><div class="qd">%s</div></div>') % (cols[i], esc(n), esc(t), esc(d))
    inner = ('<div class="frame"><div class="kicker">%s</div><div class="h1">%s</div><div class="rule"></div>'
             '<div class="quad">%s</div></div>') % (esc(kick), esc(title), cs)
    page(inner)

def diagram(kick, title, parts):
    ps = ""
    cols=[CYAN,GREEN,"#FBBF24",VIOLET,CYAN,GREEN,"#FBBF24"]
    for i,(pl,pt) in enumerate(parts):
        ps += '<div class="part"><div class="pl" style="color:%s;">%s</div><div class="pt">%s</div></div>' % (cols[i%len(cols)], esc(pl), esc(pt))
    inner = ('<div class="frame"><div class="kicker">%s</div><div class="h1">%s</div>'
             '<div class="center-pill">AI 직원 = 똑똑한 인재 한 명</div>'
             '<div class="parts">%s</div></div>') % (esc(kick), esc(title), ps)
    page(inner)

def table(kick, title, rows):
    body = '<div class="trow head"><div>쉬운 말</div><div>실제 용어</div><div>한 마디로</div></div>'
    for i,(a,b,c) in enumerate(rows):
        alt = " alt" if i%2==0 else ""
        body += '<div class="trow%s"><div class="a">%s</div><div class="b">%s</div><div class="c">%s</div></div>' % (alt, esc(a), esc(b), esc(c))
    inner = ('<div class="frame"><div class="kicker">%s</div><div class="h1">%s</div><div class="rule"></div>'
             '<div class="tbl">%s</div></div>') % (esc(kick), esc(title), body)
    page(inner)

def explain(kick, title, items):
    # items: (쉬운이름, 실제용어, 정의(HTML허용), 비유)
    cs = ""
    cols = [GREEN, CYAN, "#FBBF24", VIOLET]
    for i,(en, er, ed, ea) in enumerate(items):
        c = cols[i%len(cols)]
        cs += ('<div class="exc"><div class="eh">'
               '<span class="en" style="color:%s;">%s</span>'
               '<span class="er">%s</span></div>'
               '<div class="ed">%s</div>'
               '<div class="ea"><b>비유</b> · %s</div></div>') % (c, esc(en), esc(er), ed, esc(ea))
    inner = ('<div class="frame"><div class="kicker">%s</div><div class="h1">%s</div><div class="rule"></div>'
             '<div class="exg">%s</div></div>') % (esc(kick), esc(title), cs)
    page(inner)

def glossary2(kick, title, items):
    cols = [GREEN, CYAN, VIOLET, "#FBBF24"]
    gi = ""
    for i,(t,d) in enumerate(items):
        c = cols[i%len(cols)]
        gi += ('<div class="gi"><div class="gt" style="color:%s;">%s</div>'
               '<div class="gd">%s</div></div>') % (c, esc(t), esc(d))
    inner = ('<div class="frame"><div class="kicker">%s</div><div class="h1">%s</div><div class="rule"></div>'
             '<div class="gg">%s</div></div>') % (esc(kick), esc(title), gi)
    page(inner)

def termpage(idx, total, easy, real, oneliner, analogy, example, color=CYAN):
    inner = ('<div class="frame">'
             '<div class="kicker">용어 풀이 · %d / %d</div>'
             '<div class="th"><span class="te" style="color:%s;">%s</span>'
             '<span class="tr">%s</span></div><div class="rule"></div>'
             '<div class="tdef">%s</div>'
             '<div class="tinfo">'
             '<div class="tib"><span class="til" style="color:#9b7bff;">비유</span>%s</div>'
             '<div class="tib"><span class="til" style="color:#00FF88;">이렇게 씁니다</span>%s</div>'
             '</div></div>') % (idx, total, color, esc(easy), esc(real), oneliner, esc(analogy), esc(example))
    page(inner)

def contrast(kick, title, rowa, rowb, punch):
    # row = (label, [step,...], hot_bool); 가운데(index 1) 단계가 핵심 대비 → key 강조
    def lane(label, steps, hot):
        cells = ""
        for i, s in enumerate(steps):
            keycls = " key" if i == 1 else ""
            cells += '<div class="cstep%s">%s</div>' % (keycls, esc(s))
            if i < len(steps)-1: cells += '<div class="carrow">→</div>'
        return ('<div class="clane %s"><div class="clabel">%s</div>'
                '<div class="cflow">%s</div></div>') % ("hot" if hot else "cold", esc(label), cells)
    inner = ('<div class="frame"><div class="kicker">%s</div><div class="h1">%s</div><div class="rule"></div>'
             '<div class="clanes">%s%s</div>'
             '<div class="ctpunch grad">%s</div></div>') % (esc(kick), esc(title), lane(*rowa), lane(*rowb), esc(punch))
    page(inner)

def chat(kick, title, turns, punch):
    rows = ""
    for who, text, note in turns:
        cls = "me" if who == "me" else "ai"
        noteh = '<span class="cnote">↳ %s</span>' % esc(note) if note else ""
        rows += ('<div class="crow %s"><div class="bub">'
                 '<span class="txt">%s</span>%s</div></div>') % (cls, text, noteh)
    inner = ('<div class="frame"><div class="kicker">%s</div>'
             '<div class="h1" style="font-size:22pt;">%s</div><div class="rule"></div>'
             '<div class="chat">%s</div>'
             '<div class="cpunch grad">%s</div></div>') % (esc(kick), esc(title), rows, esc(punch))
    page(inner)

def team(kick, title, groups):
    gh = ""
    for gname, chips in groups:
        ch = ""
        for label, kind in chips:
            ch += '<span class="chip %s">%s</span>' % (kind, esc(label))
        gh += '<div class="tgroup"><div class="gname">%s</div><div class="chips">%s</div></div>' % (esc(gname), ch)
    inner = ('<div class="frame"><div class="kicker">%s</div><div class="h1">%s</div><div class="rule"></div>'
             '<div style="margin-top:14pt;">%s</div></div>') % (esc(kick), esc(title), gh)
    page(inner)

def quote(text, who):
    inner = ('<div class="qmark">“</div><div class="frame" style="justify-content:center;">'
             '<div class="qtext">%s</div><div class="qwho">— %s</div></div>') % (esc(text).replace("\n","<br>"), esc(who))
    page(inner)

def closing(big, sub):
    inner = ('<div class="dot" style="left:54pt;top:60pt;"></div>'
             '<div class="dot" style="right:64pt;bottom:70pt;background:#7B00FF;box-shadow:0 0 22pt 4pt #7B00FF;"></div>'
             '<div class="frame" style="justify-content:center;">'
             '<div class="cl-title grad">%s</div><div class="cl-sub">%s</div></div>') % (esc(big).replace("\n","<br>"), esc(sub))
    page(inner)

# ============ 콘텐츠 ============
# PART 0 — 인트로 (실제 업무 → 손이 많이 감 → 스킬 반전)
cover()
bullets("요즘은", "매일 하던 이런 일까지, AI가 합니다", [
    ("상품 상세페이지 초안을 알아서 짠다", ""),
    ("쇼핑몰 신규주문을 내려받아 정리한다", "c"),
    ("재고·상품자료를 표로 모아 정돈한다", ""),
    ("고객문의 답변 초안을 먼저 써 둔다", "c"),
])
wall("그런데 이걸 AI한테 제대로 시키려면", "원래는, 이런 기법을 하나하나 익혀야 합니다", [
    "역할·맥락 정해주기", "말투·금지 규칙 잡기", "일 순서·예외 설계", "사업 지식 떠먹이기",
    "외부 서비스 연결", "브라우저 동작 학습", "이미지 생성 다루기", "자동 실행 조건 잡기",
    "위험 차단 장치 넣기", "여러 AI 분업시키기",
], "이게 'AI를 다루는 기법'이에요. 하나하나 따로 배워야 한다면, 시작도 전에 지치죠.")
glossary2("AI를 다루는 기법 · 한 줄씩", "이게 다 뭐냐면 —", [
    ("역할·맥락 정해주기", "넌 누구고 무슨 상황인지 먼저 알려주기"),
    ("말투·금지 규칙 잡기", "어떻게 말하고, 뭘 하지 말지 정하기"),
    ("일 순서·예외 설계", "먼저 이거 → 다음 저거, 이럴 땐 멈춤"),
    ("사업 지식 떠먹이기", "내 사업 정보를 미리 읽혀두기"),
    ("외부 서비스 연결", "구글시트·쇼핑몰에 손 뻗게 잇기"),
    ("브라우저 동작 학습", "클릭 경로를 한 번 보여주면 익힘"),
    ("이미지 생성 다루기", "필요한 사진·컷을 만들게 시키기"),
    ("자동 실행 조건 잡기", "정해진 때·일이 생기면 돌리게"),
    ("위험 차단 장치 넣기", "게시·결제는 사람 확인으로 막기"),
    ("여러 AI 분업시키기", "큰 일은 보조에게 나눠 맡기기"),
])
statement("이걸 다 배우는 대신,\n스킬을 깔면 됩니다.", "위 기법들을 미리 담아 둔 게 '스킬'이에요. 깔면, 그 기법이 그대로 일을 합니다 — 사람은 안 외워도 돼요.", grad=True)
quad("오늘의 순서", "크게 셋, 그리고 부록", [
    ("PART 1", "사고방식", "AI를 어떻게 대하고, 무엇을 판단할까"),
    ("PART 2", "이렇게 한다", "실제 스킬로 일을 시키는 법 — 카테고리별"),
    ("PART 3", "준비·쓰기", "환경 준비부터 매일 쓰기까지"),
    ("부록", "용어 사전", "헷갈리는 말, 한 장씩 쉽게"),
])
# PART 1 — 사고방식 (인재 → 4가지 → 루프 → 판단 → 자동화 → 실습)
section("1", "PART 1 · 사고방식", "AI를 어떻게\n대할 것인가", "기능을 외우는 시간이 아니라, 판단을 익히는 시간입니다", GREEN)
bullets("", "AI는 '똑똑한 인재'다", [
    ("명문대 출신급 인재를 한 명 뽑은 셈이다", ""),
    ("세상 지식은 거의 다 안다", "c"),
    ("딱 하나, <b>내 사업만 모른다</b> — 방향·업무·방식·지식", ""),
    ("그 하나만 채워주면 된다", "v"),
])
contrast("사고방식 · 무엇을 말하면 되나", "'어떻게'는 몰라도 됩니다",
    ("보통 직원에겐", ["불편을 느낀다", "어떻게 풀지 내가 고민", "'이렇게 해줘' 지시"], False),
    ("AI 직원에겐", ["불편·희망만 말한다", "AI가 분석·해결법 제시", "추천 중 고르기"], True),
    "사장님은 '뭐가 불편한지'만. 해결법은 AI가 짜 옵니다.")
quad("사장이 채울 빈칸", "AI에게 줄 건 이 4가지", [
    ("① 방향", "어디로 갈지", "목표만 말하면 — 마스터가 묻고 설계"),
    ("② 업무", "말투·금지·우선순위", "'업무지침'으로 규칙을 한 번"),
    ("③ 프로세스", "일하는 순서", "'업무절차'로 순서를 묶어"),
    ("④ 지식", "사업 노하우", "'지식 노트'에 글로 쌓아 둬"),
])
loop("공통 작동 루프 · 모든 일에 똑같이", "결국 이 다섯 단계입니다", [
    "목표를\n말한다", "AI가\n묻는다", "추천을\n고른다", "작게\n테스트", "위험하면\n멈춘다",
])
chat(
    kick="이게 실제론 이렇게 보입니다",
    title="목표만 던지면, AI가 묻습니다",
    turns=[
        ("me", "광고비가 자꾸 새는 것 같은데, 어디서 빠지는지 모르겠어.", ""),
        ("ai", "지난 한 달 광고 내역 보면 돼요. 클릭만 많고 안 팔리는 키워드부터 볼까요?", "질문"),
        ("me", "응, 그런 것들 좀 골라줘.", ""),
        ("ai", "클릭은 많은데 주문 0인 키워드 8개 찾았어요. 끄는 건 사장님이 확인하시고, 매주 월요일 아침에 이 리포트를 자동으로 정리해 둘게요.", "예약"),
    ],
    punch="사장님은 욕구만 말하고, 정리는 AI가 합니다.",
)
bullets("판단 ① 의사결정", "A냐 B냐, 고르는 법", [
    ("처음이면 <b>단순한 쪽</b>부터", ""),
    ("돈 나가거나 되돌리기 어려우면 <b>안전한 쪽</b>", "c"),
    ("확신 없으면 작게 테스트로 확인", ""),
    ("내 회사 구조·최종 결정은 AI 말고 <b>사장이</b> — 이건 AI가 못 한다", "v"),
])
bullets("판단 ② 멈춤 버튼 · 가장 중요", "언제 믿고, 언제 직접 볼까", [
    ("<b>멈추고 직접</b> — 비밀번호 입력은 내가, AI는 안 만짐", "v"),
    ("<b>게시·결제·발송 버튼</b>은 항상 사람이", "v"),
    ("자동으로 돌릴 땐 위험한 일은 빼거나 마지막에 확인", "c"),
    ("<b>믿고 맡겨도 OK</b> — 초안·반복 작업·언제든 되돌릴 수 있는 일", ""),
])
ladder("자동화 3레벨 · 언제 올릴까", "한 단계씩 올립니다", [
    ("레벨 1", "부를 때 한다", "시작은 여기 — 필요할 때 '그거 해줘'"),
    ("레벨 2", "정해두면 알아서", "매일 같은 일이면 → 정해진 시각에"),
    ("레벨 3", "알아서 반응한다", "내가 없는 사이, 짧은 주기로 점검해 대응"),
], "지금 단계가 일을 해내면 더 안 올려도 됩니다. 자동일수록 위험한 일엔 사람 확인. 예약·반응은 PC·AI가 켜져 있는 동안 돕니다.")
statement("이 강의는 2시간,\n당신의 실전은 18시간.", "2시간은 사고방식. 나머지 18시간은 스킬로 실제 프로젝트를 직접 만드는 실습입니다.", grad=True)
# 다리 — AI 직원은 이렇게 움직입니다 (부품과 작동) : PART 1 → PART 2
statement("AI 직원은 챗봇이 아닙니다 —\n스스로 돌아가는 일꾼입니다",
    "부르면 답하는 걸 넘어서: 때 되면 알아서, 일 생기면 끼어들고, 벅차면 나눠 맡고, 내 시스템에 직접 손을 뻗습니다.", grad=True)
# 부품별 깊은 슬라이드 (Hook과 같은 glossary2 형식) — 자율 → 연결 → 업무절차
glossary2("AI 직원 · 예약(Cron) · 정해진 때면 알아서", "이런 때가 되면, 안 불러도 합니다", [
    ("매일 아침 9시", "어제 주문·문의를 정리해 둠"),
    ("매주 월요일", "지난주 매출·재고를 주간 보고로"),
    ("매월 1일", "지난달 정산·세금자료를 모아 둠"),
    ("마감 1시간 전", "'발주 마감 임박'을 미리 정리해 둠"),
    ("매시간", "경쟁사 가격·품절 변동만 체크해 보고"),
])
# 자동규칙(Hook) 전용 — 끼어드는 '순간'이 여럿임을 셀러 상황으로 펼침
glossary2("자동규칙(Hook) · 안 시켜도 알아서", "이런 순간마다 자동으로 끼어듭니다", [
    ("AI를 켜는 순간", "환경·오늘 할 일을 먼저 점검하고 시작"),
    ("내가 일을 시키는 순간", "우리 사업 규칙부터 챙겨 엉뚱한 답 방지"),
    ("등록·삭제 같은 행동 직전", "가격·재고를 한 번 더 자동 검사"),
    ("AI가 결제·삭제를 하려는 순간", '멈추고 "진짜 할까요?" 사장님께 확인'),
    ("일을 다 끝낸 순간", '"완료" 기록 + 다음 할 일 정리'),
])
glossary2("AI 직원 · 보조 직원(Subagent) · 벅차면 나눠서", "큰일은, 보조를 더 불러 나눠 맡습니다", [
    ("상품 100개 분석", "보조 여럿이 동시에 나눠 끝냄"),
    ("경쟁사 5곳 조사", "한 곳씩 맡아 한꺼번에"),
    ("상세컷 수십 장", "분담해 동시에 생성"),
    ("긴 매뉴얼·자료", "보조가 읽고 핵심만 가져옴"),
    ("사장님 대화창은", "결과만 깔끔하게 — 사장은 한 명"),
])
glossary2("AI 직원 · 외부 도구(MCP) · 내 시스템에 직접", "이걸 연결하면, AI가 직접 손을 뻗습니다", [
    ("구글시트", "재고·주문을 복붙 없이 바로 읽고 씀"),
    ("쇼핑몰 관리자", "주문·문의를 직접 가져옴"),
    ("캘린더", "일정·마감을 직접 읽고 등록"),
    ("1688·소싱 사이트", "상품 정보를 직접 수집"),
    ("비밀번호는", "사장님이 — AI는 절대 안 만짐"),
])
glossary2("AI 직원 · 손발(Tool) · 직접 하는 손발", "생각만 하던 AI에게, 손발을 답니다", [
    ("파일 열기·저장", "엑셀·문서를 직접 열고 채움"),
    ("계산", "마진·수량을 직접 계산"),
    ("검색", "필요한 정보를 직접 찾음"),
    ("이미지 만들기", "상세컷을 직접 생성"),
    ("표·문서 정리", "결과를 보기 좋게 정리"),
])
glossary2("AI 직원 · 업무절차(Skill·Workflow) · 일하는 방식을 굳힘", "말로 적거나, 순서를 박거나", [
    ("말투·금지 (말로·Skill)", "'존댓말로, 과장 빼고' → AI가 알아듣고 늘 그렇게"),
    ("만드는 법 (말로·Skill)", "'상세페이지는 이렇게' 적어두면 그대로"),
    ("등록 전 검사 (고정·Workflow)", "'가격·재고 먼저' — 빠지면 안 되는 순서"),
    ("정산 순서 (고정·Workflow)", "꼭 이 순서대로, AI가 못 건너뜀"),
    ("차이는", "말로=유연·AI가 알아들음 / 고정=순서 보장"),
])
# PART 2 — 이렇게 한다 (실제 스킬로 일 시키기)
section(2, "PART 2 · 이렇게 한다", "직원을 만들어\n일을 시킨다", "각 카테고리는 같은 틀 — [언제] · [나라면 이렇게] · [예시]", CYAN)
category("A", "어떻게 사업 지식을 쌓을 것인가",
    ["매번 내 사업을 처음부터 설명할 때",
     "들은 강의·메모가 흩어질 때"],
    ["사업 규칙·노하우를 <b>대화로</b> 정리",
     "<b>강의 녹취·메모</b>도 같은 형식으로 편입",
     "<b>저장 전 꼭 확인</b> — 형식은 그대로"],
    "'매번 사업 설명하기 지겨워' → AI '규칙부터 정리해둘까요?'")
category("B", "어떻게 일을 가르칠 것인가",
    ["AI 말투가 딱딱하거나 엉뚱할 때",
     "하면 안 되는 행동 할까 걱정될 때"],
    ["<b>말투·금지·우선순위</b>를 질문으로 뽑아줌",
     "그 답을 모아 <b>업무지침</b>으로 정리",
     "<b>OK 전엔 저장 안 함</b>"],
    "'말투가 마음에 안 들어' → AI '금지할 행동도 있나요?'")
category("C", "어떻게 일하는 순서를 잡을 것인가",
    ["순서를 안 지키고 건너뛸 때",
     "같은 일인데 결과가 들쭉날쭉할 때"],
    ["<b>결과 → 방식 → 갈림길</b> 순으로 설계",
     "절차를 <b>초안</b>으로 매번 같게",
     "위험한 단계는 <b>실행 전 확인</b>"],
    "'순서를 자꾸 건너뛰어' → AI '결과부터 정할까요?'")
category("D", "어떻게 외부 데이터를 연결할 것인가",
    ["시트·쇼핑몰 데이터를 못 읽을 때",
     "매번 복사해 붙여넣어 줄 때"],
    ["<b>뭘 연결하면 좋은지</b> 추천해줌",
     "연결(MCP)을 <b>단계별로</b> 안내",
     "<b>비밀번호는 내가 직접</b>"],
    "'시트 데이터를 AI가 못 읽어' → AI '뭐부터 연결할까요?'")
category("E", "어떻게 브라우저로 일을 시킬 것인가",
    ["관리자·1688 반복 클릭할 때",
     "로그인 필요해 자동화 어려울 때"],
    ["<b>내가 로그인한 크롬</b> 그대로(비번 안 만짐)",
     "한 번 <b>시범</b> 보이면 익힘(학습모드)",
     "익힌 순서를 <b>재현</b>해 대신 돌려줌"],
    "'관리자 반복 클릭 지겨워' → AI '한 번 보여주실래요?'")
category("F", "어떻게 개인 비서를 둘 것인가",
    ["할일·일정을 자꾸 까먹을 때",
     "정해둔 마감을 제때 챙기고 싶을 때"],
    ["<b>할일·일정</b>을 노트로 관리해줌",
     "정해진 때·AI 열 때 <b>'오늘 할일'</b>을 정리해 보여줌",
     "<b>놓치면 안 될 건</b> 콕 집어 보여줌"],
    "'발주 마감 자꾸 까먹어' → AI '열면 마감부터 정리해 보여드릴까요?'")
category("G", "어떻게 '없던 직원'을 새로 만들 것인가",
    ["우리가 안 만들어둔 일을 시키고 싶을 때",
     "상세페이지처럼 매번 손 많이 가는 일"],
    ["빌더에게 <b>'하고 싶다'</b>고만 말하면",
     "필요한 기법(<b>이미지 생성 등</b>)은 빌더가 끼움",
     "결과는 <b>서 있는 직원</b> — 다음엔 한마디"],
    "'상세페이지 자동으로 만들고 싶어' → AI '직원으로 만들어둘까요?'", tag="⭐ 직접 짓기")
loop("PART 2 · G 실전 · ⭐ 직접 짓기", "빌더가 이 순서로 '직원'을 짓습니다 — 외울 필요 없어요",
    ["욕구 듣기", "되물어 파악", "구성 제안", "기법 끼우기", "작게 시연", "직원으로 저장"])
chat(
    kick="PART 2 · G 실전 · ⭐ 직접 짓기",
    title="'하고 싶어' 한마디로, 상세페이지 직원 만들기",
    turns=[
        ("me", "상세페이지 만드는 거 너무 지겨워. 그냥 자동으로 하고 싶어.", ""),
        ("ai", "좋아요. 어떤 상품이에요? 쓸 만한 사진은 가지고 계세요?", "질문"),
        ("me", "텀블러야. 사진은 몇 장 있어.", ""),
        ("ai", "그럼 기존 상세페이지 톤에 맞춰 글을 쓰고, 없는 컷은 제가 만들어 채울게요. 등록 버튼은 사장님이 눌러주세요.", "지식 노트 · 이미지 생성 · 게시는 사람"),
        ("me", "응, 그리고 매일 새 상품 올라오면 그때마다 자동으로 해줘.", ""),
        ("ai", "그럼 매일 아침 초안까지 만들어 둘게요. 사장님은 등록만 확인하시면 돼요.", "예약"),
    ],
    punch="'하고 싶어' 한마디가, 직원이 됐습니다.",
)
# PART 3 — 준비·쓰기
section(3, "PART 3 · 준비하고, 쓰기", "맨 땅에서 시작해,\n매일 쓰기까지", "처음 한 번만 깔면, 그 다음은 부르기만 하면 됩니다", VIOLET)
bullets("처음 한 번 · 맨 땅에서 시작", "아무것도 없는 상태에서, 이 순서로", [
    ("<b>① Codex 설치</b> — 깔고 로그인. 딱 한 번. (다음 장에 <b>실제 명령</b>)", ""),
    ("<b>② 코치 설치</b> — 명령 두 줄로 'AI 직원 코치'를 깖. (그다음 장)", "c"),
    ("<b>③ 첫 직원</b> — 그냥 '하고 싶어' 한마디. 뭐부터 할지 모르면 마스터 코치가 안내.", "v"),
    ("브라우저 연결 같은 건 그때 <b>'환경 준비 도우미'</b>가 같이 깔아줌(로그인·허용만 사장님).", ""),
])
bullets("처음 한 번 · ① Codex 설치 (딱 한 번)", "검은 창에 두 단계면 끝", [
    ("<b>설치</b> — 시작에서 <b>PowerShell</b> 열고 한 줄 붙여넣기 → Enter", ""),
    ("&nbsp;&nbsp;&nbsp;&nbsp;<b>irm https://chatgpt.com/codex/install.ps1 | iex</b>", ""),
    ("끝나면 <b>PowerShell을 닫았다 다시 열기</b> — 그래야 codex 명령을 알아봐요.", "c"),
    ("<b>로그인</b> — <b>codex</b> 입력 → <b>'Sign in with ChatGPT'</b> → 브라우저에서 로그인. 비번은 사장님이.", ""),
    ("<span class='mute'>ChatGPT 계정이 필요해요. Node가 있으면 대신</span> <b>npm install -g @openai/codex</b><span class='mute'>.</span>", "v"),
])
bullets("처음 한 번 · ② 코치 설치 (명령 두 줄)", "GitHub에서 받아 깝니다 — 폴더 만질 필요 없어요", [
    ("<b>① 코치 묶음 등록</b>", ""),
    ("&nbsp;&nbsp;&nbsp;&nbsp;<b>codex plugin marketplace add rubydatalab/ai-project-coach</b>", ""),
    ("<b>② 코치 설치</b>", "c"),
    ("&nbsp;&nbsp;&nbsp;&nbsp;<b>codex plugin add ai-employee-coach@ai-project-coach</b>", "c"),
    ("<b>③ 부르기</b> — 그냥 한국어로 '~하고 싶어'. 뭐부터 할지 모르면 마스터 코치가 안내.", "v"),
])
glossary2("자주 쓰는 명령어 · 외우지 말고 곁에 두기", "대화 중에 '/'로 부르는 것들", [
    ("/clear", "머리 비우고 새 대화 — 앞 얘기 안 끌고 감"),
    ("/resume", "저장된 지난 대화를 골라 이어받기"),
    ("/goal", "지금 뭘 목표로 일하는지 정하고·확인하기"),
    ("/plan", "바로 시작 말고, 계획부터 세우게 시키기"),
    ("/model", "더 똑똑한 머리로 바꾸기 · 생각 깊이 조절"),
    ("/compact", "길어진 대화를 요약해 압축 (한도 넘기 전에)"),
    ("/status", "어디까지 했나 · 얼마나 썼나 한눈에"),
    ("/quit", "끄기 — 그냥 창을 닫아도 됩니다"),
])
bullets("진행상황 · 화면에 영어가 막 지나가도", "그건 AI가 '생각하며 일하는 중'이에요", [
    ("<b>초록색 영어</b>가 주르륵 흐르는 건 고장이 아니라, AI가 머릿속을 보여주는 거예요. <b>안 읽어도 됩니다.</b>", ""),
    ("<b>진행상황·결과</b>는 우리가 부른 코치(스킬)가 <b>한국어로</b> 정리해서 알려줘요.", "c"),
    ("지금 <b>어디까지 했나</b> 궁금하면 <b>/status</b>, 목표를 다시 짚고 싶으면 <b>/goal</b>.", ""),
    ("더 친절히 말해줬으면 하면, 그냥 <b>'한국어로 쉽게 설명하면서 해줘'</b>라고 말하면 돼요.", "v"),
])
bullets("환경 준비 도우미 · 점검하고, 빠지면 깔아줌", "미리 다 깔 필요 없어요", [
    ("처음 부르면 <b>환경을 한 번 점검</b> — 브라우저 등 빠진 걸 알려줌", ""),
    ("필요한 것만 <b>그때그때</b> 설치, 안 쓸 도구는 안 깖", "c"),
    ("사장님은 <b>로그인·'허용' 누르기</b>만, 비밀번호는 AI가 안 만짐", "v"),
])
bullets("매일 쓰기 · 막히면", "내 PC에서, 늘 같은 3단계", [
    ("<b>① 폴더 열기 → ② AI 켜기 → ③ '그거 해줘'</b>, 매번 같아요", ""),
    ("지난번 만든 직원은 이름으로 다시 부르면 끝", "c"),
    ("git·배포·온라인은 신경 안 써도 돼요 — 내 컴퓨터에서 씁니다", "v"),
    ("이상하면 '문제 해결 코치'가 원인을 같이 좁혀줌", ""),
])
team("스킬 한눈에", "혼자가 아닙니다 — AI 직원 코치 11명", [
    ("🏁 시작 · 준비", [("AI 직원 만들기 (마스터)", "master"), ("환경 준비 도우미", "")]),
    ("🏢 사업", [("자동화 아이디어", ""), ("사업 지식 노트", ""), ("업무지침 만들기", ""), ("일하는 순서 만들기", ""), ("외부 서비스 연결", ""), ("브라우저로 일 시키기", "")]),
    ("🙋 개인 · 🔧 사용", [("개인 비서 (할일·일정)", ""), ("내 PC에서 쓰기", ""), ("문제 해결 코치", "")]),
])
closing("외우지 마세요.\n그냥 시켜보세요.", "당신은 이제 AI 사장님입니다. 첫 직원부터 불러보세요.")
# 부록 — 용어 사전 (해부도 + 용어 12장)
section("✦", "부록 · 참고", "용어 사전", "외울 필요는 없어요 — 헷갈릴 때 한 장씩 펴 보세요", CYAN)
diagram("해부도 · 외우지 말고 직원 한 명을 떠올리기", "AI 직원은 이렇게 생겼습니다", [
    ("두뇌","Model"),("기억","Context"),("손발","Tool"),("외부 도구","MCP"),
    ("업무지침","Instruction"),("업무절차·고정","Workflow"),("업무절차·말로","Skill"),("보조 직원","Subagent"),
])
_T = 12
termpage(1, _T, "AI 직원", "Agent",
    "일을 대신 해주는 <b>AI 한 명</b>이에요. 목표만 말하면, 알아서 묻고 처리합니다.",
    "새로 뽑은 직원 — 시키면 일하고, 모르면 물어본다",
    "'이번 주 신상 5개, 상세페이지 만들어줘'", color=GREEN)
termpage(2, _T, "AI의 머리", "Model",
    "AI가 생각하는 <b>두뇌</b>예요. 더 똑똑한 머리를 고르면 더 어려운 일을 더 잘합니다.",
    "같은 자리라도, 더 똑똑한 사람을 앉히는 것",
    "어려운 기획은 똑똑한 머리로, 단순 정리는 가벼운 머리로", color=CYAN)
termpage(3, _T, "대화", "Prompt",
    "AI에게 건네는 <b>말</b>이에요. 정답 공식 없이, 사람한테 부탁하듯 말하면 됩니다.",
    "직원에게 '이거 좀 해줄래요?' 하고 말 거는 것",
    "'재고 떨어진 상품만 골라서 알려줘'", color=VIOLET)
termpage(4, _T, "상황·맥락", "Context · 기억",
    "AI가 지금 알고 있는 <b>배경</b>이에요. 내 사업·앞선 대화를 기억해야 엉뚱한 답을 안 합니다.",
    "내 사정을 아는 직원 vs 처음 보는 알바",
    "사업 노트를 먼저 읽혀두면, 매번 설명 안 해도 된다", color="#FBBF24")
termpage(5, _T, "업무지침", "Instruction",
    "AI가 늘 <b>지켜야 할 규칙</b>이에요. 한 번 적어두면 매번 그대로 따릅니다.",
    "신입에게 주는 '우리 회사 규칙' 한 장",
    "'상세설명은 존댓말로, 과장 표현은 빼고'", color=GREEN)
termpage(6, _T, "업무절차", "Workflow",
    "<b>고정된 절차</b>예요(개발자용). 한 번 정하면 AI가 멋대로 못 바꿔, 빠지면 안 되는 순서를 보장합니다.",
    "순서를 기계에 박아둔 것 — 늘 같은 순서로, 건너뛰기 없음",
    "'등록 전엔 반드시 가격 검사' 같은, 빠지면 안 되는 순서", color=CYAN)
termpage(7, _T, "업무절차", "Skill",
    "<b>말로 적어둔 업무절차</b>예요. 코드가 아니라 사람 말이라, AI가 알아듣고 그대로 일합니다. (필요할 때만 꺼내 봐서 가볍고요.)",
    "일 잘하는 직원에게 '이런 건 이렇게 해' 하고 일머리를 적어 건네는 것",
    "'상세페이지는 이렇게 만들어' 방식을 적어두면, AI가 그대로 만든다", color=GREEN)
termpage(8, _T, "손발", "Tool · 도구",
    "AI가 실제로 뭔가를 <b>하게 해주는 손발</b>이에요. 파일 열기·계산·검색 같은.",
    "머리로 생각만 하던 직원에게 손발을 달아주는 것",
    "엑셀을 직접 열어서 숫자를 채워 넣는 것", color=VIOLET)
termpage(9, _T, "외부 도구", "MCP",
    "구글시트·쇼핑몰 같은 <b>바깥 서비스에 직접 손을 뻗게</b> 해주는 연결구예요. 재고가 시트에 있으면, 복붙 없이 AI가 바로 읽어요.",
    "직원 책상에 회사 시스템 단말기를 깔아주는 것",
    "'구글시트 재고를 읽어서 정리해줘'", color="#FBBF24")
termpage(10, _T, "보조 직원", "Subagent",
    "한 직원이 벅찬 큰일을 만나면 <b>보조 직원을 더 불러 나눠 맡기는</b> 거예요. 상품 100개 분석도 보조 여럿이 동시에 나눠 끝내요.",
    "팀장이 팀원에게 일을 분담시키는 것",
    "'이 3가지를 한꺼번에 알아봐줘' → 셋이 동시에", color=CYAN)
termpage(11, _T, "예약", "Cron",
    "<b>정해진 시각에 알아서</b> 하게 해두는 거예요. 아침 9시가 되면, 안 불러도 어제 주문이 정리돼 있어요.",
    "알람 맞춰두면 그 시간에 울리는 것",
    "'매일 아침 9시에 어제 주문 정리해줘'", color=VIOLET)
termpage(12, _T, "자동규칙", "Hook",
    "AI가 어떤 일을 하는 <b>바로 그 순간 자동으로 끼어드는 규칙</b>이에요. 등록을 누르기 직전, 가격을 한 번 더 자동 검사하는 식이에요.",
    "공정 중간마다 자동으로 도장 찍는 검수 게이트",
    "'등록 누르기 직전엔 항상 가격을 한 번 검사'", color="#FBBF24")

# ---- write ----
for i, h in enumerate(slides):
    with open(os.path.join(HERE, "slide-%02d.html" % (i+1)), "w", encoding="utf-8") as f:
        f.write(h)
# 남는 옛 파일 제거 (17 등 손으로 만든 것 정리)
for fn in os.listdir(HERE):
    if fn.startswith("slide-") and fn.endswith(".html"):
        num = int(fn[6:8])
        if num > len(slides):
            os.remove(os.path.join(HERE, fn))
print("generated %d slides" % len(slides))
