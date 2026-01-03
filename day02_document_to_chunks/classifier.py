# day02_document-classifier/classifier.py
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Tuple


# -------------------------
# 1) Labels (taxonomy v1)
# -------------------------
LABELS = [
    "EMPLOYEE_HANDBOOK",
    "POLICY_PROCEDURE",
    "CONTRACT_AGREEMENT",
    "TECHNICAL_DOC",
    "FAQ_QA",
    "MEETING_NOTES",
    "MARKETING_SALES",
    "LEGAL_COMPLIANCE",
    "UNKNOWN",
]


@dataclass
class Classification:
    label: str
    confidence: float
    scores: Dict[str, float]
    reasons: Dict[str, List[str]]  # label -> reasons (matched rules)


# -------------------------
# 2) Text preprocessing
# -------------------------
def normalize(text: str) -> str:
    # Keep it simple: normalize whitespace and lowercase.
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def safe_lower(text: str) -> str:
    return text.lower()


# -------------------------
# 3) Feature rules (robust-ish heuristics)
# -------------------------
def score_employee_handbook(raw: str) -> Tuple[float, List[str]]:
    reasons = []
    s = 0.0
    t = safe_lower(raw)

    patterns = [
        (r"\bemployee handbook\b", 5.0, "contains 'employee handbook'"),
        (r"\bwelcome\b.*\bon board\b", 2.0, "welcome/on board phrasing"),
        (r"\bcode of conduct\b", 2.0, "mentions code of conduct"),
        (r"\bworkplace\b|\bharassment\b|\banti[- ]discrimination\b", 2.0, "workplace/HR policy terms"),
        (r"\bpto\b|\bpaid time off\b|\bvaca(tion|tions)\b|\bleave\b", 1.5, "leave/PTO terms"),
        (r"\bbenefits?\b|\bhealth insurance\b|\b401k\b", 1.5, "benefits terms"),
        (r"\bdisciplinary\b|\btermination\b", 1.2, "discipline/termination"),

        # Company intro sections (keep moderate)
        (r"\bmission statement\b", 1.0, "mission statement section"),
        (r"\bour mission is to\b", 0.7, "mission phrasing"),
        (r"\bcompany overview\b", 0.7, "company overview section"),
        (r"\bvision\b|\bcore values\b|\bvalues\b|\bculture\b", 0.6, "vision/values/culture language"),
    ]

    for pat, w, why in patterns:
        if re.search(pat, t, re.S):
            s += w
            reasons.append(f"+{w}: {why}")

    # ---- structure signals (use raw) ----
    has_roman = bool(re.search(r"(?m)^\s*[IVXLCDM]+\.\s+[\w\s]{3,}", raw))
    has_letter = bool(re.search(r"(?m)^\s*[A-Z]\.\s+[\w\s]{3,}", raw))

    if has_roman:
        s += 1.5
        reasons.append("+1.5: roman numeral section headings (I., II., etc.)")

    if has_letter:
        s += 1.0
        reasons.append("+1.0: lettered subsection headings (A., B., etc.)")

    # ---- KEY FIX: handbook-context bonus gated by outline ----
    has_company_intro = bool(re.search(
        r"\b(mission statement|our mission is to|company overview|vision|core values|values|culture)\b",
        t
    ))

    if (has_roman or has_letter) and has_company_intro:
        s += 1.2
        reasons.append("+1.2: outline + company-intro section ⇒ handbook context")

    return s, reasons

def score_policy_procedure(t: str) -> Tuple[float, List[str]]:
    reasons = []
    s = 0.0
    patterns = [
        (r"\bpolicy\b", 2.0, "mentions policy"),
        (r"\bprocedure\b", 2.0, "mentions procedure"),
        (r"\bscope\b", 1.5, "has scope"),
        (r"\bpurpose\b", 1.2, "has purpose"),
        (r"\bresponsibilit(y|ies)\b", 1.2, "has responsibilities"),
        (r"\bdefinitions?\b", 1.2, "has definitions"),
        (r"\bcompliance\b|\bshall\b|\bmust\b", 1.0, "normative language"),
        (r"\brevision history\b|\beffective date\b", 2.0, "revision/effective date style"),
    ]
    for pat, w, why in patterns:
        if re.search(pat, t, re.I):
            s += w
            reasons.append(f"+{w}: {why}")
    return s, reasons


def score_contract_agreement(t: str) -> Tuple[float, List[str]]:
    reasons = []
    s = 0.0
    patterns = [
        (r"\bthis (agreement|contract)\b", 3.0, "agreement/contract opener"),
        (r"\bparty\b|\bparties\b", 2.0, "mentions parties"),
        (r"\bwhereas\b", 3.0, "WHEREAS clause"),
        (r"\bindemnif(y|ication)\b", 3.0, "indemnification"),
        (r"\bgoverning law\b|\bjurisdiction\b|\bvenue\b", 2.5, "governing law/jurisdiction"),
        (r"\bconfidential(ity)?\b|\bnon[- ]disclosure\b|\bnda\b", 2.5, "confidentiality/NDA"),
        (r"\bterm\b|\btermination\b", 1.5, "term/termination"),
        (r"\bliability\b|\blimitation of liability\b", 2.5, "liability clauses"),
        (r"\bforce majeure\b", 2.0, "force majeure"),
        (r"\bsignature\b|\bin witness whereof\b", 2.5, "signature block language"),
    ]
    for pat, w, why in patterns:
        if re.search(pat, t, re.I):
            s += w
            reasons.append(f"+{w}: {why}")
    return s, reasons


