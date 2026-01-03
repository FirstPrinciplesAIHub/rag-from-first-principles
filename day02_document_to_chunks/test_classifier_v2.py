"""Day 2 - Document Classifier Test Harness

Why you were seeing FAIL:
Your classifier returns canonical labels like:
  EMPLOYEE_HANDBOOK, POLICY_PROCEDURE, CONTRACT_AGREEMENT, TECHNICAL_DOC, FAQ_QA

But your EXPECTED values were short aliases like:
  HANDBOOK, POLICY, CONTRACT, TECH_DOC, FAQ

This harness lets you keep the short aliases and maps them to canonical labels
before comparing.
"""

from __future__ import annotations
from typing import Dict

# Change this import if your classifier module name/path is different.
from classifier import classify


SAMPLES: Dict[str, str] = {
    "handbook": """
Barber Shop Employee Handbook

I. Introduction

A. Welcome Message
Welcome to [Your Company]! We are delighted to have you on board...

B. Purpose of the Handbook
This handbook explains workplace expectations, PTO, benefits, and conduct.

C. Equal Employment Opportunity
We do not tolerate discrimination or harassment in the workplace.

D. Time Off
PTO, sick leave, and holidays are described in this section.
""",
    "policy": """
Policy: Data Retention
Purpose: Define how long records must be retained.
Scope: All employees and contractors.
Responsibilities: Engineering, Security, HR.
Effective Date: 2025-01-01
Revision History: v1.2
""",
    "contract": """
THIS AGREEMENT is made between the Parties as of the Effective Date.
WHEREAS, the Parties desire to enter into this Agreement...

Governing Law: State of New York.
Limitation of Liability...

IN WITNESS WHEREOF, the Parties have executed this Agreement.

Signature:
""",
    "techdoc": """
## API Authentication
Use OAuth2.

Example:
```bash
curl -H "Authorization: Bearer <token>" https://api.example.com/v1/users
```

### Errors
- 401 Unauthorized
- 403 Forbidden
""",
    "faq": """
FAQ

Q: How do I reset my password?
A: Click "Forgot password" on the login page.

Q: Where can I download invoices?
A: Go to Billing -> Invoices.
""",
    "unknown_noise": """
lorem ipsum blargh snorfle wibble wobble
(not enough structure to confidently classify)
""",
}

EXPECTED: Dict[str, str] = {
    "handbook": "HANDBOOK",
    "policy": "POLICY",
    "contract": "CONTRACT",
    "techdoc": "TECH_DOC",
    "faq": "FAQ",
    "unknown_noise": "UNKNOWN",
}

ALIAS_TO_CANONICAL = {
    "HANDBOOK": "EMPLOYEE_HANDBOOK",
    "POLICY": "POLICY_PROCEDURE",
    "CONTRACT": "CONTRACT_AGREEMENT",
    "TECH_DOC": "TECHNICAL_DOC",
    "FAQ": "FAQ_QA",
    "UNKNOWN": "UNKNOWN",
}


def canonicalize(label: str) -> str:
    label = (label or "").strip().upper()
    return ALIAS_TO_CANONICAL.get(label, label)


def run() -> int:
    failures = 0

    for name, text in SAMPLES.items():
        expected_alias = EXPECTED.get(name, "UNKNOWN")
        expected = canonicalize(expected_alias)

        result = classify(text)
        predicted = result.label

        print("=" * 80)
        print(f"CASE: {name}")
        print(f"EXPECTED : {expected_alias} (canonical: {expected})")
        print(f"PREDICTED: {predicted}")
        print(f"CONFIDENCE: {result.confidence}\n")

        print("Scores:")
        for k, v in result.scores.items():
            print(f"  {k:18}: {v}")

        print("\nReasons:")
        for lbl, reasons in result.reasons.items():
            if not reasons:
                continue
            print(f"  [{lbl}]")
            for r in reasons:
                print(f"    - {r}")

        if predicted == expected:
            print("\nRESULT: PASS")
        else:
            print("\nRESULT: FAIL")
            failures += 1

    print("=" * 80)
    print("Failures:", failures)
    return failures


if __name__ == "__main__":
    raise SystemExit(run())
