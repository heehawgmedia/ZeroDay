"""
Generate narration audio for the CISSP Domain 2 explainer video.

Engine selection (automatic):
  1. ElevenLabs  — if ELEVEN_API_KEY is set (in .env or environment).
  2. SVOX Pico   — offline fallback (pico2wave), works anywhere.

Outputs:
  cissp_d2_audio/s0.mp3 ... cissp_d2_audio/s11.mp3
  cissp_d2_audio/durations.json

Usage:
  python generate_cissp_d2_narration.py              # skip existing valid files
  python generate_cissp_d2_narration.py --force      # regenerate everything
  python generate_cissp_d2_narration.py --only s2 s3 # specific scenes
"""
import json
import os
import re
import subprocess
import argparse

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(BASE_DIR, "cissp_d2_audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(BASE_DIR, ".env"))
except ImportError:
    pass

ELEVEN_API_KEY  = os.environ.get("ELEVEN_API_KEY") or os.environ.get("ELEVENLABS_API_KEY")
ELEVEN_VOICE_ID = os.environ.get("CISSP_D2_VOICE_ID", "TABZn6CDfjMNGrsnGzzD")
ELEVEN_MODEL    = os.environ.get("ELEVEN_MODEL", "eleven_multilingual_v2")

NARRATIONS = {
    "s0": (
        "A misconfigured S3 bucket. Customer records — publicly accessible for six months. "
        "The security team's post-mortem finds three failures. "
        "The data was never classified, so nobody knew how sensitive it was or how to protect it. "
        "It was never labeled, so nobody knew what it contained. "
        "And no retention policy existed, so nobody knew it should have been deleted two years ago. "
        "Domain 2 teaches you how to prevent all three. "
        "This is Domain 2 of the CISSP Domain Mastery Series — Asset Security. "
        "We map to objectives 2.1 through 2.6. "
        "Today: data classification, ownership roles, handling requirements, "
        "the data lifecycle, retention and end-of-life, sanitization methods, "
        "data security controls, and scoping and tailoring. "
        "Every concept in this video is exam-tested."
    ),
    "s1": (
        "Data classification is the foundation of asset security. "
        "You cannot protect what you have not categorized. "
        "There are two classification systems the exam tests. "
        "The government or military system has four levels. "
        "Top Secret: unauthorized disclosure could cause exceptionally grave damage to national security. "
        "Secret: serious damage. "
        "Confidential: damage. "
        "Unclassified: no expected damage from disclosure. "
        "The commercial system also has four common levels. "
        "Confidential — also called Proprietary: highest sensitivity. "
        "Trade secrets, strategic plans, unreleased financials. "
        "Private: sensitive personal information. HR records, medical data. "
        "Sensitive: requires care but less restriction than private. "
        "Public: intended for general release. "
        "Two principles that apply to both systems. "
        "First: the data owner determines the classification — not IT, not security. "
        "The owner is the business role accountable for the data. "
        "Second: data should be classified at its highest sensitivity level. "
        "If a document contains one top secret element, the entire document is top secret. "
        "Classification is not permanent. Data can be reclassified or declassified "
        "as its value or sensitivity changes over time."
    ),
    "s2": (
        "Data ownership is one of the most frequently tested role distinctions in Domain 2. "
        "The exam will present a scenario and ask which role is responsible for a given action. "
        "The data owner is a business role — typically a manager, director, or executive. "
        "The owner is accountable for the data and is responsible for classifying it, "
        "approving access requests, and ensuring appropriate controls are applied. "
        "The CFO owns financial data. The CHRO owns HR records. "
        "The data custodian is a technical role — IT or operations. "
        "The custodian implements and maintains the controls the owner specifies. "
        "They back it up, encrypt it, patch the systems that store it. "
        "Owner decides. Custodian implements. This distinction is non-negotiable on the exam. "
        "The data steward manages data quality and ensures data governance policies are followed. "
        "The steward ensures the data is accurate, consistent, and compliant with standards. "
        "This role appears more frequently in enterprise data governance contexts. "
        "Under GDPR — which the CISSP now references — two additional roles matter. "
        "The data controller determines the purposes and means of processing personal data. "
        "The data processor processes personal data on behalf of the controller. "
        "If your organization uses a cloud provider to process customer data, "
        "your organization is the controller and the provider is the processor."
    ),
    "s3": (
        "Once data is classified, it must be handled according to its classification level. "
        "Handling requirements cover four areas. "
        "Labeling: human-readable identification of the classification on documents, files, and media. "
        "Every asset should be labeled so anyone who encounters it knows immediately how to handle it. "
        "Unmarked data is often treated as public by default — which is a significant risk. "
        "Marking: physical or digital indicators applied to assets. "
        "Digital files may have classification metadata embedded. "
        "Physical documents have headers and footers. Storage media has visible labels. "
        "Storage requirements: higher classification requires stricter physical and logical controls. "
        "Top secret data may require separate air-gapped systems, locked facilities, "
        "and two-person integrity for access. "
        "Public data may have minimal storage restrictions. "
        "Transmission requirements: data in transit must be protected commensurate with its classification. "
        "Confidential data requires encryption over any public or untrusted network. "
        "The need-to-know principle governs access: "
        "even individuals with the appropriate clearance level may not access data "
        "unless they have a specific need to know it for their role. "
        "Clearance is necessary but not sufficient. Need-to-know is also required."
    ),
    "s4": (
        "All data passes through a lifecycle. Security controls must be applied at every stage. "
        "The exam tests whether you can identify which controls apply at which phase. "
        "Create or Collect: classification is assigned at the point of creation. "
        "This is when the data owner's role is most critical. "
        "Store: data at rest must be protected with appropriate access controls, "
        "encryption, and backup procedures based on its classification. "
        "Use or Process: data being actively used must be monitored. "
        "Data loss prevention tools and logging apply here. "
        "Share or Distribute: need-to-know governs who receives data. "
        "Transmission controls — encryption, secure channels — apply. "
        "Data shared with third parties creates controller-processor relationships. "
        "Archive: data that is no longer actively used but must be retained. "
        "Retention schedules and legal hold processes apply. "
        "Archived data must remain protected — classification does not change with archival. "
        "Destroy or Dispose: data that has reached the end of its retention period "
        "must be sanitized in a manner appropriate to its classification. "
        "The method of destruction must be documented. "
        "Key exam point: classification must be maintained throughout the entire lifecycle. "
        "Data does not become less sensitive simply because it is old or archived."
    ),
    "s5": (
        "Retention policies define how long data must be kept before it can be destroyed. "
        "They are driven by legal requirements, regulatory mandates, and business needs. "
        "The exam tests the distinction between minimum and maximum retention. "
        "Some regulations require you to keep data for a minimum period. "
        "Others require you to delete it after a maximum period — GDPR's data minimization principle. "
        "A legal hold — also called a litigation hold — overrides the normal retention schedule. "
        "When litigation is anticipated, all potentially relevant data must be preserved "
        "regardless of its scheduled destruction date. "
        "Destroying data under a legal hold is spoliation — destruction of evidence. "
        "The legal and financial consequences are severe. "
        "Hardware and software also have lifecycles. "
        "End of Life — EOL — is when a vendor stops selling or actively developing a product. "
        "End of Support — EOS — is when a vendor stops providing patches, updates, and technical support. "
        "EOS is the critical security threshold. "
        "A system past end of support will not receive security patches. "
        "Any new vulnerabilities discovered after EOS are permanently unmitigated "
        "unless the system is replaced or custom support is contracted. "
        "Running EOS systems in production is an accepted risk that must be documented."
    ),
    "s6": (
        "When data must be destroyed, the destruction method must match the classification level. "
        "The concept underlying all sanitization decisions is data remanence — "
        "the residual representation of data that remains after deletion attempts. "
        "Deleting a file does not delete the data. It deletes the pointer to the data. "
        "The actual data remains on the media until it is overwritten. "
        "Three sanitization methods, in increasing order of thoroughness. "
        "Clearing: overwriting the media with non-sensitive data. "
        "Suitable for media that will be reused within the same organization "
        "at the same or lower classification level. "
        "Not sufficient for media leaving the organization. "
        "Purging: more thorough removal. Includes degaussing — exposing magnetic media "
        "to a powerful magnetic field to randomize its contents — or cryptographic erasure, "
        "where the encryption key is destroyed. "
        "Suitable for media being released outside the organization. "
        "Destruction: physical destruction of the media itself. "
        "Shredding, incineration, pulverizing, disintegration. "
        "Provides the highest assurance of data elimination. "
        "Required for the highest classification levels. "
        "Exam tip: match the method to the scenario. "
        "Reuse within the org — clearing. Leaving the org — purging. "
        "Highly classified, must ensure no recovery — destruction."
    ),
    "s7": (
        "Data security controls protect information from unauthorized access, "
        "disclosure, modification, and destruction. "
        "The exam tests four primary technical controls in Domain 2. "
        "Encryption: protects data confidentiality at rest and in transit. "
        "Classification level determines encryption requirements. "
        "Confidential data traversing a public network requires encryption. "
        "Full disk encryption protects data at rest on devices. "
        "Data Loss Prevention — DLP: monitors data in use, in motion, and at rest "
        "for policy violations and prevents unauthorized exfiltration. "
        "DLP can block email attachments containing classified data, "
        "prevent uploads to unauthorized cloud services, or alert on USB transfers. "
        "Digital Rights Management — DRM — also called Information Rights Management or IRM: "
        "controls what recipients can do with data after they receive it. "
        "Prevents unauthorized copying, forwarding, printing, or screen capture. "
        "DLP controls whether data leaves. DRM controls what happens to it after it does. "
        "Tokenization: replaces sensitive data with a non-sensitive substitute — the token — "
        "that has no exploitable value. Used extensively in payment card processing. "
        "The actual data is stored in a secure token vault. "
        "Data masking: obscures real data with fictitious but realistic data "
        "for use in non-production environments. Developers test against masked data, "
        "never against production records."
    ),
    "s8": (
        "The final Domain 2 concept is scoping and tailoring — how organizations "
        "customize standard control sets to fit their specific environment. "
        "A baseline is the minimum set of security controls required for a given "
        "classification level or system type. "
        "NIST 800-53 provides control baselines organized by impact level: low, moderate, and high. "
        "An organization starts with the appropriate baseline and then customizes it. "
        "Scoping is the process of identifying which baseline controls apply "
        "to a particular system or environment and removing those that do not. "
        "If a control addresses physical media but the system is fully cloud-based, "
        "physical media controls may be scoped out. "
        "Tailoring is the process of modifying the remaining controls to fit the organization's "
        "specific mission, environment, and risk tolerance. "
        "A control may be tailored to implement additional parameters or constraints. "
        "Compensating controls are alternative controls used when a required control "
        "cannot be implemented as specified. "
        "They must provide equivalent protection to the original control. "
        "They must be documented and approved by the appropriate authority. "
        "A compensating control does not remove the requirement — "
        "it satisfies the requirement through an alternative means."
    ),
    "s9": (
        "Question one. "
        "An organization's legal team notifies IT that litigation is anticipated involving "
        "customer transaction records. The records are scheduled for deletion next week "
        "under the standard retention policy. What should IT do? "
        "Answer: issue a legal hold immediately. "
        "The scheduled deletion must be suspended. "
        "Destroying data under a legal hold is spoliation — destruction of evidence — "
        "with severe legal consequences. "
        "Question two. "
        "A database administrator is directed to prepare a storage array for transfer "
        "to a third-party vendor. The array contains confidential customer data. "
        "Which sanitization method is appropriate? "
        "Answer: purging. "
        "Media leaving the organization requires purging — degaussing or cryptographic erasure. "
        "Clearing is only appropriate for reuse within the same organization. "
        "Destruction would prevent the hardware transfer. "
        "Question three. "
        "A security tool prevents users from forwarding internal documents marked Confidential "
        "as email attachments, regardless of recipient. "
        "What type of control is this? "
        "Answer: DLP — Data Loss Prevention. "
        "DLP prevents unauthorized exfiltration of data in motion. "
        "DRM would control what the recipient could do with the document after receiving it. "
        "These two are commonly confused on the exam."
    ),
    "s10": (
        "Four flashcards. "
        "One: data owner classifies data and approves access. "
        "Custodian implements controls. Controller determines processing purpose. Processor processes on behalf. "
        "Two: government levels — Top Secret, Secret, Confidential, Unclassified. "
        "Commercial — Confidential slash Proprietary, Private, Sensitive, Public. "
        "Three: sanitization — clearing for internal reuse, purging for media leaving the org, "
        "destruction for highest classification. "
        "Four: DLP prevents data from leaving. DRM controls what happens after it leaves. "
        "That is Domain 2. "
        "Next episode: Domain 3 — Security Architecture and Engineering. "
        "Security models, cryptography, and secure design principles. "
        "Test yourself right now at zerodaylabs.tech. "
        "Adaptive practice exams that surface your gaps before the real exam does. "
        "Subscribe and we will see you in Domain 3."
    ),
    "s11": (
        "Before you go — if this series is building your CISSP foundation, "
        "Think Like A CISSP will take you the rest of the way. "
        "It teaches the senior security mindset that decides the borderline questions — "
        "the ones that separate candidates who pass from experienced engineers who fail. "
        "Twenty five dollars at Zero Day Labs dot tech. "
        "Link is in the description."
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
            print(f"     Fix: python generate_cissp_d2_narration.py --force --only {keys}")
        if failed_scenes:
            keys = " ".join(failed_scenes)
            print(f"\n  ✗  GENERATION FAILED for: {keys}")
            print(f"     Fix: python generate_cissp_d2_narration.py --force --only {keys}")
        print("\n  Resolve the above before running manim.\n")
        raise SystemExit(1)
    else:
        print("\n✓ All scenes generated with ElevenLabs — safe to render.")
