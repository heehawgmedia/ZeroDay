from manim import *
import json
import os
import random

# ─── Color Palette ───────────────────────────────────────────────
BG     = "#0A0E1A"
BLUE   = "#00C8FF"
AMBER  = "#F5A623"
GREEN  = "#39D353"
RED    = "#FF4D4D"
PURPLE = "#AA44FF"
MONO   = "DejaVu Sans Mono"

config.background_color = BG

AUDIO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "zt_audio")

_DUR_DEFAULTS = {
    "s0": 22.0,
    "s1": 28.0,
    "s2": 62.0,
    "s3": 88.0,
    "s4": 88.0,
    "s5": 55.0,
    "s6": 58.0,
    "s7": 30.0,
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
    t = heading(text, size=32, color=color)
    t.to_edge(UP, buff=0.45)
    bar = Line(LEFT*6.5, RIGHT*6.5, color=color, stroke_width=1.5)
    bar.next_to(t, DOWN, buff=0.12)
    scene.play(Write(t), Create(bar), run_time=0.7)
    return VGroup(t, bar)


# ═══════════════════════════════════════════════════════════════════
#  ZERO TRUST SCENE  —  manim -qh zero_trust_explainer.py ZeroTrustScene
# ═══════════════════════════════════════════════════════════════════
class ZeroTrustScene(Scene):
    _AUDIO_KEYS = ["s0", "s1", "s2", "s3", "s4", "s5", "s6", "s7"]

    def setup(self):
        missing = [k for k in self._AUDIO_KEYS
                   if not os.path.isfile(os.path.join(AUDIO, f"{k}.mp3"))]
        if missing:
            raise FileNotFoundError(
                f"Missing audio files: {', '.join(missing)}\n"
                f"Run: python generate_zero_trust_narration.py"
            )

    def construct(self):
        self.s0_ad()
        self.s1_hook()
        self.s2_old_model()
        self.s3_what_is_zt()
        self.s4_how_it_works()
        self.s5_why_everyone()
        self.s6_exam_recap()
        self.s7_end_card()

    # ── Background helper ─────────────────────────────────────────
    def _tech_bg(self) -> VGroup:
        """Hex dot grid + corner brackets. Call first in each scene."""
        rng = random.Random(73)
        dots = VGroup(*[
            Dot(
                [
                    -8.8 + c * 0.95 + (0.47 if r % 2 else 0),
                    -4.0 + r * 0.68,
                    0,
                ],
                radius=0.022, color=BLUE,
            ).set_opacity(rng.uniform(0.03, 0.09))
            for r in range(13) for c in range(20)
        ])
        corners = [
            ((-6.8,  3.6), ( 1, -1)),
            (( 6.8,  3.6), (-1, -1)),
            ((-6.8, -3.6), ( 1,  1)),
            (( 6.8, -3.6), (-1,  1)),
        ]
        brackets = VGroup(*[
            VGroup(
                Line([cx, cy, 0], [cx + dx*0.7, cy, 0],
                     stroke_width=1.2, color=BLUE, stroke_opacity=0.18),
                Line([cx, cy, 0], [cx, cy + dy*0.7, 0],
                     stroke_width=1.2, color=BLUE, stroke_opacity=0.18),
            )
            for (cx, cy), (dx, dy) in corners
        ])
        bg = VGroup(dots, brackets)
        self.add(bg)
        return bg

    def _fade_content(self, bg: VGroup, run_time=0.6):
        """Fade everything except the background grid."""
        content = [m for m in self.mobjects if m is not bg]
        if content:
            self.play(FadeOut(*content), run_time=run_time)
        self.remove(bg)

    # ── Audio helpers ─────────────────────────────────────────────
    def _sound(self, key):
        self.add_sound(os.path.join(AUDIO, f"{key}.mp3"), gain=1)

    def _pad(self, key, used_seconds):
        remaining = DUR[key] - used_seconds - 0.6
        if remaining > 0:
            self.wait(remaining)

    # ── SCENE 0 — Ebook Ad (~22 s) ──────────────────────────────
    def s0_ad(self):
        bg = self._tech_bg()
        self._sound("s0")

        ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
        cover_path = os.path.join(ASSETS, "Think Like A CISSP Cover.jpg")

        sponsor = Text("A MESSAGE FROM ZERO DAY LABS",
                       font_size=13, color=AMBER, weight=BOLD)
        sponsor.to_edge(UP, buff=0.28)
        sponsor_line = Line(LEFT*6, RIGHT*6, color=AMBER, stroke_width=0.8)
        sponsor_line.next_to(sponsor, DOWN, buff=0.1)
        self.play(FadeIn(sponsor), Create(sponsor_line), run_time=0.5)

        if os.path.exists(cover_path):
            cover = ImageMobject(cover_path)
            cover.set_height(5.5)
            cover.move_to(LEFT * 3.3 + DOWN * 0.2)
            glow = RoundedRectangle(corner_radius=0.12,
                                    width=cover.width + 0.12,
                                    height=cover.height + 0.12,
                                    color=GREEN, stroke_width=2, fill_opacity=0)
            glow.move_to(cover.get_center())
            self.play(FadeIn(cover, scale=0.92), run_time=0.9)
            self.play(Create(glow), run_time=0.4)
        else:
            placeholder = RoundedRectangle(corner_radius=0.2, width=3.2, height=5.5,
                                           color=GREEN, fill_color="#051A05",
                                           fill_opacity=0.9, stroke_width=2)
            placeholder.move_to(LEFT * 3.3 + DOWN * 0.2)
            ph_txt = Text("Think Like A CISSP Cover.jpg\nnot found",
                          font_size=16, color=GREEN)
            ph_txt.move_to(placeholder.get_center())
            self.play(FadeIn(placeholder), Write(ph_txt), run_time=0.6)

        right_x = RIGHT * 1.8
        t1 = heading("Think Like", size=44, color=WHITE)
        t2 = heading("A CISSP", size=54, color=BLUE)
        t1.move_to(right_x + UP * 1.7)
        t2.next_to(t1, DOWN, buff=0.08).align_to(t1, LEFT)
        self.play(Write(t1), run_time=0.6)
        self.play(Write(t2), run_time=0.5)

        div = Line(ORIGIN, RIGHT*4.8, color=BLUE, stroke_width=1.2)
        div.next_to(t2, DOWN, buff=0.22).align_to(t1, LEFT)
        self.play(Create(div), run_time=0.35)

        tag1 = Text("Master the mindset that separates candidates",
                    font_size=16, color=WHITE)
        tag2 = Text("who pass from engineers who fail.", font_size=16, color=WHITE)
        tag1.next_to(div, DOWN, buff=0.2).align_to(t1, LEFT)
        tag2.next_to(tag1, DOWN, buff=0.1).align_to(t1, LEFT)
        self.play(FadeIn(tag1, shift=UP*0.1), run_time=0.45)
        self.play(FadeIn(tag2, shift=UP*0.1), run_time=0.45)

        sub = Text("Reason like a senior security leader.",
                   font_size=14, color="#AAAAAA")
        sub.next_to(tag2, DOWN, buff=0.2).align_to(t1, LEFT)
        self.play(FadeIn(sub), run_time=0.4)

        price_bg = RoundedRectangle(corner_radius=0.18, width=1.7, height=0.65,
                                    fill_color=AMBER, fill_opacity=1, stroke_width=0)
        price_txt = Text("$25.00", font_size=23, color="#0A0E1A", weight=BOLD)
        price_bg.next_to(sub, DOWN, buff=0.35).align_to(t1, LEFT)
        price_txt.move_to(price_bg.get_center())
        self.play(FadeIn(price_bg, scale=0.8), Write(price_txt), run_time=0.5)

        url = mono("zerodaylabs.tech/store/think-like-a-cissp", size=13, color=BLUE)
        url.next_to(price_bg, DOWN, buff=0.25).align_to(t1, LEFT)
        self.play(Write(url), run_time=0.55)
        self.wait(2.0)
        self.play(price_bg.animate.set_fill(color="#FFD700"), run_time=0.3)
        self.play(price_bg.animate.set_fill(color=AMBER), run_time=0.3)

        self._pad("s0", 8.2)
        self._fade_content(bg)

    # ── SCENE 1 — Hook (~28 s) ───────────────────────────────────
    def s1_hook(self):
        bg = self._tech_bg()
        self._sound("s1")

        # Shield with TRUSTED label
        shield_body = RoundedRectangle(corner_radius=0.3, width=3.0, height=3.2,
                                       color=GREEN, fill_color="#051A0A",
                                       fill_opacity=1, stroke_width=3)
        shield_body.move_to(LEFT * 3.2)
        shield_label = Text("TRUSTED", font_size=24, color=GREEN, weight=BOLD)
        shield_label.move_to(shield_body.get_center())
        self.play(FadeIn(shield_body), Write(shield_label), run_time=0.7)  # t≈0.7
        self.wait(0.8)                                                      # t≈1.5

        # X slashes through shield
        slash1 = Line(shield_body.get_corner(UL) + RIGHT*0.2 + DOWN*0.2,
                      shield_body.get_corner(DR) + LEFT*0.2 + UP*0.2,
                      color=RED, stroke_width=6)
        slash2 = Line(shield_body.get_corner(UR) + LEFT*0.2 + DOWN*0.2,
                      shield_body.get_corner(DL) + RIGHT*0.2 + UP*0.2,
                      color=RED, stroke_width=6)
        self.play(Create(slash1), Create(slash2),
                  shield_body.animate.set_color(RED).set_stroke(color=RED),
                  shield_label.animate.set_color(RED),
                  run_time=0.7)                                             # t≈2.2

        # Right side: core message
        prove = heading("PROVE IT.", size=46, color=WHITE)
        prove2 = heading("AGAIN.", size=46, color=BLUE)
        prove.move_to(RIGHT * 1.8 + UP * 1.1)
        prove2.next_to(prove, DOWN, buff=0.1)
        self.play(Write(prove), run_time=0.6)                               # t≈2.8
        self.play(Write(prove2), run_time=0.4)                              # t≈3.2

        sub = Text("Every request.  Every device.  Every time.",
                   font_size=20, color=AMBER)
        sub.next_to(prove2, DOWN, buff=0.35)
        self.play(FadeIn(sub, shift=UP*0.15), run_time=0.5)                 # t≈3.7
        self.wait(2.0)                                                      # t≈5.7

        self._fade_content(bg, run_time=0.4)
        bg2 = self._tech_bg()

        # Title card
        title = Text("What Is Zero Trust\nand Why Is Everyone\nTalking About It?",
                     font_size=40, color=WHITE, weight=BOLD, line_spacing=1.15)
        title.move_to(UP * 0.6)
        self.play(Write(title), run_time=1.0)                               # t≈7.1

        zdl_bar = Rectangle(width=config.frame_width + 1, height=0.75,
                             fill_color=BLUE, fill_opacity=1, stroke_width=0)
        zdl_bar.to_edge(DOWN, buff=0)
        zdl_txt = Text("Zero Day Labs  —  Train. Test. Certify.",
                       font_size=20, color=BG, weight=BOLD)
        zdl_txt.move_to(zdl_bar.get_center())
        self.play(FadeIn(zdl_bar), FadeIn(zdl_txt), run_time=0.5)           # t≈7.6

        self._pad("s1", 7.6)
        self._fade_content(bg2)

    # ── SCENE 2 — The Old Model (~62 s) ─────────────────────────
    def s2_old_model(self):
        bg = self._tech_bg()
        self._sound("s2")

        stitle = scene_title(self, "The Old Model: Castle and Moat", color=WHITE)  # t≈0.7
        self.wait(0.4)                                                      # t≈1.1

        # Perimeter circle
        moat = Circle(radius=2.4, color="#334455", stroke_width=14,
                      stroke_opacity=0.6, fill_opacity=0)
        moat.move_to(LEFT * 0.5)
        inner = Circle(radius=2.0, color=GREEN, stroke_width=2.5,
                       fill_color="#051A05", fill_opacity=0.7)
        inner.move_to(LEFT * 0.5)
        trust_lbl = Text("TRUSTED\nINTERNAL", font_size=18, color=GREEN,
                         weight=BOLD, line_spacing=1.1)
        trust_lbl.move_to(LEFT * 0.5)
        untrust = Text("UNTRUSTED", font_size=15, color="#556677")
        untrust.move_to(RIGHT * 4.5 + UP * 2.0)

        self.play(Create(moat), Create(inner), run_time=0.9)                # t≈2.0
        self.play(Write(trust_lbl), FadeIn(untrust), run_time=0.6)          # t≈2.6
        self.wait(4.0)                                                      # t≈6.6

        # Cracks — cloud, remote icons break through
        cloud_txt = Text("☁  Cloud", font_size=19, color=AMBER)
        remote_txt = Text("⌂  Remote Work", font_size=19, color=AMBER)
        saas_txt = Text("⊞  SaaS Apps", font_size=19, color=AMBER)
        breakers = VGroup(cloud_txt, remote_txt, saas_txt)
        breakers.arrange(DOWN, buff=0.35)
        breakers.move_to(RIGHT * 4.0 + DOWN * 0.3)

        self.play(FadeIn(breakers, shift=LEFT*0.3), run_time=0.7)            # t≈7.3
        crack_line = Line(inner.get_right() + LEFT*0.1,
                          inner.get_right() + RIGHT*0.8,
                          color=RED, stroke_width=3)
        self.play(Create(crack_line), run_time=0.4)                          # t≈7.7
        self.wait(4.0)                                                      # t≈11.7

        moat_gone = Text("The moat is gone.", font_size=22, color=RED, weight=BOLD)
        moat_gone.to_edge(DOWN, buff=0.8)
        self.play(Write(moat_gone), run_time=0.6)                           # t≈12.3
        self.wait(3.5)                                                      # t≈15.8

        # Fade perimeter scene
        self.play(
            FadeOut(moat), FadeOut(inner), FadeOut(trust_lbl),
            FadeOut(untrust), FadeOut(breakers), FadeOut(crack_line),
            FadeOut(moat_gone), FadeOut(stitle), run_time=0.5
        )                                                                   # t≈16.3

        # Attack path: lateral movement
        stitle2 = scene_title(self, "One Credential → Unlimited Access", color=RED)
        self.wait(0.5)                                                      # t≈17.5

        # Node boxes
        node_data = [
            ("ATTACKER",  "#FF2200", LEFT * 5.5),
            ("EMAIL\nSERVER", BLUE, LEFT * 2.0),
            ("FILE\nSHARE", BLUE, ORIGIN + UP * 0.0),
            ("PAYROLL\nDB", BLUE, RIGHT * 2.0),
            ("DOMAIN\nCONTROLLER", RED, RIGHT * 5.0),
        ]
        nodes = []
        for lbl, col, pos in node_data:
            box = RoundedRectangle(corner_radius=0.15, width=1.85, height=1.0,
                                    color=col, fill_color=BG,
                                    fill_opacity=0.95, stroke_width=2)
            box.move_to(pos + DOWN * 0.4)
            txt = Text(lbl, font_size=14, color=col, weight=BOLD, line_spacing=1.1)
            txt.move_to(box.get_center())
            nodes.append(VGroup(box, txt))

        self.play(*[FadeIn(n, scale=0.88) for n in nodes], run_time=0.8)    # t≈18.3

        # Attacker dot moving laterally
        attacker_dot = Dot(color=RED, radius=0.14)
        attacker_dot.move_to(nodes[0].get_right())
        self.add(attacker_dot)

        elapsed = 18.3
        for i in range(1, len(nodes)):
            arr = Arrow(nodes[i-1].get_right(), nodes[i].get_left(),
                        color=RED, stroke_width=2.5, buff=0.05,
                        max_tip_length_to_length_ratio=0.12)
            self.play(
                GrowArrow(arr),
                attacker_dot.animate.move_to(nodes[i].get_center()),
                nodes[i][0].animate.set_color(RED).set_stroke(color=RED),
                run_time=0.7
            )
            self.wait(1.5)
            elapsed += 2.2

        # t≈26.5
        pwned = heading("OWNED.", size=42, color=RED)
        pwned.to_edge(DOWN, buff=0.6)
        self.play(Write(pwned), run_time=0.5)                               # t≈27.0
        self.wait(4.0)                                                      # t≈31.0

        elapsed = 31.0
        self._pad("s2", elapsed)
        self._fade_content(bg)

    # ── SCENE 3 — What Is Zero Trust? (~88 s) ────────────────────
    def s3_what_is_zt(self):
        bg = self._tech_bg()
        self._sound("s3")

        # Core principle — big impact
        never = heading("NEVER TRUST.", size=52, color=RED)
        always = heading("ALWAYS VERIFY.", size=52, color=GREEN)
        never.move_to(UP * 0.55)
        always.next_to(never, DOWN, buff=0.18)
        self.play(Write(never), run_time=0.9)                               # t≈0.9
        self.play(Write(always), run_time=0.9)                              # t≈1.8

        nist_bg = RoundedRectangle(corner_radius=0.14, width=5.8, height=0.60,
                                    color=AMBER, fill_color="#1A0D00",
                                    fill_opacity=1, stroke_width=1.5)
        nist_txt = mono("NIST SP 800-207", size=17, color=AMBER)
        nist_txt.move_to(nist_bg.get_center())
        nist_grp = VGroup(nist_bg, nist_txt)
        nist_grp.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(nist_grp, scale=0.85), run_time=0.5)               # t≈2.3
        self.wait(4.5)                                                      # t≈6.8

        self.play(FadeOut(never), FadeOut(always), FadeOut(nist_grp), run_time=0.4)

        # Three pillars
        stitle = scene_title(self, "The Three Pillars of Zero Trust", color=BLUE)
        self.wait(0.4)                                                      # t≈8.3 (approx)

        pillars = [
            (
                "1  Verify Explicitly",
                "Every user. Every device.\nEvery request. Every time.\nUse all available signals.",
                BLUE,
            ),
            (
                "2  Least Privilege",
                "Just enough access.\nJust in time.\nRevoked when the task is done.",
                AMBER,
            ),
            (
                "3  Assume Breach",
                "Segment your network.\nMonitor everything.\nLimit the blast radius.",
                GREEN,
            ),
        ]

        all_pillars = VGroup()
        for title_str, body_str, color in pillars:
            card = RoundedRectangle(corner_radius=0.2, width=3.9, height=2.7,
                                    color=color, fill_color=BG,
                                    fill_opacity=0.97, stroke_width=2.5)
            card_title = Text(title_str, font_size=19, color=color, weight=BOLD)
            card_title.move_to(card.get_center() + UP * 0.82)
            divline = Line(LEFT*1.6, RIGHT*1.6, color=color,
                           stroke_width=0.8, stroke_opacity=0.5)
            divline.move_to(card.get_center() + UP * 0.42)
            card_body = Text(body_str, font_size=15, color=WHITE, line_spacing=1.3)
            card_body.move_to(card.get_center() + DOWN * 0.45)
            all_pillars.add(VGroup(card, card_title, divline, card_body))

        all_pillars.arrange(RIGHT, buff=0.5)
        all_pillars.move_to(DOWN * 0.35)

        elapsed = 8.3
        for pillar in all_pillars:
            self.play(FadeIn(pillar, shift=UP*0.2, scale=0.92), run_time=0.7)
            self.wait(10.0)
            elapsed += 10.7
        # elapsed ≈ 40.4

        # NOT a product callout
        trap_bg = RoundedRectangle(corner_radius=0.18, width=11.0, height=1.1,
                                    color=RED, fill_color="#1A0000",
                                    fill_opacity=1, stroke_width=2)
        trap_bg.to_edge(DOWN, buff=0.32)
        trap_txt = Text(
            "Zero Trust is NOT a product you buy — it is an architecture, a strategy.",
            font_size=20, color=WHITE, weight=BOLD
        )
        trap_txt.move_to(trap_bg.get_center())
        self.play(FadeIn(trap_bg), Write(trap_txt), run_time=0.8)            # t≈41.2
        self.play(
            Flash(trap_bg.get_center(), color=RED, num_lines=10, flash_radius=1.0),
            run_time=0.5
        )                                                                    # t≈41.7
        self.wait(8.0)                                                       # t≈49.7

        elapsed = 49.7
        self._pad("s3", elapsed)
        self._fade_content(bg)

    # ── SCENE 4 — How It Works in Practice (~88 s) ───────────────
    def s4_how_it_works(self):
        bg = self._tech_bg()
        self._sound("s4")

        stitle = scene_title(self, "Zero Trust in Practice", color=GREEN)   # t≈0.7
        self.wait(0.4)                                                      # t≈1.1

        # Scenario header
        scenario = Text("Sarah  →  Coffee Shop  →  Payroll App",
                        font_size=22, color=AMBER, weight=BOLD)
        scenario.move_to(UP * 2.0)
        self.play(FadeIn(scenario, shift=DOWN*0.1), run_time=0.5)            # t≈1.6
        self.wait(1.5)                                                      # t≈3.1

        # Verification steps
        checks = [
            ("Identity",   "MFA confirmed",              BLUE,  LEFT * 4.2),
            ("Device",     "Patched, managed, clean",    AMBER, LEFT * 1.3),
            ("Context",    "Normal time, normal location", WHITE, RIGHT * 1.6),
            ("Policy",     "Decision: GRANT (payroll only)", GREEN, RIGHT * 4.5),
        ]

        check_cards = []
        elapsed = 3.1
        for label, detail, color, pos in checks:
            card_bg = RoundedRectangle(corner_radius=0.18, width=2.55, height=1.35,
                                       color=color, fill_color=BG,
                                       fill_opacity=0.95, stroke_width=2)
            card_bg.move_to(pos + DOWN * 0.2)
            card_label = Text(label, font_size=17, color=color, weight=BOLD)
            card_label.move_to(card_bg.get_center() + UP * 0.28)
            card_detail = Text(detail, font_size=13, color=WHITE, line_spacing=1.2)
            card_detail.move_to(card_bg.get_center() + DOWN * 0.2)
            check_mark = Text("✓", font_size=22, color=color, weight=BOLD)
            check_mark.next_to(card_bg.get_top(), UP, buff=0.1)
            card = VGroup(card_bg, card_label, card_detail)
            check_cards.append((card, check_mark))

            self.play(FadeIn(card, shift=UP*0.18), run_time=0.55)
            self.wait(4.5)
            self.play(Write(check_mark), run_time=0.35)
            elapsed += 5.4
        # elapsed ≈ 24.7

        # Connecting arrows between checks
        for i in range(len(check_cards) - 1):
            arr = Arrow(
                check_cards[i][0].get_right(),
                check_cards[i+1][0].get_left(),
                color="#334455", stroke_width=1.8, buff=0.05,
                max_tip_length_to_length_ratio=0.15
            )
            self.play(GrowArrow(arr), run_time=0.3)
            elapsed += 0.3

        # PDP label
        pdp_bg = RoundedRectangle(corner_radius=0.14, width=5.2, height=0.62,
                                   color=GREEN, fill_color="#05140A",
                                   fill_opacity=1, stroke_width=1.5)
        pdp_txt = mono("Policy Decision Point  (NIST 800-207)", size=16, color=GREEN)
        pdp_txt.move_to(pdp_bg.get_center())
        pdp_grp = VGroup(pdp_bg, pdp_txt)
        pdp_grp.move_to(DOWN * 1.55)
        self.play(FadeIn(pdp_grp), run_time=0.5)                            # t≈26.0
        self.wait(5.0)                                                      # t≈31.0

        # VPN vs ZTNA comparison
        self.play(
            *[FadeOut(c) for c, _ in check_cards],
            *[FadeOut(m) for _, m in check_cards],
            FadeOut(pdp_grp), FadeOut(scenario), run_time=0.4
        )                                                                   # t≈31.4

        stitle2 = scene_title(self, "ZTNA vs VPN", color=BLUE)             # t≈32.1
        self.wait(0.3)

        vpn_col = Rectangle(width=5.5, height=3.2, color="#334455",
                             fill_color="#0A1018", fill_opacity=0.9, stroke_width=2)
        ztna_col = Rectangle(width=5.5, height=3.2, color=GREEN,
                              fill_color="#051A0A", fill_opacity=0.9, stroke_width=2)
        vpn_col.move_to(LEFT * 3.2 + DOWN * 0.35)
        ztna_col.move_to(RIGHT * 3.2 + DOWN * 0.35)
        vpn_head  = heading("VPN", size=24, color="#778899")
        ztna_head = heading("ZTNA", size=24, color=GREEN)
        vpn_head.next_to(vpn_col.get_top(), DOWN, buff=0.22)
        ztna_head.next_to(ztna_col.get_top(), DOWN, buff=0.22)

        vpn_items  = Text("Full network access\nTrust once at login\nLateral movement easy\nBulky, slow for cloud",
                          font_size=16, color=WHITE, line_spacing=1.35)
        ztna_items = Text("Per-app access only\nVerify every session\nLateral movement blocked\nCloud-native, fast",
                          font_size=16, color=WHITE, line_spacing=1.35)
        vpn_items.move_to(vpn_col.get_center() + DOWN * 0.2)
        ztna_items.move_to(ztna_col.get_center() + DOWN * 0.2)

        self.play(
            FadeIn(vpn_col), FadeIn(ztna_col),
            Write(vpn_head), Write(ztna_head),
            run_time=0.7
        )                                                                   # t≈33.1
        self.play(FadeIn(vpn_items), FadeIn(ztna_items), run_time=0.7)      # t≈33.8
        self.wait(8.0)                                                      # t≈41.8

        # Microsegmentation note
        seg_bg = RoundedRectangle(corner_radius=0.16, width=10.0, height=0.82,
                                   color=AMBER, fill_color="#1A0D00",
                                   fill_opacity=1, stroke_width=2)
        seg_bg.to_edge(DOWN, buff=0.3)
        seg_txt = Text(
            "Microsegmentation — even if one session is compromised, lateral movement is blocked.",
            font_size=17, color=AMBER, weight=BOLD
        )
        seg_txt.move_to(seg_bg.get_center())
        self.play(FadeIn(seg_bg), Write(seg_txt), run_time=0.7)              # t≈42.5
        self.wait(5.0)                                                      # t≈47.5

        elapsed = 47.5
        self._pad("s4", elapsed)
        self._fade_content(bg)

    # ── SCENE 5 — Why Everyone's Talking About It (~55 s) ────────
    def s5_why_everyone(self):
        bg = self._tech_bg()
        self._sound("s5")

        stitle = scene_title(self, "Why Zero Trust, Why Now?", color=AMBER) # t≈0.7
        self.wait(0.3)                                                      # t≈1.0

        reasons = [
            ("1  The Perimeter Died",
             "Remote work and cloud dissolved the boundary.\nYou cannot protect a perimeter that no longer exists.",
             RED),
            ("2  The Breaches Proved It",
             "Lateral movement after one phished credential — the attack\npattern behind SolarWinds, Colonial Pipeline, and dozens more.",
             AMBER),
            ("3  The Government Mandated It",
             "US Executive Order 14028 (May 2021) required federal agencies\nto adopt Zero Trust architecture. Every vendor followed.",
             BLUE),
        ]

        elapsed = 1.0
        reason_cards = []
        for title_str, body_str, color in reasons:
            card_bg = RoundedRectangle(corner_radius=0.18, width=11.5, height=1.4,
                                       color=color, fill_color=BG,
                                       fill_opacity=0.95, stroke_width=2)
            y_offset = UP * (1.5 - reasons.index((title_str, body_str, color)) * 1.65)
            card_bg.move_to(y_offset + DOWN * 0.3)
            card_title = Text(title_str, font_size=19, color=color, weight=BOLD)
            card_title.move_to(card_bg.get_center() + UP * 0.35)
            card_title.align_to(card_bg.get_left(), LEFT).shift(RIGHT * 0.3)
            card_body = Text(body_str, font_size=14, color=WHITE, line_spacing=1.25)
            card_body.move_to(card_bg.get_center() + DOWN * 0.18)
            card_body.align_to(card_bg.get_left(), LEFT).shift(RIGHT * 0.3)
            reason_cards.append(VGroup(card_bg, card_title, card_body))

        for card in reason_cards:
            self.play(FadeIn(card, shift=RIGHT*0.25), run_time=0.6)
            self.wait(8.0)
            elapsed += 8.6
        # elapsed ≈ 26.8

        # Marketing vs reality callout
        reality_bg = RoundedRectangle(corner_radius=0.16, width=10.5, height=1.5,
                                       color=WHITE, fill_color="#0F0F18",
                                       fill_opacity=1, stroke_width=1.5)
        reality_bg.to_edge(DOWN, buff=0.32)
        reality_txt = Text(
            "Zero Trust is over-marketed — every vendor calls their product Zero Trust.\n"
            "The architecture is real. The buzzword is noise. Know the difference.",
            font_size=18, color=WHITE, line_spacing=1.35
        )
        reality_txt.move_to(reality_bg.get_center())
        self.play(FadeIn(reality_bg), Write(reality_txt), run_time=0.8)     # t≈27.6
        self.wait(5.0)                                                      # t≈32.6

        elapsed = 32.6
        self._pad("s5", elapsed)
        self._fade_content(bg)

    # ── SCENE 6 — Exam Relevance + Recap (~58 s) ─────────────────
    def s6_exam_recap(self):
        bg = self._tech_bg()
        self._sound("s6")

        stitle = scene_title(self, "Exam Prep — Zero Trust", color=AMBER)   # t≈0.7
        self.wait(0.3)                                                      # t≈1.0

        # Cert coverage
        cert_items = [
            ("Security+ SY0-701 Domain 1",
             "Control plane vs data plane · Adaptive identity\n"
             "Policy engine · Policy administrator · Policy enforcement point",
             BLUE),
            ("CISSP",
             "Domains 1, 3, 5, 7 — governance, architecture,\nidentity management, communications",
             GREEN),
        ]

        elapsed = 1.0
        cert_cards = []
        for title_str, body_str, color in cert_items:
            card_bg = RoundedRectangle(corner_radius=0.18, width=11.5, height=1.45,
                                       color=color, fill_color=BG,
                                       fill_opacity=0.95, stroke_width=2)
            card_bg.move_to(UP * (1.5 - cert_items.index((title_str, body_str, color)) * 1.7) + DOWN * 0.3)
            card_title = Text(title_str, font_size=18, color=color, weight=BOLD)
            card_title.move_to(card_bg.get_center() + UP * 0.3)
            card_title.align_to(card_bg.get_left(), LEFT).shift(RIGHT * 0.3)
            card_body = Text(body_str, font_size=14, color=WHITE, line_spacing=1.25)
            card_body.move_to(card_bg.get_center() + DOWN * 0.25)
            card_body.align_to(card_bg.get_left(), LEFT).shift(RIGHT * 0.3)
            cert_cards.append(VGroup(card_bg, card_title, card_body))

        for card in cert_cards:
            self.play(FadeIn(card, shift=RIGHT*0.2), run_time=0.6)
            self.wait(7.0)
            elapsed += 7.6
        # elapsed ≈ 16.2

        # Exam trap
        trap_bg = RoundedRectangle(corner_radius=0.16, width=10.5, height=0.82,
                                    color=RED, fill_color="#1A0000",
                                    fill_opacity=1, stroke_width=2)
        trap_bg.move_to(DOWN * 1.85)
        trap_txt = Text(
            "EXAM TRAP: Zero Trust is NOT a product — it is an architecture. NIST 800-207.",
            font_size=18, color=WHITE, weight=BOLD
        )
        trap_txt.move_to(trap_bg.get_center())
        self.play(FadeIn(trap_bg), Write(trap_txt), run_time=0.7)            # t≈16.9
        self.play(
            Flash(trap_bg.get_center(), color=RED, num_lines=8, flash_radius=0.9),
            run_time=0.5
        )                                                                   # t≈17.4
        self.wait(4.0)                                                      # t≈21.4

        # 3-pillar recap
        self.play(
            *[FadeOut(c) for c in cert_cards],
            FadeOut(trap_bg), FadeOut(trap_txt),
            run_time=0.4
        )                                                                   # t≈21.8

        recap_title = heading("15-Second Recap", size=28, color=WHITE)
        recap_title.move_to(UP * 2.2)
        self.play(Write(recap_title), run_time=0.5)                          # t≈22.3

        recap_items = [
            ("Verify Explicitly",  "every user, device, and request — every time",       BLUE),
            ("Least Privilege",    "just enough access, just in time",                    AMBER),
            ("Assume Breach",      "segment, monitor, limit blast radius",                GREEN),
        ]
        elapsed = 22.3
        for i, (term, desc, color) in enumerate(recap_items):
            term_mob = Text(f"  {term}", font_size=22, color=color, weight=BOLD)
            desc_mob = Text(f"    {desc}", font_size=17, color=WHITE)
            row = VGroup(term_mob, desc_mob).arrange(DOWN, buff=0.06, aligned_edge=LEFT)
            row.move_to(UP * (1.2 - i * 1.0))
            row.to_edge(LEFT, buff=0.8)
            self.play(FadeIn(row, shift=RIGHT*0.2), run_time=0.45)
            self.wait(3.5)
            elapsed += 3.95
        # elapsed ≈ 34.15

        nist_reminder = mono("Reference: NIST SP 800-207", size=17, color=AMBER)
        nist_reminder.to_edge(DOWN, buff=0.55)
        self.play(FadeIn(nist_reminder), run_time=0.4)                       # t≈34.6
        self.wait(4.0)                                                      # t≈38.6

        elapsed = 38.6
        self._pad("s6", elapsed)
        self._fade_content(bg)

    # ── SCENE 7 — End Card (~30 s) ────────────────────────────────
    def s7_end_card(self):
        bg = self._tech_bg()
        self._sound("s7")

        stitle = scene_title(self, "Think Like A CISSP", color=BLUE)        # t≈0.7
        self.wait(0.3)                                                      # t≈1.0

        book_desc = Text(
            "Complex frameworks, broken down the way the exam expects.\n"
            "Mindset over memorization.",
            font_size=21, color=WHITE, line_spacing=1.4
        )
        book_desc.move_to(UP * 0.6)
        self.play(FadeIn(book_desc, shift=UP*0.1), run_time=0.6)             # t≈1.6

        price_bg = RoundedRectangle(corner_radius=0.16, width=1.55, height=0.55,
                                    fill_color=AMBER, fill_opacity=1, stroke_width=0)
        price_txt = Text("$25.00", font_size=18, color=BG, weight=BOLD)
        price_txt.move_to(price_bg.get_center())
        avail = Text("Available at:", font_size=17, color="#AAAAAA")
        avail_url = mono("zerodaylabs.tech/store/think-like-a-cissp", size=17, color=BLUE)
        avail_row = VGroup(avail, avail_url, VGroup(price_bg, price_txt)).arrange(RIGHT, buff=0.28)
        avail_row.next_to(book_desc, DOWN, buff=0.35)
        self.play(FadeIn(avail_row), run_time=0.5)                           # t≈2.1
        self.wait(3.5)                                                      # t≈5.6
        self.play(FadeOut(book_desc), FadeOut(avail_row), run_time=0.35)     # t≈5.95

        # Website CTA
        cta_head = heading("Prep smarter at zerodaylabs.tech", size=32, color=WHITE)
        cta_head.move_to(UP * 1.4)
        self.play(Write(cta_head), run_time=0.7)                             # t≈6.65

        cta_body = Text(
            "Adaptive practice exams · Domain guides · Quizzes\n"
            "Security+  ·  CISSP",
            font_size=20, color=WHITE, line_spacing=1.4
        )
        cta_body.next_to(cta_head, DOWN, buff=0.3)
        self.play(FadeIn(cta_body), run_time=0.5)                            # t≈7.15

        url_bg = RoundedRectangle(corner_radius=0.22, width=5.4, height=0.72,
                                   color=GREEN, fill_color="#051A0A",
                                   fill_opacity=1, stroke_width=2)
        url_txt = Text("www.zerodaylabs.tech", font=MONO,
                       font_size=24, color=GREEN, weight=BOLD)
        url_txt.move_to(url_bg.get_center())
        url_grp = VGroup(url_bg, url_txt)
        url_grp.next_to(cta_body, DOWN, buff=0.35)
        self.play(FadeIn(url_grp, scale=0.88), run_time=0.55)                # t≈7.7
        self.play(url_bg.animate.set_stroke(color=WHITE, width=2.5), run_time=0.3)
        self.play(url_bg.animate.set_stroke(color=GREEN, width=2), run_time=0.3)  # t≈8.3

        thanks = Text("Thanks for watching — like, subscribe, and drop a comment!",
                      font_size=19, color=AMBER)
        comment_ask = Text('"What security buzzword should I break down next?"',
                           font_size=16, color=WHITE)
        tagline = Text("Train.  Test.  Certify.", font_size=17, color=BLUE, weight=BOLD)
        footer = VGroup(thanks, comment_ask, tagline).arrange(DOWN, buff=0.14)
        footer.to_edge(DOWN, buff=0.38)
        self.play(FadeIn(footer), run_time=0.5)                              # t≈8.8

        elapsed = 8.8
        self._pad("s7", elapsed)

        black = Rectangle(
            width=config.frame_width + 1,
            height=config.frame_height + 1,
            fill_color=BLACK, fill_opacity=0, stroke_width=0,
        )
        self.add(black)
        self.play(black.animate.set_fill(opacity=1), run_time=1.8)
        self.wait(0.4)
