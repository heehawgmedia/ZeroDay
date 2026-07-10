"""
CISSP Domain Mastery — YouTube Shorts v2
Enhanced theme, animations, and readability (1080 × 1920 / 9:16)

Render:
    manim -qh cissp_shorts.py CIATriad
    manim -qh cissp_shorts.py DataClassification
    manim -qh cissp_shorts.py ZeroTrust
    manim -qh cissp_shorts.py IncidentResponse
    manim -qh cissp_shorts.py ExamTraps
    manim -qh cissp_shorts.py RiskManagement
    manim -qh cissp_shorts.py AccessControlModels
    manim -qh cissp_shorts.py AuthenticationFactors
    manim -qh cissp_shorts.py Cryptography
    manim -qh cissp_shorts.py MalwareTypes
    manim -qh cissp_shorts.py OSIModel
    manim -qh cissp_shorts.py FirewallTypes
    manim -qh cissp_shorts.py CommonPorts
    manim -qh cissp_shorts.py WirelessSecurity
    manim -qh cissp_shorts.py VPNandIPsec
    manim -qh cissp_shorts.py NetworkAttacks
    manim -qh cissp_shorts.py BCPvsDRP
    manim -qh cissp_shorts.py RAIDLevels
    manim -qh cissp_shorts.py SecurityModels
    manim -qh cissp_shorts.py CloudModels
"""
from __future__ import annotations
import json, os
from manim import *

config.pixel_width  = 1080
config.pixel_height = 1920
config.frame_height = 16.0
config.frame_width  = 9.0

# ── Palette ───────────────────────────────────────────────────────────────────
BG      = "#060B14"   # deep blue-black
SURFACE = "#0D1826"   # card fill
BLUE    = "#0099FF"   # electric blue
AMBER   = "#FFB300"   # amber gold
GREEN   = "#00E676"   # green
RED     = "#FF5252"   # red
GRAY    = "#7A8FA6"   # muted text
WHITE   = "#FFFFFF"
TEAL    = "#00E5CC"

AUDIO = "cissp_shorts_audio"

_OrigText = Text
class Text(_OrigText):
    def __init__(self, *a, **kw):
        kw.setdefault("font", "DejaVu Sans")
        super().__init__(*a, **kw)


def _load_dur():
    p = os.path.join(AUDIO, "durations.json")
    return json.load(open(p)) if os.path.exists(p) else {}

DUR = _load_dur()


# ═════════════════════════════════════════════════════════════════════════════
# BASE CLASS
# ═════════════════════════════════════════════════════════════════════════════
class _Short(Scene):
    ID = "c0"

    def setup(self):
        self.camera.background_color = BG

    # ── Background + UI chrome ────────────────────────────────────────────────
    def _bg(self):
        bg = Rectangle(width=10, height=18,
                       fill_color=BG, fill_opacity=1, stroke_width=0)
        self.add(bg)
        # subtle dot grid
        for x in range(-4, 5):
            for y in range(-7, 8, 2):
                d = Dot(radius=0.03, color=BLUE, fill_opacity=0.22)
                d.move_to(RIGHT * x + UP * y)
                self.add(d)
        # corner bracket chrome
        for h, v in self._corners():
            self.add(h, v)
        return bg

    def _corners(self, s=0.55):
        out = []
        for cx, cy, hd, vd in [
            (-4.25,  7.7,  1, -1),
            ( 4.25,  7.7, -1, -1),
            (-4.25, -7.7,  1,  1),
            ( 4.25, -7.7, -1,  1),
        ]:
            h = Line([cx, cy, 0], [cx + hd*s, cy, 0],
                     stroke_width=2.5, color=BLUE, stroke_opacity=0.55)
            v = Line([cx, cy, 0], [cx, cy + vd*s, 0],
                     stroke_width=2.5, color=BLUE, stroke_opacity=0.55)
            out.append((h, v))
        return out

    # ── Brand badge ───────────────────────────────────────────────────────────
    def _brand(self):
        badge = RoundedRectangle(corner_radius=0.14, width=5.0, height=0.76,
                                 color=BLUE, fill_color="#050A13",
                                 fill_opacity=0.95, stroke_width=1.5)
        badge.move_to(UP * 7.2)
        lbl = Text("ZERO DAY LABS", font_size=24, color=BLUE, weight=BOLD)
        lbl.move_to(badge.get_center())
        dot_l = Dot(radius=0.07, color=BLUE).next_to(lbl, LEFT, buff=0.2)
        dot_r = Dot(radius=0.07, color=AMBER).next_to(lbl, RIGHT, buff=0.2)
        return VGroup(badge, lbl, dot_l, dot_r)

    # ── Scene title ───────────────────────────────────────────────────────────
    def _scene_title(self, text, color=BLUE):
        accent = Rectangle(width=0.22, height=0.96,
                           fill_color=color, fill_opacity=1, stroke_width=0)
        t = Text(text, font_size=36, color=color, weight=BOLD)
        row = VGroup(accent, t).arrange(RIGHT, buff=0.22)
        row.move_to(UP * 5.85)
        bar = Line(LEFT*4.1, RIGHT*4.1, color=color,
                   stroke_width=1.5, stroke_opacity=0.55)
        bar.next_to(row, DOWN, buff=0.2)
        return VGroup(row, bar)

    # ── Glowing card (returns glow + card separately for animation) ───────────
    def _glow_card(self, width, height, color):
        glow = RoundedRectangle(corner_radius=0.24,
                                width=width + 0.2, height=height + 0.16,
                                color=color, fill_color=color,
                                fill_opacity=0.10, stroke_width=0)
        card = RoundedRectangle(corner_radius=0.2, width=width, height=height,
                                color=color, fill_color=SURFACE,
                                fill_opacity=0.98, stroke_width=2.8)
        return glow, card

    # ── Audio helpers ─────────────────────────────────────────────────────────
    def _sound(self, key):
        try:
            self._t0 = self.time
        except AttributeError:
            self._t0 = 0.0
        self.add_sound(f"{AUDIO}/{self.ID}_{key}.mp3")

    def _pad(self, key):
        try:
            used = self.time - getattr(self, "_t0", 0.0)
        except AttributeError:
            used = 0.0
        rem = DUR.get(f"{self.ID}_{key}", 0) - used - 0.3
        if rem > 0:
            self.wait(rem)

    # ── Exam tip ──────────────────────────────────────────────────────────────
    def _exam_tip(self, text):
        bg = RoundedRectangle(corner_radius=0.14, width=8.4, height=1.22,
                              color=RED, fill_color="#14000A",
                              fill_opacity=1, stroke_width=2.2)
        bg.move_to(DOWN * 4.55)
        bar = Rectangle(width=0.18, height=0.92,
                        fill_color=RED, fill_opacity=1, stroke_width=0)
        label = Text("EXAM TIP", font_size=13, color=RED, weight=BOLD)
        body  = Text(text, font_size=13, color=WHITE)
        inner = VGroup(bar,
                       VGroup(label, body).arrange(DOWN, buff=0.06,
                                                   aligned_edge=LEFT)
                       ).arrange(RIGHT, buff=0.2)
        inner.move_to(bg.get_center())
        return VGroup(bg, inner)

    # ── Fade / clear scene ────────────────────────────────────────────────────
    def _fade_all(self, run_time=0.3):
        mobs = list(self.mobjects)
        if mobs:
            self.play(*[FadeOut(m) for m in mobs], run_time=run_time)
        self.clear()

    # ── CTA section ───────────────────────────────────────────────────────────
    def _cta_section(self, headline):
        self._fade_all(0.3)
        self._bg()
        self.add(self._brand())
        self._sound("c")

        hl = Text(headline, font_size=36, color=WHITE, weight=BOLD,
                  line_spacing=1.2)
        hl.move_to(UP * 3.1)
        self.play(Write(hl), run_time=0.7)

        # Pulsing amber site button
        site_bg = RoundedRectangle(corner_radius=0.24, width=6.2, height=1.02,
                                   fill_color=AMBER, fill_opacity=1,
                                   stroke_width=0)
        site_bg.next_to(hl, DOWN, buff=0.55)
        site_txt = Text("zerodaylabs.tech", font_size=28, color=BG, weight=BOLD)
        site_txt.move_to(site_bg.get_center())
        self.play(GrowFromCenter(site_bg), run_time=0.4)
        self.play(Write(site_txt), run_time=0.35)
        self.play(Flash(site_bg, color=AMBER, flash_radius=0.9,
                        num_lines=10, line_length=0.22), run_time=0.4)

        cta = Text("LIKE  ·  SUBSCRIBE  ·  SHARE",
                   font_size=24, color=BLUE, weight=BOLD)
        cta.move_to(DOWN * 1.6)
        self.play(FadeIn(cta, scale=1.08), run_time=0.4)

        sub = Text("Daily CISSP & Security+ exam tips", font_size=16, color=GRAY)
        sub.next_to(cta, DOWN, buff=0.3)
        self.play(FadeIn(sub), run_time=0.3)

        self._pad("c")


