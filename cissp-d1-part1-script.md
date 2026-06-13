# CISSP Domain Mastery Series — D1 Part 1
## Security Concepts, Governance & Ethics

---

### METADATA

| Field | Value |
|---|---|
| Episode | D1-P1 |
| Series | CISSP Domain Mastery |
| Runtime target | 10:00 |
| Narration word count | ~1,500 |
| Exam objectives | 1.1, 1.2, 1.3, 1.5 (April 2024 outline) |
| Target keywords | CISSP domain 1, security governance, due care due diligence, ISC2 code of ethics, CIA triad, security frameworks |

---

## SCRIPT

---

### [0:00–0:25] HOOK

**NARRATION:**
An organization suffers a major breach. The CISO had flagged the vulnerability in last quarter's risk assessment. The board had approved the security budget. Controls were documented in policy. And then — nothing. Nobody acted on the findings. When the regulator investigates, the question is not whether you identified the risk. The question is: did you do something about it? That gap — between knowing and doing — is the difference between due diligence and due care. It is one of the most-tested concepts on the CISSP. We are starting there.

**VISUAL:**
- Black screen → single line appears: *"You identified the risk. Did you act on it?"*
- No title card yet — cold open

---

### [0:25–0:50] ROADMAP

**NARRATION:**
This is D1 Part 1 of the CISSP Domain Mastery Series — Domain 1, Security and Risk Management. We are mapping to exam outline objectives 1.1, 1.2, 1.3, and 1.5. Today: the ISC2 Code of Professional Ethics, the five security pillars, security governance and business alignment, organizational roles and responsibilities, due care versus due diligence, the major control frameworks, and a compliance overview. Every item in this episode is exam-tested. Nothing here is background reading.

**VISUAL:**
- Series title card: "CISSP Domain Mastery Series — D1 Part 1"
- Objectives listed on screen: 1.1 / 1.2 / 1.3 / 1.5
- Topic list populates line by line

---

### [0:50–2:10] BLOCK 1 — ISC2 Code of Professional Ethics

**NARRATION:**
The ISC2 Code of Professional Ethics has two parts: a preamble and four canons. The canons are what the exam tests, and their ORDER is fair game. Most candidates know the content. They lose points because they forget the sequence.

Canon one: protect society, the common good, necessary public trust and confidence, and the infrastructure. Society comes first — not your employer, not your client. Society.

Canon two: act honorably, honestly, justly, responsibly, and legally. This canon governs your professional conduct.

Canon three: provide diligent and competent service to principals. A principal is any party you serve — your employer, a client. Competent means you are actually qualified to perform the service.

Canon four: advance and protect the profession. This comes last. If canon one and canon four conflict — if protecting the profession requires you to hide something harmful to society — society wins. Always.

Memory hook: Society, Honor, Service, Profession. Some candidates remember it as: *Security Has Strong Principles.*

Your organization may also maintain its own code of ethics. If an organizational code conflicts with the ISC2 code, the ISC2 code governs. You cannot contract out of your professional obligations.

**VISUAL:**
- Four canons numbered and highlighted in sequence as narrated
- ⚠ EXAM TIP badge: "Order is tested — Society → Honor → Service → Profession"
- Mnemonic displayed: "SHSP — Security Has Strong Principles"

---

### [2:10–3:30] BLOCK 2 — The Five Pillars of Information Security

**NARRATION:**
You know the CIA Triad. The CISSP adds two more pillars: authenticity and nonrepudiation. That gives you five. You need exact definitions and the ability to identify which pillar a scenario violates.

Confidentiality: only authorized entities can access the information. A misconfigured S3 bucket exposing customer records violates confidentiality.

Integrity: data is accurate, complete, and has not been modified without authorization. An attacker altering a transaction in transit violates integrity. Hash functions and checksums protect it.

Availability: authorized users can access systems and data when they need them. A denial-of-service attack or a ransomware encryption violates availability.

Authenticity: the identity of an entity — a user, a message, a system — is genuine and verifiable. A spoofed email pretending to come from your CFO violates authenticity. Digital certificates establish it.

Nonrepudiation: a party cannot deny having performed an action. If you digitally sign a document, you cannot later claim you did not sign it. Nonrepudiation typically requires digital signatures combined with audit logs and timestamps.

