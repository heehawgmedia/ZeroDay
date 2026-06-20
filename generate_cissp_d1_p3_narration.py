"""
Generate narration audio for the CISSP Domain 1 Part 3 explainer video.

Engine selection (automatic):
  1. ElevenLabs  — if ELEVEN_API_KEY is set (in .env or environment).
  2. SVOX Pico   — offline fallback (pico2wave), works anywhere.

Outputs:
  cissp_d1_p3_audio/s0.mp3 ... cissp_d1_p3_audio/s11.mp3
  cissp_d1_p3_audio/durations.json

Usage:
  python generate_cissp_d1_p3_narration.py              # skip existing valid files
  python generate_cissp_d1_p3_narration.py --force      # regenerate everything
  python generate_cissp_d1_p3_narration.py --only s2 s3 # specific scenes
"""
import json
import os
import re
import subprocess
import argparse

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(BASE_DIR, "cissp_d1_p3_audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(BASE_DIR, ".env"))
except ImportError:
    pass

ELEVEN_API_KEY  = os.environ.get("ELEVEN_API_KEY") or os.environ.get("ELEVENLABS_API_KEY")
ELEVEN_VOICE_ID = os.environ.get("CISSP_D1P3_VOICE_ID", "TABZn6CDfjMNGrsnGzzD")
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
        "The data center floods. Every server — gone. "
        "How long can your business operate without it? "
        "Two hours? Two days? At what point does the damage become unrecoverable? "
        "Those are not hypothetical questions. They are the inputs to your Business Continuity Plan. "
        "And the CISSP tests whether you know how to answer them with precision — "
        "not with intuition, not with optimism, but with documented, tested, board-approved numbers. "
        "This is D1 Part 3 of the CISSP Domain Mastery Series, mapping to objectives 1.7 and 1.8. "
        "Today: business continuity versus disaster recovery, "
        "the Business Impact Analysis and the recovery metrics that drive every continuity decision, "
        "recovery site strategies, DR plan testing types, "
        "personnel security across the full employment lifecycle, "
        "and security awareness training. "
        "Every item in this episode is exam-tested."
    ),
    "s2": (
        "Business Continuity and Disaster Recovery are related — but they are not the same thing. "
        "The exam tests both, and it tests whether you can distinguish them in a scenario. "
        "Business Continuity Planning — BCP — is the broader discipline. "
        "Its scope is the entire organization. "
        "BCP asks: how does the organization continue operating during a disruption? "
        "BCP addresses people, processes, facilities, communications, and technology. "
        "Disaster Recovery Planning — DRP — is a subset of BCP. "
        "Its scope is IT systems and data. "
        "DRP asks: how do we restore technology services after a disruption? "
        "The relationship: BCP keeps the business running. DRP restores the systems that support it. "
        "You cannot have effective BCP without DRP. "
        "But DRP alone does not constitute a continuity plan. "
        "The BCP is a living document — it must be reviewed, updated, and tested regularly. "
        "Senior management sponsors and approves it. "
        "The security and continuity teams develop and maintain it."
    ),
    "s3": (
        "The Business Impact Analysis is the foundation of every continuity decision. "
        "It identifies critical business functions, the systems that support them, "
        "and the consequences of disruption over time. "
        "The BIA answers: what would happen if this function went down — "
        "in one hour, one day, one week? "
        "The output of the BIA drives three things: recovery prioritization, "
        "recovery time targets, and recovery point targets. "
        "From the BIA, you derive the Maximum Tolerable Downtime — MTD. "
        "MTD is the longest period a business function can be offline before the damage "
        "becomes unacceptable or unrecoverable. "
        "If the MTD for payroll processing is seventy-two hours, "
        "then everything else — your recovery targets, your site strategy, your backup intervals — "
        "must be designed to restore payroll within seventy-two hours. "
        "MTD sets the outer boundary. All other recovery metrics must fall within it. "
        "The BIA should be conducted before any recovery strategies are selected. "
        "You identify the impact first. Then you design the solution."
    ),
    "s4": (
        "Four recovery metrics. Know exact definitions and the relationship between them. "
        "Recovery Time Objective — RTO — is the maximum acceptable time to restore "
        "a system or function after a disruption. "
        "RTO must be less than MTD. Always. "
        "If MTD is seventy-two hours, RTO must be under seventy-two hours — "
        "with margin to spare. "
        "Recovery Point Objective — RPO — is the maximum acceptable amount of data loss "
        "measured in time. "
        "An RPO of four hours means you can tolerate losing up to four hours of data. "
        "This drives your backup frequency — if RPO is four hours, you back up at least every four hours. "
        "Mean Time to Repair — MTTR — is the average time required to restore a failed component. "
        "It is a historical metric — derived from past incidents or manufacturer data. "
        "Mean Time Between Failures — MTBF — is the average time a system operates "
        "between failures. Higher MTBF means more reliable. "
        "Exam tip: RPO governs backup frequency. RTO governs recovery speed. MTD is the outer limit. "
        "RTO must always be less than MTD. "
        "These four appear together in scenario questions — know which one a given constraint maps to."
    ),
    "s5": (
        "Once you have your recovery targets, you select a recovery site strategy. "
        "The exam tests three primary site types. "
        "A hot site is a fully operational duplicate of your primary facility. "
        "Hardware, software, data — all current and ready. "
        "Failover can occur in minutes to hours. "
        "Most expensive. Used for the most critical systems with the tightest RTOs. "
        "A warm site has hardware and infrastructure in place, "
        "but systems are not fully configured and data is not current. "
        "Recovery takes hours to days. "
        "Moderate cost. The most common choice for organizations balancing cost and recovery speed. "
        "A cold site is a facility with power, cooling, and connectivity — nothing else. "
        "You bring your own hardware, load your own software, restore from backups. "
        "Recovery takes days to weeks. "
        "Cheapest. Appropriate only when MTD is very long. "
        "Two additional options: a reciprocal agreement is a contract between two organizations "
        "to host each other's operations in a disaster — low cost, but resources may not be available "
        "when you need them. "
        "A mobile site is a self-contained portable facility that can be deployed to a location. "
        "The exam may also reference redundant sites — a fully mirrored environment "
        "with real-time data synchronization. "
        "Faster than a hot site, but the most expensive option available."
    ),
    "s6": (
        "A disaster recovery plan that has never been tested is not a plan — it is a document. "
        "The CISSP tests five DR testing types, in order of increasing disruption and cost. "
        "Read-through — also called checklist review. "
        "Each team member reads the plan and verifies their understanding of their role. "
        "No systems involved. Lowest disruption. "
        "Structured walkthrough — also called tabletop exercise. "
        "Team members walk through the plan step by step in a meeting room, "
        "discussing their actions for a given scenario. No systems involved. "
        "Simulation — a scenario is announced and teams practice their responses "
        "without actually switching to the recovery site. "
        "Tests communication and decision-making without production impact. "
        "Parallel test — recovery systems are brought online at the alternate site "
        "while the primary site continues operating. Both run simultaneously. "
        "Validates that recovery systems actually work without any production risk. "
        "Full interruption — primary systems are shut down and operations fully transfer "
        "to the recovery site. "
        "Most disruptive and most realistic. Highest risk. Rarely performed. "
        "Memory hook: Read, Walk, Simulate, Parallel, Full. "
        "Each level increases realism and risk. The exam will describe a test scenario "
        "and ask which type was used."
    ),
    "s7": (
        "Personnel security begins before an employee starts. "
        "The exam tests the full lifecycle: hiring, employment, and termination. "
        "Pre-employment controls. "
        "Background checks: verify identity, criminal history, employment history, and education. "
        "Reference checks: validate character and past performance. "
        "Employment agreements: NDA signed before access is granted. "
        "Least privilege from day one: new employees receive only the access "
        "required for their specific role — nothing more. "
        "Separation of duties is established at the access provisioning stage, "
        "not after a problem occurs. "
        "Separation of duties ensures no single person can complete a sensitive transaction alone. "
        "It is a preventive control designed to reduce fraud and error. "
        "Job rotation: periodically moving employees between roles. "
        "It reduces the risk of fraud, builds cross-training, and surfaces irregularities "
        "that a person in a fixed role might conceal. "
        "Mandatory vacation: requiring employees to take uninterrupted leave. "
        "During their absence, another employee performs the role — and may detect fraud "
        "that was being actively concealed. "
        "Both job rotation and mandatory vacation are detective controls."
    ),
    "s8": (
        "Termination security is one of the highest-risk events in the personnel lifecycle. "
        "Voluntary resignations are lower risk than involuntary terminations — "
        "but the security procedures are identical. "
        "Access revocation must happen immediately. "
        "Before the employee is notified of termination if the situation is adversarial. "
        "Simultaneous with the notification in standard cases. "
        "Never after the employee leaves the building — at that point it is already too late. "
        "The termination checklist includes: "
        "revoke all logical access — accounts, VPN, email, cloud services. "
        "Recover all physical assets — badges, laptops, mobile devices, tokens, keys. "
        "Conduct an exit interview. "
        "Remind the individual of their NDA obligations and confidentiality requirements. "
        "The exam may present a scenario where access was not revoked immediately "
        "and ask what control failed. "
        "The answer is the termination procedure — specifically the access revocation step. "
        "For privileged accounts, revocation is critical. "
        "A terminated system administrator who retains credentials is an existential risk."
    ),
    "s9": (
        "Security awareness training is objective 1.7 — and it is tested more heavily than most candidates expect. "
        "There are three levels. Know the distinction. "
        "Awareness is the foundation. "
        "It changes behavior by helping people recognize security risks in their day-to-day work. "
        "Phishing simulations, posters, brief reminders. "
        "The goal is recognition — not technical skill. "
        "Training is role-based and skill-focused. "
        "It teaches people how to perform security-relevant tasks correctly. "
        "Security training for developers includes secure coding. "
        "Security training for HR includes how to handle sensitive data. "
        "The audience varies by role. "
        "Education is deeper — it builds conceptual understanding and is aimed at "
        "security professionals and candidates for security roles. "
        "CISSP preparation is security education. "
        "All three apply across the organization, but at different levels. "
        "Everyone gets awareness. Role-holders get training. Security professionals get education. "
        "Exam tip: the exam may describe a program and ask which level it represents. "
        "Awareness changes behavior. Training builds skills. Education builds understanding."
    ),
    "s10": (
        "Question one. "
        "An organization determines that its payroll system can be offline for a maximum of forty-eight hours "
        "before regulatory penalties become unavoidable. "
        "The recovery team must restore payroll within thirty-six hours of a failure. "
        "Backups run every six hours. "
        "Identify the MTD, RTO, and RPO for this system. "
        "Answer: MTD is forty-eight hours — the outer limit of acceptable downtime. "
        "RTO is thirty-six hours — the target recovery time, which falls within the MTD. "
        "RPO is six hours — the maximum data loss, set by backup frequency. "
        "Question two. "
        "During a DR test, the recovery team brings the alternate site fully online "
        "while the primary site continues operating normally. "
        "Both environments run simultaneously for four hours before the team shuts down the recovery site. "
        "Which DR test type was performed? "
        "Answer: parallel test. Both sites run simultaneously — production is never interrupted. "
        "Question three. "
        "A recently terminated network administrator's access credentials were not revoked "
        "until three days after termination. "
        "The former employee accessed internal systems during that window. "
        "Which personnel security control failed? "
        "Answer: immediate access revocation at termination. "
        "The termination procedure required same-day revocation of all logical access. "
        "The delay created the window for unauthorized access."
    ),
    "s11": (
        "Four flashcards before you go. "
        "One: MTD is the outer limit. RTO must be less than MTD. RPO drives backup frequency. "
        "Two: hot site is minutes to hours. Warm is hours to days. Cold is days to weeks. "
        "Three: DR testing in order — Read, Walk, Simulate, Parallel, Full interruption. "
        "Four: termination — revoke access immediately, recover assets, remind of NDA. "
        "That wraps Domain 1. "
        "Next episode: Domain 2 Part 1 — Asset Security. "
        "Data classification, ownership, retention, and the controls that protect information throughout its lifecycle. "
        "Test yourself right now at zerodaylabs.tech — adaptive practice exams built for CISSP. "
        "And if you want the managerial mindset that decides borderline questions, "
        "Think Like A CISSP is in the description. "
        "Subscribe and we will see you in Domain 2."
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


# Speech-rate estimate: ElevenLabs voices typically speak 3.0-4.0 wps.
# Using 3.0 (conservative) so the guard only fires when audio is genuinely
# short — not just because the voice speaks fast.
WORDS_PER_SEC    = 3.0
CHUNK_CHAR_LIMIT = 700   # split long scenes into smaller TTS requests


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


def generate_elevenlabs(key: str, text: str) -> str:
    """Chunked TTS with per-chunk and final truncation guards.

    Each scene is split into <=CHUNK_CHAR_LIMIT char chunks, synthesized
    separately, duration-checked, then concatenated. This eliminates the
    single-request truncation that produced scenes whose audio dropped out
    part way through.
    """
    from elevenlabs.client import ElevenLabs
    client = ElevenLabs(api_key=ELEVEN_API_KEY)
    mp3    = os.path.join(AUDIO_DIR, f"{key}.mp3")
    chunks = _chunk_text(text)
    parts  = []
    # Clean up any leftover temp files from a previous interrupted run.
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
            print(f"     Fix: python generate_cissp_d1_p3_narration.py --force --only {keys}")
        if failed_scenes:
            keys = " ".join(failed_scenes)
            print(f"\n  ✗  GENERATION FAILED for: {keys}")
            print(f"     Fix: python generate_cissp_d1_p3_narration.py --force --only {keys}")
        print("\n  Resolve the above before running manim.\n")
        raise SystemExit(1)
    else:
        print("\n✓ All scenes generated with ElevenLabs — safe to render.")