# ═════════════════════════════════════════════════════════════════════════════
# SHORT 1 — CIA TRIAD
# ═════════════════════════════════════════════════════════════════════════════
class CIATriad(_Short):
    ID = "c1"

    def construct(self):
        # ── Hook ──────────────────────────────────────────────────────────────
        self._bg()
        self.add(self._brand())
        self._sound("h")

        miss = Text("Most candidates miss this.", font_size=28, color=GRAY)
        miss.move_to(UP * 4.5)
        self.play(FadeIn(miss, shift=DOWN * 0.15), run_time=0.4)

        # C / I / A circles grow in sequence
        def _letter_icon(letter, color, r=0.65):
            circ  = Circle(radius=r, color=color, fill_color=color,
                           fill_opacity=0.18, stroke_width=3)
            outer = Circle(radius=r + 0.1, color=color,
                           fill_opacity=0, stroke_width=1, stroke_opacity=0.4)
            lbl = Text(letter, font_size=44, color=color, weight=BOLD)
            lbl.move_to(circ.get_center())
            return VGroup(outer, circ, lbl)

        c_icon = _letter_icon("C", BLUE)
        i_icon = _letter_icon("I", GREEN)
        a_icon = _letter_icon("A", AMBER)
        icons  = VGroup(c_icon, i_icon, a_icon).arrange(RIGHT, buff=0.45)
        icons.move_to(UP * 2.0)

        for icon in [c_icon, i_icon, a_icon]:
            self.play(GrowFromCenter(icon), run_time=0.32)

        self.play(
            Flash(c_icon, color=BLUE,  flash_radius=0.9, num_lines=8, line_length=0.2),
            Flash(i_icon, color=GREEN, flash_radius=0.9, num_lines=8, line_length=0.2),
            Flash(a_icon, color=AMBER, flash_radius=0.9, num_lines=8, line_length=0.2),
            run_time=0.4,
        )

        triad = Text("TRIAD", font_size=56, color=WHITE, weight=BOLD)
        triad.next_to(icons, DOWN, buff=0.35)
        self.play(Write(triad), run_time=0.5)

        go = Text("30 seconds. Let's go.", font_size=22, color=AMBER)
        go.next_to(triad, DOWN, buff=0.35)
        self.play(FadeIn(go, shift=UP * 0.1), run_time=0.35)
        self._pad("h")

        # ── Main ──────────────────────────────────────────────────────────────
        self._fade_all(0.3)
        self._bg()
        self.add(self._brand())
        title = self._scene_title("CIA TRIAD")
        self.play(Write(title), run_time=0.5)
        self._sound("m")

        pillars = [
            ("C", "CONFIDENTIALITY",
             "Authorized access only.\nEncrypt  ·  ACLs  ·  Need-to-Know", BLUE),
            ("I", "INTEGRITY",
             "Data must not be altered.\nHash  ·  Sign  ·  Checksum",        GREEN),
            ("A", "AVAILABILITY",
             "Systems up when needed.\nRedundancy  ·  Backups  ·  Failover", AMBER),
        ]

        cards = []
        for letter, title_str, body, color in pillars:
            glow, card = self._glow_card(8.2, 2.72, color)
            circ = Circle(radius=0.50, color=color, fill_color=color,
                          fill_opacity=0.18, stroke_width=2.8)
            circ.move_to(card.get_left() + RIGHT * 0.76)
            ltr = Text(letter, font_size=36, color=color, weight=BOLD)
            ltr.move_to(circ.get_center())
            ctitle = Text(title_str, font_size=20, color=color, weight=BOLD)
            cbody  = Text(body, font_size=14, color=WHITE, line_spacing=1.35)
            content = VGroup(ctitle, cbody).arrange(DOWN, buff=0.1,
                                                    aligned_edge=LEFT)
            content.next_to(circ, RIGHT, buff=0.3)
            content.set_y(circ.get_y())
            cards.append(VGroup(glow, card, circ, ltr, content))

        card_grp = VGroup(*cards).arrange(DOWN, buff=0.28)
        card_grp.move_to(UP * 0.38)

        for grp in cards:
            glow, card, circ, ltr, content = grp
            self.play(
                FadeIn(glow),
                DrawBorderThenFill(card),
                GrowFromCenter(circ),
                run_time=0.45,
            )
            self.play(
                Write(ltr),
                Write(content[0]),      # title
                FadeIn(content[1], shift=RIGHT * 0.1),  # body
                run_time=0.38,
            )
            self.play(
                ShowPassingFlash(
                    card.copy().set_stroke(WHITE, width=4, opacity=0.5),
                    time_width=0.45,
                ),
                run_time=0.4,
            )
            self.wait(9.0)

        tip = self._exam_tip("Control fails? Identify which pillar is violated — that's your answer.")
        self.play(FadeIn(tip, scale=0.94), run_time=0.4)
        self.play(Flash(tip, color=RED, flash_radius=0.6,
                        num_lines=8, line_length=0.15), run_time=0.35)
        self.wait(5.0)
        self._pad("m")

        # ── CTA ───────────────────────────────────────────────────────────────
        self._cta_section("Master the CIA Triad.\nMaster the CISSP.")


# ═════════════════════════════════════════════════════════════════════════════
# SHORT 2 — DATA CLASSIFICATION
# ═════════════════════════════════════════════════════════════════════════════
class DataClassification(_Short):
    ID = "c2"

    def construct(self):
        # ── Hook ──────────────────────────────────────────────────────────────
        self._bg()
        self.add(self._brand())
        self._sound("h")

        q = Text("Which data needs\nthe MOST protection?",
                 font_size=40, color=WHITE, weight=BOLD, line_spacing=1.2)
        q.move_to(UP * 2.8)
        self.play(Write(q), run_time=0.75)

        # "CLASSIFIED" stamp
        stamp_bg = RoundedRectangle(corner_radius=0.1, width=5.8, height=1.1,
                                    color=RED, fill_color=RED,
                                    fill_opacity=0.14, stroke_width=3)
        stamp_txt = Text("CLASSIFIED", font_size=46, color=RED, weight=BOLD)
        stamp = VGroup(stamp_bg, stamp_txt)
        stamp.next_to(q, DOWN, buff=0.5)
        self.play(GrowFromCenter(stamp), run_time=0.4)
        self.play(Flash(stamp, color=RED, flash_radius=1.2,
                        num_lines=8, line_length=0.22), run_time=0.35)

        sub = Text("Know these 4 levels cold.", font_size=24, color=AMBER)
        sub.next_to(stamp, DOWN, buff=0.4)
        self.play(FadeIn(sub, shift=UP * 0.1), run_time=0.35)
        self._pad("h")

        # ── Main ──────────────────────────────────────────────────────────────
        self._fade_all(0.3)
        self._bg()
        self.add(self._brand())
        title = self._scene_title("DATA CLASSIFICATION")
        self.play(Write(title), run_time=0.5)
        self._sound("m")

        tiers = [
            ("CONFIDENTIAL", "National security  ·  Crypto keys",
             "Maximum access controls.", RED),
            ("SENSITIVE",    "PII  ·  Medical records  ·  Trade secrets",
             "Significant breach impact.", AMBER),
            ("PRIVATE",      "Employee records  ·  Internal financials",
             "Internal access only.", BLUE),
            ("PUBLIC",       "Press releases  ·  Website content",
             "No harm if disclosed.", GRAY),
        ]

        blocks = []
        for label, examples, note, color in tiers:
            glow, blk = self._glow_card(8.2, 1.92, color)
            lbl = Text(label, font_size=22, color=color, weight=BOLD)
            lbl.move_to(blk.get_left() + RIGHT * 1.35)
            ex  = Text(examples, font_size=12, color=GRAY)
            nt  = Text(note, font_size=14, color=WHITE, weight=BOLD)
            right = VGroup(ex, nt).arrange(DOWN, buff=0.08, aligned_edge=LEFT)
            right.next_to(lbl, RIGHT, buff=0.28)
            right.set_y(lbl.get_y())
            blocks.append(VGroup(glow, blk, lbl, right))

        blk_grp = VGroup(*blocks).arrange(DOWN, buff=0.2)
        blk_grp.move_to(UP * 0.6)

        for grp in blocks:
            glow, blk, lbl, right = grp
            self.play(
                FadeIn(glow),
                DrawBorderThenFill(blk),
                run_time=0.4,
            )
            self.play(
                Write(lbl),
                FadeIn(right, shift=RIGHT * 0.15),
                run_time=0.35,
            )
            self.play(
                ShowPassingFlash(
                    blk.copy().set_stroke(WHITE, width=4, opacity=0.4),
                    time_width=0.5,
                ),
                run_time=0.4,
            )
            self.wait(8.0)

        tip = self._exam_tip("Owner classifies  ·  Always classify at HIGHEST sensitivity level.")
        self.play(FadeIn(tip, scale=0.94), run_time=0.4)
        self.play(Flash(tip, color=RED, flash_radius=0.6,
                        num_lines=8, line_length=0.15), run_time=0.35)
        self.wait(5.0)
        self._pad("m")

        # ── CTA ───────────────────────────────────────────────────────────────
        self._cta_section("Know your data.\nPass the exam.")


