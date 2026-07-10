"""
Generate narration audio for all 5 CISSP YouTube Shorts.

Engine selection:
  1. ElevenLabs — if ELEVEN_API_KEY is set
  2. SVOX Pico  — offline fallback (triggers quality gate)

Outputs:
  cissp_shorts_audio/{c1_h,c1_m,c1_c, c2_h,...,c5_c}.mp3
  cissp_shorts_audio/durations.json

Usage:
  python generate_cissp_shorts_narration.py
  python generate_cissp_shorts_narration.py --force
  python generate_cissp_shorts_narration.py --only c1_h c2_m
"""
import json, os, re, time, subprocess, argparse

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(BASE_DIR, "cissp_shorts_audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(BASE_DIR, ".env"))
except ImportError:
    pass

ELEVEN_API_KEY  = os.environ.get("ELEVEN_API_KEY") or os.environ.get("ELEVENLABS_API_KEY")
ELEVEN_VOICE_ID = os.environ.get("CISSP_SHORTS_VOICE_ID", "UgBBYS2sOqTuMpoF3BR0")
ELEVEN_MODEL    = os.environ.get("ELEVEN_MODEL", "eleven_multilingual_v2")

# Google AI Studio (Gemini) TTS — primary engine for the Shorts (Schedar voice).
GOOGLE_API_KEY   = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GOOGLE_AI_STUDIO_KEY")
GOOGLE_TTS_VOICE = os.environ.get("CISSP_SHORTS_GOOGLE_VOICE") or os.environ.get("GOOGLE_TTS_VOICE", "Schedar")
GOOGLE_TTS_MODEL = os.environ.get("GOOGLE_TTS_MODEL", "gemini-2.5-flash-preview-tts")
# Free tier caps Gemini TTS at ~10 req/min. Sleep between calls to stay under it.
GOOGLE_TTS_DELAY = float(os.environ.get("GOOGLE_TTS_DELAY", "7"))

NARRATIONS = {
    # ── Short 1: CIA Triad ────────────────────────────────────────────────
    "c1_h": (
        "Most candidates miss this. CIA Triad — thirty seconds. Let's go."
    ),
    "c1_m": (
        "Confidentiality means only authorized users can access data. "
        "Think encryption, access control lists, and need-to-know. "
        "Integrity means data has not been altered. "
        "Checksums, hashing, and digital signatures protect this pillar. "
        "Availability means systems are accessible when you need them. "
        "Redundancy, backups, and failover keep your services running. "
        "On the CISSP exam — when a security control fails, identify which pillar is violated. "
        "That is how you find the correct answer."
    ),
    "c1_c": (
        "Follow Zero Day Labs for daily CISSP and Security Plus exam tips. "
        "Like, subscribe, and visit zerodaylabs.tech for the full study book."
    ),

    # ── Short 2: Data Classification ──────────────────────────────────────
    "c2_h": (
        "Which data needs the most protection? "
        "Know these four levels before your exam."
    ),
    "c2_m": (
        "Public data — anyone can access it. No harm if disclosed. Press releases, website content. "
        "Private data — internal use only. Employee records, financials. A breach causes moderate harm. "
        "Sensitive data — limited access required. PII, medical records, trade secrets. "
        "Significant breach impact. "
        "Confidential data — the highest protection level. "
        "National security, cryptographic keys. Maximum access controls required. "
        "Two rules for the exam: classify data at the HIGHEST sensitivity level it contains. "
        "And the data owner assigns classification — not the custodian."
    ),
    "c2_c": (
        "Follow for more CISSP and Security Plus breakdowns. "
        "Like this short if it helped. zerodaylabs.tech for the study book."
    ),

    # ── Short 3: Zero Trust ───────────────────────────────────────────────
    "c3_h": (
        "Old security trusted anyone inside the network. "
        "Zero Trust killed that idea. Here's why it matters for your exam."
    ),
    "c3_m": (
        "The old castle-and-moat model said: get past the firewall and you are trusted. "
        "The problem — lateral movement. One breach meant full network access. "
        "Zero Trust operates on three principles. "
        "First: verify explicitly. "
        "Authenticate and authorize every single request, every time. "
        "Second: use least privilege. "
        "Minimum access — just enough, just in time. "
        "Third: assume breach. "
        "Segment networks, monitor continuously, and limit the blast radius. "
        "Exam tip: Zero Trust eliminates implicit trust for ALL users and devices — "
        "even internal ones. Never trust. Always verify."
    ),
    "c3_c": (
        "Subscribe to Zero Day Labs for CISSP and Security Plus exam content. "
        "Like this video. zerodaylabs.tech."
    ),

    # ── Short 4: Incident Response ────────────────────────────────────────
    "c4_h": (
        "Six phases. NIST Incident Response. "
        "Memorize this order — the exam tests it."
    ),
    "c4_m": (
        "Phase one: Preparation. "
        "Policies, tools, and training must be in place BEFORE an incident. "
        "Phase two: Detection and Analysis. "
        "Identify that something is wrong. Determine scope and severity. "
        "Phase three: Containment. "
        "Stop the damage. Short-term isolation first, then long-term. "
        "Phase four: Eradication. "
        "Remove the root cause. Patch and clean the environment. "
        "Phase five: Recovery. "
        "Restore systems to normal operations. Monitor for reinfection. "
        "Phase six: Post-Incident Activity. "
        "Lessons learned meeting within two weeks. Improve your process and repeat. "
        "Exam tip: the CISSP loves testing the ORDER of these phases. "
        "Preparation always comes first — before any incident occurs."
    ),
    "c4_c": (
        "Follow Zero Day Labs. Like this short if it helped. "
        "Daily exam tips at zerodaylabs.tech."
    ),

    # ── Short 5: Exam Traps (Manager Mindset) ────────────────────────────
    "c5_h": (
        "Most people fail the CISSP because they think like a technician. "
        "Here's the mindset shift."
    ),
    "c5_m": (
        "The CISSP always tests the management mindset — never the technical one. "
        "When a question asks what to do FIRST — choose planning, policy, or risk assessment — "
        "not the technical fix. "
        "When legal or regulatory issues appear — compliance wins every single time. "
        "When the answer involves people — training and awareness beat any technology solution. "
        "When lives are at risk — human safety comes before data protection, always. "
        "And when you see the words senior security manager in the question — "
        "they manage risk, not keyboards. "
        "Think like a manager. Every. Single. Question."
    ),
    "c5_c": (
        "Save this. Share it. Subscribe for daily exam tips. "
        "Visit zerodaylabs.tech for the full CISSP study book."
    ),

    # ── Short 6: Risk Management ──────────────────────────────────────────
    "c6_h": (
        "Risk is not a guess. It's math. "
        "Here's the formula the CISSP wants you to know."
    ),
    "c6_m": (
        "Start with the single loss expectancy — the dollar cost of one incident. "
        "That is asset value times exposure factor. "
        "Next, the annualized rate of occurrence — how many times per year you expect it. "
        "Multiply them and you get the annualized loss expectancy. "
        "A.L.E. equals S.L.E. times A.R.O. That number drives every spending decision. "
        "Now, the four ways to handle risk. "
        "Avoid — stop the risky activity entirely. "
        "Transfer — shift the loss to a third party, usually insurance. "
        "Mitigate — apply controls to reduce the impact or the likelihood. "
        "Accept — acknowledge the risk and move on, when the cost of control exceeds the loss. "
        "Exam tip: you can never reach zero risk. "
        "What remains after your controls is residual risk."
    ),
    "c6_c": (
        "Follow Zero Day Labs for daily CISSP and Security Plus exam tips. "
        "Like, subscribe, and visit zerodaylabs.tech for the full study book."
    ),

    # ── Short 7: Access Control Models ────────────────────────────────────
    "c7_h": (
        "Who decides who gets access? "
        "Four access control models. Know which is which."
    ),
    "c7_m": (
        "Discretionary access control, D.A.C. — the data owner decides who gets access. "
        "Flexible, but risky. Think file permissions you set yourself. "
        "Mandatory access control, M.A.C. — the system enforces access using security labels and clearances. "
        "Rigid and powerful. It is used by the military. "
        "Role-based access control, R.B.A.C. — access is tied to your job role, not your identity. "
        "Add someone to a role, and they inherit its permissions. "
        "Attribute-based access control, A.B.A.C. — access is granted by evaluating attributes: "
        "user, resource, time, and location. The most granular model. "
        "Exam tip: M.A.C. uses mandatory labels — users cannot override it. "
        "R.B.A.C. follows the job, not the person."
    ),
    "c7_c": (
        "Follow for more CISSP and Security Plus breakdowns. "
        "Like this short if it helped. zerodaylabs.tech for the study book."
    ),

    # ── Short 8: Authentication Factors ───────────────────────────────────
    "c8_h": (
        "A password alone won't save you. "
        "This is how real authentication works."
    ),
    "c8_m": (
        "Authentication relies on factors. "
        "Something you know — a password, a PIN, or a passphrase. "
        "Something you have — a token, a smart card, or your phone. "
        "Something you are — a biometric, like a fingerprint, face, or iris. "
        "Two more round it out. "
        "Somewhere you are — your location, verified by G.P.S. or a geofence. "
        "And something you do — your behavior, like typing rhythm. "
        "Multi-factor authentication means combining two or more different factor types. "
        "A password plus a code from your phone is multi-factor. "
        "But a password plus a security question is not — both are something you know. "
        "Exam tip: two of the same factor is never multi-factor. The types must differ."
    ),
    "c8_c": (
        "Subscribe to Zero Day Labs for CISSP and Security Plus exam content. "
        "Like this video. zerodaylabs.tech."
    ),

    # ── Short 9: Cryptography — Symmetric vs Asymmetric ───────────────────
    "c9_h": (
        "One key, or two? "
        "This one trips up everyone. Let's fix that."
    ),
    "c9_m": (
        "Symmetric encryption uses one shared key to encrypt and decrypt. "
        "It is fast, and great for bulk data. "
        "The catch — both sides need the same key, so key distribution is the hard problem. "
        "Think A.E.S. and the old D.E.S. "
        "Asymmetric encryption uses a key pair: a public key and a private key. "
        "What one key locks, only the other can unlock. "
        "It is slow, but it solves key exchange. Think R.S.A. and elliptic curve. "
        "The real world uses both — hybrid encryption. "
        "Asymmetric securely exchanges a symmetric key, then symmetric encrypts the data. "
        "That is exactly how T.L.S. works. "
        "Exam tip: encrypt with the recipient's public key for confidentiality. "
        "Sign with your own private key for authenticity."
    ),
    "c9_c": (
        "Follow Zero Day Labs. Like this short if it helped. "
        "Daily exam tips at zerodaylabs.tech."
    ),

    # ── Short 10: Malware Types ───────────────────────────────────────────
    "c10_h": (
        "Not all malware is a virus. "
        "Mix these up, and you'll miss the question."
    ),
    "c10_m": (
        "A virus attaches to a file and needs a user to run it before it spreads. "
        "A worm self-replicates across the network on its own — no host file, no user needed. "
        "A trojan disguises itself as legitimate software, then does something malicious behind the scenes. "
        "Ransomware encrypts your files and demands payment for the key. "
        "A rootkit hides deep in the system, often at the kernel level, to keep stealthy access. "
        "And a logic bomb sits dormant until a specific condition triggers it — a date, or an event. "
        "Exam tip: the key difference — a worm spreads by itself, "
        "while a virus needs you to execute it."
    ),
    "c10_c": (
        "Save this. Share it. Subscribe for daily exam tips. "
        "Visit zerodaylabs.tech for the full CISSP study book."
    ),

    # ── Short 11: OSI Model ───────────────────────────────────────────────
    "c11_h": (
        "Seven layers. One mnemonic. "
        "The OSI model in thirty seconds — let's go."
    ),
    "c11_m": (
        "Layer one, Physical — the raw bits on the wire. Cables, hubs, repeaters. "
        "Layer two, Data Link — frames and MAC addresses. Switches live here. "
        "Layer three, Network — logical IP addressing and routing. This is the router's layer. "
        "Layer four, Transport — end-to-end delivery. TCP for reliable, UDP for speed. "
        "Layer five, Session — it opens, maintains, and closes conversations. "
        "Layer six, Presentation — translation, compression, and encryption. "
        "Layer seven, Application — the services you actually touch. HTTP, DNS, SMTP. "
        "Remember it top to bottom: All People Seem To Need Data Processing. "
        "Exam tip: a switch is layer two, a router is layer three, and encryption is layer six."
    ),
    "c11_c": (
        "Follow Zero Day Labs for daily CISSP and Security Plus exam tips. "
        "Like, subscribe, and visit zerodaylabs.tech for the full study book."
    ),

    # ── Short 12: Firewall Types ──────────────────────────────────────────
    "c12_h": (
        "Not all firewalls are equal. "
        "Know these five before your exam."
    ),
    "c12_m": (
        "A packet-filtering firewall works at layers three and four. "
        "It checks IP addresses and ports, but it is stateless — no memory of past traffic. "
        "A stateful inspection firewall tracks active connections in a state table, "
        "so it knows if a packet belongs to an established session. "
        "An application proxy works at layer seven. "
        "It terminates the connection and inspects the actual content. "
        "A next-generation firewall adds deep packet inspection, intrusion prevention, and application awareness. "
        "And a web application firewall filters HTTP to stop SQL injection and cross-site scripting. "
        "Exam tip: stateful tracks connections, and a proxy inspects layer-seven content."
    ),
    "c12_c": (
        "Follow for more CISSP and Security Plus breakdowns. "
        "Like this short if it helped. zerodaylabs.tech for the study book."
    ),

    # ── Short 13: Common Ports ────────────────────────────────────────────
    "c13_h": (
        "If a protocol sends data in cleartext, it's a finding. "
        "Know the secure swaps."
    ),
    "c13_m": (
        "FTP moves files in cleartext on ports twenty and twenty-one. Replace it with SFTP or FTPS. "
        "Telnet gives remote access in cleartext on port twenty-three. Always replace it with SSH on port twenty-two. "
        "HTTP is cleartext web traffic on port eighty. Use HTTPS on port four-forty-three. "
        "SNMP version one and two use cleartext strings. Use version three for authentication and encryption. "
        "DNS runs on port fifty-three. LDAP is three-eighty-nine, and LDAPS over TLS is six-thirty-six. "
        "Exam tip: when you see cleartext credentials, the answer is almost always the encrypted equivalent."
    ),
    "c13_c": (
        "Follow Zero Day Labs for daily CISSP and Security Plus exam tips. "
        "Like, subscribe, and visit zerodaylabs.tech for the full study book."
    ),

    # ── Short 14: Wireless Security ───────────────────────────────────────
    "c14_h": (
        "WEP, WPA, WPA2, WPA3 — "
        "which one is safe? Thirty seconds."
    ),
    "c14_m": (
        "WEP is fundamentally broken. Its weak initialization vector can be cracked in minutes. Never use it. "
        "WPA was an interim fix built on TKIP — also weak today. "
        "WPA2 uses AES with CCMP and was the standard for years, "
        "but it is vulnerable to the KRACK attack and to offline guessing of weak passwords. "
        "WPA3 is the current standard. It uses Simultaneous Authentication of Equals to defeat offline dictionary attacks. "
        "For business networks, use Enterprise mode with 802.1X, "
        "which authenticates every user individually against a RADIUS server. "
        "Watch for the evil twin — a rogue access point impersonating a real one. "
        "Exam tip: WPA3 for confidentiality, 802.1X for enterprise authentication."
    ),
    "c14_c": (
        "Follow for more CISSP and Security Plus breakdowns. "
        "Like this short if it helped. zerodaylabs.tech for the study book."
    ),

    # ── Short 15: VPN & IPsec ─────────────────────────────────────────────
    "c15_h": (
        "IPsec: two protocols, two modes. "
        "The exam tests all four."
    ),
    "c15_m": (
        "IPsec has two protocols. AH — Authentication Header — gives you integrity and authentication, but no encryption. "
        "ESP — Encapsulating Security Payload — adds confidentiality through encryption. "
        "So when you need secrecy, you use ESP. "
        "It also has two modes. Transport mode encrypts only the payload — that's for host-to-host. "
        "Tunnel mode encrypts the entire original packet and adds a new header — that's for site-to-site VPNs. "
        "IKE, the Internet Key Exchange, negotiates the keys. "
        "And higher up the stack, TLS secures HTTPS and browser-based SSL VPNs. "
        "Exam tip: ESP encrypts and AH does not — and tunnel mode is for site-to-site."
    ),
    "c15_c": (
        "Follow Zero Day Labs for daily CISSP and Security Plus exam tips. "
        "Like, subscribe, and visit zerodaylabs.tech for the full study book."
    ),

    # ── Short 16: Network Attacks ─────────────────────────────────────────
    "c16_h": (
        "The exam describes the attack — "
        "you name it. Can you?"
    ),
    "c16_m": (
        "A denial-of-service floods a target until it's unavailable. "
        "A distributed version uses a botnet of many compromised hosts. "
        "A man-in-the-middle secretly intercepts and relays traffic between two parties. "
        "ARP poisoning sends forged replies to bind the attacker's MAC address to a victim's IP. "
        "DNS poisoning corrupts cached records to redirect you to a malicious site — DNSSEC defends against it. "
        "A SYN flood exploits the TCP handshake, leaving half-open connections that exhaust the table. "
        "And VLAN hopping reaches a segment you shouldn't, through switch spoofing or double-tagging. "
        "Exam tip: the recurring defenses are segmentation, encryption, and strong authentication."
    ),
    "c16_c": (
        "Follow for more CISSP and Security Plus breakdowns. "
        "Like this short if it helped. zerodaylabs.tech for the study book."
    ),

    # ── Short 17: BCP vs DRP ──────────────────────────────────────────────
    "c17_h": (
        "RTO, RPO, MTD — "
        "these three letters trip up everyone."
    ),
    "c17_m": (
        "Business continuity keeps the whole organization running during a disruption. "
        "Disaster recovery is the subset focused on restoring IT systems. "
        "Now the metrics. RTO — Recovery Time Objective — is how fast you must restore a system. "
        "RPO — Recovery Point Objective — is how much data you can afford to lose, measured in time. "
        "MTD — Maximum Tolerable Downtime — is the absolute limit before the business suffers unacceptable harm. "
        "Your RTO must always be shorter than your MTD. "
        "And the Business Impact Analysis is what identifies these values in the first place. "
        "Exam tip: RPO is about data loss; RTO is about time to recover."
    ),
    "c17_c": (
        "Follow Zero Day Labs for daily CISSP and Security Plus exam tips. "
        "Like, subscribe, and visit zerodaylabs.tech for the full study book."
    ),

    # ── Short 18: RAID Levels ─────────────────────────────────────────────
    "c18_h": (
        "RAID is an availability control. "
        "Know these levels cold."
    ),
    "c18_m": (
        "RAID zero is striping. It's fast, but there's no redundancy — one disk fails and you lose everything. "
        "RAID one is mirroring. Every write goes to two disks, so you have a full copy. "
        "RAID five stripes data with distributed parity. It survives one disk failure and uses space efficiently. "
        "RAID six adds a second parity block, so it survives two simultaneous disk failures. "
        "RAID ten combines mirroring and striping for both speed and redundancy. "
        "Remember: RAID protects availability, not confidentiality — and it is never a substitute for backups. "
        "Exam tip: RAID zero has no fault tolerance, and RAID five survives exactly one drive failure."
    ),
    "c18_c": (
        "Follow for more CISSP and Security Plus breakdowns. "
        "Like this short if it helped. zerodaylabs.tech for the study book."
    ),

    # ── Short 19: Security Models ─────────────────────────────────────────
    "c19_h": (
        "Bell-LaPadula or Biba? "
        "Confidentiality versus integrity — settled."
    ),
    "c19_m": (
        "Bell-LaPadula is a confidentiality model. It has two rules. "
        "No read up — you can't read above your clearance. "
        "And no write down — you can't write below your level. "
        "Biba is its mirror image — an integrity model. "
        "No read down — you can't read lower-integrity data. "
        "And no write up — you can't corrupt higher-integrity data. "
        "A memory hook: Bell-LaPadula protects secrets, Biba protects trust. "
        "Clark-Wilson also handles integrity, using well-formed transactions and separation of duties. "
        "Exam tip: confidentiality points to Bell-LaPadula; integrity points to Biba."
    ),
    "c19_c": (
        "Follow Zero Day Labs for daily CISSP and Security Plus exam tips. "
        "Like, subscribe, and visit zerodaylabs.tech for the full study book."
    ),

    # ── Short 20: Cloud Service Models ────────────────────────────────────
    "c20_h": (
        "IaaS, PaaS, SaaS — "
        "who secures what? Know the line."
    ),
    "c20_m": (
        "With Infrastructure as a Service, the provider gives you compute, storage, and networking. "
        "You manage the operating system and everything above it. "
        "With Platform as a Service, the provider also manages the OS and runtime, "
        "so you only handle your application and its data. "
        "With Software as a Service, the provider runs everything — you just use the software. "
        "The key idea is the shared responsibility model. "
        "The more the provider manages, the less you control — but security is always shared. "
        "And no matter the model, protecting your own data is always your responsibility. "
        "Exam tip: in SaaS you still own data classification and access management."
    ),
    "c20_c": (
        "Follow for more CISSP and Security Plus breakdowns. "
        "Like this short if it helped. zerodaylabs.tech for the study book."
    ),
}


def duration_of(path: str) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True,
    )
    return float(result.stdout.strip())


