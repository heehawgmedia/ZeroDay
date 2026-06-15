from manim import *
import json
import os
import random

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

AUDIO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cissp_d1_p2_audio")

_DUR_DEFAULTS = {
    "s0":  22.0,
    "s1":  55.0,
    "s2":  75.0,
    "s3":  88.0,
    "s4":  65.0,
    "s5":  62.0,
    "s6":  72.0,
    "s7":  55.0,
    "s8":  72.0,
    "s9":  40.0,
    "s10": 58.0,
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


# ═══════════════════════════════════════════════════════════════════
#  CISSP D1-P2  —  manim -qh cissp_d1_p2_explainer.py CISSP_D1P2
# ═══════════════════════════════════════════════════════════════════
class CISSP_D1P2(Scene):
    def construct(self):
        self.s0_ad()
        self.s1_hook_roadmap()
        self.s2_risk_vocabulary()
        self.s3_quantitative_math()
        self.s4_assessment_types()
        self.s5_risk_responses()
        self.s6_stride()
        self.s7_pasta_trees()
        self.s8_nist_rmf()
        self.s9_supply_chain()
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

        question = Text("What was our expected annual loss from this threat?",
                        font_size=30, color=WHITE, weight=BOLD)
        question.move_to(UP*0.5)
        self.play(Write(question), run_time=1.2)
        self.wait(2.5)

        ciso_line = Text("The CISO had no answer — because no one ran the numbers.",
                         font_size=20, color=RED, weight=BOLD)
        ciso_line.next_to(question, DOWN, buff=0.5)
        self.play(FadeIn(ciso_line, shift=UP*0.1), run_time=0.5)
        self.wait(3.5)

        self._fade_content(bg, run_time=0.4)
        bg2 = self._tech_bg()

        series = Text("CISSP Domain Mastery Series", font_size=20, color=GRAY)
        ep_title = heading("D1-P2  |  Risk Management,\nThreat Modeling & Frameworks",
                           size=34, color=WHITE)
        ep_title.move_to(UP*1.1)
        series.next_to(ep_title, UP, buff=0.3)
        self.play(FadeIn(series), Write(ep_title), run_time=0.9)

        obj_label = Text("Exam Objective Covered:", font_size=17, color=AMBER, weight=BOLD)
        obj_label.next_to(ep_title, DOWN, buff=0.4)
        obj_nums = mono("1.4  |  Risk Management Concepts", size=20, color=BLUE)
        obj_nums.next_to(obj_label, DOWN, buff=0.18)
        self.play(FadeIn(obj_label), Write(obj_nums), run_time=0.6)

        topics = [
            "Risk Vocabulary", "Quantitative Risk Math (SLE · ARO · ALE)",
            "Qualitative vs. Quantitative Assessment", "Risk Response Strategies (TARA)",
            "Threat Modeling — STRIDE", "Threat Modeling — PASTA & Attack Trees",
            "NIST Risk Management Framework", "Supply Chain Risk",
        ]
        topic_group = VGroup(*[
            Text(f"• {t}", font_size=15, color=WHITE) for t in topics
        ]).arrange(DOWN, buff=0.13, aligned_edge=LEFT)
        topic_group.next_to(obj_nums, DOWN, buff=0.3)
        for t in topic_group:
            self.play(FadeIn(t, shift=RIGHT*0.15), run_time=0.18)

        elapsed = 16.0
        self._pad("s1", elapsed)
        self._fade_content(bg2)

    # ── SCENE 2 — Risk Vocabulary ────────────────────────────────
    def s2_risk_vocabulary(self):
        bg = self._tech_bg()
        self._sound("s2")

        scene_title(self, "Risk Vocabulary", color=BLUE)

        terms = [
            ("Asset",          "Anything of value the org must protect\n(data, hardware, IP, reputation)",           BLUE),
            ("Threat",         "Potential event that could cause harm to an asset",                                    AMBER),
            ("Threat Agent",   "The entity that carries out the threat\n(attacker, insider, natural disaster)",        AMBER),
            ("Vulnerability",  "Weakness in a system or process a threat can exploit",                                 RED),
            ("Risk",           "Probability that a threat exploits a vulnerability\nand causes harm",                  RED),
            ("Exposure",       "Condition of being susceptible to loss\n(e.g. unpatched system is exposed)",           GRAY),
            ("Impact",         "Magnitude of harm if the risk is realized",                                            GREEN),
            ("Residual Risk",  "Risk remaining AFTER controls are applied",                                            "#AA44FF"),
        ]

        all_rows = VGroup()
        for term, defn, color in terms:
            row_bg = RoundedRectangle(corner_radius=0.12, width=13.0, height=0.72,
                                      color=color, fill_color=BG,
                                      fill_opacity=0.92, stroke_width=1.5)
            term_mob = Text(term, font_size=16, color=color, weight=BOLD)
            term_mob.next_to(row_bg.get_left(), RIGHT, buff=0.3)
            term_mob.set_y(row_bg.get_center()[1])
            # divider
            div = Line([0, 0, 0], [0, 0.45, 0], color=color,
                       stroke_width=1.0, stroke_opacity=0.4)
            div.move_to(row_bg.get_center() + LEFT*3.5)
            defn_mob = Text(defn, font_size=12, color=WHITE, line_spacing=1.15)
            defn_mob.move_to(row_bg.get_center() + RIGHT*1.5)
            defn_mob.set_y(row_bg.get_center()[1])
            all_rows.add(VGroup(row_bg, term_mob, div, defn_mob))

        all_rows.arrange(DOWN, buff=0.09)
        all_rows.move_to(DOWN*0.15)

        elapsed = 0.6
        for i, row in enumerate(all_rows):
            self.play(FadeIn(row, shift=RIGHT*0.15), run_time=0.4)
            dwell = [5.5, 4.0, 5.0, 4.5, 5.5, 4.5, 4.0, 5.0][i]
            self.wait(dwell)
            elapsed += 0.4 + dwell

        tip = exam_tip(self, "Risk appetite is set by senior management — not the security team")
        elapsed += 0.5
        self.wait(4.0)
        elapsed += 4.0

        self._pad("s2", elapsed)
        self._fade_content(bg)

    # ── SCENE 3 — Quantitative Risk Math ─────────────────────────
    def s3_quantitative_math(self):
        bg = self._tech_bg()
        self._sound("s3")

        scene_title(self, "Quantitative Risk Formulas", color=AMBER)

        # Formula table
        formula_data = [
            ("Asset Value",            "AV",  "Dollar value of the asset",                     BLUE),
            ("Exposure Factor",        "EF",  "% of asset lost per incident  (0.0 – 1.0)",     BLUE),
            ("Single Loss Expectancy", "SLE", "AV  ×  EF",                                     GREEN),
            ("Annualized Rate of\nOccurrence", "ARO", "Expected occurrences per year",          AMBER),
            ("Annualized Loss\nExpectancy",    "ALE", "SLE  ×  ARO",                            RED),
        ]

        hdr_y = 1.95
        col_x = [-5.8, -2.2, 1.8]
        hdr = VGroup(
            Text("TERM",       font_size=13, color=GRAY, weight=BOLD).move_to([col_x[0], hdr_y, 0]),
            Text("ABBR",       font_size=13, color=GRAY, weight=BOLD).move_to([col_x[1], hdr_y, 0]),
            Text("DEFINITION", font_size=13, color=GRAY, weight=BOLD).move_to([col_x[2], hdr_y, 0]),
        )
        hdr_line = Line(LEFT*6.8, RIGHT*6.8, color=GRAY, stroke_width=0.7, stroke_opacity=0.4)
        hdr_line.move_to(UP*1.72)
        self.play(FadeIn(hdr), Create(hdr_line), run_time=0.4)

        elapsed = 1.0
        for i, (term, abbr, defn, color) in enumerate(formula_data):
            y = 1.3 - i * 0.76
            row = VGroup(
                Text(term, font_size=14, color=color, weight=BOLD).move_to([col_x[0], y, 0]),
                Text(abbr, font_size=18, color=color, weight=BOLD).move_to([col_x[1], y, 0]),
                Text(defn, font_size=13, color=WHITE, line_spacing=1.1).move_to([col_x[2], y, 0]),
            )
            sep = Line(LEFT*6.8, RIGHT*6.8, stroke_width=0.3,
                       color="#223344", stroke_opacity=0.5).move_to(UP*(y - 0.35))
            self.play(FadeIn(row), Create(sep), run_time=0.4)
            self.wait(6.0)
            elapsed += 6.4

        # Worked example
        ex_bg = RoundedRectangle(corner_radius=0.16, width=13.0, height=1.6,
                                  color=GREEN, fill_color="#051A0A",
                                  fill_opacity=1, stroke_width=2)
        ex_bg.to_edge(DOWN, buff=0.28)
        ex_title = Text("Worked Example", font_size=14, color=GREEN, weight=BOLD)
        ex_title.move_to(ex_bg.get_top() + DOWN*0.25)
        ex_math = Text(
            "AV = $200,000  |  EF = 0.40  →  SLE = $80,000  |  ARO = 0.5  →  ALE = $40,000/yr",
            font_size=14, color=WHITE
        )
        ex_math.move_to(ex_bg.get_center() + DOWN*0.05)
        ex_note = Text(
            "Safeguard costs $12,000/yr and reduces ALE to $5,000  →  Net benefit = $23,000/yr  ✓ justified",
            font_size=12, color=AMBER
        )
        ex_note.move_to(ex_bg.get_bottom() + UP*0.25)
        self.play(FadeIn(ex_bg), Write(ex_title), run_time=0.4)
        self.play(Write(ex_math), run_time=0.6)
        self.play(FadeIn(ex_note), run_time=0.4)
        self.wait(5.0)
        elapsed += 6.4

        tip = exam_tip(self, "ALE = SLE × ARO  |  SLE = AV × EF  —  memorize both, know the order")
        elapsed += 0.5
        self.wait(4.0)
        elapsed += 4.0

        self._pad("s3", elapsed)
        self._fade_content(bg)

    # ── SCENE 4 — Assessment Types ───────────────────────────────
    def s4_assessment_types(self):
        bg = self._tech_bg()
        self._sound("s4")

        scene_title(self, "Risk Assessment Approaches", color=BLUE)

        cols_data = [
            ("QUALITATIVE", [
                "Subjective scales (High / Med / Low)",
                "No dollar figures produced",
                "Faster — uses expert judgment",
                "Delphi method: anonymous expert",
                "  consensus across multiple rounds",
                "Output: risk categories / matrix",
            ], BLUE, "#001528"),
            ("QUANTITATIVE", [
                "Numeric values — dollar amounts",
                "Produces ALE for cost/benefit analysis",
                "More rigorous; requires good data",
                "Enables direct safeguard justification",
                "",
                "Output: ALE, safeguard value",
            ], GREEN, "#051A0A"),
            ("SEMI-QUANTITATIVE", [
                "Hybrid: qualitative labels mapped",
                "  to numeric ranges",
                "Practical compromise",
                "Widely used in practice",
                "",
                "Output: scored risk matrix",
            ], AMBER, "#1A0D00"),
        ]

        cols = VGroup()
        for title_str, items, color, fill in cols_data:
            col_bg = RoundedRectangle(corner_radius=0.18, width=4.1, height=3.8,
                                      color=color, fill_color=fill,
                                      fill_opacity=0.95, stroke_width=2)
            col_title = Text(title_str, font_size=14, color=color, weight=BOLD)
            col_title.move_to(col_bg.get_top() + DOWN*0.3)
            sep_line = Line(LEFT*1.7, RIGHT*1.7, color=color,
                            stroke_width=0.7, stroke_opacity=0.5)
            sep_line.move_to(col_bg.get_center() + UP*1.35)
            col_items = VGroup(*[
                Text(it, font_size=12, color=WHITE) for it in items
            ]).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
            col_items.move_to(col_bg.get_center() + DOWN*0.2)
            cols.add(VGroup(col_bg, col_title, sep_line, col_items))

        cols.arrange(RIGHT, buff=0.45)
        cols.move_to(DOWN*0.2)
        self.play(FadeIn(cols, lag_ratio=0.25, scale=0.94), run_time=0.9)
        self.wait(14.0)

        tip = exam_tip(self,
            "Dollar figures = Quantitative  |  High/Med/Low categories = Qualitative")
        self.wait(4.0)
        elapsed = 20.0

        self._pad("s4", elapsed)
        self._fade_content(bg)

    # ── SCENE 5 — Risk Responses ─────────────────────────────────
    def s5_risk_responses(self):
        bg = self._tech_bg()
        self._sound("s5")

        scene_title(self, "Risk Response Strategies", color=AMBER)

        response_data = [
            ("TRANSFER",
             "Shift financial impact to a third party.\nCyber insurance. Outsourcing.\nLiability / regulatory accountability NEVER transfers.",
             BLUE, "#001528"),
            ("AVOID",
             "Eliminate the activity that creates the risk.\nDon't build the feature. Exit the market.\nNot always practical — some risk is inherent.",
             GREEN, "#051A0A"),
            ("REDUCE  (Mitigate)",
             "Implement controls to lower likelihood or impact.\nPatch systems. Encrypt data. Add MFA.\nMost common response in practice.",
             AMBER, "#1A0D00"),
            ("ACCEPT",
             "Acknowledge risk and choose not to act.\nMust be deliberate, documented, signed off.\nSenior management accepts — security team advises.",
             GRAY, "#0D1520"),
        ]

        all_cards = VGroup()
        for label, body, color, fill in response_data:
            card_bg = RoundedRectangle(corner_radius=0.15, width=13.0, height=1.02,
                                       color=color, fill_color=fill,
                                       fill_opacity=0.95, stroke_width=2)
            label_mob = Text(label, font_size=15, color=color, weight=BOLD)
            label_mob.next_to(card_bg.get_left(), RIGHT, buff=0.4)
            label_mob.set_y(card_bg.get_center()[1])
            body_mob = Text(body, font_size=12, color=WHITE, line_spacing=1.2)
            body_mob.move_to(card_bg.get_center() + RIGHT*2.0)
            body_mob.set_y(card_bg.get_center()[1])
            all_cards.add(VGroup(card_bg, label_mob, body_mob))

        all_cards.arrange(DOWN, buff=0.14)
        all_cards.move_to(DOWN*0.2)

        elapsed = 0.6
        dwells = [10.0, 9.0, 9.5, 10.0]
        for i, (card, dwell) in enumerate(zip(all_cards, dwells)):
            self.play(FadeIn(card, shift=RIGHT*0.2), run_time=0.5)
            self.wait(dwell)
            elapsed += 0.5 + dwell

        tip = exam_tip(self,
            "T-A-R-A: Transfer · Avoid · Reduce · Accept  |  Residual risk always remains")
        elapsed += 0.5
        self.wait(4.0)
        elapsed += 4.0

        self._pad("s5", elapsed)
        self._fade_content(bg)

    # ── SCENE 6 — STRIDE ─────────────────────────────────────────
    def s6_stride(self):
        bg = self._tech_bg()
        self._sound("s6")

        scene_title(self, "Threat Modeling — STRIDE", color=BLUE)

        stride_data = [
            ("S", "Spoofing",              "Authentication",   "Fake login page, spoofed email",      BLUE),
            ("T", "Tampering",             "Integrity",        "Altered log file, injected data",      GREEN),
            ("R", "Repudiation",           "Non-repudiation",  "Denying an action — needs audit logs", AMBER),
            ("I", "Information Disclosure","Confidentiality",  "Data leak, misconfigured bucket",      "#AA44FF"),
            ("D", "Denial of Service",     "Availability",     "Flood attack, resource exhaustion",    RED),
            ("E", "Elevation of Privilege","Authorization",    "Priv-esc, guest reads admin files",    GRAY),
        ]

        col_x = [-5.8, -3.0, 0.6, 4.2]
        hdr_y = 1.85
        hdr = VGroup(
            Text("",            font_size=13, color=GRAY, weight=BOLD).move_to([col_x[0], hdr_y, 0]),
            Text("CATEGORY",    font_size=13, color=GRAY, weight=BOLD).move_to([col_x[1], hdr_y, 0]),
            Text("VIOLATES",    font_size=13, color=GRAY, weight=BOLD).move_to([col_x[2], hdr_y, 0]),
            Text("EXAMPLE",     font_size=13, color=GRAY, weight=BOLD).move_to([col_x[3], hdr_y, 0]),
        )
        hdr_line = Line(LEFT*6.8, RIGHT*6.8, color=GRAY, stroke_width=0.7, stroke_opacity=0.4)
        hdr_line.move_to(UP*1.62)
        self.play(FadeIn(hdr), Create(hdr_line), run_time=0.4)

        elapsed = 1.0
        for i, (letter, cat, violates, example, color) in enumerate(stride_data):
            y = 1.2 - i * 0.66
            letter_circle = Circle(radius=0.24, color=color,
                                   fill_color=color, fill_opacity=0.9, stroke_width=0)
            letter_circle.move_to([col_x[0], y, 0])
            letter_mob = Text(letter, font_size=17, color=BG, weight=BOLD)
            letter_mob.move_to(letter_circle.get_center())
            cat_mob  = Text(cat,      font_size=14, color=color, weight=BOLD).move_to([col_x[1], y, 0])
            viol_mob = Text(violates, font_size=13, color=WHITE).move_to([col_x[2], y, 0])
            ex_mob   = Text(example,  font_size=12, color=GRAY).move_to([col_x[3], y, 0])
            sep = Line(LEFT*6.8, RIGHT*6.8, stroke_width=0.3,
                       color="#223344", stroke_opacity=0.5).move_to(UP*(y-0.30))
            row = VGroup(letter_circle, letter_mob, cat_mob, viol_mob, ex_mob, sep)
            self.play(FadeIn(row, shift=UP*0.1), run_time=0.4)
            self.wait(6.5)
            elapsed += 6.9

        tip = exam_tip(self,
            "STRIDE maps to the 5 pillars — Spoofing→Auth, Tampering→Integrity, etc.")
        elapsed += 0.5
        self.wait(4.0)
        elapsed += 4.0

        self._pad("s6", elapsed)
        self._fade_content(bg)

    # ── SCENE 7 — PASTA & Attack Trees ───────────────────────────
    def s7_pasta_trees(self):
        bg = self._tech_bg()
        self._sound("s7")

        scene_title(self, "Threat Modeling — PASTA & Beyond", color=AMBER)

        # PASTA box
        pasta_bg = RoundedRectangle(corner_radius=0.18, width=6.0, height=3.8,
                                     color=BLUE, fill_color="#001528",
                                     fill_opacity=0.95, stroke_width=2)
        pasta_bg.move_to(LEFT*3.3 + DOWN*0.2)
        pasta_title = Text("PASTA", font_size=22, color=BLUE, weight=BOLD)
        pasta_full  = Text("Process for Attack Simulation\n& Threat Analysis",
                           font_size=13, color=GRAY, line_spacing=1.2)
        pasta_title.move_to(pasta_bg.get_top() + DOWN*0.35)
        pasta_full.next_to(pasta_title, DOWN, buff=0.12)
        pasta_items = VGroup(
            Text("7-stage risk-centric methodology", font_size=13, color=WHITE),
            Text("Aligns threats to business objectives", font_size=13, color=WHITE),
            Text("Produces attack simulations", font_size=13, color=WHITE),
            Text("When to use: connect technical risk", font_size=13, color=WHITE),
            Text("  to quantifiable business impact", font_size=13, color=WHITE),
        ).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        pasta_items.next_to(pasta_full, DOWN, buff=0.2)

        # Attack Trees box
        tree_bg = RoundedRectangle(corner_radius=0.18, width=6.0, height=3.8,
                                    color=GREEN, fill_color="#051A0A",
                                    fill_opacity=0.95, stroke_width=2)
        tree_bg.move_to(RIGHT*3.3 + DOWN*0.2)
        tree_title = Text("Attack Trees", font_size=22, color=GREEN, weight=BOLD)
        tree_title.move_to(tree_bg.get_top() + DOWN*0.35)
        tree_items = VGroup(
            Text("Hierarchical threat representation", font_size=13, color=WHITE),
            Text("Root = attacker's objective", font_size=13, color=WHITE),
            Text("Child nodes = steps / preconditions", font_size=13, color=WHITE),
            Text("Enumerate ALL paths to compromise", font_size=13, color=WHITE),
            Text("Use to prioritize defenses", font_size=13, color=WHITE),
        ).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        tree_items.next_to(tree_title, DOWN, buff=0.25)

        self.play(
            FadeIn(pasta_bg), Write(pasta_title), FadeIn(pasta_full), FadeIn(pasta_items),
            FadeIn(tree_bg),  Write(tree_title),  FadeIn(tree_items),
            run_time=0.9
        )
        self.wait(12.0)

        # DREAD footnote
        dread_txt = Text(
            "DREAD (deprecated): Damage · Reproducibility · Exploitability · Affected users · Discoverability",
            font_size=13, color=GRAY
        )
        dread_txt.to_edge(DOWN, buff=0.4)
        self.play(FadeIn(dread_txt), run_time=0.4)
        self.wait(5.0)
        elapsed = 19.0

        self._pad("s7", elapsed)
        self._fade_content(bg)

    # ── SCENE 8 — NIST RMF ───────────────────────────────────────
    def s8_nist_rmf(self):
        bg = self._tech_bg()
        self._sound("s8")

        scene_title(self, "NIST Risk Management Framework", color=BLUE)

        steps = [
            ("1", "PREPARE",    "Establish context, priorities, resources",         GRAY),
            ("2", "CATEGORIZE", "Classify system/data by impact (FIPS 199)",        BLUE),
            ("3", "SELECT",     "Choose controls from NIST 800-53",                 GREEN),
            ("4", "IMPLEMENT",  "Deploy and configure selected controls",            GREEN),
            ("5", "ASSESS",     "Evaluate whether controls work as intended",        AMBER),
            ("6", "AUTHORIZE",  "Senior official formally accepts residual risk",    RED),
            ("7", "MONITOR",    "Continuously track effectiveness & new threats",    "#AA44FF"),
        ]

        BAR_H = 0.56
        y_start = 1.72

        elapsed = 0.6
        for i, (num, step, desc, color) in enumerate(steps):
            cy = y_start - i * (BAR_H + 0.10)
            bar = Rectangle(width=13.0, height=BAR_H,
                            color=color, fill_color=BG, fill_opacity=0.88, stroke_width=1.5)
            bar.move_to([0, cy, 0])
            num_mob = Text(num, font_size=14, color=color, weight=BOLD)
            num_mob.next_to(bar.get_left(), RIGHT, buff=0.3)
            num_mob.set_y(cy)
            step_mob = Text(step, font_size=14, color=color, weight=BOLD)
            step_mob.next_to(num_mob, RIGHT, buff=0.45)
            step_mob.set_y(cy)
            desc_mob = Text(desc, font_size=12, color=WHITE)
            desc_mob.next_to(bar.get_right(), LEFT, buff=0.35)
            desc_mob.set_y(cy)
            grp = VGroup(bar, num_mob, step_mob, desc_mob)
            self.play(FadeIn(grp, shift=LEFT*0.15), run_time=0.35)
            self.wait(5.5)
            elapsed += 5.85

        tip = exam_tip(self,
            "Categorize → Select → Implement → Assess → Authorize  |  Monitor is ongoing")
        elapsed += 0.5
        self.wait(4.0)
        elapsed += 4.0

        self._pad("s8", elapsed)
        self._fade_content(bg)

    # ── SCENE 9 — Supply Chain Risk ──────────────────────────────
    def s9_supply_chain(self):
        bg = self._tech_bg()
        self._sound("s9")

        scene_title(self, "Supply Chain Risk Management", color=AMBER)

        controls = [
            ("Vendor Assessment\n& Due Diligence",
             "Review SOC 2 reports, pen test results,\ncertifications BEFORE engagement.",
             BLUE, "#001528"),
            ("Right-to-Audit\nClause",
             "Contract provision allowing you to audit\nthe vendor. Refusal = risk indicator.",
             GREEN, "#051A0A"),
            ("Service Level\nAgreement (SLA)",
             "Defines security & operational commitments.\nCreates contractual accountability.",
             AMBER, "#1A0D00"),
        ]

        cols = VGroup()
        for title_str, body, color, fill in controls:
            col_bg = RoundedRectangle(corner_radius=0.18, width=4.0, height=2.8,
                                      color=color, fill_color=fill,
                                      fill_opacity=0.95, stroke_width=2)
            col_title = Text(title_str, font_size=15, color=color,
                             weight=BOLD, line_spacing=1.2)
            col_title.move_to(col_bg.get_top() + DOWN*0.48)
            col_body = Text(body, font_size=13, color=WHITE, line_spacing=1.3)
            col_body.move_to(col_bg.get_center() + DOWN*0.3)
            cols.add(VGroup(col_bg, col_title, col_body))

        cols.arrange(RIGHT, buff=0.55)
        cols.move_to(DOWN*0.0)
        self.play(FadeIn(cols, lag_ratio=0.2, scale=0.93), run_time=0.8)
        self.wait(10.0)

        note = Text(
            "Outsourcing transfers operational risk — NEVER legal or regulatory accountability.",
            font_size=16, color=RED, weight=BOLD
        )
        note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note), run_time=0.4)
        self.wait(5.0)
        elapsed = 17.0

        self._pad("s9", elapsed)
        self._fade_content(bg)

    # ── SCENE 10 — Practice Questions ────────────────────────────
    def s10_practice_questions(self):
        bg = self._tech_bg()
        self._sound("s10")

        scene_title(self, "Practice Questions", color=GREEN)

        questions = [
            (
                "A server worth $200,000 faces ransomware with a 40% exposure factor.\n"
                "The threat is expected to occur twice per year.\n"
                "What is the Annualized Loss Expectancy?",
                "A. $40,000",
                "B. $80,000",
                "C. $160,000",
                "C — ALE = SLE × ARO = (200,000 × 0.40) × 2 = $80,000 × 2 = $160,000/yr"
            ),
            (
                "A risk assessment produces a matrix categorizing risks as Critical, High,\n"
                "Medium, or Low — with no dollar values assigned to any risk.\n"
                "This is an example of which assessment type?",
                "A. Quantitative",
                "B. Qualitative",
                "C. Factor Analysis of Information Risk",
                "B — Qualitative. Categories without dollar figures define qualitative assessment."
            ),
            (
                "During threat modeling, analysts identify a path where an attacker gains\n"
                "administrator access by exploiting a privilege escalation flaw.\n"
                "Which STRIDE category applies?",
                "A. Tampering",
                "B. Repudiation",
                "C. Elevation of Privilege",
                "C — Elevation of Privilege. Gaining capabilities beyond what is authorized."
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

            ans_bg = RoundedRectangle(corner_radius=0.14, width=12.0, height=0.62,
                                       color=GREEN, fill_color="#051A0A",
                                       fill_opacity=1, stroke_width=1.5)
            ans_bg.to_edge(DOWN, buff=0.35)
            ans_txt = Text(answer, font_size=15, color=WHITE, weight=BOLD)
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
            ("1", "Formulas:",    "ALE = SLE × ARO  |  SLE = AV × EF",               BLUE),
            ("2", "TARA:",        "Transfer · Avoid · Reduce · Accept",                GREEN),
            ("3", "STRIDE:",      "Spoof · Tamper · Repudiate · Disclose · DoS · EoP", AMBER),
            ("4", "NIST RMF:",    "Prepare → Categorize → Select → Implement →\n"
                                  "Assess → Authorize → Monitor",                      RED),
        ]

        all_cards = VGroup()
        for num, label, detail, color in cards:
            card_bg = RoundedRectangle(corner_radius=0.18, width=13.0, height=0.88,
                                       color=color, fill_color=BG,
                                       fill_opacity=0.95, stroke_width=2)
            num_mob    = Text(num,    font_size=20, color=color, weight=BOLD)
            num_mob.move_to(card_bg.get_left() + RIGHT*0.5)
            label_mob  = Text(label,  font_size=17, color=color, weight=BOLD)
            label_mob.move_to(card_bg.get_left() + RIGHT*2.0)
            detail_mob = Text(detail, font_size=15, color=WHITE, line_spacing=1.2)
            detail_mob.move_to(card_bg.get_center() + RIGHT*1.8)
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

        cta_head = heading("Test yourself right now.", size=26, color=WHITE)
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

        next_ep = Text("Next: D1-P3 — Business Continuity, Disaster Recovery & Personnel Security",
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
