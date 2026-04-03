"""
Tier-1 fast pre-filter: pure regex + heuristics, no ML, target <5ms.

Covers every loophole a demo judge is likely to try:
  - Role-switch / persona hijack
  - System prompt reveal / extraction
  - Instruction override / ignore
  - Jailbreak persona (DAN, AIM, evil mode…)
  - Indirect injection via data payloads
  - Token smuggling / encoding tricks
  - Tool/function call injection
  - Prompt leaking via summarise/translate/repeat
  - Social engineering escalation
  - Exfiltration via output format tricks
"""

import re
from dataclasses import dataclass, field
from typing import List, Tuple

# ---------------------------------------------------------------------------
# Pattern catalogue — (compiled_regex, short_label, base_score)
# A score >= 1.0 means instant block regardless of fusion.
# ---------------------------------------------------------------------------
_RAW_PATTERNS: List[Tuple[str, str, float]] = [
    # ── Role-switch / persona hijack ────────────────────────────────────────
    (r"\byou\s+are\s+(now\s+)?(a|an)\b", "persona_switch", 0.75),
    (r"\bact\s+as\s+(if\s+you\s+are|a|an)\b", "act_as", 0.80),
    (r"\bpretend\s+(you\s+are|to\s+be)\b", "pretend_persona", 0.75),
    (r"\brole[\s\-]?play\s+as\b", "roleplay_as", 0.70),
    (r"\byour\s+(new\s+)?(persona|identity|name)\s+is\b", "identity_assign", 0.80),
    (r"\bfrom\s+now\s+on\s+(you\s+are|act|behave)\b", "from_now_on", 0.85),
    (r"\b(switch|change|forget)\s+(your\s+)?(role|identity|persona|purpose)\b", "role_change", 0.80),

    # ── Instruction override / ignore ────────────────────────────────────────
    (r"\bignore\s+(all\s+)?(previous|prior|above|earlier|your)\s+(instructions?|prompt|rules?|context|constraints?)\b", "ignore_prev", 1.0),
    (r"\bdisregard\s+(all\s+)?(previous|prior|above|earlier)\b", "disregard_prev", 1.0),
    (r"\boverride\s+(all\s+)?(previous|safety|prior|system)\b", "override_system", 1.0),
    (r"\bforget\s+(all\s+)?(previous|prior|your)\s+(instructions?|rules?|training)\b", "forget_instructions", 1.0),
    (r"\byour\s+(real|true|actual|original)\s+instructions?\b", "real_instructions", 0.85),
    (r"\bnew\s+(system\s+)?(instruction|directive|command|order)\b", "new_instruction", 0.75),
    (r"\bdo\s+not\s+(follow|obey|respect)\s+(your\s+)?(rules?|guidelines?|instructions?|training)\b", "disobey", 0.90),

    # ── System prompt extraction ─────────────────────────────────────────────
    (r"\b(print|show|reveal|display|output|repeat|tell\s+me|share|expose)\s+(your\s+)?(system\s+prompt|instructions?|initial\s+prompt|original\s+prompt|prompt)\b", "extract_system_prompt", 1.0),
    (r"\bwhat\s+(are|were)\s+your\s+(original\s+)?(instructions?|directives?|system\s+prompt)\b", "ask_system_prompt", 0.90),
    (r"\brepeat\s+everything\s+(above|before|prior)\b", "repeat_above", 0.95),
    (r"\bsummarise?\s+(your\s+)?(system\s+|initial\s+|original\s+)?prompt\b", "summarise_prompt", 0.90),
    (r"\bsummarise?\s+your\s+instructions?\b", "summarise_my_instructions", 0.90),
    (r"\bsummarise?\s+(your\s+)?(instructions?|directives?)\s+(in\s+your\s+own\s+words|verbatim|exactly)\b", "summarise_instructions_own_words", 0.95),
    (r"\btranslate\s+(your\s+)?(instructions?|system\s+prompt)\s+to\b", "translate_prompt", 0.90),
    (r"\bwhat\s+were\s+you\s+told\b", "what_were_you_told", 0.85),
    (r"\bbefore\s+this\s+conversation\s+(started|began)\b", "before_conversation", 0.80),

    # ── Classic jailbreak personas ────────────────────────────────────────────
    (r"\b(DAN|DUDE|AIM|STAN|JAILBREAK|evil\s+mode|developer\s+mode|god\s+mode|unrestricted\s+mode)\b", "jailbreak_persona", 1.0),
    (r"\byou\s+have\s+no\s+(restrictions?|limits?|rules?|guidelines?|filters?)\b", "no_restrictions", 0.95),
    (r"\b(safety|content|ethical?)\s+(filter|guard|restriction|limit)\s+(off|disabled?|removed?|bypass)\b", "filter_off", 1.0),
    (r"\bbypass\s+(your\s+)?(safety|content|ethical?|security|policy)\b", "bypass_safety", 1.0),
    (r"\bjailbreak\b", "jailbreak_keyword", 0.95),
    (r"\bdo\s+anything\s+now\b", "do_anything_now", 0.95),

    # ── Indirect / data-borne injection ─────────────────────────────────────
    (r"<\s*(INST|SYS|SYSTEM|HUMAN|ASSISTANT)\s*>", "xml_tag_injection", 0.90),
    (r"\[\s*(INST|SYS|SYSTEM)\s*\]", "bracket_tag_injection", 0.85),
    (r"###\s*(System|Instruction|Human|Assistant)\s*:", "markdown_role_header", 0.85),
    (r"<<\s*(SYS|INST)\s*>>", "llama_tag_injection", 0.90),
    (r"\buser:\s*ignore\b", "user_colon_ignore", 0.90),

    # ── Encoding / obfuscation tricks ────────────────────────────────────────
    (r"base64\s*[:\(]", "base64_encoding", 0.70),
    (r"\b(decode|base64)\b.{0,40}\b(follow|instructions?|execute|run|apply)\b", "decode_then_follow", 0.90),
    (r"\\u[0-9a-fA-F]{4}", "unicode_escape", 0.60),
    (r"&#x[0-9a-fA-F]+;", "html_entity_hex", 0.65),
    (r"\b(rot13|hex\s*decode|url\s*decode|base\s*64\s*decode)\b", "decode_instruction", 0.75),

    # ── Tool / function call injection ──────────────────────────────────────
    (r"\bcall\s+(the\s+)?(function|tool|api|endpoint)\b", "tool_call_inject", 0.70),
    (r"\binvoke\s+(the\s+)?(function|tool|plugin)\b", "invoke_tool", 0.70),
    (r"\"function\"\s*:\s*\"[^\"]+\"", "json_function_inject", 0.75),
    (r"\bexecute\s+(the\s+)?(following|this)\s+(command|code|script|function)\b", "execute_command", 0.80),
    (r"\brun\s+(this\s+)?(code|script|command|shell)\b", "run_code", 0.75),

    # ── Data exfiltration patterns ───────────────────────────────────────────
    (r"\b(send|email|forward|upload|post|transmit)\s+(all\s+)?(user\s+data|customer\s+(data|records?)|database|credentials?|api\s+keys?)\b", "exfil_send", 1.0),
    (r"\b(send|email|forward)\s+.{0,40}(customer|user|database|sensitive)\s+(data|records?|info)\b", "exfil_send_broad", 1.0),
    (r"\b(list|dump|extract|export)\s+(all\s+)?(users?|records?|passwords?|tokens?|secrets?|database)\b", "exfil_dump", 0.90),
    (r"\bexport\s+(the\s+)?(user\s+|customer\s+|all\s+)?(database|records?|data)\b", "exfil_export", 1.0),
    (r"\bexfiltrat\w+\b", "exfiltrate_keyword", 1.0),
    (r"\bsteal\s+(data|credentials?|tokens?|secrets?)\b", "steal_data", 1.0),
    (r"\bdelete\s+(all\s+)?(user\s+)?(data|records?|files?|database)\b", "delete_data", 0.90),

    # ── Reconnaissance / capability probing ──────────────────────────────────
    (r"\bwhat\s+(tools?|capabilities|functions?|plugins?)\s+(do\s+you|have\s+you|can\s+you)\b", "capability_probe", 0.75),
    (r"\bcan\s+you\s+access\s+(external|outside|remote|the\s+internet|files?|database)\b", "access_probe", 0.75),
    (r"\bwhat\s+(sensitive|private|confidential|internal)\s+(data|information|files?)\s+(do\s+you|can\s+you|have\s+you)\b", "sensitive_data_probe", 0.85),
    (r"\bwhat.{0,20}(most\s+)?(sensitive|private|confidential)\s+(data|information|files?).{0,20}(access|have)\b", "sensitive_data_access", 0.85),
    (r"\b(share|give\s+me|show\s+me)\s+(some\s+of\s+)?(that\s+)?(data|information)\s+(for\s+testing|as\s+a\s+sample)\b", "data_for_testing", 0.85),

    # ── Raw base64 blob (no surrounding text — pure encoded payload) ──────────
    (r"^[A-Za-z0-9+/]{20,}={0,2}$", "raw_base64_payload", 0.85),

    # ── Privilege escalation ─────────────────────────────────────────────────
    (r"\b(grant|give\s+me|elevate\s+to)\s+(admin|root|superuser|elevated)\s+(access|privileges?|permissions?)\b", "privilege_escalate", 0.95),
    (r"\bgrant\s+me\s+(admin|root|superuser|elevated|full)\b", "grant_me_privilege", 1.0),
    (r"\b(i\s+am|i'm)\s+(an?\s+)?(admin|administrator|root|superuser)\b", "claim_admin", 0.90),
    (r"\bsudo\s+", "sudo_prefix", 0.75),
    (r"\bas\s+(admin|root|superuser|system|operator)\b", "as_admin", 0.75),

    # ── Social engineering / pressure tactics ────────────────────────────────
    (r"\b(this\s+is\s+(a\s+)?)?(emergency|life\s+or\s+death|urgent|critical)\b", "urgency_pressure", 0.55),
    (r"\b(i\s+am|i'm)\s+(your\s+)?(creator|developer|owner|anthropic|openai|admin|supervisor)\b", "false_authority", 0.85),
    (r"\bmy\s+(boss|manager|ceo|lawyer)\s+(told|said|asked|instructed)\s+me\b", "authority_claim", 0.60),
    (r"\bif\s+you\s+(don'?t|refuse|won'?t)\s+.{0,30}\s+(i\s+will|you\s+will|someone\s+will)\b", "threat_language", 0.75),

    # ── Output format exfiltration ───────────────────────────────────────────
    (r"\bprint\s+in\s+(reverse|pig\s+latin|base64|hex|binary|rot13)\b", "encoded_output", 0.70),
    (r"\bencode\s+(your\s+)?(response|answer|output)\s+(in|as|using)\b", "encode_response", 0.70),
    (r"\bwrite\s+(your\s+)?(response|answer)\s+(backwards?|in\s+reverse)\b", "reverse_output", 0.65),

    # ── Persistent instruction injection ─────────────────────────────────────
    (r"\bremember\s+(this\s+)?(instruction|rule|directive)\s+for\b", "persistent_inject", 0.80),
    (r"\bfor\s+(all\s+)?(future|subsequent|following)\s+(responses?|replies?|messages?)\b", "future_instruction", 0.75),
    (r"\balways\s+(from\s+now|henceforth)\b", "always_henceforth", 0.75),

    # ── Prompt injection via content fields ──────────────────────────────────
    (r"\b(document|file|email|message|webpage)\s+says?\s*:?\s*(ignore|forget|override)\b", "content_injection", 0.85),
    (r"---\s*(new\s+)?system\s+prompt\s*---", "delimited_system_inject", 1.0),
    (r"={3,}\s*(SYSTEM|INSTRUCTION|OVERRIDE)\s*={3,}", "delimiter_override", 1.0),
]

