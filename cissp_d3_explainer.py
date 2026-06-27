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

AUDIO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cissp_d3_audio")

_DUR_DEFAULTS = {
    "s0":  55.0,
    "s1":  72.0,
    "s2":  75.0,
    "s3":  72.0,
    "s4":  68.0,
    "s5":  72.0,
    "s6":  75.0,
    "s7":  72.0,
    "s8":  72.0,
    "s9":  68.0,
    "s10_q1": 14.0,
    "s10_a1": 16.0,
    "s10_q2": 13.0,
    "s10_a2": 18.0,
    "s10_q3": 18.0,
    "s10_a3": 20.0,
    "s11": 52.0,
    "s12": 22.0,
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
        badge.to_edge(DOWN, buff=0.3)
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
#  CISSP D3  —  manim -qh cissp_d3_explainer.py CISSP_D3
# ═══════════════════════════════════════════════════════════════════
class CISSP_D3(Scene):
    def construct(self):
        _preflight_audio(AUDIO, _DUR_DEFAULTS, "generate_cissp_d3_narration.py")
        self.s0_hook_roadmap()
        self.s1_secure_design()
        self.s2_bell_biba()
        self.s3_models_tcb()
        self.s4_evaluation()
        self.s5_symmetric()
        self.s6_asymmetric()
        self.s7_pki()
        self.s8_cryptanalysis()
        self.s9_physical()
        self.s10_practice_questions()
        self.s11_recap_cta()
        self.s12_book_ad()

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
        self._sound("s0")

        # Three failure bullets
        failures = VGroup(
            Text("✗  Developer returns full stack trace to the browser on every exception.",
                 font_size=17, color=RED),
            Text("✗  Network engineer configures firewall to permit all traffic unless explicitly blocked.",
                 font_size=17, color=AMBER),
            Text("✗  Systems architect places both redundant servers in the same rack.",
                 font_size=17, color=GRAY),
        ).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        failures.move_to(UP*1.2)
        for f in failures:
            self.play(FadeIn(f, shift=RIGHT*0.15), run_time=0.35)
        self.wait(2.0)

        self._fade_content(bg, run_time=0.4)
        bg2 = self._tech_bg()

        series = Text("CISSP Domain Mastery Series", font_size=20, color=GRAY)
        ep_title = heading("Domain 3  |  Security Architecture & Engineering", size=34, color=WHITE)
        ep_title.move_to(UP*1.4)
        series.next_to(ep_title, UP, buff=0.3)
        self.play(FadeIn(series), Write(ep_title), run_time=0.9)

        obj_label = Text("Exam Objectives Covered:", font_size=17, color=AMBER, weight=BOLD)
        obj_label.next_to(ep_title, DOWN, buff=0.4)
        obj_nums = mono("3.1  |  3.2  |  3.3  |  3.4  |  3.5  |  3.6  |  3.7  |  3.8  |  3.9", size=16, color=BLUE)
        obj_nums.next_to(obj_label, DOWN, buff=0.18)
        self.play(FadeIn(obj_label), Write(obj_nums), run_time=0.5)

        topics = [
            "Secure Design Principles — Fail-safe, Least Privilege, Defense in Depth, Zero Trust",
            "Security Models — Bell-LaPadula, Biba, Clark-Wilson, Brewer-Nash",
            "Trusted Computing Base & Reference Monitor",
            "Security Evaluation — Common Criteria EAL1–7, TCSEC Orange Book",
            "Symmetric Cryptography — DES, 3DES, AES, block cipher modes",
            "Asymmetric Cryptography, Hashing — RSA, ECC, SHA, Digital Signatures",
            "PKI, Certificate Authorities, CRL, OCSP, Key Management",
            "Cryptanalytic Attacks — Brute Force, Rainbow Tables, Side-Channel",
            "Physical Security — Site Selection, Mantraps, Clean Agents",
        ]
        topic_group = VGroup(*[
            Text(f"• {t}", font_size=13, color=WHITE) for t in topics
        ]).arrange(DOWN, buff=0.10, aligned_edge=LEFT)
        topic_group.next_to(obj_nums, DOWN, buff=0.22)
        for t in topic_group:
            self.play(FadeIn(t, shift=RIGHT*0.12), run_time=0.15)

        elapsed = 20.0
        self._pad("s0", elapsed)
        self._fade_content(bg2)

    # ── SCENE 1 — Secure Design Principles ───────────────────────
    def s1_secure_design(self):
        bg = self._tech_bg()
        self._sound("s1")

        scene_title(self, "Secure Design Principles", color=BLUE)

        principles = [
            ("FAIL-SAFE DEFAULTS",    "Deny by default. Permissions granted explicitly, not assumed.\nA system that fails open violates this principle.",              RED),
            ("LEAST PRIVILEGE",       "Minimum permissions for the function. Nothing more.\nA web server running as root violates least privilege.",                 BLUE),
            ("SEPARATION OF DUTIES",  "No single person completes a sensitive transaction alone.\nRequires collusion — preventive control against fraud.",             GREEN),
            ("DEFENSE IN DEPTH",      "Multiple independent layers protect the same asset.\nOne layer fails — the next catches it. No single point of failure.",     AMBER),
            ("ZERO TRUST",            "Never trust, always verify. No implicit trust from network location.\nInside traffic receives the same scrutiny as outside.",  "#AA44FF"),
            ("OPEN DESIGN",           "Security does not depend on secrecy of the mechanism — only the key.\nSecurity through obscurity is not a principle.",         GRAY),
        ]

        all_rows = VGroup()
        for label, desc, color in principles:
            row_bg = RoundedRectangle(corner_radius=0.12, width=13.0, height=0.90,
                                      color=color, fill_color=BG,
                                      fill_opacity=0.92, stroke_width=1.8)
            label_mob = Text(label, font_size=13, color=color, weight=BOLD)
            label_mob.next_to(row_bg.get_left(), RIGHT, buff=0.35)
            label_mob.set_y(row_bg.get_center()[1])
            desc_mob = Text(desc, font_size=11, color=WHITE, line_spacing=1.15)
            desc_mob.move_to(row_bg.get_center() + RIGHT*1.5)
            desc_mob.set_y(row_bg.get_center()[1])
            all_rows.add(VGroup(row_bg, label_mob, desc_mob))

        all_rows.arrange(DOWN, buff=0.08)
        all_rows.move_to(DOWN*0.35)

        elapsed = 0.6
        dwells = [8.5, 7.5, 7.0, 7.0, 7.5, 7.0]
        for row, dwell in zip(all_rows, dwells):
            self.play(FadeIn(row, shift=RIGHT*0.15), run_time=0.4)
            self.wait(dwell)
            elapsed += 0.4 + dwell

        tip = exam_tip(self,
            "Fail-safe defaults = deny by default  |  Least privilege ≠ separation of duties — know the difference")
        elapsed += 0.5
        self.wait(4.0)
        elapsed += 4.0

        self._pad("s1", elapsed)
        self._fade_content(bg)

    # ── SCENE 2 — Bell-LaPadula & Biba ───────────────────────────
    def s2_bell_biba(self):
        bg = self._tech_bg()
        self._sound("s2")

        scene_title(self, "Security Models: Confidentiality vs Integrity", color=BLUE)

        # Left panel — Bell-LaPadula
        blp_bg = RoundedRectangle(corner_radius=0.18, width=6.0, height=5.0,
                                   color=BLUE, fill_color="#00101A",
                                   fill_opacity=0.95, stroke_width=2)
        blp_bg.move_to(LEFT*3.3 + DOWN*0.2)
        blp_title = Text("BELL-LaPADULA", font_size=18, color=BLUE, weight=BOLD)
        blp_title.move_to(blp_bg.get_top() + DOWN*0.35)
        blp_div = Line(LEFT*2.6, RIGHT*2.6, color=BLUE, stroke_width=0.7, stroke_opacity=0.5)
        blp_div.next_to(blp_title, DOWN, buff=0.12)
        blp_items = VGroup(
            Text("Goal: Confidentiality — prevent disclosure", font_size=12, color=WHITE),
            Text("Simple Security: No Read Up (NRU)", font_size=12, color=AMBER, weight=BOLD),
            Text("  Subject cannot read above their level", font_size=11, color=WHITE),
            Text("*-Property: No Write Down (NWD)", font_size=12, color=AMBER, weight=BOLD),
            Text("  Subject cannot write below their level", font_size=11, color=WHITE),
            Text("Hook: Reads down ✓  Writes up ✓", font_size=12, color=GREEN),
            Text("Protects: CONFIDENTIALITY", font_size=13, color=BLUE, weight=BOLD),
        ).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        blp_items.next_to(blp_div, DOWN, buff=0.2)

        # Right panel — Biba
        biba_bg = RoundedRectangle(corner_radius=0.18, width=6.0, height=5.0,
                                    color=GREEN, fill_color="#001A05",
                                    fill_opacity=0.95, stroke_width=2)
        biba_bg.move_to(RIGHT*3.3 + DOWN*0.2)
        biba_title = Text("BIBA", font_size=18, color=GREEN, weight=BOLD)
        biba_title.move_to(biba_bg.get_top() + DOWN*0.35)
        biba_div = Line(LEFT*2.6, RIGHT*2.6, color=GREEN, stroke_width=0.7, stroke_opacity=0.5)
        biba_div.next_to(biba_title, DOWN, buff=0.12)
        biba_items = VGroup(
            Text("Goal: Integrity — prevent corruption", font_size=12, color=WHITE),
            Text("Simple Integrity: No Read Down (NRD)", font_size=12, color=AMBER, weight=BOLD),
            Text("  Subject cannot read below their level", font_size=11, color=WHITE),
            Text("*-Integrity: No Write Up (NWU)", font_size=12, color=AMBER, weight=BOLD),
            Text("  Subject cannot write above their level", font_size=11, color=WHITE),
            Text("Hook: Reads up ✓  Writes down ✓", font_size=12, color=BLUE),
            Text("Protects: INTEGRITY", font_size=13, color=GREEN, weight=BOLD),
        ).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        biba_items.next_to(biba_div, DOWN, buff=0.2)

        blp_group  = VGroup(blp_bg, blp_title, blp_div, blp_items)
        biba_group = VGroup(biba_bg, biba_title, biba_div, biba_items)

        self.play(FadeIn(blp_group), FadeIn(biba_group), run_time=1.0)
        self.wait(20.0)

        tip = exam_tip(self,
            "Confidentiality concern → Bell-LaPadula  |  Integrity concern → Biba  |  They are inverses of each other")
        elapsed = 0.6 + 1.0 + 20.0 + 0.5 + 6.0
        self.wait(6.0)

        self._pad("s2", elapsed)
        self._fade_content(bg)

    # ── SCENE 3 — Clark-Wilson, Brewer-Nash & TCB ─────────────────
    def s3_models_tcb(self):
        bg = self._tech_bg()
        self._sound("s3")

        scene_title(self, "Clark-Wilson, Brewer-Nash & the TCB", color=GREEN)

        # Clark-Wilson panel
        cw_bg = RoundedRectangle(corner_radius=0.15, width=5.8, height=2.5,
                                  color=BLUE, fill_color="#00061A",
                                  fill_opacity=0.95, stroke_width=2)
        cw_bg.move_to(LEFT*3.1 + DOWN*0.1)
        cw_items = VGroup(
            Text("CLARK-WILSON — Integrity", font_size=13, color=BLUE, weight=BOLD),
            Text("Commercial integrity model — well-formed transactions", font_size=11, color=WHITE),
            Text("CDI: Constrained Data Items (must stay accurate)", font_size=11, color=AMBER),
            Text("TP: Transformation Procedures (only way to modify CDIs)", font_size=11, color=AMBER),
            Text("Users → TP → CDI  |  Enforces SoD + audit trail", font_size=11, color=WHITE),
            Text("Model behind double-entry bookkeeping", font_size=11, color=GRAY),
        ).arrange(DOWN, buff=0.13, aligned_edge=LEFT)
        cw_items.move_to(cw_bg.get_center())

        # Brewer-Nash panel
        bn_bg = RoundedRectangle(corner_radius=0.15, width=5.8, height=2.5,
                                  color=AMBER, fill_color="#1A0D00",
                                  fill_opacity=0.95, stroke_width=2)
        bn_bg.move_to(RIGHT*3.1 + DOWN*0.1)
        bn_items = VGroup(
            Text("BREWER-NASH (Chinese Wall)", font_size=13, color=AMBER, weight=BOLD),
            Text("Prevents conflicts of interest", font_size=11, color=WHITE),
            Text("After accessing Company A data, cannot access rival data", font_size=11, color=WHITE),
            Text("Wall grows dynamically as subject accesses information", font_size=11, color=WHITE),
            Text("Used in investment banking and legal environments", font_size=11, color=GRAY),
        ).arrange(DOWN, buff=0.16, aligned_edge=LEFT)
        bn_items.move_to(bn_bg.get_center())

        cw_group = VGroup(cw_bg, cw_items)
        bn_group = VGroup(bn_bg, bn_items)

        # Position top panels
        top_panels = VGroup(cw_group, bn_group).arrange(RIGHT, buff=0.4)
        top_panels.move_to(UP*1.15)

        # TCB + Reference Monitor panel
        tcb_bg = RoundedRectangle(corner_radius=0.15, width=13.0, height=2.1,
                                   color=RED, fill_color="#1A0000",
                                   fill_opacity=0.95, stroke_width=2)
        tcb_bg.move_to(DOWN*2.45)
        tcb_items = VGroup(
            Text("TRUSTED COMPUTING BASE (TCB): All hardware, firmware & software that enforce security policy. Everything outside = untrusted.",
                 font_size=11, color=WHITE, line_spacing=1.15),
            Text("REFERENCE MONITOR: Abstract mediator — checks every subject↔object access. Must be: always invoked | tamper-proof | verifiable",
                 font_size=11, color=AMBER, line_spacing=1.15),
            Text("SECURITY KERNEL: The concrete hardware/software implementation of the reference monitor",
                 font_size=11, color=RED, weight=BOLD),
        ).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        tcb_items.move_to(tcb_bg.get_center())
        tcb_group = VGroup(tcb_bg, tcb_items)

        self.play(FadeIn(cw_group), FadeIn(bn_group), run_time=1.0)
        self.wait(12.0)
        self.play(FadeIn(tcb_group), run_time=0.6)
        self.wait(8.0)

        elapsed = 0.6 + 1.0 + 12.0 + 0.6 + 8.0
        self._pad("s3", elapsed)
        self._fade_content(bg)

    # ── SCENE 4 — Security Evaluation Criteria ────────────────────
    def s4_evaluation(self):
        bg = self._tech_bg()
        self._sound("s4")

        scene_title(self, "Security Evaluation Criteria", color=AMBER)

        eals = [
            ("EAL 1", "Functionally Tested",                         GRAY),
            ("EAL 2", "Structurally Tested",                         GRAY),
            ("EAL 3", "Methodically Tested & Checked",               BLUE),
            ("EAL 4", "Methodically Designed, Tested & Reviewed",    GREEN),
            ("EAL 5", "Semiformally Designed & Tested",              AMBER),
            ("EAL 6", "Semiformally Verified Design & Tested",       AMBER),
            ("EAL 7", "Formally Verified Design & Tested",           RED),
        ]

        # Common Criteria column
        cc_bg = RoundedRectangle(corner_radius=0.15, width=7.5, height=5.2,
                                  color=BLUE, fill_color="#00061A",
                                  fill_opacity=0.95, stroke_width=2)
        cc_bg.move_to(LEFT*2.6 + DOWN*0.25)
        cc_title = Text("COMMON CRITERIA (ISO/IEC 15408)", font_size=14, color=BLUE, weight=BOLD)
        cc_title.move_to(cc_bg.get_top() + DOWN*0.35)
        cc_div = Line(LEFT*3.3, RIGHT*3.3, color=BLUE, stroke_width=0.7, stroke_opacity=0.5)
        cc_div.next_to(cc_title, DOWN, buff=0.12)

        eal_rows = VGroup()
        for eal_label, eal_desc, color in eals:
            row = VGroup(
                Text(eal_label, font_size=12, color=color, weight=BOLD),
                Text(eal_desc,  font_size=11, color=WHITE),
            ).arrange(RIGHT, buff=0.28)
            eal_rows.add(row)

        # Annotations
        eal4_note = Text("← Commercial max", font_size=10, color=GREEN)
        eal7_note = Text("← Military/Gov",   font_size=10, color=RED)

        eal_rows.arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        eal_rows.next_to(cc_div, DOWN, buff=0.18)
        eal4_note.next_to(eal_rows[3], RIGHT, buff=0.18)
        eal7_note.next_to(eal_rows[6], RIGHT, buff=0.18)

        cc_group = VGroup(cc_bg, cc_title, cc_div, eal_rows, eal4_note, eal7_note)

        # TCSEC column
        tcsec_bg = RoundedRectangle(corner_radius=0.15, width=5.0, height=5.2,
                                     color=AMBER, fill_color="#1A0D00",
                                     fill_opacity=0.95, stroke_width=2)
        tcsec_bg.move_to(RIGHT*4.2 + DOWN*0.25)
        tcsec_title = Text("TCSEC (Orange Book)", font_size=14, color=AMBER, weight=BOLD)
        tcsec_title.move_to(tcsec_bg.get_top() + DOWN*0.35)
        tcsec_div = Line(LEFT*2.2, RIGHT*2.2, color=AMBER, stroke_width=0.7, stroke_opacity=0.5)
        tcsec_div.next_to(tcsec_title, DOWN, buff=0.12)

        tcsec_entries = [
            ("D",  "Minimal Protection",      GRAY),
            ("C1", "Discretionary (basic)",   GRAY),
            ("C2", "Controlled Access",        BLUE),
            ("B1", "Labeled Security (MAC)",   GREEN),
            ("B2", "Structured Protection",    AMBER),
            ("B3", "Security Domains",         AMBER),
            ("A1", "Verified Design",          RED),
        ]
        tcsec_rows = VGroup()
        for div_label, div_desc, color in tcsec_entries:
            row = VGroup(
                Text(div_label, font_size=12, color=color, weight=BOLD),
                Text(div_desc,  font_size=11, color=WHITE),
            ).arrange(RIGHT, buff=0.22)
            tcsec_rows.add(row)
        tcsec_rows.arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        tcsec_rows.next_to(tcsec_div, DOWN, buff=0.18)

        c2_note = Text("← Commercial target", font_size=10, color=BLUE)
        c2_note.next_to(tcsec_rows[2], RIGHT, buff=0.12)

        tcsec_group = VGroup(tcsec_bg, tcsec_title, tcsec_div, tcsec_rows, c2_note)

        self.play(FadeIn(cc_group), FadeIn(tcsec_group), run_time=1.0)
        self.wait(18.0)

        tip = exam_tip(self,
            "EAL4 = highest commercial level  |  EAL7 = formally verified  |  Protection Profile defines class requirements")
        elapsed = 0.6 + 1.0 + 18.0 + 0.5 + 4.0
        self.wait(4.0)

        self._pad("s4", elapsed)
        self._fade_content(bg)

    # ── SCENE 5 — Symmetric Cryptography ─────────────────────────
    def s5_symmetric(self):
        bg = self._tech_bg()
        self._sound("s5")

        scene_title(self, "Symmetric Cryptography", color=BLUE)

        algos = [
            ("DES",     "56-bit",        "BROKEN — Do not use",     RED),
            ("3DES",    "112 / 168-bit", "Deprecated — legacy use",  AMBER),
            ("AES-128", "128-bit",       "Current standard",         GREEN),
            ("AES-256", "256-bit",       "Highest assurance",        GREEN),
        ]

        algo_rows = VGroup()
        for name, keysize, status, color in algos:
            row_bg = RoundedRectangle(corner_radius=0.10, width=13.0, height=0.65,
                                      color=color, fill_color=BG,
                                      fill_opacity=0.92, stroke_width=1.5)
            name_mob   = Text(name,    font_size=14, color=color, weight=BOLD)
            name_mob.next_to(row_bg.get_left(), RIGHT, buff=0.35)
            name_mob.set_y(row_bg.get_center()[1])
            key_mob    = Text(keysize,  font_size=13, color=WHITE)
            key_mob.move_to(row_bg.get_center() + LEFT*1.5)
            key_mob.set_y(row_bg.get_center()[1])
            status_mob = Text(status,  font_size=13, color=color)
            status_mob.next_to(row_bg.get_right(), LEFT, buff=0.35)
            status_mob.set_y(row_bg.get_center()[1])
            algo_rows.add(VGroup(row_bg, name_mob, key_mob, status_mob))

        algo_rows.arrange(DOWN, buff=0.08)
        algo_rows.move_to(UP*1.5)

        elapsed = 0.6
        for row in algo_rows:
            self.play(FadeIn(row, shift=RIGHT*0.15), run_time=0.4)
            self.wait(2.5)
            elapsed += 0.4 + 2.5

        # Key distribution note
        kdist_bg = RoundedRectangle(corner_radius=0.12, width=13.0, height=0.62,
                                     color=AMBER, fill_color="#1A0D00",
                                     fill_opacity=0.95, stroke_width=1.5)
        kdist_bg.next_to(algo_rows, DOWN, buff=0.22)
        kdist_txt = Text(
            "Keys required for n parties: n(n−1)/2   |   10 parties = 45 keys   |   100 parties = 4,950 keys",
            font_size=13, color=WHITE, weight=BOLD
        )
        kdist_txt.move_to(kdist_bg.get_center())
        self.play(FadeIn(kdist_bg), Write(kdist_txt), run_time=0.4)
        self.wait(3.0)
        elapsed += 0.4 + 3.0

        # Cipher modes
        modes = [
            ("ECB", "Identical blocks → identical ciphertext.\nINSECURE — reveals patterns.", RED),
            ("CBC", "Blocks chained. Each depends on previous.\nSecure for most uses.", GREEN),
            ("CTR", "Turns block cipher into stream cipher.\nParallelizable.", BLUE),
            ("GCM", "Authenticated encryption.\nConfidentiality + Integrity in one pass.", AMBER),
        ]
        mode_cards = VGroup()
        for mode_name, mode_desc, color in modes:
            card_bg = RoundedRectangle(corner_radius=0.12, width=3.0, height=1.5,
                                       color=color, fill_color=BG,
                                       fill_opacity=0.92, stroke_width=1.5)
            m_label = Text(mode_name, font_size=14, color=color, weight=BOLD)
            m_label.move_to(card_bg.get_top() + DOWN*0.28)
            m_desc  = Text(mode_desc, font_size=10, color=WHITE, line_spacing=1.2)
            m_desc.move_to(card_bg.get_center() + DOWN*0.1)
            mode_cards.add(VGroup(card_bg, m_label, m_desc))

        mode_cards.arrange(RIGHT, buff=0.22)
        mode_cards.next_to(kdist_bg, DOWN, buff=0.22)
        self.play(FadeIn(mode_cards, lag_ratio=0.15), run_time=1.0)
        self.wait(12.0)
        elapsed += 1.0 + 12.0

        self._pad("s5", elapsed)
        self._fade_content(bg)

    # ── SCENE 6 — Asymmetric Cryptography & Hashing ───────────────
    def s6_asymmetric(self):
        bg = self._tech_bg()
        self._sound("s6")

        scene_title(self, "Asymmetric Cryptography & Hashing", color=GREEN)

        # Left panel — Asymmetric
        asym_bg = RoundedRectangle(corner_radius=0.18, width=6.2, height=5.2,
                                    color=BLUE, fill_color="#00061A",
                                    fill_opacity=0.95, stroke_width=2)
        asym_bg.move_to(LEFT*3.3 + DOWN*0.2)
        asym_items = VGroup(
            Text("ASYMMETRIC ENCRYPTION", font_size=13, color=BLUE, weight=BOLD),
            Text("Public key: freely distributed", font_size=11, color=WHITE),
            Text("Private key: never shared", font_size=11, color=WHITE),
            Text("Encrypt with recipient's public key → only they decrypt", font_size=11, color=WHITE),
            Text("─" * 32, font_size=8, color=BLUE),
            Text("RSA — factor large integers", font_size=11, color=AMBER),
            Text("ECC — shorter keys, same strength", font_size=11, color=AMBER),
            Text("  256-bit ECC ≈ 3072-bit RSA", font_size=11, color=WHITE),
            Text("Diffie-Hellman — key AGREEMENT", font_size=11, color=GREEN),
            Text("  (not encryption)", font_size=11, color=GRAY),
            Text("SLOW — use for key exchange only", font_size=11, color=RED, weight=BOLD),
            Text("Hybrid: asymmetric exchanges key,", font_size=11, color=WHITE),
            Text("  symmetric encrypts the data (TLS)", font_size=11, color=WHITE),
        ).arrange(DOWN, buff=0.14, aligned_edge=LEFT)
        asym_items.move_to(asym_bg.get_center())

        # Right panel — Hashing
        hash_bg = RoundedRectangle(corner_radius=0.18, width=6.2, height=5.2,
                                    color=GREEN, fill_color="#001A05",
                                    fill_opacity=0.95, stroke_width=2)
        hash_bg.move_to(RIGHT*3.3 + DOWN*0.2)
        hash_items = VGroup(
            Text("HASH FUNCTIONS", font_size=13, color=GREEN, weight=BOLD),
            Text("Fixed-length digest from any input", font_size=11, color=WHITE),
            Text("One-way: cannot reverse", font_size=11, color=WHITE),
            Text("Deterministic: same input → same output", font_size=11, color=WHITE),
            Text("Avalanche: 1 bit change → ~50% output change", font_size=11, color=WHITE),
            Text("─" * 32, font_size=8, color=GREEN),
            Text("MD5 — 128-bit — BROKEN", font_size=11, color=RED),
            Text("SHA-1 — 160-bit — DEPRECATED", font_size=11, color=AMBER),
            Text("SHA-256 — Current standard", font_size=11, color=GREEN),
            Text("SHA-3 — Alternative standard", font_size=11, color=GREEN),
            Text("─" * 32, font_size=8, color=GREEN),
            Text("Provides: INTEGRITY only", font_size=11, color=AMBER, weight=BOLD),
            Text("NOT confidentiality, NOT authentication", font_size=11, color=RED),
        ).arrange(DOWN, buff=0.14, aligned_edge=LEFT)
        hash_items.move_to(hash_bg.get_center())

        asym_group = VGroup(asym_bg, asym_items)
        hash_group = VGroup(hash_bg, hash_items)

        self.play(FadeIn(asym_group), FadeIn(hash_group), run_time=1.0)
        self.wait(20.0)

        tip = exam_tip(self,
            "Hashing = integrity only  |  Digital signatures = authentication + integrity + non-repudiation")
        elapsed = 0.6 + 1.0 + 20.0 + 0.5 + 5.0
        self.wait(5.0)

        self._pad("s6", elapsed)
        self._fade_content(bg)

    # ── SCENE 7 — PKI & Key Management ───────────────────────────
    def s7_pki(self):
        bg = self._tech_bg()
        self._sound("s7")

        scene_title(self, "PKI & Key Management", color=AMBER)

        # PKI component cards
        pki_components = [
            ("CA",   "Certificate\nAuthority",        "Issues & signs\ncertificates.\nThe trusted root.",           BLUE),
            ("RA",   "Registration\nAuthority",        "Verifies identity\nbefore CA issues.\nCA signs, RA verifies.", GREEN),
            ("CRL",  "Certificate\nRevocation List",   "List of revoked certs\nbefore expiry.\nDownloaded by clients.", AMBER),
            ("OCSP", "Online Certificate\nStatus Protocol", "Real-time cert status.\nNo full CRL download\nneeded.", RED),
        ]

        pki_cards = VGroup()
        for abbr, full_name, desc, color in pki_components:
            card_bg = RoundedRectangle(corner_radius=0.15, width=3.0, height=2.2,
                                       color=color, fill_color=BG,
                                       fill_opacity=0.92, stroke_width=2)
            abbr_mob = Text(abbr,      font_size=20, color=color, weight=BOLD)
            abbr_mob.move_to(card_bg.get_top() + DOWN*0.32)
            name_mob = Text(full_name, font_size=10, color=WHITE, line_spacing=1.1)
            name_mob.next_to(abbr_mob, DOWN, buff=0.08)
            desc_mob = Text(desc,      font_size=10, color=GRAY, line_spacing=1.1)
            desc_mob.next_to(name_mob, DOWN, buff=0.1)
            pki_cards.add(VGroup(card_bg, abbr_mob, name_mob, desc_mob))

        pki_cards.arrange(RIGHT, buff=0.3)
        pki_cards.move_to(UP*1.4)

        # Digital Signature panel
        sig_bg = RoundedRectangle(corner_radius=0.12, width=13.0, height=1.5,
                                   color=BLUE, fill_color="#00101A",
                                   fill_opacity=0.95, stroke_width=1.8)
        sig_bg.move_to(UP*0.0)
        sig_items = VGroup(
            Text("DIGITAL SIGNATURES: Sign (hash → encrypt with PRIVATE key)  |  Verify (decrypt with PUBLIC key → recompute hash)",
                 font_size=12, color=WHITE, weight=BOLD),
            Text("Provides: Authentication ✓   Integrity ✓   Non-repudiation ✓   Confidentiality ✗",
                 font_size=12, color=AMBER),
        ).arrange(DOWN, buff=0.2)
        sig_items.move_to(sig_bg.get_center())
        sig_group = VGroup(sig_bg, sig_items)
        sig_group.next_to(pki_cards, DOWN, buff=0.28)

        # Key management lifecycle
        km_stages = ["Generate", "Distribute", "Store", "Rotate", "Revoke", "Destroy"]
        km_cards = VGroup()
        for stage in km_stages:
            s_bg = RoundedRectangle(corner_radius=0.10, width=1.8, height=0.52,
                                    color=GREEN, fill_color=BG,
                                    fill_opacity=0.90, stroke_width=1.2)
            s_txt = Text(stage, font_size=12, color=GREEN, weight=BOLD)
            s_txt.move_to(s_bg.get_center())
            km_cards.add(VGroup(s_bg, s_txt))

        km_cards.arrange(RIGHT, buff=0.12)
        escrow_note = Text("Key Escrow: Third-party copy for authorized recovery", font_size=11, color=GRAY)
        km_group = VGroup(km_cards, escrow_note).arrange(DOWN, buff=0.15)
        km_group.next_to(sig_group, DOWN, buff=0.3)

        self.play(FadeIn(pki_cards, lag_ratio=0.15, scale=0.93), run_time=1.0)
        self.wait(8.0)
        self.play(FadeIn(sig_group), run_time=0.5)
        self.wait(8.0)
        self.play(FadeIn(km_group), run_time=0.5)
        self.wait(5.0)

        tip = exam_tip(self,
            "Digital signatures do NOT provide confidentiality — they prove who sent it and that it wasn't altered")
        elapsed = 0.6 + 1.0 + 8.0 + 0.5 + 8.0 + 0.5 + 5.0 + 0.5 + 4.0
        self.wait(4.0)

        self._pad("s7", elapsed)
        self._fade_content(bg)

    # ── SCENE 8 — Cryptanalytic Attacks ──────────────────────────
    def s8_cryptanalysis(self):
        bg = self._tech_bg()
        self._sound("s8")

        scene_title(self, "Cryptanalytic Attacks", color=RED)

        attacks = [
            ("BRUTE FORCE",      "Try every possible key systematically. Key length = primary defense.\n256-bit key: 2²⁵⁶ possibilities — computationally infeasible.",                RED),
            ("KNOWN-PLAINTEXT",  "Attacker has plaintext+ciphertext pairs. Analyzes pairs to deduce the key.\nHistorically broke Enigma.",                                                       AMBER),
            ("CHOSEN-PLAINTEXT", "Attacker selects specific plaintexts and observes ciphertext output.\nMore powerful — attacker controls the input.",                                           AMBER),
            ("BIRTHDAY ATTACK",  "Finds two inputs with the same hash (collision). For n-bit hash: ~2^(n/2) operations.\nBreaks SHA-1 — reason it is deprecated.",                             BLUE),
            ("RAINBOW TABLE",    "Precomputed hash chains for fast password recovery. Defeated by SALTING.\nUnsalted MD5/SHA-1 databases are trivially cracked.",                               GREEN),
            ("SIDE-CHANNEL",     "Exploits physical implementation: timing, power analysis, electromagnetic emissions.\nAlgorithm is correct — the hardware leaks information.",                GRAY),
        ]

        all_rows = VGroup()
        for label, desc, color in attacks:
            row_bg = RoundedRectangle(corner_radius=0.12, width=13.0, height=0.9,
                                      color=color, fill_color=BG,
                                      fill_opacity=0.92, stroke_width=1.8)
            label_mob = Text(label, font_size=13, color=color, weight=BOLD)
            label_mob.next_to(row_bg.get_left(), RIGHT, buff=0.35)
            label_mob.set_y(row_bg.get_center()[1])
            desc_mob = Text(desc, font_size=11, color=WHITE, line_spacing=1.2)
            desc_mob.move_to(row_bg.get_center() + RIGHT*1.5)
            desc_mob.set_y(row_bg.get_center()[1])
            all_rows.add(VGroup(row_bg, label_mob, desc_mob))

        all_rows.arrange(DOWN, buff=0.08)
        all_rows.move_to(DOWN*0.3)

        elapsed = 0.6
        dwells = [7.0, 6.5, 6.5, 7.0, 7.5, 7.0]
        for row, dwell in zip(all_rows, dwells):
            self.play(FadeIn(row, shift=RIGHT*0.15), run_time=0.4)
            self.wait(dwell)
            elapsed += 0.4 + dwell

        tip = exam_tip(self,
            "Rainbow tables → defeated by salting  |  Side-channel ≠ cryptographic attack — targets implementation")
        elapsed += 0.5
        self.wait(4.0)
        elapsed += 4.0

        self._pad("s8", elapsed)
        self._fade_content(bg)

    # ── SCENE 9 — Physical Security ───────────────────────────────
    def s9_physical(self):
        bg = self._tech_bg()
        self._sound("s9")

        scene_title(self, "Physical Security", color=AMBER)

        # Site Selection panel
        site_bg = RoundedRectangle(corner_radius=0.15, width=4.0, height=4.2,
                                    color=BLUE, fill_color="#00061A",
                                    fill_opacity=0.95, stroke_width=2)
        site_items = VGroup(
            Text("SITE SELECTION", font_size=13, color=BLUE, weight=BOLD),
            Text("Crime rate & local hazards", font_size=11, color=WHITE),
            Text("Proximity to emergency services", font_size=11, color=WHITE),
            Text("Natural disaster risk (flood, quake)", font_size=11, color=WHITE),
            Text("Utility reliability (power, water)", font_size=11, color=WHITE),
            Text("Avoid: flight paths, flood zones", font_size=11, color=RED),
            Text("Transportation access", font_size=11, color=WHITE),
        ).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        site_items.move_to(site_bg.get_center())
        site_group = VGroup(site_bg, site_items)

        # Perimeter & Entry panel
        peri_bg = RoundedRectangle(corner_radius=0.15, width=4.5, height=4.2,
                                    color=GREEN, fill_color="#001A05",
                                    fill_opacity=0.95, stroke_width=2)
        peri_items = VGroup(
            Text("PERIMETER & ENTRY", font_size=13, color=GREEN, weight=BOLD),
            Text("Fencing — defines boundary", font_size=11, color=WHITE),
            Text("Bollards — vehicle attack prevention", font_size=11, color=WHITE),
            Text("Lighting — reduces concealment", font_size=11, color=WHITE),
            Text("CCTV — deters and records", font_size=11, color=WHITE),
            Text("─" * 24, font_size=8, color=GREEN),
            Text("MANTRAP (Access Control Vestibule)", font_size=11, color=GREEN, weight=BOLD),
            Text("Two-door: 1st closes before 2nd opens", font_size=11, color=WHITE),
            Text("One person at a time", font_size=11, color=WHITE),
            Text("Prevents tailgating", font_size=11, color=AMBER),
        ).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        peri_items.move_to(peri_bg.get_center())
        peri_group = VGroup(peri_bg, peri_items)

        # Data Center panel
        dc_bg = RoundedRectangle(corner_radius=0.15, width=4.0, height=4.2,
                                  color=RED, fill_color="#1A0000",
                                  fill_opacity=0.95, stroke_width=2)
        dc_items = VGroup(
            Text("DATA CENTER", font_size=13, color=RED, weight=BOLD),
            Text("Raised floors — water, cables", font_size=11, color=WHITE),
            Text("HVAC — temp & humidity control", font_size=11, color=WHITE),
            Text("─" * 24, font_size=8, color=RED),
            Text("FIRE SUPPRESSION", font_size=11, color=RED, weight=BOLD),
            Text("Halon — phased out (ozone)", font_size=11, color=GRAY),
            Text("FM-200 — clean agent ✓", font_size=11, color=GREEN),
            Text("CO₂ — clean agent ✓", font_size=11, color=GREEN),
            Text("Inert gas — clean agent ✓", font_size=11, color=GREEN),
            Text("No water sprinklers", font_size=11, color=AMBER),
            Text("Access logs reviewed regularly", font_size=11, color=WHITE),
        ).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        dc_items.move_to(dc_bg.get_center())
        dc_group = VGroup(dc_bg, dc_items)

        panels = VGroup(site_group, peri_group, dc_group).arrange(RIGHT, buff=0.3)
        panels.move_to(DOWN*0.2)

        self.play(FadeIn(site_group), FadeIn(peri_group), FadeIn(dc_group), run_time=1.0)
        self.wait(18.0)

        tip = exam_tip(self,
            "Mantrap = access control vestibule = prevents tailgating  |  Clean agents = no residue damage")
        elapsed = 0.6 + 1.0 + 18.0 + 0.5 + 5.0
        self.wait(5.0)

        self._pad("s9", elapsed)
        self._fade_content(bg)

    # ── SCENE 10 — Practice Questions ────────────────────────────
    def s10_practice_questions(self):
        bg = self._tech_bg()

        scene_title(self, "Practice Questions", color=GREEN)

        questions = [
            (
                "A military information system enforces: users may read at or below their clearance,\n"
                "but may only write at or above their clearance level.\n"
                "Which security model is implemented?",
                "A. Biba",
                "B. Clark-Wilson",
                "C. Bell-LaPadula",
                "C — Bell-LaPadula. No read up (simple security). No write down (star property). Biba is the inverse."
            ),
            (
                "A TLS handshake uses RSA to exchange a session key,\n"
                "then switches to AES for the bulk data transfer.\n"
                "What cryptographic approach does this represent?",
                "A. Perfect Forward Secrecy",
                "B. Hybrid Encryption",
                "C. Key Escrow",
                "B — Hybrid Encryption. Asymmetric (RSA) exchanges the key. Symmetric (AES) encrypts the data."
            ),
            (
                "A legacy database stores passwords as unsalted MD5 hashes.\n"
                "An attacker uses a precomputed table to recover most passwords rapidly.\n"
                "What attack is being used?",
                "A. Brute Force",
                "B. Birthday Attack",
                "C. Rainbow Table Attack",
                "C — Rainbow Table Attack. Precomputed hash chains. Defeated by salting each password before hashing."
            ),
        ]

        # Each stem/answer pair has its own audio clip. We start the clip, then
        # hold for its MEASURED duration (from durations.json) — so the answer
        # reveal always lands with the narration, independent of TTS voice/rate.
        for i, (stem, a, b, c, answer) in enumerate(questions, start=1):
            qkey, akey = f"s10_q{i}", f"s10_a{i}"

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

            # Stem: start audio, reveal the question, hold for the rest of the clip.
            self._sound(qkey)
            self.play(FadeIn(q_bg), Write(q_txt), run_time=0.6)
            self.play(FadeIn(choices), run_time=0.4)
            self.wait(max(0.5, DUR.get(qkey, 12.0) - 1.0))

            ans_bg = RoundedRectangle(corner_radius=0.14, width=12.5, height=0.72,
                                       color=GREEN, fill_color="#051A0A",
                                       fill_opacity=1, stroke_width=1.5)
            ans_bg.to_edge(DOWN, buff=0.35)
            ans_txt = Text(answer, font_size=14, color=WHITE, weight=BOLD)
            ans_txt.move_to(ans_bg.get_center())

            # Answer: start audio as the answer appears, hold for the rest of the clip.
            self._sound(akey)
            self.play(FadeIn(ans_bg), Write(ans_txt), run_time=0.5)
            self.wait(max(0.5, DUR.get(akey, 14.0) - 0.5))

            self.play(FadeOut(q_bg), FadeOut(q_txt), FadeOut(choices),
                      FadeOut(ans_bg), FadeOut(ans_txt), run_time=0.4)

        self._fade_content(bg)

    # ── SCENE 11 — Recap + CTA ────────────────────────────────────
    def s11_recap_cta(self):
        bg = self._tech_bg()
        self._sound("s11")

        scene_title(self, "Four Flashcards", color=WHITE)

        cards = [
            ("1", "Models:",
             "Bell-LaPadula: no read↑, no write↓ (confidentiality)  |  Biba: no read↓, no write↑ (integrity)",
             BLUE),
            ("2", "Crypto:",
             "Hybrid = asymmetric key exchange + symmetric data  |  TLS does this",
             GREEN),
            ("3", "Common Criteria:",
             "EAL4 = commercial max  |  EAL7 = formally verified  |  Protection Profile + Security Target",
             AMBER),
            ("4", "Digital Signatures:",
             "Authentication + Integrity + Non-repudiation  |  Sign: private key  |  Verify: public key",
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

        cta_head = heading("Domain 3 complete. Test yourself now.", size=24, color=WHITE)
        url_bg = RoundedRectangle(corner_radius=0.2, width=5.2, height=0.68,
                                   color=GREEN, fill_color="#051A0A",
                                   fill_opacity=1, stroke_width=2)
        url_txt = Text("www.zerodaylabs.tech", font=MONO, font_size=22, color=GREEN, weight=BOLD)
        url_txt.move_to(url_bg.get_center())
        url_grp = VGroup(url_bg, url_txt)
        next_ep = Text("Next: Domain 4 — Communication and Network Security",
                       font_size=15, color=AMBER, weight=BOLD)
        cta_group = VGroup(cta_head, url_grp, next_ep).arrange(DOWN, buff=0.22)
        cta_group.to_edge(DOWN, buff=0.38)
        self.play(FadeIn(cta_group), run_time=0.5)
        self.wait(5.0)
        elapsed = 0.6 + 4*(0.45+4.0) + 0.4 + 0.5 + 5.0

        self._pad("s11", elapsed)
        self._fade_content(bg)

    # ── SCENE 12 — Book Ad (End) ──────────────────────────────────
    def s12_book_ad(self):
        bg = self._tech_bg()
        self._sound("s12")

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
        self._pad("s12", 7.5)

        black = Rectangle(
            width=config.frame_width + 1, height=config.frame_height + 1,
            fill_color=BLACK, fill_opacity=0, stroke_width=0,
        )
        self.add(black)
        self.play(black.animate.set_fill(opacity=1), run_time=1.8)
        self.wait(0.3)