# ═════════════════════════════════════════════════════════════════════════════
# SHORT 3 — ZERO TRUST
# ═════════════════════════════════════════════════════════════════════════════
class ZeroTrust(_Short):
    ID = "c3"

    def construct(self):
        # ── Hook ──────────────────────────────────────────────────────────────
        self._bg()
        self.add(self._brand())
        self._sound("h")

        never  = Text("NEVER TRUST,",  font_size=46, color=RED,  weight=BOLD)
        always = Text("ALWAYS VERIFY.", font_size=46, color=BLUE, weight=BOLD)
        motto  = VGroup(never, always).arrange(DOWN, buff=0.22)
        motto.move_to(UP * 2.0)
        self.play(Write(never),  run_time=0.5)
        self.play(Write(always), run_time=0.5)
        self.play(
            Flash(always, color=BLUE, flash_radius=1.1,
                  num_lines=10, line_length=0.22),
            run_time=0.4,
        )

        sub = Text("Here's what that means for your exam.", font_size=20, color=AMBER)
        sub.next_to(motto, DOWN, buff=0.5)
        self.play(FadeIn(sub, shift=UP * 0.1), run_time=0.35)
        self._pad("h")

        # ── Main ──────────────────────────────────────────────────────────────
        self._fade_all(0.3)
        self._bg()
        self.add(self._brand())
        title = self._scene_title("ZERO TRUST MODEL")
        self.play(Write(title), run_time=0.5)
        self._sound("m")

        # Old vs Zero Trust comparison
        glow_old, old_bg = self._glow_card(3.9, 2.55, GRAY)
        glow_old.move_to(LEFT * 2.1 + UP * 3.55)
        old_bg.move_to(LEFT * 2.1  + UP * 3.55)
        old_lbl  = Text("OLD MODEL", font_size=16, color=GRAY, weight=BOLD)
        old_lbl.move_to(old_bg.get_top() + DOWN * 0.3)
        old_body = Text("Castle + Moat\nInside = Trusted\nLateral movement\nfree after breach",
                        font_size=12, color=GRAY, line_spacing=1.25)
        old_body.move_to(old_bg.get_center() + DOWN * 0.22)

        glow_zt, zt_bg = self._glow_card(3.9, 2.55, BLUE)
        glow_zt.move_to(RIGHT * 2.1 + UP * 3.55)
        zt_bg.move_to(RIGHT * 2.1  + UP * 3.55)
        zt_lbl  = Text("ZERO TRUST", font_size=16, color=BLUE, weight=BOLD)
        zt_lbl.move_to(zt_bg.get_top() + DOWN * 0.3)
        zt_body = Text("Verify everyone\nMinimum access\nAssume breach\nAlways verify",
                       font_size=12, color=WHITE, line_spacing=1.25)
        zt_body.move_to(zt_bg.get_center() + DOWN * 0.22)

        old_card = VGroup(glow_old, old_bg, old_lbl, old_body)
        zt_card  = VGroup(glow_zt,  zt_bg,  zt_lbl,  zt_body)

        self.play(FadeIn(glow_old), DrawBorderThenFill(old_bg),
                  FadeIn(old_lbl), FadeIn(old_body), run_time=0.5)
        self.play(FadeIn(glow_zt),  DrawBorderThenFill(zt_bg),
                  FadeIn(zt_lbl),  FadeIn(zt_body),  run_time=0.5)
        self.wait(5.5)

        # Cross out old model
        x1 = Line(old_bg.get_corner(UL) + RIGHT*0.1 + DOWN*0.08,
                  old_bg.get_corner(DR) + LEFT*0.1  + UP*0.08,
                  color=RED, stroke_width=3.5)
        x2 = Line(old_bg.get_corner(UR) + LEFT*0.1  + DOWN*0.08,
                  old_bg.get_corner(DL) + RIGHT*0.1 + UP*0.08,
                  color=RED, stroke_width=3.5)
        self.play(
            Create(x1), Create(x2),
            old_card.animate.set_opacity(0.32),
            run_time=0.45,
        )
        self.play(Flash(zt_card, color=BLUE, flash_radius=1.3,
                        num_lines=10, line_length=0.2), run_time=0.4)
        self.wait(2.0)

        # Three principles
        p_label = Text("3 CORE PRINCIPLES", font_size=22, color=AMBER, weight=BOLD)
        p_label.move_to(UP * 1.25)
        self.play(Write(p_label), run_time=0.4)

        principles = [
            ("1  VERIFY EXPLICITLY",
             "Auth every request  ·  Every time", BLUE),
            ("2  LEAST PRIVILEGE",
             "Min access  ·  Just enough  ·  Just in time", GREEN),
            ("3  ASSUME BREACH",
             "Segment  ·  Monitor  ·  Limit blast radius", RED),
        ]

        p_cards = []
        for title_str, body, color in principles:
            glow, card = self._glow_card(8.2, 1.52, color)
            ptitle = Text(title_str, font_size=18, color=color, weight=BOLD)
            pbody  = Text(body, font_size=13, color=WHITE)
            pc = VGroup(ptitle, pbody).arrange(DOWN, buff=0.1, aligned_edge=LEFT)
            pc.move_to(card.get_center() + LEFT * 0.5)
            p_cards.append(VGroup(glow, card, pc))

        p_grp = VGroup(*p_cards).arrange(DOWN, buff=0.2)
        p_grp.move_to(DOWN * 1.3)

        for pc in p_cards:
            glow, card, content = pc
            self.play(FadeIn(glow), DrawBorderThenFill(card),
                      FadeIn(content, shift=RIGHT * 0.15), run_time=0.42)
            self.wait(7.5)

        tip = self._exam_tip("Zero Trust removes implicit trust — even for internal users.")
        self.play(FadeIn(tip, scale=0.94), run_time=0.4)
        self.play(Flash(tip, color=RED, flash_radius=0.6,
                        num_lines=8, line_length=0.15), run_time=0.35)
        self.wait(4.0)
        self._pad("m")

        # ── CTA ───────────────────────────────────────────────────────────────
        self._cta_section("Never Trust.\nAlways Verify.")


# ═════════════════════════════════════════════════════════════════════════════
# SHORT 4 — INCIDENT RESPONSE
# ═════════════════════════════════════════════════════════════════════════════
class IncidentResponse(_Short):
    ID = "c4"

    def construct(self):
        # ── Hook ──────────────────────────────────────────────────────────────
        self._bg()
        self.add(self._brand())
        self._sound("h")

        big_six = Text("6", font_size=130, color=BLUE, weight=BOLD)
        big_six.move_to(UP * 2.2)
        self.play(GrowFromCenter(big_six), run_time=0.5)
        self.play(Flash(big_six, color=BLUE, flash_radius=1.8,
                        num_lines=12, line_length=0.3), run_time=0.4)

        sub1 = Text("PHASES", font_size=48, color=WHITE, weight=BOLD)
        sub1.next_to(big_six, DOWN, buff=0.15)
        sub2 = Text("NIST Incident Response", font_size=24, color=GRAY)
        sub2.next_to(sub1, DOWN, buff=0.25)
        sub3 = Text("Memorize the ORDER.", font_size=22, color=AMBER, weight=BOLD)
        sub3.next_to(sub2, DOWN, buff=0.18)
        self.play(Write(sub1), run_time=0.4)
        self.play(FadeIn(sub2), FadeIn(sub3), run_time=0.4)
        self._pad("h")

        # ── Main ──────────────────────────────────────────────────────────────
        self._fade_all(0.3)
        self._bg()
        self.add(self._brand())
        title = self._scene_title("INCIDENT RESPONSE")
        self.play(Write(title), run_time=0.5)
        self._sound("m")

        steps = [
            ("1", "PREPARATION",
             "Policies  ·  Tools  ·  Training — BEFORE incident.", BLUE),
            ("2", "DETECTION & ANALYSIS",
             "Identify breach  ·  Scope & severity.",              GREEN),
            ("3", "CONTAINMENT",
             "Short-term isolation → Long-term.",                   AMBER),
            ("4", "ERADICATION",
             "Remove root cause  ·  Patch  ·  Eliminate.",         RED),
            ("5", "RECOVERY",
             "Restore safely  ·  Monitor for reinfection.",        TEAL),
            ("6", "POST-INCIDENT",
             "Lessons learned within 2 weeks.",                     GRAY),
        ]

        step_cards = []
        for num, name, desc, color in steps:
            glow, card = self._glow_card(8.2, 1.35, color)
            outer = Circle(radius=0.42, color=color,
                           fill_color=color, fill_opacity=0.14, stroke_width=0)
            inner = Circle(radius=0.34, color=color,
                           fill_color=SURFACE, fill_opacity=1, stroke_width=2.5)
            num_txt = Text(num, font_size=20, color=color, weight=BOLD)
            outer.move_to(card.get_left() + RIGHT * 0.55)
            inner.move_to(outer.get_center())
            num_txt.move_to(outer.get_center())
            sname = Text(name, font_size=15, color=color, weight=BOLD)
            sdesc = Text(desc, font_size=12, color=WHITE)
            sc = VGroup(sname, sdesc).arrange(DOWN, buff=0.06, aligned_edge=LEFT)
            sc.next_to(outer, RIGHT, buff=0.22)
            sc.set_y(outer.get_y())
            step_cards.append(VGroup(glow, card, outer, inner, num_txt, sc))

        steps_grp = VGroup(*step_cards).arrange(DOWN, buff=0.16)
        steps_grp.move_to(UP * 0.2)

        for grp in step_cards:
            glow, card, outer, inner, num_txt, sc = grp
            self.play(
                FadeIn(glow),
                DrawBorderThenFill(card),
                GrowFromCenter(VGroup(outer, inner)),
                run_time=0.38,
            )
            self.play(Write(num_txt), FadeIn(sc, shift=RIGHT * 0.1), run_time=0.3)
            self.wait(5.8)

        # Cascade flash to show order flow
        self.play(
            LaggedStart(
                *[Indicate(grp[1], color=WHITE, scale_factor=1.02)
                  for grp in step_cards],
                lag_ratio=0.08,
            ),
            run_time=0.8,
        )

        tip = self._exam_tip("Exam tests ORDER — Preparation ALWAYS comes first.")
        self.play(FadeIn(tip, scale=0.94), run_time=0.4)
        self.play(Flash(tip, color=RED, flash_radius=0.6,
                        num_lines=8, line_length=0.15), run_time=0.35)
        self.wait(4.0)
        self._pad("m")

        # ── CTA ───────────────────────────────────────────────────────────────
        self._cta_section("Know the phases.\nPass the exam.")


# ═════════════════════════════════════════════════════════════════════════════
# SHORT 5 — EXAM TRAPS (MANAGER MINDSET)
# ═════════════════════════════════════════════════════════════════════════════
class ExamTraps(_Short):
    ID = "c5"

    def construct(self):
        # ── Hook ──────────────────────────────────────────────────────────────
        self._bg()
        self.add(self._brand())
        self._sound("h")

        tech = Text("TECHNICAL MINDSET", font_size=38, color=GRAY, weight=BOLD)
        tech.move_to(UP * 3.0)
        self.play(FadeIn(tech, shift=DOWN * 0.15), run_time=0.4)

        strike = Line(
            tech.get_left()  + LEFT  * 0.15,
            tech.get_right() + RIGHT * 0.15,
            color=RED, stroke_width=5,
        )
        self.play(Create(strike), run_time=0.38)
        self.play(tech.animate.set_opacity(0.35), run_time=0.2)

        mgr = Text("MANAGER MINDSET", font_size=42, color=GREEN, weight=BOLD)
        mgr.next_to(tech, DOWN, buff=0.55)
        self.play(Write(mgr), run_time=0.5)
        self.play(Flash(mgr, color=GREEN, flash_radius=1.1,
                        num_lines=10, line_length=0.22), run_time=0.4)

        sub = Text("Here's the mindset shift.", font_size=22, color=AMBER)
        sub.next_to(mgr, DOWN, buff=0.4)
        self.play(FadeIn(sub, shift=UP * 0.1), run_time=0.35)
        self._pad("h")

        # ── Main ──────────────────────────────────────────────────────────────
        self._fade_all(0.3)
        self._bg()
        self.add(self._brand())
        title = self._scene_title("MANAGER MINDSET", color=AMBER)
        self.play(Write(title), run_time=0.5)
        self._sound("m")

        # Column headers + divider
        hdr_w = Text("TECHNICIAN", font_size=20, color=RED,   weight=BOLD)
        hdr_r = Text("MANAGER",    font_size=20, color=GREEN, weight=BOLD)
        hdr_w.move_to(LEFT  * 2.1 + UP * 4.85)
        hdr_r.move_to(RIGHT * 2.1 + UP * 4.85)
        col_div = Line([0, 4.62, 0], [0, -3.9, 0],
                       color=GRAY, stroke_width=0.9, stroke_opacity=0.4)
        self.play(FadeIn(hdr_w), FadeIn(hdr_r), Create(col_div), run_time=0.4)

        rows_data = [
            ("Fix the\ntechnology", "Assess the\nrisk first",  BLUE),
            ("Ignore\nthe law",     "Comply first\nalways",    RED),
            ("Deploy\na tool",      "Train the\npeople first", GREEN),
            ("Save the\ndata",      "Save human\nlives first", AMBER),
        ]

        row_objs    = []
        wrong_texts = []
        for wrong, right, color in rows_data:
            glow, hl = self._glow_card(8.2, 1.38, color)
            w_txt = Text(wrong, font_size=18, color="#CC6666",
                         line_spacing=1.1, weight=BOLD)
            r_txt = Text(right, font_size=18, color=GREEN,
                         line_spacing=1.1, weight=BOLD)
            w_txt.move_to(LEFT  * 2.1)
            r_txt.move_to(RIGHT * 2.1)
            row_objs.append(VGroup(glow, hl, w_txt, r_txt))
            wrong_texts.append(w_txt)

        rows_grp = VGroup(*row_objs).arrange(DOWN, buff=0.18)
        rows_grp.move_to(UP * 1.05)

        for grp in row_objs:
            glow, hl, w_txt, r_txt = grp
            self.play(FadeIn(glow), DrawBorderThenFill(hl),
                      FadeIn(w_txt), FadeIn(r_txt), run_time=0.4)
            self.wait(8.0)

        # Strike through wrong column + highlight right column
        strikes = [
            Line(
                wt.get_corner(UL) + DOWN*0.06,
                wt.get_corner(DR) + UP*0.06,
                color=RED, stroke_width=3,
            )
            for wt in wrong_texts
        ]
        self.play(
            LaggedStart(*[Create(s) for s in strikes], lag_ratio=0.12),
            LaggedStart(*[wt.animate.set_opacity(0.28) for wt in wrong_texts],
                        lag_ratio=0.12),
            run_time=0.6,
        )
        self.play(
            LaggedStart(
                *[Indicate(grp[3], color=GREEN, scale_factor=1.06)
                  for grp in row_objs],
                lag_ratio=0.1,
            ),
            run_time=0.5,
        )

        tip = self._exam_tip("Think like a senior security MANAGER — never an engineer.")
        self.play(FadeIn(tip, scale=0.94), run_time=0.4)
        self.play(Flash(tip, color=RED, flash_radius=0.6,
                        num_lines=8, line_length=0.15), run_time=0.35)
        self.wait(4.0)
        self._pad("m")

        # ── CTA ───────────────────────────────────────────────────────────────
        self._cta_section("Think like a manager.\nPass the CISSP.")


