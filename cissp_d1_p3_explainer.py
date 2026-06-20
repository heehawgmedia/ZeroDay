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

AUDIO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cissp_d1_p3_audio")

_DUR_DEFAULTS = {
    "s0":  22.0,
    "s1":  55.0,
    "s2":  68.0,
    "s3":  70.0,
    "s4":  75.0,
    "s5":  72.0,
    "s6":  70.0,
    "s7":  68.0,
    "s8":  62.0,
    "s9":  58.0,
    "s10": 60.0,
    "s11": 45.0,
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


def _preflight_audio(audio_dir: str, dur: dict, generator: str) -> None:
    """Fail loudly before rendering if any audio file is missing, too small,
    or shorter than its recorded duration (truncated / dropped-out audio)."""
    bad = []
    for key in dur:
        path = os.path.join(audio_dir, f"{key}.mp3")
        if not os.path.exists(path) or os.path.getsize(path) < 1024:
            bad.append(key)
            continue
        # Catch truncated audio: file on disk is materially shorter than the
        # duration recorded at generation time (the "volume drops out" bug).
        try:
            actual   = _ffprobe_seconds(path)
            expected = float(dur.get(key, 0))
        except Exception:
            bad.append(key)
            continue
        if expected and actual < expected - 2.0:
            bad.append(key)
    if bad:
        keys = " ".join(bad)
        raise RuntimeError(
            f"\n{'='*60}\n"
            f"  MISSING / TRUNCATED AUDIO — DO NOT RENDER\n"
            f"{'='*60}\n"
            f"  Files missing, invalid, or truncated: {keys}\n"
            f"  Fix: python {generator} --force --only {keys}\n"
            f"{'='*60}\n"
        )


# ═══════════════════════════════════════════════════════════════════
#  CISSP D1-P3  —  manim -qh cissp_d1_p3_explainer.py CISSP_D1P3
# ═══════════════════════════════════════════════════════════════════
class CISSP_D1P3(Scene):
    def construct(self):
        _preflight_audio(AUDIO, DUR, "generate_cissp_d1_p3_narration.py")
        self.s0_ad()
        self.s1_hook_roadmap()
        self.s2_bcp_vs_drp()
        self.s3_bia()
        self.s4_recovery_metrics()
        self.s5_recovery_sites()
        self.s6_dr_testing()
        self.s7_personnel_hiring()
        self.s8_personnel_termination()
        self.s9_awareness_training()
        self.s10_practice_questions()
        self.s11_recap_cta()

    # ── Background ───────────────────────────────────────────────
    def _tech_bg(self) -> VGroup:
        rng = random.Random(42)
        base = Rectangle(
            width=config.frame_width + 0.5, height=config.frame_height + 0.5,
            fill_color="#04080F", fill_opacity=1, stroke_width=0,
        )
        glow = Ellipse(width=13, height=8.5,
                       fill_color="#0A1830", fill_opacity=0.55, stroke_width=0)
        grid = VGroup(*[
            Line(LEFT*8, RIGHT*8, stroke_width=0.45,
                 color="#0D2040", stroke_opacity=1).shift(UP*y)
            for y in [-3.0, -1.5, 0.0, 1.5, 3.0]
        ])
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

        question = Text("The data center floods. How long can your business survive?",
                        font_size=28, color=WHITE, weight=BOLD)
        question.move_to(UP*0.6)
        self.play(Write(question), run_time=1.2)
        self.wait(2.5)

        sub = Text("That answer must be documented, tested, and board-approved — not guessed.",
                   font_size=18, color=AMBER)
        sub.next_to(question, DOWN, buff=0.45)
        self.play(FadeIn(sub, shift=UP*0.1), run_time=0.5)
        self.wait(3.5)

        self._fade_content(bg, run_time=0.4)
        bg2 = self._tech_bg()

        series = Text("CISSP Domain Mastery Series", font_size=20, color=GRAY)
        ep_title = heading("D1-P3  |  Business Continuity,\nRecovery & Personnel Security",
                           size=34, color=WHITE)
        ep_title.move_to(UP*1.1)
        series.next_to(ep_title, UP, buff=0.3)
        self.play(FadeIn(series), Write(ep_title), run_time=0.9)

        obj_label = Text("Exam Objectives Covered:", font_size=17, color=AMBER, weight=BOLD)
        obj_label.next_to(ep_title, DOWN, buff=0.4)
        obj_nums = mono("1.7  |  1.8", size=20, color=BLUE)
        obj_nums.next_to(obj_label, DOWN, buff=0.18)
        self.play(FadeIn(obj_label), Write(obj_nums), run_time=0.6)

        topics = [
            "BCP vs. DRP — scope and relationship",
            "Business Impact Analysis (BIA)",
            "Recovery Metrics — MTD, RTO, RPO, MTTR, MTBF",
            "Recovery Site Strategies — Hot / Warm / Cold",
            "DR Plan Testing — 5 types in order",
            "Personnel Security — Hiring & Employment",
            "Personnel Termination — Access Revocation",
            "Security Awareness, Training & Education",
        ]
        topic_group = VGroup(*[
            Text(f"• {t}", font_size=15, color=WHITE) for t in topics
        ]).arrange(DOWN, buff=0.13, aligned_edge=LEFT)
        topic_group.next_to(obj_nums, DOWN, buff=0.28)
        for t in topic_group:
            self.play(FadeIn(t, shift=RIGHT*0.15), run_time=0.17)

        elapsed = 16.5
        self._pad("s1", elapsed)
        self._fade_content(bg2)

    # ── SCENE 2 — BCP vs DRP ─────────────────────────────────────
    def s2_bcp_vs_drp(self):
        bg = self._tech_bg()
        self._sound("s2")

        scene_title(self, "BCP vs. Disaster Recovery", color=BLUE)

        bcp_bg = RoundedRectangle(corner_radius=0.18, width=5.8, height=4.2,
                                   color=BLUE, fill_color="#001528",
                                   fill_opacity=0.95, stroke_width=2.5)
        bcp_bg.move_to(LEFT*3.3 + DOWN*0.25)
        bcp_title = Text("BCP", font_size=26, color=BLUE, weight=BOLD)
        bcp_sub   = Text("Business Continuity Planning", font_size=13, color=GRAY)
        bcp_title.move_to(bcp_bg.get_top() + DOWN*0.38)
        bcp_sub.next_to(bcp_title, DOWN, buff=0.08)
        bcp_items = VGroup(
            Text("Scope: entire organization", font_size=14, color=WHITE),
            Text("People, process, facilities,", font_size=14, color=WHITE),
            Text("  communications, technology", font_size=14, color=WHITE),
            Text("Keeps the business OPERATING", font_size=14, color=BLUE, weight=BOLD),
            Text("during a disruption", font_size=14, color=WHITE),
            Text("Sponsored by senior management", font_size=13, color=GRAY),
        ).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        bcp_items.next_to(bcp_sub, DOWN, buff=0.22)

        drp_bg = RoundedRectangle(corner_radius=0.18, width=5.8, height=4.2,
                                   color=GREEN, fill_color="#051A0A",
                                   fill_opacity=0.95, stroke_width=2.5)
        drp_bg.move_to(RIGHT*3.3 + DOWN*0.25)
        drp_title = Text("DRP", font_size=26, color=GREEN, weight=BOLD)
        drp_sub   = Text("Disaster Recovery Planning", font_size=13, color=GRAY)
        drp_title.move_to(drp_bg.get_top() + DOWN*0.38)
        drp_sub.next_to(drp_title, DOWN, buff=0.08)
        drp_items = VGroup(
            Text("Scope: IT systems and data", font_size=14, color=WHITE),
            Text("Subset of BCP", font_size=14, color=GREEN, weight=BOLD),
            Text("Restores TECHNOLOGY after", font_size=14, color=WHITE),
            Text("  a disruption", font_size=14, color=WHITE),
            Text("DRP alone ≠ continuity plan", font_size=14, color=RED, weight=BOLD),
            Text("Must be reviewed, updated, tested", font_size=13, color=GRAY),
        ).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        drp_items.next_to(drp_sub, DOWN, buff=0.22)

        self.play(
            FadeIn(bcp_bg), Write(bcp_title), FadeIn(bcp_sub), FadeIn(bcp_items),
            FadeIn(drp_bg), Write(drp_title), FadeIn(drp_sub), FadeIn(drp_items),
            run_time=0.9
        )
        self.wait(15.0)

        tip = exam_tip(self,
            "BCP keeps the business running  |  DRP restores the IT systems that support it")
        self.wait(5.0)
        elapsed = 22.0

        self._pad("s2", elapsed)
        self._fade_content(bg)

    # ── SCENE 3 — BIA ─────────────────────────────────────────────
    def s3_bia(self):
        bg = self._tech_bg()
        self._sound("s3")

        scene_title(self, "Business Impact Analysis (BIA)", color=AMBER)

        # What BIA does
        intro_bg = RoundedRectangle(corner_radius=0.16, width=13.0, height=0.72,
                                     color=AMBER, fill_color="#1A0D00",
                                     fill_opacity=1, stroke_width=2)
        intro_bg.move_to(UP*1.9)
        intro_txt = Text(
            "Identifies critical functions, supporting systems, and the cost of disruption over time.",
            font_size=16, color=WHITE
        )
        intro_txt.move_to(intro_bg.get_center())
        self.play(FadeIn(intro_bg), Write(intro_txt), run_time=0.7)
        self.wait(4.0)

        # BIA outputs as three cards
        bia_outputs = [
            ("Recovery\nPrioritization",
             "Which functions are restored first\nbased on business criticality",
             BLUE, "#001528"),
            ("Recovery Time\nTargets (RTO)",
             "How quickly each function\nmust be restored",
             GREEN, "#051A0A"),
            ("Recovery Point\nTargets (RPO)",
             "Maximum acceptable data loss\nfor each function",
             AMBER, "#1A0D00"),
        ]

        cols = VGroup()
        for title_str, body, color, fill in bia_outputs:
            col_bg = RoundedRectangle(corner_radius=0.18, width=3.9, height=2.4,
                                      color=color, fill_color=fill,
                                      fill_opacity=0.95, stroke_width=2)
            col_title = Text(title_str, font_size=15, color=color,
                             weight=BOLD, line_spacing=1.2)
            col_title.move_to(col_bg.get_top() + DOWN*0.45)
            col_body = Text(body, font_size=13, color=WHITE, line_spacing=1.3)
            col_body.move_to(col_bg.get_center() + DOWN*0.25)
            cols.add(VGroup(col_bg, col_title, col_body))

        cols.arrange(RIGHT, buff=0.45)
        cols.move_to(DOWN*0.35)
        self.play(FadeIn(cols, lag_ratio=0.2, scale=0.93), run_time=0.8)
        self.wait(10.0)

        # MTD callout
        mtd_bg = RoundedRectangle(corner_radius=0.14, width=13.0, height=0.72,
                                   color=RED, fill_color="#1A0000",
                                   fill_opacity=1, stroke_width=2)
        mtd_bg.to_edge(DOWN, buff=0.28)
        mtd_txt = Text(
            "MTD — Maximum Tolerable Downtime: the outer limit. All recovery targets must fall within it.",
            font_size=15, color=WHITE, weight=BOLD
        )
        mtd_txt.move_to(mtd_bg.get_center())
        self.play(FadeIn(mtd_bg), Write(mtd_txt), run_time=0.6)
        self.wait(6.0)
        elapsed = 23.0

        tip = exam_tip(self,
            "Conduct BIA FIRST — identify impact before selecting recovery strategies")
        elapsed += 0.5
        self.wait(4.0)
        elapsed += 4.0

        self._pad("s3", elapsed)
        self._fade_content(bg)

    # ── SCENE 4 — Recovery Metrics ────────────────────────────────
    def s4_recovery_metrics(self):
        bg = self._tech_bg()
        self._sound("s4")

        scene_title(self, "Recovery Metrics", color=BLUE)

        metrics = [
            ("MTD",  "Maximum Tolerable Downtime",
             "Longest acceptable outage before\ndamage becomes unrecoverable",
             RED,   "Outer boundary — all other metrics must fit inside it"),
            ("RTO",  "Recovery Time Objective",
             "Maximum time to restore a system\nor function after disruption",
             AMBER, "Must be LESS than MTD — always"),
            ("RPO",  "Recovery Point Objective",
             "Maximum acceptable data loss,\nmeasured in time",
             GREEN, "Drives backup frequency — backup at least every RPO interval"),
            ("MTTR", "Mean Time to Repair",
             "Average time to restore\na failed component",
             BLUE,  "Historical/observed metric — used in reliability planning"),
            ("MTBF", "Mean Time Between Failures",
             "Average operating time\nbetween failures",
             GRAY,  "Higher MTBF = more reliable system"),
        ]

        col_x = [-5.5, -1.4, 3.5]
        hdr_y = 1.88
        hdr = VGroup(
            Text("ABBR",       font_size=12, color=GRAY, weight=BOLD).move_to([col_x[0], hdr_y, 0]),
            Text("DEFINITION", font_size=12, color=GRAY, weight=BOLD).move_to([col_x[1], hdr_y, 0]),
            Text("EXAM NOTE",  font_size=12, color=GRAY, weight=BOLD).move_to([col_x[2], hdr_y, 0]),
        )
        hdr_line = Line(LEFT*6.8, RIGHT*6.8, color=GRAY,
                        stroke_width=0.7, stroke_opacity=0.4).move_to(UP*1.65)
        self.play(FadeIn(hdr), Create(hdr_line), run_time=0.4)

        elapsed = 1.0
        for i, (abbr, full, defn, color, note) in enumerate(metrics):
            y = 1.22 - i * 0.72
            abbr_mob = Text(abbr, font_size=18, color=color, weight=BOLD).move_to([col_x[0], y, 0])
            defn_mob = Text(f"{full}\n{defn}", font_size=12, color=WHITE,
                            line_spacing=1.15).move_to([col_x[1], y, 0])
            note_mob = Text(note, font_size=12, color=color).move_to([col_x[2], y, 0])
            sep = Line(LEFT*6.8, RIGHT*6.8, stroke_width=0.3,
                       color="#223344", stroke_opacity=0.5).move_to(UP*(y - 0.33))
            self.play(FadeIn(VGroup(abbr_mob, defn_mob, note_mob), shift=UP*0.1),
                      Create(sep), run_time=0.4)
            self.wait(7.0)
            elapsed += 7.4

        tip = exam_tip(self,
            "RPO → backup frequency  |  RTO → recovery speed  |  RTO must always be < MTD")
        elapsed += 0.5
        self.wait(4.0)
        elapsed += 4.0

        self._pad("s4", elapsed)
        self._fade_content(bg)

    # ── SCENE 5 — Recovery Sites ──────────────────────────────────
    def s5_recovery_sites(self):
        bg = self._tech_bg()
        self._sound("s5")

        scene_title(self, "Recovery Site Strategies", color=AMBER)

        sites = [
            ("HOT SITE",
             "Fully operational duplicate. Hardware, software, data — all current.\nFailover in minutes to hours.",
             "Highest cost", "Tightest RTOs / most critical systems",
             RED),
            ("WARM SITE",
             "Hardware in place, not fully configured. Data is not current.\nRecovery in hours to days.",
             "Moderate cost", "Most common — balances cost and recovery speed",
             AMBER),
            ("COLD SITE",
             "Power, cooling, connectivity only. Bring your own hardware.\nRecovery in days to weeks.",
             "Lowest cost", "Only when MTD is very long",
             GRAY),
            ("REDUNDANT SITE",
             "Fully mirrored with real-time data sync. Faster than hot site.\nSeamless failover.",
             "Most expensive", "Mission-critical / zero-tolerance downtime",
             BLUE),
        ]

        all_cards = VGroup()
        for label, desc, cost, use_when, color in sites:
            card_bg = RoundedRectangle(corner_radius=0.15, width=13.0, height=0.95,
                                       color=color, fill_color=BG,
                                       fill_opacity=0.92, stroke_width=2)
            label_mob = Text(label, font_size=14, color=color, weight=BOLD)
            label_mob.next_to(card_bg.get_left(), RIGHT, buff=0.35)
            label_mob.set_y(card_bg.get_center()[1])
            desc_mob = Text(desc, font_size=12, color=WHITE, line_spacing=1.2)
            desc_mob.move_to(card_bg.get_center() + RIGHT*0.5)
            desc_mob.set_y(card_bg.get_center()[1])
            cost_mob = Text(cost, font_size=12, color=color, weight=BOLD)
            cost_mob.next_to(card_bg.get_right(), LEFT, buff=0.35)
            cost_mob.set_y(card_bg.get_center()[1])
            all_cards.add(VGroup(card_bg, label_mob, desc_mob, cost_mob))

        all_cards.arrange(DOWN, buff=0.14)
        all_cards.move_to(DOWN*0.1)

        elapsed = 0.6
        dwells = [10.0, 10.0, 9.0, 8.0]
        for card, dwell in zip(all_cards, dwells):
            self.play(FadeIn(card, shift=RIGHT*0.15), run_time=0.45)
            self.wait(dwell)
            elapsed += 0.45 + dwell

        tip = exam_tip(self,
            "Hot→minutes  |  Warm→hours  |  Cold→days  |  Redundant→real-time mirror")
        elapsed += 0.5
        self.wait(4.0)
        elapsed += 4.0

        self._pad("s5", elapsed)
        self._fade_content(bg)

    # ── SCENE 6 — DR Testing ─────────────────────────────────────
    def s6_dr_testing(self):
        bg = self._tech_bg()
        self._sound("s6")

        scene_title(self, "DR Plan Testing — 5 Types", color=GREEN)

        hdr_bg = RoundedRectangle(corner_radius=0.14, width=13.0, height=0.60,
                                   color=GREEN, fill_color="#051A0A",
                                   fill_opacity=1, stroke_width=1.5)
        hdr_bg.move_to(UP*2.0)
        hdr_txt = Text("Ordered by increasing disruption and realism →",
                       font_size=15, color=GREEN, weight=BOLD)
        hdr_txt.move_to(hdr_bg.get_center())
        self.play(FadeIn(hdr_bg), Write(hdr_txt), run_time=0.5)

        tests = [
            ("1", "READ-THROUGH",     "Team reads the plan. Verifies understanding of roles.\nNo systems involved.",                        GRAY),
            ("2", "WALKTHROUGH",      "Team steps through the plan in a meeting room.\nDiscusses actions for a given scenario.",            BLUE),
            ("3", "SIMULATION",       "Scenario announced. Teams practice responses.\nNo systems switched. Tests communication.",           AMBER),
            ("4", "PARALLEL TEST",    "Recovery systems brought online at alternate site.\nPrimary site continues operating simultaneously.", GREEN),
            ("5", "FULL INTERRUPTION","Primary systems shut down. Full failover occurs.\nMost realistic. Highest risk. Rarely performed.",  RED),
        ]

        elapsed = 1.1
        for i, (num, name, desc, color) in enumerate(tests):
            y = 1.28 - i * 0.72
            num_circle = Circle(radius=0.22, color=color,
                                fill_color=color, fill_opacity=0.9, stroke_width=0)
            num_circle.move_to([-6.2, y, 0])
            num_mob = Text(num, font_size=14, color=BG, weight=BOLD)
            num_mob.move_to(num_circle.get_center())
            name_mob = Text(name, font_size=14, color=color, weight=BOLD)
            name_mob.move_to([-3.8, y, 0])
            desc_mob = Text(desc, font_size=12, color=WHITE, line_spacing=1.2)
            desc_mob.move_to([2.8, y, 0])
            sep = Line(LEFT*6.8, RIGHT*6.8, stroke_width=0.3,
                       color="#223344", stroke_opacity=0.5).move_to(UP*(y - 0.32))
            grp = VGroup(num_circle, num_mob, name_mob, desc_mob, sep)
            self.play(FadeIn(grp, shift=UP*0.1), run_time=0.4)
            self.wait(7.0)
            elapsed += 7.4

        tip = exam_tip(self,
            "Read → Walk → Simulate → Parallel → Full  |  Full interruption = most realistic, highest risk")
        elapsed += 0.5
        self.wait(4.0)
        elapsed += 4.0

        self._pad("s6", elapsed)
        self._fade_content(bg)

    # ── SCENE 7 — Personnel: Hiring & Employment ─────────────────
    def s7_personnel_hiring(self):
        bg = self._tech_bg()
        self._sound("s7")

        scene_title(self, "Personnel Security — Hiring & Employment", color=AMBER)

        phase_data = [
            ("PRE-EMPLOYMENT", [
                ("Background checks", "Identity, criminal, employment, education",        BLUE),
                ("Reference checks",  "Validate character and past performance",          BLUE),
                ("NDA",               "Signed BEFORE access is granted",                  RED),
                ("Least privilege",   "Access limited to role requirements from day one", GREEN),
            ], BLUE),
            ("DURING EMPLOYMENT", [
                ("Separation of duties", "No single person completes a sensitive transaction alone",   AMBER),
                ("Job rotation",         "Periodic role changes — detects concealed fraud (detective)", GREEN),
                ("Mandatory vacation",   "Uninterrupted leave — another person covers role (detective)", GREEN),
                ("AUP",                  "Acceptable Use Policy governs system use",                    GRAY),
            ], AMBER),
        ]

        cols = VGroup()
        for phase, items, header_color in phase_data:
            col_bg = RoundedRectangle(corner_radius=0.18, width=6.1, height=4.4,
                                      color=header_color, fill_color=BG,
                                      fill_opacity=0.94, stroke_width=2)
            col_title = Text(phase, font_size=15, color=header_color, weight=BOLD)
            col_title.move_to(col_bg.get_top() + DOWN*0.3)
            sep_line = Line(LEFT*2.6, RIGHT*2.6, color=header_color,
                            stroke_width=0.7, stroke_opacity=0.5)
            sep_line.next_to(col_title, DOWN, buff=0.12)

            rows = VGroup()
            for ctrl, desc, color in items:
                ctrl_mob = Text(f"• {ctrl}", font_size=13, color=color, weight=BOLD)
                desc_mob = Text(f"  {desc}", font_size=12, color=WHITE)
                rows.add(VGroup(ctrl_mob, desc_mob).arrange(DOWN, buff=0.04, aligned_edge=LEFT))

            rows.arrange(DOWN, buff=0.22, aligned_edge=LEFT)
            rows.next_to(sep_line, DOWN, buff=0.18)
            cols.add(VGroup(col_bg, col_title, sep_line, rows))

        cols.arrange(RIGHT, buff=0.6)
        cols.move_to(DOWN*0.15)
        self.play(FadeIn(cols, lag_ratio=0.2, scale=0.93), run_time=0.9)
        self.wait(18.0)

        tip = exam_tip(self,
            "Job rotation & mandatory vacation are DETECTIVE controls — they uncover fraud already occurring")
        self.wait(5.0)
        elapsed = 25.0

        self._pad("s7", elapsed)
        self._fade_content(bg)

    # ── SCENE 8 — Personnel Termination ──────────────────────────
    def s8_personnel_termination(self):
        bg = self._tech_bg()
        self._sound("s8")

        scene_title(self, "Personnel Termination", color=RED)

        warning_bg = RoundedRectangle(corner_radius=0.16, width=13.0, height=0.70,
                                       color=RED, fill_color="#1A0000",
                                       fill_opacity=1, stroke_width=2)
        warning_bg.move_to(UP*2.0)
        warning_txt = Text(
            "Termination is the highest-risk event in the personnel lifecycle.",
            font_size=17, color=WHITE, weight=BOLD
        )
        warning_txt.move_to(warning_bg.get_center())
        self.play(FadeIn(warning_bg), Write(warning_txt), run_time=0.6)
        self.wait(3.0)

        steps = [
            ("REVOKE ACCESS",    "Immediately — before or simultaneous with notification.\nNever after the employee leaves the building.",        RED),
            ("RECOVER ASSETS",   "Badges, laptops, mobile devices, tokens, keys, MFA hardware.",                                                   AMBER),
            ("EXIT INTERVIEW",   "Document the separation. Review outstanding obligations.",                                                         BLUE),
            ("REMIND OF NDA",    "Confidentiality obligations survive termination.\nDocument acknowledgement.",                                       GREEN),
            ("PRIVILEGED USERS", "Admins and privileged accounts — highest priority for revocation.\nChange shared credentials immediately.",         RED),
        ]

        all_steps = VGroup()
        for label, desc, color in steps:
            step_bg = RoundedRectangle(corner_radius=0.12, width=13.0, height=0.78,
                                        color=color, fill_color=BG,
                                        fill_opacity=0.90, stroke_width=1.5)
            label_mob = Text(label, font_size=14, color=color, weight=BOLD)
            label_mob.next_to(step_bg.get_left(), RIGHT, buff=0.35)
            label_mob.set_y(step_bg.get_center()[1])
            desc_mob = Text(desc, font_size=12, color=WHITE, line_spacing=1.2)
            desc_mob.move_to(step_bg.get_center() + RIGHT*2.0)
            desc_mob.set_y(step_bg.get_center()[1])
            all_steps.add(VGroup(step_bg, label_mob, desc_mob))

        all_steps.arrange(DOWN, buff=0.10)
        all_steps.move_to(DOWN*0.38)

        elapsed = 4.0
        dwells = [8.0, 6.0, 5.5, 6.0, 6.5]
        for step, dwell in zip(all_steps, dwells):
            self.play(FadeIn(step, shift=LEFT*0.15), run_time=0.4)
            self.wait(dwell)
            elapsed += 0.4 + dwell

        tip = exam_tip(self,
            "Access revocation MUST be immediate — delayed revocation = failed termination procedure")
        elapsed += 0.5
        self.wait(4.0)
        elapsed += 4.0

        self._pad("s8", elapsed)
        self._fade_content(bg)

    # ── SCENE 9 — Awareness Training ─────────────────────────────
    def s9_awareness_training(self):
        bg = self._tech_bg()
        self._sound("s9")

        scene_title(self, "Security Awareness, Training & Education", color=GREEN)

        levels = [
            ("AWARENESS",  "Everyone",
             "Changes behavior — helps people RECOGNIZE risks\nin day-to-day work.",
             "Phishing simulations, posters, reminders",
             "Goal: recognition",
             BLUE),
            ("TRAINING",   "Role-based",
             "Builds SKILLS — teaches how to perform\nsecurity tasks correctly.",
             "Secure coding for devs · Data handling for HR",
             "Goal: competence",
             GREEN),
            ("EDUCATION",  "Security professionals",
             "Builds UNDERSTANDING — conceptual depth\nfor security roles and certifications.",
             "CISSP preparation is security education",
             "Goal: expertise",
             AMBER),
        ]

        all_cards = VGroup()
        for level, audience, desc, example, goal, color in levels:
            card_bg = RoundedRectangle(corner_radius=0.16, width=13.0, height=1.08,
                                       color=color, fill_color=BG,
                                       fill_opacity=0.92, stroke_width=2)
            level_mob = Text(level, font_size=15, color=color, weight=BOLD)
            level_mob.next_to(card_bg.get_left(), RIGHT, buff=0.35)
            level_mob.set_y(card_bg.get_center()[1])
            aud_mob = Text(f"({audience})", font_size=12, color=GRAY)
            aud_mob.next_to(level_mob, DOWN, buff=0.05)

            body_mob = Text(desc, font_size=12, color=WHITE, line_spacing=1.2)
            body_mob.move_to(card_bg.get_center() + RIGHT*0.5)
            body_mob.set_y(card_bg.get_center()[1])

            goal_mob = Text(goal, font_size=12, color=color, weight=BOLD)
            goal_mob.next_to(card_bg.get_right(), LEFT, buff=0.35)
            goal_mob.set_y(card_bg.get_center()[1])

            all_cards.add(VGroup(card_bg, level_mob, aud_mob, body_mob, goal_mob))

        all_cards.arrange(DOWN, buff=0.18)
        all_cards.move_to(DOWN*0.1)

        elapsed = 0.6
        dwells = [12.0, 12.0, 10.0]
        for card, dwell in zip(all_cards, dwells):
            self.play(FadeIn(card, shift=RIGHT*0.15), run_time=0.45)
            self.wait(dwell)
            elapsed += 0.45 + dwell

        tip = exam_tip(self,
            "Awareness→recognition  |  Training→skills  |  Education→understanding")
        elapsed += 0.5
        self.wait(4.0)
        elapsed += 4.0

        self._pad("s9", elapsed)
        self._fade_content(bg)

    # ── SCENE 10 — Practice Questions ────────────────────────────
    def s10_practice_questions(self):
        bg = self._tech_bg()
        self._sound("s10")

        scene_title(self, "Practice Questions", color=GREEN)

        questions = [
            (
                "Payroll must be restored within 36 hours of failure. The max penalty-free\n"
                "outage is 48 hours. Backups run every 6 hours.\n"
                "What are the MTD, RTO, and RPO?",
                "A. MTD=48h  RTO=36h  RPO=6h",
                "B. MTD=36h  RTO=6h   RPO=48h",
                "C. MTD=6h   RTO=48h  RPO=36h",
                "A — MTD=48h (outer limit), RTO=36h (must be < MTD), RPO=6h (backup interval)"
            ),
            (
                "A DR test brings the alternate site fully online while primary continues\n"
                "operating normally. Both environments run simultaneously for 4 hours.\n"
                "Which DR test type was performed?",
                "A. Simulation",
                "B. Parallel test",
                "C. Full interruption",
                "B — Parallel test. Both sites run simultaneously — primary is never interrupted."
            ),
            (
                "A terminated network admin's credentials were not revoked until 3 days\n"
                "after termination. The former employee accessed internal systems.\n"
                "Which personnel security control failed?",
                "A. Background check",
                "B. Mandatory vacation",
                "C. Immediate access revocation at termination",
                "C — Access revocation must be immediate. The delay created the unauthorized access window."
            ),
        ]

        elapsed = 0.6
        for stem, a, b, c, answer in questions:
            q_bg = RoundedRectangle(corner_radius=0.16, width=13.0, height=1.65,
                                     color=BLUE, fill_color="#00101A",
                                     fill_opacity=1, stroke_width=1.5)
            q_bg.move_to(UP*1.55)
            q_txt = Text(stem, font_size=16, color=WHITE, line_spacing=1.3)
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
            self.wait(5.0)
            elapsed += 6.0

            ans_bg = RoundedRectangle(corner_radius=0.14, width=12.5, height=0.62,
                                       color=GREEN, fill_color="#051A0A",
                                       fill_opacity=1, stroke_width=1.5)
            ans_bg.to_edge(DOWN, buff=0.35)
            ans_txt = Text(answer, font_size=14, color=WHITE, weight=BOLD)
            ans_txt.move_to(ans_bg.get_center())
            self.play(FadeIn(ans_bg), Write(ans_txt), run_time=0.5)
            self.wait(5.5)
            elapsed += 6.0

            self.play(FadeOut(q_bg), FadeOut(q_txt), FadeOut(choices),
                      FadeOut(ans_bg), FadeOut(ans_txt), run_time=0.4)
            elapsed += 0.4

        self._pad("s10", elapsed)
        self._fade_content(bg)

    # ── SCENE 11 — Recap + CTA ────────────────────────────────────
    def s11_recap_cta(self):
        bg = self._tech_bg()
        self._sound("s11")

        scene_title(self, "Four Flashcards", color=WHITE)

        cards = [
            ("1", "Recovery metrics:",
             "MTD > RTO > 0  |  RPO = backup frequency",    BLUE),
            ("2", "Site types:",
             "Hot→minutes  |  Warm→hours  |  Cold→days",    GREEN),
            ("3", "DR testing order:",
             "Read → Walk → Simulate → Parallel → Full",    AMBER),
            ("4", "Termination:",
             "Revoke access IMMEDIATELY — recover assets — remind of NDA", RED),
        ]

        all_cards = VGroup()
        for num, label, detail, color in cards:
            card_bg = RoundedRectangle(corner_radius=0.18, width=13.0, height=0.86,
                                       color=color, fill_color=BG,
                                       fill_opacity=0.95, stroke_width=2)
            num_mob    = Text(num,    font_size=20, color=color, weight=BOLD)
            num_mob.move_to(card_bg.get_left() + RIGHT*0.5)
            label_mob  = Text(label,  font_size=16, color=color, weight=BOLD)
            label_mob.move_to(card_bg.get_left() + RIGHT*2.2)
            detail_mob = Text(detail, font_size=15, color=WHITE)
            detail_mob.move_to(card_bg.get_center() + RIGHT*2.0)
            detail_mob.set_y(card_bg.get_center()[1])
            all_cards.add(VGroup(card_bg, num_mob, label_mob, detail_mob))

        all_cards.arrange(DOWN, buff=0.16)
        all_cards.move_to(DOWN*0.1)

        elapsed = 0.6
        for card in all_cards:
            self.play(FadeIn(card, shift=RIGHT*0.2), run_time=0.45)
            self.wait(4.5)
            elapsed += 4.95

        self.play(*[c.animate.set_opacity(0.4) for c in all_cards], run_time=0.4)

        cta_head = heading("Domain 1 complete. Test yourself now.", size=24, color=WHITE)
        url_bg = RoundedRectangle(corner_radius=0.2, width=5.2, height=0.68,
                                   color=GREEN, fill_color="#051A0A",
                                   fill_opacity=1, stroke_width=2)
        url_txt = Text("www.zerodaylabs.tech", font=MONO, font_size=22, color=GREEN, weight=BOLD)
        url_txt.move_to(url_bg.get_center())
        url_grp = VGroup(url_bg, url_txt)
        cta_group = VGroup(cta_head, url_grp).arrange(DOWN, buff=0.22)
        cta_group.to_edge(DOWN, buff=0.45)
        self.play(FadeIn(cta_group), run_time=0.5)
        self.wait(3.0)

        next_ep = Text("Next: Domain 2 Part 1 — Asset Security, Data Classification & Retention",
                       font_size=16, color=AMBER, weight=BOLD)
        next_ep.next_to(cta_group, UP, buff=0.3)
        self.play(FadeIn(next_ep), run_time=0.4)
        self.wait(4.0)
        elapsed = 30.0

        self._pad("s11", elapsed)

        black = Rectangle(
            width=config.frame_width + 1, height=config.frame_height + 1,
            fill_color=BLACK, fill_opacity=0, stroke_width=0,
        )
        self.add(black)
        self.play(black.animate.set_fill(opacity=1), run_time=1.8)
        self.wait(0.3)
