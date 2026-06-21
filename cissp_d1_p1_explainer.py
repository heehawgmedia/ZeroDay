from manim import *
import json
import os
import random
import subprocess

# Ensure all Text() calls default to DejaVu Sans — prevents VPS monospace fallback
import manim as _manim
class Text(_manim.Text):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('font', 'DejaVu Sans')
        super().__init__(*args, **kwargs)

# ─── Color Palette ───────────────────────────────────────────────
BG    = "#0A0E1A"
BLUE  = "#00C8FF"
AMBER = "#F5A623"
GREEN = "#39D353"
RED   = "#FF4D4D"
GRAY  = "#778899"
MONO  = "DejaVu Sans Mono"

config.background_color = BG

AUDIO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cissp_d1_p1_audio")

_DUR_DEFAULTS = {
    "s0":  22.0,   # ebook ad
    "s1":  52.0,   # hook + roadmap
    "s2":  82.0,   # ISC2 ethics
    "s3":  82.0,   # five pillars
    "s4":  72.0,   # governance
    "s5":  38.0,   # org processes
    "s6":  58.0,   # roles
    "s7":  68.0,   # due care vs diligence
    "s8":  58.0,   # frameworks
    "s9":  22.0,   # compliance
    "s10": 54.0,   # rapid-fire Q&A
    "s11": 44.0,   # recap + CTA
}
_dur_file = os.path.join(AUDIO, "durations.json")
if os.path.exists(_dur_file):
    with open(_dur_file) as _f:
        DUR = {**_DUR_DEFAULTS, **json.load(_f)}
else:
    DUR = _DUR_DEFAULTS

# ─── Helpers ─────────────────────────────────────────────────────
def mono(text, size=20, color=WHITE, **kw):
    return Text(text, font=MONO, font_size=size, color=color, **kw)

def heading(text, size=36, color=WHITE, **kw):
    return Text(text, font_size=size, color=color, weight=BOLD, **kw)

def scene_title(scene, text, color=WHITE):
    t = heading(text, size=30, color=color)
    t.to_edge(UP, buff=0.38)
    bar = Line(LEFT*6.5, RIGHT*6.5, color=color, stroke_width=1.5)
    bar.next_to(t, DOWN, buff=0.1)
    scene.play(Write(t), Create(bar), run_time=0.6)
    return VGroup(t, bar)

def exam_tip(scene, text, anchor=None, buff=0.3, **_):
    prefix = Text("▶ EXAM TIP:", font_size=14, color=RED, weight=BOLD)
    body   = Text(text, font_size=14, color=AMBER)
    grp    = VGroup(prefix, body).arrange(RIGHT, buff=0.28)
    uline  = Line(grp.get_left(), grp.get_right(),
                  color=RED, stroke_width=1.0, stroke_opacity=0.5)
    uline.next_to(grp, DOWN, buff=0.07)
    badge = VGroup(grp, uline)
    if anchor:
        badge.next_to(anchor, DOWN, buff=buff)
    else:
        badge.to_edge(UP, buff=1.0)
    scene.play(FadeIn(badge, shift=DOWN*0.1), run_time=0.5)
    return badge


def _ffprobe_seconds(path: str) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True,
    )
    return float(out.stdout.strip())


def _preflight_audio(audio_dir: str, defaults: dict, generator: str) -> None:
    """Fail loudly before rendering if any audio is missing or suspiciously short.

    `defaults` must be the hardcoded _DUR_DEFAULTS dict (conservative estimates),
    NOT the runtime DUR loaded from durations.json — comparing actual vs measured
    is circular and misses ElevenLabs stream truncation.
    """
    bad = []
    for key in defaults:
        path = os.path.join(audio_dir, f"{key}.mp3")
        if not os.path.exists(path) or os.path.getsize(path) < 1024:
            bad.append(key)
            continue
        try:
            actual = _ffprobe_seconds(path)
            # 60% of the conservative default is a safe floor:
            # fast voices (~4 wps) produce audio at ~70-80% of the 2.4-wps default,
            # so genuine truncation at <50% is caught while fast speech passes.
            if actual < defaults[key] * 0.60:
                bad.append(key)
        except Exception:
            bad.append(key)
    if bad:
        keys = " ".join(bad)
        raise RuntimeError(
            f"\n{'='*60}\n"
            f"  MISSING / TRUNCATED AUDIO — DO NOT RENDER\n"
            f"{'='*60}\n"
            f"  Files missing, too small, or too short: {keys}\n"
            f"  Fix: python {generator} --force --only {keys}\n"
            f"{'='*60}\n"
        )