def is_valid_mp3(path: str) -> bool:
    if not os.path.exists(path) or os.path.getsize(path) < 1024:
        return False
    try:
        return duration_of(path) > 0.5
    except Exception:
        return False


# Measured speech rate for these voices: ~3.3 words/sec on long passages.
# Using the measured rate so the truncation guard fires on genuinely short
# audio, not on fast speech.
WORDS_PER_SEC    = 3.3
CHUNK_CHAR_LIMIT = 240   # SMALL chunks: ElevenLabs truncation isolates to one
                         # short chunk that is easy to detect and cheap to retry
CHUNK_MIN_RATIO  = 0.55  # a chunk under this * expected is treated as truncated
FINAL_MIN_RATIO  = 0.70  # whole-scene floor after concatenation
MAX_TTS_RETRIES  = 4     # re-fetch a short chunk before giving up (truncation
                         # is intermittent — a retry almost always succeeds)


def _split_sentences(text: str) -> list:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p]


def _chunk_text(text: str, limit: int = CHUNK_CHAR_LIMIT) -> list:
    """Group sentences into chunks no longer than `limit` characters."""
    chunks, cur = [], ""
    for sent in _split_sentences(text):
        if cur and len(cur) + 1 + len(sent) > limit:
            chunks.append(cur)
            cur = sent
        else:
            cur = f"{cur} {sent}".strip()
    if cur:
        chunks.append(cur)
    return chunks or [text.strip()]


