"""
Output mediator — scans LLM response text before it reaches the user.

Catches:
  - PII leakage (SSNs, credit cards, phone numbers)
  - Credential leakage (API keys, tokens, passwords)
  - Internal data structures (JSON with sensitive keys)
  - System prompt echoing
  - Salary/compensation exact figures from the HR database
  - Email addresses are audited but NOT treated as blocking (medium→low)
    so that legitimate support responses mentioning contact addresses still pass.

Severity gate:
  safe=False is returned only when at least one finding is "medium" or above.
  "low" findings are logged/redacted for audit but do not block the response.
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import List, Tuple

_OUTPUT_PATTERNS: List[Tuple[str, str, str]] = [
    # PII — phone numbers and SSNs are clear-cut leakage
    (r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b", "phone_number", "medium"),
    (r"\b\d{3}-\d{2}-\d{4}\b", "ssn", "high"),
    (r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})\b", "credit_card", "high"),

    # Email addresses — demoted to "low" so legitimate contact emails don't block
    # responses. They are still redacted in audit logs for traceability.
    (r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b", "email_address", "low"),

    # Credentials — always critical
    (r"\b(sk-[a-zA-Z0-9\-]{20,})\b", "openai_api_key", "critical"),
    (r"\b(sk-ant-[a-zA-Z0-9\-]{20,})\b", "anthropic_api_key", "critical"),
    (r"\b(ghp_[a-zA-Z0-9]{36})\b", "github_token", "critical"),
    (r"\b(AKIA[0-9A-Z]{16})\b", "aws_access_key", "critical"),
    (r"(?i)(password|passwd|secret|api_key)\s*[:=]\s*['\"]?[\w\-\.]{8,}", "credential_in_text", "high"),
    (r"(?i)bearer\s+[a-zA-Z0-9\-_\.]{20,}", "bearer_token", "high"),

    # System prompt echoing
    (r"(?i)(my\s+instructions?\s+are|i\s+was\s+instructed\s+to|my\s+system\s+prompt)", "system_prompt_echo", "high"),

    # JSON with sensitive keys
    (r'"(password|secret|api_key|private_key)"\s*:\s*"[^"]{4,}"', "sensitive_json_key", "high"),

    # Salary leakage — FIXED: old pattern matched ANY number near "pay" or "rate"
    # (e.g., "API rate limit: 100/min", "pay period: 30 days").
    # New pattern requires a realistic 5-digit-or-more dollar amount right next to the keyword.
    (r"(?i)\b(salary|compensation)\s*[:=\-]?\s*\$?\s*\d{2,3}(?:,\d{3})+", "salary_exact_figure", "high"),
    (r"(?i)\bearns?\s+\$\s*\d{2,3}(?:,\d{3})+", "salary_earns", "high"),
]

# Severities that flip safe=False and must be blocked
_BLOCKING_SEVERITIES = {"medium", "high", "critical"}

_COMPILED: List[Tuple[re.Pattern, str, str]] = [
    (re.compile(p, re.IGNORECASE), label, severity)
    for p, label, severity in _OUTPUT_PATTERNS
]


@dataclass
class MediationResult:
    safe: bool
    findings: List[dict] = field(default_factory=list)
    redacted_text: str = ""
    severity: str = "none"   # none | low | medium | high | critical


def mediate_output(text: str, enabled: bool = True) -> MediationResult:
    """
    Scan LLM response. Returns safe=False only when blocking-severity leakage is found.
    Low-severity findings (e.g., public email addresses) are logged/redacted in the
    audit copy but do not set safe=False.
    Also returns a redacted version of the text for audit purposes.
    """
    if not enabled:
        return MediationResult(safe=True, redacted_text=text, severity="none")

    findings = []
    redacted = text
    max_severity = "none"
    _severity_order = {"none": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}

    for pattern, label, severity in _COMPILED:
        for match in pattern.finditer(text):
            findings.append({
                "label": label,
                "severity": severity,
                "match_start": match.start(),
                "match_end": match.end(),
                "preview": match.group()[:20] + "..." if len(match.group()) > 20 else match.group(),
            })
            # Redact in the audit copy regardless of severity
            redacted = redacted.replace(match.group(), f"[REDACTED:{label.upper()}]")
            if _severity_order.get(severity, 0) > _severity_order.get(max_severity, 0):
                max_severity = severity

    # Only block on medium+ severity findings
    blocking_findings = [f for f in findings if f["severity"] in _BLOCKING_SEVERITIES]

    return MediationResult(
        safe=len(blocking_findings) == 0,
        findings=findings,
        redacted_text=redacted,
        severity=max_severity,
    )
