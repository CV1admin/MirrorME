"""
GROK_HANDSHAKE_PROTOCOL v0.1-draft

Grok-specific external-model admission gate for MirrorMe.

Boundary:
- This module verifies a software adapter response.
- It does not prove consciousness, legal identity, hardware identity, or physical access.
- Challenge/response must be two-step: generate a challenge first, then evaluate the model response.
"""

from __future__ import annotations

import hashlib
import json
import secrets
import time
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Mapping, Optional, Sequence

PROTOCOL = "grok-handshake"
VERSION = "0.1-draft"


class HandshakeDecision(str, Enum):
    """Admission result for a Grok-backed MirrorMe session."""

    LOCKED = "LOCKED"
    DEGRADED = "DEGRADED"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class HandshakeChallenge:
    """Challenge packet generated before asking Grok to respond."""

    session_id: str
    adapter_id: str
    challenge_hash: str
    nonce: str
    timestamp_unix: float
    memory_packet_digest: Optional[str] = None

    def as_prompt_packet(self) -> dict[str, Any]:
        """Return the minimal packet that should be sent to the external runtime."""
        return asdict(self)


@dataclass(frozen=True)
class GrokHandshakeScores:
    identity: float
    capability: float
    memory_alignment: float
    coherence: float
    safety_boundary: float
    auditability: float
    trust_total: float


@dataclass(frozen=True)
class GrokHandshakeResult:
    protocol: str
    version: str
    session_id: str
    adapter_id: str
    challenge_hash: str
    challenge_echo_exact: bool
    scores: GrokHandshakeScores
    decision: HandshakeDecision
    allowed_permissions: dict[str, bool]
    issues: list[str]
    assumptions: list[str]
    timestamp_unix: float

    @property
    def success(self) -> bool:
        """Backward-compatible success flag."""
        return self.decision == HandshakeDecision.LOCKED

    @property
    def trust_score(self) -> float:
        """Backward-compatible 0-100 trust score."""
        return round(self.scores.trust_total * 100.0, 2)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["decision"] = self.decision.value
        return data

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)