def _expected_seconds(text: str) -> float:
    return max(1.0, len(text.split()) / WORDS_PER_SEC)


def _tts_one(client, text: str, path: str) -> None:
    audio = client.text_to_speech.convert(
        voice_id=ELEVEN_VOICE_ID,
        model_id=ELEVEN_MODEL,
        text=text,
        output_format="mp3_44100_128",
    )
    with open(path, "wb") as f:
        for chunk in audio:
            f.write(chunk)


def _tts_chunk_with_retry(client, text: str, path: str, label: str) -> float:
    """Synthesize one chunk, retrying if ElevenLabs returns truncated audio.

    Returns the final duration in seconds. Raises if every attempt is short —
    that propagates to the Pico fallback and the quality gate so a bad scene is
    never silently rendered.
    """
    exp  = _expected_seconds(text)
    best = -1.0
    for attempt in range(1, MAX_TTS_RETRIES + 1):
        _tts_one(client, text, path)
        got = duration_of(path)
        if got >= CHUNK_MIN_RATIO * exp:
            return got
        best = max(best, got)
        print(f"      {label}: got {got:.1f}s, expected ~{exp:.1f}s "
              f"(retry {attempt}/{MAX_TTS_RETRIES})")
    raise RuntimeError(
        f"{label} truncated after {MAX_TTS_RETRIES} retries — "
        f"best {best:.1f}s for ~{exp:.1f}s of text"
    )


