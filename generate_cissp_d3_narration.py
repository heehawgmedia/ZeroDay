"""
Generate narration audio for the CISSP Domain 3 explainer video.

Engine selection (automatic):
  1. ElevenLabs  — if ELEVEN_API_KEY is set (in .env or environment).
  2. SVOX Pico   — offline fallback (pico2wave), works anywhere.

Outputs:
  cissp_d3_audio/s0.mp3 ... cissp_d3_audio/s12.mp3
  cissp_d3_audio/durations.json

Usage:
  python generate_cissp_d3_narration.py              # skip existing valid files
  python generate_cissp_d3_narration.py --force      # regenerate everything
  python generate_cissp_d3_narration.py --only s2 s3 # specific scenes
"""
import json
import os
import re
import subprocess
import argparse

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(BASE_DIR, "cissp_d3_audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(BASE_DIR, ".env"))
except ImportError:
    pass

ELEVEN_API_KEY  = os.environ.get("ELEVEN_API_KEY") or os.environ.get("ELEVENLABS_API_KEY")
ELEVEN_VOICE_ID = os.environ.get("CISSP_D3_VOICE_ID", "TABZn6CDfjMNGrsnGzzD")
ELEVEN_MODEL    = os.environ.get("ELEVEN_MODEL", "eleven_multilingual_v2")

NARRATIONS = {
    "s0": (
        "A developer writes an error handler that returns the full stack trace to the browser on any exception. "
        "A network engineer configures a firewall to permit all traffic unless explicitly blocked. "
        "A systems architect places both redundant servers in the same rack. "
        "Three failures. Three disciplines. One root cause: none of them applied the principles of secure design. "
        "This is Domain 3 of the CISSP Domain Mastery Series — Security Architecture and Engineering. "
        "We map to objectives 3.1 through 3.9. "
        "Today: secure design principles, the Bell-LaPadula and Biba security models, "
        "Clark-Wilson and Brewer-Nash, the trusted computing base and reference monitor, "
        "security evaluation criteria including Common Criteria and TCSEC, "
        "symmetric and asymmetric cryptography, hashing and digital signatures, "
        "PKI and key management, cryptanalytic attacks, and physical security. "
        "Every concept in this video is exam-tested."
    ),
    "s1": (
        "Secure design principles are the rules that constrain how systems are built "
        "to maintain security properties even when components fail or are attacked. "
        "The exam presents scenarios and tests whether you can identify which principle applies or was violated. "
        "Fail-safe defaults: systems should deny access by default. "
        "Permissions are granted explicitly, not assumed. "
        "A firewall that permits all traffic unless told otherwise violates this principle. "
        "A system that fails open — granting access when it cannot verify identity — violates this principle. "
        "Least privilege: every user, process, and service receives only the minimum permissions "
        "required to perform its function. Nothing more. "
        "A web server running as root violates least privilege. "
        "Separation of duties: no single person can complete a sensitive transaction alone. "
        "Two people must cooperate. This requires collusion to commit fraud — it is a preventive control. "
        "Defense in depth: security is layered. Multiple independent controls protect the same asset. "
        "If one layer fails, the next one catches it. No single point of failure in the security design. "
        "Zero trust: never trust, always verify. No implicit trust based on network location. "
        "Requests from inside the network receive the same scrutiny as requests from outside. "
        "Open design: the security of a mechanism should not depend on the secrecy of its design — "
        "only on the secrecy of the key. Security through obscurity is not a principle — it is a risk."
    ),
    "s2": (
        "Security models are formal frameworks specifying the rules a system must enforce "
        "to maintain a security property. "
        "The two most tested models are Bell-LaPadula and Biba. Know the rules exactly — not just the names. "
        "Bell-LaPadula is a confidentiality model developed for the U.S. military. "
        "Its goal is to prevent unauthorized disclosure of classified information. "
        "It enforces two rules. "
        "The simple security property: no read up. A subject cannot read data at a higher classification level. "
        "The star property: no write down. A subject cannot write data to a lower classification level. "
        "This prevents classified information from flowing into an unclassified container. "
        "Memory hook: Bell-LaPadula — no read up, no write down. Protects confidentiality. "
        "Biba is an integrity model. It is the inverse of Bell-LaPadula. "
        "Its goal is to prevent unauthorized modification of data by untrusted subjects. "
        "The simple integrity property: no read down. "
        "A subject cannot read data at a lower integrity level — to avoid contaminating decisions with untrusted input. "
        "The star integrity property: no write up. A subject cannot write to a higher integrity level. "
        "Memory hook: Biba — no read down, no write up. Protects integrity. "
        "The exam will give you a scenario and ask which model applies. "
        "Confidentiality concern — Bell-LaPadula. Integrity concern — Biba."
    ),
    "s3": (
        "Two more security models, then the architectural concepts that implement them. "
        "Clark-Wilson is an integrity model for commercial environments. "
        "It enforces integrity through well-formed transactions and separation of duties. "
        "The model defines constrained data items — CDIs — which must remain accurate and consistent. "
        "Transformation procedures — TPs — are the only operations permitted to modify CDIs. "
        "Users cannot access CDIs directly. They go through transformation procedures, "
        "which enforce separation of duties and create an audit trail. "
        "Clark-Wilson is the model behind double-entry bookkeeping. "
        "Brewer-Nash — also called the Chinese Wall model — prevents conflicts of interest. "
        "A subject who has accessed data about one company cannot access competing data about a rival company. "
        "The wall grows dynamically as the subject accesses data. "
        "Used in investment banking and legal environments. "
        "The Trusted Computing Base is the combination of all hardware, firmware, and software components "
        "that enforce the security policy of a system. "
        "Everything inside the TCB is trusted. Everything outside is not. "
        "The reference monitor is the abstract concept: an access control mechanism that "
        "mediates every access between subjects and objects. "
        "It must be always invoked, tamper-proof, and small enough to be verified. "
        "The security kernel is the concrete implementation of the reference monitor in hardware and software."
    ),
    "s4": (
        "Security evaluation criteria provide a standardized way to verify that a product's security claims "
        "have been independently tested and validated. "
        "The primary international standard is Common Criteria — ISO slash IEC 15408. "
        "Common Criteria defines Evaluation Assurance Levels — EALs — from one through seven. "
        "EAL one: functionally tested. Lowest assurance — basic examination of claimed functions. "
        "EAL two: structurally tested. "
        "EAL three: methodically tested and checked. "
        "EAL four: methodically designed, tested, and reviewed. "
        "This is the highest level routinely achievable for commercial products. "
        "Most enterprise security products are evaluated at EAL two through four. "
        "EAL five through seven require increasingly formal mathematical proofs of security properties. "
        "EAL seven — formally verified design and tested — is used in military and government systems. "
        "A Protection Profile defines the security requirements for a class of products. "
        "A Security Target is the vendor's specific claim about what their product provides. "
        "Evaluation validates the Security Target against the actual product. "
        "TCSEC — the Trusted Computer System Evaluation Criteria, also called the Orange Book — "
        "was the predecessor to Common Criteria in the United States. "
        "It defined four divisions: D — minimal protection, C — discretionary, "
        "B — mandatory access controls, A — formally verified. "
        "TCSEC has been superseded by Common Criteria but may appear on the exam as a historical reference."
    ),
    "s5": (
        "Cryptography is one of the most heavily tested areas in Domain 3. "
        "Symmetric encryption uses the same key for both encryption and decryption. "
        "It is fast and efficient — well suited for encrypting large volumes of data. "
        "The fundamental challenge with symmetric encryption is key distribution: "
        "how do two parties securely share a key before they can communicate securely? "
        "If the channel is insecure, the key cannot be safely transmitted. "
        "The number of keys required for n parties to communicate is n times n minus one divided by two. "
        "For one hundred parties, that is four thousand nine hundred fifty keys. This does not scale. "
        "Key algorithms. DES — Data Encryption Standard — uses a 56-bit key. It is broken and must not be used. "
        "Triple-DES — 3DES — applies DES three times for effective key lengths of 112 or 168 bits. Deprecated. "
        "AES — Advanced Encryption Standard — is the current standard. "
        "Key sizes: 128, 192, or 256 bits. AES is fast in hardware and considered secure. "
        "Block cipher modes matter. ECB mode is insecure: identical plaintext blocks produce identical ciphertext, "
        "revealing patterns in the data. "
        "CBC mode chains blocks together, eliminating ECB's weakness. "
        "GCM mode provides authenticated encryption — confidentiality and integrity in a single pass."
    ),
    "s6": (
        "Asymmetric encryption uses a mathematically related key pair — a public key and a private key. "
        "What one key encrypts, only the other can decrypt. "
        "The public key is freely distributed. The private key is never shared. "
        "Asymmetric encryption solves the key distribution problem: "
        "anyone can encrypt using your public key, and only you can decrypt with your private key. "
        "It is much slower than symmetric — not suitable for bulk data. "
        "In practice, asymmetric is used to exchange a symmetric session key. Symmetric handles the data. "
        "This combination is called hybrid encryption, and it is how TLS works. "
        "RSA is the dominant asymmetric algorithm. Its security rests on the difficulty of factoring large integers. "
        "ECC — Elliptic Curve Cryptography — achieves equivalent security with much shorter key lengths. "
        "A 256-bit ECC key provides security equivalent to a 3072-bit RSA key. Preferred in mobile and IoT contexts. "
        "Diffie-Hellman is a key agreement protocol — not encryption. "
        "It allows two parties to derive a shared secret over an insecure channel without ever transmitting the secret. "
        "Hash functions produce a fixed-length digest from any input. "
        "They are one-way: you cannot reverse a hash to recover the original input. "
        "Properties: deterministic, collision-resistant, and the avalanche effect — "
        "changing one input bit changes approximately half the output bits. "
        "MD5 produces 128-bit digests and is broken. SHA-1 is deprecated. "
        "SHA-256 and SHA-3 are the current standards. "
        "Hashing provides integrity verification — not confidentiality, not authentication."
    ),
    "s7": (
        "Public Key Infrastructure — PKI — is the system that creates, distributes, manages, and revokes digital certificates. "
        "A digital certificate binds a public key to an identity. It is signed by a Certificate Authority. "
        "The Certificate Authority — CA — is the trusted third party that issues and signs certificates. "
        "The Registration Authority — RA — handles identity verification before the CA issues a certificate. "
        "The CA signs. The RA verifies the identity first. "
        "When a certificate must be invalidated before its expiry date, it is placed on the "
        "Certificate Revocation List — CRL. "
        "OCSP — Online Certificate Status Protocol — provides real-time certificate status checking "
        "without requiring the full CRL download. "
        "Digital signatures use asymmetric cryptography to provide three security properties: "
        "authentication, integrity, and non-repudiation. "
        "To sign: the sender hashes the message, then encrypts the hash with their private key. "
        "To verify: the receiver decrypts with the sender's public key and recomputes the hash. If they match, "
        "the message is authentic and unmodified. "
        "Critical exam point: digital signatures do not provide confidentiality. "
        "They prove who sent the message and that it was not altered. They do not hide the content. "
        "Key management covers the full key lifecycle: "
        "generation, distribution, storage, rotation, suspension, revocation, and destruction. "
        "Key escrow stores a copy of the encryption key with a trusted third party for authorized recovery. "
        "Exam tip: key escrow is a policy and governance decision, not a cryptographic weakness."
    ),
    "s8": (
        "Cryptanalytic attacks target the algorithm, the key, or the implementation. "
        "Know the attack types by name and be able to match them to a scenario description. "
        "Brute force: systematically trying every possible key. "
        "Key length determines resistance — a 256-bit key has two to the 256 possible values. "
        "Known-plaintext attack: the attacker has pairs of plaintext and corresponding ciphertext "
        "and uses these to analyze the key. "
        "Chosen-plaintext attack: the attacker selects specific plaintexts and observes the resulting ciphertext. "
        "More powerful than known-plaintext because the attacker controls the input. "
        "Birthday attack: exploits the birthday paradox to find two different inputs that produce the same hash — a collision. "
        "For an n-bit hash, collisions can be found with approximately two to the n divided by two operations. "
        "SHA-1 is vulnerable to birthday attacks. SHA-256 is not currently practical to attack this way. "
        "Rainbow table attack: uses precomputed chains of hash values to reverse hash functions quickly. "
        "Defeated by salting — adding a random value to each input before hashing, "
        "making precomputation of the tables impractical. "
        "Side-channel attacks exploit information leaked by the physical implementation, not the algorithm. "
        "Timing attacks measure how long cryptographic operations take. "
        "Power analysis measures power consumption during operations. "
        "The algorithm itself is correct — the implementation leaks information. "
        "Meet-in-the-middle: encrypts from the plaintext end and decrypts from the ciphertext end, meeting in the middle. "
        "This is why double-DES offers only marginally more security than single DES."
    ),
    "s9": (
        "Physical security is the foundational layer. If an attacker gains physical access, all logical controls fail. "
        "The exam tests physical security across site selection, perimeter controls, and interior controls. "
        "Site selection: evaluate crime rates, proximity to emergency services, natural disaster risk, "
        "utility reliability, and transportation access. "
        "Avoid flood zones, flight paths, and areas with unreliable power or water supply. "
        "Perimeter controls create the outer barrier. "
        "Fencing defines the boundary. Bollards prevent vehicle-based attacks. "
        "Lighting reduces concealment. CCTV deters and records. "
        "Building entry controls: mantraps — also called access control vestibules — use two-door systems. "
        "The first door must close before the second opens. One person at a time. "
        "Mantraps prevent tailgating — unauthorized personnel following authorized personnel through a secured door. "
        "Data center controls: raised floors protect against water damage and enable cable management. "
        "HVAC systems maintain temperature and humidity within equipment tolerances. "
        "Fire suppression in data centers must not damage equipment. "
        "Halon has been phased out due to environmental impact. "
        "Clean agents — FM-200, CO2, and inert gas systems — suppress fire without leaving residue. "
        "Water-based sprinkler systems are generally not used in data centers. "
        "Physical access must be logged and the logs reviewed regularly for anomalies."
    ),
    "s10": (
        "Question one. "
        "A military information system enforces the following rules: "
        "users may read documents at or below their clearance level, "
        "but may only write to documents at or above their clearance level. "
        "Which security model is implemented? "
        "Answer: Bell-LaPadula. "
        "The simple security property — no read up — and the star property — no write down — define Bell-LaPadula. "
        "Biba is the opposite: no read down, no write up. "
        "Bell-LaPadula protects confidentiality. Biba protects integrity. "
        "Question two. "
        "A TLS handshake uses RSA to exchange a session key, "
        "then switches to AES for the duration of the data transfer. "
        "What cryptographic approach does this represent? "
        "Answer: hybrid encryption. "
        "RSA — asymmetric — solves the key distribution problem. "
        "AES — symmetric — provides efficient bulk encryption. "
        "Using asymmetric to exchange a symmetric key, then switching to symmetric for data, is hybrid encryption. "
        "This is how TLS works. "
        "Question three. "
        "A security administrator discovers that a legacy password database "
        "stores passwords as unsalted MD5 hashes. "
        "An attacker with access to the database could use a precomputed table "
        "to recover most passwords quickly. "
        "What attack is being described? "
        "Answer: rainbow table attack. "
        "Rainbow tables are precomputed chains of hash values that enable fast password recovery. "
        "They are defeated by salting — adding a random per-user value before hashing. "
        "Unsalted MD5 is particularly vulnerable because MD5 is fast to compute "
        "and rainbow tables for it are widely available."
    ),
    "s11": (
        "Four flashcards before you go. "
        "One: Bell-LaPadula — no read up, no write down — confidentiality. "
        "Biba — no read down, no write up — integrity. Opposites. "
        "Two: hybrid encryption — asymmetric exchanges the key, symmetric encrypts the data. "
        "TLS does this. "
        "Three: Common Criteria EAL four is the highest level routinely achievable for commercial products. "
        "EAL seven requires formal mathematical proofs. "
        "Four: digital signatures provide authentication, integrity, and non-repudiation — not confidentiality. "
        "Sign with private key. Verify with public key. "
        "That is Domain 3. "
        "Next episode: Domain 4 — Communication and Network Security. "
        "OSI model, TCP/IP, network attacks, firewalls, VPNs, and secure protocols. "
        "Test yourself right now at zerodaylabs.tech — adaptive practice exams built for CISSP. "
        "And if you want the senior security mindset that decides borderline questions, "
        "Think Like A CISSP is in the description. "
        "Subscribe and we will see you in Domain 4."
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
    "s10": 72.0,
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
    print(f"Voice:  {ELEVEN_VOICE_ID}")
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
            print(f"     Fix: python generate_cissp_d3_narration.py --force --only {keys}")
        if failed_scenes:
            keys = " ".join(failed_scenes)
            print(f"\n  ✗  GENERATION FAILED for: {keys}")
            print(f"     Fix: python generate_cissp_d3_narration.py --force --only {keys}")
        print("\n  Resolve the above before running manim.\n")
        raise SystemExit(1)
    else:
        print("\n✓ All scenes generated with ElevenLabs — safe to render.")
