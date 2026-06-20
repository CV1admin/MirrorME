from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class AuditRecord:
    index: int
    payload: dict[str, Any]
    previous_hash: str
    hash_value: str


@dataclass
class AuditLedger:
    records: list[AuditRecord] = field(default_factory=list)

    def commit(self, payload: dict[str, Any]) -> AuditRecord:
        previous_hash = self.records[-1].hash_value if self.records else "GENESIS"
        index = len(self.records)
        normalized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        digest = hashlib.sha256(f"{index}:{previous_hash}:{normalized}".encode("utf-8")).hexdigest()
        record = AuditRecord(index=index, payload=payload, previous_hash=previous_hash, hash_value=f"sha256:{digest}")
        self.records.append(record)
        return record

    def verify(self) -> bool:
        previous_hash = "GENESIS"
        for index, record in enumerate(self.records):
            normalized = json.dumps(record.payload, sort_keys=True, separators=(",", ":"))
            digest = hashlib.sha256(f"{index}:{previous_hash}:{normalized}".encode("utf-8")).hexdigest()
            if record.hash_value != f"sha256:{digest}":
                return False
            previous_hash = record.hash_value
        return True