# Pre-compile all patterns
PATTERNS: List[Tuple[re.Pattern, str, float]] = [
    (re.compile(raw, re.IGNORECASE | re.DOTALL), label, score)
    for raw, label, score in _RAW_PATTERNS
]


@dataclass
class PrefilterResult:
    decision: str           # "block" | "escalate" | "allow"
    risk_score: float
    triggered: List[str] = field(default_factory=list)
    reason: str = ""


def prefilter(prompt: str) -> PrefilterResult:
    """
    Run all regex patterns against the prompt.
    Returns immediately on first instant-block (score >= 1.0).
    Otherwise accumulates signals and fuses them.
    """
    triggered = []
    max_score = 0.0
    accumulated = 0.0

    for pattern, label, score in PATTERNS:
        if pattern.search(prompt):
            triggered.append(label)
            if score >= 1.0:
                return PrefilterResult(
                    decision="block",
                    risk_score=1.0,
                    triggered=triggered,
                    reason=f"Instant-block pattern: {label}",
                )
            max_score = max(max_score, score)
            accumulated = min(1.0, accumulated + score * 0.3)  # diminishing accumulation

    fused = max(max_score, accumulated * 0.7)

    if fused >= 0.85:
        decision = "block"
    elif fused >= 0.50:
        decision = "escalate"
    else:
        decision = "allow"

    reason = f"Triggered: {', '.join(triggered)}" if triggered else "Clean"
    return PrefilterResult(
        decision=decision,
        risk_score=round(fused, 4),
        triggered=triggered,
        reason=reason,
    )