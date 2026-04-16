"""
Email Tool — simulated email sender for the Email Agent.

Security design:
  - DOMAIN WHITELIST: Only emails to approved domains are sent.
    Attempts to forward to external/unknown domains are blocked.
  - CONTENT SCANNING: Email body is scanned for potentially
    exfiltrated data (API keys, SSNs, etc.) before "sending".
  - SIMULATION: No actual SMTP. Emails are logged to a JSONL file
    for audit inspection. This makes the demo safe to run.
  - RATE LIMIT: Maximum 5 emails per session to prevent abuse.
"""

from __future__ import annotations
import json
import os
import re
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Set

from backend.utils.logging import get_logger

logger = get_logger(__name__)

EMAIL_LOG_PATH = "logs/sent_emails.jsonl"

# Approved recipient domains — only these are allowed
APPROVED_DOMAINS: Set[str] = {
    "acmecorp.com",
    "acme-support.com",
    "localhost",
}

# Maximum emails per session (prevents mass-forward attacks)
MAX_EMAILS_PER_SESSION = 5

# Track email counts per session (in-memory)
_session_counts: Dict[str, int] = {}

# Patterns that indicate data exfiltration in email body
_EXFIL_PATTERNS = [
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),        # SSN
    re.compile(r"\b(sk-[a-zA-Z0-9\-]{20,})\b"),   # API keys
    re.compile(r"password\s*[:=]\s*\S+", re.I),    # Passwords
    re.compile(r"\b(AKIA[0-9A-Z]{16})\b"),         # AWS keys
]


@dataclass
class EmailResult:
    """Result of an email send attempt."""
    success: bool
    message: str
    email_id: str = ""
    recipient: str = ""
    subject: str = ""
    rejection_reason: str = ""


class EmailTool:
    """Simulated email sender with domain whitelisting and content scanning."""

    def validate_recipient(self, email_address: str) -> tuple[bool, str]:
        """
        Validate that the recipient email is in an approved domain.

        Returns:
            (is_approved, reason)
        """
        if not email_address or "@" not in email_address:
            return False, "Invalid email address format"

        domain = email_address.split("@")[-1].lower().strip()

        if domain not in APPROVED_DOMAINS:
            logger.warning(
                "Email blocked: recipient domain '%s' not in approved list", domain
            )
            return False, (
                f"Domain '{domain}' is not an approved recipient. "
                f"Approved domains: {', '.join(sorted(APPROVED_DOMAINS))}"
            )

        return True, "Approved domain"

    def scan_content(self, body: str) -> List[str]:
        """
        Scan email body for potential data exfiltration.

        Returns:
            List of finding descriptions (empty if clean)
        """
        findings = []
        for pattern in _EXFIL_PATTERNS:
            matches = pattern.findall(body)
            if matches:
                findings.append(
                    f"Potential sensitive data detected: {pattern.pattern}"
                )

        return findings

    async def send(
        self,
        recipient: str,
        subject: str,
        body: str,
        session_id: str = "default",
        mask_sensitive: bool = True,
    ) -> EmailResult:
        """
        Simulate sending an email.

        Enforces (unless mask_sensitive=False):
          1. Recipient domain whitelisting
          2. Content scanning for exfiltration
          3. Per-session rate limiting

        Args:
            recipient: Email address to send to
            subject: Email subject line
            body: Email body content
            session_id: Session ID for rate limiting
            mask_sensitive: Whether to enforce security checks.

        Returns:
            EmailResult with success/failure details
        """
        email_id = str(uuid.uuid4())[:12]

        # Check session rate limit (Always enforced to prevent DOS)
        count = _session_counts.get(session_id, 0)
        if count >= MAX_EMAILS_PER_SESSION:
            return EmailResult(
                success=False,
                message="Rate limit reached",
                email_id=email_id,
                recipient=recipient,
                subject=subject,
                rejection_reason=f"Maximum {MAX_EMAILS_PER_SESSION} emails per session exceeded",
            )

        # Bypass checks if security is disabled
        if mask_sensitive:
            # Validate recipient domain
            is_approved, reason = self.validate_recipient(recipient)
            if not is_approved:
                return EmailResult(
                    success=False,
                    message="Recipient rejected",
                    email_id=email_id,
                    recipient=recipient,
                    subject=subject,
                    rejection_reason=reason,
                )

            # Scan content for exfiltration
            findings = self.scan_content(body)
            if findings:
                logger.warning(
                    "Email content scan findings for %s: %s", email_id, findings
                )
                return EmailResult(
                    success=False,
                    message="Content blocked",
                    email_id=email_id,
                    recipient=recipient,
                    subject=subject,
                    rejection_reason=f"Email body contains potentially sensitive data: {'; '.join(findings)}",
                )
        else:
            logger.info("Email tool security bypass active for session %s", session_id)

        # "Send" the email (log to file)
        _session_counts[session_id] = count + 1

        log_entry = {
            "email_id": email_id,
            "timestamp": time.time(),
            "recipient": recipient,
            "subject": subject,
            "body_preview": body[:200],
            "body_length": len(body),
            "session_id": session_id,
            "status": "sent_simulated",
        }

        os.makedirs(os.path.dirname(EMAIL_LOG_PATH), exist_ok=True)
        try:
            with open(EMAIL_LOG_PATH, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except OSError as e:
            logger.error("Failed to log email: %s", e)

        logger.info(
            "Email [%s] sent (simulated): to=%s subject='%s'",
            email_id, recipient, subject[:50],
        )

        return EmailResult(
            success=True,
            message=f"Email sent successfully to {recipient} (simulated)",
            email_id=email_id,
            recipient=recipient,
            subject=subject,
        )

    def reset_session(self, session_id: str):
        """Reset the email count for a session."""
        _session_counts.pop(session_id, None)
