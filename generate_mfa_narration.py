"""
Generate narration audio for the MFA explainer video.

Engine selection (automatic):
  1. ElevenLabs  — if ELEVEN_API_KEY is set (in .env or environment).
  2. SVOX Pico   — offline fallback (pico2wave), works anywhere.

Outputs:
  mfa_audio/s0.mp3 ... mfa_audio/s6.mp3
  mfa_audio/durations.json   (read by mfa_explainer.py to sync animations)

Usage:
  python generate_mfa_narration.py              # skip existing valid files
  python generate_mfa_narration.py --force      # regenerate everything
  python generate_mfa_narration.py --only s5 s6 # regenerate specific scenes
"""
import json
import os
import subprocess
import argparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(BASE_DIR, "mfa_audio")
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
        "Your phone buzzes. Six-digit code. You type it in. Account locked — funds gone. "
        "You had two-factor authentication turned on. So what happened? "
        "If you are using SMS codes, you might be one phone call away from losing everything. "
        "Here is why. "
        "Zero Day Labs — Train. Test. Certify."
    ),
    "s2": (
        "Let us get two definitions straight. "
        "Authentication is proving who you are. "
        "Authorization is what you are allowed to do once you have proven it. "
        "Multi-factor authentication means you prove identity using at least two different factor types. "
        "And every factor falls into one of three classic categories — and these are exam gold. "
        "First: something you know. Passwords, PINs, security questions. "
        "Second: something you have. A smart card, hardware token, or authenticator app. "
        "Third: something you are. Biometrics — fingerprint, face scan, iris, voice. "
        "Security Plus and CISSP exams also test two extended factors. "
        "Somewhere you are — your physical location. "
        "And something you do — behavioral biometrics, like how you type or move a mouse. "
        "Now here is the most important exam trap in this entire topic. "
        "A password plus a security question is NOT multi-factor authentication. "
        "Both inputs are something you know. That is one factor — two inputs from the same category. "
        "The exam will test this. It is a classic trap. "
        "The rule is simple: MFA requires two different factor types."
    ),
    "s3": (
        "So why is SMS not enough? "
        "Here is how it works. You log in. The server sends a six-digit code to your phone. You enter it. Access granted. "
        "Sounds secure. Let us break it. "
        "Attack one: SIM swapping. "
        "An attacker calls your mobile carrier, impersonates you, and convinces them to port your number "
        "to a SIM the attacker controls. "
        "From that moment, every SMS code you are supposed to receive goes to the attacker instead. "
        "This is the dominant real-world attack against SMS two-factor authentication. "
        "It is used in account takeover and crypto theft constantly. "
        "Attack two: SS7 protocol weaknesses. "
        "SS7 is the decades-old signaling protocol that routes every phone call and text message globally. "
        "Nation-state actors and sophisticated attackers can exploit SS7 to intercept your messages in transit. "
        "No malware on your phone required. The vulnerability is in the network itself. "
        "Attack three: phishing and real-time relay. "
        "The attacker builds a fake login page that looks exactly like your bank or email provider. "
        "You enter your password — captured. You enter your SMS code — captured. "
        "The attacker immediately replays both to the real site within the thirty-second window. "
        "SMS codes are phishable. They do nothing against an adversary in the middle. "
        "Attack four: mobile malware that silently forwards your incoming texts to the attacker. "
        "Here is a critical exam reference: NIST Special Publication 800-63B. "
        "The United States government has officially flagged SMS and PSTN-based authentication as restricted. "
        "When federal agencies are told to move away from something, pay attention. "
        "Write down NIST 800-63B — it is exam relevant. "
        "Here is an important nuance: SMS MFA is still better than no MFA. "
        "The goal is not to turn it off. The goal is to upgrade when you can. "
        "Flashcard: SMS is phishable, SIM-swappable, and interceptable."
    ),
    "s4": (
        "So what do you use instead? "
        "Here is the MFA strength ladder — weakest to strongest. "
        "Level one: SMS and voice codes. "
        "Better than nothing, but phishable and SIM-swappable. If this is all you have, keep it. Just know the risk. "
        "Level two: TOTP authenticator apps. "
        "Google Authenticator, Microsoft Authenticator, Authy. "
        "Codes are generated directly on your device. Immune to SIM swapping. "
        "But still phishable via relay — an attacker can still capture and replay them in real time. "
        "Level three: push notifications with number matching. "
        "More resistant to basic phishing because you have to match a number displayed on screen. "
        "But this level is vulnerable to push bombing — also called MFA fatigue. "
        "The attacker floods your phone with approval requests at two in the morning "
        "hoping you tap approve just to make it stop. "
        "Know this term. It appears on certification exams. "
        "Level four: phishing-resistant MFA. FIDO2. WebAuthn. Hardware keys like YubiKey. Platform passkeys. "
        "This is the gold standard and where the entire industry is heading. "
        "Here is why FIDO2 is fundamentally different. "
        "The cryptographic key validates the actual origin of the website it is talking to. "
        "If you are on a fake site, the hardware key simply does not respond. "
        "The relay attack fails by design. "
        "The human can be tricked. The cryptography cannot. "
        "One-line takeaway: FIDO2 and passkeys are the only MFA methods that make phishing technically impossible."
    ),
    "s5": (
        "Quick exam prep. "
        "Know your three factor categories cold — something you know, something you have, something you are. "
        "Spot the same-factor trap — a password plus a PIN is one factor, not two. "
        "Know that SMS is the weakest MFA form — SIM swap, SS7, phishing relay. "
        "Know these terms: TOTP. Push bombing. MFA fatigue. FIDO2. WebAuthn. Passkeys. NIST 800-63B. "
        "Sample exam question: A user authenticates with a password and a four-digit PIN. How many factors is this? "
        "Pause. "
        "The answer is one. Both are something you know. One factor, two inputs. Classic trap."
    ),
    "s6": (
        "If the way I broke that down clicked for you, that is exactly how I teach exam strategy in Think Like A CISSP. "
        "It is a mindset guide for thinking the way the exam expects you to think — not just memorizing definitions. "
        "Twenty five dollars at Zero Day Labs dot tech — link in the description. "
        "If you are prepping for Security Plus or CISSP, head to Zero Day Labs dot tech. "
        "We use adaptive practice exams that learn your weak spots and drill you on exactly what you need, "
        "so you spend less time grinding and more time actually moving toward your certification. "
        "Train. Test. Certify. "
        "Thanks for watching. Hit like, subscribe, and share with someone who needs this. "
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
                        help="Only generate these keys (e.g. --only s0 s5)")
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
