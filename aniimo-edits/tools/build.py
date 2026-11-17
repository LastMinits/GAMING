#!/usr/bin/env python3
"""Build a HyperFrames project (index.html + compositions/captions.html) from an EDL JSON.

EDL times ("at", caption "t"/"e") are in SOURCE seconds of the original livestream;
the builder maps them onto the edited timeline. Segments play back to back.

usage: build.py <edl.json> <project_dir>
"""
import json, sys, os, html, re

W, H = 1080, 1920


def esc(s):
    return html.escape(s, quote=True)


def load(p):
    with open(p) as f:
        return json.load(f)


# ----------------------------------------------------------------------------- styles
STYLES = {
    # ---------------------------------------------------------------- FUNNY: comic chaos
    "funny": dict(
        frame=dict(top=430, w=1080, h=760, scale=1.25, radius=0, border="10px solid #111", rot=-1.2),
        css="""
:root{--bg:#FFD21F;--ink:#111;--hot:#FF3B5C;--accent:#1FD1FF;--paper:#fff}
#bg{position:absolute;inset:0;background:
  radial-gradient(circle at 20% 15%,rgba(255,255,255,.55) 0 180px,transparent 181px),
  radial-gradient(rgba(0,0,0,.16) 3px,transparent 3.5px) 0 0/28px 28px,var(--bg)}
#bg-rays{position:absolute;left:-540px;top:-540px;width:2160px;height:2160px;opacity:.18;
  background:repeating-conic-gradient(from 0deg at 50% 50%,#fff 0 9deg,transparent 9deg 18deg)}
.frame{box-shadow:16px 16px 0 #111}
.chapter{position:absolute;left:0;right:0;top:200px;display:flex;justify-content:center}
.chapter .inner{background:#111;color:#fff;font:900 54px/1.05 Montserrat;padding:22px 36px;border-radius:14px;
  text-transform:uppercase;letter-spacing:-.01em;max-width:960px;text-align:center;box-shadow:8px 8px 0 var(--hot)}
.chapter .num{display:block;font:800 30px/1 Montserrat;color:var(--bg);margin-bottom:10px;letter-spacing:.08em}
.sticker{position:absolute;font:900 74px/1 Montserrat;color:#fff;-webkit-text-stroke:5px #111;paint-order:stroke fill;
  text-transform:uppercase;white-space:nowrap}
.sticker .in{display:inline-block;padding:18px 30px;background:var(--hot);border:6px solid #111;border-radius:20px;box-shadow:8px 8px 0 #111}
.sticker.blue .in{background:var(--accent)}
.sticker.white .in{background:#fff;color:#111;-webkit-text-stroke:0}
.hook{position:absolute;left:0;right:0;top:190px;text-align:center}
.hook .l1{display:inline-block;font:900 92px/1 Montserrat;color:#fff;-webkit-text-stroke:7px #111;paint-order:stroke fill;text-transform:uppercase}
.hook .l2{display:block;margin-top:14px;font:800 40px/1.1 Montserrat;color:#111}
.wipe{position:absolute;inset:0;background:#111}
.wipe .stripe{position:absolute;left:0;right:0;height:640px;background:var(--hot)}
.outro{position:absolute;inset:0;background:var(--bg);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:30px}
.outro .big{font:900 120px/0.95 Montserrat;color:#fff;-webkit-text-stroke:8px #111;paint-order:stroke fill;text-align:center;text-transform:uppercase}
.outro .small{font:800 44px/1.2 Montserrat;color:#111;text-align:center}
""",
        cap_css="""
#root{position:absolute;inset:0}
.cg{position:absolute;left:50px;right:50px;top:1222px;display:flex;flex-wrap:wrap;justify-content:center;column-gap:24px;opacity:0}
.w{display:inline-block;font:900 76px/1.12 Montserrat;color:#fff;-webkit-text-stroke:7px #111;paint-order:stroke fill;text-transform:uppercase}
.w.hl{color:#FF3B5C}
""",
    ),
    # ---------------------------------------------------------------- BEST: neon arena hype
    "best": dict(
        frame=dict(top=360, w=1080, h=840, scale=1.38, radius=0, border="0", rot=0),
        css="""
:root{--bg:#060918;--ink:#fff;--cyan:#22E6FF;--mag:#FF2BD6;--gold:#FFC83A}
#bg{position:absolute;inset:0;background:linear-gradient(180deg,#0B1236 0%,#060918 45%,#100726 100%)}
#bg-rays{position:absolute;left:-400px;top:0;width:1880px;height:1920px;opacity:.35;
  background:repeating-linear-gradient(115deg,transparent 0 120px,rgba(34,230,255,.10) 120px 126px,transparent 126px 260px,rgba(255,43,214,.08) 260px 264px)}
.frame{box-shadow:0 0 0 4px rgba(34,230,255,.9),0 0 60px rgba(34,230,255,.35)}
.edge{position:absolute;left:0;right:0;height:6px;background:linear-gradient(90deg,var(--cyan),var(--mag))}
.chapter{position:absolute;left:70px;right:70px;top:190px}
.chapter .num{display:block;font:700 34px/1 Oswald;color:var(--cyan);letter-spacing:.25em}
.chapter .inner{display:block;font:400 112px/0.92 'League Gothic';color:#fff;text-transform:uppercase;letter-spacing:.01em;margin-top:8px}
.counter{position:absolute;right:70px;top:196px;font:700 34px/1 Oswald;color:rgba(255,255,255,.55);letter-spacing:.2em}
.sticker{position:absolute;font:400 120px/0.9 'League Gothic';color:#fff;text-transform:uppercase;white-space:nowrap;
  text-shadow:0 0 30px rgba(34,230,255,.8)}
.sticker .in{display:inline-block;padding:8px 26px;border:4px solid var(--cyan);background:rgba(6,9,24,.75)}
.sticker.gold{text-shadow:0 0 30px rgba(255,200,58,.8)}
.sticker.gold .in{border-color:var(--gold);color:var(--gold)}
.hook{position:absolute;left:70px;right:70px;top:180px}
.hook .l2{display:block;font:700 36px/1 Oswald;color:var(--cyan);letter-spacing:.25em}
.hook .l1{display:block;font:400 128px/0.9 'League Gothic';color:#fff;text-transform:uppercase;margin-top:10px}
.wipe{position:absolute;inset:0;background:transparent}
.wipe .slash{position:absolute;top:-200px;height:2320px;width:520px;background:linear-gradient(90deg,var(--cyan),var(--mag))}
.wipe .flash{position:absolute;inset:0;background:#fff;opacity:0}
.outro{position:absolute;inset:0;background:var(--bg);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:24px}
.outro .small{font:700 40px/1 Oswald;color:var(--cyan);letter-spacing:.3em;text-transform:uppercase}
.outro .big{font:400 190px/0.88 'League Gothic';color:#fff;text-transform:uppercase;text-align:center}
""",
        cap_css="""
#root{position:absolute;inset:0}
.cg{position:absolute;left:70px;right:70px;top:1236px;display:flex;flex-wrap:wrap;column-gap:18px;opacity:0}
.w{display:inline-block;font:700 66px/1.12 Oswald;color:#fff;text-transform:uppercase;
  text-shadow:0 4px 18px rgba(0,0,0,.6)}
.w.hl{color:#22E6FF}
""",
    ),
    # ---------------------------------------------------------------- DISC: field journal
    "disc": dict(
        frame=dict(top=360, w=1000, h=563, scale=0.926, radius=26, border="14px solid #fff", rot=0),
        css="""
:root{--bg:#F2EAD9;--ink:#1E2A2F;--teal:#0F8B8D;--coral:#F2545B;--sun:#F6B93B}
#bg{position:absolute;inset:0;background:
  linear-gradient(rgba(15,139,141,.10) 2px,transparent 2px) 0 0/60px 60px,
  linear-gradient(90deg,rgba(15,139,141,.10) 2px,transparent 2px) 0 0/60px 60px,var(--bg)}
#bg-rays{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 0%,rgba(246,185,59,.25),transparent 60%)}
.frame{box-shadow:0 24px 50px rgba(30,42,47,.28)}
.journal-head{position:absolute;left:60px;right:60px;top:186px;display:flex;align-items:flex-end;justify-content:space-between;border-bottom:4px solid var(--ink);padding-bottom:16px}
.journal-head .t{font:900 50px/1 Nunito;color:var(--ink);letter-spacing:.02em}
.journal-head .t b{color:var(--teal)}
.journal-head .p{font:800 30px/1 Nunito;color:var(--teal);letter-spacing:.12em}
.chapter{position:absolute;left:60px;right:60px;top:290px}
.chapter .inner{font:800 40px/1.1 Nunito;color:var(--ink)}
.chapter .num{display:inline-block;font:900 26px/1 Nunito;color:#fff;background:var(--teal);padding:8px 14px;border-radius:999px;margin-right:14px;vertical-align:middle;letter-spacing:.1em}
.card{position:absolute;left:60px;right:60px;top:1072px;height:212px;background:#fff;border-radius:26px;box-shadow:0 14px 34px rgba(30,42,47,.18);
  display:flex;align-items:center;gap:30px;padding:0 36px;border-left:16px solid var(--teal)}
.card .ico{width:130px;height:130px;border-radius:50%;background:var(--sun);display:flex;align-items:center;justify-content:center;flex:none;
  font:900 74px/1 Nunito;color:#1E2A2F}
.card .tx{flex:1;min-width:0}
.card .k{font:900 28px/1 Nunito;color:var(--teal);letter-spacing:.16em;text-transform:uppercase}
.card .n{font:900 62px/1.02 Nunito;color:var(--ink);margin-top:8px}
.card .d{font:700 30px/1.2 Nunito;color:#55636A;margin-top:8px}
.stamp{position:absolute;right:90px;top:1036px;font:900 46px/1 Nunito;color:var(--coral);border:6px solid var(--coral);border-radius:14px;padding:10px 18px;background:rgba(255,255,255,.85);letter-spacing:.06em}
.sticker{position:absolute;font:900 44px/1 Nunito;color:#fff;white-space:nowrap}
.sticker .in{display:inline-block;padding:14px 24px;background:var(--coral);border-radius:999px;box-shadow:0 8px 20px rgba(0,0,0,.18)}
.sticker.teal .in{background:var(--teal)}
.pin{position:absolute;width:70px;height:70px}
.pin .dot{position:absolute;left:0;top:0;width:70px;height:70px;border-radius:50% 50% 50% 0;background:var(--coral);border:6px solid #fff;box-shadow:0 6px 14px rgba(0,0,0,.3)}
.hook{position:absolute;left:0;right:0;top:150px;height:205px;padding:30px 60px 0;background:var(--bg)}
.hook .l2{display:block;font:900 30px/1 Nunito;color:var(--teal);letter-spacing:.16em}
.hook .l1{display:block;font:900 64px/1.02 Nunito;color:var(--ink);margin-top:12px}
.wipe{position:absolute;inset:0;background:transparent}
.wipe .page{position:absolute;inset:0;background:var(--teal)}
.outro{position:absolute;inset:0;background:var(--bg);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:26px}
.outro .small{font:900 34px/1 Nunito;color:var(--teal);letter-spacing:.18em}
.outro .big{font:900 96px/1.02 Nunito;color:var(--ink);text-align:center}
""",
        cap_css="""
#root{position:absolute;inset:0}
.cg{position:absolute;left:60px;right:60px;top:960px;text-align:center;opacity:0}
.cg .pill{display:inline-block;background:#1E2A2F;border-radius:22px;padding:14px 30px;max-width:960px}
.w{display:inline-block;margin:0 6px;font:800 46px/1.2 Nunito;color:rgba(255,255,255,.35)}
.w.hl{color:#F6B93B}
""",
    ),
}