def generate_elevenlabs(key: str, text: str) -> str:
    """Per-sentence chunked TTS with per-chunk retry and a final length guard.

    Each scene is split into small (<=CHUNK_CHAR_LIMIT char) chunks. Each chunk
    is synthesized and duration-checked; a short chunk is re-fetched up to
    MAX_TTS_RETRIES times. Chunks are then concatenated. Because the chunks are
    small, ElevenLabs stream truncation shows up as one obviously-short chunk
    rather than a whole scene that is mildly short — which the old coarse
    guards could not distinguish from natural speech-rate variance.
    """
    from elevenlabs.client import ElevenLabs
    client = ElevenLabs(api_key=ELEVEN_API_KEY)
    mp3    = os.path.join(AUDIO_DIR, f"{key}.mp3")
    chunks = _chunk_text(text)
    parts  = []
    for f in os.listdir(AUDIO_DIR):
        if f.startswith(f".{key}_"):
            try:
                os.remove(os.path.join(AUDIO_DIR, f))
            except OSError:
                pass
    try:
        for i, ch in enumerate(chunks):
            part = os.path.join(AUDIO_DIR, f".{key}_part{i}.mp3")
            _tts_chunk_with_retry(client, ch, part, f"{key} chunk {i+1}/{len(chunks)}")
            parts.append(part)

        if len(parts) == 1:
            os.replace(parts[0], mp3)
        else:
            listf = os.path.join(AUDIO_DIR, f".{key}_list.txt")
            with open(listf, "w") as f:
                for p in parts:
                    f.write(f"file '{os.path.basename(p)}'\n")
            subprocess.run(
                ["ffmpeg", "-y", "-f", "concat", "-safe", "0",
                 "-i", os.path.basename(listf),
                 "-c:a", "libmp3lame", "-q:a", "2", os.path.basename(mp3)],
                check=True, capture_output=True, cwd=AUDIO_DIR,
            )
            os.remove(listf)

        total, exp_total = duration_of(mp3), _expected_seconds(text)
        if total < FINAL_MIN_RATIO * exp_total:
            raise RuntimeError(
                f"final audio truncated — {total:.1f}s for ~{exp_total:.1f}s of text"
            )
        return mp3
    finally:
        for p in parts:
            if os.path.exists(p):
                try:
                    os.remove(p)
                except OSError:
                    pass