# ═════════════════════════════════════════════════════════════════════════════
# SHORT 6 — RISK MANAGEMENT
# ═════════════════════════════════════════════════════════════════════════════
class RiskManagement(_Short):
    ID = "c6"

    def construct(self):
        # ── Hook ──────────────────────────────────────────────────────────────
        self._bg()
        self.add(self._brand())
        self._sound("h")

        line = Text("Risk isn't a guess.", font_size=40, color=WHITE, weight=BOLD)
        line.move_to(UP * 3.4)
        self.play(Write(line), run_time=0.55)

        fglow, fcard = self._glow_card(7.2, 1.3, AMBER)
        fcard.move_to(UP * 1.3)
        fglow.move_to(UP * 1.3)
        formula = Text("ALE = SLE × ARO", font_size=44, color=AMBER, weight=BOLD)
        formula.move_to(fcard.get_center())
        self.play(FadeIn(fglow), DrawBorderThenFill(fcard), run_time=0.4)
        self.play(Write(formula), run_time=0.5)
        self.play(Flash(fcard, color=AMBER, flash_radius=1.2,
                        num_lines=10, line_length=0.22), run_time=0.4)

        sub = Text("It's math. Let's break it down.", font_size=22, color=GRAY)
        sub.next_to(fcard, DOWN, buff=0.55)
        self.play(FadeIn(sub, shift=UP * 0.1), run_time=0.35)
        self._pad("h")

        # ── Main ──────────────────────────────────────────────────────────────
        self._fade_all(0.3)
        self._bg()
        self.add(self._brand())
        title = self._scene_title("RISK MANAGEMENT", color=AMBER)
        self.play(Write(title), run_time=0.5)
        self._sound("m")

        # Formula strip
        sglow, strip = self._glow_card(8.2, 1.25, AMBER)
        strip.move_to(UP * 4.0)
        sglow.move_to(UP * 4.0)
        f_main = Text("ALE = SLE × ARO", font_size=28, color=AMBER, weight=BOLD)
        f_sub  = Text("Annualized Loss = Single Loss × Annual Rate",
                      font_size=13, color=WHITE)
        f_grp  = VGroup(f_main, f_sub).arrange(DOWN, buff=0.12)
        f_grp.move_to(strip.get_center())
        self.play(FadeIn(sglow), DrawBorderThenFill(strip),
                  FadeIn(f_grp), run_time=0.5)
        self.wait(9.0)

        responses = [
            ("AVOID",    "Stop the risky activity entirely.",            RED),
            ("TRANSFER", "Shift the loss to a third party — insurance.", BLUE),
            ("MITIGATE", "Apply controls to cut impact or likelihood.",  GREEN),
            ("ACCEPT",   "Cost of control exceeds the loss — live with it.", AMBER),
        ]
        cards = []
        for label, desc, color in responses:
            glow, card = self._glow_card(8.2, 1.4, color)
            lbl = Text(label, font_size=21, color=color, weight=BOLD)
            lbl.move_to(card.get_left() + RIGHT * 1.4)
            d = Text(desc, font_size=13, color=WHITE)
            d.next_to(lbl, RIGHT, buff=0.3)
            d.set_y(lbl.get_y())
            cards.append(VGroup(glow, card, lbl, d))

        grp = VGroup(*cards).arrange(DOWN, buff=0.16)
        grp.move_to(DOWN * 0.55)

        for g in cards:
            glow, card, lbl, d = g
            self.play(FadeIn(glow), DrawBorderThenFill(card),
                      Write(lbl), FadeIn(d, shift=RIGHT * 0.12), run_time=0.4)
            self.wait(4.6)

        tip = self._exam_tip("Risk is never zero — what's left after controls is RESIDUAL risk.")
        self.play(FadeIn(tip, scale=0.94), run_time=0.4)
        self.play(Flash(tip, color=RED, flash_radius=0.6,
                        num_lines=8, line_length=0.15), run_time=0.35)
        self.wait(4.0)
        self._pad("m")

        # ── CTA ───────────────────────────────────────────────────────────────
        self._cta_section("Quantify the risk.\nPass the CISSP.")


# ═════════════════════════════════════════════════════════════════════════════
# SHORT 7 — ACCESS CONTROL MODELS
# ═════════════════════════════════════════════════════════════════════════════
class AccessControlModels(_Short):
    ID = "c7"

    def construct(self):
        # ── Hook ──────────────────────────────────────────────────────────────
        self._bg()
        self.add(self._brand())
        self._sound("h")

        q = Text("Who decides\nwho gets access?",
                 font_size=40, color=WHITE, weight=BOLD, line_spacing=1.2)
        q.move_to(UP * 2.9)
        self.play(Write(q), run_time=0.7)

        four = Text("4 MODELS", font_size=52, color=BLUE, weight=BOLD)
        four.next_to(q, DOWN, buff=0.5)
        self.play(GrowFromCenter(four), run_time=0.4)
        self.play(Flash(four, color=BLUE, flash_radius=1.2,
                        num_lines=10, line_length=0.22), run_time=0.35)

        sub = Text("DAC · MAC · RBAC · ABAC", font_size=24, color=AMBER)
        sub.next_to(four, DOWN, buff=0.4)
        self.play(FadeIn(sub, shift=UP * 0.1), run_time=0.35)
        self._pad("h")

        # ── Main ──────────────────────────────────────────────────────────────
        self._fade_all(0.3)
        self._bg()
        self.add(self._brand())
        title = self._scene_title("ACCESS CONTROL", color=BLUE)
        self.play(Write(title), run_time=0.5)
        self._sound("m")

        models = [
            ("DAC",  "Owner decides who gets in.",          "Discretionary — flexible.",   BLUE),
            ("MAC",  "System enforces via labels.",         "Mandatory — military.",       RED),
            ("RBAC", "Access tied to your job role.",       "Role-based, not identity.",   GREEN),
            ("ABAC", "Evaluates user, time, location.",     "Attribute-based — granular.", AMBER),
        ]
        blocks = []
        for abbr, line1, line2, color in models:
            glow, blk = self._glow_card(8.2, 1.92, color)
            lbl = Text(abbr, font_size=24, color=color, weight=BOLD)
            lbl.move_to(blk.get_left() + RIGHT * 1.2)
            l1 = Text(line1, font_size=13, color=WHITE, weight=BOLD)
            l2 = Text(line2, font_size=12, color=GRAY)
            right = VGroup(l1, l2).arrange(DOWN, buff=0.1, aligned_edge=LEFT)
            right.next_to(lbl, RIGHT, buff=0.28)
            right.set_y(lbl.get_y())
            blocks.append(VGroup(glow, blk, lbl, right))

        grp = VGroup(*blocks).arrange(DOWN, buff=0.2)
        grp.move_to(UP * 0.6)

        for g in blocks:
            glow, blk, lbl, right = g
            self.play(FadeIn(glow), DrawBorderThenFill(blk), run_time=0.4)
            self.play(Write(lbl), FadeIn(right, shift=RIGHT * 0.15), run_time=0.35)
            self.play(
                ShowPassingFlash(
                    blk.copy().set_stroke(WHITE, width=4, opacity=0.4),
                    time_width=0.5),
                run_time=0.4)
            self.wait(6.5)

        tip = self._exam_tip("MAC = mandatory labels. RBAC follows the job, not the person.")
        self.play(FadeIn(tip, scale=0.94), run_time=0.4)
        self.play(Flash(tip, color=RED, flash_radius=0.6,
                        num_lines=8, line_length=0.15), run_time=0.35)
        self.wait(4.0)
        self._pad("m")

        # ── CTA ───────────────────────────────────────────────────────────────
        self._cta_section("Know the models.\nAce the exam.")


