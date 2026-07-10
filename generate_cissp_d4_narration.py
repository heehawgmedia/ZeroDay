"""
Generate narration audio for the CISSP Domain 4 explainer video.

Engine selection (automatic):
  1. ElevenLabs  — if ELEVEN_API_KEY is set (in .env or environment).
  2. SVOX Pico   — offline fallback (pico2wave), works anywhere.

Outputs:
  cissp_d4_audio/s0.mp3 ... cissp_d4_audio/s12.mp3
  cissp_d4_audio/durations.json

Usage:
  python generate_cissp_d4_narration.py              # skip existing valid files
  python generate_cissp_d4_narration.py --force      # regenerate everything
  python generate_cissp_d4_narration.py --only s2 s3 # specific scenes
"""
import json
import os
import re
import time
import subprocess
import argparse

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(BASE_DIR, "cissp_d4_audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(BASE_DIR, ".env"))
except ImportError:
    pass

ELEVEN_API_KEY  = os.environ.get("ELEVEN_API_KEY") or os.environ.get("ELEVENLABS_API_KEY")
ELEVEN_VOICE_ID = os.environ.get("CISSP_D4_VOICE_ID", "CwhRBWXzGAHq8TQ4Fs17")
ELEVEN_MODEL    = os.environ.get("ELEVEN_MODEL", "eleven_multilingual_v2")

GOOGLE_API_KEY   = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GOOGLE_AI_STUDIO_KEY")
GOOGLE_TTS_VOICE = os.environ.get("GOOGLE_TTS_VOICE", "Charon")
GOOGLE_TTS_MODEL = os.environ.get("GOOGLE_TTS_MODEL", "gemini-2.5-flash-preview-tts")
# Free tier caps Gemini TTS at ~10 req/min. Sleep between calls to stay under it.
GOOGLE_TTS_DELAY = float(os.environ.get("GOOGLE_TTS_DELAY", "7"))

NARRATIONS = {
    "s0": (
        "A user connects to public Wi-Fi and logs into their bank over plain HTTP. "
        "An administrator leaves Telnet open on a production router. "
        "A company puts its database server on the same flat network as the guest Wi-Fi. "
        "Three failures. Three habits. One root cause: none of them understood how the network actually moves and protects data. "
        "This is Domain 4 of the CISSP Domain Mastery Series — Communication and Network Security. "
        "We map to objectives 4.1 through 4.3. "
        "Today: the OSI and TCP/IP models, IP addressing and subnetting, "
        "secure and insecure protocols, network hardware, firewall architectures, "
        "wireless security, VPNs and secure channels, and the network attacks the exam loves to test. "
        "Every concept in this video is exam-tested."
    ),
    "s1": (
        "The OSI model is the foundation of Domain 4. Seven layers, each with a distinct function. "
        "You must know the layers in order, their functions, and which devices and protocols operate at each. "
        "Layer one, Physical: raw bits on the wire — cables, connectors, hubs, and repeaters. "
        "Layer two, Data Link: frames and physical MAC addressing — switches and bridges live here. "
        "Layer three, Network: logical IP addressing and routing — this is where routers operate. "
        "Layer four, Transport: end-to-end delivery — TCP for reliable connections, UDP for speed. "
        "Layer five, Session: establishes, maintains, and tears down sessions between applications. "
        "Layer six, Presentation: translation, encryption, and compression — data formatting. "
        "Layer seven, Application: the interface to the user — HTTP, FTP, DNS, and SMTP. "
        "A memory aid, top to bottom: All People Seem To Need Data Processing. "
        "The exam will ask which layer a device or protocol operates at. "
        "A switch is layer two. A router is layer three. In the OSI model, encryption is presentation — layer six."
    ),
    "s2": (
        "The TCP/IP model is the practical model the internet actually runs on. "
        "It collapses the seven OSI layers into four. "
        "The Application layer of TCP/IP combines OSI layers five, six, and seven. "
        "The Transport layer maps to OSI layer four — TCP and UDP. "
        "The Internet layer maps to OSI layer three — IP. "
        "And the Link, or Network Access, layer combines OSI layers one and two. "
        "TCP is connection-oriented. It uses the three-way handshake — SYN, SYN-ACK, ACK — "
        "to establish a reliable, ordered, error-checked session. "
        "UDP is connectionless. No handshake, no guaranteed delivery — but fast, "
        "ideal for streaming, DNS, and voice over IP. "
        "Encapsulation is the core concept. As data moves down the stack, each layer adds its own header. "
        "The transport layer creates a segment. The network layer wraps it in a packet with IP addresses. "
        "The data link layer wraps that in a frame with MAC addresses. "
        "At the receiving end, each layer strips its header in reverse — de-encapsulation. "
        "Exam tip: a segment lives at layer four, a packet lives at layer three, a frame lives at layer two. "
        "The terminology matters."
    ),
    "s3": (
        "IP addressing identifies hosts on a network. "
        "IPv4 uses 32-bit addresses written as four octets — for example, 192.168.1.1. "
        "IPv6 uses 128-bit addresses, vastly expanding the address space "
        "and building in features like native IPsec support. "
        "Know the private address ranges — they are not routable on the public internet: "
        "10.0.0.0/8, 172.16.0.0/12, and 192.168.0.0/16. "
        "Network Address Translation — NAT — maps private internal addresses to a public address, "
        "conserving public IPs and hiding the internal network structure. "
        "APIPA — the 169.254 range — is self-assigned when a host cannot reach a DHCP server. "
        "Loopback is 127.0.0.1 — the host referring to itself. "
        "Subnetting divides a network into smaller segments using the subnet mask, "
        "which separates the network portion from the host portion of an address. "
        "CIDR notation — the slash number — indicates how many bits belong to the network. "
        "A slash twenty-four means 24 network bits, leaving 254 usable host addresses. "
        "Subnetting improves performance and, critically for security, enables segmentation — "
        "isolating systems so a breach in one segment cannot spread freely to others."
    ),
    "s4": (
        "The exam tests whether you know which protocols are secure and which are dangerous legacy protocols. "
        "For every insecure protocol, know its secure replacement. "
        "FTP transfers files in cleartext on ports 20 and 21 — replace it with SFTP or FTPS. "
        "Telnet provides remote access in cleartext on port 23 — always replace it with SSH on port 22. "
        "HTTP is cleartext web traffic on port 80 — replace it with HTTPS on port 443, which uses TLS. "
        "SNMP versions one and two use cleartext community strings — "
        "use SNMP version three, which adds authentication and encryption. "
        "Email: SMTP is port 25, POP3 is 110, IMAP is 143 — cleartext by default. Secure them with TLS. "
        "DNS runs on port 53 — DNS over TLS and DNS over HTTPS protect query privacy. "
        "LDAP is port 389 — LDAPS over TLS is port 636. "
        "Key exam point: if a protocol transmits credentials or data in cleartext, it is a finding. "
        "The correct answer is almost always the encrypted equivalent. "
        "TLS is the workhorse that secures the modern web — it replaced the deprecated SSL."
    ),
    "s5": (
        "Network hardware operates at specific OSI layers — and that determines what it can see and control. "
        "A hub is a layer one device. It repeats every signal to every port — "
        "no intelligence, and a security and performance liability. "
        "A switch is a layer two device. It forwards frames based on MAC addresses, "
        "sending traffic only to the intended port. "
        "Switches enable VLANs — virtual LANs — which logically segment a network without separate physical hardware. "
        "A router is a layer three device. It forwards packets between networks based on IP addresses "
        "and enforces access control lists. "
        "Network Access Control — NAC — enforces policy on devices before they join the network, "
        "checking posture such as patch level and antivirus status. "
        "The 802.1X standard provides port-based access control, "
        "authenticating a device before granting network access. "
        "Content delivery networks — CDNs — distribute content across geographically dispersed servers, "
        "improving performance and absorbing denial-of-service traffic. "
        "Transmission media matter: fiber optic is the most secure — "
        "it is difficult to tap and immune to electromagnetic interference. "
        "Copper cabling is vulnerable to eavesdropping and interference."
    ),
    "s6": (
        "Firewalls are the classic exam topic — know the generations and what each can inspect. "
        "A packet-filtering firewall is the first generation. It operates at layers three and four, "
        "examining source and destination IP addresses and ports. "
        "It is stateless — it treats each packet in isolation, with no memory of prior traffic. Fast, but easily fooled. "
        "A stateful inspection firewall tracks the state of active connections in a state table. "
        "It knows whether a packet belongs to an established session, "
        "making it far more secure than stateless filtering. "
        "An application-layer proxy firewall operates at layer seven. "
        "It fully terminates the connection and inspects the actual content of the traffic, "
        "acting as an intermediary between client and server. Deep inspection, but slower. "
        "A next-generation firewall combines stateful inspection with deep packet inspection, "
        "intrusion prevention, and application awareness. "
        "A web application firewall — WAF — specifically protects web applications by filtering HTTP traffic, "
        "defending against attacks like SQL injection and cross-site scripting. "
        "Architecture matters: a screened subnet — historically called a DMZ — "
        "places public-facing servers in an isolated zone between two firewalls, "
        "so a compromise there does not reach the internal network."
    ),
    "s7": (
        "Wireless security is heavily tested because wireless removes the physical boundary — "
        "anyone in range can attempt to connect. Know the protocols in order of strength. "
        "WEP — Wired Equivalent Privacy — is fundamentally broken. "
        "Its weak initialization vector can be cracked in minutes. Never use it. "
        "WPA was an interim fix using TKIP — also now considered weak. "
        "WPA2 uses AES with CCMP and was the standard for years. "
        "It remains acceptable but is vulnerable to the KRACK attack "
        "and to offline dictionary attacks on weak pre-shared keys. "
        "WPA3 is the current standard. It uses Simultaneous Authentication of Equals — SAE — "
        "which defeats offline dictionary attacks and provides forward secrecy. "
        "For enterprise wireless, use WPA2 or WPA3 Enterprise with 802.1X, "
        "which authenticates each user individually against a RADIUS server "
        "rather than sharing one pre-shared key. "
        "Threats to know: an evil twin is a rogue access point impersonating a legitimate one to harvest credentials. "
        "A rogue access point is any unauthorized AP connected to the network. "
        "Disable WPS — Wi-Fi Protected Setup — its PIN is brute-forceable. "
        "Exam tip: WPA3 for confidentiality, 802.1X for enterprise authentication."
    ),
    "s8": (
        "Secure communication channels protect data in transit across untrusted networks. "
        "IPsec is the exam's favorite VPN protocol. It operates at the network layer "
        "and has two protocols and two modes. "
        "The two protocols. AH — Authentication Header — provides integrity and authentication but no encryption. "
        "ESP — Encapsulating Security Payload — provides integrity, authentication, "
        "and confidentiality through encryption. "
        "Because AH does not encrypt, ESP is what you use when confidentiality is required. "
        "The two modes. Transport mode encrypts only the payload, leaving the original IP header — "
        "used for host-to-host. "
        "Tunnel mode encrypts the entire original packet and adds a new header — "
        "used for site-to-site and remote-access VPNs. "
        "IKE — Internet Key Exchange — negotiates the security association and keys. "
        "TLS operates higher in the stack and secures application traffic — "
        "it underpins HTTPS and SSL VPNs that work through a browser. "
        "SSH provides an encrypted channel for remote administration and secure file transfer, replacing Telnet. "
        "For remote access, RADIUS and TACACS-plus provide centralized authentication. "
        "TACACS-plus encrypts the entire payload and separates authentication, authorization, and accounting. "
        "RADIUS encrypts only the password."
    ),
    "s9": (
        "Network attacks are tested by scenario — match the description to the attack. "
        "A denial-of-service attack overwhelms a target to make it unavailable. "
        "A distributed denial-of-service — DDoS — uses many compromised hosts, a botnet, to amplify the flood. "
        "A man-in-the-middle attack intercepts and relays communication between two parties "
        "who believe they are talking directly — defeated by mutual authentication and encryption. "
        "ARP poisoning sends forged ARP replies to associate the attacker's MAC address "
        "with another host's IP, redirecting traffic on the local segment. "
        "DNS poisoning, or cache poisoning, corrupts DNS records to redirect victims to malicious sites — "
        "DNSSEC defends against it by signing records. "
        "A SYN flood exploits the TCP three-way handshake, sending many SYN packets without completing it, "
        "exhausting the connection table. "
        "VLAN hopping lets an attacker reach a VLAN they should not access, "
        "through switch spoofing or double-tagging. "
        "Session hijacking steals a valid session token to impersonate a user. "
        "And a smurf attack amplifies ICMP traffic using a network's broadcast address. "
        "Exam tip: segmentation, encryption, and strong authentication are the recurring defenses."
    ),
    # s10 is split into per-question stem/answer clips so the visual reveals in
    # the explainer can be driven by each clip's MEASURED duration. This keeps
    # the answer reveals in sync regardless of TTS engine or speech rate.
    "s10_q1": (
        "Question one. "
        "A network administrator needs a device that forwards traffic between two different IP networks "
        "and can enforce access control lists. "
        "At which OSI layer does this device operate?"
    ),
    "s10_a1": (
        "Answer: Layer three, the Network layer. "
        "A router forwards packets between networks based on IP addresses and can enforce access control lists. "
        "A switch operates at layer two using MAC addresses. A hub operates at layer one. "
        "Routing and logical IP addressing are layer three functions."
    ),
    "s10_q2": (
        "Question two. "
        "A company needs a site-to-site VPN that encrypts the entire original packet, "
        "including the original IP header, and provides confidentiality. "
        "Which IPsec protocol and mode should be used?"
    ),
    "s10_a2": (
        "Answer: ESP in tunnel mode. "
        "ESP — Encapsulating Security Payload — provides confidentiality through encryption, "
        "unlike AH, which offers no encryption. "
        "Tunnel mode encrypts the entire original packet and adds a new IP header, "
        "which is required for site-to-site VPNs."
    ),
    "s10_q3": (
        "Question three. "
        "A security assessor finds a corporate wireless network using WPA2 with a shared pre-shared key. "
        "Management wants to authenticate each user individually and defeat offline dictionary attacks. "
        "What should be recommended?"
    ),
    "s10_a3": (
        "Answer: WPA3 Enterprise with 802.1X. "
        "WPA3 uses Simultaneous Authentication of Equals to defeat offline dictionary attacks, "
        "and 802.1X with a RADIUS server authenticates each user individually "
        "instead of sharing one pre-shared key. "
        "This removes the shared-key weakness entirely."
    ),
    "s11": (
        "Four flashcards before you go. "
        "One: the OSI layers — All People Seem To Need Data Processing. "
        "Switch is layer two, router is layer three, encryption is layer six. "
        "Two: TCP is connection-oriented with the three-way handshake; UDP is connectionless and fast. "
        "A packet is layer three, a frame is layer two. "
        "Three: IPsec — ESP encrypts, AH does not; tunnel mode for site-to-site, transport mode for host-to-host. "
        "Four: wireless — WPA3 is current, WEP is broken, "
        "and 802.1X authenticates enterprise users individually. "
        "That is Domain 4. "
        "Next episode: Domain 5 — Identity and Access Management. "
        "Authentication, authorization, single sign-on, and access control models. "
        "Test yourself right now at zerodaylabs.tech — adaptive practice exams built for CISSP. "
        "And if you want the senior security mindset that decides borderline questions, "
        "Think Like A CISSP is in the description. "
        "Subscribe and we will see you in Domain 5."
    ),
    "s12": (
        "Think Like A CISSP. "
        "Twenty five dollars. "
        "The study guide that gives you the senior security mindset "
        "that separates candidates who pass from experienced engineers who fail. "
        "Stop memorizing. Start reasoning like a security leader. "
        "Link in the description."
    ),
}

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

    The API returns raw PCM (s16le, 24 kHz, mono) encoded as base64.
    ffmpeg converts that to MP3. Requires GOOGLE_API_KEY in .env.
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
    # Retry on 429 (rate limit) with exponential backoff before giving up.
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
        raise RuntimeError(
            f"Google TTS {resp.status_code}: {resp.text[:300]}"
        )
    data = resp.json()
    audio_b64 = (
        data["candidates"][0]["content"]["parts"][0]["inlineData"]["data"]
    )
    pcm_bytes = base64.b64decode(audio_b64)

    mp3 = os.path.join(AUDIO_DIR, f"{key}.mp3")
    proc = subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "s16le", "-ar", "24000", "-ac", "1", "-i", "pipe:0",
            "-codec:a", "libmp3lame", "-qscale:a", "2", mp3,
        ],
        input=pcm_bytes,
        capture_output=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"ffmpeg PCM→MP3 failed: {proc.stderr.decode()[:200]}"
        )
    # Throttle to stay under the free-tier per-minute request cap.
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
                        help="Only generate these keys (e.g. --only s2 s3)")
    args = parser.parse_args()

    if ELEVEN_API_KEY:
        engine = "ElevenLabs"
        voice_label = ELEVEN_VOICE_ID
    elif GOOGLE_API_KEY:
        engine = "Google AI Studio TTS"
        voice_label = GOOGLE_TTS_VOICE
    else:
        engine = "Pico (offline fallback)"
        voice_label = "N/A"
    print(f"Engine: {engine}")
    print(f"Voice:  {voice_label}")
    print(f"Output: {AUDIO_DIR}")

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
            if ELEVEN_API_KEY:
                mp3 = generate_elevenlabs(key, text)
            elif GOOGLE_API_KEY:
                mp3 = generate_google_tts(key, text)
            else:
                mp3 = generate_pico(key, text)
            durations[key] = round(duration_of(mp3), 2)
            print(f"  {key}: {durations[key]:.1f}s → {mp3}")
        except Exception as e:
            print(f"  {key}: TTS FAILED — {e}")
            # If ElevenLabs failed and Google is available, try it before Pico
            if ELEVEN_API_KEY and GOOGLE_API_KEY:
                print(f"         Attempting Google TTS fallback...")
                try:
                    mp3 = generate_google_tts(key, text)
                    durations[key] = round(duration_of(mp3), 2)
                    print(f"  {key}: {durations[key]:.1f}s → {mp3}  (Google TTS fallback)")
                    continue
                except Exception as ge:
                    print(f"  {key}: Google TTS also failed — {ge}")
            print(f"         Attempting Pico fallback...")
            try:
                mp3 = generate_pico(key, text)
                durations[key] = round(duration_of(mp3), 2)
                print(f"  {key}: {durations[key]:.1f}s → {mp3}  ⚠ PICO FALLBACK")
                pico_fallbacks.append(key)
            except Exception as e2:
                print(f"  {key}: Pico also failed — {e2}  ✗ SCENE MISSING")
                failed_scenes.append(key)

    with open(dur_path, "w") as f:
        json.dump(durations, f, indent=2)

    total = sum(durations.values())
    print(f"\nWrote {dur_path}")
    print(f"Total narration: {total:.1f}s ({total/60:.1f} min)")

    # ── Quality gate ─────────────────────────────────────────────
    if pico_fallbacks or failed_scenes:
        print("\n" + "="*60)
        print("  AUDIO QUALITY GATE — DO NOT RENDER")
        print("="*60)
        if pico_fallbacks:
            keys = " ".join(pico_fallbacks)
            print(f"\n  ⚠  ROBOT VOICE (Pico) used for: {keys}")
            print(f"     Fix: python generate_cissp_d4_narration.py --force --only {keys}")
        if failed_scenes:
            keys = " ".join(failed_scenes)
            print(f"\n  ✗  GENERATION FAILED for: {keys}")
            print(f"     Fix: python generate_cissp_d4_narration.py --force --only {keys}")
        print("\n  Resolve the above before running manim.\n")
        raise SystemExit(1)
    else:
        print(f"\n✓ All scenes generated with {engine} — safe to render.")