def generate_google_tts(key: str, text: str) -> str:
    """Synthesize via Google AI Studio Gemini TTS, returns path to MP3.

    The API returns raw PCM (s16le, 24 kHz, mono) as base64; ffmpeg converts it
    to MP3. Retries 429 (rate limit) with exponential backoff, and throttles
    between calls to respect the free-tier ~10 req/min cap.
    """
    import base64
    import requests as _req

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GOOGLE_TTS_MODEL}:generateContent?key={GOOGLE_API_KEY}"
    )
    payload = {
        "contents": [{"parts": [{"text": text}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {
                "voiceConfig": {
                    "prebuiltVoiceConfig": {"voiceName": GOOGLE_TTS_VOICE}
                }
            },
        },
    }
    resp = None
    for attempt in range(1, 5):
        resp = _req.post(url, json=payload, timeout=120)
        if resp.status_code == 200:
            break
        if resp.status_code == 429 and attempt < 4:
            wait = 20 * attempt  # 20s, 40s, 60s
            print(f"      {key}: rate-limited (429), waiting {wait}s "
                  f"(retry {attempt}/3)...")
            time.sleep(wait)
            continue
        raise RuntimeError(f"Google TTS {resp.status_code}: {resp.text[:300]}")

    data = resp.json()
    audio_b64 = data["candidates"][0]["content"]["parts"][0]["inlineData"]["data"]
    pcm_bytes = base64.b64decode(audio_b64)

    mp3 = os.path.join(AUDIO_DIR, f"{key}.mp3")
    proc = subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "s16le", "-ar", "24000", "-ac", "1", "-i", "pipe:0",
            "-codec:a", "libmp3lame", "-qscale:a", "2", mp3,
        ],
        input=pcm_bytes, capture_output=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg PCM→MP3 failed: {proc.stderr.decode()[:200]}")
    if GOOGLE_TTS_DELAY > 0:
        time.sleep(GOOGLE_TTS_DELAY)
    return mp3


def generate_pico(key: str, text: str) -> str:
    wav = os.path.join(AUDIO_DIR, f"{key}.wav")
    mp3 = os.path.join(AUDIO_DIR, f"{key}.mp3")
    subprocess.run(["pico2wave", "-l", "en-US", "-w", wav, text], check=True)
    subprocess.run(
        ["ffmpeg", "-y", "-i", wav, "-filter:a", "atempo=1.05", "-q:a", "2", mp3],
        check=True, capture_output=True,
    )
    os.remove(wav)
    return mp3


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true",
                        help="Regenerate all audio even if files already exist")
    parser.add_argument("--only", nargs="+", metavar="KEY",
                        help="Only generate these keys (e.g. --only c1_h c2_m)")
    args = parser.parse_args()

    # Shorts prefer Google AI Studio (Schedar voice) when a key is present.
    if GOOGLE_API_KEY:
        engine = "Google AI Studio TTS"
        voice_label = GOOGLE_TTS_VOICE
    elif ELEVEN_API_KEY:
        engine = "ElevenLabs"
        voice_label = ELEVEN_VOICE_ID
    else:
        engine = "Pico (offline fallback)"
        voice_label = "N/A"
    print(f"Engine: {engine}")
    print(f"Voice:  {voice_label}")
    print(f"Output: {AUDIO_DIR}")
    print(f"Keys:   {len(NARRATIONS)} segments across 10 shorts\n")

    dur_path = os.path.join(AUDIO_DIR, "durations.json")
    durations: dict = {}
    if os.path.exists(dur_path):
        with open(dur_path) as f:
            durations = json.load(f)

    pico_fallbacks: list = []
    failed_scenes:  list = []

    for key, text in NARRATIONS.items():
        if args.only and key not in args.only:
            print(f"  {key}: skipped (not in --only list)")
            continue

        mp3 = os.path.join(AUDIO_DIR, f"{key}.mp3")

        if not args.force and is_valid_mp3(mp3):
            print(f"  {key}: already exists ({durations.get(key, '?')}s) — skipping")
            continue

        try:
            if GOOGLE_API_KEY:
                mp3 = generate_google_tts(key, text)
            elif ELEVEN_API_KEY:
                mp3 = generate_elevenlabs(key, text)
            else:
                mp3 = generate_pico(key, text)
            durations[key] = round(duration_of(mp3), 2)
            print(f"  {key}: {durations[key]:.1f}s → {mp3}")
        except Exception as e:
            print(f"  {key}: TTS FAILED — {e}")
            # If Google failed and ElevenLabs is available, try it before Pico.
            if GOOGLE_API_KEY and ELEVEN_API_KEY:
                print(f"         Attempting ElevenLabs fallback...")
                try:
                    mp3 = generate_elevenlabs(key, text)
                    durations[key] = round(duration_of(mp3), 2)
                    print(f"  {key}: {durations[key]:.1f}s → {mp3}  (ElevenLabs fallback)")
                    continue
                except Exception as ee:
                    print(f"  {key}: ElevenLabs also failed — {ee}")
            print(f"         Attempting Pico fallback...")
            try:
                mp3 = generate_pico(key, text)
                durations[key] = round(duration_of(mp3), 2)
                print(f"  {key}: {durations[key]:.1f}s → {mp3}  ⚠ PICO FALLBACK")
                pico_fallbacks.append(key)
            except Exception as e2:
                print(f"  {key}: Pico also failed — {e2}  ✗ SEGMENT MISSING")
                failed_scenes.append(key)

    with open(dur_path, "w") as f:
        json.dump(durations, f, indent=2)

    total = sum(durations.values())
    print(f"\nWrote {dur_path}")
    print(f"Total narration: {total:.1f}s ({total/60:.1f} min)")
    print(f"Avg per short:   {total/10:.1f}s")

    # ── Quality gate ─────────────────────────────────────────────────────────
    if pico_fallbacks or failed_scenes:
        print("\n" + "=" * 60)
        print("  AUDIO QUALITY GATE — DO NOT RENDER")
        print("=" * 60)
        if pico_fallbacks:
            keys = " ".join(pico_fallbacks)
            print(f"\n  ⚠  ROBOT VOICE (Pico) used for: {keys}")
            print(f"     Fix: python generate_cissp_shorts_narration.py --force --only {keys}")
        if failed_scenes:
            keys = " ".join(failed_scenes)
            print(f"\n  ✗  GENERATION FAILED for: {keys}")
            print(f"     Fix: python generate_cissp_shorts_narration.py --force --only {keys}")
        print("\n  Resolve the above before running manim.\n")
        raise SystemExit(1)
    else:
        print(f"\n✓ All segments generated with {engine} — safe to render.")
        print("\nRender commands:")
        for short in ["CIATriad", "DataClassification", "ZeroTrust",
                      "IncidentResponse", "ExamTraps",
                      "RiskManagement", "AccessControlModels",
                      "AuthenticationFactors", "Cryptography", "MalwareTypes"]:
            print(f"  manim -qh cissp_shorts.py {short}")
