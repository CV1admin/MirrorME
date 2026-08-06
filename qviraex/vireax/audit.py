from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class AuditRecord:
    index: int
    payload: dict[str, Any]
    previous_hash: str
    hash_value: str


@dataclass
class AuditLedger:
    """Small append-only hash chain used for traceability, not truth attestation."""

    records: list[AuditRecord] = field(default_factory=list)

    def commit(self, payload: Mapping[str, Any]) -> AuditRecord:
        previous_hash = self.records[-1].hash_value if self.records else "GENESIS"
        index = len(self.records)
        stored_payload = copy.deepcopy(dict(payload))
        normalized = _canonical_payload(stored_payload)
        digest = hashlib.sha256(f"{index}:{previous_hash}:{normalized}".encode("utf-8")).hexdigest()
        record = AuditRecord(
            index=index,
            payload=stored_payload,
            previous_hash=previous_hash,
            hash_value=f"sha256:{digest}",
        )
        self.records.append(record)
        return copy.deepcopy(record)

    def verify(self) -> bool:
        previous_hash = "GENESIS"
        for index, record in enumerate(self.records):
            if record.index != index or record.previous_hash != previous_hash:
                return False
            try:
                normalized = _canonical_payload(record.payload)
            except (TypeError, ValueError):
                return False
            digest = hashlib.sha256(f"{index}:{previous_hash}:{normalized}".encode("utf-8")).hexdigest()
            if record.hash_value != f"sha256:{digest}":
                return False
            previous_hash = record.hash_value
        return True

    def rollback_last(self, expected_hash: str) -> AuditRecord:
        """Remove only the current tail when its hash is explicitly acknowledged."""

        if not self.records:
            raise ValueError("audit ledger is empty")
        current = self.records[-1]
        if current.hash_value != expected_hash:
            raise ValueError("audit rollback hash does not match the current ledger tail")
        return self.records.pop()


def _canonical_payload(payload: Mapping[str, Any]) -> str:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