**EXAM TIP:** Authenticity and nonrepudiation are the two pillars candidates most often confuse. Authenticity answers: *is this entity who they claim to be?* Nonrepudiation answers: *can they deny this action later?* They are related — but distinct.

**VISUAL:**
- Five pillars displayed as a table: Pillar | Definition | Example Violation | Common Control
- ⚠ EXAM TIP badge: "Authenticity = identity is genuine / Nonrepudiation = action cannot be denied"

---

### [3:30–4:40] BLOCK 3 — Security Governance

**NARRATION:**
Security governance is the set of policies, processes, and accountability structures that align the security function to organizational strategy, business goals, mission, and objectives.

Here is the framing the exam demands: think like a CEO, not an engineer. A CEO does not ask how a firewall rule is configured. They ask: does our security posture support our business objectives? Does it protect shareholder value? Does it manage risk to an acceptable level? Governance answers those questions.

Security must function as a business enabler — not a cost center, not a blocker. The security program exists to allow the business to operate safely, not to prevent it from operating.

Governance structures include the board of directors, audit committees, and risk committees. These bodies set the organization's risk appetite — the level of risk the organization is willing to accept in pursuit of its objectives — and they hold leadership accountable for security outcomes. These are oversight bodies, not operational bodies. The board does not configure firewalls. The board asks whether the right controls exist and whether management is accountable for them.

**VISUAL:**
- Governance pyramid: Board → Executive Leadership → CISO/Security Team → Operations
- Label: "Risk Appetite set at top — Security Operations at bottom"
- Lower-third: "Governance = alignment + oversight + accountability"

---

### [4:40–5:15] BLOCK 4 — Organizational Processes

**NARRATION:**
Acquisitions and divestitures appear on the exam from a governance and due diligence perspective.

In an acquisition, security's job is to evaluate the target's security posture, policies, compliance obligations, and data handling practices before the deal closes. You need to understand what risks the organization is inheriting. You do not discover a legacy HIPAA liability after signing.

In a divestiture, the security concerns are data classification, access revocation, and sanitization of systems being transferred or retired. Who controls what data after the split?

Governance committees — audit committees, risk committees, information security steering committees — provide the oversight layer between the board and operational security. They review risk, validate controls, and ensure accountability. They do not run operations.

**VISUAL:**
- Two-column comparison: Acquisition (what to review) vs. Divestiture (what to resolve)
- Governance committee hierarchy diagram

---

### [5:15–6:10] BLOCK 5 — Roles and Responsibilities

**NARRATION:**
This is non-negotiable: senior management owns risk. Not the CISO. Not the security team. Not the auditor. When a question asks who is ultimately responsible or accountable for information security, the answer is senior management.

Security professionals advise. We assess risks, design controls, implement safeguards, and monitor outcomes. We provide the inputs that management uses to make decisions. We do not own the risk. Management does — and management cannot delegate that ownership.

Two additional roles the exam tests consistently.

The data owner is a business role — typically a manager or department head — responsible for classifying data and determining who should be authorized to access it. The data owner sets the rules.

The data custodian is a technical role — typically IT or operations — responsible for implementing and maintaining the controls that protect the data on behalf of the owner. The data custodian follows the rules.

If a question blends those two roles in a wrong answer choice, it is a trap. The owner decides. The custodian implements.

**VISUAL:**
- Role table: Role | Function | Accountability
- ⚠ EXAM TIP badge: "Who is ULTIMATELY responsible? → Senior Management. Every time."

---

### [6:10–7:15] BLOCK 6 — Due Care vs. Due Diligence

**NARRATION:**
Back to the hook. Due diligence and due care are distinct. The exam will present both in answer choices and require you to select the correct one for a given scenario.

Due diligence is the research and discovery phase. It means investigating, evaluating, and understanding risks, requirements, and obligations before making a decision. Reviewing a vendor's SOC 2 report before signing a contract is due diligence. Reading the risk assessment findings is due diligence. The knowing.

Due care is the action phase. It means doing what a reasonable and prudent professional would do given what they know. Implementing the recommended controls after the risk assessment is due care. Patching the known vulnerability is due care. The doing.

