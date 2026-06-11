from manim import *
import json
import os
import random

# ─── Color Palette ───────────────────────────────────────────────
BG    = "#0A0E1A"
BLUE  = "#00C8FF"
AMBER = "#F5A623"
GREEN = "#39D353"
RED   = "#FF4D4D"
MONO  = "DejaVu Sans Mono"

config.background_color = BG

AUDIO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio")

# ─── Durations (seconds) per scene — synced to generated audio ──
# generate_narration.py writes audio/durations.json; fall back to the
# Pico TTS timings if it hasn't been run yet.
_DUR_DEFAULTS = {
    "s1": 29.3,
    "s2": 21.4,
    "s3": 55.5,
    "s4": 64.9,
    "s5": 27.6,
    "s6": 58.9,
    "s7": 40.0,
    "s8": 21.6,
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
#  MASTER SCENE  —  manim -qh encryption_explainer.py MasterScene
# ═══════════════════════════════════════════════════════════════════
class MasterScene(Scene):
    def construct(self):
        self.s1_hook()
        self.s2_core_question()
        self.s3_encryption()
        self.s4_hashing()
        self.s5_comparison()
        self.s6_use_cases()
        self.s7_never_confuse()
        self.s8_outro()

    # ── helpers ──────────────────────────────────────────────────
    def _sound(self, key):
        self.add_sound(f"{AUDIO}/{key}.mp3")

    def _pad(self, key, used_seconds):
        """Wait out the remaining time in this scene's audio slot."""
        remaining = DUR[key] - used_seconds - 0.6   # 0.6 for fade_all
        if remaining > 0:
            self.wait(remaining)

    # ── SCENE 1 — Hook  (29.3 s) ─────────────────────────────────
    def s1_hook(self):
        # NARRATION s1: "Look at your screen right now…"
        self._sound("s1")                                   # t=0

        rng = random.Random(42)
        bits = []
        for r in range(14):
            for c in range(32):
                b = Text(rng.choice(["0","1"]), font_size=16,
                         color=BLUE, fill_opacity=0.25)
                b.move_to(np.array([-7.5 + c*0.5, -4 + r*0.58, 0]))
                bits.append(b)
        stream = VGroup(*bits)
        self.play(FadeIn(stream, lag_ratio=0.005), run_time=1.8)  # t≈1.8

        for _ in range(4):
            sample = rng.sample(bits, 18)
            anims = [b.animate.set_color(rng.choice([BLUE, WHITE, AMBER]))
                       .set_opacity(rng.uniform(0.15, 0.5)) for b in sample]
            self.play(*anims, run_time=0.25)                # t≈2.8

        self.wait(1.0)                                      # t≈3.8

        # Lock icon
        shackle = Arc(radius=0.38, start_angle=0, angle=PI,
                      color=AMBER, stroke_width=7)
        shackle.move_to(UP * 0.85)
        body = RoundedRectangle(corner_radius=0.1, width=0.85, height=0.65,
                                color=AMBER, fill_color=AMBER, fill_opacity=0.9,
                                stroke_width=0)
        body.next_to(shackle, DOWN, buff=-0.02)
        keyhole = Circle(radius=0.1, color=BG, fill_color=BG,
                         fill_opacity=1, stroke_width=0)
        keyhole.move_to(body.get_center() + UP*0.05)
        lock = VGroup(body, shackle, keyhole)
        lock.move_to(ORIGIN + UP*0.6)

        self.play(stream.animate.set_opacity(0.12), run_time=0.4)
        self.play(GrowFromCenter(lock), run_time=0.9)       # t≈5.1
        self.wait(1.5)                                      # t≈6.6

        title = heading("What Is Encryption?", size=52, color=WHITE)
        title.next_to(lock, DOWN, buff=0.45)
        sub   = Text("(And Why It's Not the Same as Hashing)",
                     font_size=26, color=BLUE)
        sub.next_to(title, DOWN, buff=0.18)

        self.play(Write(title), run_time=1.2)               # t≈7.8
        self.play(FadeIn(sub, shift=UP*0.15), run_time=0.7) # t≈8.5

        # Glow flash
        self.play(title.animate.set_color(BLUE), run_time=0.25)
        self.play(title.animate.set_color(WHITE), run_time=0.25) # t≈9.0

        self.wait(2.0)                                      # t≈11.0

        # Subtitle pop — draw attention while narrator says "not the same thing"
        self.play(sub.animate.scale(1.05).set_color(AMBER), run_time=0.4)
        self.play(sub.animate.scale(1/1.05).set_color(BLUE), run_time=0.4) # t≈11.8

        # ~s1 total animation so far ≈ 11.8 s, target 29.3 s
        self._pad("s1", 11.8)                               # waits ~17s
        fade_all(self)

    # ── SCENE 2 — Core Question  (21.4 s) ────────────────────────
    def s2_core_question(self):
        # NARRATION s2: "Here is the core question…"
        self._sound("s2")                                   # t=0

        enc_rect  = Rectangle(width=4.2, height=2.6, color=BLUE,
                               fill_color="#030D1A", fill_opacity=0.9, stroke_width=3)
        hash_rect = Rectangle(width=4.2, height=2.6, color=AMBER,
                               fill_color="#140A00", fill_opacity=0.9, stroke_width=3)
        enc_rect.move_to(LEFT  * 3.3)
        hash_rect.move_to(RIGHT * 3.3)
        enc_lbl  = heading("ENCRYPTION", size=28, color=BLUE)
        enc_lbl.move_to(enc_rect.get_center())
        hash_lbl = heading("HASHING", size=28, color=AMBER)
        hash_lbl.move_to(hash_rect.get_center())
        neq = Text("≠", font_size=80, color=WHITE)

        self.play(Create(enc_rect), Create(hash_rect), run_time=0.9) # t≈0.9
        self.play(Write(enc_lbl),   Write(hash_lbl),   run_time=0.7) # t≈1.6
        self.play(Write(neq),                          run_time=0.5) # t≈2.1
        self.wait(1.0)                                               # t≈3.1

        q_enc  = Text("?", font_size=52, color=BLUE,  weight=BOLD)
        q_hash = Text("?", font_size=52, color=AMBER, weight=BOLD)
        q_enc.next_to(enc_rect,  UP, buff=0.3)
        q_hash.next_to(hash_rect, UP, buff=0.3)
        self.play(FadeIn(q_enc, scale=0.4), FadeIn(q_hash, scale=0.4), run_time=0.7) # t≈3.8
        self.wait(1.0)                                               # t≈4.8

        caption = Text("Both scramble data. But they solve completely different problems.",
                       font_size=22, color=WHITE)
        caption.to_edge(DOWN, buff=0.6)
        self.play(Write(caption), run_time=1.4)                      # t≈6.2

        # Animate ≠ to reinforce the point
        self.play(neq.animate.scale(1.2).set_color(RED),  run_time=0.4)
        self.play(neq.animate.scale(1/1.2).set_color(WHITE), run_time=0.4) # t≈7.0

        self._pad("s2", 7.0)
        fade_all(self)

    # ── SCENE 3 — What Is Encryption?  (55.5 s) ──────────────────
    def s3_encryption(self):
        # NARRATION s3: "Let us start with encryption…"
        self._sound("s3")                                   # t=0

        stitle = scene_title(self, "What Is Encryption?", color=BLUE) # t≈0.7
        self.wait(1.0)                                      # t≈1.7

        # Plaintext panel
        pt_box = Rectangle(width=3.2, height=1.3, color=GREEN, stroke_width=2,
                           fill_color="#011A00", fill_opacity=0.85)
        pt_box.move_to(LEFT * 4.5 + UP * 0.8)
        pt_lbl = Text("PLAINTEXT", font_size=14, color=GREEN)
        pt_lbl.next_to(pt_box, UP, buff=0.1)
        pt_txt = mono('"Hello, Alice"', size=20, color=GREEN)
        pt_txt.move_to(pt_box.get_center())

        self.play(Create(pt_box), FadeIn(pt_lbl), Write(pt_txt), run_time=0.9) # t≈2.6
        self.wait(2.0)                                      # t≈4.6

        # Ciphertext panel
        ct_box = Rectangle(width=3.2, height=1.3, color=BLUE, stroke_width=2,
                           fill_color="#00101A", fill_opacity=0.85)
        ct_box.move_to(RIGHT * 4.5 + UP * 0.8)
        ct_lbl = Text("CIPHERTEXT", font_size=14, color=BLUE)
        ct_lbl.next_to(ct_box, UP, buff=0.1)
        ct_txt = mono('"X9$kL#2mQ@"', size=20, color=BLUE)
        ct_txt.move_to(ct_box.get_center())

        fwd = Arrow(pt_box.get_right(), ct_box.get_left(), color=AMBER,
                    stroke_width=4, buff=0.1, max_tip_length_to_length_ratio=0.12)
        fwd_lbl = Text("🔑 Key + Algorithm", font_size=18, color=AMBER)
        fwd_lbl.next_to(fwd, UP, buff=0.14)

        self.play(GrowArrow(fwd), Write(fwd_lbl), run_time=0.8)     # t≈5.4
        self.play(Create(ct_box), FadeIn(ct_lbl), Write(ct_txt), run_time=0.9) # t≈6.3
        self.wait(2.5)                                      # t≈8.8

        # Reverse arrow
        rev = Arrow(ct_box.get_left(), pt_box.get_right(), color=GREEN,
                    stroke_width=4, buff=0.1, max_tip_length_to_length_ratio=0.12)
        rev.shift(DOWN * 0.55)
        rev_lbl = Text("🔑 Same Key (or Paired Key)", font_size=16, color=GREEN)
        rev_lbl.next_to(rev, DOWN, buff=0.12)
        self.play(GrowArrow(rev), Write(rev_lbl), run_time=0.8)     # t≈9.6

        reversible = heading("↔  Reversible", size=24, color=GREEN)
        rev_pill = SurroundingRectangle(reversible, color=GREEN, buff=0.15, corner_radius=0.12)
        reversible.move_to(DOWN * 1.85)
        rev_pill.move_to(DOWN * 1.85)
        self.play(Write(reversible), Create(rev_pill), run_time=0.7) # t≈10.3
        self.wait(3.0)                                      # t≈13.3

        # Transition to sub-types
        self.play(
            FadeOut(fwd), FadeOut(fwd_lbl),
            FadeOut(rev), FadeOut(rev_lbl),
            FadeOut(reversible), FadeOut(rev_pill),
            run_time=0.4
        )                                                   # t≈13.7

        # Sub-type cards
        sym_card = RoundedRectangle(corner_radius=0.15, width=3.8, height=1.7,
                                    color=BLUE, fill_color="#040D1A",
                                    fill_opacity=0.95, stroke_width=2)
        sym_card.move_to(LEFT * 2.2 + DOWN * 0.4)
        sym_h = Text("🗝  Symmetric", font_size=20, color=BLUE, weight=BOLD)
        sym_h.next_to(sym_card.get_top(), DOWN, buff=0.22)
        sym_d = Text("AES — same key to lock & unlock\n\nUsed in: WiFi, banks, storage",
                     font_size=15, color=WHITE, line_spacing=1.3)
        sym_d.move_to(sym_card.get_center() + DOWN * 0.15)

        asym_card = RoundedRectangle(corner_radius=0.15, width=3.8, height=1.7,
                                     color=AMBER, fill_color="#140A00",
                                     fill_opacity=0.95, stroke_width=2)
        asym_card.move_to(RIGHT * 2.2 + DOWN * 0.4)
        asym_h = Text("🔐 Asymmetric", font_size=20, color=AMBER, weight=BOLD)
        asym_h.next_to(asym_card.get_top(), DOWN, buff=0.22)
        asym_d = Text("RSA — public key encrypts,\nprivate key decrypts\n\nUsed in: HTTPS, email",
                      font_size=15, color=WHITE, line_spacing=1.3)
        asym_d.move_to(asym_card.get_center() + DOWN * 0.12)

        self.play(FadeIn(sym_card), Write(sym_h), Write(sym_d), run_time=1.0) # t≈14.7
        self.wait(1.5)
        self.play(FadeIn(asym_card), Write(asym_h), Write(asym_d), run_time=1.0) # t≈17.2
        self.wait(2.0)                                      # t≈19.2

        # Highlight symmetric in context
        self.play(Indicate(sym_card, color=BLUE, scale_factor=1.04), run_time=0.8)
        self.wait(1.5)
        self.play(Indicate(asym_card, color=AMBER, scale_factor=1.04), run_time=0.8) # t≈22.3

        self._pad("s3", 22.3)
        fade_all(self)

    # ── SCENE 4 — What Is Hashing?  (64.9 s) ─────────────────────
    def s4_hashing(self):
        # NARRATION s4: "Now let us talk about hashing…"
        self._sound("s4")                                   # t=0

        stitle = scene_title(self, "What Is Hashing?", color=AMBER) # t≈0.7
        self.wait(1.0)                                      # t≈1.7

        pt_box = Rectangle(width=3.0, height=1.2, color=GREEN, stroke_width=2,
                           fill_color="#011A00", fill_opacity=0.85)
        pt_box.move_to(LEFT * 4.2 + UP * 1.1)
        pt_lbl = Text("INPUT", font_size=13, color=GREEN)
        pt_lbl.next_to(pt_box, UP, buff=0.1)
        pt_txt = mono('"Hello, Alice"', size=18, color=GREEN)
        pt_txt.move_to(pt_box.get_center())

        hash_box = Rectangle(width=3.5, height=1.2, color=AMBER, stroke_width=2,
                             fill_color="#140A00", fill_opacity=0.85)
        hash_box.move_to(RIGHT * 4.2 + UP * 1.1)
        hash_lbl = Text("HASH (SHA-256)", font_size=13, color=AMBER)
        hash_lbl.next_to(hash_box, UP, buff=0.1)
        hash_txt = mono("a3f5c9...d2e1", size=18, color=AMBER)
        hash_txt.move_to(hash_box.get_center())

        fwd = Arrow(pt_box.get_right(), hash_box.get_left(), color=AMBER,
                    stroke_width=4, buff=0.1, max_tip_length_to_length_ratio=0.12)
        fn_lbl = Text("Hash Function (SHA-256)", font_size=17, color=AMBER)
        fn_lbl.next_to(fwd, UP, buff=0.14)

        self.play(Create(pt_box), FadeIn(pt_lbl), Write(pt_txt), run_time=0.7) # t≈2.4
        self.wait(1.5)
        self.play(GrowArrow(fwd), Write(fn_lbl), run_time=0.7)  # t≈4.6
        self.play(Create(hash_box), FadeIn(hash_lbl), Write(hash_txt), run_time=0.8) # t≈5.4
        self.wait(1.5)                                      # t≈6.9

        # Broken reverse
        rev_fail = Arrow(hash_box.get_left(), pt_box.get_right(), color=RED,
                         stroke_width=4, buff=0.1, max_tip_length_to_length_ratio=0.12)
        rev_fail.shift(DOWN * 0.52)
        self.play(GrowArrow(rev_fail), run_time=0.5)        # t≈7.4
        x_mark = Text("✗", font_size=52, color=RED, weight=BOLD)
        x_mark.move_to(rev_fail.get_center() + UP * 0.45)
        no_rev = Text("Cannot Reverse", font_size=20, color=RED, weight=BOLD)
        no_rev.next_to(rev_fail, DOWN, buff=0.14)

        self.play(
            Write(x_mark), Write(no_rev),
            Flash(rev_fail.get_center(), color=RED, num_lines=8, flash_radius=0.6),
            run_time=0.8
        )                                                   # t≈8.2
        self.wait(2.0)                                      # t≈10.2
        self.play(FadeOut(rev_fail), FadeOut(x_mark), FadeOut(no_rev), run_time=0.35) # t≈10.6

        # ── Property 1: Deterministic ──
        p1 = Text("Property 1 — Deterministic", font_size=21, color=WHITE, weight=BOLD)
        p1.move_to(UP * 0.0)
        self.play(Write(p1), run_time=0.6)                  # t≈11.2
        self.wait(1.5)

        run1 = mono("Run 1 → a3f5c9...d2e1  ✓", size=17, color=GREEN)
        run2 = mono("Run 2 → a3f5c9...d2e1  ✓", size=17, color=GREEN)
        run1.next_to(p1, DOWN, buff=0.25)
        run2.next_to(run1, DOWN, buff=0.15)
        self.play(FadeIn(run1, shift=RIGHT*0.3), run_time=0.45) # t≈13.65
        self.wait(0.8)
        self.play(FadeIn(run2, shift=RIGHT*0.3), run_time=0.45) # t≈14.9

        match_lbl = Text("✓ Same output, every time", font_size=19, color=GREEN)
        match_lbl.next_to(run2, DOWN, buff=0.2)
        self.play(FadeIn(match_lbl), run_time=0.5)          # t≈15.4
        self.wait(2.5)                                      # t≈17.9
        self.play(FadeOut(p1), FadeOut(run1), FadeOut(run2),
                  FadeOut(match_lbl), run_time=0.4)         # t≈18.3

        # ── Property 2: Avalanche effect ──
        p2 = Text("Property 2 — Avalanche Effect", font_size=21, color=WHITE, weight=BOLD)
        p2.move_to(UP * 0.0)
        self.play(Write(p2), run_time=0.6)                  # t≈18.9
        self.wait(1.5)

        mod_txt = mono('"Hello, Alice!"', size=18, color=AMBER)
        mod_txt.move_to(pt_txt.get_center())
        changed = Text("↑ 1 char added", font_size=13, color=AMBER)
        changed.next_to(pt_box, DOWN, buff=0.1)
        self.play(Transform(pt_txt, mod_txt), FadeIn(changed), run_time=0.7) # t≈21.1
        self.wait(1.0)

        new_hash = mono("9f2a1b...c7d4", size=18, color=RED)
        new_hash.move_to(hash_txt.get_center())
        self.play(Transform(hash_txt, new_hash), run_time=0.4) # t≈22.5
        self.play(
            Flash(hash_box.get_center(), color=RED, num_lines=10, flash_radius=0.9),
            run_time=0.5
        )                                                   # t≈23.0

        avalanche = Text("⚡ Completely different hash!", font_size=19, color=RED)
        avalanche.next_to(p2, DOWN, buff=0.28)
        self.play(Write(avalanche), run_time=0.6)           # t≈23.6
        self.wait(2.0)

        ow = heading("→|  One-Way Function", size=22, color=AMBER)
        ow.next_to(avalanche, DOWN, buff=0.3)
        ow_box = SurroundingRectangle(ow, color=AMBER, buff=0.16, corner_radius=0.12)
        self.play(Write(ow), Create(ow_box), run_time=0.8)  # t≈26.4

        self._pad("s4", 26.4)
        fade_all(self)

    # ── SCENE 5 — Comparison Table  (27.6 s) ─────────────────────
    def s5_comparison(self):
        # NARRATION s5: "Let us lock in the differences side by side…"
        self._sound("s5")                                   # t=0

        stitle = scene_title(self, "Encryption vs Hashing", color=WHITE) # t≈0.7
        self.wait(0.8)                                      # t≈1.5

        cols   = [-4.0, 0.3, 4.6]
        widths = [3.8,  3.8,  3.8]
        rh     = 0.72
        top_y  = 1.85

        headers = [("Property", WHITE), ("Encryption", BLUE), ("Hashing", AMBER)]
        for (h, c), x, w in zip(headers, cols, widths):
            rect = Rectangle(width=w, height=rh,
                             fill_color="#0F1525", fill_opacity=1,
                             stroke_color=c, stroke_width=2)
            rect.move_to([x, top_y, 0])
            t = Text(h, font_size=19, color=c, weight=BOLD)
            t.move_to(rect.get_center())
            self.play(Create(rect), Write(t), run_time=0.3)

        self.wait(0.5)                                      # t≈3.0

        rows = [
            ["Reversible?",        "✅ Yes",           "❌ No"],
            ["Uses a Key?",         "✅ Yes",           "❌ No"],
            ["Consistent output?",  "✅ Yes",           "✅ Yes"],
            ["Primary use case",    "Secure transit",  "Passwords / Integrity"],
        ]

        def cell_color(cell, col):
            if "✅" in cell: return GREEN
            if "❌" in cell: return RED
            return BLUE if col == 1 else (AMBER if col == 2 else WHITE)

        elapsed = 3.0
        for ri, row in enumerate(rows):
            y = top_y - (ri + 1) * rh
            group = VGroup()
            for ci, (cell, x, w) in enumerate(zip(row, cols, widths)):
                rect = Rectangle(width=w, height=rh,
                                 fill_color="#050810", fill_opacity=1,
                                 stroke_color="#1A2035", stroke_width=1)
                rect.move_to([x, y, 0])
                fs = 16 if len(cell) > 14 else 18
                t = Text(cell, font_size=fs, color=cell_color(cell, ci))
                t.move_to(rect.get_center())
                group.add(rect, t)
            self.play(FadeIn(group, shift=LEFT*0.25), run_time=0.6)
            self.wait(0.8)
            elapsed += 1.4

        # t ≈ 8.6
        self._pad("s5", elapsed)
        fade_all(self)

    # ── SCENE 6 — Real-World Use Cases  (58.9 s) ─────────────────
    def s6_use_cases(self):
        # NARRATION s6: "Where do we actually see these in action?…"
        self._sound("s6")                                   # t=0

        stitle = scene_title(self, "Real-World Use Cases", color=WHITE) # t≈0.7
        self.wait(1.0)                                      # t≈1.7

        # ── HTTPS / Encryption ──
        enc_sub = Text("Encryption: HTTPS / TLS", font_size=22, color=BLUE, weight=BOLD)
        enc_sub.move_to(UP * 1.7)
        self.play(Write(enc_sub), run_time=0.6)             # t≈2.3

        browser = RoundedRectangle(corner_radius=0.15, width=2.8, height=1.2,
                                   color=BLUE, fill_color="#020D1A", fill_opacity=0.9)
        browser.move_to(LEFT * 4 + UP * 0.3)
        b_lbl = Text("🌐  Browser", font_size=18, color=BLUE)
        b_lbl.move_to(browser.get_center())

        server = RoundedRectangle(corner_radius=0.15, width=2.8, height=1.2,
                                  color=GREEN, fill_color="#011A00", fill_opacity=0.9)
        server.move_to(RIGHT * 4 + UP * 0.3)
        s_lbl = Text("🖥  Bank Server", font_size=17, color=GREEN)
        s_lbl.move_to(server.get_center())

        self.play(FadeIn(browser), Write(b_lbl),
                  FadeIn(server),  Write(s_lbl), run_time=0.7) # t≈3.0

        top_line = Line(browser.get_right(), server.get_left(),
                        color=BLUE, stroke_width=3).shift(UP*0.18)
        bot_line = Line(browser.get_right(), server.get_left(),
                        color=BLUE, stroke_width=3).shift(DOWN*0.18)
        lock_lbl = Text("🔒  AES-256 Encrypted", font_size=17, color=BLUE)
        lock_lbl.move_to(UP * 0.3)
        self.play(Create(top_line), Create(bot_line), run_time=0.5)
        self.play(Write(lock_lbl), run_time=0.5)            # t≈4.0

        cap1 = Text("Your bank encrypts data in transit (TLS/AES)", font_size=17, color=WHITE)
        cap1.move_to(DOWN * 0.5)
        self.play(Write(cap1), run_time=0.8)                # t≈4.8
        self.wait(3.5)                                      # t≈8.3

        self.play(
            FadeOut(enc_sub), FadeOut(browser), FadeOut(b_lbl),
            FadeOut(server),  FadeOut(s_lbl),  FadeOut(top_line),
            FadeOut(bot_line), FadeOut(lock_lbl), FadeOut(cap1),
            run_time=0.5
        )                                                   # t≈8.8

        # ── Password Hashing ──
        hash_sub = Text("Hashing: Password Storage", font_size=22, color=AMBER, weight=BOLD)
        hash_sub.move_to(UP * 1.7)
        self.play(Write(hash_sub), run_time=0.6)            # t≈9.4

        form = RoundedRectangle(corner_radius=0.18, width=2.8, height=1.5,
                                color=BLUE, fill_color="#020D1A", fill_opacity=0.9)
        form.move_to(LEFT * 4 + UP * 0.3)
        f_title = Text("Login Form", font_size=15, color=BLUE)
        f_title.next_to(form.get_top(), DOWN, buff=0.2)
        f_pw = mono("pw: ••••••••", size=15, color=WHITE)
        f_pw.move_to(form.get_center() + DOWN * 0.1)
        self.play(FadeIn(form), Write(f_title), Write(f_pw), run_time=0.7) # t≈10.1
        self.wait(1.5)

        pw_arr = Arrow(LEFT*2.2 + UP*0.3, RIGHT*0.5 + UP*0.3,
                       color=AMBER, stroke_width=3, buff=0.1,
                       max_tip_length_to_length_ratio=0.1)
        fn_txt = Text("bcrypt / SHA-256", font_size=15, color=AMBER)
        fn_txt.next_to(pw_arr, UP, buff=0.1)
        self.play(GrowArrow(pw_arr), Write(fn_txt), run_time=0.6) # t≈12.2

        db = RoundedRectangle(corner_radius=0.18, width=3.2, height=1.5,
                              color=AMBER, fill_color="#140A00", fill_opacity=0.9)
        db.move_to(RIGHT * 3.8 + UP * 0.3)
        db_title = Text("Database", font_size=15, color=AMBER)
        db_title.next_to(db.get_top(), DOWN, buff=0.2)
        db_hash = mono("$2b$12$eW5...\n3f9a1b...c2d", size=12, color=AMBER)
        db_hash.move_to(db.get_center() + DOWN * 0.1)
        self.play(FadeIn(db), Write(db_title), Write(db_hash), run_time=0.8) # t≈13.0
        self.wait(2.5)                                      # t≈15.5

        # Forgot password bubble
        bubble = RoundedRectangle(corner_radius=0.18, width=6.2, height=0.85,
                                  color=GREEN, fill_color="#011A00",
                                  fill_opacity=0.95, stroke_width=2)
        bubble.move_to(DOWN * 1.55)
        b_txt = Text('"Forgot password?" → site can\'t look it up → must RESET',
                     font_size=15, color=GREEN)
        b_txt.move_to(bubble.get_center())
        self.play(FadeIn(bubble, scale=0.85), Write(b_txt), run_time=0.8) # t≈16.3
        self.wait(3.0)                                      # t≈19.3

        # 🧂 Salt bonus callout
        salt_bg = RoundedRectangle(corner_radius=0.15, width=8.0, height=1.3,
                                   color="#666666", fill_color="#0A0A1A",
                                   fill_opacity=0.97, stroke_width=1.5)
        salt_bg.move_to(DOWN * 2.8)
        salt_line1 = Text("🧂 Salt: password + random_salt  →  hash",
                         font_size=15, color="#CCCCCC")
        salt_line2 = Text("Defeats rainbow table attacks — same password, different hash",
                         font_size=14, color="#999999")
        salt_line1.next_to(salt_bg.get_top(), DOWN, buff=0.2)
        salt_line2.next_to(salt_line1, DOWN, buff=0.1)

        self.play(FadeIn(salt_bg), Write(salt_line1), run_time=0.7) # t≈20.0
        self.play(Write(salt_line2), run_time=0.6)          # t≈20.6
        self.wait(3.0)                                      # t≈23.6

        self._pad("s6", 23.6)
        fade_all(self)

    # ── SCENE 7 — Never Confuse These  (40.0 s) ──────────────────
    def s7_never_confuse(self):
        # NARRATION s7: "Here is the rule…"
        self._sound("s7")                                   # t=0

        stitle = scene_title(self, "Right Tool. Right Job.", color=WHITE) # t≈0.7
        self.wait(1.0)                                      # t≈1.7

        enc_box  = Rectangle(width=4.0, height=2.2, color=BLUE,  stroke_width=3,
                             fill_color="#030D1A", fill_opacity=0.85)
        hash_box = Rectangle(width=4.0, height=2.2, color=AMBER, stroke_width=3,
                             fill_color="#140A00", fill_opacity=0.85)
        enc_box.move_to(LEFT  * 3.1 + UP * 0.3)
        hash_box.move_to(RIGHT * 3.1 + UP * 0.3)
        enc_lbl  = heading("ENCRYPTION", size=26, color=BLUE)
        enc_lbl.move_to(enc_box.get_center())
        hash_lbl = heading("HASHING",    size=26, color=AMBER)
        hash_lbl.move_to(hash_box.get_center())

        self.play(Create(enc_box),  Write(enc_lbl),
                  Create(hash_box), Write(hash_lbl), run_time=0.8)  # t≈2.5

        # Scenario helper
        def scenario(question, answer, target_box, answer_color, t_elapsed):
            q = Text(question, font_size=20, color=WHITE)
            q.move_to(DOWN * 1.7)
            a = Text(answer, font_size=21, color=answer_color, weight=BOLD)
            a.move_to(DOWN * 2.45)
            self.play(Write(q), run_time=0.6)
            self.wait(0.5)
            self.play(Indicate(target_box, color=answer_color, scale_factor=1.06), run_time=0.7)
            self.play(FadeIn(a), run_time=0.4)
            self.wait(1.5)
            self.play(FadeOut(q), FadeOut(a), run_time=0.3)
            return t_elapsed + 4.0

        elapsed = 2.5
        elapsed = scenario("Storing a password securely?",
                           "✅ Use Hashing", hash_box, GREEN, elapsed)  # +4 → t≈6.5
        self.wait(0.5)
        elapsed += 0.5
        elapsed = scenario("Sending a secret someone must read?",
                           "✅ Use Encryption", enc_box, BLUE, elapsed) # +4 → t≈11.0
        self.wait(0.5)
        elapsed += 0.5

        # Scenario C — bad practice
        bad_q = Text("Encrypting passwords instead of hashing?", font_size=20, color=WHITE)
        bad_q.move_to(DOWN * 1.7)
        self.play(Write(bad_q), run_time=0.6)               # t≈12.1
        self.wait(0.8)

        cross = Cross(enc_box, color=RED, stroke_width=6)
        self.play(Create(cross), run_time=0.5)
        self.play(Flash(enc_box.get_center(), color=RED, num_lines=12, flash_radius=1.6), run_time=0.5)
        elapsed += 2.4                                      # t≈14.1... wait actually

        warn = Text("❌  Key leaks → ALL passwords instantly exposed",
                    font_size=20, color=RED, weight=BOLD)
        warn.move_to(DOWN * 2.45)
        self.play(Write(warn), run_time=0.7)                # +0.7

        elapsed = 15.0  # conservative
        self._pad("s7", elapsed)
        fade_all(self)

    # ── SCENE 8 — Recap & Outro  (21.6 s) ────────────────────────
    def s8_outro(self):
        # NARRATION s8: "Let us recap…"
        self._sound("s8")                                   # t=0

        stitle = scene_title(self, "Recap", color=WHITE)   # t≈0.7
        self.wait(0.5)                                      # t≈1.2

        cards_data = [
            ("🔐 Encryption",  "Scramble + Unscramble\n(needs a key)",     BLUE),
            ("#  Hashing",      "Scramble only, forever\n(no key needed)",  AMBER),
            ("✓  Remember",     "Right tool\nfor the right job",            GREEN),
        ]

        cards = VGroup()
        for hstr, bstr, c in cards_data:
            bg = RoundedRectangle(corner_radius=0.2, width=3.7, height=2.1,
                                  color=c, fill_color=BG, fill_opacity=0.97, stroke_width=2)
            h  = Text(hstr, font_size=21, color=c, weight=BOLD)
            h.next_to(bg.get_top(), DOWN, buff=0.28)
            b  = Text(bstr, font_size=17, color=WHITE, line_spacing=1.35)
            b.move_to(bg.get_center() + DOWN * 0.18)
            cards.add(VGroup(bg, h, b))

        cards.arrange(RIGHT, buff=0.5)
        cards.move_to(UP * 0.45)

        elapsed = 1.2
        for card in cards:
            self.play(FadeIn(card, shift=UP*0.25, scale=0.92), run_time=0.65)
            self.wait(0.5)
            elapsed += 1.15

        # t ≈ 4.65

        end = heading("Now you think like a security professional.", size=27, color=WHITE)
        end.move_to(DOWN * 1.85)
        self.play(Write(end), run_time=1.1)                 # t≈5.75
        self.wait(1.0)

        zdl  = Text("Zero Day Labs", font_size=20, color=BLUE, weight=BOLD)
        tag  = Text("Train. Test. Certify.", font_size=13, color=BLUE)
        zdl_group = VGroup(zdl, tag).arrange(DOWN, buff=0.08)
        zdl_group.to_corner(DR, buff=0.45)
        self.play(FadeIn(zdl_group, scale=0.8), run_time=0.7) # t≈7.45

        elapsed = 7.45
        self._pad("s8", elapsed)

        # Fade to black
        black = Rectangle(
            width=config.frame_width + 1,
            height=config.frame_height + 1,
            fill_color=BLACK, fill_opacity=0, stroke_width=0
        )
        self.add(black)
        self.play(black.animate.set_fill(opacity=1), run_time=1.6)
        self.wait(0.5)
