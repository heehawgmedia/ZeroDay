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

AUDIO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cissp_d2_audio")

_DUR_DEFAULTS = {
    "s0":  52.0,   # hook + roadmap
    "s1":  78.0,   # data classification
    "s2":  72.0,   # ownership roles
    "s3":  65.0,   # handling requirements
    "s4":  68.0,   # data lifecycle
    "s5":  65.0,   # retention + EOL/EOS
    "s6":  75.0,   # sanitization
    "s7":  70.0,   # data security controls
    "s8":  58.0,   # scoping & tailoring
    "s9":  58.0,   # practice questions
    "s10": 42.0,   # recap + CTA
    "s11": 22.0,   # book ad (end)
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


def _preflight_audio(audio_dir: str, dur: dict, generator: str) -> None:
    """Fail loudly before rendering if any audio file is missing or too small."""
    missing = []
    for key in dur:
        path = os.path.join(audio_dir, f"{key}.mp3")
        if not os.path.exists(path) or os.path.getsize(path) < 1024:
            missing.append(key)
    if missing:
        keys = " ".join(missing)
        raise RuntimeError(
            f"\n{'='*60}\n"
            f"  MISSING AUDIO — DO NOT RENDER\n"
            f"{'='*60}\n"
            f"  Files missing or invalid: {keys}\n"
            f"  Fix: python {generator} --force --only {keys}\n"
            f"{'='*60}\n"
        )


# ═══════════════════════════════════════════════════════════════════
#  CISSP D2  —  manim -qh cissp_d2_explainer.py CISSP_D2
# ═══════════════════════════════════════════════════════════════════
class CISSP_D2(Scene):
    def construct(self):
        _preflight_audio(AUDIO, DUR, "generate_cissp_d2_narration.py")
        self.s0_hook_roadmap()
        self.s1_classification()
        self.s2_ownership_roles()
        self.s3_handling()
        self.s4_lifecycle()
        self.s5_retention_eol()
        self.s6_sanitization()
        self.s7_security_controls()
        self.s8_scoping_tailoring()
        self.s9_practice_questions()
        self.s10_recap_cta()
        self.s11_book_ad()

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

    # ── SCENE 0 — Hook + Roadmap ─────────────────────────────────
    def s0_hook_roadmap(self):
        bg = self._tech_bg()

        welcome = Text("Welcome back to Zero Day Labs!", font_size=38, color=BLUE, weight=BOLD)
        welcome.move_to(ORIGIN)
        self.play(Write(welcome), run_time=0.8)
        self.wait(1.5)
        self.play(FadeOut(welcome), run_time=0.5)

        self._sound("s0")

        # Breach scenario
        lines = VGroup(
            Text("Misconfigured S3 bucket.", font_size=28, color=RED, weight=BOLD),
            Text("Customer records exposed for six months.", font_size=22, color=WHITE),
        ).arrange(DOWN, buff=0.3)
        lines.move_to(UP*1.0)
        self.play(Write(lines[0]), run_time=0.8)
        self.play(FadeIn(lines[1], shift=UP*0.1), run_time=0.5)
        self.wait(1.5)

        failures = VGroup(
            Text("✗  Data was never classified — nobody knew how sensitive it was.",
                 font_size=17, color=GRAY),
            Text("✗  Data was never labeled — nobody knew what it contained.",
                 font_size=17, color=GRAY),
            Text("✗  No retention policy — it should have been deleted two years ago.",
                 font_size=17, color=GRAY),
        ).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        failures.next_to(lines, DOWN, buff=0.5)
        for f in failures:
            self.play(FadeIn(f, shift=RIGHT*0.15), run_time=0.35)
        self.wait(3.0)

        self._fade_content(bg, run_time=0.4)
        bg2 = self._tech_bg()

        series = Text("CISSP Domain Mastery Series", font_size=20, color=GRAY)
        ep_title = heading("Domain 2  |  Asset Security", size=38, color=WHITE)
        ep_title.move_to(UP*1.2)
        series.next_to(ep_title, UP, buff=0.3)
        self.play(FadeIn(series), Write(ep_title), run_time=0.9)

        obj_label = Text("Exam Objectives Covered:", font_size=17, color=AMBER, weight=BOLD)
        obj_label.next_to(ep_title, DOWN, buff=0.4)
        obj_nums = mono("2.1  |  2.2  |  2.3  |  2.4  |  2.5  |  2.6", size=18, color=BLUE)
        obj_nums.next_to(obj_label, DOWN, buff=0.18)
        self.play(FadeIn(obj_label), Write(obj_nums), run_time=0.5)

        topics = [
            "Data Classification — Government & Commercial",
            "Data Ownership — Owner, Custodian, Steward, Controller, Processor",
            "Handling Requirements — Labeling, Marking, Storage, Transmission",
            "Data Lifecycle — 6 phases with security controls at each",
            "Asset Retention, EOL vs. End of Support, Legal Hold",
            "Data Sanitization — Clearing, Purging, Destruction",
            "Data Security Controls — Encryption, DLP, DRM, Tokenization",
            "Scoping, Tailoring & Compensating Controls",
        ]
        topic_group = VGroup(*[
            Text(f"• {t}", font_size=14, color=WHITE) for t in topics
        ]).arrange(DOWN, buff=0.12, aligned_edge=LEFT)
        topic_group.next_to(obj_nums, DOWN, buff=0.28)
        for t in topic_group:
            self.play(FadeIn(t, shift=RIGHT*0.12), run_time=0.15)

        elapsed = 18.0
        self._pad("s0", elapsed)
        self._fade_content(bg2)

    # ── SCENE 1 — Data Classification ────────────────────────────
    def s1_classification(self):
        bg = self._tech_bg()
        self._sound("s1")

        scene_title(self, "Data Classification", color=BLUE)

        # Two columns: Government vs Commercial
        gov_levels = [
            ("TOP SECRET",    "Exceptionally grave damage\nto national security", RED),
            ("SECRET",        "Serious damage",                                    AMBER),
            ("CONFIDENTIAL",  "Damage",                                            BLUE),
            ("UNCLASSIFIED",  "No expected damage from disclosure",                GRAY),
        ]
        com_levels = [
            ("CONFIDENTIAL /\nPROPRIETARY", "Trade secrets, strategic plans,\nunreleased financials", RED),
            ("PRIVATE",       "Sensitive personal data:\nHR records, medical data",                    AMBER),
            ("SENSITIVE",     "Requires care; less restricted\nthan Private",                          BLUE),
            ("PUBLIC",        "Intended for general release",                                           GRAY),
        ]

        def make_col(title, levels, header_color):
            col_bg = RoundedRectangle(corner_radius=0.18, width=6.2, height=5.2,
                                      color=header_color, fill_color=BG,
                                      fill_opacity=0.94, stroke_width=2)
            col_title = Text(title, font_size=16, color=header_color, weight=BOLD)
            col_title.move_to(col_bg.get_top() + DOWN*0.3)
            div = Line(LEFT*2.7, RIGHT*2.7, color=header_color,
                       stroke_width=0.7, stroke_opacity=0.5)
            div.next_to(col_title, DOWN, buff=0.12)
            rows = VGroup()
            for label, desc, color in levels:
                lbl = Text(label, font_size=13, color=color, weight=BOLD)
                dsc = Text(desc, font_size=11, color=WHITE, line_spacing=1.1)
                rows.add(VGroup(lbl, dsc).arrange(DOWN, buff=0.04, aligned_edge=LEFT))
            rows.arrange(DOWN, buff=0.26, aligned_edge=LEFT)
            rows.next_to(div, DOWN, buff=0.18)
            return VGroup(col_bg, col_title, div, rows)

        gov_col = make_col("GOVERNMENT / MILITARY", gov_levels, BLUE)
        com_col = make_col("COMMERCIAL",            com_levels, GREEN)
        cols = VGroup(gov_col, com_col).arrange(RIGHT, buff=0.5)
        cols.move_to(DOWN*0.12)
        self.play(FadeIn(cols, lag_ratio=0.25, scale=0.93), run_time=0.9)
        self.wait(18.0)

        tip = exam_tip(self,
            "Owner classifies  |  Classify at highest sensitivity  |  Can be reclassified over time")
        self.wait(5.0)
        elapsed = 25.0

        self._pad("s1", elapsed)
        self._fade_content(bg)

    # ── SCENE 2 — Ownership Roles ─────────────────────────────────
    def s2_ownership_roles(self):
        bg = self._tech_bg()
        self._sound("s2")

        scene_title(self, "Data Ownership Roles", color=AMBER)

        roles = [
            ("DATA OWNER",
             "Business role (manager / exec)\nClassifies data · Approves access · Accountable",
             "CFO owns financial data · CHRO owns HR records",
             RED),
            ("DATA CUSTODIAN",
             "Technical role (IT / ops)\nImplements controls the owner specifies",
             "Backup, encryption, patching the storage system",
             BLUE),
            ("DATA STEWARD",
             "Manages data quality & governance compliance\nEnsures accuracy, consistency, policy adherence",
             "Appears in enterprise data governance contexts",
             GREEN),
            ("DATA CONTROLLER",
             "GDPR role: determines the PURPOSE\nand MEANS of processing personal data",
             "Your organization collecting customer data = controller",
             AMBER),
            ("DATA PROCESSOR",
             "GDPR role: processes personal data\nON BEHALF of the controller",
             "Cloud provider processing your customer data = processor",
             GRAY),
        ]

        all_rows = VGroup()
        for label, desc, example, color in roles:
            row_bg = RoundedRectangle(corner_radius=0.12, width=13.0, height=0.85,
                                      color=color, fill_color=BG,
                                      fill_opacity=0.92, stroke_width=1.8)
            label_mob = Text(label, font_size=14, color=color, weight=BOLD)
            label_mob.next_to(row_bg.get_left(), RIGHT, buff=0.35)
            label_mob.set_y(row_bg.get_center()[1])
            desc_mob = Text(desc, font_size=12, color=WHITE, line_spacing=1.15)
            desc_mob.move_to(row_bg.get_center() + RIGHT*0.5)
            desc_mob.set_y(row_bg.get_center()[1])
            ex_mob = Text(example, font_size=11, color=GRAY)
            ex_mob.next_to(row_bg.get_right(), LEFT, buff=0.35)
            ex_mob.set_y(row_bg.get_center()[1])
            all_rows.add(VGroup(row_bg, label_mob, desc_mob, ex_mob))

        all_rows.arrange(DOWN, buff=0.10)
        all_rows.move_to(DOWN*0.15)

        elapsed = 0.6
        dwells = [10.0, 9.0, 8.0, 9.0, 8.5]
        for row, dwell in zip(all_rows, dwells):
            self.play(FadeIn(row, shift=RIGHT*0.15), run_time=0.4)
            self.wait(dwell)
            elapsed += 0.4 + dwell

        tip = exam_tip(self,
            "Owner DECIDES — Custodian IMPLEMENTS  |  Never blend these roles in an answer")
        elapsed += 0.5
        self.wait(4.0)
        elapsed += 4.0

        self._pad("s2", elapsed)
        self._fade_content(bg)

    # ── SCENE 3 — Handling Requirements ──────────────────────────
    def s3_handling(self):
        bg = self._tech_bg()
        self._sound("s3")

        scene_title(self, "Data Handling Requirements", color=BLUE)

        areas = [
            ("LABELING",      "Human-readable classification on documents, files, media.\nUnmarked data is treated as public by default.",             BLUE),
            ("MARKING",       "Physical or digital indicators embedded in assets.\nHeaders/footers on docs · Metadata in files · Labels on media.",   GREEN),
            ("STORAGE",       "Controls match classification level.\nTop Secret may require air-gapped systems and two-person integrity.",             AMBER),
            ("TRANSMISSION",  "Confidential data over public/untrusted networks requires encryption.\nProtection level matches classification.",       RED),
        ]

        all_rows = VGroup()
        for title_str, body, color in areas:
            row_bg = RoundedRectangle(corner_radius=0.12, width=13.0, height=1.1,
                                      color=color, fill_color=BG,
                                      fill_opacity=0.92, stroke_width=1.8)
            label_mob = Text(title_str, font_size=14, color=color, weight=BOLD)
            label_mob.next_to(row_bg.get_left(), RIGHT, buff=0.35)
            label_mob.set_y(row_bg.get_center()[1])
            desc_mob = Text(body, font_size=12, color=WHITE, line_spacing=1.2)
            desc_mob.move_to(row_bg.get_center() + RIGHT*1.5)
            desc_mob.set_y(row_bg.get_center()[1])
            all_rows.add(VGroup(row_bg, label_mob, desc_mob))

        all_rows.arrange(DOWN, buff=0.14)
        all_rows.move_to(DOWN*0.2)

        elapsed = 0.6
        dwells = [10.0, 9.0, 9.5, 9.5]
        for row, dwell in zip(all_rows, dwells):
            self.play(FadeIn(row, shift=RIGHT*0.15), run_time=0.4)
            self.wait(dwell)
            elapsed += 0.4 + dwell

        tip = exam_tip(self,
            "Need-to-Know: clearance + business need — both required, neither alone is enough")
        elapsed += 0.5
        self.wait(5.0)
        elapsed += 5.0

        self._pad("s3", elapsed)
        self._fade_content(bg)

    # ── SCENE 4 — Data Lifecycle ──────────────────────────────────
    def s4_lifecycle(self):
        bg = self._tech_bg()
        self._sound("s4")

        scene_title(self, "Data Lifecycle", color=GREEN)

        phases = [
            ("CREATE /\nCOLLECT",  "Classification assigned at creation.\nOwner's role is most critical here.",               BLUE),
            ("STORE",              "Encryption at rest · Access controls · Backup.\nProtection matches classification.",        GREEN),
            ("USE /\nPROCESS",     "Monitoring, DLP, and logging apply.\nData actively being worked on.",                     AMBER),
            ("SHARE /\nDISTRIBUTE","Need-to-know governs recipients.\nEncryption in transit · Third-party = controller/processor.", RED),
            ("ARCHIVE",            "Retention schedules apply.\nClassification unchanged — still requires full protection.",   GRAY),
            ("DESTROY /\nDISPOSE", "Sanitize to match classification level.\nMethod must be documented.",                     "#AA44FF"),
        ]

        cards = []
        for i, (phase, desc, color) in enumerate(phases):
            ph_bg = RoundedRectangle(corner_radius=0.14, width=4.1, height=2.05,
                                     color=color, fill_color=BG,
                                     fill_opacity=0.92, stroke_width=1.8)
            ph_num = Circle(radius=0.22, color=color,
                            fill_color=color, fill_opacity=0.9, stroke_width=0)
            ph_num.move_to(ph_bg.get_top() + DOWN*0.3)
            num_txt = Text(str(i+1), font_size=14, color=BG, weight=BOLD)
            num_txt.move_to(ph_num.get_center())
            ph_label = Text(phase, font_size=13, color=color,
                            weight=BOLD, line_spacing=1.1)
            ph_label.next_to(ph_num, DOWN, buff=0.08)
            ph_desc = Text(desc, font_size=10, color=WHITE, line_spacing=1.2)
            ph_desc.move_to(ph_bg.get_bottom() + UP*0.44)
            cards.append(VGroup(ph_bg, ph_num, num_txt, ph_label, ph_desc))

        row1 = VGroup(*cards[:3]).arrange(RIGHT, buff=0.28)
        row2 = VGroup(*cards[3:]).arrange(RIGHT, buff=0.28)
        all_phases = VGroup(row1, row2).arrange(DOWN, buff=0.25)
        all_phases.move_to(DOWN*0.22)
        self.play(FadeIn(all_phases, lag_ratio=0.12, scale=0.93), run_time=1.0)
        self.wait(16.0)

        tip = exam_tip(self,
            "Classification persists through ALL lifecycle phases — archival does not reduce sensitivity")
        self.wait(5.0)
        elapsed = 23.0

        self._pad("s4", elapsed)
        self._fade_content(bg)

    # ── SCENE 5 — Retention & EOL/EOS ────────────────────────────
    def s5_retention_eol(self):
        bg = self._tech_bg()
        self._sound("s5")

        scene_title(self, "Asset Retention & End of Life", color=AMBER)

        # Retention + Legal Hold left column
        ret_bg = RoundedRectangle(corner_radius=0.18, width=5.9, height=4.6,
                                   color=BLUE, fill_color="#001528",
                                   fill_opacity=0.95, stroke_width=2)
        ret_bg.move_to(LEFT*3.3 + DOWN*0.2)
        ret_title = Text("RETENTION", font_size=20, color=BLUE, weight=BOLD)
        ret_title.move_to(ret_bg.get_top() + DOWN*0.35)
        ret_items = VGroup(
            Text("Defines how long data must be kept", font_size=13, color=WHITE),
            Text("Driven by legal, regulatory, business needs", font_size=13, color=WHITE),
            Text("Min retention: must keep AT LEAST this long", font_size=13, color=AMBER),
            Text("Max retention: must DELETE by this date (GDPR)", font_size=13, color=AMBER),
            Text("─" * 28, font_size=10, color=BLUE),
            Text("LEGAL HOLD (Litigation Hold)", font_size=13, color=RED, weight=BOLD),
            Text("Overrides ALL retention schedules", font_size=13, color=WHITE),
            Text("Anticipated litigation = preserve everything", font_size=13, color=WHITE),
            Text("Destroying held data = SPOLIATION", font_size=13, color=RED, weight=BOLD),
        ).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        ret_items.next_to(ret_title, DOWN, buff=0.2)

        # EOL/EOS right column
        eol_bg = RoundedRectangle(corner_radius=0.18, width=5.9, height=4.6,
                                   color=RED, fill_color="#1A0000",
                                   fill_opacity=0.95, stroke_width=2)
        eol_bg.move_to(RIGHT*3.3 + DOWN*0.2)
        eol_title = Text("EOL vs. EOS", font_size=20, color=RED, weight=BOLD)
        eol_title.move_to(eol_bg.get_top() + DOWN*0.35)
        eol_items = VGroup(
            Text("End of Life (EOL)", font_size=14, color=AMBER, weight=BOLD),
            Text("Vendor stops selling / developing product", font_size=13, color=WHITE),
            Text("System may still receive patches", font_size=13, color=WHITE),
            Text("─" * 28, font_size=10, color=RED),
            Text("End of Support (EOS)", font_size=14, color=RED, weight=BOLD),
            Text("Vendor stops patches, updates, support", font_size=13, color=WHITE),
            Text("New vulnerabilities = permanently unmitigated", font_size=13, color=RED),
            Text("EOS is the CRITICAL security threshold", font_size=13, color=WHITE, weight=BOLD),
            Text("Running EOS must be documented as accepted risk", font_size=12, color=GRAY),
        ).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        eol_items.next_to(eol_title, DOWN, buff=0.2)

        self.play(
            FadeIn(ret_bg), Write(ret_title), FadeIn(ret_items),
            FadeIn(eol_bg), Write(eol_title), FadeIn(eol_items),
            run_time=0.9
        )
        self.wait(16.0)

        tip = exam_tip(self,
            "EOS = no more patches = unmitigated vulnerabilities  |  Must be accepted and documented")
        self.wait(4.0)
        elapsed = 22.0

        self._pad("s5", elapsed)
        self._fade_content(bg)

    # ── SCENE 6 — Data Sanitization ──────────────────────────────
    def s6_sanitization(self):
        bg = self._tech_bg()
        self._sound("s6")

        scene_title(self, "Data Remanence & Sanitization", color=RED)

        remanence_bg = RoundedRectangle(corner_radius=0.14, width=13.0, height=0.68,
                                         color=AMBER, fill_color="#1A0D00",
                                         fill_opacity=1, stroke_width=2)
        remanence_bg.move_to(UP*1.95)
        remanence_txt = Text(
            "Data Remanence: residual data that remains after deletion — "
            "deleting a file removes the pointer, NOT the data.",
            font_size=15, color=WHITE, weight=BOLD
        )
        remanence_txt.move_to(remanence_bg.get_center())
        self.play(FadeIn(remanence_bg), Write(remanence_txt), run_time=0.6)
        self.wait(4.0)

        methods = [
            ("CLEARING",
             "Overwrite media with non-sensitive data.\nSuitable for reuse WITHIN the same organization.",
             "NOT sufficient for media leaving the org.",
             GREEN),
            ("PURGING",
             "Degaussing (magnetic field randomizes content)\nor cryptographic erasure (destroy the key).\nFor media leaving the organization.",
             "Higher assurance than clearing.",
             AMBER),
            ("DESTRUCTION",
             "Physical destruction: shredding, incineration,\npulverizing, disintegration.\nHighest assurance — no recovery possible.",
             "Required for highest classification levels.",
             RED),
        ]

        all_cards = VGroup()
        for label, desc, note, color in methods:
            card_bg = RoundedRectangle(corner_radius=0.15, width=13.0, height=1.05,
                                       color=color, fill_color=BG,
                                       fill_opacity=0.92, stroke_width=2)
            label_mob = Text(label, font_size=15, color=color, weight=BOLD)
            label_mob.next_to(card_bg.get_left(), RIGHT, buff=0.35)
            label_mob.set_y(card_bg.get_center()[1])
            desc_mob = Text(desc, font_size=12, color=WHITE, line_spacing=1.2)
            desc_mob.move_to(card_bg.get_center() + RIGHT*0.5)
            desc_mob.set_y(card_bg.get_center()[1])
            note_mob = Text(note, font_size=12, color=color)
            note_mob.next_to(card_bg.get_right(), LEFT, buff=0.35)
            note_mob.set_y(card_bg.get_center()[1])
            all_cards.add(VGroup(card_bg, label_mob, desc_mob, note_mob))

        all_cards.arrange(DOWN, buff=0.14)
        all_cards.move_to(DOWN*0.68)

        elapsed = 5.5
        dwells = [9.0, 9.0, 9.0]
        for card, dwell in zip(all_cards, dwells):
            self.play(FadeIn(card, shift=RIGHT*0.15), run_time=0.4)
            self.wait(dwell)
            elapsed += 0.4 + dwell

        tip = exam_tip(self,
            "Reuse in org→Clear  |  Leaving org→Purge  |  Highest classification→Destroy")
        elapsed += 0.5
        self.wait(4.0)
        elapsed += 4.0

        self._pad("s6", elapsed)
        self._fade_content(bg)

    # ── SCENE 7 — Data Security Controls ─────────────────────────
    def s7_security_controls(self):
        bg = self._tech_bg()
        self._sound("s7")

        scene_title(self, "Data Security Controls", color=BLUE)

        controls = [
            ("ENCRYPTION",
             "Protects confidentiality at rest AND in transit.\nClassification drives encryption requirements.",
             "Full disk, database, transport (TLS)",
             BLUE),
            ("DLP — Data Loss\nPrevention",
             "Monitors data in use, in motion, at rest.\nPREVENTS unauthorized exfiltration.",
             "Blocks email attachments, USB, cloud uploads",
             GREEN),
            ("DRM / IRM",
             "Controls what recipients CAN DO after access.\nPrevents copy, forward, print, screenshot.",
             "DLP = stops it leaving  |  DRM = controls it after",
             AMBER),
            ("TOKENIZATION",
             "Replaces sensitive data with a non-sensitive token.\nActual data stored in secure token vault.",
             "Extensively used in PCI DSS / payment processing",
             RED),
            ("DATA MASKING",
             "Replaces real data with fictitious but realistic values.\nDevelopers test on masked data — never production.",
             "Non-production environments, QA, testing",
             GRAY),
        ]

        all_rows = VGroup()
        for label, desc, note, color in controls:
            row_bg = RoundedRectangle(corner_radius=0.12, width=13.0, height=0.82,
                                      color=color, fill_color=BG,
                                      fill_opacity=0.90, stroke_width=1.5)
            label_mob = Text(label, font_size=13, color=color, weight=BOLD, line_spacing=1.1)
            label_mob.next_to(row_bg.get_left(), RIGHT, buff=0.3)
            label_mob.set_y(row_bg.get_center()[1])
            desc_mob = Text(desc, font_size=12, color=WHITE, line_spacing=1.15)
            desc_mob.move_to(row_bg.get_center() + RIGHT*0.6)
            desc_mob.set_y(row_bg.get_center()[1])
            note_mob = Text(note, font_size=11, color=color)
            note_mob.next_to(row_bg.get_right(), LEFT, buff=0.3)
            note_mob.set_y(row_bg.get_center()[1])
            all_rows.add(VGroup(row_bg, label_mob, desc_mob, note_mob))

        all_rows.arrange(DOWN, buff=0.10)
        all_rows.move_to(DOWN*0.12)

        elapsed = 0.6
        dwells = [8.0, 8.5, 9.0, 7.5, 7.0]
        for row, dwell in zip(all_rows, dwells):
            self.play(FadeIn(row, shift=RIGHT*0.12), run_time=0.38)
            self.wait(dwell)
            elapsed += 0.38 + dwell

        tip = exam_tip(self,
            "DLP prevents data from leaving  |  DRM controls what happens after it leaves")
        elapsed += 0.5
        self.wait(4.0)
        elapsed += 4.0

        self._pad("s7", elapsed)
        self._fade_content(bg)

    # ── SCENE 8 — Scoping & Tailoring ────────────────────────────
    def s8_scoping_tailoring(self):
        bg = self._tech_bg()
        self._sound("s8")

        scene_title(self, "Scoping, Tailoring & Compensating Controls", color=GREEN)

        concepts = [
            ("BASELINE",
             "Minimum set of controls for a given classification level or system type.\nNIST 800-53 organizes baselines by impact: Low, Moderate, High.",
             BLUE),
            ("SCOPING",
             "Remove controls from the baseline that DO NOT apply to this environment.\nCloud-only system → scope out physical media controls.",
             GREEN),
            ("TAILORING",
             "Modify remaining controls to fit the organization's mission,\nenvironment, and risk tolerance. Add parameters or constraints.",
             AMBER),
            ("COMPENSATING\nCONTROLS",
             "Alternative control used when the required control CANNOT be implemented.\nMust provide equivalent protection · Must be documented and approved.",
             RED),
        ]

        all_cards = VGroup()
        for label, desc, color in concepts:
            card_bg = RoundedRectangle(corner_radius=0.15, width=13.0, height=1.0,
                                       color=color, fill_color=BG,
                                       fill_opacity=0.92, stroke_width=2)
            label_mob = Text(label, font_size=14, color=color,
                             weight=BOLD, line_spacing=1.1)
            label_mob.next_to(card_bg.get_left(), RIGHT, buff=0.35)
            label_mob.set_y(card_bg.get_center()[1])
            desc_mob = Text(desc, font_size=12, color=WHITE, line_spacing=1.2)
            desc_mob.move_to(card_bg.get_center() + RIGHT*1.8)
            desc_mob.set_y(card_bg.get_center()[1])
            all_cards.add(VGroup(card_bg, label_mob, desc_mob))

        all_cards.arrange(DOWN, buff=0.14)
        all_cards.move_to(DOWN*0.12)

        elapsed = 0.6
        dwells = [8.0, 8.5, 8.5, 9.0]
        for card, dwell in zip(all_cards, dwells):
            self.play(FadeIn(card, shift=RIGHT*0.15), run_time=0.4)
            self.wait(dwell)
            elapsed += 0.4 + dwell

        tip = exam_tip(self,
            "Compensating control ≠ no control — must provide equivalent protection and be approved")
        elapsed += 0.5
        self.wait(4.0)
        elapsed += 4.0

        self._pad("s8", elapsed)
        self._fade_content(bg)

    # ── SCENE 9 — Practice Questions ─────────────────────────────
    def s9_practice_questions(self):
        bg = self._tech_bg()
        self._sound("s9")

        scene_title(self, "Practice Questions", color=GREEN)

        questions = [
            (
                "Litigation is anticipated involving customer transaction records.\n"
                "The records are scheduled for deletion next week per the retention policy.\n"
                "What must IT do immediately?",
                "A. Delete on schedule — policy takes precedence",
                "B. Issue a legal hold — suspend the scheduled deletion",
                "C. Archive the records and proceed with deletion",
                "B — Legal hold overrides retention policy. Deleting held data is spoliation."
            ),
            (
                "A storage array containing Confidential customer data must be transferred\n"
                "to a third-party vendor. Which sanitization method is appropriate?",
                "A. Clearing — overwrite with non-sensitive data",
                "B. Purging — degaussing or cryptographic erasure",
                "C. No sanitization — vendor is contractually bound",
                "B — Purging. Media leaving the organization requires purging, not clearing."
            ),
            (
                "A control prevents users from forwarding Confidential documents\n"
                "as email attachments, regardless of recipient.\n"
                "What type of control is this?",
                "A. DRM — Digital Rights Management",
                "B. Data Masking",
                "C. DLP — Data Loss Prevention",
                "C — DLP. It prevents data from leaving. DRM would control use after delivery."
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

        self._pad("s9", elapsed)
        self._fade_content(bg)

    # ── SCENE 10 — Recap + CTA ────────────────────────────────────
    def s10_recap_cta(self):
        bg = self._tech_bg()
        self._sound("s10")

        scene_title(self, "Four Flashcards", color=WHITE)

        cards = [
            ("1", "Ownership:",
             "Owner classifies & decides  |  Custodian implements  |  Controller→Processor (GDPR)",
             BLUE),
            ("2", "Classification:",
             "Gov: TS / S / C / U  |  Commercial: Confidential / Private / Sensitive / Public",
             GREEN),
            ("3", "Sanitization:",
             "Clear→internal reuse  |  Purge→leaving org  |  Destroy→highest classification",
             AMBER),
            ("4", "Controls:",
             "DLP prevents exfiltration  |  DRM controls post-delivery  |  EOS = no more patches",
             RED),
        ]

        all_cards = VGroup()
        for num, label, detail, color in cards:
            card_bg = RoundedRectangle(corner_radius=0.18, width=13.0, height=0.86,
                                       color=color, fill_color=BG,
                                       fill_opacity=0.95, stroke_width=2)
            num_mob   = Text(num,    font_size=20, color=color, weight=BOLD)
            num_mob.move_to(card_bg.get_left() + RIGHT*0.5)
            label_mob = Text(label,  font_size=16, color=color, weight=BOLD)
            label_mob.move_to(card_bg.get_left() + RIGHT*2.1)
            detail_mob = Text(detail, font_size=14, color=WHITE)
            detail_mob.move_to(card_bg.get_center() + RIGHT*2.0)
            detail_mob.set_y(card_bg.get_center()[1])
            all_cards.add(VGroup(card_bg, num_mob, label_mob, detail_mob))

        all_cards.arrange(DOWN, buff=0.16)
        all_cards.move_to(DOWN*0.1)

        elapsed = 0.6
        for card in all_cards:
            self.play(FadeIn(card, shift=RIGHT*0.2), run_time=0.45)
            self.wait(4.0)
            elapsed += 4.45

        self.play(*[c.animate.set_opacity(0.4) for c in all_cards], run_time=0.4)

        cta_head = heading("Domain 2 complete. Test yourself now.", size=24, color=WHITE)
        url_bg = RoundedRectangle(corner_radius=0.2, width=5.2, height=0.68,
                                   color=GREEN, fill_color="#051A0A",
                                   fill_opacity=1, stroke_width=2)
        url_txt = Text("www.zerodaylabs.tech", font=MONO, font_size=22, color=GREEN, weight=BOLD)
        url_txt.move_to(url_bg.get_center())
        url_grp = VGroup(url_bg, url_txt)
        next_ep = Text("Next: Domain 3 — Security Architecture, Cryptography & Secure Design",
                       font_size=15, color=AMBER, weight=BOLD)
        cta_group = VGroup(cta_head, url_grp, next_ep).arrange(DOWN, buff=0.22)
        cta_group.to_edge(DOWN, buff=0.38)
        self.play(FadeIn(cta_group), run_time=0.5)
        self.wait(5.0)
        elapsed = 28.0

        self._pad("s10", elapsed)
        self._fade_content(bg)

    # ── SCENE 11 — Book Ad (End) ──────────────────────────────────
    def s11_book_ad(self):
        bg = self._tech_bg()
        self._sound("s11")

        ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
        cover_path = os.path.join(ASSETS, "Think Like A CISSP Cover.jpg")

        if os.path.exists(cover_path):
            cover = ImageMobject(cover_path)
            cover.set_height(5.0).move_to(LEFT*3.0 + DOWN*0.15)
            glow = RoundedRectangle(corner_radius=0.12, width=cover.width+0.12,
                                    height=cover.height+0.12, color=AMBER,
                                    stroke_width=2, fill_opacity=0)
            glow.move_to(cover.get_center())
            self.play(FadeIn(cover, scale=0.92), Create(glow), run_time=0.8)
        else:
            ph = RoundedRectangle(corner_radius=0.2, width=3.0, height=5.0,
                                   color=AMBER, fill_color="#1A0D00",
                                   fill_opacity=0.9, stroke_width=2)
            ph.move_to(LEFT*3.0 + DOWN*0.15)
            self.play(FadeIn(ph), run_time=0.5)

        rx = RIGHT*2.0
        t1 = heading("Think Like", size=40, color=WHITE); t1.move_to(rx + UP*1.6)
        t2 = heading("A CISSP",   size=50, color=AMBER);  t2.next_to(t1, DOWN, buff=0.08).align_to(t1, LEFT)
        self.play(Write(t1), run_time=0.5)
        self.play(Write(t2), run_time=0.5)

        div = Line(ORIGIN, RIGHT*4.5, color=AMBER, stroke_width=1.2)
        div.next_to(t2, DOWN, buff=0.2).align_to(t1, LEFT)
        self.play(Create(div), run_time=0.3)

        tag = Text("The senior security mindset that decides\nborderline CISSP questions.",
                   font_size=16, color=WHITE, line_spacing=1.3)
        tag.next_to(div, DOWN, buff=0.22).align_to(t1, LEFT)
        self.play(FadeIn(tag), run_time=0.4)

        pbg = RoundedRectangle(corner_radius=0.18, width=1.7, height=0.65,
                               fill_color=AMBER, fill_opacity=1, stroke_width=0)
        ptxt = Text("$25.00", font_size=23, color="#0A0E1A", weight=BOLD)
        pbg.next_to(tag, DOWN, buff=0.3).align_to(t1, LEFT)
        ptxt.move_to(pbg.get_center())
        self.play(FadeIn(pbg, scale=0.8), Write(ptxt), run_time=0.5)

        url = mono("zerodaylabs.tech", size=14, color=AMBER)
        url.next_to(pbg, DOWN, buff=0.18).align_to(t1, LEFT)
        self.play(Write(url), run_time=0.4)

        self.wait(2.0)
        self._pad("s11", 7.5)

        black = Rectangle(
            width=config.frame_width + 1, height=config.frame_height + 1,
            fill_color=BLACK, fill_opacity=0, stroke_width=0,
        )
        self.add(black)
        self.play(black.animate.set_fill(opacity=1), run_time=1.8)
        self.wait(0.3)
