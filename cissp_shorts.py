"""
CISSP Domain Mastery — YouTube Shorts
Five 60-second portrait explainer videos (1080 × 1920 / 9:16)

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

BG    = "#0A0E1A"
BLUE  = "#00BFFF"
AMBER = "#FFB300"
GREEN = "#00FF88"
RED   = "#FF4444"
GRAY  = "#8899AA"
WHITE = "#FFFFFF"
TEAL  = "#00DDAA"

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


# ── Base class ────────────────────────────────────────────────────────────────
class _Short(Scene):
    ID = "c0"

    def setup(self):
        self.camera.background_color = BG

    def _bg(self):
        bg = Rectangle(width=10, height=18,
                       fill_color=BG, fill_opacity=1, stroke_width=0)
        self.add(bg)
        for x in [-3, -1.5, 0, 1.5, 3]:
            self.add(Line(UP*8.5 + RIGHT*x, DOWN*8.5 + RIGHT*x,
                          stroke_width=0.5, color=BLUE, stroke_opacity=0.07))
        for y in range(-7, 8, 2):
            self.add(Line(LEFT*4.8 + UP*y, RIGHT*4.8 + UP*y,
                          stroke_width=0.4, color=BLUE, stroke_opacity=0.05))
        return bg

    def _brand(self):
        lbl = Text("ZERO DAY LABS", font_size=24, color=BLUE, weight=BOLD)
        lbl.move_to(UP * 7.2)
        bar = Line(LEFT*2.0, RIGHT*2.0, color=BLUE, stroke_width=1.2)
        bar.next_to(lbl, DOWN, buff=0.12)
        return VGroup(lbl, bar)

    def _scene_title(self, text, color=BLUE):
        t = Text(text, font_size=34, color=color, weight=BOLD)
        t.move_to(UP * 5.9)
        bar = Line(LEFT*3.8, RIGHT*3.8, color=color, stroke_width=1.5)
        bar.next_to(t, DOWN, buff=0.15)
        return VGroup(t, bar)

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

    def _exam_tip(self, text):
        bg = RoundedRectangle(corner_radius=0.14, width=8.4, height=1.15,
                              color=RED, fill_color="#1A0000",
                              fill_opacity=1, stroke_width=2)
        bg.move_to(DOWN * 4.55)
        prefix = Text("▶ EXAM TIP:", font_size=13, color=RED, weight=BOLD)
        body   = Text(text, font_size=12, color=WHITE)
        row = VGroup(prefix, body).arrange(RIGHT, buff=0.14)
        row.move_to(bg.get_center())
        return VGroup(bg, row)

    def _fade_all(self, run_time=0.3):
        mobs = list(self.mobjects)
        if mobs:
            self.play(*[FadeOut(m) for m in mobs], run_time=run_time)
        self.clear()

    def _cta_section(self, headline):
        self._fade_all(0.3)
        self._bg()
        brand = self._brand()
        self.add(brand)
        self._sound("c")

        hl = Text(headline, font_size=36, color=WHITE, weight=BOLD, line_spacing=1.2)
        hl.move_to(UP * 3.0)
        self.play(Write(hl), run_time=0.7)

        site_bg = RoundedRectangle(corner_radius=0.18, width=5.8, height=0.92,
                                   fill_color=AMBER, fill_opacity=1, stroke_width=0)
        site_bg.next_to(hl, DOWN, buff=0.55)
        site_txt = Text("zerodaylabs.tech", font_size=26, color=BG, weight=BOLD)
        site_txt.move_to(site_bg.get_center())
        self.play(FadeIn(site_bg, scale=0.85), Write(site_txt), run_time=0.5)

        cta_txt = Text("LIKE  ·  SUBSCRIBE  ·  SHARE", font_size=22,
                       color=BLUE, weight=BOLD)
        cta_txt.move_to(DOWN * 1.6)
        self.play(FadeIn(cta_txt), run_time=0.4)

        sub_txt = Text("Daily CISSP & Security+ exam tips", font_size=16, color=GRAY)
        sub_txt.next_to(cta_txt, DOWN, buff=0.3)
        self.play(FadeIn(sub_txt), run_time=0.3)

        self._pad("c")


# ════════════════════════════════════════════════════════════════════════════
# SHORT 1 — CIA TRIAD
# ════════════════════════════════════════════════════════════════════════════
class CIATriad(_Short):
    ID = "c1"

    def construct(self):
        # ── Hook ────────────────────────────────────────────────────────────
        self._bg()
        brand = self._brand()
        self.add(brand)
        self._sound("h")

        miss = Text("Most candidates miss this.", font_size=30, color=GRAY)
        miss.move_to(UP * 3.5)
        self.play(FadeIn(miss), run_time=0.5)

        cia = Text("CIA TRIAD", font_size=64, color=BLUE, weight=BOLD)
        cia.move_to(UP * 1.5)
        self.play(Write(cia), run_time=0.8)

        go_txt = Text("30 seconds. Let's go.", font_size=24, color=AMBER)
        go_txt.next_to(cia, DOWN, buff=0.4)
        self.play(FadeIn(go_txt, shift=UP * 0.1), run_time=0.4)
        self._pad("h")

        # ── Main ────────────────────────────────────────────────────────────
        self._fade_all(0.3)
        self._bg()
        brand2 = self._brand()
        self.add(brand2)
        title_grp = self._scene_title("CIA TRIAD")
        self.play(Write(title_grp), run_time=0.5)
        self._sound("m")

        pillars = [
            ("C", "CONFIDENTIALITY",
             "Authorized access only.\nEncrypt · ACLs · Need-to-Know", BLUE),
            ("I", "INTEGRITY",
             "Data must not be altered.\nHash · Sign · Checksum", GREEN),
            ("A", "AVAILABILITY",
             "Systems up when needed.\nRedundancy · Backups · Failover", AMBER),
        ]

        cards = []
        for letter, title_str, body, color in pillars:
            card_bg = RoundedRectangle(corner_radius=0.2, width=8.2, height=2.75,
                                       color=color, fill_color=BG,
                                       fill_opacity=0.95, stroke_width=2.5)
            circ = Circle(radius=0.46, color=color, fill_color=color,
                          fill_opacity=0.15, stroke_width=2.5)
            circ.move_to(card_bg.get_left() + RIGHT * 0.72)
            ltr = Text(letter, font_size=34, color=color, weight=BOLD)
            ltr.move_to(circ.get_center())
            card_title = Text(title_str, font_size=19, color=color, weight=BOLD)
            card_body  = Text(body, font_size=13, color=WHITE, line_spacing=1.3)
            content = VGroup(card_title, card_body).arrange(DOWN, buff=0.1,
                                                             aligned_edge=LEFT)
            content.next_to(circ, RIGHT, buff=0.28)
            content.set_y(circ.get_y())
            cards.append(VGroup(card_bg, circ, ltr, content))

        cards_grp = VGroup(*cards).arrange(DOWN, buff=0.3)
        cards_grp.move_to(UP * 0.35)

        for card in cards:
            self.play(FadeIn(card, shift=RIGHT * 0.2), run_time=0.45)
            self.wait(10.0)

        tip = self._exam_tip("When a control fails — identify which CIA pillar is violated.")
        self.play(FadeIn(tip), run_time=0.4)
        self.wait(5.0)
        self._pad("m")

        # ── CTA ─────────────────────────────────────────────────────────────
        self._cta_section("Master the CIA Triad.\nMaster the CISSP.")


# ════════════════════════════════════════════════════════════════════════════
# SHORT 2 — DATA CLASSIFICATION
# ════════════════════════════════════════════════════════════════════════════
class DataClassification(_Short):
    ID = "c2"

    def construct(self):
        # ── Hook ────────────────────────────────────────────────────────────
        self._bg()
        brand = self._brand()
        self.add(brand)
        self._sound("h")

        q = Text("Which data needs\nthe MOST protection?",
                 font_size=38, color=WHITE, weight=BOLD, line_spacing=1.2)
        q.move_to(UP * 2.5)
        self.play(Write(q), run_time=0.8)

        sub = Text("Know these 4 levels cold.", font_size=26, color=AMBER)
        sub.next_to(q, DOWN, buff=0.5)
        self.play(FadeIn(sub, shift=UP * 0.1), run_time=0.4)
        self._pad("h")

        # ── Main ────────────────────────────────────────────────────────────
        self._fade_all(0.3)
        self._bg()
        brand2 = self._brand()
        self.add(brand2)
        title_grp = self._scene_title("DATA CLASSIFICATION")
        self.play(Write(title_grp), run_time=0.5)
        self._sound("m")

        tiers = [
            ("CONFIDENTIAL", "National security · Crypto keys",
             "Maximum access controls.", RED),
            ("SENSITIVE",    "PII · Medical records · Trade secrets",
             "Significant breach impact.", AMBER),
            ("PRIVATE",      "Employee records · Internal financials",
             "Internal use only.", BLUE),
            ("PUBLIC",       "Press releases · Website content",
             "No harm if disclosed.", GRAY),
        ]

        blocks = []
        for label, examples, note, color in tiers:
            blk_bg = RoundedRectangle(corner_radius=0.16, width=8.2, height=1.9,
                                      color=color, fill_color=BG,
                                      fill_opacity=0.94, stroke_width=2.2)
            lbl = Text(label, font_size=21, color=color, weight=BOLD)
            lbl.move_to(blk_bg.get_left() + RIGHT * 1.35)
            ex  = Text(examples, font_size=12, color=GRAY)
            nt  = Text(note, font_size=13, color=WHITE, weight=BOLD)
            right_grp = VGroup(ex, nt).arrange(DOWN, buff=0.07, aligned_edge=LEFT)
            right_grp.next_to(lbl, RIGHT, buff=0.28)
            right_grp.set_y(lbl.get_y())
            blocks.append(VGroup(blk_bg, lbl, right_grp))

        blk_grp = VGroup(*blocks).arrange(DOWN, buff=0.22)
        blk_grp.move_to(UP * 0.55)

        for blk in blocks:
            self.play(FadeIn(blk, shift=RIGHT * 0.2), run_time=0.4)
            self.wait(8.5)

        tip = self._exam_tip("Owner classifies · Classify at the HIGHEST sensitivity level.")
        self.play(FadeIn(tip), run_time=0.4)
        self.wait(5.0)
        self._pad("m")

        # ── CTA ─────────────────────────────────────────────────────────────
        self._cta_section("Know your data.\nPass the exam.")


# ════════════════════════════════════════════════════════════════════════════
# SHORT 3 — ZERO TRUST
# ════════════════════════════════════════════════════════════════════════════
class ZeroTrust(_Short):
    ID = "c3"

    def construct(self):
        # ── Hook ────────────────────────────────────────────────────────────
        self._bg()
        brand = self._brand()
        self.add(brand)
        self._sound("h")

        old = Text("Old security trusted\neveryone inside the network.",
                   font_size=28, color=GRAY, line_spacing=1.2)
        old.move_to(UP * 3.0)
        self.play(FadeIn(old), run_time=0.5)
        self.wait(1.2)

        kill = Text("Zero Trust\nkilled that idea.", font_size=42,
                    color=RED, weight=BOLD, line_spacing=1.1)
        kill.next_to(old, DOWN, buff=0.5)
        self.play(Write(kill), run_time=0.6)
        self._pad("h")

        # ── Main ────────────────────────────────────────────────────────────
        self._fade_all(0.3)
        self._bg()
        brand2 = self._brand()
        self.add(brand2)
        title_grp = self._scene_title("ZERO TRUST MODEL")
        self.play(Write(title_grp), run_time=0.5)
        self._sound("m")

        # Old vs Zero Trust comparison boxes
        old_bg = RoundedRectangle(corner_radius=0.16, width=3.9, height=2.5,
                                  color=GRAY, fill_color=BG,
                                  fill_opacity=0.94, stroke_width=1.8)
        old_bg.move_to(LEFT * 2.1 + UP * 3.6)
        old_lbl = Text("OLD MODEL", font_size=15, color=GRAY, weight=BOLD)
        old_lbl.move_to(old_bg.get_top() + DOWN * 0.28)
        old_body = Text("Castle + Moat\nInside = Trusted\nLateral movement\nfree after breach",
                        font_size=12, color=GRAY, line_spacing=1.2)
        old_body.move_to(old_bg.get_center() + DOWN * 0.2)

        zt_bg = RoundedRectangle(corner_radius=0.16, width=3.9, height=2.5,
                                 color=BLUE, fill_color=BG,
                                 fill_opacity=0.94, stroke_width=1.8)
        zt_bg.move_to(RIGHT * 2.1 + UP * 3.6)
        zt_lbl = Text("ZERO TRUST", font_size=15, color=BLUE, weight=BOLD)
        zt_lbl.move_to(zt_bg.get_top() + DOWN * 0.28)
        zt_body = Text("Verify everyone\nMin. access only\nAssume breach\nAlways verify",
                       font_size=12, color=WHITE, line_spacing=1.2)
        zt_body.move_to(zt_bg.get_center() + DOWN * 0.2)

        comparison = VGroup(
            VGroup(old_bg, old_lbl, old_body),
            VGroup(zt_bg,  zt_lbl,  zt_body),
        )
        self.play(FadeIn(comparison, lag_ratio=0.3), run_time=0.7)
        self.wait(8.0)

        # Three principles
        p_label = Text("THREE CORE PRINCIPLES", font_size=20, color=AMBER, weight=BOLD)
        p_label.move_to(UP * 1.3)
        self.play(Write(p_label), run_time=0.4)

        principles = [
            ("1  VERIFY EXPLICITLY",
             "Auth every request · Every time", BLUE),
            ("2  LEAST PRIVILEGE",
             "Min access · Just enough · Just in time", GREEN),
            ("3  ASSUME BREACH",
             "Segment · Monitor · Limit blast radius", RED),
        ]

        p_cards = []
        for title_str, body, color in principles:
            p_bg = RoundedRectangle(corner_radius=0.14, width=8.2, height=1.52,
                                    color=color, fill_color=BG,
                                    fill_opacity=0.94, stroke_width=2)
            p_title = Text(title_str, font_size=17, color=color, weight=BOLD)
            p_body  = Text(body, font_size=13, color=WHITE)
            p_content = VGroup(p_title, p_body).arrange(DOWN, buff=0.1,
                                                         aligned_edge=LEFT)
            p_content.move_to(p_bg.get_center() + LEFT * 0.5)
            p_cards.append(VGroup(p_bg, p_content))

        p_grp = VGroup(*p_cards).arrange(DOWN, buff=0.22)
        p_grp.move_to(DOWN * 1.3)

        for pc in p_cards:
            self.play(FadeIn(pc, shift=RIGHT * 0.2), run_time=0.4)
            self.wait(8.5)

        tip = self._exam_tip("Zero Trust removes implicit trust — even for internal users.")
        self.play(FadeIn(tip), run_time=0.4)
        self.wait(4.0)
        self._pad("m")

        # ── CTA ─────────────────────────────────────────────────────────────
        self._cta_section("Never Trust.\nAlways Verify.")


# ════════════════════════════════════════════════════════════════════════════
# SHORT 4 — INCIDENT RESPONSE
# ════════════════════════════════════════════════════════════════════════════
class IncidentResponse(_Short):
    ID = "c4"

    def construct(self):
        # ── Hook ────────────────────────────────────────────────────────────
        self._bg()
        brand = self._brand()
        self.add(brand)
        self._sound("h")

        big = Text("6 PHASES", font_size=72, color=BLUE, weight=BOLD)
        big.move_to(UP * 2.5)
        self.play(Write(big), run_time=0.7)

        sub1 = Text("NIST Incident Response", font_size=26, color=WHITE)
        sub1.next_to(big, DOWN, buff=0.35)
        sub2 = Text("Memorize this order.", font_size=22, color=AMBER)
        sub2.next_to(sub1, DOWN, buff=0.18)
        self.play(FadeIn(sub1), run_time=0.4)
        self.play(FadeIn(sub2), run_time=0.3)
        self._pad("h")

        # ── Main ────────────────────────────────────────────────────────────
        self._fade_all(0.3)
        self._bg()
        brand2 = self._brand()
        self.add(brand2)
        title_grp = self._scene_title("INCIDENT RESPONSE")
        self.play(Write(title_grp), run_time=0.5)
        self._sound("m")

        steps = [
            ("1", "PREPARATION",
             "Policies · Tools · Training before incident.", BLUE),
            ("2", "DETECTION & ANALYSIS",
             "Identify breach · Scope & severity.", GREEN),
            ("3", "CONTAINMENT",
             "Short-term isolation → Long-term.", AMBER),
            ("4", "ERADICATION",
             "Remove root cause · Patch · Eliminate.", RED),
            ("5", "RECOVERY",
             "Restore safely · Monitor for reinfection.", TEAL),
            ("6", "POST-INCIDENT",
             "Lessons learned within 2 weeks.", GRAY),
        ]

        step_cards = []
        for num, name, desc, color in steps:
            s_bg = RoundedRectangle(corner_radius=0.14, width=8.2, height=1.35,
                                    color=color, fill_color=BG,
                                    fill_opacity=0.94, stroke_width=2)
            circ = Circle(radius=0.34, color=color,
                          fill_color=color, fill_opacity=0.2, stroke_width=2)
            circ.move_to(s_bg.get_left() + RIGHT * 0.5)
            num_txt = Text(num, font_size=20, color=color, weight=BOLD)
            num_txt.move_to(circ.get_center())
            s_name = Text(name, font_size=15, color=color, weight=BOLD)
            s_desc = Text(desc, font_size=12, color=WHITE)
            s_content = VGroup(s_name, s_desc).arrange(DOWN, buff=0.06,
                                                        aligned_edge=LEFT)
            s_content.next_to(circ, RIGHT, buff=0.22)
            s_content.set_y(circ.get_y())
            step_cards.append(VGroup(s_bg, circ, num_txt, s_content))

        steps_grp = VGroup(*step_cards).arrange(DOWN, buff=0.17)
        steps_grp.move_to(UP * 0.2)

        for sc in step_cards:
            self.play(FadeIn(sc, shift=RIGHT * 0.15), run_time=0.35)
            self.wait(6.5)

        tip = self._exam_tip("Exam tests ORDER — Preparation ALWAYS comes first.")
        self.play(FadeIn(tip), run_time=0.4)
        self.wait(4.0)
        self._pad("m")

        # ── CTA ─────────────────────────────────────────────────────────────
        self._cta_section("Know the phases.\nPass the exam.")


# ════════════════════════════════════════════════════════════════════════════
# SHORT 5 — EXAM TRAPS (MANAGER MINDSET)
# ════════════════════════════════════════════════════════════════════════════
class ExamTraps(_Short):
    ID = "c5"

    def construct(self):
        # ── Hook ────────────────────────────────────────────────────────────
        self._bg()
        brand = self._brand()
        self.add(brand)
        self._sound("h")

        trap = Text("Most people fail CISSP\nthinking like a technician.",
                    font_size=32, color=WHITE, weight=BOLD, line_spacing=1.2)
        trap.move_to(UP * 2.8)
        self.play(Write(trap), run_time=0.8)

        fix = Text("Here's the mindset shift.", font_size=24, color=AMBER)
        fix.next_to(trap, DOWN, buff=0.5)
        self.play(FadeIn(fix, shift=UP * 0.1), run_time=0.4)
        self._pad("h")

        # ── Main ────────────────────────────────────────────────────────────
        self._fade_all(0.3)
        self._bg()
        brand2 = self._brand()
        self.add(brand2)
        title_grp = self._scene_title("MANAGER MINDSET", color=AMBER)
        self.play(Write(title_grp), run_time=0.5)
        self._sound("m")

        # Column headers
        hdr_wrong = Text("TECHNICIAN", font_size=19, color=RED, weight=BOLD)
        hdr_right = Text("MANAGER", font_size=19, color=GREEN, weight=BOLD)
        hdr_wrong.move_to(LEFT * 2.1 + UP * 4.85)
        hdr_right.move_to(RIGHT * 2.1 + UP * 4.85)
        col_div = Line(UP * 4.6 + ORIGIN, DOWN * 3.8 + ORIGIN,
                       color=GRAY, stroke_width=0.8, stroke_opacity=0.45)
        self.play(FadeIn(hdr_wrong), FadeIn(hdr_right),
                  Create(col_div), run_time=0.5)

        rows_data = [
            ("Fix the\ntechnology", "Assess the\nrisk first",      BLUE),
            ("Ignore\nthe law",     "Comply first —\nalways",       RED),
            ("Deploy a\ntool",      "Train the\npeople first",      GREEN),
            ("Save the\ndata",      "Save human\nlives first",      AMBER),
        ]

        row_objs = []
        for wrong, right, color in rows_data:
            hl = RoundedRectangle(corner_radius=0.1, width=8.2, height=1.35,
                                  color=color, fill_color=color,
                                  fill_opacity=0.07, stroke_width=1.2)
            w_txt = Text(wrong, font_size=17, color="#CC6666",
                         line_spacing=1.1, weight=BOLD)
            r_txt = Text(right, font_size=17, color=GREEN,
                         line_spacing=1.1, weight=BOLD)
            w_txt.move_to(LEFT * 2.1)
            r_txt.move_to(RIGHT * 2.1)
            row_objs.append(VGroup(hl, w_txt, r_txt))

        rows_grp = VGroup(*row_objs).arrange(DOWN, buff=0.2)
        rows_grp.move_to(UP * 1.0)

        for row in row_objs:
            self.play(FadeIn(row, shift=UP * 0.12), run_time=0.4)
            self.wait(8.5)

        tip = self._exam_tip("Think like a senior security MANAGER — not an engineer.")
        self.play(FadeIn(tip), run_time=0.4)
        self.wait(4.0)
        self._pad("m")

        # ── CTA ─────────────────────────────────────────────────────────────
        self._cta_section("Think like a manager.\nPass the CISSP.")