# ----------------------------------------------------------------------------- helpers
def layout(edl):
    """assign output start/duration for each segment"""
    t = edl.get("lead", 0.0)
    for s in edl["segments"]:
        s["_start"] = round(t, 3)
        s["_dur"] = round(s["out"] - s["in"], 3)
        t += s["_dur"]
    return t


def mapt(seg, at):
    return round(seg["_start"] + (at - seg["in"]), 3)


def split_groups(text, maxw):
    words = text.split()
    groups, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) >= maxw or re.search(r"[.!?]$", w):
            groups.append(cur)
            cur = []
    if cur:
        groups.append(cur)
    # never leave a lone trailing word: fold it into the group before it
    out = []
    for g in groups:
        if out and len(g) == 1 and not re.search(r"[.!?]$", out[-1][-1]) and len(out[-1]) <= maxw:
            out[-1] = out[-1] + g
        else:
            out.append(g)
    return out


# ----------------------------------------------------------------------------- build
def build(edl, out):
    st = STYLES[edl["style"]]
    fr = st["frame"]
    total_media = layout(edl)
    outro_d = edl.get("outro", {}).get("dur", 0)
    total = round(total_media + outro_d, 3)
    os.makedirs(os.path.join(out, "compositions"), exist_ok=True)

    els, js, audios = [], [], []
    z = [10]

    def zi():
        z[0] += 1
        return z[0]

    fx = (W - fr["w"]) // 2
    vw, vh = round(1080 * fr["scale"]), round(608 * fr["scale"])
    vx, vy = round((fr["w"] - vw) / 2), round((fr["h"] - vh) / 2)

    # ---- background (untimed full-bleed)
    els.append('<div id="bg"></div><div id="bg-rays"></div>')
    js.append('tl.fromTo("#bg-rays",{rotation:0},{rotation:%s,duration:%s,ease:"none"},0);' %
              (25 if edl["style"] != "disc" else 0, total))
    if edl["style"] == "best":
        els.append('<div class="edge" style="top:%dpx"></div><div class="edge" style="top:%dpx"></div>' % (fr["top"] - 6, fr["top"] + fr["h"]))

    deco = {
        "funny": '<div id="deco" style="position:absolute;left:-60px;right:-60px;top:1440px;height:330px" data-layout-ignore>'
                 '<div id="tape1" style="position:absolute;left:0;top:0;width:4200px;height:110px;background:#111;color:#FFD21F;font:900 64px/110px Montserrat;white-space:nowrap">'
                 + "HAHAHA &#9733; WOI! &#9733; TAK NAK! &#9733; " * 8 + '</div>'
                 '<div id="tape2" style="position:absolute;left:0;top:150px;width:4200px;height:96px;background:#FF3B5C;color:#fff;font:900 54px/96px Montserrat;white-space:nowrap">'
                 + "KESABARAN DIUJI &#9679; MIRA VS ANIIMO &#9679; " * 8 + '</div></div>',
        "best": '<div id="deco" style="position:absolute;left:0;right:0;top:1400px;height:420px" data-layout-ignore>'
                '<div id="tape1" style="position:absolute;left:0;top:40px;width:5200px;font:400 230px/1 \'League Gothic\';color:transparent;-webkit-text-stroke:2px rgba(34,230,255,.35);white-space:nowrap">'
                + "BEST MOMENTS &middot; ANIIMO &middot; " * 8 + '</div></div>',
        "disc": '<div id="deco" style="position:absolute;left:60px;right:60px;top:1400px;height:380px" data-layout-ignore>'
                '<div style="position:absolute;inset:0;border-top:3px dashed rgba(30,42,47,.25)"></div>'
                '<div style="position:absolute;left:0;top:34px;font:800 30px/1.6 Nunito;color:rgba(30,42,47,.45)">Catatan lapangan &middot; rakaman live stream<br>Whisperwake Isles &middot; kemas kini map baru</div>'
                '<div id="tape1" style="position:absolute;right:0;top:30px;width:150px;height:150px;border-radius:50%;border:6px solid rgba(15,139,141,.35);display:flex;align-items:center;justify-content:center;font:900 30px/1.1 Nunito;color:rgba(15,139,141,.6);text-align:center">ANIIMO<br>LOG</div></div>',
    }[edl["style"]]
    els.append(deco)
    if edl["style"] in ("funny", "best"):
        js.append('tl.fromTo("#tape1",{x:0},{x:-1400,duration:%s,ease:"none"},0);' % total)
        if edl["style"] == "funny":
            js.append('tl.set("#deco",{rotation:-4},0);tl.fromTo("#tape2",{x:-1400},{x:0,duration:%s,ease:"none"},0);' % total)
    else:
        js.append('tl.fromTo("#tape1",{rotation:-12},{rotation:12,duration:%s,ease:"none"},0);' % total)

    # ---- gameplay frame with one zoom wrapper per segment
    vids = []
    for i, s in enumerate(edl["segments"]):
        sid = s["id"]
        vol = s.get("vol", 1)
        vids.append(
            f'<div class="zw" id="zw-{sid}" style="position:absolute;left:{vx}px;top:{vy}px;width:{vw}px;height:{vh}px">'
            f'<video id="v-{sid}" class="clip" src="assets/clips/{sid}.mp4" data-start="{s["_start"]}" data-duration="{s["_dur"]}" '
            f'data-media-start="0" data-track-index="0" data-has-audio="true" data-volume="{vol}" playsinline '
            f'style="position:absolute;left:0;top:0;width:{vw}px;height:{vh}px;object-fit:cover"></video></div>')
        st0 = s["_start"]
        js.append(f'tl.set("#zw-{sid}",{{scale:1,x:0,y:0,transformOrigin:"50% 50%"}},{st0});')
        for zm in s.get("zooms", []):
            t0 = mapt(s, zm["at"])
            ox, oy = zm.get("ox", 50), zm.get("oy", 50)
            d = zm.get("d", 0.35)
            ease = zm.get("ease", "power3.out" if zm["s"] > 1 else "power2.inOut")
            js.append(f'tl.to("#zw-{sid}",{{scale:{zm["s"]},transformOrigin:"{ox}% {oy}%",duration:{d},ease:"{ease}"}},{t0});')
        for sh in s.get("shake", []):
            t0 = mapt(s, sh)
            pts = [(-18, 10), (16, -12), (-12, 8), (10, -6), (-6, 4), (0, 0)]
            for k, (x, y) in enumerate(pts):
                js.append(f'tl.to("#frame-shake",{{x:{x},y:{y},duration:0.04,ease:"none"}},{round(t0 + k * 0.04, 3)});')
    border = fr["border"]
    els.append(
        f'<div id="frame-rot" style="position:absolute;left:{fx}px;top:{fr["top"]}px;width:{fr["w"]}px;height:{fr["h"]}px">'
        f'<div id="frame-shake" style="position:absolute;inset:0">'
        f'<div class="frame" data-layout-allow-overflow style="position:absolute;inset:0;overflow:hidden;border-radius:{fr["radius"]}px;outline:none;'
        f'{"border:" + border + ";" if border != "0" else ""}background:#000">' + "".join(vids) + '</div></div></div>')
    if fr["rot"]:
        js.append(f'tl.set("#frame-rot",{{rotation:{fr["rot"]}}},0);')

    # ---- chapter titles (per segment, optional)
    nseg_ch = [s for s in edl["segments"] if s.get("chapter")]
    for ci, s in enumerate(nseg_ch):
        ch = s["chapter"]
        cid = f'ch-{s["id"]}'
        d = ch.get("d", s["_dur"])
        t0 = s["_start"] + ch.get("delay", 0)
        num = ch.get("num", "")
        els.append(f'<div id="{cid}" class="clip chapter" data-start="{t0}" data-duration="{d}" data-track-index="2" style="z-index:{zi()}">'
                   f'<div class="inner" id="{cid}-i">' + (f'<span class="num">{esc(num)}</span>' if num else "") + f'{esc(ch["text"])}</div></div>')
        if edl["style"] == "funny":
            js.append(f'tl.fromTo("#{cid}-i",{{scale:0.3,rotation:-8,opacity:0}},{{scale:1,rotation:-2,opacity:1,duration:0.45,ease:"back.out(2.2)"}},{t0});')
            js.append(f'tl.to("#{cid}-i",{{scale:0.6,opacity:0,duration:0.18,ease:"power3.in"}},{round(t0 + d - 0.2, 3)});')
        elif edl["style"] == "best":
            js.append(f'tl.fromTo("#{cid}-i",{{x:-120,opacity:0,filter:"blur(12px)"}},{{x:0,opacity:1,filter:"blur(0px)",duration:0.4,ease:"expo.out"}},{t0});')
            js.append(f'tl.to("#{cid}-i",{{x:80,opacity:0,filter:"blur(10px)",duration:0.2,ease:"power3.in"}},{round(t0 + d - 0.22, 3)});')
        else:
            js.append(f'tl.fromTo("#{cid}-i",{{y:24,opacity:0}},{{y:0,opacity:1,duration:0.5,ease:"power4.out"}},{t0});')
            js.append(f'tl.to("#{cid}-i",{{opacity:0,duration:0.2,ease:"power2.in"}},{round(t0 + d - 0.22, 3)});')

    if edl["style"] == "best":
        n = len(edl["segments"])
        for i, s in enumerate(edl["segments"]):
            if s.get("chapter"):
                cid = f'cnt-{s["id"]}'
                els.append(f'<div id="{cid}" class="clip counter" data-start="{s["_start"]}" data-duration="{s["_dur"]}" data-track-index="3" style="z-index:{zi()}">'
                           f'<span id="{cid}-i">{esc(s["chapter"].get("count", ""))}</span></div>')
    if edl["style"] == "disc":
        hd = edl.get("hook", {}).get("d", 0)
        els.append(f'<div id="jhead" class="clip journal-head" data-start="{hd}" data-duration="{round(total - hd, 3)}" data-track-index="3" style="z-index:{zi()}"><div class="t" id="jhead-t">ANIIMO <b>DISCOVERY LOG</b></div><div class="p">MAP BARU</div></div>')
        js.append(f'tl.fromTo("#jhead-t",{{opacity:0,y:-14}},{{opacity:1,y:0,duration:0.4,ease:"power3.out"}},{hd});')

    # ---- discovery cards
    for s in edl["segments"]:
        c = s.get("card")
        if not c:
            continue
        cid = f'card-{s["id"]}'
        t0 = mapt(s, c["at"])
        d = c.get("d", round(s["_start"] + s["_dur"] - t0, 3))
        els.append(f'<div id="{cid}" class="clip" data-start="{t0}" data-duration="{d}" data-track-index="4" style="position:absolute;inset:0;z-index:{zi()}">'
                   f'<div class="card" id="{cid}-c"><div class="ico" id="{cid}-ico">{esc(c.get("icon", "?"))}</div><div class="tx">'
                   f'<div class="k">{esc(c["kicker"])}</div><div class="n">{esc(c["name"])}</div><div class="d">{esc(c["desc"])}</div></div></div>'
                   + (f'<div class="stamp" id="{cid}-st">{esc(c["stamp"])}</div>' if c.get("stamp") else "") + '</div>')
        js.append(f'tl.fromTo("#{cid}-c",{{y:80,opacity:0}},{{y:0,opacity:1,duration:0.55,ease:"expo.out"}},{t0});')
        js.append(f'tl.fromTo("#{cid}-ico",{{scale:0,rotation:-90}},{{scale:1,rotation:0,duration:0.6,ease:"back.out(2)"}},{round(t0 + 0.15, 3)});')
        if c.get("stamp"):
            js.append(f'tl.fromTo("#{cid}-st",{{scale:2.4,opacity:0,rotation:-24}},{{scale:1,opacity:1,rotation:-10,duration:0.3,ease:"power4.in"}},{round(t0 + 0.45, 3)});')
        js.append(f'tl.to("#{cid}-c",{{y:40,opacity:0,duration:0.22,ease:"power2.in"}},{round(t0 + d - 0.24, 3)});')
        if c.get("stamp"):
            js.append(f'tl.to("#{cid}-st",{{opacity:0,duration:0.2}},{round(t0 + d - 0.24, 3)});')

    # ---- stickers / pins
    for s in edl["segments"]:
        for k, sk in enumerate(s.get("stickers", [])):
            cid = f'sk-{s["id"]}-{k}'
            t0 = mapt(s, sk["at"])
            d = sk.get("d", 1.4)
            cls = sk.get("cls", "")
            if sk.get("kind") == "pin":
                els.append(f'<div id="{cid}" class="clip pin" data-start="{t0}" data-duration="{d}" data-track-index="5" style="left:{sk["x"]}px;top:{sk["y"]}px;z-index:{zi()}">'
                           f'<div class="dot" id="{cid}-i"></div></div>')
                js.append(f'tl.fromTo("#{cid}-i",{{y:-160,opacity:0,rotation:-45}},{{y:0,opacity:1,rotation:-45,duration:0.45,ease:"bounce.out"}},{t0});')
                js.append(f'tl.to("#{cid}-i",{{opacity:0,duration:0.15}},{round(t0 + d - 0.16, 3)});')
                continue
            rot = sk.get("rot", -6)
            els.append(f'<div id="{cid}" class="clip sticker {cls}" data-start="{t0}" data-duration="{d}" data-track-index="5" style="left:{sk["x"]}px;top:{sk["y"]}px;z-index:{zi()}">'
                       f'<span class="in" id="{cid}-i">{esc(sk["text"])}</span></div>')
            if edl["style"] == "funny":
                js.append(f'tl.fromTo("#{cid}-i",{{scale:0,rotation:{rot - 25}}},{{scale:1,rotation:{rot},duration:0.4,ease:"back.out(3)"}},{t0});')
            elif edl["style"] == "best":
                js.append(f'tl.fromTo("#{cid}-i",{{scale:1.8,opacity:0,filter:"blur(10px)"}},{{scale:1,opacity:1,filter:"blur(0px)",duration:0.25,ease:"power4.out"}},{t0});')
            else:
                js.append(f'tl.fromTo("#{cid}-i",{{y:30,opacity:0,scale:0.8}},{{y:0,opacity:1,scale:1,duration:0.4,ease:"back.out(1.6)"}},{t0});')
            js.append(f'tl.to("#{cid}-i",{{scale:0.7,opacity:0,duration:0.15,ease:"power2.in"}},{round(t0 + d - 0.16, 3)});')

    # ---- seam transitions (cover each cut)
    for i, s in enumerate(edl["segments"][1:], start=1):
        tc = s["_start"]
        if s.get("cut") == "hard":
            continue
        cid = f'tr-{i}'
        t0 = round(tc - 0.18, 3)
        if edl["style"] == "funny":
            els.append(f'<div id="{cid}" class="clip wipe" data-start="{t0}" data-duration="0.4" data-track-index="6" style="background:transparent;z-index:900">'
                       f'<div class="stripe" id="{cid}-a" style="top:0;background:#111"></div><div class="stripe" id="{cid}-b" style="top:640px"></div><div class="stripe" id="{cid}-c" style="top:1280px;background:#1FD1FF"></div></div>')
            for k, ch in enumerate("abc"):
                dirn = 1 if k % 2 == 0 else -1
                js.append(f'tl.fromTo("#{cid}-{ch}",{{x:{-1200 * dirn}}},{{x:0,duration:0.17,ease:"power3.in"}},{round(t0 + k * 0.02, 3)});')
                js.append(f'tl.to("#{cid}-{ch}",{{x:{1200 * dirn},duration:0.18,ease:"power3.out"}},{round(tc + 0.02 + k * 0.02, 3)});')
        elif edl["style"] == "best":
            els.append(f'<div id="{cid}" class="clip wipe" data-start="{t0}" data-duration="0.44" data-track-index="6" style="z-index:900">'
                       f'<div class="slash" id="{cid}-s"></div><div class="flash" id="{cid}-f"></div></div>')
            js.append(f'tl.fromTo("#{cid}-s",{{x:-900,skewX:-20}},{{x:1500,skewX:-20,duration:0.36,ease:"power2.inOut"}},{t0});')
            js.append(f'tl.fromTo("#{cid}-f",{{opacity:0}},{{opacity:0.85,duration:0.06}},{round(tc - 0.04, 3)});')
            js.append(f'tl.to("#{cid}-f",{{opacity:0,duration:0.2,ease:"power2.out"}},{round(tc + 0.03, 3)});')
        else:
            els.append(f'<div id="{cid}" class="clip wipe" data-start="{t0}" data-duration="0.5" data-track-index="6" style="z-index:900">'
                       f'<div class="page" id="{cid}-p"></div></div>')
            js.append(f'tl.fromTo("#{cid}-p",{{clipPath:"circle(0% at 50% 42%)"}},{{clipPath:"circle(75% at 50% 42%)",duration:0.18,ease:"power2.in"}},{t0});')
            js.append(f'tl.to("#{cid}-p",{{clipPath:"circle(0% at 50% 42%)",duration:0.26,ease:"power2.out"}},{round(tc + 0.02, 3)});')

    # ---- hook overlay
    hk = edl.get("hook")
    if hk:
        d = hk.get("d", 2.6)
        els.append(f'<div id="hook" class="clip hook" data-start="0" data-duration="{d}" data-track-index="2" style="z-index:{zi()}">'
                   f'<span class="l2" id="hook-2">{esc(hk.get("kicker", ""))}</span><span class="l1" id="hook-1">{esc(hk["text"])}</span></div>')
        js.append('tl.fromTo("#hook-1",{scale:1.08},{scale:1,duration:0.5,ease:"power3.out"},0);')
        js.append(f'tl.to(["#hook-1","#hook-2"],{{opacity:0,y:-20,duration:0.2,ease:"power2.in"}},{round(d - 0.22, 3)});')

    # ---- outro
    oc = edl.get("outro")
    if oc:
        t0 = round(total_media, 3)
        els.append(f'<div id="outro" class="clip outro" data-start="{t0}" data-duration="{oc["dur"]}" data-track-index="7" style="z-index:950">'
                   f'<div class="small" id="outro-s">{esc(oc["kicker"])}</div><div class="big" id="outro-b">{oc["text"]}</div></div>')
        js.append(f'tl.fromTo("#outro-b",{{scale:0.7,opacity:0}},{{scale:1,opacity:1,duration:0.5,ease:"back.out(2)"}},{round(t0 + 0.1, 3)});')
        js.append(f'tl.fromTo("#outro-s",{{y:20,opacity:0}},{{y:0,opacity:1,duration:0.4,ease:"power3.out"}},{round(t0 + 0.35, 3)});')

    # ---- sfx
    k = 0
    for s in edl["segments"]:
        for sf in s.get("sfx", []):
            k += 1
            t0 = max(0, mapt(s, sf["at"]))
            audios.append(f'<audio id="sfx-{k}" class="clip" src="assets/sfx/{sf["name"]}.mp3" data-start="{t0}" '
                          f'data-track-index="20" data-volume="{sf.get("vol", 0.35)}"></audio>')
    for i, s in enumerate(edl["segments"][1:], start=1):
        if s.get("cut") == "hard" or not edl.get("seam_sfx"):
            continue
        k += 1
        names = edl["seam_sfx"]
        audios.append(f'<audio id="sfx-{k}" class="clip" src="assets/sfx/{names[i % len(names)]}.mp3" data-start="{round(s["_start"] - 0.2, 3)}" '
                      f'data-track-index="21" data-volume="{edl.get("seam_vol", 0.3)}"></audio>')
    if oc and oc.get("sfx"):
        k += 1
        audios.append(f'<audio id="sfx-{k}" class="clip" src="assets/sfx/{oc["sfx"]}.mp3" data-start="{round(total_media + 0.1, 3)}" data-track-index="20" data-volume="0.4"></audio>')

    # ---- captions composition
    cap_groups, cap_js = [], []
    maxw = edl.get("cap_words", 3)
    gi = 0
    for s in edl["segments"]:
        for c in s.get("captions", []):
            t0, t1 = mapt(s, c["t"]), mapt(s, c["e"])
            t0 = max(t0, s["_start"] + 0.05)
            t1 = min(t1, s["_start"] + s["_dur"] - 0.02)
            if t1 - t0 < 0.25:
                continue
            groups = split_groups(c["text"], maxw)
            nchar = sum(len(" ".join(g)) for g in groups)
            tt = t0
            hl = set(x.upper() for x in c.get("hl", []))
            for g in groups:
                gd = (t1 - t0) * len(" ".join(g)) / max(1, nchar)
                gs, ge = round(tt, 3), round(tt + gd, 3)
                tt += gd
                gi += 1
                gid = f"g{gi}"
                spans = []
                for wi, w in enumerate(g):
                    cls = "w hl" if re.sub(r"[^\w']", "", w.upper()) in hl or w.upper() in hl else "w"
                    spans.append(f'<span class="{cls}" id="{gid}w{wi}">{esc(w)}</span>')
                inner = "".join(spans)
                if edl["style"] == "disc":
                    inner = f'<span class="pill">{inner}</span>'
                cap_groups.append(f'<div class="cg" id="{gid}">{inner}</div>')
                cap_js.append(f'tl.set("#{gid}",{{opacity:1,visibility:"visible"}},{gs});')
                step = min(0.09, (ge - gs) / max(1, len(g)) * 0.6)
                for wi in range(len(g)):
                    wt = round(gs + wi * step, 3)
                    if edl["style"] == "funny":
                        cap_js.append(f'tl.fromTo("#{gid}w{wi}",{{scale:0.2,rotation:{(-8 if wi % 2 else 8)}}},{{scale:1,rotation:0,duration:0.28,ease:"back.out(3)"}},{wt});')
                    elif edl["style"] == "best":
                        cap_js.append(f'tl.fromTo("#{gid}w{wi}",{{opacity:0,y:26,filter:"blur(8px)"}},{{opacity:1,y:0,filter:"blur(0px)",duration:0.16,ease:"power3.out"}},{wt});')
                    else:
                        cap_js.append(f'tl.fromTo("#{gid}w{wi}",{{color:"rgba(255,255,255,0.35)"}},{{color:"{"#F6B93B" if "hl" in spans[wi] else "#ffffff"}",duration:0.1,ease:"none"}},{wt});')
                if edl["style"] == "disc":
                    cap_js.append(f'tl.fromTo("#{gid}",{{y:16}},{{y:0,duration:0.25,ease:"power3.out"}},{gs});')
                cap_js.append(f'tl.to("#{gid}",{{opacity:0,duration:0.1,ease:"power2.in"}},{round(max(gs + 0.15, ge - 0.1), 3)});')
                cap_js.append(f'tl.set("#{gid}",{{opacity:0,visibility:"hidden"}},{ge});')

    cap_html = f"""<template>
  <style>
{st["cap_css"]}
  </style>
  <div id="root" data-composition-id="captions" data-width="{W}" data-height="{H}">
    {chr(10).join(cap_groups)}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    {chr(10).join(cap_js)}
    window.__timelines["captions"] = tl;
  </script>
</template>
"""
    with open(os.path.join(out, "compositions", "captions.html"), "w") as f:
        f.write(cap_html)

    index = f"""<!doctype html>
<html lang="ms" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <title>{esc(edl["title"])}</title>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: {W}px; height: {H}px; overflow: hidden; background: #000; }}
      #root {{ position: relative; width: {W}px; height: {H}px; overflow: hidden; }}
{st["css"]}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-width="{W}" data-height="{H}">
      {chr(10).join(els)}
      <div id="captions" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0"
        data-duration="{total}" data-track-index="8" data-track-kind="captions" data-width="{W}" data-height="{H}" style="position:absolute;inset:0;z-index:800"></div>
      {chr(10).join(audios)}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      {chr(10).join("      " + j for j in js).strip()}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
    with open(os.path.join(out, "index.html"), "w") as f:
        f.write(index)
    print(f"built {out}: {len(edl['segments'])} segments, {total:.1f}s")


if __name__ == "__main__":
    build(load(sys.argv[1]), sys.argv[2])