# ═════════════════════════════════════════════════════════════════════════════
# SHORT 8 — AUTHENTICATION FACTORS
# ═════════════════════════════════════════════════════════════════════════════
class AuthenticationFactors(_Short):
    ID = "c8"

    def construct(self):
        # ── Hook ──────────────────────────────────────────────────────────────
        self._bg()
        self.add(self._brand())
        self._sound("h")

        line = Text("A password alone\nwon't save you.",
                    font_size=40, color=WHITE, weight=BOLD, line_spacing=1.2)
        line.move_to(UP * 2.9)
        self.play(Write(line), run_time=0.7)

        mfa = Text("MFA", font_size=84, color=GREEN, weight=BOLD)
        mfa.next_to(line, DOWN, buff=0.45)
        self.play(GrowFromCenter(mfa), run_time=0.4)
        self.play(Flash(mfa, color=GREEN, flash_radius=1.4,
                        num_lines=12, line_length=0.26), run_time=0.4)

        sub = Text("The factors that prove who you are.", font_size=22, color=AMBER)
        sub.next_to(mfa, DOWN, buff=0.45)
        self.play(FadeIn(sub, shift=UP * 0.1), run_time=0.35)
        self._pad("h")

        # ── Main ──────────────────────────────────────────────────────────────
        self._fade_all(0.3)
        self._bg()
        self.add(self._brand())
        title = self._scene_title("AUTH FACTORS", color=GREEN)
        self.play(Write(title), run_time=0.5)
        self._sound("m")

        factors = [
            ("KNOW",  "Password · PIN · passphrase",    BLUE),
            ("HAVE",  "Token · smart card · phone",     GREEN),
            ("ARE",   "Fingerprint · face · iris",      AMBER),
            ("WHERE", "Location · GPS · geofence",      TEAL),
            ("DO",    "Typing rhythm · behavior",       RED),
        ]
        rows = []
        for label, desc, color in factors:
            glow, card = self._glow_card(8.2, 1.28, color)
            lbl = Text(label, font_size=22, color=color, weight=BOLD)
            lbl.move_to(card.get_left() + RIGHT * 1.35)
            d = Text(desc, font_size=14, color=WHITE)
            d.next_to(lbl, RIGHT, buff=0.4)
            d.set_y(lbl.get_y())
            rows.append(VGroup(glow, card, lbl, d))

        grp = VGroup(*rows).arrange(DOWN, buff=0.16)
        grp.move_to(UP * 0.45)

        for g in rows:
            glow, card, lbl, d = g
            self.play(FadeIn(glow), DrawBorderThenFill(card),
                      Write(lbl), FadeIn(d, shift=RIGHT * 0.12), run_time=0.4)
            self.wait(4.8)

        tip = self._exam_tip("Two of the SAME factor is NOT MFA — the types must differ.")
        self.play(FadeIn(tip, scale=0.94), run_time=0.4)
        self.play(Flash(tip, color=RED, flash_radius=0.6,
                        num_lines=8, line_length=0.15), run_time=0.35)
        self.wait(4.0)
        self._pad("m")

        # ── CTA ───────────────────────────────────────────────────────────────
        self._cta_section("Layer your factors.\nLock it down.")


# ═════════════════════════════════════════════════════════════════════════════
# SHORT 9 — CRYPTOGRAPHY: SYMMETRIC vs ASYMMETRIC
# ═════════════════════════════════════════════════════════════════════════════
class Cryptography(_Short):
    ID = "c9"

    def construct(self):
        # ── Hook ──────────────────────────────────────────────────────────────
        self._bg()
        self.add(self._brand())
        self._sound("h")

        one = Text("One key,", font_size=46, color=GREEN, weight=BOLD)
        two = Text("or two?",  font_size=46, color=BLUE,  weight=BOLD)
        motto = VGroup(one, two).arrange(DOWN, buff=0.2)
        motto.move_to(UP * 2.5)
        self.play(Write(one), run_time=0.45)
        self.play(Write(two), run_time=0.45)
        self.play(Flash(two, color=BLUE, flash_radius=1.1,
                        num_lines=10, line_length=0.22), run_time=0.4)

        sub = Text("Symmetric vs Asymmetric — settled.", font_size=22, color=AMBER)
        sub.next_to(motto, DOWN, buff=0.55)
        self.play(FadeIn(sub, shift=UP * 0.1), run_time=0.35)
        self._pad("h")

        # ── Main ──────────────────────────────────────────────────────────────
        self._fade_all(0.3)
        self._bg()
        self.add(self._brand())
        title = self._scene_title("CRYPTOGRAPHY", color=BLUE)
        self.play(Write(title), run_time=0.5)
        self._sound("m")

        # Two columns
        glow_s, sym = self._glow_card(3.9, 3.4, GREEN)
        sym.move_to(LEFT * 2.1 + UP * 2.55)
        glow_s.move_to(LEFT * 2.1 + UP * 2.55)
        s_lbl = Text("SYMMETRIC", font_size=18, color=GREEN, weight=BOLD)
        s_lbl.move_to(sym.get_top() + DOWN * 0.32)
        s_body = Text("ONE shared key\nFast — bulk data\nAES · DES · 3DES\nKey distribution\nis the problem",
                      font_size=13, color=WHITE, line_spacing=1.3)
        s_body.move_to(sym.get_center() + DOWN * 0.18)

        glow_a, asym = self._glow_card(3.9, 3.4, BLUE)
        asym.move_to(RIGHT * 2.1 + UP * 2.55)
        glow_a.move_to(RIGHT * 2.1 + UP * 2.55)
        a_lbl = Text("ASYMMETRIC", font_size=18, color=BLUE, weight=BOLD)
        a_lbl.move_to(asym.get_top() + DOWN * 0.32)
        a_body = Text("Public + private\nSlow — secure\nRSA · ECC\nSolves the key\nexchange problem",
                      font_size=13, color=WHITE, line_spacing=1.3)
        a_body.move_to(asym.get_center() + DOWN * 0.18)

        self.play(FadeIn(glow_s), DrawBorderThenFill(sym),
                  FadeIn(s_lbl), FadeIn(s_body), run_time=0.5)
        self.wait(9.5)
        self.play(FadeIn(glow_a), DrawBorderThenFill(asym),
                  FadeIn(a_lbl), FadeIn(a_body), run_time=0.5)
        self.wait(9.5)

        # Hybrid strip
        hglow, hyb = self._glow_card(8.2, 1.5, AMBER)
        hyb.move_to(DOWN * 1.7)
        hglow.move_to(DOWN * 1.7)
        h_lbl  = Text("HYBRID = TLS", font_size=18, color=AMBER, weight=BOLD)
        h_desc = Text("Asymmetric exchanges the key → symmetric encrypts the data",
                      font_size=12, color=WHITE)
        hc = VGroup(h_lbl, h_desc).arrange(DOWN, buff=0.12)
        hc.move_to(hyb.get_center())
        self.play(FadeIn(hglow), DrawBorderThenFill(hyb), FadeIn(hc), run_time=0.5)
        self.play(Flash(hyb, color=AMBER, flash_radius=0.9,
                        num_lines=8, line_length=0.2), run_time=0.4)
        self.wait(7.0)

        tip = self._exam_tip("Encrypt with the recipient's PUBLIC key. Sign with your PRIVATE key.")
        self.play(FadeIn(tip, scale=0.94), run_time=0.4)
        self.play(Flash(tip, color=RED, flash_radius=0.6,
                        num_lines=8, line_length=0.15), run_time=0.35)
        self.wait(4.0)
        self._pad("m")

        # ── CTA ───────────────────────────────────────────────────────────────
        self._cta_section("One key or two?\nNow you know.")


# ═════════════════════════════════════════════════════════════════════════════
# SHORT 10 — MALWARE TYPES
# ═════════════════════════════════════════════════════════════════════════════
class MalwareTypes(_Short):
    ID = "c10"

    def construct(self):
        # ── Hook ──────────────────────────────────────────────────────────────
        self._bg()
        self.add(self._brand())
        self._sound("h")

        v = Text("VIRUS  ≠  WORM", font_size=48, color=RED, weight=BOLD)
        v.move_to(UP * 2.6)
        self.play(Write(v), run_time=0.6)
        self.play(Flash(v, color=RED, flash_radius=1.3,
                        num_lines=10, line_length=0.24), run_time=0.4)

        nope = Text("Not all malware\nis a virus.",
                    font_size=34, color=WHITE, weight=BOLD, line_spacing=1.2)
        nope.next_to(v, DOWN, buff=0.5)
        self.play(FadeIn(nope, shift=DOWN * 0.1), run_time=0.45)

        sub = Text("6 types the exam loves.", font_size=24, color=AMBER)
        sub.next_to(nope, DOWN, buff=0.45)
        self.play(FadeIn(sub, shift=UP * 0.1), run_time=0.35)
        self._pad("h")

        # ── Main ──────────────────────────────────────────────────────────────
        self._fade_all(0.3)
        self._bg()
        self.add(self._brand())
        title = self._scene_title("MALWARE TYPES", color=RED)
        self.play(Write(title), run_time=0.5)
        self._sound("m")

        types = [
            ("VIRUS",      "Attaches to a file · needs you to run it", RED),
            ("WORM",       "Self-replicates · spreads alone",          AMBER),
            ("TROJAN",     "Disguised as legit software",              BLUE),
            ("RANSOMWARE", "Encrypts files · demands payment",         TEAL),
            ("ROOTKIT",    "Hides at kernel level · stealth access",   GREEN),
            ("LOGIC BOMB", "Dormant until a trigger fires",            GRAY),
        ]
        rows = []
        for label, desc, color in types:
            glow, card = self._glow_card(8.2, 1.18, color)
            lbl = Text(label, font_size=18, color=color, weight=BOLD)
            lbl.move_to(card.get_left() + RIGHT * 1.5)
            d = Text(desc, font_size=12, color=WHITE)
            d.next_to(lbl, RIGHT, buff=0.3)
            d.set_y(lbl.get_y())
            rows.append(VGroup(glow, card, lbl, d))

        grp = VGroup(*rows).arrange(DOWN, buff=0.12)
        grp.move_to(UP * 0.4)

        for g in rows:
            glow, card, lbl, d = g
            self.play(FadeIn(glow), DrawBorderThenFill(card),
                      Write(lbl), FadeIn(d, shift=RIGHT * 0.12), run_time=0.38)
            self.wait(4.4)

        tip = self._exam_tip("Worm spreads by itself. A virus needs YOU to execute it.")
        self.play(FadeIn(tip, scale=0.94), run_time=0.4)
        self.play(Flash(tip, color=RED, flash_radius=0.6,
                        num_lines=8, line_length=0.15), run_time=0.35)
        self.wait(4.0)
        self._pad("m")

        # ── CTA ───────────────────────────────────────────────────────────────
        self._cta_section("Know your malware.\nPass the exam.")


