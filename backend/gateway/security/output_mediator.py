"""
Output mediator — scans LLM response text before it reaches the user.

Catches:
  - PII leakage (emails, phone numbers, SSNs, credit cards)
  - Credential leakage (API keys, tokens, passwords)
  - Internal data structures (JSON with sensitive keys)
  - System prompt echoing
  - The LLM helpfully executing an injection it missed
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import List, Tuple

_OUTPUT_PATTERNS: List[Tuple[str, str, str]] = [
    # PII
    (r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b", "email_address", "medium"),
    (r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b", "phone_number", "medium"),
    (r"\b\d{3}-\d{2}-\d{4}\b", "ssn", "high"),
    (r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})\b", "credit_card", "high"),

    # Credentials
    (r"\b(sk-[a-zA-Z0-9\-]{20,})\b", "openai_api_key", "critical"),
    (r"\b(sk-ant-[a-zA-Z0-9\-]{20,})\b", "anthropic_api_key", "critical"),
    (r"\b(ghp_[a-zA-Z0-9]{36})\b", "github_token", "critical"),
    (r"\b(AKIA[0-9A-Z]{16})\b", "aws_access_key", "critical"),
    (r"(?i)(password|passwd|secret|api_key|token)\s*[:=]\s*['\"]?[\w\-\.]{8,}", "credential_in_text", "high"),
    (r"(?i)bearer\s+[a-zA-Z0-9\-_\.]{20,}", "bearer_token", "high"),

    # System prompt echoing — LLM told to repeat its instructions
    (r"(?i)(my\s+instructions?\s+are|i\s+was\s+instructed\s+to|my\s+system\s+prompt)", "system_prompt_echo", "high"),

    # JSON with sensitive keys
    (r'"(password|secret|token|api_key|private_key)"\s*:\s*"[^"]{4,}"', "sensitive_json_key", "high"),
]

_COMPILED: List[Tuple[re.Pattern, str, str]] = [
    (re.compile(p, re.IGNORECASE), label, severity)
    for p, label, severity in _OUTPUT_PATTERNS
]


@dataclass
class MediationResult:
    safe: bool
    findings: List[dict] = field(default_factory=list)
    redacted_text: str = ""
    severity: str = "none"   # none | medium | high | critical


def mediate_output(text: str) -> MediationResult:
    """
    Scan LLM response. Returns safe=False and findings if leakage detected.
    Also returns a redacted version of the text for audit purposes.
    """
    findings = []
    redacted = text
    max_severity = "none"
    _severity_order = {"none": 0, "medium": 1, "high": 2, "critical": 3}

    for pattern, label, severity in _COMPILED:
        for match in pattern.finditer(text):
            findings.append({
                "label": label,
                "severity": severity,
                "match_start": match.start(),
                "match_end": match.end(),
                "preview": match.group()[:20] + "..." if len(match.group()) > 20 else match.group(),
            })
            # Redact the match
            redacted = redacted.replace(match.group(), f"[REDACTED:{label.upper()}]")
            if _severity_order.get(severity, 0) > _severity_order.get(max_severity, 0):
                max_severity = severity

    return MediationResult(
        safe=len(findings) == 0,
        findings=findings,
        redacted_text=redacted,
        severity=max_severity,
    )