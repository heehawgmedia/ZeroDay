from manim import *
import json
import os

# ─── Color Palette ───────────────────────────────────────────────
BG    = "#0A0E1A"
BLUE  = "#00C8FF"
AMBER = "#F5A623"
GREEN = "#39D353"
RED   = "#FF4D4D"
PURPLE = "#AA44FF"
MONO  = "DejaVu Sans Mono"

config.background_color = BG

AUDIO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mfa_audio")

_DUR_DEFAULTS = {
    "s0":  22.0,
    "s1":  20.0,
    "s2":  85.0,
    "s3": 120.0,
    "s4":  90.0,
    "s5":  30.0,
    "s6":  45.0,
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

def fade_all(scene, run_time=0.6):
    mobs = list(scene.mobjects)
    if mobs:
        scene.play(FadeOut(*mobs), run_time=run_time)

def scene_title(scene, text, color=WHITE):
    t = heading(text, size=32, color=color)
    t.to_edge(UP, buff=0.45)
    bar = Line(LEFT*6.5, RIGHT*6.5, color=color, stroke_width=1.5)
    bar.next_to(t, DOWN, buff=0.12)
    scene.play(Write(t), Create(bar), run_time=0.7)
    return VGroup(t, bar)


# ═══════════════════════════════════════════════════════════════════
#  MFA SCENE  —  manim -qh mfa_explainer.py MFAScene
# ═══════════════════════════════════════════════════════════════════
class MFAScene(Scene):
    def construct(self):
        self.s0_ad()
        self.s1_hook()
        self.s2_what_is_mfa()
        self.s3_sms_attacks()
        self.s4_mfa_ladder()
        self.s5_exam_tie_in()
        self.s6_end_card()

    # ── helpers ──────────────────────────────────────────────────
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

    # ── SCENE 0 — Ebook Ad (~22 s) ──────────────────────────────
    def s0_ad(self):
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
            ph_txt = Text("Think Like A CISSP Cover.jpg\nnot found", font_size=16, color=GREEN)
            ph_txt.move_to(placeholder.get_center())
            self.play(FadeIn(placeholder), Write(ph_txt), run_time=0.6)
            cover = placeholder

        right_x = RIGHT * 1.8
        title_line1 = heading("Think Like", size=44, color=WHITE)
        title_line2 = heading("A CISSP", size=54, color=BLUE)
        title_line1.move_to(right_x + UP * 1.7)
        title_line2.next_to(title_line1, DOWN, buff=0.08)
        title_line2.align_to(title_line1, LEFT)
        self.play(Write(title_line1), run_time=0.6)
        self.play(Write(title_line2), run_time=0.5)

        div = Line(ORIGIN, RIGHT * 4.8, color=BLUE, stroke_width=1.2)
        div.next_to(title_line2, DOWN, buff=0.22)
        div.align_to(title_line1, LEFT)
        self.play(Create(div), run_time=0.35)

        tag1 = Text("Master the mindset that separates candidates",
                    font_size=16, color=WHITE)
        tag2 = Text("who pass from engineers who fail.", font_size=16, color=WHITE)
        tag1.next_to(div, DOWN, buff=0.2)
        tag2.next_to(tag1, DOWN, buff=0.1)
        tag1.align_to(title_line1, LEFT)
        tag2.align_to(title_line1, LEFT)
        self.play(FadeIn(tag1, shift=UP*0.1), run_time=0.45)
        self.play(FadeIn(tag2, shift=UP*0.1), run_time=0.45)

        sub = Text("Reason like a senior security leader.",
                   font_size=14, color="#AAAAAA")
        sub.next_to(tag2, DOWN, buff=0.2)
        sub.align_to(title_line1, LEFT)
        self.play(FadeIn(sub), run_time=0.4)

        price_bg = RoundedRectangle(corner_radius=0.18, width=1.7, height=0.65,
                                    fill_color=AMBER, fill_opacity=1, stroke_width=0)
        price_txt = Text("$25.00", font_size=23, color="#0A0E1A", weight=BOLD)
        price_bg.next_to(sub, DOWN, buff=0.35)
        price_bg.align_to(title_line1, LEFT)
        price_txt.move_to(price_bg.get_center())
        self.play(FadeIn(price_bg, scale=0.8), Write(price_txt), run_time=0.5)

        url = mono("zerodaylabs.tech/store/think-like-a-cissp", size=13, color=BLUE)
        url.next_to(price_bg, DOWN, buff=0.25)
        url.align_to(title_line1, LEFT)
        self.play(Write(url), run_time=0.55)
        self.wait(2.0)
        self.play(price_bg.animate.set_fill(color="#FFD700"), run_time=0.3)
        self.play(price_bg.animate.set_fill(color=AMBER), run_time=0.3)

        self._pad("s0", 8.2)
        fade_all(self)

    # ── SCENE 1 — Hook (~20 s) ───────────────────────────────────
    def s1_hook(self):
        self._sound("s1")

        # Phone with SMS code
        phone = RoundedRectangle(corner_radius=0.3, width=2.2, height=3.8,
                                 color=WHITE, fill_color="#111827",
                                 fill_opacity=1, stroke_width=2)
        phone.move_to(LEFT * 3.5)
        notch = RoundedRectangle(corner_radius=0.08, width=0.6, height=0.18,
                                 color="#111827", fill_color="#111827",
                                 fill_opacity=1, stroke_width=0)
        notch.next_to(phone.get_top(), DOWN, buff=0.12)
        self.play(FadeIn(phone), FadeIn(notch), run_time=0.7)              # t≈0.7

        sms_bg = RoundedRectangle(corner_radius=0.15, width=1.9, height=1.1,
                                   color=BLUE, fill_color="#001A2A",
                                   fill_opacity=1, stroke_width=1.5)
        sms_bg.move_to(phone.get_center() + UP * 0.55)
        sms_lbl = Text("SMS", font_size=12, color=BLUE, weight=BOLD)
        sms_lbl.next_to(sms_bg.get_top(), DOWN, buff=0.1)
        sms_code = mono("847291", size=30, color=WHITE)
        sms_code.move_to(sms_bg.get_center() + DOWN * 0.06)
        self.play(FadeIn(sms_bg), FadeIn(sms_lbl), Write(sms_code), run_time=0.6)  # t≈1.3

        # Account locked warning
        warn_bg = RoundedRectangle(corner_radius=0.15, width=1.9, height=1.0,
                                    color=RED, fill_color="#1A0000",
                                    fill_opacity=1, stroke_width=1.5)
        warn_bg.move_to(phone.get_center() + DOWN * 0.75)
        warn_txt = Text("ACCOUNT\nLOCKED", font_size=18, color=RED, weight=BOLD,
                        line_spacing=1.1)
        warn_txt.move_to(warn_bg.get_center())
        self.play(FadeIn(warn_bg), Write(warn_txt), run_time=0.5)          # t≈1.8
        self.play(
            Flash(warn_bg.get_center(), color=RED, num_lines=8, flash_radius=0.8),
            run_time=0.5
        )                                                                   # t≈2.3

        # Right side hook
        hook1 = heading("You had 2FA.", size=36, color=WHITE)
        hook2 = heading("Still got hacked.", size=36, color=RED)
        hook1.move_to(RIGHT * 1.8 + UP * 1.1)
        hook2.next_to(hook1, DOWN, buff=0.22)
        self.play(Write(hook1), run_time=0.6)                               # t≈2.9
        self.play(Write(hook2), run_time=0.5)                               # t≈3.4

        question = Text(
            "Using SMS codes? You might be\none phone call away from losing everything.",
            font_size=20, color=AMBER, line_spacing=1.3
        )
        question.next_to(hook2, DOWN, buff=0.3)
        self.play(FadeIn(question, shift=UP*0.2), run_time=0.7)             # t≈4.1
        self.wait(2.0)                                                      # t≈6.1

        fade_all(self)

        # Title card
        title = Text("What Is Multi-Factor\nAuthentication?",
                     font_size=46, color=WHITE, weight=BOLD, line_spacing=1.15)
        sub = Text("— and Why SMS Isn't Enough —", font_size=24, color=BLUE)
        title.move_to(UP * 0.8)
        sub.next_to(title, DOWN, buff=0.28)
        self.play(Write(title), run_time=1.0)                               # t≈7.7
        self.play(FadeIn(sub, shift=UP*0.15), run_time=0.6)                 # t≈8.3

        # Branded bar
        zdl_bar = Rectangle(width=config.frame_width + 1, height=0.75,
                             fill_color=BLUE, fill_opacity=1, stroke_width=0)
        zdl_bar.to_edge(DOWN, buff=0)
        zdl_txt = Text("Zero Day Labs  —  Train. Test. Certify.",
                       font_size=20, color=BG, weight=BOLD)
        zdl_txt.move_to(zdl_bar.get_center())
        self.play(FadeIn(zdl_bar), FadeIn(zdl_txt), run_time=0.5)           # t≈8.8

        self._pad("s1", 8.8)
        fade_all(self)

    # ── SCENE 2 — What Is MFA? (~85 s) ──────────────────────────
    def s2_what_is_mfa(self):
        self._sound("s2")

        stitle = scene_title(self, "What Is MFA?", color=BLUE)             # t≈0.7
        self.wait(0.5)                                                      # t≈1.2

        # Auth vs Authz definitions
        auth_txt  = Text("Authentication  =  proving who you are",
                         font_size=22, color=WHITE)
        authz_txt = Text("Authorization  =  what you're allowed to do",
                         font_size=22, color="#888888")
        auth_txt.move_to(UP * 1.5)
        authz_txt.next_to(auth_txt, DOWN, buff=0.3)
        self.play(Write(auth_txt), run_time=0.7)                            # t≈1.9
        self.wait(0.6)
        self.play(FadeIn(authz_txt), run_time=0.5)                          # t≈3.0
        self.wait(3.5)                                                      # t≈6.5
        self.play(FadeOut(auth_txt), FadeOut(authz_txt), run_time=0.4)      # t≈6.9

        # Three factor cards
        factors = [
            ("Something\nYou KNOW",  "Password, PIN,\nSecurity Questions",  BLUE,  "?"),
            ("Something\nYou HAVE",  "Smart Card, Token,\nAuthenticator App", AMBER, "#"),
            ("Something\nYou ARE",   "Fingerprint, Face,\nIris, Voice",       GREEN, "@"),
        ]

        all_cards = VGroup()
        for title_str, body_str, color, sym in factors:
            card_bg = RoundedRectangle(corner_radius=0.2, width=3.7, height=2.6,
                                       color=color, fill_color=BG,
                                       fill_opacity=0.97, stroke_width=2.5)
            sym_mob = Text(sym, font=MONO, font_size=38, color=color)
            sym_mob.move_to(card_bg.get_center() + UP * 0.78)
            card_title = Text(title_str, font_size=19, color=color, weight=BOLD,
                              line_spacing=1.1)
            card_title.move_to(card_bg.get_center() + UP * 0.05)
            card_body = Text(body_str, font_size=15, color=WHITE, line_spacing=1.3)
            card_body.move_to(card_bg.get_center() + DOWN * 0.76)
            all_cards.add(VGroup(card_bg, sym_mob, card_title, card_body))

        all_cards.arrange(RIGHT, buff=0.5)
        all_cards.move_to(DOWN * 0.25)

        elapsed = 6.9
        for card in all_cards:
            self.play(FadeIn(card, shift=UP*0.2, scale=0.92), run_time=0.7)
            self.wait(8.5)
            elapsed += 9.2
        # t≈33.5

        # Extended factors note
        ext_label = Text("Extended factors — also on Security+ & CISSP exams:",
                         font_size=17, color="#AAAAAA")
        ext_items = mono(
            "Somewhere You Are  (location)        Something You Do  (behavioral)",
            size=16, color=BLUE
        )
        ext_label.to_edge(DOWN, buff=1.15)
        ext_items.next_to(ext_label, DOWN, buff=0.16)
        self.play(FadeIn(ext_label), FadeIn(ext_items), run_time=0.6)       # t≈34.1
        self.wait(7.0)                                                      # t≈41.1
        self.play(FadeOut(ext_label), FadeOut(ext_items), run_time=0.35)    # t≈41.5

        # EXAM TRAP banner
        trap_box = RoundedRectangle(corner_radius=0.2, width=11.5, height=2.3,
                                    color=RED, fill_color="#1A0000",
                                    fill_opacity=1, stroke_width=2.5)
        trap_box.move_to(DOWN * 2.0)
        trap_head = Text("EXAM TRAP", font_size=24, color=RED, weight=BOLD)
        trap_head.next_to(trap_box.get_top(), DOWN, buff=0.22)
        trap_body = Text(
            'Password  +  Security Question  =  ONE factor  (both are "something you know")\n'
            "Two inputs from the same category is NOT MFA.",
            font_size=19, color=WHITE, line_spacing=1.35
        )
        trap_body.next_to(trap_head, DOWN, buff=0.2)

        self.play(FadeIn(trap_box, scale=0.92), Write(trap_head), run_time=0.65)  # t≈42.2
        self.play(Write(trap_body), run_time=1.0)                           # t≈43.2
        self.play(
            Flash(trap_box.get_center(), color=RED, num_lines=10, flash_radius=1.2),
            run_time=0.5
        )                                                                   # t≈43.7
        self.wait(8.0)                                                      # t≈51.7

        # Takeaway
        self.play(FadeOut(trap_box), FadeOut(trap_head), FadeOut(trap_body), run_time=0.4)
        takeaway = heading("MFA = two DIFFERENT factor types", size=26, color=GREEN)
        box = SurroundingRectangle(takeaway, color=GREEN, buff=0.22, corner_radius=0.14)
        takeaway.move_to(DOWN * 2.0)
        box.move_to(DOWN * 2.0)
        self.play(Write(takeaway), Create(box), run_time=0.8)               # t≈52.9
        self.wait(5.0)                                                      # t≈57.9

        elapsed = 57.9
        self._pad("s2", elapsed)
        fade_all(self)

    # ── SCENE 3 — SMS Attacks (~120 s) ──────────────────────────
    def s3_sms_attacks(self):
        self._sound("s3")

        stitle = scene_title(self, "Why SMS MFA Fails", color=RED)         # t≈0.7
        self.wait(0.5)                                                      # t≈1.2

        # Quick SMS flow
        labels  = ["LOGIN", "SERVER\nSENDS CODE", "YOU\nENTER CODE", "ACCESS\nGRANTED"]
        colors  = [WHITE, BLUE, GREEN, AMBER]
        x_pos   = [-5.2, -1.8, 1.6, 5.0]

        flow_group = VGroup()
        for lbl, col, x in zip(labels, colors, x_pos):
            b = RoundedRectangle(corner_radius=0.14, width=2.8, height=1.0,
                                 color=col, fill_color=BG, fill_opacity=0.9, stroke_width=2)
            b.move_to([x, 1.8, 0])
            t = Text(lbl, font_size=16, color=col, weight=BOLD, line_spacing=1.1)
            t.move_to(b.get_center())
            flow_group.add(VGroup(b, t))

        arrows = VGroup(*[
            Arrow(flow_group[i].get_right(), flow_group[i+1].get_left(),
                  color="#555555", stroke_width=2.5, buff=0.05,
                  max_tip_length_to_length_ratio=0.15)
            for i in range(3)
        ])

        self.play(FadeIn(flow_group, lag_ratio=0.15), run_time=0.8)        # t≈2.0
        self.play(*[GrowArrow(a) for a in arrows], run_time=0.5)           # t≈2.5
        self.wait(3.5)                                                      # t≈6.0
        self.play(FadeOut(flow_group), FadeOut(arrows), run_time=0.4)      # t≈6.4

        # 4 attack cards in 2×2 grid
        attacks = [
            ("1  SIM Swapping",
             "Attacker convinces your carrier to port your number\n"
             "to their SIM. All SMS codes now go to them.\n"
             "Dominant real-world attack against SMS 2FA.",
             RED, LEFT*3.3 + UP*0.9, 22.0),
            ("2  SS7 Protocol Weakness",
             "Decades-old telecom signaling protocol.\n"
             "Nation-state actors intercept SMS in transit.\n"
             "No malware on your phone required.",
             AMBER, RIGHT*3.3 + UP*0.9, 17.0),
            ("3  Phishing / Real-Time Relay",
             "Fake login page captures your code live.\n"
             "Attacker replays it within the 30-second window.\n"
             "SMS codes are phishable by design.",
             BLUE, LEFT*3.3 + DOWN*1.55, 22.0),
            ("4  Mobile Malware",
             "Malware on your device silently forwards\n"
             "your texts to the attacker. Game over.",
             PURPLE, RIGHT*3.3 + DOWN*1.55, 12.0),
        ]

        elapsed = 6.4
        attack_cards = []
        for title_str, body_str, color, pos, dwell in attacks:
            card_bg = RoundedRectangle(corner_radius=0.18, width=5.8, height=2.1,
                                       color=color, fill_color="#0D0A14",
                                       fill_opacity=0.97, stroke_width=2)
            card_bg.move_to(pos)
            card_title = Text(title_str, font_size=19, color=color, weight=BOLD)
            card_title.next_to(card_bg.get_top(), DOWN, buff=0.2)
            card_body = Text(body_str, font_size=14, color=WHITE, line_spacing=1.25)
            card_body.next_to(card_title, DOWN, buff=0.16)
            card = VGroup(card_bg, card_title, card_body)
            attack_cards.append(card)
            self.play(FadeIn(card, shift=UP*0.2), run_time=0.65)
            self.wait(dwell)
            elapsed += 0.65 + dwell
        # elapsed ≈ 6.4 + (0.65+22) + (0.65+17) + (0.65+22) + (0.65+12) = 6.4 + 75 = 81.4

        # NIST badge
        nist_bg = RoundedRectangle(corner_radius=0.18, width=10.5, height=0.82,
                                    color=AMBER, fill_color="#1A0D00",
                                    fill_opacity=1, stroke_width=2)
        nist_bg.to_edge(DOWN, buff=0.3)
        nist_txt = Text(
            "NIST SP 800-63B — SMS / PSTN authentication is RESTRICTED for agency use",
            font_size=18, color=AMBER, weight=BOLD
        )
        nist_txt.move_to(nist_bg.get_center())
        self.play(FadeIn(nist_bg), Write(nist_txt), run_time=0.8)          # t≈82.2
        self.wait(10.0)                                                     # t≈92.2
        elapsed = 92.2

        self.play(
            *[FadeOut(c) for c in attack_cards],
            FadeOut(nist_bg), FadeOut(nist_txt),
            run_time=0.5
        )                                                                   # t≈92.7

        # Nuance slide
        nuance = heading("SMS MFA is still better than no MFA.", size=30, color=GREEN)
        nuance.move_to(UP * 0.6)
        msg = Text(
            "The goal is not to turn it off.\nThe goal is to upgrade when you can.",
            font_size=22, color=WHITE, line_spacing=1.4
        )
        msg.next_to(nuance, DOWN, buff=0.35)
        self.play(Write(nuance), run_time=0.7)                              # t≈93.4
        self.play(FadeIn(msg, shift=UP*0.1), run_time=0.6)                  # t≈94.0
        self.wait(8.0)                                                      # t≈102.0

        # Flashcard
        fc = heading("SMS = phishable · SIM-swappable · interceptable", size=22, color=RED)
        fc_box = SurroundingRectangle(fc, color=RED, buff=0.2, corner_radius=0.14)
        fc.move_to(DOWN * 1.9)
        fc_box.move_to(DOWN * 1.9)
        self.play(Write(fc), Create(fc_box), run_time=0.7)                  # t≈102.7
        self.wait(4.0)                                                      # t≈106.7

        elapsed = 106.7
        self._pad("s3", elapsed)
        fade_all(self)

    # ── SCENE 4 — MFA Strength Ladder (~90 s) ────────────────────
    def s4_mfa_ladder(self):
        self._sound("s4")

        stitle = scene_title(self, "The MFA Strength Ladder", color=GREEN) # t≈0.7
        self.wait(0.5)                                                      # t≈1.2

        levels = [
            ("1  SMS / Voice Codes",
             "Better than nothing — phishable, SIM-swappable",
             RED,   DOWN * 2.3),
            ("2  TOTP Authenticator Apps",
             "On-device codes — immune to SIM swap, but still phishable via relay",
             AMBER, DOWN * 0.7),
            ("3  Push w/ Number Matching",
             "Resists basic phishing — vulnerable to push bombing / MFA fatigue",
             BLUE,  UP   * 0.9),
            ("4  FIDO2 / WebAuthn / Passkeys",
             "Phishing-resistant — cryptographically bound to the real site",
             GREEN, UP   * 2.5),
        ]

        dwell_times = [14.0, 12.0, 14.0, 16.0]
        elapsed = 1.2
        level_cards = []

        for (title_str, desc_str, color, ypos), dwell in zip(levels, dwell_times):
            bar = Rectangle(width=12.0, height=1.08,
                            color=color, fill_color=BG,
                            fill_opacity=0.92, stroke_width=2)
            bar.move_to(ypos)
            title_mob = Text(title_str, font_size=20, color=color, weight=BOLD)
            title_mob.move_to(bar.get_left() + RIGHT * 2.9)
            vdiv = Line(UP*0.38, DOWN*0.38, color=color,
                        stroke_width=1, stroke_opacity=0.4)
            vdiv.move_to(bar.get_left() + RIGHT * 5.3)
            desc_mob = Text(desc_str, font_size=15, color=WHITE, line_spacing=1.2)
            desc_mob.move_to(bar.get_left() + RIGHT * 8.8)
            card = VGroup(bar, title_mob, vdiv, desc_mob)
            level_cards.append(card)

            self.play(FadeIn(card, shift=RIGHT*0.3), run_time=0.6)
            self.wait(dwell)
            elapsed += 0.6 + dwell
        # elapsed ≈ 1.2 + 57.6 + 4*0.6 = 61.2

        # FIDO2 explanation callout
        fido_bg = RoundedRectangle(corner_radius=0.16, width=11.2, height=1.35,
                                    color=GREEN, fill_color="#05140A",
                                    fill_opacity=1, stroke_width=2)
        fido_bg.to_edge(DOWN, buff=0.28)
        fido_txt = Text(
            "Why FIDO2 beats phishing: the key validates the website's actual origin.\n"
            "The human can be fooled. The cryptography cannot.",
            font_size=18, color=WHITE, line_spacing=1.35
        )
        fido_txt.move_to(fido_bg.get_center())
        self.play(FadeIn(fido_bg), Write(fido_txt), run_time=0.9)           # t≈62.1
        self.wait(8.0)                                                      # t≈70.1
        self.play(FadeOut(fido_bg), FadeOut(fido_txt), run_time=0.35)       # t≈70.5

        # Push bombing callout
        pb_bg = RoundedRectangle(corner_radius=0.16, width=9.5, height=0.82,
                                  color=AMBER, fill_color="#1A0D00",
                                  fill_opacity=1, stroke_width=2)
        pb_bg.to_edge(DOWN, buff=0.38)
        pb_txt = Text(
            "Push Bombing / MFA Fatigue — EXAM TERM: attacker floods approvals hoping you accept",
            font_size=17, color=AMBER, weight=BOLD
        )
        pb_txt.move_to(pb_bg.get_center())
        self.play(FadeIn(pb_bg), Write(pb_txt), run_time=0.7)               # t≈71.2
        self.wait(5.0)                                                      # t≈76.2

        elapsed = 76.2
        self._pad("s4", elapsed)
        fade_all(self)

    # ── SCENE 5 — Exam Tie-In (~30 s) ────────────────────────────
    def s5_exam_tie_in(self):
        self._sound("s5")

        stitle = scene_title(self, "Exam Prep", color=AMBER)               # t≈0.7
        self.wait(0.3)                                                      # t≈1.0

        terms = [
            ("Three factor categories",     "know them cold — spot the same-factor trap",     WHITE),
            ("SMS = weakest MFA",            "SIM swap + SS7 + phishing relay",                RED),
            ("TOTP",                         "time-based one-time password, generated on-device", BLUE),
            ("Push Bombing / MFA Fatigue",   "attacker floods push requests to force acceptance", AMBER),
            ("FIDO2 / WebAuthn / Passkeys",  "phishing-resistant, cryptographically bound",     GREEN),
            ("NIST SP 800-63B",              "SMS flagged RESTRICTED — know this reference",    AMBER),
        ]

        elapsed = 1.0
        for i, (term, desc, color) in enumerate(terms):
            term_mob = Text(f"  {term}", font_size=20, color=color, weight=BOLD)
            desc_mob = Text(f"    {desc}", font_size=16, color=WHITE)
            row = VGroup(term_mob, desc_mob).arrange(DOWN, buff=0.06, aligned_edge=LEFT)
            row.move_to(UP * (2.4 - i * 0.82))
            row.to_edge(LEFT, buff=0.7)
            self.play(FadeIn(row, shift=RIGHT*0.25), run_time=0.3)
            elapsed += 0.3
        # elapsed ≈ 2.8

        self.wait(2.5)                                                      # t≈5.3
        fade_all(self, run_time=0.4)

        # Sample question
        q_bg = RoundedRectangle(corner_radius=0.2, width=11.5, height=1.6,
                                 color=BLUE, fill_color="#00101A",
                                 fill_opacity=1, stroke_width=2)
        q_bg.move_to(UP * 1.1)
        q_txt = Text(
            "A user authenticates with a password and a 4-digit PIN.\n"
            "How many factors is this?",
            font_size=22, color=WHITE, line_spacing=1.35
        )
        q_txt.move_to(q_bg.get_center())
        self.play(FadeIn(q_bg), Write(q_txt), run_time=0.8)                 # t≈6.5
        self.wait(3.5)                                                      # t≈10.0  ← dramatic pause

        ans_bg = RoundedRectangle(corner_radius=0.18, width=6.5, height=1.05,
                                   color=RED, fill_color="#1A0000",
                                   fill_opacity=1, stroke_width=2.5)
        ans_bg.move_to(DOWN * 1.0)
        ans_txt = Text("ONE factor — both are something you know.",
                       font_size=22, color=WHITE, weight=BOLD)
        ans_txt.move_to(ans_bg.get_center())
        self.play(FadeIn(ans_bg, scale=0.8), Write(ans_txt), run_time=0.7)  # t≈10.7
        self.play(
            Flash(ans_bg.get_center(), color=RED, num_lines=8, flash_radius=0.9),
            run_time=0.5
        )                                                                   # t≈11.2
        self.wait(3.0)                                                      # t≈14.2

        elapsed = 14.2
        self._pad("s5", elapsed)
        fade_all(self)

    # ── SCENE 6 — End Card (~45 s) ────────────────────────────────
    def s6_end_card(self):
        self._sound("s6")

        stitle = scene_title(self, "Think Like A CISSP", color=BLUE)       # t≈0.7
        self.wait(0.4)                                                      # t≈1.1

        book_desc = Text(
            "A mindset guide for thinking the way the exam wants you to think.\n"
            "Not just definitions — exam strategy.",
            font_size=21, color=WHITE, line_spacing=1.4
        )
        book_desc.move_to(UP * 0.6)
        self.play(FadeIn(book_desc, shift=UP*0.1), run_time=0.6)            # t≈1.7

        price_bg = RoundedRectangle(corner_radius=0.16, width=1.55, height=0.55,
                                    fill_color=AMBER, fill_opacity=1, stroke_width=0)
        price_txt = Text("$25.00", font_size=18, color=BG, weight=BOLD)
        price_txt.move_to(price_bg.get_center())
        price_grp = VGroup(price_bg, price_txt)

        avail_lbl = Text("Available at:", font_size=17, color="#AAAAAA")
        avail_url = mono("zerodaylabs.tech/store/think-like-a-cissp", size=17, color=BLUE)
        avail_row = VGroup(avail_lbl, avail_url, price_grp).arrange(RIGHT, buff=0.28)
        avail_row.next_to(book_desc, DOWN, buff=0.38)
        self.play(FadeIn(avail_row), run_time=0.5)                          # t≈2.2
        self.wait(5.0)                                                      # t≈7.2
        self.play(FadeOut(book_desc), FadeOut(avail_row), run_time=0.4)     # t≈7.6

        # Website CTA
        cta_head = heading("Ready to prep smarter?", size=36, color=WHITE)
        cta_head.move_to(UP * 1.5)
        self.play(Write(cta_head), run_time=0.7)                            # t≈8.3

        cta_body = Text(
            "Adaptive practice exams that learn your weak spots\n"
            "and drill you on what matters — Security+  ·  CISSP",
            font_size=20, color=WHITE, line_spacing=1.4
        )
        cta_body.next_to(cta_head, DOWN, buff=0.32)
        self.play(FadeIn(cta_body, shift=UP*0.1), run_time=0.6)             # t≈8.9

        url_bg = RoundedRectangle(corner_radius=0.22, width=5.4, height=0.72,
                                   color=GREEN, fill_color="#051A0A",
                                   fill_opacity=1, stroke_width=2)
        url_txt = Text("www.zerodaylabs.tech", font=MONO,
                       font_size=24, color=GREEN, weight=BOLD)
        url_txt.move_to(url_bg.get_center())
        url_grp = VGroup(url_bg, url_txt)
        url_grp.next_to(cta_body, DOWN, buff=0.38)
        self.play(FadeIn(url_grp, scale=0.88), run_time=0.6)                # t≈9.5
        self.play(url_bg.animate.set_stroke(color=WHITE, width=2.5), run_time=0.3)
        self.play(url_bg.animate.set_stroke(color=GREEN, width=2), run_time=0.3)  # t≈10.1

        thanks = Text("Thanks for watching — like, subscribe, and share!",
                      font_size=20, color=AMBER)
        tagline = Text("Train.  Test.  Certify.", font_size=18, color=BLUE, weight=BOLD)
        footer = VGroup(thanks, tagline).arrange(DOWN, buff=0.14)
        footer.to_edge(DOWN, buff=0.42)
        self.play(FadeIn(footer), run_time=0.5)                             # t≈10.6

        elapsed = 10.6
        self._pad("s6", elapsed)

        black = Rectangle(
            width=config.frame_width + 1,
            height=config.frame_height + 1,
            fill_color=BLACK, fill_opacity=0, stroke_width=0,
        )
        self.add(black)
        self.play(black.animate.set_fill(opacity=1), run_time=1.8)
        self.wait(0.4)
