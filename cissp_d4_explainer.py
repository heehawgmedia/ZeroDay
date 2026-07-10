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

AUDIO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cissp_d4_audio")

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
#  CISSP D4  —  manim -qh cissp_d4_explainer.py CISSP_D4
# ═══════════════════════════════════════════════════════════════════
class CISSP_D4(Scene):
    def construct(self):
        _preflight_audio(AUDIO, _DUR_DEFAULTS, "generate_cissp_d4_narration.py")
        self.s0_hook_roadmap()
        self.s1_osi_model()
        self.s2_tcpip_encapsulation()
        self.s3_ip_addressing()
        self.s4_protocols_ports()
        self.s5_network_hardware()
        self.s6_firewalls()
        self.s7_wireless()
        self.s8_vpn_channels()
        self.s9_network_attacks()
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

        failures = VGroup(
            Text("✗  User logs into their bank over plain HTTP on public Wi-Fi.",
                 font_size=17, color=RED),
            Text("✗  Admin leaves Telnet open on a production router.",
                 font_size=17, color=AMBER),
            Text("✗  Database server shares one flat network with the guest Wi-Fi.",
                 font_size=17, color=GRAY),
        ).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        failures.move_to(UP*1.2)
        for f in failures:
            self.play(FadeIn(f, shift=RIGHT*0.15), run_time=0.35)
        self.wait(2.0)

        self._fade_content(bg, run_time=0.4)
        bg2 = self._tech_bg()

        series = Text("CISSP Domain Mastery Series", font_size=20, color=GRAY)
        ep_title = heading("Domain 4  |  Communication & Network Security", size=32, color=WHITE)
        ep_title.move_to(UP*1.5)
        series.next_to(ep_title, UP, buff=0.3)
        self.play(FadeIn(series), Write(ep_title), run_time=0.9)

        obj_label = Text("Exam Objectives Covered:", font_size=17, color=AMBER, weight=BOLD)
        obj_label.next_to(ep_title, DOWN, buff=0.4)
        obj_nums = mono("4.1   |   4.2   |   4.3", size=16, color=BLUE)
        obj_nums.next_to(obj_label, DOWN, buff=0.18)
        self.play(FadeIn(obj_label), Write(obj_nums), run_time=0.5)

        topics = [
            "OSI Model & TCP/IP Model — the 7 layers, encapsulation, PDUs",
            "IP Addressing & Subnetting — IPv4/IPv6, private ranges, NAT, CIDR",
            "Secure vs Insecure Protocols — FTP/Telnet/HTTP and their replacements",
            "Network Hardware — hubs, switches, routers, NAC, 802.1X, transmission media",
            "Firewall Architectures — packet filter, stateful, proxy, NGFW, WAF, DMZ",
            "Wireless Security — WEP, WPA, WPA2, WPA3, SAE, evil twin, rogue AP",
            "VPNs & Secure Channels — IPsec (AH/ESP, tunnel/transport), TLS, SSH",
            "Network Attacks — DoS/DDoS, MITM, ARP/DNS poisoning, VLAN hopping",
        ]
        topic_group = VGroup(*[
            Text(f"• {t}", font_size=13, color=WHITE) for t in topics
        ]).arrange(DOWN, buff=0.11, aligned_edge=LEFT)
        topic_group.next_to(obj_nums, DOWN, buff=0.24)
        for t in topic_group:
            self.play(FadeIn(t, shift=RIGHT*0.12), run_time=0.15)

        self._pad("s0", 20.0)
        self._fade_content(bg2)

    # ── SCENE 1 — OSI Model ──────────────────────────────────────
    def s1_osi_model(self):
        bg = self._tech_bg()
        self._sound("s1")

        scene_title(self, "The OSI Model — 7 Layers", color=BLUE)

        mnem = Text("Mnemonic (L7→L1):  All People Seem To Need Data Processing",
                    font_size=15, color=AMBER, weight=BOLD)
        mnem.move_to(UP*2.5)
        self.play(FadeIn(mnem), run_time=0.4)

        # (num, name, function, example) — top layer first
        layers = [
            ("7", "Application",  "User-facing services",        "HTTP · FTP · DNS · SMTP", "#AA44FF"),
            ("6", "Presentation", "Translation · ENCRYPTION",    "TLS/SSL · JPEG · ASCII",  BLUE),
            ("5", "Session",      "Establish / maintain sessions","RPC · NetBIOS · sockets", GREEN),
            ("4", "Transport",    "End-to-end delivery",         "TCP (reliable) · UDP",    AMBER),
            ("3", "Network",      "Logical IP addr · routing",   "ROUTERS · IP · ICMP",     "#00C8FF"),
            ("2", "Data Link",    "Frames · MAC addressing",     "SWITCHES · bridges · ARP",RED),
            ("1", "Physical",     "Raw bits on the wire",        "HUBS · cables · repeaters",GRAY),
        ]
        start_y, step = 1.85, -0.63
        rows = VGroup()
        for i, (n, name, func, ex, col) in enumerate(layers):
            y = start_y + i*step
            rb = RoundedRectangle(corner_radius=0.10, width=12.6, height=0.56,
                                  color=col, fill_color=BG, fill_opacity=0.92,
                                  stroke_width=1.6).move_to([0, y, 0])
            c1 = Text(f"L{n}  {name}", font_size=15, color=col, weight=BOLD)
            c1.move_to([-6.05, y, 0], aligned_edge=LEFT)
            c2 = Text(func, font_size=12, color=WHITE)
            c2.move_to([-2.35, y, 0], aligned_edge=LEFT)
            c3 = Text(ex, font_size=12, color=GRAY)
            c3.move_to([2.55, y, 0], aligned_edge=LEFT)
            rows.add(VGroup(rb, c1, c2, c3))
        for r in rows:
            self.play(FadeIn(r, shift=RIGHT*0.12), run_time=0.22)

        exam_tip(self, "Switch = L2 · Router = L3 · Encryption = L6 (Presentation)")
        self._pad("s1", 22.0)
        self._fade_content(bg)

    # ── SCENE 2 — TCP/IP Model & Encapsulation ───────────────────
    def s2_tcpip_encapsulation(self):
        bg = self._tech_bg()
        self._sound("s2")

        scene_title(self, "TCP/IP Model & Encapsulation", color=GREEN)

        # Left: TCP/IP 4-layer stack mapped to OSI
        stk_head = Text("TCP/IP Model  (maps to OSI)", font_size=15, color=BLUE, weight=BOLD)
        stk_head.move_to([-3.6, 2.35, 0])
        stack = [
            ("Application",      "OSI 5·6·7",        "#AA44FF"),
            ("Transport",        "OSI 4 — TCP/UDP",  AMBER),
            ("Internet",         "OSI 3 — IP",       BLUE),
            ("Link / Net Access","OSI 1·2",          GRAY),
        ]
        sy, sstep = 1.55, -0.78
        lstack = VGroup()
        for i, (nm, mp, col) in enumerate(stack):
            y = sy + i*sstep
            b = RoundedRectangle(corner_radius=0.10, width=5.4, height=0.66,
                                 color=col, fill_color=BG, fill_opacity=0.92,
                                 stroke_width=1.6).move_to([-3.6, y, 0])
            t1 = Text(nm, font_size=14, color=col, weight=BOLD)
            t1.move_to([-6.05, y, 0], aligned_edge=LEFT)
            t2 = Text(mp, font_size=12, color=WHITE)
            t2.move_to([-1.15, y, 0], aligned_edge=RIGHT)
            lstack.add(VGroup(b, t1, t2))

        # Right: TCP vs UDP
        cmp_head = Text("Transport Layer", font_size=15, color=AMBER, weight=BOLD)
        cmp_head.move_to([3.4, 2.35, 0])
        tcp = RoundedRectangle(corner_radius=0.12, width=5.4, height=1.25,
                               color=GREEN, fill_color="#051A0A", fill_opacity=1,
                               stroke_width=1.6).move_to([3.4, 1.15, 0])
        tcp_t = Text("TCP — connection-oriented\n3-way handshake: SYN → SYN-ACK → ACK\nreliable · ordered · error-checked",
                     font_size=12, color=WHITE, line_spacing=1.15).move_to(tcp.get_center())
        udp = RoundedRectangle(corner_radius=0.12, width=5.4, height=1.05,
                               color=RED, fill_color="#1A0505", fill_opacity=1,
                               stroke_width=1.6).move_to([3.4, -0.35, 0])
        udp_t = Text("UDP — connectionless · no handshake\nfast · best-effort — DNS, VoIP, streaming",
                     font_size=12, color=WHITE, line_spacing=1.15).move_to(udp.get_center())

        self.play(FadeIn(stk_head), FadeIn(cmp_head), run_time=0.4)
        for r in lstack:
            self.play(FadeIn(r, shift=RIGHT*0.1), run_time=0.2)
        self.play(FadeIn(tcp), Write(tcp_t), run_time=0.5)
        self.play(FadeIn(udp), Write(udp_t), run_time=0.5)

        # Encapsulation chain
        enc_head = Text("Encapsulation — each layer adds a header:", font_size=13, color=BLUE, weight=BOLD)
        enc_head.move_to([-3.05, -1.55, 0], aligned_edge=LEFT)
        pdus = [("Data", GRAY), ("Segment  L4", AMBER), ("Packet  L3", BLUE),
                ("Frame  L2", RED), ("Bits  L1", "#AA44FF")]
        chain = VGroup()
        for nm, col in pdus:
            b = RoundedRectangle(corner_radius=0.08, width=2.35, height=0.55,
                                 color=col, fill_color=BG, fill_opacity=0.92, stroke_width=1.5)
            t = Text(nm, font_size=13, color=col, weight=BOLD).move_to(b.get_center())
            chain.add(VGroup(b, t))
        chain.arrange(RIGHT, buff=0.14).move_to([0, -2.25, 0])
        arrows = VGroup(*[
            Text("▸", font_size=16, color=WHITE).move_to(
                (chain[i].get_right()+chain[i+1].get_left())/2)
            for i in range(len(chain)-1)
        ])
        self.play(FadeIn(enc_head), run_time=0.3)
        self.play(FadeIn(chain), FadeIn(arrows), run_time=0.6)

        exam_tip(self, "Segment = L4  ·  Packet = L3  ·  Frame = L2")
        self._pad("s2", 22.0)
        self._fade_content(bg)

    # ── SCENE 3 — IP Addressing & Subnetting ─────────────────────
    def s3_ip_addressing(self):
        bg = self._tech_bg()
        self._sound("s3")

        scene_title(self, "IP Addressing & Subnetting", color=BLUE)

        def card(x, w, h, y, col, head, body):
            cb = RoundedRectangle(corner_radius=0.14, width=w, height=h,
                                  color=col, fill_color=BG, fill_opacity=0.94,
                                  stroke_width=1.8).move_to([x, y, 0])
            ht = Text(head, font_size=15, color=col, weight=BOLD)
            ht.next_to(cb.get_top(), DOWN, buff=0.16)
            bt = Text(body, font_size=12, color=WHITE, line_spacing=1.2)
            bt.move_to(cb.get_center()+DOWN*0.18)
            return VGroup(cb, ht, bt)

        c1 = card(-4.4, 4.2, 2.5, 1.15, GREEN, "IPv4  vs  IPv6",
                  "IPv4: 32-bit · 4 octets\n  e.g. 192.168.1.1\nIPv6: 128-bit · native\n  IPsec support")
        c2 = card(0.0, 4.2, 2.5, 1.15, AMBER, "Private Ranges (RFC 1918)",
                  "10.0.0.0/8\n172.16.0.0/12\n192.168.0.0/16\nNot internet-routable")
        c3 = card(4.4, 4.2, 2.5, 1.15, "#AA44FF", "Special Addresses",
                  "NAT → hides internal net\nAPIPA → 169.254.x.x\nLoopback → 127.0.0.1")
        for c in (c1, c2, c3):
            self.play(FadeIn(c, shift=UP*0.1), run_time=0.45)

        strip = RoundedRectangle(corner_radius=0.12, width=12.8, height=1.15,
                                 color=BLUE, fill_color="#00101A", fill_opacity=1,
                                 stroke_width=1.6).move_to([0, -1.75, 0])
        strip_t = Text(
            "Subnetting splits a network via the SUBNET MASK  ·  CIDR /24 = 24 network bits = 254 usable hosts\n"
            "Security payoff: SEGMENTATION — a breach in one segment cannot spread freely to others",
            font_size=13, color=WHITE, line_spacing=1.25).move_to(strip.get_center())
        self.play(FadeIn(strip), Write(strip_t), run_time=0.6)

        exam_tip(self, "Private ranges are NOT internet-routable  ·  /24 = 254 hosts")
        self._pad("s3", 20.0)
        self._fade_content(bg)

    # ── SCENE 4 — Secure vs Insecure Protocols ───────────────────
    def s4_protocols_ports(self):
        bg = self._tech_bg()
        self._sound("s4")

        scene_title(self, "Secure vs Insecure Protocols", color=AMBER)

        cols_x = [-5.9, -2.9, -0.2, 3.6]  # insecure, port, secure, port
        header = VGroup(
            Text("INSECURE",  font_size=14, color=RED,   weight=BOLD).move_to([cols_x[0], 2.35, 0], aligned_edge=LEFT),
            Text("PORT",      font_size=14, color=GRAY,  weight=BOLD).move_to([cols_x[1], 2.35, 0], aligned_edge=LEFT),
            Text("SECURE REPLACEMENT", font_size=14, color=GREEN, weight=BOLD).move_to([cols_x[2], 2.35, 0], aligned_edge=LEFT),
            Text("PORT",      font_size=14, color=GRAY,  weight=BOLD).move_to([cols_x[3], 2.35, 0], aligned_edge=LEFT),
        )
        self.play(FadeIn(header), run_time=0.4)
        hbar = Line([-6.3, 2.1, 0], [6.3, 2.1, 0], color=GRAY, stroke_width=1.0)
        self.play(Create(hbar), run_time=0.3)

        rows = [
            ("FTP",        "20 / 21", "SFTP  /  FTPS",     "22 / 990"),
            ("Telnet",     "23",      "SSH",               "22"),
            ("HTTP",       "80",      "HTTPS  (TLS)",      "443"),
            ("SNMP v1/v2", "161",     "SNMP v3  (auth+enc)","161"),
            ("SMTP/POP3/IMAP","25/110/143","+ TLS (implicit/STARTTLS)","465/995/993"),
            ("DNS",        "53",      "DoT  /  DoH",       "853 / 443"),
            ("LDAP",       "389",     "LDAPS  (TLS)",      "636"),
        ]
        ry, rstep = 1.55, -0.52
        rowg = VGroup()
        for i, (ins, p1, sec, p2) in enumerate(rows):
            y = ry + i*rstep
            rowg.add(
                Text(ins, font_size=13, color=RED).move_to([cols_x[0], y, 0], aligned_edge=LEFT),
                mono(p1, size=12, color=GRAY).move_to([cols_x[1], y, 0], aligned_edge=LEFT),
                Text(sec, font_size=13, color=GREEN).move_to([cols_x[2], y, 0], aligned_edge=LEFT),
                mono(p2, size=12, color=GRAY).move_to([cols_x[3], y, 0], aligned_edge=LEFT),
            )
        for i in range(0, len(rowg), 4):
            self.play(FadeIn(VGroup(*rowg[i:i+4]), shift=RIGHT*0.1), run_time=0.2)

        exam_tip(self, "Cleartext credentials = a finding  ·  answer = the encrypted equivalent")
        self._pad("s4", 20.0)
        self._fade_content(bg)

    # ── SCENE 5 — Network Hardware & Media ───────────────────────
    def s5_network_hardware(self):
        bg = self._tech_bg()
        self._sound("s5")

        scene_title(self, "Network Hardware & Media", color=GREEN)

        devices = [
            ("HUB",    "Layer 1", "Repeats every signal to\nevery port. No intelligence.\nSecurity liability.", RED),
            ("SWITCH", "Layer 2", "Forwards frames by MAC.\nOnly to the right port.\nEnables VLANs.", BLUE),
            ("ROUTER", "Layer 3", "Forwards packets by IP\nbetween networks.\nEnforces ACLs.", GREEN),
        ]
        cards = VGroup()
        for nm, ly, desc, col in devices:
            cb = RoundedRectangle(corner_radius=0.14, width=4.0, height=2.05,
                                  color=col, fill_color=BG, fill_opacity=0.94, stroke_width=1.8)
            nt = Text(nm, font_size=20, color=col, weight=BOLD)
            lt = Text(ly, font_size=13, color=WHITE, weight=BOLD)
            dt = Text(desc, font_size=12, color=GRAY, line_spacing=1.15)
            inner = VGroup(nt, lt, dt).arrange(DOWN, buff=0.14)
            inner.move_to(cb.get_center())
            cards.add(VGroup(cb, inner))
        cards.arrange(RIGHT, buff=0.4).move_to([0, 1.15, 0])
        for c in cards:
            self.play(FadeIn(c, shift=UP*0.1), run_time=0.4)

        concepts = [
            ("NAC",      "Checks device posture\n(patch, AV) before join", AMBER),
            ("802.1X",   "Port-based access control\nauth before network", BLUE),
            ("CDN",      "Distributes content\nabsorbs DDoS traffic", GREEN),
            ("FIBER",    "Most secure media —\nhard to tap, EMI-immune", "#AA44FF"),
        ]
        crow = VGroup()
        for nm, desc, col in concepts:
            cb = RoundedRectangle(corner_radius=0.12, width=3.0, height=1.15,
                                  color=col, fill_color=BG, fill_opacity=0.92, stroke_width=1.5)
            nt = Text(nm, font_size=15, color=col, weight=BOLD)
            dt = Text(desc, font_size=11, color=WHITE, line_spacing=1.1)
            inner = VGroup(nt, dt).arrange(DOWN, buff=0.1).move_to(cb.get_center())
            crow.add(VGroup(cb, inner))
        crow.arrange(RIGHT, buff=0.22).move_to([0, -1.35, 0])
        for c in crow:
            self.play(FadeIn(c, shift=UP*0.08), run_time=0.25)

        exam_tip(self, "Fiber is hardest to tap  ·  a switch enables VLAN segmentation")
        self._pad("s5", 22.0)
        self._fade_content(bg)

    # ── SCENE 6 — Firewall Architectures ─────────────────────────
    def s6_firewalls(self):
        bg = self._tech_bg()
        self._sound("s6")

        scene_title(self, "Firewall Generations", color=RED)

        gens = [
            ("Packet-Filtering", "L3/L4 · stateless — inspects IP/port per packet, no memory. Fast, easily fooled.", GRAY),
            ("Stateful Inspection", "Tracks active connections in a STATE TABLE — knows if a packet belongs to a session.", BLUE),
            ("Application Proxy", "L7 — terminates the connection, inspects actual content. Deep, but slower.", GREEN),
            ("Next-Gen (NGFW)", "Stateful + deep packet inspection + IPS + application awareness.", AMBER),
            ("Web App Firewall (WAF)", "Filters HTTP — defends web apps against SQL injection and XSS.", "#AA44FF"),
        ]
        start_y, step = 1.75, -0.72
        rows = VGroup()
        for i, (nm, desc, col) in enumerate(gens):
            y = start_y + i*step
            rb = RoundedRectangle(corner_radius=0.10, width=12.8, height=0.62,
                                  color=col, fill_color=BG, fill_opacity=0.92, stroke_width=1.6).move_to([0, y, 0])
            t1 = Text(nm, font_size=14, color=col, weight=BOLD).move_to([-6.15, y, 0], aligned_edge=LEFT)
            t2 = Text(desc, font_size=12, color=WHITE).move_to([-2.55, y, 0], aligned_edge=LEFT)
            rows.add(VGroup(rb, t1, t2))
        for r in rows:
            self.play(FadeIn(r, shift=RIGHT*0.1), run_time=0.28)

        arch = RoundedRectangle(corner_radius=0.12, width=12.8, height=0.92,
                                color=BLUE, fill_color="#00101A", fill_opacity=1,
                                stroke_width=1.6).move_to([0, -2.35, 0])
        arch_t = Text("Screened subnet (DMZ): public-facing servers sit in an isolated zone between TWO firewalls —\n"
                      "a compromise there does not reach the internal network.",
                      font_size=12, color=WHITE, line_spacing=1.2).move_to(arch.get_center())
        self.play(FadeIn(arch), Write(arch_t), run_time=0.6)

        exam_tip(self, "Stateful tracks connections  ·  proxy = L7 content  ·  DMZ between two firewalls")
        self._pad("s6", 22.0)
        self._fade_content(bg)

    # ── SCENE 7 — Wireless Security ──────────────────────────────
    def s7_wireless(self):
        bg = self._tech_bg()
        self._sound("s7")

        scene_title(self, "Wireless Security", color=AMBER)

        ladder = [
            ("WEP",  "Wired Equivalent Privacy — BROKEN. Weak IV, cracked in minutes. Never use.", RED),
            ("WPA",  "Interim fix using TKIP — now considered weak.", "#F5A623"),
            ("WPA2", "AES + CCMP — long the standard. Vulnerable to KRACK & offline dictionary on weak PSK.", BLUE),
            ("WPA3", "CURRENT — SAE (Simultaneous Auth of Equals) defeats offline dictionary; forward secrecy.", GREEN),
        ]
        start_y, step = 1.85, -0.74
        rows = VGroup()
        for i, (nm, desc, col) in enumerate(ladder):
            y = start_y + i*step
            rb = RoundedRectangle(corner_radius=0.10, width=12.8, height=0.64,
                                  color=col, fill_color=BG, fill_opacity=0.92, stroke_width=1.7).move_to([0, y, 0])
            t1 = Text(nm, font_size=16, color=col, weight=BOLD).move_to([-6.1, y, 0], aligned_edge=LEFT)
            t2 = Text(desc, font_size=12, color=WHITE).move_to([-4.55, y, 0], aligned_edge=LEFT)
            rows.add(VGroup(rb, t1, t2))
        for r in rows:
            self.play(FadeIn(r, shift=RIGHT*0.1), run_time=0.3)

        ent = RoundedRectangle(corner_radius=0.12, width=6.2, height=1.35,
                               color=BLUE, fill_color="#00101A", fill_opacity=1,
                               stroke_width=1.6).move_to([-3.35, -1.95, 0])
        ent_t = Text("ENTERPRISE\nWPA2/3 Enterprise + 802.1X\nper-user auth via RADIUS\n(no shared pre-shared key)",
                     font_size=12, color=WHITE, line_spacing=1.15, weight=BOLD).move_to(ent.get_center())
        thr = RoundedRectangle(corner_radius=0.12, width=6.2, height=1.35,
                               color=RED, fill_color="#1A0505", fill_opacity=1,
                               stroke_width=1.6).move_to([3.35, -1.95, 0])
        thr_t = Text("THREATS\nEvil twin — rogue AP impersonates\nRogue AP — unauthorized AP\nDisable WPS (PIN brute-forceable)",
                     font_size=12, color=WHITE, line_spacing=1.15).move_to(thr.get_center())
        self.play(FadeIn(ent), Write(ent_t), FadeIn(thr), Write(thr_t), run_time=0.7)

        exam_tip(self, "WPA3 for confidentiality  ·  802.1X for enterprise per-user auth")
        self._pad("s7", 22.0)
        self._fade_content(bg)

    # ── SCENE 8 — VPNs & Secure Channels ─────────────────────────
    def s8_vpn_channels(self):
        bg = self._tech_bg()
        self._sound("s8")

        scene_title(self, "IPsec & Secure Channels", color=BLUE)

        ip_head = Text("IPsec  (network layer)", font_size=16, color=BLUE, weight=BOLD)
        ip_head.move_to([0, 2.4, 0])
        self.play(FadeIn(ip_head), run_time=0.3)

        proto = RoundedRectangle(corner_radius=0.12, width=6.2, height=1.6,
                                 color=AMBER, fill_color=BG, fill_opacity=0.94,
                                 stroke_width=1.7).move_to([-3.4, 1.15, 0])
        proto_t = Text("PROTOCOLS\nAH — integrity + auth, NO encryption\nESP — integrity + auth + ENCRYPTION\n→ use ESP when confidentiality required",
                       font_size=12, color=WHITE, line_spacing=1.2).move_to(proto.get_center())
        modes = RoundedRectangle(corner_radius=0.12, width=6.2, height=1.6,
                                 color=GREEN, fill_color=BG, fill_opacity=0.94,
                                 stroke_width=1.7).move_to([3.4, 1.15, 0])
        modes_t = Text("MODES\nTransport — encrypts payload only\n  (host-to-host)\nTunnel — encrypts whole packet + new hdr\n  (site-to-site / remote access)",
                       font_size=12, color=WHITE, line_spacing=1.2).move_to(modes.get_center())
        self.play(FadeIn(proto), Write(proto_t), run_time=0.55)
        self.play(FadeIn(modes), Write(modes_t), run_time=0.55)

        ike = Text("IKE (Internet Key Exchange) negotiates the security association & keys",
                   font_size=12, color=AMBER).move_to([0, -0.35, 0])
        self.play(FadeIn(ike), run_time=0.35)

        others = [
            ("TLS",  "Secures app traffic — HTTPS, browser SSL-VPN", "#AA44FF"),
            ("SSH",  "Encrypted remote admin & file transfer — replaces Telnet", BLUE),
            ("RADIUS vs TACACS+", "RADIUS: encrypts password only  |  TACACS+: encrypts whole payload, separates AAA", GREEN),
        ]
        oy, ostep = -1.1, -0.62
        og = VGroup()
        for i, (nm, desc, col) in enumerate(others):
            y = oy + i*ostep
            rb = RoundedRectangle(corner_radius=0.10, width=12.8, height=0.54,
                                  color=col, fill_color=BG, fill_opacity=0.9, stroke_width=1.4).move_to([0, y, 0])
            t1 = Text(nm, font_size=13, color=col, weight=BOLD).move_to([-6.15, y, 0], aligned_edge=LEFT)
            t2 = Text(desc, font_size=12, color=WHITE).move_to([-2.35, y, 0], aligned_edge=LEFT)
            og.add(VGroup(rb, t1, t2))
        for r in og:
            self.play(FadeIn(r, shift=RIGHT*0.1), run_time=0.25)

        exam_tip(self, "ESP encrypts, AH does not  ·  tunnel = site-to-site, transport = host-to-host")
        self._pad("s8", 24.0)
        self._fade_content(bg)

    # ── SCENE 9 — Network Attacks ────────────────────────────────
    def s9_network_attacks(self):
        bg = self._tech_bg()
        self._sound("s9")

        scene_title(self, "Network Attacks", color=RED)

        attacks = [
            ("DoS / DDoS", "Overwhelm target. DDoS uses a botnet of compromised hosts.", RED),
            ("Man-in-the-Middle", "Intercept & relay traffic. Defeat: mutual auth + encryption.", AMBER),
            ("ARP Poisoning", "Forged ARP replies bind attacker MAC to a victim IP.", BLUE),
            ("DNS Poisoning", "Corrupt DNS cache → malicious site. Defeat: DNSSEC.", GREEN),
            ("SYN Flood", "Half-open TCP handshakes exhaust the connection table.", "#AA44FF"),
            ("VLAN Hopping", "Reach another VLAN via switch spoofing / double-tagging.", "#F5A623"),
            ("Session Hijacking", "Steal a valid session token to impersonate a user.", RED),
            ("Smurf", "Amplify ICMP using the network broadcast address.", BLUE),
        ]
        # 4 rows × 2 columns, positioned manually (matches the codebase idiom)
        col_x = [-3.28, 3.28]
        row_y = [2.02, 0.72, -0.58, -1.88]
        cards = VGroup()
        for idx, (nm, desc, col) in enumerate(attacks):
            x = col_x[idx % 2]
            y = row_y[idx // 2]
            cb = RoundedRectangle(corner_radius=0.12, width=6.15, height=1.02,
                                  color=col, fill_color=BG, fill_opacity=0.93,
                                  stroke_width=1.6).move_to([x, y, 0])
            nt = Text(nm, font_size=15, color=col, weight=BOLD)
            nt.next_to(cb.get_top(), DOWN, buff=0.13)
            dt = Text(desc, font_size=11, color=WHITE, line_spacing=1.1)
            dt.next_to(nt, DOWN, buff=0.09)
            cards.add(VGroup(cb, nt, dt))
        for i in range(0, len(cards), 2):
            self.play(FadeIn(VGroup(*cards[i:i+2]), shift=UP*0.08), run_time=0.3)

        exam_tip(self, "Recurring defenses: segmentation, encryption, strong authentication")
        self._pad("s9", 22.0)
        self._fade_content(bg)

    # ── SCENE 10 — Practice Questions ────────────────────────────
    def s10_practice_questions(self):
        bg = self._tech_bg()

        scene_title(self, "Practice Questions", color=GREEN)

        questions = [
            (
                "A network admin needs a device that forwards traffic between two\n"
                "different IP networks and can enforce access control lists.\n"
                "At which OSI layer does this device operate?",
                "A. Layer 2 — Data Link",
                "B. Layer 3 — Network",
                "C. Layer 4 — Transport",
                "B — Layer 3 (Network). A router forwards packets by IP and enforces ACLs. Switch = L2, hub = L1."
            ),
            (
                "A company needs a site-to-site VPN that encrypts the ENTIRE original\n"
                "packet (including the original IP header) and provides confidentiality.\n"
                "Which IPsec protocol and mode should be used?",
                "A. AH in transport mode",
                "B. ESP in transport mode",
                "C. ESP in tunnel mode",
                "C — ESP in tunnel mode. ESP encrypts (AH does not); tunnel mode wraps the whole packet in a new header."
            ),
            (
                "A wireless network uses WPA2 with a shared pre-shared key. Management\n"
                "wants per-user authentication and to defeat offline dictionary attacks.\n"
                "What should be recommended?",
                "A. Rotate the WPA2 pre-shared key",
                "B. WPA3 Enterprise with 802.1X",
                "C. Hide the SSID broadcast",
                "B — WPA3 Enterprise + 802.1X. SAE defeats offline dictionary; RADIUS authenticates each user individually."
            ),
        ]

        # Each stem/answer pair has its own audio clip. Start the clip, then hold
        # for its MEASURED duration (durations.json) so the reveal lands with the
        # narration regardless of TTS voice or speech rate.
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
            ("1", "OSI Layers:",
             "All People Seem To Need Data Processing  |  Switch = L2, Router = L3, Encryption = L6",
             BLUE),
            ("2", "TCP vs UDP:",
             "TCP = connection-oriented, 3-way handshake  |  UDP = connectionless  |  Packet = L3, Frame = L2",
             GREEN),
            ("3", "IPsec:",
             "ESP encrypts, AH does not  |  Tunnel = site-to-site, Transport = host-to-host",
             AMBER),
            ("4", "Wireless:",
             "WPA3 = current, WEP = broken  |  802.1X authenticates enterprise users individually",
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
            label_mob.move_to(card_bg.get_left() + RIGHT*2.0)
            detail_mob = Text(detail, font_size=13, color=WHITE)
            detail_mob.move_to(card_bg.get_center() + RIGHT*2.15)
            detail_mob.set_y(card_bg.get_center()[1])
            all_cards.add(VGroup(card_bg, num_mob, label_mob, detail_mob))

        all_cards.arrange(DOWN, buff=0.16)
        all_cards.move_to(DOWN*0.1)

        for card in all_cards:
            self.play(FadeIn(card, shift=RIGHT*0.2), run_time=0.45)
            self.wait(4.0)

        self.play(*[c.animate.set_opacity(0.4) for c in all_cards], run_time=0.4)

        cta_head = heading("Domain 4 complete. Test yourself now.", size=24, color=WHITE)
        url_bg = RoundedRectangle(corner_radius=0.2, width=5.2, height=0.68,
                                   color=GREEN, fill_color="#051A0A",
                                   fill_opacity=1, stroke_width=2)
        url_txt = Text("www.zerodaylabs.tech", font=MONO, font_size=22, color=GREEN, weight=BOLD)
        url_txt.move_to(url_bg.get_center())
        url_grp = VGroup(url_bg, url_txt)
        next_ep = Text("Next: Domain 5 — Identity and Access Management",
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
