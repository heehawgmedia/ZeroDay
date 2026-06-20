"""
Generate narration audio for the CISSP Domain 1 Part 2 explainer video.

Engine selection (automatic):
  1. ElevenLabs  — if ELEVEN_API_KEY is set (in .env or environment).
  2. SVOX Pico   — offline fallback (pico2wave), works anywhere.

Outputs:
  cissp_d1_p2_audio/s0.mp3 ... cissp_d1_p2_audio/s11.mp3
  cissp_d1_p2_audio/durations.json

Usage:
  python generate_cissp_d1_p2_narration.py              # skip existing valid files
  python generate_cissp_d1_p2_narration.py --force      # regenerate everything
  python generate_cissp_d1_p2_narration.py --only s2 s3 # specific scenes
"""
import json
import os
import re
import subprocess
import argparse

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(BASE_DIR, "cissp_d1_p2_audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(BASE_DIR, ".env"))
except ImportError:
    pass

ELEVEN_API_KEY  = os.environ.get("ELEVEN_API_KEY") or os.environ.get("ELEVENLABS_API_KEY")
ELEVEN_VOICE_ID = os.environ.get("CISSP_D1P2_VOICE_ID", "TABZn6CDfjMNGrsnGzzD")
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
        "A system is breached. Forty thousand customer records are exfiltrated. "
        "The board asks: what was our expected annual loss from this type of event? "
        "The CISO has no answer — because no one ever ran the numbers. "
        "That is not a technical failure. That is a risk management failure. "
        "And that scenario is exactly what the CISSP exam tests. "
        "This is D1 Part 2 of the CISSP Domain Mastery Series, mapping to exam objective 1.4. "
        "Today: the risk vocabulary the exam demands, "
        "quantitative risk formulas with a worked example, "
        "qualitative versus quantitative assessment, "
        "risk response strategies, "
        "threat modeling with STRIDE, PASTA, and attack trees, "
        "and the NIST Risk Management Framework. "
        "Everything here is exam-tested. Nothing is background."
    ),
    "s2": (
        "Risk management starts with vocabulary. "
        "The exam will use these terms precisely — you need to match that precision. "
        "An asset is anything of value the organization must protect. "
        "Hardware, data, intellectual property, reputation — all assets. "
        "A threat is any potential event that could cause harm to an asset. "
        "A threat agent — sometimes called a threat actor — is the entity that carries out the threat. "
        "An external attacker, a malicious insider, a natural disaster. "
        "A vulnerability is a weakness in a system, process, or control that a threat can exploit. "
        "Risk is the probability that a threat will exploit a vulnerability and cause harm. "
        "Risk equals threat times vulnerability — conceptually. "
        "Exposure is the condition of being susceptible to loss. "
        "A system with an unpatched vulnerability is exposed. "
        "Impact is the magnitude of harm if a risk is realized. "
        "And residual risk is the risk that remains after controls are applied. "
        "You cannot eliminate all risk. You manage it to an acceptable level. "
        "That acceptable level is determined by the organization's risk appetite — "
        "set by senior management, not by the security team."
    ),
    "s3": (
        "The quantitative formulas are non-negotiable on the CISSP. "
        "Memorize them. Know how to apply them in a scenario. "
        "Asset Value — abbreviated AV — is the dollar value of the asset being protected. "
        "Exposure Factor — EF — is the percentage of asset value lost if a threat is realized. "
        "A threat that destroys half the asset has an exposure factor of fifty percent, or zero point five. "
        "Single Loss Expectancy — SLE — is the expected loss from one occurrence of the threat. "
        "SLE equals Asset Value multiplied by Exposure Factor. "
        "If an asset is worth one hundred thousand dollars and the exposure factor is forty percent, "
        "the SLE is forty thousand dollars. "
        "Annualized Rate of Occurrence — ARO — is how many times per year the threat is expected to occur. "
        "A threat expected once every two years has an ARO of zero point five. "
        "Annualized Loss Expectancy — ALE — is the expected loss per year from that threat. "
        "ALE equals SLE multiplied by ARO. "
        "If SLE is forty thousand and ARO is zero point five, ALE is twenty thousand dollars per year. "
        "Safeguard value: if a control costs fifteen thousand dollars per year and reduces ALE from twenty thousand to three thousand, "
        "the net benefit is two thousand dollars per year. That control is financially justified. "
        "The exam will give you numbers and ask you to calculate. "
        "ALE before minus ALE after minus annual cost of safeguard equals the value of the safeguard."
    ),
    "s4": (
        "There are three risk assessment approaches. "
        "Qualitative assessment uses subjective scales — high, medium, low. "
        "No dollar figures. Faster to perform and easier to communicate to non-technical stakeholders. "
        "The Delphi method is a structured qualitative technique that collects anonymous expert opinions "
        "through multiple rounds until consensus is reached. "
        "Quantitative assessment assigns numeric values — dollar amounts, probabilities, frequencies. "
        "It produces ALE, which allows direct comparison to safeguard cost. "
        "More rigorous, but requires reliable data and more time to perform. "
        "Semi-quantitative assessment combines both: qualitative labels mapped to numeric ranges. "
        "The exam may describe a scenario and ask which approach was used. "
        "Key discriminator: if the output includes dollar figures, it is quantitative. "
        "If it uses categories like high, medium, or low without dollar values, it is qualitative. "
        "Most organizations use a risk matrix — probability on one axis, impact on the other. "
        "The result of any risk assessment feeds the risk treatment decision."
    ),
    "s5": (
        "Once you know the risk, you have four response options. "
        "Some candidates remember them with the acronym TARA. "
        "Transfer: shift the financial impact to a third party. "
        "Purchasing cyber insurance transfers risk. "
        "Outsourcing to a vendor transfers some operational risk — "
        "but never the legal or regulatory accountability. "
        "The organization always retains liability for its own data. "
        "Avoid: eliminate the activity that creates the risk. "
        "If a feature creates unacceptable risk, do not build it. "
        "This is not always practical — some risk is inherent to doing business. "
        "Reduce — also called mitigate: implement controls that lower likelihood or impact. "
        "Patching, encryption, access controls — these all reduce risk. "
        "Accept: acknowledge the risk and choose not to act on it. "
        "This is a deliberate management decision, not inaction. "
        "Risk acceptance must be documented and signed off by the appropriate authority. "
        "Senior management accepts risk. Security professionals advise. "
        "After applying any response, residual risk remains. "
        "If the residual risk exceeds the organization's risk tolerance, additional controls are required."
    ),
    "s6": (
        "Threat modeling is the process of identifying threats to a system before they can be exploited. "
        "STRIDE is the Microsoft model and the one the CISSP tests most directly. "
        "Each letter maps to a threat category and the security property it violates. "
        "Spoofing — violates authentication. Pretending to be someone you are not. "
        "A fake login page. A spoofed email sender. "
        "Tampering — violates integrity. Unauthorized modification of data. "
        "Altering a log file. Injecting malicious data into a stream. "
        "Repudiation — violates nonrepudiation. Denying that an action was performed. "
        "This is why audit logs and digital signatures exist. "
        "Information Disclosure — violates confidentiality. Exposing data to unauthorized parties. "
        "Denial of Service — violates availability. Preventing legitimate users from accessing the system. "
        "Elevation of Privilege — violates authorization. Gaining access or capabilities beyond what is authorized. "
        "A regular user escalating to admin. A guest account reading sensitive files. "
        "STRIDE is used to evaluate each component of a system and ask: "
        "what could go wrong here, and which threat category does it fall into?"
    ),
    "s7": (
        "Beyond STRIDE, the exam may reference two other models. "
        "PASTA stands for Process for Attack Simulation and Threat Analysis. "
        "It is a seven-stage, risk-centric methodology. "
        "PASTA aligns threat modeling to business objectives and produces attack simulations. "
        "It is used when you need to connect technical threats to business impact. "
        "Attack trees are a structured, hierarchical representation of how an attacker could achieve a goal. "
        "The root node is the attacker's objective. "
        "Child nodes represent the steps or preconditions required to reach that objective. "
        "Attack trees help analysts enumerate paths to compromise and prioritize defenses. "
        "DREAD was an older Microsoft scoring model: "
        "Damage potential, Reproducibility, Exploitability, Affected users, Discoverability. "
        "It has largely been deprecated, but older exam questions may reference it. "
        "Know that it produces a numeric risk score for each threat. "
        "The exam may describe a scenario and ask which modeling approach is being used. "
        "STRIDE identifies what can go wrong. PASTA models how it happens in a business context. "
        "Attack trees show the path to exploitation."
    ),
    "s8": (
        "The NIST Risk Management Framework defines seven steps for integrating risk management "
        "into system development and operations. "
        "Step one: Prepare. Establish the context, priorities, and resources before starting. "
        "Step two: Categorize. Classify the information system and its data based on impact. "
        "FIPS 199 and NIST 800-60 guide this step. "
        "Step three: Select. Choose appropriate security controls from NIST 800-53. "
        "Step four: Implement. Deploy and configure the selected controls. "
        "Step five: Assess. Evaluate whether controls are implemented correctly and producing the intended outcome. "
        "Step six: Authorize. A senior official — the Authorizing Official — formally accepts residual risk. "
        "This is a management decision, not a technical one. "
        "Step seven: Monitor. Continuously track control effectiveness, changes, and new threats. "
        "The exam may ask about the order of steps or which step a scenario falls into. "
        "Categorize comes before Select. Assess comes before Authorize. Monitor is ongoing. "
        "ISO 31000 is an international risk management standard providing principles and guidelines. "
        "FAIR — Factor Analysis of Information Risk — is a quantitative framework for measuring "
        "and managing information risk in financial terms. "
        "It is increasingly referenced in enterprise risk management contexts."
    ),
    "s9": (
        "Supply chain risk is a growing exam topic. "
        "Third-party vendors, cloud providers, software developers, and hardware manufacturers "
        "all introduce risk into your organization's security posture. "
        "The exam tests three key supply chain controls. "
        "Vendor assessment and due diligence: evaluate the security posture of third parties "
        "before engaging them. Review SOC 2 reports, penetration test results, and certifications. "
        "Right-to-audit clauses: contractual provisions that allow your organization "
        "to audit the vendor's security controls. "
        "If a vendor refuses a right-to-audit clause, that is a risk indicator. "
        "Service Level Agreements: define the security and operational commitments the vendor must meet. "
        "SLAs create accountability. "
        "Remember: outsourcing an activity transfers some risk, but never regulatory accountability. "
        "If a vendor breaches your customer data, your organization still answers to the regulator."
    ),
    "s10": (
        "Question one. "
        "A server worth two hundred thousand dollars is at risk of ransomware. "
        "Analysis shows a forty percent exposure factor and an expected occurrence of twice per year. "
        "What is the annualized loss expectancy? "
        "Answer: SLE equals two hundred thousand times zero point four, which is eighty thousand. "
        "ALE equals eighty thousand times two, which is one hundred sixty thousand dollars per year. "
        "Question two. "
        "An organization's risk assessment identifies high-likelihood, high-impact risks in a matrix "
        "using categories of critical, high, medium, and low. No dollar values are produced. "
        "This is an example of which type of risk assessment? "
        "Answer: qualitative. Categories without dollar figures define qualitative assessment. "
        "Question three. "
        "A threat modeling session identifies a risk where an attacker could gain administrator access "
        "by exploiting a privilege escalation vulnerability in a web application. "
        "Using STRIDE, which threat category does this represent? "
        "Answer: Elevation of Privilege. "
        "The attacker is gaining capabilities beyond what is authorized. "
        "Elevation of Privilege maps to the authorization property in STRIDE."
    ),
    "s11": (
        "Four flashcards before you go. "
        "One: ALE equals SLE times ARO. SLE equals Asset Value times Exposure Factor. "
        "Two: risk responses — Transfer, Avoid, Reduce, Accept. "
        "Management accepts risk. Security professionals advise. "
        "Three: STRIDE — Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, "
        "Elevation of Privilege. "
        "Four: NIST RMF — Prepare, Categorize, Select, Implement, Assess, Authorize, Monitor. "
        "Assess before Authorize. Monitor is continuous. "
        "That is Domain 1 Part 2. "
        "Next episode: D1-P3 — Business Continuity Planning, Disaster Recovery, "
        "and personnel security policies. "
        "Test yourself right now at zerodaylabs.tech — adaptive practice exams built for CISSP. "
        "And if you want the managerial mindset that decides borderline questions, "
        "Think Like A CISSP is in the description. "
        "Subscribe and we will see you in Part 3."
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


WORDS_PER_SEC    = 3.0
CHUNK_CHAR_LIMIT = 700


def _split_sentences(text: str) -> list:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p]


def _chunk_text(text: str, limit: int = CHUNK_CHAR_LIMIT) -> list:
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


def generate_elevenlabs(key: str, text: str) -> str:
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
            _tts_one(client, ch, part)
            got, exp = duration_of(part), _expected_seconds(ch)
            if got < 0.35 * exp:
                raise RuntimeError(
                    f"chunk {i+1}/{len(chunks)} truncated — "
                    f"{got:.1f}s audio for ~{exp:.1f}s of text"
                )
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
        if total < 0.40 * exp_total:
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
            print(f"     Fix: python generate_cissp_d1_p2_narration.py --force --only {keys}")
        if failed_scenes:
            keys = " ".join(failed_scenes)
            print(f"\n  ✗  GENERATION FAILED for: {keys}")
            print(f"     Fix: python generate_cissp_d1_p2_narration.py --force --only {keys}")
        print("\n  Resolve the above before running manim.\n")
        raise SystemExit(1)
    else:
        print("\n✓ All scenes generated with ElevenLabs — safe to render.")