# ═══════════════════════════════════════════════════════════════════
#  CISSP D1-P1 SCENE  —  manim -qh cissp_d1_p1_explainer.py CISSPS_D1P1
# ═══════════════════════════════════════════════════════════════════
class CISSP_D1P1(Scene):
    def construct(self):
        _preflight_audio(AUDIO, _DUR_DEFAULTS, "generate_cissp_d1_p1_narration.py")
        self.s0_ad()
        self.s1_hook_roadmap()
        self.s2_ethics()
        self.s3_five_pillars()
        self.s4_governance()
        self.s5_org_processes()
        self.s6_roles()
        self.s7_due_care()
        self.s8_frameworks()
        self.s9_compliance()
        self.s10_practice_questions()
        self.s11_recap_cta()

    # ── Background ───────────────────────────────────────────────
    def _tech_bg(self) -> VGroup:
        rng = random.Random(42)

        # Dark base + subtle center glow for depth
        base = Rectangle(
            width=config.frame_width + 0.5, height=config.frame_height + 0.5,
            fill_color="#04080F", fill_opacity=1, stroke_width=0,
        )
        glow = Ellipse(width=13, height=8.5,
                       fill_color="#0A1830", fill_opacity=0.55, stroke_width=0)

        # Faint horizontal grid lines
        grid = VGroup(*[
            Line(LEFT*8, RIGHT*8, stroke_width=0.45,
                 color="#0D2040", stroke_opacity=1).shift(UP*y)
            for y in [-3.0, -1.5, 0.0, 1.5, 3.0]
        ])

        # PCB-style circuit traces in corners
        _C = "#00C8FF"
        trace_segs = [
            ((-7.1, 2.8), (-5.2, 2.8)), ((-5.2, 2.8), (-5.2, 1.8)),
            ((-6.1, 1.8), (-5.2, 1.8)),
            ((7.1, 2.8),  (5.2, 2.8)),  ((5.2, 2.8),  (5.2, 1.8)),
            ((5.2, 1.8),  (6.1, 1.8)),
            ((-7.1, -2.8), (-5.5, -2.8)), ((-5.5, -2.8), (-5.5, -1.9)),
            ((7.1, -2.8),  (5.5, -2.8)),  ((5.5, -2.8),  (5.5, -2.0)),
            ((5.5, -2.0),  (6.3, -2.0)),
        ]
        traces = VGroup(*[
            Line([s[0], s[1], 0], [e[0], e[1], 0],
                 stroke_width=1.1, color=_C, stroke_opacity=0.20)
            for s, e in trace_segs
        ])
        node_pts = [(-5.2, 1.8), (-6.1, 1.8), (5.2, 1.8), (6.1, 1.8),
                    (-5.5, -1.9), (5.5, -2.0), (6.3, -2.0)]
        nodes = VGroup(*[
            Dot([x, y, 0], radius=0.045, color=_C).set_opacity(0.30)
            for x, y in node_pts
        ])

        # Corner brackets (more visible, with corner dot)
        corners = [
            ((-6.9, 3.6), (1, -1)), ((6.9, 3.6), (-1, -1)),
            ((-6.9,-3.6), (1,  1)), ((6.9,-3.6), (-1,  1)),
        ]
        brackets = VGroup(*[
            VGroup(
                Line([cx,cy,0],[cx+dx*1.05,cy,0],
                     stroke_width=1.6, color=_C, stroke_opacity=0.32),
                Line([cx,cy,0],[cx,cy+dy*1.05,0],
                     stroke_width=1.6, color=_C, stroke_opacity=0.32),
                Dot([cx, cy, 0], radius=0.04, color=_C).set_opacity(0.40),
            )
            for (cx,cy),(dx,dy) in corners
        ])

        # Hex dot field — mostly blue, some purple for variety
        _palette = [_C]*6 + ["#7744CC"]
        hex_dots = VGroup()
        for r in range(13):
            for c in range(20):
                if rng.random() < 0.72:
                    x = -8.8 + c*0.95 + (0.47 if r%2 else 0)
                    y = -4.0 + r*0.68
                    col = _palette[rng.randint(0, len(_palette)-1)]
                    hex_dots.add(
                        Dot([x,y,0], radius=0.024, color=col)
                        .set_opacity(rng.uniform(0.04, 0.13))
                    )

        # Side tick marks
        ticks = VGroup()
        for y_off in [-0.6, 0.0, 0.6]:
            for xd, xr in [(-7.1, -6.8), (7.1, 6.8)]:
                ticks.add(Line([xd, y_off, 0], [xr, y_off, 0],
                               stroke_width=1.0, color=_C, stroke_opacity=0.22))

        bg = VGroup(base, glow, grid, traces, nodes, brackets, hex_dots, ticks)
        self.add(bg)
        return bg

    def _fade_content(self, bg: VGroup, run_time=0.5):
        content = [m for m in self.mobjects if m is not bg]
        if content:
            self.play(FadeOut(*content), run_time=run_time)
        self.remove(bg)

    def _sound(self, key):
        try:
            self._scene_start = self.time
        except AttributeError:
            self._scene_start = 0.0
        self.add_sound(f"{AUDIO}/{key}.mp3")

    def _pad(self, key, used=0):
        try:
            scene_elapsed = self.time - getattr(self, '_scene_start', 0.0)
        except AttributeError:
            scene_elapsed = used
        remaining = DUR[key] - scene_elapsed - 0.3
        if remaining > 0:
            self.wait(remaining)

    # ── SCENE 0 — Ebook Ad ───────────────────────────────────────
    def s0_ad(self):
        bg = self._tech_bg()
        self._sound("s0")
        ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
        cover_path = os.path.join(ASSETS, "Think Like A CISSP Cover.jpg")

        sponsor = Text("A MESSAGE FROM ZERO DAY LABS", font_size=13, color=AMBER, weight=BOLD)
        sponsor.to_edge(UP, buff=0.28)
        sline = Line(LEFT*6, RIGHT*6, color=AMBER, stroke_width=0.8)
        sline.next_to(sponsor, DOWN, buff=0.1)
        self.play(FadeIn(sponsor), Create(sline), run_time=0.5)

        if os.path.exists(cover_path):
            cover = ImageMobject(cover_path)
            cover.set_height(5.5).move_to(LEFT*3.3 + DOWN*0.2)
            glow = RoundedRectangle(corner_radius=0.12, width=cover.width+0.12,
                                    height=cover.height+0.12, color=GREEN,
                                    stroke_width=2, fill_opacity=0)
            glow.move_to(cover.get_center())
            self.play(FadeIn(cover, scale=0.92), run_time=0.9)
            self.play(Create(glow), run_time=0.4)
        else:
            ph = RoundedRectangle(corner_radius=0.2, width=3.2, height=5.5,
                                   color=GREEN, fill_color="#051A05", fill_opacity=0.9, stroke_width=2)
            ph.move_to(LEFT*3.3 + DOWN*0.2)
            self.play(FadeIn(ph), run_time=0.5)

        rx = RIGHT*1.8
        t1 = heading("Think Like", size=44, color=WHITE); t1.move_to(rx + UP*1.7)
        t2 = heading("A CISSP",   size=54, color=BLUE);  t2.next_to(t1, DOWN, buff=0.08).align_to(t1, LEFT)
        self.play(Write(t1), run_time=0.6); self.play(Write(t2), run_time=0.5)
        div = Line(ORIGIN, RIGHT*4.8, color=BLUE, stroke_width=1.2)
        div.next_to(t2, DOWN, buff=0.22).align_to(t1, LEFT)
        self.play(Create(div), run_time=0.3)
        tag1 = Text("Master the mindset that separates candidates", font_size=16, color=WHITE)
        tag2 = Text("who pass from engineers who fail.", font_size=16, color=WHITE)
        tag1.next_to(div, DOWN, buff=0.2).align_to(t1, LEFT)
        tag2.next_to(tag1, DOWN, buff=0.1).align_to(t1, LEFT)
        self.play(FadeIn(tag1, shift=UP*0.1), run_time=0.4)
        self.play(FadeIn(tag2, shift=UP*0.1), run_time=0.4)
        pbg = RoundedRectangle(corner_radius=0.18, width=1.7, height=0.65,
                               fill_color=AMBER, fill_opacity=1, stroke_width=0)
        ptxt = Text("$25.00", font_size=23, color="#0A0E1A", weight=BOLD)
        pbg.next_to(tag2, DOWN, buff=0.35).align_to(t1, LEFT)
        ptxt.move_to(pbg.get_center())
        self.play(FadeIn(pbg, scale=0.8), Write(ptxt), run_time=0.5)
        url = mono("zerodaylabs.tech/store/think-like-a-cissp", size=13, color=BLUE)
        url.next_to(pbg, DOWN, buff=0.22).align_to(t1, LEFT)
        self.play(Write(url), run_time=0.5)
        self.wait(1.5)
        self.play(pbg.animate.set_fill(color="#FFD700"), run_time=0.3)
        self.play(pbg.animate.set_fill(color=AMBER), run_time=0.3)
        self._pad("s0", 8.0)
        self._fade_content(bg)

    # ── SCENE 1 — Hook + Roadmap ─────────────────────────────────
    def s1_hook_roadmap(self):
        bg = self._tech_bg()

        welcome = Text("Welcome back to Zero Day Labs!", font_size=38, color=BLUE, weight=BOLD)
        welcome.move_to(ORIGIN)
        self.play(Write(welcome), run_time=0.8)
        self.wait(1.5)
        self.play(FadeOut(welcome), run_time=0.5)

        self._sound("s1")

        # Cold open: single question
        question = Text("You identified the risk. Did you act on it?",
                        font_size=34, color=WHITE, weight=BOLD)
        question.move_to(UP * 0.3)
        self.play(Write(question), run_time=1.2)               # t≈1.2
        self.wait(3.0)                                         # t≈4.2

        breach_lines = VGroup(
            Text("• CISO flagged the vulnerability last quarter.", font_size=19, color=GRAY),
            Text("• Board approved the budget.", font_size=19, color=GRAY),
            Text("• Controls were documented in policy.", font_size=19, color=GRAY),
            Text("• Nobody acted on the findings.", font_size=19, color=RED, weight=BOLD),
        ).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        breach_lines.next_to(question, DOWN, buff=0.5)
        for line in breach_lines:
            self.play(FadeIn(line, shift=RIGHT*0.2), run_time=0.35)
        self.wait(3.5)                                         # t≈11.2

        self._fade_content(bg, run_time=0.4)
        bg2 = self._tech_bg()

        # Series title card
        series = Text("CISSP Domain Mastery Series", font_size=20, color=GRAY)
        ep_title = heading("D1-P1  |  Security Concepts,\nGovernance & Ethics",
                           size=36, color=WHITE)
        ep_title.move_to(UP * 1.1)
        series.next_to(ep_title, UP, buff=0.3)
        self.play(FadeIn(series), Write(ep_title), run_time=0.9)   # t≈12.5

        obj_label = Text("Exam Objectives Covered:", font_size=17, color=AMBER, weight=BOLD)
        obj_label.next_to(ep_title, DOWN, buff=0.45)
        obj_nums = mono("1.1  |  1.2  |  1.3  |  1.5", size=20, color=BLUE)
        obj_nums.next_to(obj_label, DOWN, buff=0.2)
        self.play(FadeIn(obj_label), Write(obj_nums), run_time=0.6)   # t≈13.1

        topics = [
            "ISC2 Code of Ethics", "Five Security Pillars",
            "Governance & Business Alignment", "Roles & Responsibilities",
            "Due Care vs. Due Diligence", "Control Frameworks", "Compliance Overview",
        ]
        topic_group = VGroup(*[
            Text(f"• {t}", font_size=16, color=WHITE) for t in topics
        ]).arrange(DOWN, buff=0.14, aligned_edge=LEFT)
        topic_group.next_to(obj_nums, DOWN, buff=0.35)
        for t in topic_group:
            self.play(FadeIn(t, shift=RIGHT*0.15), run_time=0.2)
        # t≈15.5

        elapsed = 15.5
        self._pad("s1", elapsed)
        self._fade_content(bg2)

    # ── SCENE 2 — ISC2 Code of Ethics ────────────────────────────
    def s2_ethics(self):
        bg = self._tech_bg()
        self._sound("s2")

        scene_title(self, "ISC2 Code of Professional Ethics", color=BLUE)  # t≈0.6
        self.wait(0.4)

        canon_data = [
            ("1", "Protect Society",
             "…the common good, necessary public trust\nand confidence, and the infrastructure.",
             BLUE),
            ("2", "Act Honorably",
             "…honestly, justly, responsibly, and legally.",
             GREEN),
            ("3", "Provide Diligent Service",
             "…competent service to principals.\n(A principal = any party you serve.)",
             AMBER),
            ("4", "Advance the Profession",
             "…and protect the profession.\nLowest priority if canons conflict.",
             GRAY),
        ]

        all_canons = VGroup()
        for num, title, body, color in canon_data:
            row_bg = RoundedRectangle(corner_radius=0.16, width=11.8, height=1.0,
                                      color=color, fill_color=BG,
                                      fill_opacity=0.95, stroke_width=2)
            num_circle = Circle(radius=0.30, color=color, fill_color=color,
                                fill_opacity=1, stroke_width=0)
            num_txt = Text(num, font_size=20, color=BG, weight=BOLD)
            num_circle.move_to(row_bg.get_left() + RIGHT*0.52)
            num_txt.move_to(num_circle.get_center())
            title_mob = Text(title, font_size=18, color=color, weight=BOLD)
            # Left-align title starting after the circle so long titles don't overlap
            title_mob.next_to(num_circle, RIGHT, buff=0.22)
            title_mob.set_y(row_bg.get_center()[1])
            body_mob = Text(body, font_size=13, color=WHITE, line_spacing=1.2,
                            font="DejaVu Sans")
            body_mob.move_to(row_bg.get_right() + LEFT*3.2)
            body_mob.set_y(row_bg.get_center()[1])
            all_canons.add(VGroup(row_bg, num_circle, num_txt, title_mob, body_mob))

        all_canons.arrange(DOWN, buff=0.15)
        all_canons.move_to(DOWN * 0.2)

        elapsed = 1.0
        for i, canon in enumerate(all_canons):
            self.play(FadeIn(canon, shift=RIGHT*0.2), run_time=0.6)
            dwell = [10.0, 8.0, 8.0, 8.0][i]
            self.wait(dwell)
            elapsed += 0.6 + dwell
        # elapsed ≈ 36.4

        tip = exam_tip(self, "Order is exam-tested — Society → Honor → Service → Profession")
        elapsed += 0.9
        self.wait(3.5)
        elapsed += 3.5

        self.play(FadeOut(tip), run_time=0.3)
        mnemonic_bg = RoundedRectangle(corner_radius=0.16, width=7.0, height=0.65,
                                        color=GREEN, fill_color="#05140A",
                                        fill_opacity=1, stroke_width=1.5)
        mnemonic_bg.to_edge(DOWN, buff=0.35)
        mnemonic_txt = Text("SHSP  —  Security Has Strong Principles",
                            font_size=18, color=GREEN, weight=BOLD)
        mnemonic_txt.move_to(mnemonic_bg.get_center())
        self.play(FadeIn(mnemonic_bg), Write(mnemonic_txt), run_time=0.6)
        self.wait(4.0)
        elapsed += 5.3

        # Org code note
        note = Text("Org codes of ethics are subordinate to the ISC2 code if they conflict.",
                    font_size=17, color=GRAY)
        note.next_to(mnemonic_bg, UP, buff=0.25)
        self.play(FadeIn(note), run_time=0.4)
        self.wait(3.0)
        elapsed += 3.4

        self._pad("s2", elapsed)
        self._fade_content(bg)

    # ── SCENE 3 — Five Pillars ────────────────────────────────────
    def s3_five_pillars(self):
        bg = self._tech_bg()
        self._sound("s3")

        scene_title(self, "The Five Security Pillars", color=BLUE)         # t≈0.6

        pillar_data = [
            ("Confidentiality", "Only authorized entities can access the information.",
             "Misconfigured S3 bucket, data breach", BLUE),
            ("Integrity",       "Data is accurate and unmodified without authorization.",
             "Altered transaction in transit, tampering", GREEN),
            ("Availability",    "Authorized users can access systems when needed.",
             "DoS attack, ransomware encryption", AMBER),
            ("Authenticity",    "The identity of an entity is genuine and verifiable.",
             "Spoofed email, identity forgery", "#AA44FF"),
            ("Nonrepudiation",  "A party cannot deny having performed an action.",
             "Unsigned transactions, deniable logs", RED),
        ]

        # Header row
        hdr = VGroup(
            Text("PILLAR", font_size=14, color=GRAY, weight=BOLD),
            Text("DEFINITION", font_size=14, color=GRAY, weight=BOLD),
            Text("VIOLATED BY", font_size=14, color=GRAY, weight=BOLD),
        )
        hdr[0].move_to(LEFT*5.5 + UP*2.0)
        hdr[1].move_to(LEFT*1.2 + UP*2.0)
        hdr[2].move_to(RIGHT*3.8 + UP*2.0)
        hdr_line = Line(LEFT*6.8, RIGHT*6.8, color=GRAY, stroke_width=0.8, stroke_opacity=0.5)
        hdr_line.move_to(UP*1.75)
        self.play(FadeIn(hdr), Create(hdr_line), run_time=0.5)

        elapsed = 1.1
        rows = []
        for i, (name, defn, violation, color) in enumerate(pillar_data):
            y = 1.2 - i * 0.92
            name_mob = Text(name, font_size=17, color=color, weight=BOLD)
            name_mob.move_to(LEFT*5.5 + UP*y)
            defn_mob = Text(defn, font_size=13, color=WHITE, line_spacing=1.1)
            defn_mob.move_to(LEFT*1.2 + UP*y)
            viol_mob = Text(violation, font_size=13, color=GRAY, line_spacing=1.1)
            viol_mob.move_to(RIGHT*3.8 + UP*y)
            sep = Line(LEFT*6.8, RIGHT*6.8, stroke_width=0.4, color="#223344", stroke_opacity=0.5)
            sep.move_to(UP*(y - 0.45))
            row = VGroup(name_mob, defn_mob, viol_mob, sep)
            rows.append(row)
            self.play(FadeIn(row, shift=UP*0.12), run_time=0.45)
            self.wait(6.5)
            elapsed += 6.95
        # elapsed ≈ 36.0

        tip = exam_tip(self,
            "Authenticity = identity is genuine  |  Nonrepudiation = action cannot be denied later")
        elapsed += 0.9
        self.wait(5.0)
        elapsed += 5.0

        self._pad("s3", elapsed)
        self._fade_content(bg)

    # ── SCENE 4 — Security Governance ────────────────────────────
    def s4_governance(self):
        bg = self._tech_bg()
        self._sound("s4")

        scene_title(self, "Security Governance", color=BLUE)               # t≈0.6

        # CEO mindset callout
        ceo_bg = RoundedRectangle(corner_radius=0.18, width=11.5, height=0.78,
                                   color=AMBER, fill_color="#1A0D00",
                                   fill_opacity=1, stroke_width=2)
        ceo_bg.move_to(UP*2.0)
        ceo_txt = Text("Think like a CEO, not an engineer  —  governance is oversight, not operations.",
                       font_size=18, color=WHITE, weight=BOLD)
        ceo_txt.move_to(ceo_bg.get_center())
        self.play(FadeIn(ceo_bg), Write(ceo_txt), run_time=0.7)            # t≈1.3
        self.wait(4.0)                                                     # t≈5.3

        # Governance pyramid — wider bars at each tier, labels flush to bar edges
        levels = [
            ("Board of Directors",      "Sets risk appetite · holds accountability", BLUE,   7.5, 10.0),
            ("Executive Leadership",    "Owns risk · approves security strategy",    GREEN,  9.5,  9.0),
            ("CISO / Security Team",    "Advises · implements · monitors · reports", AMBER, 11.5,  9.0),
            ("Operations / Custodians", "Executes controls day to day",              GRAY,  13.0,  8.0),
        ]

        elapsed = 5.3
        for i, (label, desc, color, bar_w, dwell) in enumerate(levels):
            cy = 0.98 - i * 0.77
            bar = Rectangle(width=bar_w, height=0.65,
                            color=color, fill_color=BG, fill_opacity=0.9, stroke_width=2)
            bar.move_to([0, cy, 0])
            bar_label = Text(label, font_size=14, color=color, weight=BOLD)
            bar_label.next_to(bar.get_left(), RIGHT, buff=0.35)
            bar_label.set_y(cy)
            bar_desc = Text(desc, font_size=12, color=WHITE)
            bar_desc.next_to(bar.get_right(), LEFT, buff=0.35)
            bar_desc.set_y(cy)
            grp = VGroup(bar, bar_label, bar_desc)
            self.play(FadeIn(grp, shift=LEFT*0.2), run_time=0.5)
            self.wait(dwell)
            elapsed += 0.5 + dwell

        # t≈42.3

        enabler_bg = RoundedRectangle(corner_radius=0.14, width=9.5, height=0.65,
                                       color=GREEN, fill_color="#051A0A",
                                       fill_opacity=1, stroke_width=1.5)
        enabler_bg.to_edge(DOWN, buff=0.35)
        enabler_txt = Text("Security is a business ENABLER — not a cost center, not a blocker.",
                           font_size=17, color=GREEN, weight=BOLD)
        enabler_txt.move_to(enabler_bg.get_center())
        self.play(FadeIn(enabler_bg), Write(enabler_txt), run_time=0.6)    # t≈42.9
        self.wait(4.5)
        elapsed += 5.1

        self._pad("s4", elapsed)
        self._fade_content(bg)

    # ── SCENE 5 — Organizational Processes ───────────────────────
    def s5_org_processes(self):
        bg = self._tech_bg()
        self._sound("s5")

        scene_title(self, "Organizational Processes", color=AMBER)         # t≈0.6

        col_data = [
            ("ACQUISITIONS", [
                "Review target's security posture",
                "Audit compliance obligations",
                "Identify inherited liabilities",
                "Discover legacy risks before signing",
            ], BLUE),
            ("DIVESTITURES", [
                "Sanitize transferred systems",
                "Revoke access credentials",
                "Classify & protect remaining data",
                "Confirm data ownership post-split",
            ], AMBER),
        ]

        cols = VGroup()
        for title_str, items, color in col_data:
            col_bg = RoundedRectangle(corner_radius=0.18, width=5.4, height=3.6,
                                      color=color, fill_color=BG,
                                      fill_opacity=0.95, stroke_width=2)
            col_title = Text(title_str, font_size=19, color=color, weight=BOLD)
            col_title.move_to(col_bg.get_top() + DOWN*0.38)
            col_items = VGroup(*[
                Text(f"• {it}", font_size=15, color=WHITE) for it in items
            ]).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
            col_items.move_to(col_bg.get_center() + DOWN*0.25)
            cols.add(VGroup(col_bg, col_title, col_items))

        cols.arrange(RIGHT, buff=0.6)
        cols.move_to(DOWN*0.15)
        self.play(FadeIn(cols, shift=UP*0.15), run_time=0.8)               # t≈1.4
        self.wait(12.0)                                                    # t≈13.4

        committee_txt = Text(
            "Governance committees (audit, risk, IS steering) provide oversight — they do not run operations.",
            font_size=17, color=GRAY
        )
        committee_txt.to_edge(DOWN, buff=0.55)
        self.play(FadeIn(committee_txt), run_time=0.4)                     # t≈13.8
        self.wait(5.0)
        elapsed = 18.8

        self._pad("s5", elapsed)
        self._fade_content(bg)

    # ── SCENE 6 — Roles & Responsibilities ───────────────────────
    def s6_roles(self):
        bg = self._tech_bg()
        self._sound("s6")

        scene_title(self, "Roles & Responsibilities", color=BLUE)          # t≈0.6

        # Senior Mgmt vs Security Professionals
        owns_bg = RoundedRectangle(corner_radius=0.18, width=5.5, height=1.9,
                                    color=RED, fill_color="#1A0000",
                                    fill_opacity=0.95, stroke_width=2)
        owns_bg.move_to(LEFT*3.2 + UP*1.25)
        owns_title = Text("Senior Management", font_size=19, color=RED, weight=BOLD)
        owns_title.next_to(owns_bg.get_top(), DOWN, buff=0.22)
        owns_body = Text("OWNS risk.\nUltimately accountable.\nCannot delegate risk ownership.",
                         font_size=15, color=WHITE, line_spacing=1.3)
        owns_body.move_to(owns_bg.get_center() + DOWN*0.18)

        adv_bg = RoundedRectangle(corner_radius=0.18, width=5.5, height=1.9,
                                   color=BLUE, fill_color="#001528",
                                   fill_opacity=0.95, stroke_width=2)
        adv_bg.move_to(RIGHT*3.2 + UP*1.25)
        adv_title = Text("Security Professionals", font_size=19, color=BLUE, weight=BOLD)
        adv_title.next_to(adv_bg.get_top(), DOWN, buff=0.22)
        adv_body = Text("ADVISE on risk.\nAssess, design, implement, monitor.\nProvide inputs for decisions.",
                        font_size=15, color=WHITE, line_spacing=1.3)
        adv_body.move_to(adv_bg.get_center() + DOWN*0.18)

        self.play(
            FadeIn(owns_bg), Write(owns_title), FadeIn(owns_body),
            FadeIn(adv_bg),  Write(adv_title),  FadeIn(adv_body),
            run_time=0.8
        )                                                                  # t≈1.4
        self.wait(8.0)                                                     # t≈9.4

        tip = exam_tip(self, "Who is ULTIMATELY responsible for information security?  Senior Management.  Always.")
        self.wait(3.5)                                                     # t≈13.8
        self.play(FadeOut(tip), run_time=0.3)

        # Data Owner vs Data Custodian
        do_bg = RoundedRectangle(corner_radius=0.18, width=5.5, height=1.9,
                                  color=GREEN, fill_color="#051A0A",
                                  fill_opacity=0.95, stroke_width=2)
        do_bg.move_to(LEFT*3.2 + DOWN*1.5)
        do_title = Text("Data Owner", font_size=19, color=GREEN, weight=BOLD)
        do_title.next_to(do_bg.get_top(), DOWN, buff=0.22)
        do_body = Text("Business role (manager/exec).\nClassifies data.\nSets access rules.",
                       font_size=15, color=WHITE, line_spacing=1.3)
        do_body.move_to(do_bg.get_center() + DOWN*0.12)

        dc_bg = RoundedRectangle(corner_radius=0.18, width=5.5, height=1.9,
                                  color=AMBER, fill_color="#1A0D00",
                                  fill_opacity=0.95, stroke_width=2)
        dc_bg.move_to(RIGHT*3.2 + DOWN*1.5)
        dc_title = Text("Data Custodian", font_size=19, color=AMBER, weight=BOLD)
        dc_title.next_to(dc_bg.get_top(), DOWN, buff=0.22)
        dc_body = Text("Technical role (IT/ops).\nImplements controls.\nFollows the owner's rules.",
                       font_size=15, color=WHITE, line_spacing=1.3)
        dc_body.move_to(dc_bg.get_center() + DOWN*0.12)

        self.play(
            FadeIn(do_bg), Write(do_title), FadeIn(do_body),
            FadeIn(dc_bg), Write(dc_title), FadeIn(dc_body),
            run_time=0.8
        )                                                                  # t≈14.9
        self.wait(9.0)                                                     # t≈23.9

        trap_txt = Text("Owner decides.  Custodian implements.  Never blend them in an answer.",
                        font_size=18, color=RED, weight=BOLD)
        trap_txt.to_edge(DOWN, buff=0.55)
        self.play(Write(trap_txt), run_time=0.5)                           # t≈24.4
        self.wait(4.0)
        elapsed = 28.4

        self._pad("s6", elapsed)
        self._fade_content(bg)

    # ── SCENE 7 — Due Care vs. Due Diligence ─────────────────────
    def s7_due_care(self):
        bg = self._tech_bg()
        self._sound("s7")

        scene_title(self, "Due Care vs. Due Diligence", color=AMBER)       # t≈0.6

        # Two columns
        dd_bg = RoundedRectangle(corner_radius=0.18, width=5.6, height=4.4,
                                  color=BLUE, fill_color="#001528",
                                  fill_opacity=0.95, stroke_width=2.5)
        dd_bg.move_to(LEFT*3.1 + DOWN*0.3)
        dd_head = heading("DUE DILIGENCE", size=22, color=BLUE)
        dd_head.next_to(dd_bg.get_top(), DOWN, buff=0.25)
        dd_items = VGroup(
            Text("The RESEARCH phase", font_size=16, color=BLUE, weight=BOLD),
            Text("Investigate + understand risks", font_size=15, color=WHITE),
            Text("Evaluate requirements", font_size=15, color=WHITE),
            Text("Before making a decision", font_size=15, color=GREEN, weight=BOLD),
            Text('The "KNOWING"', font=MONO, font_size=16, color=WHITE),
            Text("e.g. Review vendor SOC 2 report", font_size=14, color=GRAY),
        ).arrange(DOWN, buff=0.26, aligned_edge=LEFT)
        dd_items.move_to(dd_bg.get_center() + DOWN*0.25)

        dc_bg = RoundedRectangle(corner_radius=0.18, width=5.6, height=4.4,
                                  color=GREEN, fill_color="#051A0A",
                                  fill_opacity=0.95, stroke_width=2.5)
        dc_bg.move_to(RIGHT*3.1 + DOWN*0.3)
        dc_head = heading("DUE CARE", size=22, color=GREEN)
        dc_head.next_to(dc_bg.get_top(), DOWN, buff=0.25)
        dc_items = VGroup(
            Text("The ACTION phase", font_size=16, color=GREEN, weight=BOLD),
            Text("Implement appropriate controls", font_size=15, color=WHITE),
            Text("Act on what you know", font_size=15, color=WHITE),
            Text("After learning the risk", font_size=15, color=GREEN, weight=BOLD),
            Text('The "DOING"', font=MONO, font_size=16, color=WHITE),
            Text("e.g. Patch the known vulnerability", font_size=14, color=GRAY),
        ).arrange(DOWN, buff=0.26, aligned_edge=LEFT)
        dc_items.move_to(dc_bg.get_center() + DOWN*0.25)

        self.play(
            FadeIn(dd_bg), Write(dd_head), FadeIn(dd_items),
            FadeIn(dc_bg), Write(dc_head), FadeIn(dc_items),
            run_time=0.9
        )                                                                  # t≈1.5
        self.wait(12.0)                                                    # t≈13.5

        tip1 = exam_tip(self, "Diligence = Discovery (before)  |  Care = Conduct (after)")
        self.wait(3.5)                                                     # t≈17.9
        self.play(FadeOut(tip1), run_time=0.3)

        neg_bg = RoundedRectangle(corner_radius=0.14, width=9.5, height=0.65,
                                   color=RED, fill_color="#1A0000",
                                   fill_opacity=1, stroke_width=2)
        neg_bg.to_edge(DOWN, buff=0.35)
        neg_txt = Text("Knowing without acting = NEGLIGENCE.  Courts and ISC2 apply the prudent person standard.",
                       font_size=16, color=WHITE, weight=BOLD)
        neg_txt.move_to(neg_bg.get_center())
        self.play(FadeIn(neg_bg), Write(neg_txt), run_time=0.6)            # t≈18.8
        self.wait(6.0)
        elapsed = 24.8

        self._pad("s7", elapsed)
        self._fade_content(bg)

    # ── SCENE 8 — Control Frameworks ─────────────────────────────
    def s8_frameworks(self):
        bg = self._tech_bg()
        self._sound("s8")

        scene_title(self, "Security Control Frameworks", color=BLUE)       # t≈0.6

        fw_data = [
            ("ISO/IEC 27001",  "ISMS Certification",      "Global",          "Voluntary*",  BLUE),
            ("NIST CSF",       "Risk-based posture",      "Critical infra",  "Voluntary*",  GREEN),
            ("COBIT",          "IT Governance",           "Enterprise IT",   "Voluntary",   AMBER),
            ("SABSA",          "Security Architecture",   "Enterprise",      "Voluntary",   "#AA44FF"),
            ("PCI DSS",        "Payment card security",   "Card-processing", "Mandatory",   RED),
            ("FedRAMP",        "Cloud authorization",     "US Federal",      "Mandatory",   RED),
        ]

        # Header
        hdr_labels = ["FRAMEWORK", "PURPOSE", "SCOPE", "REQUIRED?"]
        hdr_x = [-5.0, -1.6, 2.0, 4.8]
        hdr_group = VGroup(*[
            Text(h, font_size=13, color=GRAY, weight=BOLD).move_to([hdr_x[i], 2.6, 0])
            for i, h in enumerate(hdr_labels)
        ])
        hdr_line = Line(LEFT*6.5, RIGHT*6.5, stroke_width=0.8, color=GRAY, stroke_opacity=0.4)
        hdr_line.move_to(UP*2.35)
        self.play(FadeIn(hdr_group), Create(hdr_line), run_time=0.4)       # t≈1.0

        elapsed = 1.0
        for i, (name, purpose, scope, req, color) in enumerate(fw_data):
            y = 1.88 - i * 0.72
            req_color = RED if req == "Mandatory" else GRAY
            row = VGroup(
                Text(name,    font_size=16, color=color, weight=BOLD).move_to([hdr_x[0], y, 0]),
                Text(purpose, font_size=14, color=WHITE).move_to([hdr_x[1], y, 0]),
                Text(scope,   font_size=14, color=WHITE).move_to([hdr_x[2], y, 0]),
                Text(req,     font_size=14, color=req_color, weight=BOLD).move_to([hdr_x[3], y, 0]),
            )
            sep = Line(LEFT*6.5, RIGHT*6.5, stroke_width=0.3, color="#223344", stroke_opacity=0.4)
            sep.move_to(UP*(y - 0.33))
            self.play(FadeIn(row), Create(sep), run_time=0.4)
            self.wait(4.5)
            elapsed += 4.9

        # t≈30.4

        note = Text("* Voluntary in adoption — market-driven or sector-required in practice.",
                    font_size=14, color=GRAY)
        note.to_edge(DOWN, buff=0.45)
        self.play(FadeIn(note), run_time=0.35)
        self.wait(4.0)
        elapsed += 4.35

        self._pad("s8", elapsed)
        self._fade_content(bg)

    # ── SCENE 9 — Compliance Overview ────────────────────────────
    def s9_compliance(self):
        bg = self._tech_bg()
        self._sound("s9")

        scene_title(self, "Compliance Obligations", color=AMBER)           # t≈0.6

        comp_data = [
            ("CONTRACTUAL", "SLA, vendor contract,\nclient agreement", "Breach of contract", BLUE),
            ("LEGAL",       "HIPAA, GDPR, CCPA,\nstate laws",          "Civil/criminal liability", GREEN),
            ("REGULATORY",  "SEC, FINRA, CISA,\nsector regulators",    "Fines, sanctions, license loss", RED),
        ]

        cols = VGroup()
        for cat, examples, consequence, color in comp_data:
            col_bg = RoundedRectangle(corner_radius=0.18, width=3.8, height=3.0,
                                       color=color, fill_color=BG,
                                       fill_opacity=0.95, stroke_width=2)
            col_title = Text(cat, font_size=18, color=color, weight=BOLD)
            col_title.move_to(col_bg.get_top() + DOWN*0.32)
            sep = Line(LEFT*1.6, RIGHT*1.6, color=color, stroke_width=0.7, stroke_opacity=0.5)
            sep.move_to(col_bg.get_center() + UP*0.45)
            ex_mob = Text(examples, font_size=14, color=WHITE, line_spacing=1.25)
            ex_mob.move_to(col_bg.get_center() + UP*0.05)
            cons_label = Text("Consequence:", font_size=12, color=GRAY)
            cons_mob   = Text(consequence, font_size=13, color=color)
            cons_group = VGroup(cons_label, cons_mob).arrange(DOWN, buff=0.06)
            cons_group.move_to(col_bg.get_bottom() + UP*0.45)
            cols.add(VGroup(col_bg, col_title, sep, ex_mob, cons_group))

        cols.arrange(RIGHT, buff=0.5)
        cols.move_to(DOWN*0.15)
        self.play(FadeIn(cols, lag_ratio=0.2, scale=0.92), run_time=0.8)   # t≈1.4
        self.wait(7.0)                                                     # t≈8.4

        note = Text("Know which category a given obligation falls under — the exam will ask.",
                    font_size=17, color=AMBER, weight=BOLD)
        note.to_edge(DOWN, buff=0.55)
        self.play(FadeIn(note), run_time=0.4)
        self.wait(3.5)
        elapsed = 12.3

        self._pad("s9", elapsed)
        self._fade_content(bg)

    # ── SCENE 10 — Practice Questions ────────────────────────────
    def s10_practice_questions(self):
        bg = self._tech_bg()
        self._sound("s10")

        scene_title(self, "Practice Questions", color=GREEN)               # t≈0.6

        questions = [
            (
                "A security team reviews a cloud vendor's SOC 2 Type II report,\n"
                "pen test results, and incident disclosures BEFORE recommending approval.\n"
                "This BEST represents which concept?",
                "A. Due care",
                "B. Due diligence",
                "C. Regulatory compliance",
                "B — Due diligence. Research before the decision. Due care follows after signing."
            ),
            (
                "A CISO documented a critical vulnerability 6 months ago. Leadership declined\n"
                "to fund remediation. A breach exploits that vulnerability. Who bears\n"
                "ULTIMATE accountability?",
                "A. The CISO",
                "B. The security team",
                "C. Senior management",
                "C — Senior management. They own the risk. The CISO advised; management chose not to act."
            ),
            (
                "An employer directs a security professional to deny knowledge of an incident\n"
                "to a regulatory authority. ISC2 ethics requires the professional to:",
                "A. Follow the employer directive",
                "B. Refuse — Canon 1 supersedes organizational codes",
                "C. Escalate internally first",
                "B — Canon 1: protect society. No org code overrides ISC2's. Refuse and report."
            ),
        ]

        # Per-question dwell times tuned to narration at 3.3 wps.
        # Answer reveal aligns with narrator's "Answer:" cue for each question.
        # Q1 "Answer:" at audio t=10.6s, Q2 at t=29.1s, Q3 at t=47.9s.
        q_timing = [
            (9.0, 7.0),   # Q1: 33-word stem → 10.0s, answer reveal at t=10.6s
            (9.6, 7.9),   # Q2: 33-word stem → 10.0s, answer reveal at t=29.1s
            (9.0, 6.5),   # Q3: 31-word stem → 9.4s,  answer reveal at t=47.9s
        ]

        elapsed = 0.6
        for (stem, a, b, c, answer), (stem_dwell, ans_dwell) in zip(questions, q_timing):
            q_bg = RoundedRectangle(corner_radius=0.16, width=12.5, height=1.65,
                                     color=BLUE, fill_color="#00101A",
                                     fill_opacity=1, stroke_width=1.5)
            q_bg.move_to(UP*1.55)
            q_txt = Text(stem, font_size=17, color=WHITE, line_spacing=1.3)
            q_txt.move_to(q_bg.get_center())
            choices = VGroup(
                Text(a, font_size=16, color=WHITE),
                Text(b, font_size=16, color=WHITE),
                Text(c, font_size=16, color=WHITE),
            ).arrange(DOWN, buff=0.16, aligned_edge=LEFT)
            choices.next_to(q_bg, DOWN, buff=0.25)
            choices.to_edge(LEFT, buff=1.5)

            self.play(FadeIn(q_bg), Write(q_txt), run_time=0.6)
            self.play(FadeIn(choices), run_time=0.4)
            self.wait(stem_dwell)
            elapsed += 1.0 + stem_dwell

            ans_bg = RoundedRectangle(corner_radius=0.14, width=11.5, height=0.62,
                                       color=GREEN, fill_color="#051A0A",
                                       fill_opacity=1, stroke_width=1.5)
            ans_bg.to_edge(DOWN, buff=0.35)
            ans_txt = Text(answer, font_size=16, color=WHITE, weight=BOLD)
            ans_txt.move_to(ans_bg.get_center())
            self.play(FadeIn(ans_bg), Write(ans_txt), run_time=0.5)
            self.wait(ans_dwell)
            elapsed += 0.5 + ans_dwell

            self.play(FadeOut(q_bg), FadeOut(q_txt), FadeOut(choices),
                      FadeOut(ans_bg), FadeOut(ans_txt), run_time=0.4)
            elapsed += 0.4

        self._pad("s10", elapsed)
        self._fade_content(bg)

    # ── SCENE 11 — Recap + CTA ────────────────────────────────────
    def s11_recap_cta(self):
        bg = self._tech_bg()
        self._sound("s11")

        scene_title(self, "Four Flashcards", color=WHITE)                  # t≈0.6

        cards = [
            ("1", "Canon order:", "Society → Honor → Service → Profession", BLUE),
            ("2", "Five pillars:", "CIA + Authenticity + Nonrepudiation",    GREEN),
            ("3", "Risk ownership:", "Senior Mgmt OWNS · Security Pros ADVISE", AMBER),
            ("4", "Due Care/Diligence:", "Diligence = Discovery · Care = Conduct",  RED),
        ]

        all_cards = VGroup()
        for num, label, detail, color in cards:
            card_bg = RoundedRectangle(corner_radius=0.18, width=11.5, height=0.82,
                                       color=color, fill_color=BG,
                                       fill_opacity=0.95, stroke_width=2)
            num_mob    = Text(num, font_size=20, color=color, weight=BOLD)
            num_mob.move_to(card_bg.get_left() + RIGHT*0.5)
            label_mob  = Text(label, font_size=17, color=color, weight=BOLD)
            label_mob.move_to(card_bg.get_left() + RIGHT*2.4)
            detail_mob = Text(detail, font_size=17, color=WHITE)
            detail_mob.move_to(card_bg.get_right() + LEFT*3.2)
            all_cards.add(VGroup(card_bg, num_mob, label_mob, detail_mob))

        all_cards.arrange(DOWN, buff=0.18)
        all_cards.move_to(DOWN*0.15)

        elapsed = 0.6
        for card in all_cards:
            self.play(FadeIn(card, shift=RIGHT*0.2), run_time=0.45)
            self.wait(4.0)
            elapsed += 4.45
        # t≈18.4

        # CTA
        self.play(*[c.animate.set_opacity(0.4) for c in all_cards], run_time=0.4)

        cta_head = heading("Test yourself right now.", size=28, color=WHITE)
        url_bg = RoundedRectangle(corner_radius=0.2, width=5.2, height=0.68,
                                   color=GREEN, fill_color="#051A0A",
                                   fill_opacity=1, stroke_width=2)
        url_txt = Text("www.zerodaylabs.tech", font=MONO, font_size=22, color=GREEN, weight=BOLD)
        url_txt.move_to(url_bg.get_center())
        url_grp = VGroup(url_bg, url_txt)
        cta_group = VGroup(cta_head, url_grp).arrange(DOWN, buff=0.25)
        cta_group.to_edge(DOWN, buff=0.45)
        self.play(FadeIn(cta_group), run_time=0.5)                         # t≈19.3
        self.wait(3.0)                                                     # t≈22.3

        next_ep = Text("Next: D1-P2 — Risk Concepts, Threat Modeling, ALE/SLE/ARO",
                       font_size=17, color=AMBER, weight=BOLD)
        next_ep.next_to(cta_group, UP, buff=0.3)
        self.play(FadeIn(next_ep), run_time=0.4)                           # t≈22.7
        self.wait(4.0)
        elapsed = 26.7

        self._pad("s11", elapsed)

        black = Rectangle(
            width=config.frame_width + 1, height=config.frame_height + 1,
            fill_color=BLACK, fill_opacity=0, stroke_width=0,
        )
        self.add(black)
        self.play(black.animate.set_fill(opacity=1), run_time=1.8)
        self.wait(0.3)
