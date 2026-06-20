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
import json, os, re, subprocess, argparse

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

    engine = "ElevenLabs" if ELEVEN_API_KEY else "Pico (offline fallback)"
    print(f"Engine: {engine}")
    print(f"Voice:  {ELEVEN_VOICE_ID}")
    print(f"Output: {AUDIO_DIR}")
    print(f"Keys:   {len(NARRATIONS)} segments across 5 shorts\n")

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
                print(f"  {key}: Pico also failed — {e2}  ✗ SEGMENT MISSING")
                failed_scenes.append(key)

    with open(dur_path, "w") as f:
        json.dump(durations, f, indent=2)

    total = sum(durations.values())
    print(f"\nWrote {dur_path}")
    print(f"Total narration: {total:.1f}s ({total/60:.1f} min)")
    print(f"Avg per short:   {total/5:.1f}s")

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
        print("\n✓ All segments generated with ElevenLabs — safe to render.")
        print("\nRender commands:")
        for short in ["CIATriad", "DataClassification", "ZeroTrust",
                      "IncidentResponse", "ExamTraps"]:
            print(f"  manim -qh cissp_shorts.py {short}")