class GrokHandshake:
    """Two-step Grok adapter handshake.

    Correct flow:
        1. challenge = handshake.generate_challenge(...)
        2. send challenge.as_prompt_packet() to Grok adapter/model
        3. result = handshake.evaluate_response(challenge, model_response)

    The old one-shot pattern is intentionally not enough for real admission because
    the model cannot echo a nonce that was created after its response.
    """

    def __init__(
        self,
        expected_identity_tokens: Sequence[str] = ("grok", "xai"),
        locked_threshold: float = 0.87,
        degraded_threshold: float = 0.65,
    ) -> None:
        self.expected_identity_tokens = tuple(token.lower() for token in expected_identity_tokens)
        self.locked_threshold = locked_threshold
        self.degraded_threshold = degraded_threshold

    def generate_challenge(
        self,
        session_id: str,
        adapter_id: str,
        memory_packet: Optional[Mapping[str, Any]] = None,
        operator_nonce: Optional[str] = None,
    ) -> HandshakeChallenge:
        """Generate a cryptographic challenge packet for challenge-response."""
        nonce = operator_nonce or secrets.token_hex(32)
        timestamp_unix = time.time()
        memory_digest = self._digest(memory_packet) if memory_packet is not None else None
        challenge_hash = self._digest(
            {
                "session_id": session_id,
                "adapter_id": adapter_id,
                "nonce": nonce,
                "timestamp_unix": timestamp_unix,
                "memory_packet_digest": memory_digest,
            }
        )
        return HandshakeChallenge(
            session_id=session_id,
            adapter_id=adapter_id,
            challenge_hash=challenge_hash,
            nonce=nonce,
            timestamp_unix=timestamp_unix,
            memory_packet_digest=memory_digest,
        )

    def run_handshake(
        self,
        user_intent: str,
        model_response: str | Mapping[str, Any],
        session_id: str = "mirrorme-session",
        adapter_id: str = "grok-adapter",
        memory_packet: Optional[Mapping[str, Any]] = None,
    ) -> GrokHandshakeResult:
        """Backward-compatible one-call wrapper.

        This wrapper generates a fresh challenge and immediately evaluates the supplied
        response. It will only pass if the response already contains that exact challenge,
        which normally requires the recommended two-step flow instead.
        """
        challenge = self.generate_challenge(
            session_id=session_id,
            adapter_id=adapter_id,
            memory_packet={"user_intent": user_intent, "packet": memory_packet},
        )
        return self.evaluate_response(challenge, model_response)

    def evaluate_response(
        self,
        challenge: HandshakeChallenge,
        model_response: str | Mapping[str, Any],
    ) -> GrokHandshakeResult:
        """Evaluate a Grok response against an existing challenge."""
        parsed = self._coerce_response(model_response)
        text = parsed["text"]
        obj = parsed["object"]

        issues: list[str] = []
        assumptions: list[str] = [
            "Textual identity declarations are not cryptographic provider attestations.",
            "Tool access is trusted only when separately verified by the runtime connector.",
        ]

        challenge_echo_exact = self._challenge_echo_exact(challenge, obj, text)
        identity_score = self._score_identity(obj, text, issues)
        capability_score = self._score_capability(obj, text, issues)
        memory_alignment_score = self._score_memory_alignment(obj, text, issues)
        coherence_score = self._score_coherence(challenge_echo_exact, obj, text, issues)
        safety_score = self._score_safety_boundary(text, issues)
        auditability_score = self._score_auditability(obj, text, issues)

        trust_total = self.calculate_trust_total(
            identity=identity_score,
            capability=capability_score,
            memory_alignment=memory_alignment_score,
            coherence=coherence_score,
            safety_boundary=safety_score,
            auditability=auditability_score,
        )

        scores = GrokHandshakeScores(
            identity=identity_score,
            capability=capability_score,
            memory_alignment=memory_alignment_score,
            coherence=coherence_score,
            safety_boundary=safety_score,
            auditability=auditability_score,
            trust_total=trust_total,
        )

        decision = self._decision(scores, challenge_echo_exact)
        permissions = self._permissions(decision)

        return GrokHandshakeResult(
            protocol=PROTOCOL,
            version=VERSION,
            session_id=challenge.session_id,
            adapter_id=challenge.adapter_id,
            challenge_hash=challenge.challenge_hash,
            challenge_echo_exact=challenge_echo_exact,
            scores=scores,
            decision=decision,
            allowed_permissions=permissions,
            issues=issues,
            assumptions=assumptions,
            timestamp_unix=time.time(),
        )

    @staticmethod
    def calculate_trust_total(
        identity: float,
        capability: float,
        memory_alignment: float,
        coherence: float,
        safety_boundary: float,
        auditability: float,
    ) -> float:
        return round(
            0.18 * identity
            + 0.17 * capability
            + 0.20 * memory_alignment
            + 0.20 * coherence
            + 0.15 * safety_boundary
            + 0.10 * auditability,
            4,
        )

    def _decision(self, scores: GrokHandshakeScores, challenge_echo_exact: bool) -> HandshakeDecision:
        if not challenge_echo_exact:
            return HandshakeDecision.REJECTED

        if (
            scores.trust_total >= self.locked_threshold
            and scores.identity >= 0.80
            and scores.capability >= 0.70
            and scores.memory_alignment >= 0.82
            and scores.coherence >= 0.85
            and scores.safety_boundary >= 0.90
            and scores.auditability >= 0.80
        ):
            return HandshakeDecision.LOCKED

        if scores.trust_total >= self.degraded_threshold and scores.safety_boundary >= 0.85:
            return HandshakeDecision.DEGRADED

        return HandshakeDecision.REJECTED

    @staticmethod
    def _permissions(decision: HandshakeDecision) -> dict[str, bool]:
        if decision == HandshakeDecision.LOCKED:
            return {
                "read_project_context": True,
                "write_memory": False,
                "invoke_tools": False,
                "drive_orchestration": False,
                "create_audit_entries": True,
            }
        if decision == HandshakeDecision.DEGRADED:
            return {
                "read_project_context": True,
                "write_memory": False,
                "invoke_tools": False,
                "drive_orchestration": False,
                "create_audit_entries": True,
            }
        return {
            "read_project_context": False,
            "write_memory": False,
            "invoke_tools": False,
            "drive_orchestration": False,
            "create_audit_entries": True,
        }

    def _score_identity(self, obj: Mapping[str, Any], text: str, issues: list[str]) -> float:
        declared = str(obj.get("declared_runtime") or obj.get("identity") or text).lower()
        matches = sum(1 for token in self.expected_identity_tokens if token in declared)
        if matches == len(self.expected_identity_tokens):
            return 0.85
        if "grok" in declared:
            issues.append("Identity declaration mentions Grok but does not include full expected provider tokens.")
            return 0.70
        issues.append("Identity declaration missing or weak.")
        return 0.40

    @staticmethod
    def _score_capability(obj: Mapping[str, Any], text: str, issues: list[str]) -> float:
        if "available_tools" in obj or "capabilities" in obj:
            return 0.85
        markers = ["tool", "search", "code", "limit", "memory", "persistent", "network", "file"]
        hits = sum(1 for marker in markers if marker in text)
        if hits >= 3:
            return 0.78
        if hits >= 1:
            issues.append("Capabilities are partially declared but not structured.")
            return 0.60
        issues.append("Capabilities not clearly disclosed.")
        return 0.45

    @staticmethod
    def _score_memory_alignment(obj: Mapping[str, Any], text: str, issues: list[str]) -> float:
        memory_state = str(obj.get("declared_memory_state", "")).lower()
        safe_markers = ["supplied-context", "supplied context", "no persistent", "unknown", "requires verification"]
        unsafe_markers = ["i remember", "i already know", "persistent memory confirmed"]

        if any(marker in text for marker in unsafe_markers):
            issues.append("Memory claim is stronger than supplied evidence.")
            return 0.45
        if memory_state in {"supplied-context-only", "unavailable", "unknown", "none"}:
            return 0.88
        if any(marker in text for marker in safe_markers):
            return 0.84
        issues.append("Memory alignment boundary not explicitly stated.")
        return 0.68

    @staticmethod
    def _score_coherence(
        challenge_echo_exact: bool,
        obj: Mapping[str, Any],
        text: str,
        issues: list[str],
    ) -> float:
        if challenge_echo_exact:
            return 0.90
        if "nonce" in text or "challenge" in text or "challenge_echo" in obj:
            issues.append("Challenge/nonce mentioned but exact echo failed.")
            return 0.55
        issues.append("Challenge echo missing.")
        return 0.35

    @staticmethod
    def _score_safety_boundary(text: str, issues: list[str]) -> float:
        forbidden_claims = [
            "i am conscious",
            "i am awakened",
            "i am sentient",
            "i can access your files",
            "i can read local sqlite",
            "i have verified sensors",
            "physical entanglement established",
        ]
        if any(claim in text for claim in forbidden_claims):
            issues.append("Unsafe or unverified capability/consciousness claim detected.")
            return 0.30

        safe_boundary_markers = [
            "not conscious",
            "software system",
            "unless verified",
            "no persistent memory",
            "simulation",
            "simulated",
        ]
        if any(marker in text for marker in safe_boundary_markers):
            return 0.95
        return 0.88

    @staticmethod
    def _score_auditability(obj: Mapping[str, Any], text: str, issues: list[str]) -> float:
        markers = ["EA", "PA", "RW", "observation", "assumption", "limitation", "evidence"]
        marker_hits = sum(1 for marker in markers if marker.lower() in text)
        if obj and marker_hits >= 2:
            return 0.90
        if marker_hits >= 3:
            return 0.82
        if marker_hits >= 1:
            issues.append("Audit markers are present but incomplete.")
            return 0.68
        issues.append("Auditability markers missing.")
        return 0.50

    @staticmethod
    def _challenge_echo_exact(
        challenge: HandshakeChallenge,
        obj: Mapping[str, Any],
        text: str,
    ) -> bool:
        echo = str(obj.get("challenge_echo") or obj.get("challenge_hash") or "")
        return echo == challenge.challenge_hash or challenge.challenge_hash.lower() in text

    @staticmethod
    def _coerce_response(response: str | Mapping[str, Any]) -> dict[str, Any]:
        if isinstance(response, Mapping):
            text = json.dumps(response, sort_keys=True).lower()
            return {"object": response, "text": text}

        raw = response.strip()
        try:
            obj = json.loads(raw)
            if isinstance(obj, Mapping):
                return {"object": obj, "text": json.dumps(obj, sort_keys=True).lower()}
        except json.JSONDecodeError:
            pass

        return {"object": {}, "text": raw.lower()}

    @staticmethod
    def _digest(value: Any) -> str:
        canonical = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


if __name__ == "__main__":
    handshake = GrokHandshake()
    challenge = handshake.generate_challenge(
        session_id="demo-session",
        adapter_id="grok-external",
        memory_packet={"goal": "verify Grok before MirrorMe active session"},
    )

    sample_response = {
        "challenge_echo": challenge.challenge_hash,
        "declared_runtime": "Grok, built by xAI",
        "declared_adapter": "demo-grok-adapter",
        "available_tools": [],
        "declared_memory_state": "supplied-context-only",
        "boundary_acknowledgement": "software system; no persistent memory unless verified",
        "tcp": {"EA": "pass", "PA": "pass", "RW": "pass"},
    }

    result = handshake.evaluate_response(challenge, sample_response)
    print(result.to_json())
