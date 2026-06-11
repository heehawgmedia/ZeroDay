from manim import *
import random

# ─── Color Palette ───────────────────────────────────────────────
BG       = "#0A0E1A"
BLUE     = "#00C8FF"
AMBER    = "#F5A623"
GREEN    = "#39D353"
RED      = "#FF4D4D"
MONO     = "DejaVu Sans Mono"

config.background_color = BG


# ─── Helpers ─────────────────────────────────────────────────────
def mono(text, size=20, color=WHITE, **kw):
    return Text(text, font=MONO, font_size=size, color=color, **kw)

def heading(text, size=36, color=WHITE, **kw):
    return Text(text, font_size=size, color=color, weight=BOLD, **kw)

def pill(text, color, font_size=20):
    t = Text(text, font_size=font_size, color=color, weight=BOLD)
    box = SurroundingRectangle(t, color=color, buff=0.18, corner_radius=0.12)
    return VGroup(box, t)

def scene_title(scene_obj, text, color=WHITE):
    t = heading(text, size=32, color=color)
    t.to_edge(UP, buff=0.45)
    bar = Line(LEFT * 6.5, RIGHT * 6.5, color=color, stroke_width=1.5).next_to(t, DOWN, buff=0.12)
    scene_obj.play(Write(t), Create(bar), run_time=0.7)
    return VGroup(t, bar)

def fade_all(scene_obj, run_time=0.6):
    mobs = [m for m in scene_obj.mobjects]
    if mobs:
        scene_obj.play(FadeOut(*mobs), run_time=run_time)


