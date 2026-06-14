"""
Generate narration audio for each scene of the encryption explainer video.

Engine selection (automatic):
  1. ElevenLabs  — if ELEVEN_API_KEY is set (in .env or environment). Studio quality.
  2. SVOX Pico   — offline fallback (pico2wave), works anywhere.

Outputs:
  audio/s1.mp3 ... audio/s8.mp3
  audio/durations.json   (read by encryption_explainer.py to sync animations)
"""
import json
import os
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(BASE_DIR, "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

# Load .env if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(BASE_DIR, ".env"))
except ImportError:
    pass

ELEVEN_API_KEY = os.environ.get("ELEVEN_API_KEY") or os.environ.get("ELEVENLABS_API_KEY")
# Adam — classic deep narration voice. Override with ELEVEN_VOICE_ID in .env
ELEVEN_VOICE_ID = os.environ.get("ELEVEN_VOICE_ID", "pNInz6obpgDQGcFmaJgB")
ELEVEN_MODEL = os.environ.get("ELEVEN_MODEL", "eleven_multilingual_v2")

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
        "Look at your screen right now. Every login you make, every message you send, "
        "every bank transaction you complete — all of that starts as plain, readable data. "
        "Without protection, anyone intercepting it could read it instantly. "
        "Today, we are going to cover two of the most important tools in cybersecurity — "
        "encryption and hashing. "
        "They both scramble data. But they are NOT the same thing. "
        "And confusing them? That is how security breaches happen."
    ),
    "s2": (
        "Here is the core question. If both encryption and hashing scramble data — "
        "why do we have two different things? "
        "The answer is simple: they solve completely different problems. "
        "Encryption is designed to be reversed. "
        "Hashing is designed to NEVER be reversed. "
        "That single difference changes everything about how, and when, you use each one."
    ),
    "s3": (
        "Let us start with encryption. "
        "You have a message — let us say: Hello Alice. "
        "You feed it into an encryption algorithm along with a key. "
        "Out comes ciphertext — a completely scrambled, unreadable version of your original message. "
        "Now here is the key point — literally. "
        "Because you have the key, you can run this process in reverse. "
        "Feed the ciphertext back in with the same key, "
        "and you get Hello Alice back. "
        "That reversibility is the entire point of encryption. "
        "You are locking something up so you can unlock it later. "
        "There are two main types. "
        "Symmetric encryption uses the same key to lock and unlock. "
        "AES is the gold standard here, used in everything from your Wi-Fi to your bank. "
        "Asymmetric encryption uses a pair of keys — "
        "a public key to encrypt, and a private key to decrypt. "
        "RSA is the classic example. "
        "Your browser uses this every single time it connects to a website."
    ),
    "s4": (
        "Now let us talk about hashing. "
        "Same input — Hello Alice. "
        "We run it through a hash function like SHA-256. "
        "Out comes a fixed-length string of characters called a hash, or digest. "
        "Now watch what happens when we try to go backwards. "
        "We cannot. "
        "There is no key. There is no reverse function. "
        "The hash function permanently destroys the path back to the original data. "
        "This is completely intentional. "
        "Hashing has two properties that make it incredibly useful. "
        "First: it is deterministic. "
        "Hello Alice will always produce the exact same hash. Every single time. "
        "Second — and this is the fascinating part — the avalanche effect. "
        "Change just one character. Add an exclamation mark. "
        "The output hash is completely, wildly different. "
        "Not a little different. Unrecognizably different. "
        "This is what makes hashing so powerful for detecting tampering — "
        "if even a single byte of your data changes, the hash changes completely. "
        "And you will know immediately."
    ),
    "s5": (
        "Let us lock in the differences side by side. "
        "Encryption is reversible. Hashing is not. "
        "Encryption requires a key. Hashing requires no key at all. "
        "Both produce consistent outputs for the same input. "
        "Encryption is used for secure data transmission. "
        "Hashing is used for integrity checking and storing passwords. "
        "Both are essential in modern security. "
        "But they are tools built for completely different jobs."
    ),
    "s6": (
        "Where do we actually see these in action? "
        "Every time your browser connects to a website using HTTPS, encryption is working. "
        "Your browser and the server negotiate a shared key "
        "and use AES to encrypt everything flowing between them. "
        "Your bank, your email, your messages — all encrypted in transit using TLS. "
        "Now for hashing. "
        "When you create an account on any modern website, "
        "your password is never stored as plain text. It is hashed. "
        "When you log in, the site hashes what you typed "
        "and compares it to the stored hash. "
        "They never need to see your actual password. "
        "And this is exactly why Forgot Password does not show you your old password — "
        "the site literally cannot look it up. It no longer exists in readable form. "
        "Modern systems take this even further with salting — "
        "adding a unique random value before hashing "
        "to prevent rainbow table attacks. "
        "The salt means that even two users with the same password "
        "will have completely different stored hashes."
    ),
    "s7": (
        "Here is the rule. "
        "Storing a password? Hash it. Never encrypt it. "
        "Sending a secret that someone needs to actually read later? Encrypt it. Never hash it. "
        "The classic mistake is encrypting passwords instead of hashing them. "
        "And this mistake has caused some of the biggest data breaches in history. "
        "Why? Because encryption requires a key. "
        "And if an attacker finds that key — "
        "every single password in your database is instantly readable. "
        "With hashing, even if an attacker gets the entire database, "
        "they still cannot reverse the hashes without enormous effort. "
        "Right tool. Right job. Every time."
    ),
    "s8": (
        "Let us recap. "
        "Encryption: scramble and unscramble, needs a key. "
        "Hashing: scramble permanently, no key needed. "
        "Right tool for the right job. "
        "That is what separates a developer who writes secure code "
        "from one who creates vulnerabilities. "
        "You now know the difference. "
        "Now you think like a security professional."
    ),
    "s9": (
        "Thanks for watching. "
        "If this video helped you, hit like, subscribe, and share it with someone studying for their exam — "
        "it really does help the channel grow. "
        "And if you want to actually pass — not just study — "
        "check out Zero Day Labs at www dot zerodaylabs dot tech. "
        "We use adaptive testing that learns exactly where you are weak "
        "and drills you on what matters most, "
        "so you spend less time grinding and more time progressing. "
        "Train. Test. Certify. "
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


def is_valid_mp3(path: str) -> bool:
    """Return True only if the file exists and ffprobe can read a duration from it."""
    if not os.path.exists(path) or os.path.getsize(path) < 1024:
        return False
    try:
        dur = duration_of(path)
        return dur > 0.5
    except Exception:
        return False


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true",
                        help="Regenerate all audio even if files already exist")
    parser.add_argument("--only", nargs="+", metavar="KEY",
                        help="Only generate these keys (e.g. --only s0 s9)")
    args = parser.parse_args()

    engine = "ElevenLabs" if ELEVEN_API_KEY else "Pico (offline fallback)"
    print(f"Engine: {engine}")

    # Load existing durations so we can preserve entries we skip
    dur_path = os.path.join(AUDIO_DIR, "durations.json")
    durations: dict = {}
    if os.path.exists(dur_path):
        with open(dur_path) as f:
            durations = json.load(f)

    pico_fallbacks: list = []
    failed_scenes: list = []
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
            print(f"  {key}: ElevenLabs FAILED — {e}")
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
            print(f"     Fix: python generate_narration.py --force --only {keys}")
        if failed_scenes:
            keys = " ".join(failed_scenes)
            print(f"\n  ✗  GENERATION FAILED for: {keys}")
            print(f"     Fix: python generate_narration.py --force --only {keys}")
        print("\n  Resolve the above before running manim.\n")
        raise SystemExit(1)
    else:
        print("\n✓ All scenes generated with ElevenLabs — safe to render.")
