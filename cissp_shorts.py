"""
CISSP Domain Mastery — YouTube Shorts v2
Enhanced theme, animations, and readability (1080 × 1920 / 9:16)

Render:
    manim -qh cissp_shorts.py CIATriad
    manim -qh cissp_shorts.py DataClassification
    manim -qh cissp_shorts.py ZeroTrust
    manim -qh cissp_shorts.py IncidentResponse
    manim -qh cissp_shorts.py ExamTraps
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
