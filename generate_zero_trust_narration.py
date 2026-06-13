"""
Generate narration audio for the Zero Trust explainer video.

Engine selection (automatic):
  1. ElevenLabs  — if ELEVEN_API_KEY is set (in .env or environment).
  2. SVOX Pico   — offline fallback (pico2wave), works anywhere.

Outputs:
  zt_audio/s0.mp3 ... zt_audio/s7.mp3
  zt_audio/durations.json

Usage:
  python generate_zero_trust_narration.py              # skip existing valid files
  python generate_zero_trust_narration.py --force      # regenerate everything
  python generate_zero_trust_narration.py --only s3 s4 # specific scenes
"""
import json
import os
import subprocess
import argparse

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(BASE_DIR, "zt_audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(BASE_DIR, ".env"))
except ImportError:
    pass

ELEVEN_API_KEY  = os.environ.get("ELEVEN_API_KEY") or os.environ.get("ELEVENLABS_API_KEY")
ELEVEN_VOICE_ID = os.environ.get("ELEVEN_VOICE_ID", "pNInz6obpgDQGcFmaJgB")  # Adam
ELEVEN_MODEL    = os.environ.get("ELEVEN_MODEL", "eleven_multilingual_v2")

NARRATIONS = {
    "s0": (
        "Before we dive in — if this video gets you thinking like a security professional, "
        "imagine what a full guide could do. "
        "Think Like A CISSP teaches you the senior security mindset that separates "
        "candidates who pass from experienced engineers who fail. "
        "Reason like a security leader, not just a technician. "
        "Twenty five dollars at Zero Day Labs dot tech — link in the description."
    ),
    "s1": (
        "Your firewall says this user is trusted. "
        "Zero Trust says: prove it. Again. "
        "Every request. Every device. Every time. "
        "Somewhere right now, an attacker is inside a corporate network "
        "moving laterally on a single stolen credential. "
        "The firewall let them in — because they looked trusted. "
        "That assumption is the vulnerability. "
        "That is what Zero Trust is designed to eliminate. "
        "Zero Day Labs — Train. Test. Certify."
    ),
    "s2": (
        "For decades, security was built on one assumption: "
        "trust everything inside the perimeter, trust nothing outside it. "
        "Castle walls and a moat. "
        "If you're inside, you belong there. "
        "This worked when every employee sat in the same building "
        "and your data lived in one server room. "
        "Then came cloud computing. Then remote work. Then SaaS. "
        "The perimeter dissolved. "
        "Your data now lives across AWS, Azure, Salesforce, and dozens of other platforms. "
        "Your employees connect from home networks, coffee shops, and airports. "
        "The moat is gone — but many organizations are still trusting anyone who reaches where the drawbridge used to be. "
        "Here is the concrete danger. "
        "An attacker phishes one employee. Gets their credentials. "
        "Inside the old perimeter model, that attacker can now move laterally — "
        "from system to system — largely unchallenged. "
        "One set of credentials. Unlimited internal access. "
        "That is the attack pattern behind the biggest breaches of the past decade."
    ),
    "s3": (
        "Zero Trust is not a product. It is an architecture. A strategy. A shift in how you think about trust. "
        "The core principle, straight from NIST Special Publication 800-207: "
        "never trust, always verify. "
        "Zero Trust has three pillars. Know these for the exam. "
        "Pillar one: verify explicitly. "
        "Every user, every device, every application, every request — "
        "verified every single time using every available signal: "
        "who you are, what device you're on, where you are, what time it is, what you're trying to do. "
        "Not just at login. Every access decision, in real time. "
        "Pillar two: least privilege access. "
        "Give users just enough access to do their job — nothing more, nothing less. "
        "Just in time, just enough. "
        "If you need temporary elevated access, you get it for that task only, then it is revoked automatically. "
        "Pillar three: assume breach. "
        "Operate as if an attacker is already inside. "
        "Segment your network so lateral movement is blocked. "
        "Monitor everything. Limit the blast radius. "
        "Because breaches happen — the question is how much damage they can do before you contain them. "
        "And here is the misconception you need to kill: "
        "Zero Trust is not a product you buy from one vendor. "
        "No vendor sells you Zero Trust in a box. "
        "It is a framework implemented across identity, devices, networks, applications, and data."
    ),
    "s4": (
        "Let us walk through a real scenario. "
        "An employee — call her Sarah — opens her laptop at a coffee shop "
        "and tries to access the payroll system. "
        "In the old model: VPN connection, inside the trusted network, access granted. Done. "
        "In a Zero Trust model, every step is verified. "
        "Identity check: Sarah's identity is confirmed with multi-factor authentication. "
        "Device check: is her laptop company-managed, fully patched, with no signs of compromise? "
        "Context check: is this a normal time for Sarah to access payroll? "
        "Is the location flagged? Does the behavior match her baseline? "
        "All of this goes through what NIST calls the Policy Decision Point — "
        "the brain of a Zero Trust architecture. "
        "It evaluates every signal and makes a real-time access decision. "
        "Result: Sarah gets access to the payroll application specifically. "
        "Not to the internal network. Not to other systems. "
        "Just the app she needs, at that moment, from that device. "
        "That is ZTNA — Zero Trust Network Access — "
        "replacing the VPN's blanket internal access with per-app, per-session decisions. "
        "And if Sarah's device was compromised? "
        "Access denied — or severely limited — automatically. No human intervention required. "
        "This is microsegmentation in action: "
        "even if one session is breached, the attacker cannot move laterally. "
        "The blast radius is contained."
    ),
    "s5": (
        "Three reasons Zero Trust went from a NIST research paper to every vendor's pitch deck. "
        "First: the perimeter died. "
        "Remote work and cloud adoption killed it. "
        "You cannot protect a perimeter that no longer exists. "
        "Second: the breaches proved it. "
        "SolarWinds. Colonial Pipeline. Lateral movement after a single credential compromise "
        "is the attack pattern behind the biggest incidents of the past decade. "
        "Third: the government mandated it. "
        "In May 2021, United States Executive Order 14028 required federal agencies "
        "to adopt a Zero Trust architecture. "
        "That single document sent every vendor scrambling to slap the term on their products. "
        "Be honest about this: Zero Trust is massively over-marketed. "
        "Every firewall vendor calls their product Zero Trust. Most are repackaging existing features. "
        "The architecture underneath is real. The buzzword is noise. Know the difference."
    ),
    "s6": (
        "What you need to know for Security Plus and CISSP. "
        "Security Plus SY0-701 Domain 1 tests Zero Trust explicitly: "
        "the control plane versus the data plane, adaptive identity, "
        "policy engine, policy administrator, and policy enforcement point. "
        "Know what layer each element sits at. "
        "CISSP examines Zero Trust across domains one, three, five, and seven — "
        "security governance, architecture, identity, and communications. "
        "Quick recap of the three pillars. "
        "Verify explicitly — every user, device, and request, every time. "
        "Least privilege — just enough access, just in time. "
        "Assume breach — segment, monitor, limit blast radius. "
        "One exam trap: Zero Trust is NOT a product. "
        "The exam tests whether you understand it as an architecture and a strategy — "
        "not a solution you install. "
        "NIST 800-207 is the authoritative reference. Write that down."
    ),
    "s7": (
        "If this made Zero Trust click, that is exactly what I do in Think Like A CISSP — "
        "break down complex frameworks the way the exam expects you to reason through them. "
        "Twenty five dollars at Zero Day Labs dot tech — link in the description. "
        "Head to Zero Day Labs dot tech for adaptive practice exams "
        "built to find your weak spots before the exam does. "
        "Train. Test. Certify. "
        "Hit like, subscribe, and drop a comment — "
        "what security buzzword should I break down next? "
        "See you in the next one."
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


def generate_elevenlabs(key: str, text: str) -> str:
    from elevenlabs.client import ElevenLabs
    client = ElevenLabs(api_key=ELEVEN_API_KEY)
    mp3 = os.path.join(AUDIO_DIR, f"{key}.mp3")
    audio = client.text_to_speech.convert(
        voice_id=ELEVEN_VOICE_ID,
        model_id=ELEVEN_MODEL,
        text=text,
        output_format="mp3_44100_128",
    )
    with open(mp3, "wb") as f:
        for chunk in audio:
            f.write(chunk)
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
                        help="Only generate these keys (e.g. --only s3 s4)")
    args = parser.parse_args()

    engine = "ElevenLabs" if ELEVEN_API_KEY else "Pico (offline fallback)"
    print(f"Engine: {engine}")
    print(f"Output: {AUDIO_DIR}")

    dur_path = os.path.join(AUDIO_DIR, "durations.json")
    durations: dict = {}
    if os.path.exists(dur_path):
        with open(dur_path) as f:
            durations = json.load(f)

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
            else:
                mp3 = generate_pico(key, text)
            durations[key] = round(duration_of(mp3), 2)
            print(f"  {key}: {durations[key]:.1f}s → {mp3}")
        except Exception as e:
            print(f"  {key}: FAILED — {e}")
            print(f"         Falling back to Pico TTS...")
            try:
                mp3 = generate_pico(key, text)
                durations[key] = round(duration_of(mp3), 2)
                print(f"  {key}: {durations[key]:.1f}s → {mp3} (Pico fallback)")
            except Exception as e2:
                print(f"  {key}: Pico also failed — {e2}")

    with open(dur_path, "w") as f:
        json.dump(durations, f, indent=2)

    total = sum(durations.values())
    print(f"\nWrote {dur_path}")
    print(f"Total narration: {total:.1f}s ({total/60:.1f} min)")