Diligence before. Care after. You cannot exercise due care without first exercising due diligence. But — and this is critical — knowing without acting is negligence. That is exactly what happened in the opening scenario.

The legal standard the exam applies is the reasonable and prudent person test: what would a competent professional in the same role, with the same knowledge, have done? Courts use this. Regulators use this. ISC2 uses this.

Memory hook: **Diligence = Discovery. Care = Conduct.**

**VISUAL:**
- Two-column table: Due Diligence | Due Care
  - Research vs. Action
  - Before decision vs. After decision
  - "Knowing" vs. "Doing"
  - Example for each
- ⚠ EXAM TIP badge: "Knowing without acting = negligence"
- Mnemonic: "Diligence = Discovery / Care = Conduct"

---

### [7:15–8:10] BLOCK 7 — Security Control Frameworks

**NARRATION:**
The exam tests awareness of the major frameworks — not deep technical content. Know what each one is designed to do and when an organization would adopt it.

ISO/IEC 27001 is an international standard for establishing an Information Security Management System — an ISMS. Its primary purpose is independent certification. Organizations pursue it to demonstrate security posture to customers and regulators.

NIST Cybersecurity Framework is a voluntary, risk-based framework for critical infrastructure. Its core functions are Govern, Identify, Protect, Detect, Respond, and Recover. Widely adopted even outside its original scope.

COBIT — Control Objectives for Information and Related Technology — is an IT governance framework. Its purpose is aligning IT management to business goals. It sits at the governance layer, not the operational layer.

SABSA — Sherwood Applied Business Security Architecture — is an enterprise security architecture framework that derives security requirements directly from business objectives. Architecture-first thinking.

PCI DSS — Payment Card Industry Data Security Standard — applies to any organization that stores, processes, or transmits payment card data. This is mandatory and contractually enforced by the card brands.

FedRAMP is the US federal government's cloud authorization program. Any cloud service provider selling to federal agencies must hold FedRAMP authorization. Mandatory for that market.

**VISUAL:**
- Framework comparison table: Name | Purpose | Scope | Mandatory?
- ISO 27001 | ISMS Certification | Global | Voluntary (market-driven)
- NIST CSF | Risk-based posture | Critical infra | Voluntary (federal EO-influenced)
- COBIT | IT Governance | Enterprise IT | Voluntary
- SABSA | Security Architecture | Enterprise | Voluntary
- PCI DSS | Payment card security | Card environments | Mandatory
- FedRAMP | Cloud authorization | US federal | Mandatory for federal

---

### [8:10–8:30] BLOCK 8 — Compliance Overview

**NARRATION:**
Compliance obligations come from three distinct sources. Know the categories.

Contractual requirements come from agreements — vendor contracts, SLAs, client agreements. Failure to meet them is a breach of contract, with financial and legal consequences.

Legal requirements come from legislation — HIPAA, GDPR, CCPA. These are not optional and vary by jurisdiction and data type.

Regulatory requirements come from sector-specific oversight bodies — the SEC, FINRA, CISA. Noncompliance can mean fines, sanctions, or loss of operating license.

The exam will ask you to categorize a given obligation. Know which bucket each falls into.

**VISUAL:**
- Three-column table: Contractual | Legal | Regulatory
- Example for each: SLA | HIPAA | SEC rules

---

### [8:30–9:20] RAPID-FIRE REVIEW — 3 Practice Questions

**NARRATION:**

Question one. A security team is reviewing a prospective cloud vendor's SOC 2 Type II report, penetration test results, and prior incident disclosures before recommending approval to the CIO. This activity BEST represents which concept? Answer: due diligence. The team is researching the vendor's security posture before a decision is made. Due care would follow — implementing contractual security requirements after signing.

Question two. A CISO documented a critical vulnerability and recommended remediation with a budget estimate six months ago. Senior leadership declined to fund the remediation. A breach exploiting that vulnerability occurs. Who bears ultimate accountability? Answer: senior management. They own the risk. The CISO fulfilled the advisory role. Management chose not to act — that is a failure of due care at the leadership level.

Question three. A security professional is directed by their employer to deny knowledge of a security incident to a regulatory authority. According to the ISC2 Code of Ethics, the professional should do what? Answer: refuse and report if required by law. Canon one — protect society and the public trust — supersedes the employer directive. No organizational code of ethics overrides ISC2's.