def score_technical_doc(t: str) -> Tuple[float, List[str]]:
    reasons = []
    s = 0.0
    patterns = [
        (r"\bapi\b|\bendpoints?\b|\bauth\b|\boauth\b", 2.5, "API/auth language"),
        (r"\binstall\b|\bsetup\b|\bconfiguration\b", 1.8, "setup/config language"),
        (r"\berror\b|\bexception\b|\btraceback\b", 2.0, "errors/exceptions"),
        (r"\bjson\b|\byaml\b|\btoml\b|\bcli\b", 1.8, "config/CLI formats"),
        (r"`[^`]+`", 1.5, "inline code formatting"),
        (r"```", 2.0, "code blocks"),
        (r"\bhttp(s)?://\S+", 1.0, "URLs"),
    ]
    for pat, w, why in patterns:
        if re.search(pat, t, re.I):
            s += w
            reasons.append(f"+{w}: {why}")
    return s, reasons


def score_faq_qa(t: str) -> Tuple[float, List[str]]:
    reasons = []
    s = 0.0

    # Many Q:/A: pairs is a strong signal
    q_count = len(re.findall(r"^\s*q\s*[:\-]\s+", t, re.I | re.M))
    a_count = len(re.findall(r"^\s*a\s*[:\-]\s+", t, re.I | re.M))
    if q_count + a_count >= 3:
        s += 5.0
        reasons.append(f"+5.0: multiple Q:/A: lines (q={q_count}, a={a_count})")

    # "Frequently Asked Questions"
    if re.search(r"\bfrequently asked questions\b|\bfaq\b", t, re.I):
        s += 3.0
        reasons.append("+3.0: mentions FAQ")

    return s, reasons


def score_meeting_notes(t: str) -> Tuple[float, List[str]]:
    reasons = []
    s = 0.0
    patterns = [
        (r"\battendees?\b|\bparticipants?\b", 2.0, "attendees/participants"),
        (r"\bagenda\b", 2.0, "agenda"),
        (r"\baction items?\b|\bai:\b", 2.5, "action items"),
        (r"\bdecisions?\b", 1.5, "decisions"),
        (r"\bnext steps\b", 1.5, "next steps"),
        (r"\bminutes\b", 1.5, "meeting minutes"),
        (r"\bdate:\b|\btime:\b", 1.0, "date/time fields"),
    ]
    for pat, w, why in patterns:
        if re.search(pat, t, re.I):
            s += w
            reasons.append(f"+{w}: {why}")
    return s, reasons


def score_marketing_sales(t: str) -> Tuple[float, List[str]]:
    reasons = []
    s = 0.0
    patterns = [
        (r"\bcall to action\b|\bsign up\b|\bget started\b", 2.5, "CTA language"),
        (r"\bpricing\b|\bfree trial\b|\bdemo\b", 2.5, "pricing/trial/demo"),
        (r"\bbenefits?\b|\bfeatures?\b", 1.5, "features/benefits"),
        (r"\bvalue proposition\b|\bcase study\b", 2.0, "marketing terms"),
        (r"\btestimonial\b|\bcustomer\b", 1.0, "customer/testimonial"),
    ]
    for pat, w, why in patterns:
        if re.search(pat, t, re.I):
            s += w
            reasons.append(f"+{w}: {why}")
    return s, reasons


def score_legal_compliance(t: str) -> Tuple[float, List[str]]:
    reasons = []
    s = 0.0
    patterns = [
        (r"\bcompliance\b|\bregulation\b|\bregulatory\b", 2.0, "compliance/regulatory"),
        (r"\banti[- ]corruption\b|\banti[- ]bribery\b|\bsanctions\b", 2.5, "anti-corruption/sanctions"),
        (r"\bprivacy\b|\bgdpr\b|\bhipaa\b", 2.5, "privacy/GDPR/HIPAA"),
        (r"\bcode of (business )?conduct\b", 2.0, "code of conduct"),
        (r"\bwhistleblower\b|\bintegrity line\b", 2.0, "whistleblower reporting"),
        (r"\bshall\b|\bmust\b|\bprohibited\b", 1.0, "normative legal language"),
    ]
    for pat, w, why in patterns:
        if re.search(pat, t, re.I):
            s += w
            reasons.append(f"+{w}: {why}")
    return s, reasons


# -------------------------
# 4) Classifier (scores -> label)
# -------------------------
SCORERS = {
    "EMPLOYEE_HANDBOOK": score_employee_handbook,
    "POLICY_PROCEDURE": score_policy_procedure,
    "CONTRACT_AGREEMENT": score_contract_agreement,
    "TECHNICAL_DOC": score_technical_doc,
    "FAQ_QA": score_faq_qa,
    "MEETING_NOTES": score_meeting_notes,
    "MARKETING_SALES": score_marketing_sales,
    "LEGAL_COMPLIANCE": score_legal_compliance,
}


def classify(text: str) -> Classification:
    raw = normalize(text)
    t = safe_lower(raw)

    scores: Dict[str, float] = {}
    reasons_map: Dict[str, List[str]] = {}

    for label, fn in SCORERS.items():
        s, reasons = fn(raw)  # use raw to preserve case/format patterns too
        scores[label] = s
        reasons_map[label] = reasons

    # Pick best label by score
    best_label = max(scores, key=scores.get)
    best_score = scores[best_label]

    # If everything is weak, call it UNKNOWN
    if best_score < 3.0:
        return Classification(
            label="UNKNOWN",
            confidence=0.0,
            scores=scores,
            reasons=reasons_map,
        )

    # Confidence: normalize against total positive evidence
    total = sum(max(0.0, v) for v in scores.values())
    confidence = 0.0 if total == 0 else best_score / total

    return Classification(
        label=best_label,
        confidence=round(confidence, 3),
        scores={k: round(v, 2) for k, v in sorted(scores.items(), key=lambda x: -x[1])},
        reasons=reasons_map,
    )