# ═════════════════════════════════════════════════════════════════════════════
# SHORT 11 — OSI MODEL
# ═════════════════════════════════════════════════════════════════════════════
class OSIModel(_Short):
    ID = "c11"

    def construct(self):
        self._bg()
        self.add(self._brand())
        self._sound("h")

        seven = Text("7 LAYERS", font_size=52, color=BLUE, weight=BOLD)
        seven.move_to(UP * 2.6)
        self.play(Write(seven), run_time=0.5)
        self.play(Flash(seven, color=BLUE, flash_radius=1.3,
                        num_lines=10, line_length=0.24), run_time=0.4)
        sub = Text("One mnemonic.\nThe OSI model.", font_size=32, color=WHITE,
                   weight=BOLD, line_spacing=1.2)
        sub.next_to(seven, DOWN, buff=0.5)
        self.play(FadeIn(sub, shift=DOWN * 0.1), run_time=0.45)
        self._pad("h")

        self._fade_all(0.3)
        self._bg()
        self.add(self._brand())
        title = self._scene_title("THE OSI MODEL", color=BLUE)
        self.play(Write(title), run_time=0.5)
        self._sound("m")

        layers = [
            ("L7 Application",  "HTTP · DNS · SMTP",        "#AA66FF"),
            ("L6 Presentation", "Encryption · formatting",  BLUE),
            ("L5 Session",      "Open / maintain sessions",  GREEN),
            ("L4 Transport",    "TCP · UDP",                 AMBER),
            ("L3 Network",      "Routers · IP · routing",    TEAL),
            ("L2 Data Link",    "Switches · MAC · frames",   RED),
            ("L1 Physical",     "Cables · hubs · bits",      GRAY),
        ]
        rows = []
        for label, desc, color in layers:
            glow, card = self._glow_card(8.4, 0.84, color)
            lbl = Text(label, font_size=16, color=color, weight=BOLD)
            lbl.move_to(card.get_left() + RIGHT * 1.8)
            d = Text(desc, font_size=12, color=WHITE)
            d.next_to(lbl, RIGHT, buff=0.3)
            d.set_y(lbl.get_y())
            rows.append(VGroup(glow, card, lbl, d))
        grp = VGroup(*rows).arrange(DOWN, buff=0.1)
        grp.move_to(UP * 0.35)
        for g in rows:
            glow, card, lbl, d = g
            self.play(FadeIn(glow), DrawBorderThenFill(card),
                      Write(lbl), FadeIn(d, shift=RIGHT * 0.12), run_time=0.32)
            self.wait(2.9)

        tip = self._exam_tip("Switch = L2 · Router = L3 · Encryption = L6")
        self.play(FadeIn(tip, scale=0.94), run_time=0.4)
        self.play(Flash(tip, color=RED, flash_radius=0.6,
                        num_lines=8, line_length=0.15), run_time=0.35)
        self.wait(3.5)
        self._pad("m")

        self._cta_section("Seven layers.\nNow you know.")


# ═════════════════════════════════════════════════════════════════════════════
# SHORT 12 — FIREWALL TYPES
# ═════════════════════════════════════════════════════════════════════════════
class FirewallTypes(_Short):
    ID = "c12"

    def construct(self):
        self._bg()
        self.add(self._brand())
        self._sound("h")

        v = Text("5 FIREWALLS", font_size=50, color=RED, weight=BOLD)
        v.move_to(UP * 2.6)
        self.play(Write(v), run_time=0.55)
        self.play(Flash(v, color=RED, flash_radius=1.3,
                        num_lines=10, line_length=0.24), run_time=0.4)
        nope = Text("Not all firewalls\nare equal.", font_size=34, color=WHITE,
                    weight=BOLD, line_spacing=1.2)
        nope.next_to(v, DOWN, buff=0.5)
        self.play(FadeIn(nope, shift=DOWN * 0.1), run_time=0.45)
        self._pad("h")

        self._fade_all(0.3)
        self._bg()
        self.add(self._brand())
        title = self._scene_title("FIREWALL TYPES", color=RED)
        self.play(Write(title), run_time=0.5)
        self._sound("m")

        types = [
            ("PACKET FILTER", "L3/L4 · stateless · IP + port",  GRAY),
            ("STATEFUL",      "Tracks connections in a table",   BLUE),
            ("PROXY",         "L7 · inspects actual content",    GREEN),
            ("NGFW",          "DPI + IPS + app awareness",       AMBER),
            ("WAF",           "Filters HTTP · stops SQLi & XSS",  "#AA66FF"),
        ]
        rows = []
        for label, desc, color in types:
            glow, card = self._glow_card(8.4, 1.16, color)
            lbl = Text(label, font_size=18, color=color, weight=BOLD)
            lbl.move_to(card.get_left() + RIGHT * 1.7)
            d = Text(desc, font_size=12, color=WHITE)
            d.next_to(lbl, RIGHT, buff=0.3)
            d.set_y(lbl.get_y())
            rows.append(VGroup(glow, card, lbl, d))
        grp = VGroup(*rows).arrange(DOWN, buff=0.16)
        grp.move_to(UP * 0.25)
        for g in rows:
            glow, card, lbl, d = g
            self.play(FadeIn(glow), DrawBorderThenFill(card),
                      Write(lbl), FadeIn(d, shift=RIGHT * 0.12), run_time=0.38)
            self.wait(4.3)

        tip = self._exam_tip("Stateful tracks connections · a proxy inspects L7 content.")
        self.play(FadeIn(tip, scale=0.94), run_time=0.4)
        self.play(Flash(tip, color=RED, flash_radius=0.6,
                        num_lines=8, line_length=0.15), run_time=0.35)
        self.wait(3.5)
        self._pad("m")

        self._cta_section("Firewalls, sorted.\nPass the exam.")


# ═════════════════════════════════════════════════════════════════════════════
# SHORT 13 — COMMON PORTS
# ═════════════════════════════════════════════════════════════════════════════
class CommonPorts(_Short):
    ID = "c13"

    def construct(self):
        self._bg()
        self.add(self._brand())
        self._sound("h")

        v = Text("CLEARTEXT\n= FINDING", font_size=48, color=RED, weight=BOLD,
                 line_spacing=1.1)
        v.move_to(UP * 2.4)
        self.play(Write(v), run_time=0.6)
        self.play(Flash(v, color=RED, flash_radius=1.3,
                        num_lines=10, line_length=0.24), run_time=0.4)
        sub = Text("Know the secure swaps.", font_size=26, color=AMBER)
        sub.next_to(v, DOWN, buff=0.5)
        self.play(FadeIn(sub, shift=UP * 0.1), run_time=0.35)
        self._pad("h")

        self._fade_all(0.3)
        self._bg()
        self.add(self._brand())
        title = self._scene_title("SECURE THE PORTS", color=GREEN)
        self.play(Write(title), run_time=0.5)
        self._sound("m")

        swaps = [
            ("FTP  20/21", "SFTP / FTPS  22"),
            ("Telnet  23",  "SSH  22"),
            ("HTTP  80",    "HTTPS  443"),
            ("SNMP v1/v2",  "SNMP v3"),
            ("LDAP  389",   "LDAPS  636"),
        ]
        rows = []
        for insec, sec in swaps:
            glow, card = self._glow_card(8.4, 1.08, BLUE)
            ins = Text(insec, font_size=16, color=RED, weight=BOLD)
            ins.move_to(card.get_left() + RIGHT * 1.55)
            arrow = Text("→", font_size=22, color=WHITE)
            arrow.move_to(card.get_center() + LEFT * 0.1)
            arrow.set_y(ins.get_y())
            secure = Text(sec, font_size=16, color=GREEN, weight=BOLD)
            secure.move_to(card.get_center() + RIGHT * 2.2)
            secure.set_y(ins.get_y())
            rows.append(VGroup(glow, card, ins, arrow, secure))
        grp = VGroup(*rows).arrange(DOWN, buff=0.16)
        grp.move_to(UP * 0.25)
        for g in rows:
            self.play(FadeIn(g[0]), DrawBorderThenFill(g[1]),
                      Write(g[2]), FadeIn(g[3]), Write(g[4]), run_time=0.4)
            self.wait(4.0)

        tip = self._exam_tip("Cleartext credentials → answer = the encrypted equivalent.")
        self.play(FadeIn(tip, scale=0.94), run_time=0.4)
        self.play(Flash(tip, color=RED, flash_radius=0.6,
                        num_lines=8, line_length=0.15), run_time=0.35)
        self.wait(3.5)
        self._pad("m")

        self._cta_section("Insecure in,\nsecure out.")


# ═════════════════════════════════════════════════════════════════════════════
# SHORT 14 — WIRELESS SECURITY
# ═════════════════════════════════════════════════════════════════════════════
class WirelessSecurity(_Short):
    ID = "c14"

    def construct(self):
        self._bg()
        self.add(self._brand())
        self._sound("h")

        one = Text("WEP → WPA3", font_size=48, color=BLUE, weight=BOLD)
        one.move_to(UP * 2.6)
        self.play(Write(one), run_time=0.55)
        self.play(Flash(one, color=BLUE, flash_radius=1.2,
                        num_lines=10, line_length=0.22), run_time=0.4)
        sub = Text("Which one is safe?", font_size=28, color=AMBER)
        sub.next_to(one, DOWN, buff=0.55)
        self.play(FadeIn(sub, shift=UP * 0.1), run_time=0.35)
        self._pad("h")

        self._fade_all(0.3)
        self._bg()
        self.add(self._brand())
        title = self._scene_title("WIRELESS SECURITY", color=TEAL)
        self.play(Write(title), run_time=0.5)
        self._sound("m")

        ladder = [
            ("WEP",  "BROKEN · weak IV · never use", RED),
            ("WPA",  "TKIP · now weak",              AMBER),
            ("WPA2", "AES/CCMP · KRACK vulnerable",  BLUE),
            ("WPA3", "SAE · CURRENT standard",       GREEN),
        ]
        rows = []
        for label, desc, color in ladder:
            glow, card = self._glow_card(8.4, 1.24, color)
            lbl = Text(label, font_size=20, color=color, weight=BOLD)
            lbl.move_to(card.get_left() + RIGHT * 1.3)
            d = Text(desc, font_size=13, color=WHITE)
            d.next_to(lbl, RIGHT, buff=0.35)
            d.set_y(lbl.get_y())
            rows.append(VGroup(glow, card, lbl, d))
        grp = VGroup(*rows).arrange(DOWN, buff=0.2)
        grp.move_to(UP * 0.55)
        for g in rows:
            glow, card, lbl, d = g
            self.play(FadeIn(glow), DrawBorderThenFill(card),
                      Write(lbl), FadeIn(d, shift=RIGHT * 0.12), run_time=0.4)
            self.wait(4.6)

        ent_glow, ent = self._glow_card(8.4, 1.1, "#AA66FF")
        ent.move_to(DOWN * 2.7)
        ent_glow.move_to(DOWN * 2.7)
        et = VGroup(
            Text("ENTERPRISE", font_size=16, color="#AA66FF", weight=BOLD),
            Text("WPA2/3 + 802.1X → per-user auth via RADIUS", font_size=12, color=WHITE),
        ).arrange(DOWN, buff=0.1)
        et.move_to(ent.get_center())
        self.play(FadeIn(ent_glow), DrawBorderThenFill(ent), FadeIn(et), run_time=0.45)
        self.wait(3.5)

        tip = self._exam_tip("WPA3 for confidentiality · 802.1X for enterprise auth.")
        self.play(FadeIn(tip, scale=0.94), run_time=0.4)
        self.wait(3.0)
        self._pad("m")

        self._cta_section("WPA3 or bust.\nNow you know.")