**VISUAL:**
- Each question displayed as a formatted exam question
- Correct answer revealed with one-line rationale
- Wrong answer callout for each (common distractor)

---

### [9:20–10:00] RECAP + CTA

**NARRATION:**
Four items for your flashcard. One: four canons in order — Society, Honor, Service, Profession. Two: five pillars — confidentiality, integrity, availability, authenticity, nonrepudiation. Three: senior management owns risk, security professionals advise. Four: due diligence is discovery, due care is conduct — knowing without acting is negligence.

That is the foundation of Domain 1. Next episode: Domain 1 Part 2 — risk management concepts, threat modeling, and quantitative risk calculations including ALE, SLE, and ARO. If you want to test yourself on today's material right now, head to zerodaylabs.tech — adaptive practice exams that surface your gaps before the exam does. And if you want the managerial mindset that decides borderline CISSP questions, pick up Think Like A CISSP — link in the description. See you in Part 2.

**VISUAL:**
- Flashcard graphic: four bullet points, one at a time
- ZDL CTA with URL and book cover
- End screen: subscribe button, next episode card

---

## YOUTUBE PACKAGE

### Title Options

1. `CISSP Domain 1 Part 1 — Ethics, Governance & Security Foundations | Exam Prep 2024`
2. `CISSP D1: Due Care vs Due Diligence, Code of Ethics & Frameworks EXPLAINED`
3. `CISSP Security Concepts You MUST Know | Domain 1 Part 1 Full Lesson`

---

### Description

**CISSP Domain Mastery Series — D1 Part 1: Security Concepts, Governance & Ethics**

Maps to ISC2 CISSP exam outline objectives 1.1, 1.2, 1.3, 1.5 (April 2024).

In this episode you will learn:
- The ISC2 Code of Professional Ethics — 4 canons in exact exam order
- The five security pillars (CIA + authenticity + nonrepudiation) with precise definitions
- Security governance: why security is a business enabler, not a cost center
- Organizational roles: who OWNS risk vs. who advises on risk
- Due care vs. due diligence — the exam's most-tested governance distinction
- Control frameworks: ISO 27001, NIST CSF, COBIT, SABSA, PCI DSS, FedRAMP — what each is FOR
- Compliance obligations: contractual, legal, and regulatory categories

**CHAPTERS**
00:00 Hook — the gap between knowing and acting
00:25 Roadmap — objectives covered
00:50 ISC2 Code of Professional Ethics
02:10 Five Pillars of Security
03:30 Security Governance
04:40 Organizational Processes
05:15 Roles and Responsibilities
06:10 Due Care vs. Due Diligence
07:15 Security Control Frameworks
08:10 Compliance Overview
08:30 Practice Questions
09:20 Recap + Next Episode

🎯 **Adaptive CISSP practice exams → https://zerodaylabs.tech**
📘 **Think Like A CISSP (strategy guide) → https://zerodaylabs.tech/store/think-like-a-cissp**

*Zero Day Labs — Train. Test. Certify.*

---

### Tags

```
CISSP domain 1, CISSP exam prep 2024, CISSP study guide, ISC2 CISSP, due care due diligence, 
code of professional ethics ISC2, CIA triad CISSP, security governance CISSP, 
CISSP security frameworks, ISO 27001, NIST cybersecurity framework, 
COBIT security, PCI DSS, FedRAMP, CISSP roles responsibilities, 
data owner data custodian, nonrepudiation authenticity, CISSP domain mastery
```

---

### Pinned Comment Draft

> **Study notes for this episode:**
> - **Canon order (exam-tested):** Society → Honor → Service → Profession
> - **5 Pillars:** Confidentiality, Integrity, Availability, Authenticity, Nonrepudiation
> - **Risk ownership:** Senior Management owns it. Security professionals advise.
> - **Due Diligence = Discovery (before) / Due Care = Conduct (after)**
> - **Frameworks quick ref:** ISO 27001 = ISMS certification | NIST CSF = risk posture | COBIT = IT governance | SABSA = architecture | PCI DSS = payment cards (mandatory) | FedRAMP = fed cloud (mandatory)
>
> Practice questions for this topic → https://zerodaylabs.tech
