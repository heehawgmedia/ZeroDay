"""
Generate narration audio for the CISSP Domain 1 Part 1 explainer video.

Engine selection (automatic):
  1. ElevenLabs  — if ELEVEN_API_KEY is set (in .env or environment).
  2. SVOX Pico   — offline fallback (pico2wave), works anywhere.

Outputs:
  cissp_d1_p1_audio/s0.mp3 ... cissp_d1_p1_audio/s11.mp3
  cissp_d1_p1_audio/durations.json

Usage:
  python generate_cissp_d1_p1_narration.py              # skip existing valid files
  python generate_cissp_d1_p1_narration.py --force      # regenerate everything
  python generate_cissp_d1_p1_narration.py --only s2 s3 # specific scenes
"""
import json
import os
import re
import subprocess
import argparse

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(BASE_DIR, "cissp_d1_p1_audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(BASE_DIR, ".env"))
except ImportError:
    pass

ELEVEN_API_KEY  = os.environ.get("ELEVEN_API_KEY") or os.environ.get("ELEVENLABS_API_KEY")
ELEVEN_VOICE_ID = os.environ.get("CISSP_VOICE_ID") or os.environ.get("ELEVEN_VOICE_ID", "keLVje3aBMuRpxuu0bqO")
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
        "An organization suffers a major breach. "
        "The CISO had flagged the vulnerability in last quarter's risk assessment. "
        "The board had approved the security budget. "
        "Controls were documented in policy. "
        "And then — nothing. Nobody acted on the findings. "
        "When the regulator investigates, the question is not whether you identified the risk. "
        "The question is: did you do something about it? "
        "That gap — between knowing and doing — is the difference between due diligence and due care. "
        "It is one of the most-tested concepts on the CISSP. We are starting there. "
        "This is D1 Part 1 of the CISSP Domain Mastery Series — Domain 1, Security and Risk Management. "
        "We are mapping to exam outline objectives 1.1, 1.2, 1.3, and 1.5. "
        "Today: the ISC2 Code of Professional Ethics, the five security pillars, "
        "security governance and business alignment, organizational roles and responsibilities, "
        "due care versus due diligence, the major control frameworks, and a compliance overview. "
        "Every item in this episode is exam-tested. Nothing here is background reading."
    ),
    "s2": (
        "The ISC2 Code of Professional Ethics has two parts: a preamble and four canons. "
        "The canons are what the exam tests, and their order is fair game. "
        "Most candidates know the content. They lose points because they forget the sequence. "
        "Canon one: protect society, the common good, necessary public trust and confidence, and the infrastructure. "
        "Society comes first — not your employer, not your client. Society. "
        "Canon two: act honorably, honestly, justly, responsibly, and legally. "
        "This canon governs your professional conduct. "
        "Canon three: provide diligent and competent service to principals. "
        "A principal is any party you serve — your employer, a client. "
        "Competent means you are actually qualified to perform the service. "
        "Canon four: advance and protect the profession. "
        "This comes last. "
        "If canon one and canon four conflict — if protecting the profession requires you to hide something harmful to society — "
        "society wins. Always. "
        "Memory hook: Society, Honor, Service, Profession. "
        "Some candidates remember it as: Security Has Strong Principles. "
        "Your organization may also maintain its own code of ethics. "
        "If an organizational code conflicts with the ISC2 code, the ISC2 code governs. "
        "You cannot contract out of your professional obligations."
    ),
    "s3": (
        "You know the CIA Triad. The CISSP adds two more pillars: authenticity and nonrepudiation. "
        "That gives you five. You need exact definitions and the ability to identify which pillar a scenario violates. "
        "Confidentiality: only authorized entities can access the information. "
        "A misconfigured S3 bucket exposing customer records violates confidentiality. "
        "Integrity: data is accurate, complete, and has not been modified without authorization. "
        "An attacker altering a transaction in transit violates integrity. "
        "Hash functions and checksums protect it. "
        "Availability: authorized users can access systems and data when they need them. "
        "A denial-of-service attack or a ransomware encryption violates availability. "
        "Authenticity: the identity of an entity — a user, a message, a system — is genuine and verifiable. "
        "A spoofed email pretending to come from your CFO violates authenticity. "
        "Digital certificates establish it. "
        "Nonrepudiation: a party cannot deny having performed an action. "
        "If you digitally sign a document, you cannot later claim you did not sign it. "
        "Nonrepudiation typically requires digital signatures combined with audit logs and timestamps. "
        "Exam tip: Authenticity and nonrepudiation are the two pillars candidates most often confuse. "
        "Authenticity answers: is this entity who they claim to be? "
        "Nonrepudiation answers: can they deny this action later? "
        "They are related — but distinct."
    ),
    "s4": (
        "Security governance is the set of policies, processes, and accountability structures "
        "that align the security function to organizational strategy, business goals, mission, and objectives. "
        "Here is the framing the exam demands: think like a CEO, not an engineer. "
        "A CEO does not ask how a firewall rule is configured. "
        "They ask: does our security posture support our business objectives? "
        "Does it protect shareholder value? Does it manage risk to an acceptable level? "
        "Governance answers those questions. "
        "Security must function as a business enabler — not a cost center, not a blocker. "
        "The security program exists to allow the business to operate safely, not to prevent it from operating. "
        "Governance structures include the board of directors, audit committees, and risk committees. "
        "These bodies set the organization's risk appetite — the level of risk the organization is willing to accept "
        "in pursuit of its objectives — and they hold leadership accountable for security outcomes. "
        "These are oversight bodies, not operational bodies. "
        "The board does not configure firewalls. "
        "The board asks whether the right controls exist and whether management is accountable for them."
    ),
    "s5": (
        "Acquisitions and divestitures appear on the exam from a governance and due diligence perspective. "
        "In an acquisition, security's job is to evaluate the target's security posture, policies, "
        "compliance obligations, and data handling practices before the deal closes. "
        "You need to understand what risks the organization is inheriting. "
        "You do not discover a legacy HIPAA liability after signing. "
        "In a divestiture, the security concerns are data classification, access revocation, "
        "and sanitization of systems being transferred or retired. "
        "Who controls what data after the split? "
        "Governance committees — audit committees, risk committees, information security steering committees — "
        "provide the oversight layer between the board and operational security. "
        "They review risk, validate controls, and ensure accountability. They do not run operations."
    ),
    "s6": (
        "This is non-negotiable: senior management owns risk. "
        "Not the CISO. Not the security team. Not the auditor. "
        "When a question asks who is ultimately responsible or accountable for information security, "
        "the answer is senior management. "
        "Security professionals advise. We assess risks, design controls, implement safeguards, and monitor outcomes. "
        "We provide the inputs that management uses to make decisions. "
        "We do not own the risk. Management does — and management cannot delegate that ownership. "
        "Two additional roles the exam tests consistently. "
        "The data owner is a business role — typically a manager or department head — "
        "responsible for classifying data and determining who should be authorized to access it. "
        "The data owner sets the rules. "
        "The data custodian is a technical role — typically IT or operations — "
        "responsible for implementing and maintaining the controls that protect the data on behalf of the owner. "
        "The data custodian follows the rules. "
        "If a question blends those two roles in a wrong answer choice, it is a trap. "
        "The owner decides. The custodian implements."
    ),
    "s7": (
        "Back to the hook. Due diligence and due care are distinct. "
        "The exam will present both in answer choices and require you to select the correct one for a given scenario. "
        "Due diligence is the research and discovery phase. "
        "It means investigating, evaluating, and understanding risks, requirements, and obligations before making a decision. "
        "Reviewing a vendor's SOC 2 report before signing a contract is due diligence. "
        "Reading the risk assessment findings is due diligence. The knowing. "
        "Due care is the action phase. "
        "It means doing what a reasonable and prudent professional would do given what they know. "
        "Implementing the recommended controls after the risk assessment is due care. "
        "Patching the known vulnerability is due care. The doing. "
        "Diligence before. Care after. "
        "You cannot exercise due care without first exercising due diligence. "
        "But — and this is critical — knowing without acting is negligence. "
        "That is exactly what happened in the opening scenario. "
        "The legal standard the exam applies is the reasonable and prudent person test: "
        "what would a competent professional in the same role, with the same knowledge, have done? "
        "Courts use this. Regulators use this. ISC2 uses this. "
        "Memory hook: Diligence equals Discovery. Care equals Conduct."
    ),
    "s8": (
        "The exam tests awareness of the major frameworks — not deep technical content. "
        "Know what each one is designed to do and when an organization would adopt it. "
        "ISO/IEC 27001 is an international standard for establishing an Information Security Management System — an ISMS. "
        "Its primary purpose is independent certification. "
        "Organizations pursue it to demonstrate security posture to customers and regulators. "
        "NIST Cybersecurity Framework is a voluntary, risk-based framework for critical infrastructure. "
        "Its core functions are Govern, Identify, Protect, Detect, Respond, and Recover. "
        "Widely adopted even outside its original scope. "
        "COBIT — Control Objectives for Information and Related Technology — is an IT governance framework. "
        "Its purpose is aligning IT management to business goals. "
        "It sits at the governance layer, not the operational layer. "
        "SABSA — Sherwood Applied Business Security Architecture — is an enterprise security architecture framework "
        "that derives security requirements directly from business objectives. Architecture-first thinking. "
        "PCI DSS — Payment Card Industry Data Security Standard — "
        "applies to any organization that stores, processes, or transmits payment card data. "
        "This is mandatory and contractually enforced by the card brands. "
        "FedRAMP is the US federal government's cloud authorization program. "
        "Any cloud service provider selling to federal agencies must hold FedRAMP authorization. "
        "Mandatory for that market."
    ),
    "s9": (
        "Compliance obligations come from three distinct sources. Know the categories. "
        "Contractual requirements come from agreements — vendor contracts, SLAs, client agreements. "
        "Failure to meet them is a breach of contract, with financial and legal consequences. "
        "Legal requirements come from legislation — HIPAA, GDPR, CCPA. "
        "These are not optional and vary by jurisdiction and data type. "
        "Regulatory requirements come from sector-specific oversight bodies — the SEC, FINRA, CISA. "
        "Noncompliance can mean fines, sanctions, or loss of operating license. "
        "The exam will ask you to categorize a given obligation. Know which bucket each falls into."
    ),
    "s10": (
        "Question one. "
        "A security team is reviewing a prospective cloud vendor's SOC 2 Type II report, "
        "penetration test results, and prior incident disclosures before recommending approval to the CIO. "
        "This activity best represents which concept? "
        "Answer: due diligence. "
        "The team is researching the vendor's security posture before a decision is made. "
        "Due care would follow — implementing contractual security requirements after signing. "
        "Question two. "
        "A CISO documented a critical vulnerability and recommended remediation with a budget estimate six months ago. "
        "Senior leadership declined to fund the remediation. "
        "A breach exploiting that vulnerability occurs. Who bears ultimate accountability? "
        "Answer: senior management. They own the risk. "
        "The CISO fulfilled the advisory role. "
        "Management chose not to act — that is a failure of due care at the leadership level. "
        "Question three. "
        "A security professional is directed by their employer to deny knowledge of a security incident "
        "to a regulatory authority. "
        "According to the ISC2 Code of Ethics, the professional should do what? "
        "Answer: refuse and report if required by law. "
        "Canon one — protect society and the public trust — supersedes the employer directive. "
        "No organizational code of ethics overrides ISC2's."
    ),
    "s11": (
        "Four items for your flashcard. "
        "One: four canons in order — Society, Honor, Service, Profession. "
        "Two: five pillars — confidentiality, integrity, availability, authenticity, nonrepudiation. "
        "Three: senior management owns risk, security professionals advise. "
        "Four: due diligence is discovery, due care is conduct — knowing without acting is negligence. "
        "That is the foundation of Domain 1. "
        "Next episode: Domain 1 Part 2 — risk management concepts, threat modeling, "
        "and quantitative risk calculations including ALE, SLE, and ARO. "
        "If you want to test yourself on today's material right now, head to zerodaylabs.tech — "
        "adaptive practice exams that surface your gaps before the exam does. "
        "And if you want the managerial mindset that decides borderline CISSP questions, "
        "pick up Think Like A CISSP — link in the description. "
        "Hit like, subscribe, and we will see you in Part 2."
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
                        help="Only generate these keys (e.g. --only s2 s3)")
    args = parser.parse_args()

    engine = "ElevenLabs" if ELEVEN_API_KEY else "Pico (offline fallback)"
    print(f"Engine: {engine}")
    print(f"Output: {AUDIO_DIR}")

    dur_path = os.path.join(AUDIO_DIR, "durations.json")
    durations: dict = {}
    if os.path.exists(dur_path):
        with open(dur_path) as f:
            durations = json.load(f)

    pico_fallbacks: list = []   # scenes that fell back to robot voice
    failed_scenes:  list = []   # scenes that failed completely

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
            print(f"     Fix: python generate_cissp_d1_p1_narration.py --force --only {keys}")
        if failed_scenes:
            keys = " ".join(failed_scenes)
            print(f"\n  ✗  GENERATION FAILED for: {keys}")
            print(f"     Fix: python generate_cissp_d1_p1_narration.py --force --only {keys}")
        print("\n  Resolve the above before running manim.\n")
        raise SystemExit(1)
    else:
        print("\n✓ All scenes generated with ElevenLabs — safe to render.")
