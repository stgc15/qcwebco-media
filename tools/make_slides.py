from PIL import Image, ImageDraw, ImageFont
import os, subprocess

NAVY = (14, 30, 58); AMBER = (245, 166, 35); PAPER = (245, 241, 232); SLATE = (74, 85, 104)
FD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts/")
OUT = os.environ.get("OUT", "out/"); os.makedirs(OUT, exist_ok=True)

def font(name, size, weight):
    f = ImageFont.truetype(FD + name, size)
    try: f.set_variation_by_axes([weight] if name.startswith("Space") else [14 if size < 40 else 32, weight])
    except Exception: pass
    return f

def wrap(d, text, f, maxw):
    lines = []
    for para in text.split("\n"):
        cur = ""
        for w in para.split():
            t = (cur + " " + w).strip()
            if d.textlength(t, font=f) <= maxw: cur = t
            else: lines.append(cur); cur = w
        lines.append(cur)
    return lines

def slide(s, W, H, idx, total, brand):
    dark = s.get("dark", idx % 2 == 0)
    bg, fg, sub = (NAVY, PAPER, (190, 200, 215)) if dark else (PAPER, NAVY, SLATE)
    im = Image.new("RGB", (W, H), bg); d = ImageDraw.Draw(im)
    m = 96; maxw = W - 2 * m
    # blueprint grid
    gc = tuple(min(255, c + 12) for c in bg) if dark else tuple(max(0, c - 10) for c in bg)
    for x in range(0, W, 60): d.line([(x, 0), (x, H)], fill=gc, width=1)
    for y in range(0, H, 60): d.line([(0, y), (W, y)], fill=gc, width=1)
    d.rectangle([m, m, m + 120, m + 14], fill=AMBER)
    scratch = ImageDraw.Draw(Image.new("RGB", (W, H)))
    h = content(scratch, s, 0, m, maxw, fg, sub)
    top, bottom = m + 60, H - m - 80
    y = max(top, top + (bottom - top - h) // 2 - 40)
    content(d, s, y, m, maxw, fg, sub)
    ff = font("SpaceGrotesk.ttf", 34, 600)
    d.text((m, H - m), brand, font=ff, fill=sub, anchor="ls")
    if total > 1:
        d.text((W - m, H - m), f"{idx+1}/{total}" + ("  →" if idx < total - 1 else ""), font=ff, fill=AMBER, anchor="rs")
    return im

def content(d, s, y, m, maxw, fg, sub):
    y0 = y
    if s.get("kicker"):
        f = font("SpaceGrotesk.ttf", 38, 600)
        d.text((m, y), s["kicker"].upper(), font=f, fill=AMBER); y += 80
    bs = s.get("size", 104)
    fb = font("SpaceGrotesk.ttf", bs, 700)
    for ln in wrap(d, s["big"], fb, maxw):
        d.text((m, y), ln, font=fb, fill=fg); y += int(bs * 1.12)
    y += 40
    if s.get("list"):
        fl = font("Inter.ttf", 50, 600)
        for i, it in enumerate(s["list"], 1):
            d.rectangle([m, y + 8, m + 58, y + 66], fill=AMBER)
            d.text((m + 29, y + 37), str(i), font=font("SpaceGrotesk.ttf", 40, 700), fill=NAVY, anchor="mm")
            for j, ln in enumerate(wrap(d, it, fl, maxw - 90)):
                d.text((m + 90, y + j * 64), ln, font=fl, fill=fg)
            y += 64 * len(wrap(d, it, fl, maxw - 90)) + 40
    if s.get("small"):
        fs = font("Inter.ttf", 50, 400)
        for ln in wrap(d, s["small"], fs, maxw):
            d.text((m, y), ln, font=fs, fill=sub); y += 68
    if s.get("cta"):
        y += 30; fc = font("SpaceGrotesk.ttf", 52, 700)
        tw = d.textlength(s["cta"], font=fc)
        d.rounded_rectangle([m, y, m + tw + 80, y + 104], radius=14, fill=AMBER)
        d.text((m + 40, y + 52), s["cta"], font=fc, fill=NAVY, anchor="lm"); y += 104
    return y - y0

SETS = {
 "facebook": [
  {"kicker": "Small Business Saturday", "big": "Can people actually find you?", "size": 120, "small": "It’s this weekend. Here’s what most Charlotte shops miss."},
  {"big": "They don’t pick the best shop.", "small": "They pick the one they can find — and the one that looks legit on their phone."},
  {"kicker": "Where customers slip away", "big": "3 silent deal-breakers", "size": 92, "list": ["Your site breaks on phones", "No hours, address or phone up top", "It looks like nobody’s home"]},
  {"big": "You put your whole life into this business.", "size": 92, "small": "It deserves to be found."},
  {"kicker": "Free this week", "big": "Website check-up", "small": "Send me your link (or tell me you don’t have one). I’ll give you an honest rundown.", "cta": "Message QC Web Co."},
 ],
 "instagram": [
  {"big": "I build websites after my kids go to bed.", "size": 112},
  {"big": "5 kids. A full-time warehouse job.", "size": 100, "small": "And a business I build at night."},
  {"big": "Every site I make, I build like my name is on it.", "size": 92, "small": "Because it is."},
  {"big": "Grinding the same way?", "size": 110, "small": "I see you. Let’s make your business look as serious as you are."},
  {"kicker": "Free website review", "big": "DM me “CHECK”", "size": 120, "cta": "@qcwebco"},
 ],
 "linkedin": [
  {"big": "I run a warehouse by day.", "size": 110, "small": "At night, I build the software I wish we’d had."},
  {"big": "Clipboards. Spreadsheets. “Where did that pallet go?”", "size": 92},
  {"big": "Nobody was lazy.", "size": 110, "small": "The tools were just bad."},
  {"kicker": "So I built my own", "big": "Tools from the floor up", "size": 88, "list": ["Inventory tracking with barcode scans", "Bin locations that make sense", "Dispatch, driver tickets & invoices in one app"]},
  {"big": "The people closest to the work know what’s broken.", "size": 88, "small": "Run a trucking company, warehouse or 3PL? Tell me what’s slowing your team down.", "cta": "Let’s talk"},
 ],
}
BRAND = "QC WEB CO. · CHARLOTTE"
for name, slides in SETS.items():
    imgs = [slide(s, 1080, 1350, i, len(slides), BRAND) for i, s in enumerate(slides)]
    for i, im in enumerate(imgs): im.save(f"{OUT}{name}_{i+1}.png")
    if name == "linkedin":
        imgs[0].save(OUT + "linkedin_carousel.pdf", save_all=True, append_images=imgs[1:], resolution=150)
    if name == "instagram":
        rd = OUT + "reel/"; os.makedirs(rd, exist_ok=True)
        for i, s in enumerate(slides):
            slide(s, 1080, 1920, i, 1, BRAND).save(f"{rd}{i}.png")
        # 2.6s per slide with crossfades
        inputs = [];
        for i in range(len(slides)): inputs += ["-loop", "1", "-t", "3.0", "-i", f"{rd}{i}.png"]
        fc = ""; prev = "[0:v]"; off = 0
        for i in range(1, len(slides)):
            off += 2.6
            out = f"[v{i}]"
            fc += f"{prev}[{i}:v]xfade=transition=slideleft:duration=0.4:offset={off:.1f}{out};"; prev = out
        fc += f"{prev}format=yuv420p[vout]"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", fc, "-map", "[vout]", "-r", "30",
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-movflags", "+faststart", OUT + "instagram_reel.mp4"], check=True)
print(sorted(os.listdir(OUT)))