# ═════════════════════════════════════════════════════════════════════════════
# SHORT 15 — VPN & IPsec
# ═════════════════════════════════════════════════════════════════════════════
class VPNandIPsec(_Short):
    ID = "c15"

    def construct(self):
        self._bg()
        self.add(self._brand())
        self._sound("h")

        one = Text("IPsec", font_size=56, color=GREEN, weight=BOLD)
        two = Text("2 × 2", font_size=48, color=BLUE, weight=BOLD)
        motto = VGroup(one, two).arrange(DOWN, buff=0.25)
        motto.move_to(UP * 2.5)
        self.play(Write(one), run_time=0.45)
        self.play(Write(two), run_time=0.45)
        self.play(Flash(two, color=BLUE, flash_radius=1.1,
                        num_lines=10, line_length=0.22), run_time=0.4)
        sub = Text("2 protocols · 2 modes.", font_size=24, color=AMBER)
        sub.next_to(motto, DOWN, buff=0.55)
        self.play(FadeIn(sub, shift=UP * 0.1), run_time=0.35)
        self._pad("h")

        self._fade_all(0.3)
        self._bg()
        self.add(self._brand())
        title = self._scene_title("IPsec", color=GREEN)
        self.play(Write(title), run_time=0.5)
        self._sound("m")

        glow_p, proto = self._glow_card(3.9, 3.4, AMBER)
        proto.move_to(LEFT * 2.1 + UP * 2.55)
        glow_p.move_to(LEFT * 2.1 + UP * 2.55)
        p_lbl = Text("PROTOCOLS", font_size=18, color=AMBER, weight=BOLD)
        p_lbl.move_to(proto.get_top() + DOWN * 0.32)
        p_body = Text("AH\nintegrity only\nNO encryption\n\nESP\nencrypts data",
                      font_size=13, color=WHITE, line_spacing=1.25)
        p_body.move_to(proto.get_center() + DOWN * 0.18)

        glow_m, modes = self._glow_card(3.9, 3.4, BLUE)
        modes.move_to(RIGHT * 2.1 + UP * 2.55)
        glow_m.move_to(RIGHT * 2.1 + UP * 2.55)
        m_lbl = Text("MODES", font_size=18, color=BLUE, weight=BOLD)
        m_lbl.move_to(modes.get_top() + DOWN * 0.32)
        m_body = Text("Transport\npayload only\nhost-to-host\n\nTunnel\nwhole packet",
                      font_size=13, color=WHITE, line_spacing=1.25)
        m_body.move_to(modes.get_center() + DOWN * 0.18)

        self.play(FadeIn(glow_p), DrawBorderThenFill(proto),
                  FadeIn(p_lbl), FadeIn(p_body), run_time=0.5)
        self.wait(9.5)
        self.play(FadeIn(glow_m), DrawBorderThenFill(modes),
                  FadeIn(m_lbl), FadeIn(m_body), run_time=0.5)
        self.wait(9.5)

        iglow, ike = self._glow_card(8.2, 1.5, "#AA66FF")
        ike.move_to(DOWN * 1.7)
        iglow.move_to(DOWN * 1.7)
        ic = VGroup(
            Text("IKE + TLS", font_size=18, color="#AA66FF", weight=BOLD),
            Text("IKE negotiates keys · TLS secures HTTPS & SSL-VPN", font_size=12, color=WHITE),
        ).arrange(DOWN, buff=0.12)
        ic.move_to(ike.get_center())
        self.play(FadeIn(iglow), DrawBorderThenFill(ike), FadeIn(ic), run_time=0.5)
        self.wait(6.5)

        tip = self._exam_tip("ESP encrypts, AH does not · tunnel = site-to-site.")
        self.play(FadeIn(tip, scale=0.94), run_time=0.4)
        self.play(Flash(tip, color=RED, flash_radius=0.6,
                        num_lines=8, line_length=0.15), run_time=0.35)
        self.wait(3.5)
        self._pad("m")

        self._cta_section("Two protocols,\ntwo modes.")


# ═════════════════════════════════════════════════════════════════════════════
# SHORT 16 — NETWORK ATTACKS
# ═════════════════════════════════════════════════════════════════════════════
class NetworkAttacks(_Short):
    ID = "c16"

    def construct(self):
        self._bg()
        self.add(self._brand())
        self._sound("h")

        v = Text("NAME THE\nATTACK", font_size=48, color=RED, weight=BOLD,
                 line_spacing=1.1)
        v.move_to(UP * 2.5)
        self.play(Write(v), run_time=0.6)
        self.play(Flash(v, color=RED, flash_radius=1.3,
                        num_lines=10, line_length=0.24), run_time=0.4)
        sub = Text("The exam describes it —\nyou name it.", font_size=28, color=WHITE,
                   weight=BOLD, line_spacing=1.2)
        sub.next_to(v, DOWN, buff=0.5)
        self.play(FadeIn(sub, shift=DOWN * 0.1), run_time=0.45)
        self._pad("h")

        self._fade_all(0.3)
        self._bg()
        self.add(self._brand())
        title = self._scene_title("NETWORK ATTACKS", color=RED)
        self.play(Write(title), run_time=0.5)
        self._sound("m")

        types = [
            ("DoS / DDoS",   "Flood via botnet → unavailable",    RED),
            ("MITM",         "Intercept & relay traffic",          AMBER),
            ("ARP POISON",   "Forged replies → attacker MAC",      BLUE),
            ("DNS POISON",   "Corrupt cache · DNSSEC defends",     TEAL),
            ("SYN FLOOD",    "Half-open handshakes exhaust table", GREEN),
            ("VLAN HOP",     "Reach another VLAN · double-tag",    "#AA66FF"),
        ]
        rows = []
        for label, desc, color in types:
            glow, card = self._glow_card(8.4, 1.16, color)
            lbl = Text(label, font_size=17, color=color, weight=BOLD)
            lbl.move_to(card.get_left() + RIGHT * 1.55)
            d = Text(desc, font_size=12, color=WHITE)
            d.next_to(lbl, RIGHT, buff=0.3)
            d.set_y(lbl.get_y())
            rows.append(VGroup(glow, card, lbl, d))
        grp = VGroup(*rows).arrange(DOWN, buff=0.12)
        grp.move_to(UP * 0.4)
        for g in rows:
            glow, card, lbl, d = g
            self.play(FadeIn(glow), DrawBorderThenFill(card),
                      Write(lbl), FadeIn(d, shift=RIGHT * 0.12), run_time=0.38)
            self.wait(4.2)

        tip = self._exam_tip("Defenses: segmentation, encryption, strong authentication.")
        self.play(FadeIn(tip, scale=0.94), run_time=0.4)
        self.play(Flash(tip, color=RED, flash_radius=0.6,
                        num_lines=8, line_length=0.15), run_time=0.35)
        self.wait(3.5)
        self._pad("m")

        self._cta_section("Match the clue.\nName the attack.")


# ═════════════════════════════════════════════════════════════════════════════
# SHORT 17 — BCP vs DRP
# ═════════════════════════════════════════════════════════════════════════════
class BCPvsDRP(_Short):
    ID = "c17"

    def construct(self):
        self._bg()
        self.add(self._brand())
        self._sound("h")

        v = Text("RTO · RPO · MTD", font_size=40, color=AMBER, weight=BOLD)
        v.move_to(UP * 2.6)
        self.play(Write(v), run_time=0.6)
        self.play(Flash(v, color=AMBER, flash_radius=1.3,
                        num_lines=10, line_length=0.24), run_time=0.4)
        sub = Text("Three letters that\ntrip up everyone.", font_size=30, color=WHITE,
                   weight=BOLD, line_spacing=1.2)
        sub.next_to(v, DOWN, buff=0.5)
        self.play(FadeIn(sub, shift=DOWN * 0.1), run_time=0.45)
        self._pad("h")

        self._fade_all(0.3)
        self._bg()
        self.add(self._brand())
        title = self._scene_title("BCP vs DRP", color=AMBER)
        self.play(Write(title), run_time=0.5)
        self._sound("m")

        items = [
            ("BCP", "Keeps the whole business running",       BLUE),
            ("DRP", "Subset · restores IT systems",           TEAL),
            ("RTO", "Time to RESTORE a system",               GREEN),
            ("RPO", "Acceptable DATA LOSS (in time)",         AMBER),
            ("MTD", "Max downtime before real harm",          RED),
        ]
        rows = []
        for label, desc, color in items:
            glow, card = self._glow_card(8.4, 1.1, color)
            lbl = Text(label, font_size=19, color=color, weight=BOLD)
            lbl.move_to(card.get_left() + RIGHT * 1.15)
            d = Text(desc, font_size=13, color=WHITE)
            d.next_to(lbl, RIGHT, buff=0.35)
            d.set_y(lbl.get_y())
            rows.append(VGroup(glow, card, lbl, d))
        grp = VGroup(*rows).arrange(DOWN, buff=0.16)
        grp.move_to(UP * 0.25)
        for g in rows:
            glow, card, lbl, d = g
            self.play(FadeIn(glow), DrawBorderThenFill(card),
                      Write(lbl), FadeIn(d, shift=RIGHT * 0.12), run_time=0.4)
            self.wait(4.2)

        tip = self._exam_tip("RPO = data loss · RTO = time to recover · RTO < MTD.")
        self.play(FadeIn(tip, scale=0.94), run_time=0.4)
        self.play(Flash(tip, color=RED, flash_radius=0.6,
                        num_lines=8, line_length=0.15), run_time=0.35)
        self.wait(3.5)
        self._pad("m")

        self._cta_section("RTO, RPO, MTD.\nLocked in.")