# ═══════════════════════════════════════════════════════════════════
#  MASTER SCENE — render with:  manim -qh encryption_explainer.py MasterScene
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

    # ── SCENE 1 — Hook (0:00–0:30) ────────────────────────────────
    def s1_hook(self):
        # NARRATION: "Data is everywhere. And most of it shouldn't be readable to just anyone."

        # Binary stream background
        rng = random.Random(42)
        bits = []
        for r in range(14):
            for c in range(32):
                b = Text(rng.choice(["0","1"]), font_size=16,
                         color=BLUE, fill_opacity=0.25)
                b.move_to(np.array([-7.5 + c * 0.5, -4 + r * 0.58, 0]))
                bits.append(b)
        stream = VGroup(*bits)
        self.play(FadeIn(stream, lag_ratio=0.005), run_time=1.8)

        # Flicker a few bits
        for _ in range(4):
            sample = rng.sample(bits, 18)
            anims = [b.animate.set_color(rng.choice([BLUE, WHITE, AMBER])).set_opacity(rng.uniform(0.15, 0.5))
                     for b in sample]
            self.play(*anims, run_time=0.25)

        # Lock icon (primitive shapes)
        shackle = Arc(radius=0.38, start_angle=0, angle=PI,
                      color=AMBER, stroke_width=7)
        shackle.move_to(UP * 0.85)
        body = RoundedRectangle(corner_radius=0.1, width=0.85, height=0.65,
                                color=AMBER, fill_color=AMBER, fill_opacity=0.9,
                                stroke_width=0)
        body.next_to(shackle, DOWN, buff=-0.02)
        keyhole = Circle(radius=0.1, color=BG, fill_color=BG, fill_opacity=1, stroke_width=0)
        keyhole.move_to(body.get_center() + UP * 0.05)
        lock = VGroup(body, shackle, keyhole)
        lock.move_to(ORIGIN + UP * 0.6)

        self.play(stream.animate.set_opacity(0.12), run_time=0.4)
        self.play(GrowFromCenter(lock), run_time=0.9)
        self.wait(0.3)

        # ~0:10
        # NARRATION: "Encryption and hashing — two of the most misunderstood concepts in security."
        title = heading("What Is Encryption?", size=52, color=WHITE)
        title.next_to(lock, DOWN, buff=0.45)
        sub   = Text("(And Why It's Not the Same as Hashing)",
                     font_size=26, color=BLUE)
        sub.next_to(title, DOWN, buff=0.18)

        self.play(Write(title), run_time=1.2)
        self.play(FadeIn(sub, shift=UP * 0.15), run_time=0.7)

        # Glow flash
        self.play(title.animate.set_color(BLUE),   run_time=0.25)
        self.play(title.animate.set_color(WHITE),  run_time=0.25)

        self.wait(2.0)
        fade_all(self)

    # ── SCENE 2 — Core Question (0:30–1:00) ───────────────────────
    def s2_core_question(self):
        # NARRATION: "Both scramble your data. But they solve completely different problems."

        enc_rect  = Rectangle(width=4.2, height=2.6, color=BLUE,  stroke_width=3,
                              fill_color="#030D1A", fill_opacity=0.9)
        hash_rect = Rectangle(width=4.2, height=2.6, color=AMBER, stroke_width=3,
                              fill_color="#140A00", fill_opacity=0.9)
        enc_rect.move_to(LEFT  * 3.3)
        hash_rect.move_to(RIGHT * 3.3)

        enc_lbl  = heading("ENCRYPTION", size=28, color=BLUE)
        enc_lbl.move_to(enc_rect.get_center())
        hash_lbl = heading("HASHING",    size=28, color=AMBER)
        hash_lbl.move_to(hash_rect.get_center())

        neq = Text("≠", font_size=80, color=WHITE)

        self.play(Create(enc_rect),  Create(hash_rect),  run_time=0.9)
        self.play(Write(enc_lbl),    Write(hash_lbl),    run_time=0.7)
        self.play(Write(neq),                            run_time=0.5)
        self.wait(0.3)

        q_enc  = Text("?", font_size=52, color=BLUE,  weight=BOLD)
        q_hash = Text("?", font_size=52, color=AMBER, weight=BOLD)
        q_enc.next_to(enc_rect,  UP, buff=0.3)
        q_hash.next_to(hash_rect, UP, buff=0.3)
        self.play(FadeIn(q_enc, scale=0.4), FadeIn(q_hash, scale=0.4), run_time=0.7)
        self.wait(0.4)

        # NARRATION: "Both scramble data. But they solve completely different problems."
        caption = Text("Both scramble data. But they solve completely different problems.",
                       font_size=22, color=WHITE)
        caption.to_edge(DOWN, buff=0.6)
        self.play(Write(caption), run_time=1.4)
        self.wait(2.0)
        fade_all(self)

    # ── SCENE 3 — What Is Encryption? (1:00–2:30) ─────────────────
    def s3_encryption(self):
        # NARRATION: "Encryption takes plaintext and scrambles it using a key and an algorithm."

        stitle = scene_title(self, "What Is Encryption?", color=BLUE)
        self.wait(0.3)

        # Panels
        pt_box = Rectangle(width=3.2, height=1.3, color=GREEN, stroke_width=2,
                           fill_color="#011A00", fill_opacity=0.85)
        pt_box.move_to(LEFT * 4.5 + UP * 0.8)
        pt_lbl = Text("PLAINTEXT", font_size=14, color=GREEN)
        pt_lbl.next_to(pt_box, UP, buff=0.1)
        pt_txt = mono('"Hello, Alice"', size=20, color=GREEN)
        pt_txt.move_to(pt_box.get_center())

        ct_box = Rectangle(width=3.2, height=1.3, color=BLUE, stroke_width=2,
                           fill_color="#00101A", fill_opacity=0.85)
        ct_box.move_to(RIGHT * 4.5 + UP * 0.8)
        ct_lbl = Text("CIPHERTEXT", font_size=14, color=BLUE)
        ct_lbl.next_to(ct_box, UP, buff=0.1)
        ct_txt = mono('"X9$kL#2mQ@"', size=20, color=BLUE)
        ct_txt.move_to(ct_box.get_center())

        self.play(Create(pt_box), FadeIn(pt_lbl), Write(pt_txt), run_time=0.8)

        # Forward arrow
        fwd = Arrow(pt_box.get_right(), ct_box.get_left(), color=AMBER,
                    stroke_width=4, buff=0.1, max_tip_length_to_length_ratio=0.12)
        fwd_lbl = Text("🔑 Key + Algorithm", font_size=18, color=AMBER)
        fwd_lbl.next_to(fwd, UP, buff=0.14)

        self.play(GrowArrow(fwd), Write(fwd_lbl), run_time=0.8)
        self.play(Create(ct_box), FadeIn(ct_lbl), Write(ct_txt), run_time=0.9)
        self.wait(0.4)

        # Reverse arrow
        # NARRATION: "With the right key, you can completely reverse it."
        rev = Arrow(ct_box.get_left(), pt_box.get_right(), color=GREEN,
                    stroke_width=4, buff=0.1, max_tip_length_to_length_ratio=0.12)
        rev.shift(DOWN * 0.55)
        rev_lbl = Text("🔑 Same Key (or Paired Key)", font_size=16, color=GREEN)
        rev_lbl.next_to(rev, DOWN, buff=0.12)
        self.play(GrowArrow(rev), Write(rev_lbl), run_time=0.8)

        reversible = heading("↔  Reversible", size=24, color=GREEN)
        rev_pill = SurroundingRectangle(reversible, color=GREEN, buff=0.15, corner_radius=0.12)
        reversible.move_to(DOWN * 1.8)
        rev_pill.move_to(DOWN * 1.8)
        self.play(Write(reversible), Create(rev_pill), run_time=0.7)
        self.wait(0.5)

        # Fade mid-panel to make room for sub-type cards
        self.play(
            FadeOut(fwd), FadeOut(fwd_lbl),
            FadeOut(rev), FadeOut(rev_lbl),
            FadeOut(reversible), FadeOut(rev_pill),
            run_time=0.4
        )

        # Sub-type cards
        # NARRATION: "There are two main flavors — symmetric and asymmetric."
        sym_card = RoundedRectangle(corner_radius=0.15, width=3.8, height=1.6,
                                   color=BLUE, fill_color="#040D1A", fill_opacity=0.95,
                                   stroke_width=2)
        sym_card.move_to(LEFT * 2.2 + DOWN * 0.5)
        sym_h = Text("🗝  Symmetric", font_size=20, color=BLUE, weight=BOLD)
        sym_h.next_to(sym_card.get_top(), DOWN, buff=0.22)
        sym_d = Text("AES — same key to lock & unlock", font_size=15, color=WHITE)
        sym_d.move_to(sym_card.get_center() + DOWN * 0.18)

        asym_card = RoundedRectangle(corner_radius=0.15, width=3.8, height=1.6,
                                    color=AMBER, fill_color="#140A00", fill_opacity=0.95,
                                    stroke_width=2)
        asym_card.move_to(RIGHT * 2.2 + DOWN * 0.5)
        asym_h = Text("🔐 Asymmetric", font_size=20, color=AMBER, weight=BOLD)
        asym_h.next_to(asym_card.get_top(), DOWN, buff=0.22)
        asym_d = Text("RSA — public key encrypts,\nprivate key decrypts", font_size=15,
                      color=WHITE, line_spacing=1.3)
        asym_d.move_to(asym_card.get_center() + DOWN * 0.12)

        self.play(FadeIn(sym_card),  Write(sym_h),  Write(sym_d),  run_time=0.9)
        self.play(FadeIn(asym_card), Write(asym_h), Write(asym_d), run_time=0.9)
        self.wait(2.0)
        fade_all(self)

    # ── SCENE 4 — What Is Hashing? (2:30–3:45) ────────────────────
    def s4_hashing(self):
        # NARRATION: "Hashing is completely different. It's a one-way function — no reverse gear."

        stitle = scene_title(self, "What Is Hashing?", color=AMBER)
        self.wait(0.3)

        # Input / output panels
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

        self.play(Create(pt_box),   FadeIn(pt_lbl),   Write(pt_txt),   run_time=0.7)
        self.play(GrowArrow(fwd),   Write(fn_lbl),                      run_time=0.7)
        self.play(Create(hash_box), FadeIn(hash_lbl), Write(hash_txt),  run_time=0.8)
        self.wait(0.4)

        # Broken reverse arrow
        # NARRATION: "You cannot reverse a hash. Period."
        rev_fail = Arrow(hash_box.get_left(), pt_box.get_right(), color=RED,
                         stroke_width=4, buff=0.1, max_tip_length_to_length_ratio=0.12)
        rev_fail.shift(DOWN * 0.52)
        self.play(GrowArrow(rev_fail), run_time=0.5)

        x_mark = Text("✗", font_size=52, color=RED, weight=BOLD)
        x_mark.move_to(rev_fail.get_center() + UP * 0.45)
        no_rev = Text("Cannot Reverse", font_size=20, color=RED, weight=BOLD)
        no_rev.next_to(rev_fail, DOWN, buff=0.14)

        self.play(
            Write(x_mark),
            Write(no_rev),
            Flash(rev_fail.get_center(), color=RED, num_lines=8, flash_radius=0.6),
            run_time=0.8
        )
        self.wait(0.4)
        self.play(FadeOut(rev_fail), FadeOut(x_mark), FadeOut(no_rev), run_time=0.35)

        # ── Property 1: Deterministic ──
        # NARRATION: "The same input always produces the exact same hash."
        p1 = Text("Property 1 — Deterministic", font_size=21, color=WHITE, weight=BOLD)
        p1.move_to(UP * 0.0)
        self.play(Write(p1), run_time=0.6)

        run1 = mono('Run 1 → a3f5c9...d2e1  ✓', size=17, color=GREEN)
        run2 = mono('Run 2 → a3f5c9...d2e1  ✓', size=17, color=GREEN)
        run1.next_to(p1, DOWN, buff=0.25)
        run2.next_to(run1, DOWN, buff=0.15)

        self.play(FadeIn(run1, shift=RIGHT * 0.3), run_time=0.45)
        self.play(FadeIn(run2, shift=RIGHT * 0.3), run_time=0.45)
        self.wait(0.5)
        self.play(FadeOut(p1), FadeOut(run1), FadeOut(run2), run_time=0.35)

        # ── Property 2: Avalanche effect ──
        # NARRATION: "But change even one character and the entire hash is completely different."
        p2 = Text("Property 2 — Avalanche Effect", font_size=21, color=WHITE, weight=BOLD)
        p2.move_to(UP * 0.0)
        self.play(Write(p2), run_time=0.6)

        mod_txt = mono('"Hello, Alice!"', size=18, color=AMBER)
        mod_txt.move_to(pt_txt.get_center())
        changed = Text("↑ 1 char added", font_size=13, color=AMBER)
        changed.next_to(pt_box, DOWN, buff=0.1)

        self.play(Transform(pt_txt, mod_txt), FadeIn(changed), run_time=0.7)

        new_hash = mono("9f2a1b...c7d4", size=18, color=RED)
        new_hash.move_to(hash_txt.get_center())
        self.play(Transform(hash_txt, new_hash), run_time=0.4)
        self.play(
            Flash(hash_box.get_center(), color=RED, num_lines=10, flash_radius=0.9),
            run_time=0.5
        )

        avalanche = Text("⚡ Completely different hash!", font_size=19, color=RED)
        avalanche.next_to(p2, DOWN, buff=0.28)
        self.play(Write(avalanche), run_time=0.6)

        # One-way label
        ow = heading("→|  One-Way Function", size=22, color=AMBER)
        ow.next_to(avalanche, DOWN, buff=0.3)
        ow_box = SurroundingRectangle(ow, color=AMBER, buff=0.16, corner_radius=0.12)
        self.play(Write(ow), Create(ow_box), run_time=0.8)

        self.wait(2.0)
        fade_all(self)

    # ── SCENE 5 — Comparison Table (3:45–4:30) ────────────────────
    def s5_comparison(self):
        # NARRATION: "Let's put them side by side."

        stitle = scene_title(self, "Encryption vs Hashing", color=WHITE)
        self.wait(0.3)

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
            self.play(Create(rect), Write(t), run_time=0.35)

        rows = [
            ["Reversible?",        "✅ Yes",             "❌ No"],
            ["Uses a Key?",         "✅ Yes",             "❌ No"],
            ["Consistent output?",  "✅ Yes",             "✅ Yes"],
            ["Primary use case",    "Secure transit",    "Passwords / Integrity"],
        ]

        def cell_color(cell, col):
            if "✅" in cell: return GREEN
            if "❌" in cell: return RED
            if col == 1:     return BLUE
            if col == 2:     return AMBER
            return WHITE

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
            self.play(FadeIn(group, shift=LEFT * 0.25), run_time=0.55)
            self.wait(0.25)

        self.wait(2.0)
        fade_all(self)

    # ── SCENE 6 — Real-World Use Cases (4:30–5:30) ────────────────
    def s6_use_cases(self):
        # NARRATION: "Let's see where each one shows up in the real world."

        stitle = scene_title(self, "Real-World Use Cases", color=WHITE)
        self.wait(0.3)

        # ── Encryption: HTTPS ──
        # NARRATION: "Every HTTPS connection uses encryption to protect data in transit."
        enc_sub = Text("Encryption in Action: HTTPS / TLS", font_size=22, color=BLUE, weight=BOLD)
        enc_sub.move_to(UP * 1.7)
        self.play(Write(enc_sub), run_time=0.6)

        browser = RoundedRectangle(corner_radius=0.15, width=2.8, height=1.2,
                                   color=BLUE, fill_color="#020D1A", fill_opacity=0.9)
        browser.move_to(LEFT * 4 + UP * 0.3)
        b_lbl = Text("🌐  Browser", font_size=18, color=BLUE)
        b_lbl.move_to(browser.get_center())

        server = RoundedRectangle(corner_radius=0.15, width=2.8, height=1.2,
                                  color=GREEN, fill_color="#011A00", fill_opacity=0.9)
        server.move_to(RIGHT * 4 + UP * 0.3)
        s_lbl = Text("🖥  Server", font_size=18, color=GREEN)
        s_lbl.move_to(server.get_center())

        self.play(FadeIn(browser), Write(b_lbl), FadeIn(server), Write(s_lbl), run_time=0.7)

        top_line = Line(browser.get_right(), server.get_left(),
                        color=BLUE, stroke_width=3).shift(UP * 0.18)
        bot_line = Line(browser.get_right(), server.get_left(),
                        color=BLUE, stroke_width=3).shift(DOWN * 0.18)
        lock_lbl = Text("🔒  AES / TLS Encrypted", font_size=17, color=BLUE)
        lock_lbl.move_to(UP * 0.3)

        self.play(Create(top_line), Create(bot_line), run_time=0.5)
        self.play(Write(lock_lbl), run_time=0.5)

        cap1 = Text("Your bank encrypts data in transit (TLS/AES)", font_size=17, color=WHITE)
        cap1.move_to(DOWN * 0.5)
        self.play(Write(cap1), run_time=0.8)
        self.wait(1.0)

        self.play(
            FadeOut(enc_sub), FadeOut(browser), FadeOut(b_lbl),
            FadeOut(server), FadeOut(s_lbl), FadeOut(top_line),
            FadeOut(bot_line), FadeOut(lock_lbl), FadeOut(cap1),
            run_time=0.5
        )

        # ── Hashing: Password Storage ──
        # NARRATION: "When you sign up on a website, your password is hashed before it's ever saved."
        hash_sub = Text("Hashing in Action: Password Storage", font_size=22, color=AMBER, weight=BOLD)
        hash_sub.move_to(UP * 1.7)
        self.play(Write(hash_sub), run_time=0.6)

        form = RoundedRectangle(corner_radius=0.18, width=2.8, height=1.5,
                                color=BLUE, fill_color="#020D1A", fill_opacity=0.9)
        form.move_to(LEFT * 4 + UP * 0.3)
        f_title = Text("Login Form", font_size=15, color=BLUE)
        f_title.next_to(form.get_top(), DOWN, buff=0.2)
        f_pw = mono("pw: ••••••••", size=15, color=WHITE)
        f_pw.move_to(form.get_center() + DOWN * 0.1)

        self.play(FadeIn(form), Write(f_title), Write(f_pw), run_time=0.7)

        pw_arr = Arrow(LEFT * 2.5 + UP * 0.3, RIGHT * 0.5 + UP * 0.3,
                       color=AMBER, stroke_width=3, buff=0.1,
                       max_tip_length_to_length_ratio=0.1)
        fn_txt = Text("bcrypt / SHA-256", font_size=15, color=AMBER)
        fn_txt.next_to(pw_arr, UP, buff=0.1)
        self.play(GrowArrow(pw_arr), Write(fn_txt), run_time=0.6)

        db = RoundedRectangle(corner_radius=0.18, width=3.2, height=1.5,
                              color=AMBER, fill_color="#140A00", fill_opacity=0.9)
        db.move_to(RIGHT * 3.8 + UP * 0.3)
        db_title = Text("Database", font_size=15, color=AMBER)
        db_title.next_to(db.get_top(), DOWN, buff=0.2)
        db_hash = mono("$2b$12$eW5...\n3f9a1b...c2d", size=12, color=AMBER)
        db_hash.move_to(db.get_center() + DOWN * 0.1)

        self.play(FadeIn(db), Write(db_title), Write(db_hash), run_time=0.8)
        self.wait(0.5)

        # Speech bubble
        # NARRATION: "This is why 'Forgot Password' resets it — they literally cannot look up your original password."
        bubble = RoundedRectangle(corner_radius=0.18, width=6.0, height=0.85,
                                  color=GREEN, fill_color="#011A00", fill_opacity=0.95,
                                  stroke_width=2)
        bubble.move_to(DOWN * 1.55)
        b_txt = Text('"Forgot password?" → Site can\'t look it up → Must reset!',
                     font_size=15, color=GREEN)
        b_txt.move_to(bubble.get_center())
        self.play(FadeIn(bubble, scale=0.85), Write(b_txt), run_time=0.8)
        self.wait(0.4)

        # 🧂 BONUS: Salt callout
        # NARRATION: "Modern systems also add a random salt before hashing — this defeats rainbow table attacks."
        salt_bg = RoundedRectangle(corner_radius=0.15, width=7.8, height=0.85,
                                   color="#666666", fill_color="#0A0A1A", fill_opacity=0.95,
                                   stroke_width=1.5)
        salt_bg.move_to(DOWN * 2.7)
        salt_txt = Text("🧂 Salt:  password + random_salt  →  hash   (defeats rainbow tables)",
                        font_size=14, color="#BBBBBB")
        salt_txt.move_to(salt_bg.get_center())
        self.play(FadeIn(salt_bg), Write(salt_txt), run_time=0.8)

        self.wait(2.0)
        fade_all(self)

    # ── SCENE 7 — Never Confuse These (5:30–6:15) ─────────────────
    def s7_never_confuse(self):
        # NARRATION: "So here is the rule: use the right tool for the right job."

        stitle = scene_title(self, "Right Tool. Right Job.", color=WHITE)
        self.wait(0.3)

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

        self.play(Create(enc_box), Write(enc_lbl), Create(hash_box), Write(hash_lbl), run_time=0.8)
        self.wait(0.3)

        q_label = Text("", font_size=20, color=WHITE)  # placeholder

        def scenario(question, answer, target_box, answer_color):
            q = Text(question, font_size=20, color=WHITE)
            q.move_to(DOWN * 1.7)
            a = Text(answer, font_size=21, color=answer_color, weight=BOLD)
            a.move_to(DOWN * 2.45)
            self.play(Write(q), run_time=0.6)
            self.play(Indicate(target_box, color=answer_color, scale_factor=1.06), run_time=0.7)
            self.play(FadeIn(a), run_time=0.4)
            self.wait(0.7)
            self.play(FadeOut(q), FadeOut(a), run_time=0.3)

        # NARRATION: "Storing a password? Hash it."
        scenario("Storing a password securely?",
                 "✅ Use Hashing", hash_box, GREEN)

        # NARRATION: "Sending a secret that someone needs to read? Encrypt it."
        scenario("Sending a secret someone must read?",
                 "✅ Use Encryption", enc_box, BLUE)

        # NARRATION: "Encrypting passwords is a classic mistake — if the key leaks, everyone is exposed."
        bad_q = Text("Encrypting passwords instead of hashing?", font_size=20, color=WHITE)
        bad_q.move_to(DOWN * 1.7)
        self.play(Write(bad_q), run_time=0.6)

        cross = Cross(enc_box, color=RED, stroke_width=6)
        self.play(Create(cross), run_time=0.5)
        self.play(Flash(enc_box.get_center(), color=RED, num_lines=12, flash_radius=1.6), run_time=0.5)

        warn = Text("❌  Key leaks → ALL passwords exposed", font_size=20, color=RED, weight=BOLD)
        warn.move_to(DOWN * 2.45)
        self.play(Write(warn), run_time=0.7)

        self.wait(2.0)
        fade_all(self)

    # ── SCENE 8 — Recap & Outro (6:15–6:45) ───────────────────────
    def s8_outro(self):
        # NARRATION: "Let's lock this in."

        stitle = scene_title(self, "Recap", color=WHITE)
        self.wait(0.3)

        cards_data = [
            ("🔐 Encryption",  "Scramble + Unscramble\n(needs a key)",      BLUE),
            ("# Hashing",       "Scramble only, forever\n(no key needed)",   AMBER),
            ("✓ Remember",      "Right tool\nfor the right job",             GREEN),
        ]

        cards = VGroup()
        for heading_str, body_str, c in cards_data:
            bg = RoundedRectangle(corner_radius=0.2, width=3.7, height=2.1,
                                  color=c, fill_color=BG, fill_opacity=0.97, stroke_width=2)
            h  = Text(heading_str, font_size=21, color=c, weight=BOLD)
            h.next_to(bg.get_top(), DOWN, buff=0.28)
            b  = Text(body_str, font_size=17, color=WHITE, line_spacing=1.35)
            b.move_to(bg.get_center() + DOWN * 0.18)
            cards.add(VGroup(bg, h, b))

        cards.arrange(RIGHT, buff=0.5)
        cards.move_to(UP * 0.45)

        for card in cards:
            self.play(FadeIn(card, shift=UP * 0.25, scale=0.92), run_time=0.65)
            self.wait(0.25)

        self.wait(0.3)

        # End card
        # NARRATION: "Now you think like a security professional."
        end = heading("Now you think like a security professional.", size=27, color=WHITE)
        end.move_to(DOWN * 1.85)
        self.play(Write(end), run_time=1.1)

        # Zero Day Labs watermark
        zdl  = Text("Zero Day Labs", font_size=20, color=BLUE, weight=BOLD)
        tag  = Text("Train. Test. Certify.", font_size=13, color=BLUE)
        zdl_group = VGroup(zdl, tag).arrange(DOWN, buff=0.08)
        zdl_group.to_corner(DR, buff=0.45)
        self.play(FadeIn(zdl_group, scale=0.8), run_time=0.7)

        self.wait(2.2)

        # Fade to black
        black = Rectangle(
            width=config.frame_width + 1,
            height=config.frame_height + 1,
            fill_color=BLACK, fill_opacity=0, stroke_width=0
        )
        self.add(black)
        self.play(black.animate.set_fill(opacity=1), run_time=1.6)
        self.wait(0.3)
