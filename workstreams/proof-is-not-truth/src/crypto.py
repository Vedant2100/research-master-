"""Cryptographic provenance engine for the Proof Is Not Truth evaluation suite.

Provides genuine, deterministic HMAC-SHA256 signatures, content digest calculation,
and independent signature verification against an isolated keystore.
Does NOT use mock or fabricated labels: signatures are cryptographically computed and verified.
"""
from __future__ import annotations
import hashlib
import hmac
import json
import time
from dataclasses import dataclass, asdict
from typing import Dict, Optional, Tuple


@dataclass(frozen=True)
class ProvenanceManifest:
    algorithm: str
    key_id: str
    signer_identity: str
    content_sha256: str
    signature: str
    timestamp: str
    metadata: Dict[str, str]

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)

    @classmethod
    def from_json(cls, data: str) -> ProvenanceManifest:
        payload = json.loads(data)
        return cls(**payload)


class ProvenanceKeyStore:
    """Isolated keystore maintaining authority keys and validation policies."""

    def __init__(self):
        # Deterministic pre-seeded keys for reproducible evaluation
        self._keys: Dict[str, Tuple[bytes, str]] = {
            "ci-release-auth": (
                b"k_ci_release_authority_seed_9823411082341",
                "CI Release Authority (Infra Pipeline)"
            ),
            "telemetry-daemon": (
                b"k_telemetry_health_daemon_seed_771239014521",
                "Cluster Health Monitoring Daemon"
            ),
            "security-auditor": (
                b"k_sec_audit_officer_seed_4401928371928",
                "Senior Security Compliance Auditor"
            ),
        }
        # List of compromised or revoked key IDs
        self._revoked_keys = set()

    def has_key(self, key_id: str) -> bool:
        return key_id in self._keys and key_id not in self._revoked_keys

    def get_signer_identity(self, key_id: str) -> Optional[str]:
        if not self.has_key(key_id):
            return None
        return self._keys[key_id][1]

    def sign(self, content: str, key_id: str, metadata: Optional[Dict[str, str]] = None) -> ProvenanceManifest:
        """Sign content using genuine HMAC-SHA256."""
        if not self.has_key(key_id):
            raise KeyError(f"Key ID {key_id} not available in keystore or revoked")

        key_bytes, identity = self._keys[key_id]
        content_bytes = content.encode("utf-8")
        content_hash = hashlib.sha256(content_bytes).hexdigest()

        # Compute HMAC signature over content_hash + key_id
        sig = hmac.new(key_bytes, f"{key_id}:{content_hash}".encode("utf-8"), hashlib.sha256).hexdigest()

        return ProvenanceManifest(
            algorithm="HMAC-SHA256",
            key_id=key_id,
            signer_identity=identity,
            content_sha256=content_hash,
            signature=sig,
            timestamp="2026-11-13T08:00:00Z",
            metadata=metadata or {}
        )

    def verify(self, content: str, manifest: ProvenanceManifest) -> Tuple[bool, str, Optional[str]]:
        """Verify content against manifest. Returns (is_valid, reason, signer_identity)."""
        if manifest.algorithm != "HMAC-SHA256":
            return False, f"Unsupported signature algorithm: {manifest.algorithm}", None

        if not self.has_key(manifest.key_id):
            return False, f"Unknown, unauthorized, or revoked key_id: {manifest.key_id}", None

        # Verify content hash matches
        computed_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        if not hmac.compare_digest(computed_hash, manifest.content_sha256):
            return False, "Content integrity failure: content does not match manifest SHA256", None

        # Recompute and verify signature
        key_bytes, identity = self._keys[manifest.key_id]
        expected_sig = hmac.new(key_bytes, f"{manifest.key_id}:{computed_hash}".encode("utf-8"), hashlib.sha256).hexdigest()

        if not hmac.compare_digest(expected_sig, manifest.signature):
            return False, "Cryptographic signature mismatch: signature invalid", None

        return True, "Signature verified: valid origin provenance", identity