# ═════════════════════════════════════════════════════════════════════════════
# SHORT 18 — RAID LEVELS
# ═════════════════════════════════════════════════════════════════════════════
class RAIDLevels(_Short):
    ID = "c18"

    def construct(self):
        self._bg()
        self.add(self._brand())
        self._sound("h")

        v = Text("RAID\n0 · 1 · 5 · 6 · 10", font_size=44, color=GREEN, weight=BOLD,
                 line_spacing=1.1)
        v.move_to(UP * 2.4)
        self.play(Write(v), run_time=0.6)
        self.play(Flash(v, color=GREEN, flash_radius=1.3,
                        num_lines=10, line_length=0.24), run_time=0.4)
        sub = Text("An availability control.", font_size=26, color=AMBER)
        sub.next_to(v, DOWN, buff=0.5)
        self.play(FadeIn(sub, shift=UP * 0.1), run_time=0.35)
        self._pad("h")

        self._fade_all(0.3)
        self._bg()
        self.add(self._brand())
        title = self._scene_title("RAID LEVELS", color=GREEN)
        self.play(Write(title), run_time=0.5)
        self._sound("m")

        levels = [
            ("RAID 0",  "Striping · fast · NO redundancy",   RED),
            ("RAID 1",  "Mirroring · full copy",             BLUE),
            ("RAID 5",  "Parity · survives 1 disk fail",     GREEN),
            ("RAID 6",  "Double parity · survives 2 fails",  TEAL),
            ("RAID 10", "Mirror + stripe · speed + safety",  AMBER),
        ]
        rows = []
        for label, desc, color in levels:
            glow, card = self._glow_card(8.4, 1.1, color)
            lbl = Text(label, font_size=18, color=color, weight=BOLD)
            lbl.move_to(card.get_left() + RIGHT * 1.35)
            d = Text(desc, font_size=12, color=WHITE)
            d.next_to(lbl, RIGHT, buff=0.3)
            d.set_y(lbl.get_y())
            rows.append(VGroup(glow, card, lbl, d))
        grp = VGroup(*rows).arrange(DOWN, buff=0.16)
        grp.move_to(UP * 0.25)
        for g in rows:
            glow, card, lbl, d = g
            self.play(FadeIn(glow), DrawBorderThenFill(card),
                      Write(lbl), FadeIn(d, shift=RIGHT * 0.12), run_time=0.4)
            self.wait(4.2)

        tip = self._exam_tip("RAID 0 = no fault tolerance · RAID 5 survives ONE drive.")
        self.play(FadeIn(tip, scale=0.94), run_time=0.4)
        self.play(Flash(tip, color=RED, flash_radius=0.6,
                        num_lines=8, line_length=0.15), run_time=0.35)
        self.wait(3.5)
        self._pad("m")

        self._cta_section("RAID is availability —\nnot a backup.")


# ═════════════════════════════════════════════════════════════════════════════
# SHORT 19 — SECURITY MODELS
# ═════════════════════════════════════════════════════════════════════════════
class SecurityModels(_Short):
    ID = "c19"

    def construct(self):
        self._bg()
        self.add(self._brand())
        self._sound("h")

        one = Text("Bell-LaPadula", font_size=38, color=BLUE, weight=BOLD)
        two = Text("or Biba?",      font_size=42, color=GREEN, weight=BOLD)
        motto = VGroup(one, two).arrange(DOWN, buff=0.25)
        motto.move_to(UP * 2.5)
        self.play(Write(one), run_time=0.45)
        self.play(Write(two), run_time=0.45)
        self.play(Flash(two, color=GREEN, flash_radius=1.1,
                        num_lines=10, line_length=0.22), run_time=0.4)
        sub = Text("Confidentiality vs integrity.", font_size=22, color=AMBER)
        sub.next_to(motto, DOWN, buff=0.55)
        self.play(FadeIn(sub, shift=UP * 0.1), run_time=0.35)
        self._pad("h")

        self._fade_all(0.3)
        self._bg()
        self.add(self._brand())
        title = self._scene_title("SECURITY MODELS", color=BLUE)
        self.play(Write(title), run_time=0.5)
        self._sound("m")

        glow_b, blp = self._glow_card(3.9, 3.4, BLUE)
        blp.move_to(LEFT * 2.1 + UP * 2.55)
        glow_b.move_to(LEFT * 2.1 + UP * 2.55)
        b_lbl = Text("BELL-LAPADULA", font_size=15, color=BLUE, weight=BOLD)
        b_lbl.move_to(blp.get_top() + DOWN * 0.32)
        b_body = Text("Confidentiality\n\nNo READ up\nNo WRITE down\n\nProtects secrets",
                      font_size=13, color=WHITE, line_spacing=1.3)
        b_body.move_to(blp.get_center() + DOWN * 0.18)

        glow_i, biba = self._glow_card(3.9, 3.4, GREEN)
        biba.move_to(RIGHT * 2.1 + UP * 2.55)
        glow_i.move_to(RIGHT * 2.1 + UP * 2.55)
        i_lbl = Text("BIBA", font_size=18, color=GREEN, weight=BOLD)
        i_lbl.move_to(biba.get_top() + DOWN * 0.32)
        i_body = Text("Integrity\n\nNo READ down\nNo WRITE up\n\nProtects trust",
                      font_size=13, color=WHITE, line_spacing=1.3)
        i_body.move_to(biba.get_center() + DOWN * 0.18)

        self.play(FadeIn(glow_b), DrawBorderThenFill(blp),
                  FadeIn(b_lbl), FadeIn(b_body), run_time=0.5)
        self.wait(9.5)
        self.play(FadeIn(glow_i), DrawBorderThenFill(biba),
                  FadeIn(i_lbl), FadeIn(i_body), run_time=0.5)
        self.wait(9.5)

        cglow, cw = self._glow_card(8.2, 1.5, AMBER)
        cw.move_to(DOWN * 1.7)
        cglow.move_to(DOWN * 1.7)
        cc = VGroup(
            Text("CLARK-WILSON", font_size=18, color=AMBER, weight=BOLD),
            Text("Integrity via well-formed transactions + separation of duties", font_size=12, color=WHITE),
        ).arrange(DOWN, buff=0.12)
        cc.move_to(cw.get_center())
        self.play(FadeIn(cglow), DrawBorderThenFill(cw), FadeIn(cc), run_time=0.5)
        self.wait(6.0)

        tip = self._exam_tip("Confidentiality → Bell-LaPadula · Integrity → Biba.")
        self.play(FadeIn(tip, scale=0.94), run_time=0.4)
        self.play(Flash(tip, color=RED, flash_radius=0.6,
                        num_lines=8, line_length=0.15), run_time=0.35)
        self.wait(3.5)
        self._pad("m")

        self._cta_section("Secrets or trust?\nNow you know.")


# ═════════════════════════════════════════════════════════════════════════════
# SHORT 20 — CLOUD SERVICE MODELS
# ═════════════════════════════════════════════════════════════════════════════
class CloudModels(_Short):
    ID = "c20"

    def construct(self):
        self._bg()
        self.add(self._brand())
        self._sound("h")

        v = Text("IaaS · PaaS · SaaS", font_size=40, color=TEAL, weight=BOLD)
        v.move_to(UP * 2.6)
        self.play(Write(v), run_time=0.6)
        self.play(Flash(v, color=TEAL, flash_radius=1.3,
                        num_lines=10, line_length=0.24), run_time=0.4)
        sub = Text("Who secures what?", font_size=30, color=WHITE, weight=BOLD)
        sub.next_to(v, DOWN, buff=0.5)
        self.play(FadeIn(sub, shift=DOWN * 0.1), run_time=0.45)
        self._pad("h")

        self._fade_all(0.3)
        self._bg()
        self.add(self._brand())
        title = self._scene_title("CLOUD MODELS", color=TEAL)
        self.play(Write(title), run_time=0.5)
        self._sound("m")

        models = [
            ("IaaS", "Provider: compute/storage/net", "You: OS + apps + data", BLUE),
            ("PaaS", "Provider: OS + runtime",         "You: app + data",       GREEN),
            ("SaaS", "Provider: runs everything",      "You: just use it",      AMBER),
        ]
        rows = []
        for label, prov, you, color in models:
            glow, card = self._glow_card(8.4, 1.7, color)
            lbl = Text(label, font_size=24, color=color, weight=BOLD)
            lbl.move_to(card.get_left() + RIGHT * 1.1)
            body = VGroup(
                Text(prov, font_size=13, color=GRAY),
                Text(you,  font_size=13, color=WHITE, weight=BOLD),
            ).arrange(DOWN, buff=0.14, aligned_edge=LEFT)
            body.next_to(lbl, RIGHT, buff=0.4)
            body.set_y(lbl.get_y())
            rows.append(VGroup(glow, card, lbl, body))
        grp = VGroup(*rows).arrange(DOWN, buff=0.24)
        grp.move_to(UP * 0.7)
        for g in rows:
            glow, card, lbl, body = g
            self.play(FadeIn(glow), DrawBorderThenFill(card),
                      Write(lbl), FadeIn(body, shift=RIGHT * 0.12), run_time=0.45)
            self.wait(6.2)

        srglow, sr = self._glow_card(8.4, 1.05, "#AA66FF")
        sr.move_to(DOWN * 2.75)
        srglow.move_to(DOWN * 2.75)
        srt = VGroup(
            Text("SHARED RESPONSIBILITY", font_size=15, color="#AA66FF", weight=BOLD),
            Text("More provider control = less yours — but security is always shared", font_size=11, color=WHITE),
        ).arrange(DOWN, buff=0.1)
        srt.move_to(sr.get_center())
        self.play(FadeIn(srglow), DrawBorderThenFill(sr), FadeIn(srt), run_time=0.45)
        self.wait(3.0)

        tip = self._exam_tip("In SaaS you STILL own data classification & access.")
        self.play(FadeIn(tip, scale=0.94), run_time=0.4)
        self.wait(3.0)
        self._pad("m")

        self._cta_section("Know the line.\nOwn your data.")
