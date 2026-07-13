"""EMK Material Certificate and Finality v8."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
import hashlib
import json

try:
    from emk_audit_report_v7 import CandidateAudit, run_audit_report
except ImportError:
    import sys
    sys.path.append(str(Path(__file__).resolve().parent))
    from emk_audit_report_v7 import CandidateAudit, run_audit_report

CERTIFICATE_VERSION = "EMK_MATERIAL_CERTIFICATE_V8"
LEDGER_VERSION = "EMK_MATERIAL_FINALITY_LEDGER_V8"

def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def sha256_hex(obj: Any) -> str:
    data = obj.encode("utf-8") if isinstance(obj, str) else canonical_json(obj).encode("utf-8")
    return hashlib.sha256(data).hexdigest()

@dataclass
class MaterialCertificate:
    certificate_version: str
    created_at_utc: str
    material: str
    family: str
    rank: int
    source_weighted_priority: float
    model_priority_score: float
    evidence_strength: float
    strongest_signal: str
    warning_flags: List[str]
    missing_evidence: List[str]
    next_action: str
    classification: str
    claim_boundary: str
    payload_hash: str
    certificate_hash: str
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class FinalityCommit:
    ledger_version: str
    created_at_utc: str
    source_type: str
    material: str
    certificate_hash: str
    payload_hash: str
    prev_commit_hash: str
    proposed_state_hash: str
    proposal_hash: str
    entropy_delta: float
    commit_hash: str
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class MaterialCertificateFactory:
    def build_certificate(self, audit: CandidateAudit) -> MaterialCertificate:
        payload = {
            "material": audit.name,
            "family": audit.family,
            "rank": audit.rank,
            "source_weighted_priority": round(audit.source_weighted_priority, 12),
            "model_priority_score": round(audit.model_priority_score, 12),
            "evidence_strength": round(audit.evidence_strength, 12),
            "strongest_signal": audit.strongest_signal,
            "warning_flags": list(audit.warning_flags),
            "missing_evidence": list(audit.missing_evidence),
            "next_action": audit.next_action,
        }
        payload_hash = sha256_hex(payload)
        classification = self.classify_certificate(audit)
        claim_boundary = self.claim_boundary(audit)
        certificate_body = {
            "certificate_version": CERTIFICATE_VERSION,
            "material": audit.name,
            "family": audit.family,
            "rank": audit.rank,
            "payload_hash": payload_hash,
            "classification": classification,
            "claim_boundary": claim_boundary,
        }
        return MaterialCertificate(
            CERTIFICATE_VERSION,
            datetime.now(timezone.utc).isoformat(),
            audit.name,
            audit.family,
            audit.rank,
            float(audit.source_weighted_priority),
            float(audit.model_priority_score),
            float(audit.evidence_strength),
            audit.strongest_signal,
            list(audit.warning_flags),
            list(audit.missing_evidence),
            audit.next_action,
            classification,
            claim_boundary,
            payload_hash,
            sha256_hex(certificate_body),
        )

    @staticmethod
    def classify_certificate(audit: CandidateAudit) -> str:
        if audit.source_weighted_priority >= 0.62 and audit.evidence_strength >= 0.55:
            return "MATERIAL_SUPPORTED_RESEARCH_CANDIDATE"
        if audit.source_weighted_priority >= 0.48 and audit.evidence_strength < 0.45:
            return "MATERIAL_PROMISING_BUT_UNDER_EVIDENCED"
        if audit.evidence_strength >= 0.55 and audit.model_priority_score < 0.40:
            return "MATERIAL_EVIDENCE_SUPPORTED_CONTROL_OR_BASELINE"
        return "MATERIAL_EARLY_STAGE_RESEARCH_RECORD"

    @staticmethod
    def claim_boundary(audit: CandidateAudit) -> str:
        if audit.evidence_strength < 0.45:
            return "Computational screening record only; external evidence insufficient for empirical claim."
        return "Computational screening record with preliminary evidence support; still requires domain validation."

class MaterialFinalityLedger:
    def __init__(self, ledger_path: str | Path = "outputs/material_finality_ledger_v8.jsonl") -> None:
        self.ledger_path = Path(ledger_path)
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)

    def _read_commits(self) -> List[Dict[str, Any]]:
        if not self.ledger_path.exists():
            return []
        rows = []
        with self.ledger_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    rows.append(json.loads(line))
        return rows

    def last_commit_hash(self) -> str:
        commits = self._read_commits()
        return commits[-1]["commit_hash"] if commits else "GENESIS"

    def commit_certificate(self, certificate: MaterialCertificate, source_type: str = "EMK_MATERIAL_CERTIFICATE") -> FinalityCommit:
        prev_hash = self.last_commit_hash()
        proposed_state = {
            "material": certificate.material,
            "classification": certificate.classification,
            "certificate_hash": certificate.certificate_hash,
            "rank": certificate.rank,
            "priority": round(certificate.source_weighted_priority, 12),
        }
        proposed_state_hash = sha256_hex(proposed_state)
        proposal = {
            "source_type": source_type,
            "certificate_hash": certificate.certificate_hash,
            "payload_hash": certificate.payload_hash,
            "prev_commit_hash": prev_hash,
            "proposed_state_hash": proposed_state_hash,
        }
        proposal_hash = sha256_hex(proposal)
        entropy_delta = self.entropy_delta(certificate)
        body = {
            "ledger_version": LEDGER_VERSION,
            "source_type": source_type,
            "material": certificate.material,
            "certificate_hash": certificate.certificate_hash,
            "payload_hash": certificate.payload_hash,
            "prev_commit_hash": prev_hash,
            "proposed_state_hash": proposed_state_hash,
            "proposal_hash": proposal_hash,
            "entropy_delta": entropy_delta,
        }
        commit = FinalityCommit(
            LEDGER_VERSION,
            datetime.now(timezone.utc).isoformat(),
            source_type,
            certificate.material,
            certificate.certificate_hash,
            certificate.payload_hash,
            prev_hash,
            proposed_state_hash,
            proposal_hash,
            entropy_delta,
            sha256_hex(body),
        )
        with self.ledger_path.open("a", encoding="utf-8") as handle:
            handle.write(canonical_json(commit.to_dict()) + "\n")
        return commit

    @staticmethod
    def entropy_delta(certificate: MaterialCertificate) -> float:
        return float(1.0 + 0.10 * len(certificate.warning_flags) + 0.08 * len(certificate.missing_evidence)
                     + 0.25 * certificate.evidence_strength + 0.15 * certificate.source_weighted_priority)

    def verify(self) -> Dict[str, Any]:
        commits = self._read_commits()
        prev = "GENESIS"
        for index, commit in enumerate(commits):
            if commit.get("prev_commit_hash") != prev:
                return {"ok": False, "count": len(commits), "bad_index": index, "message": "previous commit hash mismatch"}
            body = {key: commit[key] for key in (
                "ledger_version", "source_type", "material", "certificate_hash", "payload_hash",
                "prev_commit_hash", "proposed_state_hash", "proposal_hash", "entropy_delta"
            )}
            if sha256_hex(body) != commit.get("commit_hash"):
                return {"ok": False, "count": len(commits), "bad_index": index, "message": "commit hash mismatch"}
            if float(commit.get("entropy_delta", 0.0)) <= 0.0:
                return {"ok": False, "count": len(commits), "bad_index": index, "message": "entropy delta is not positive"}
            prev = commit["commit_hash"]
        return {"ok": True, "count": len(commits), "head": prev, "message": "ledger verified"}

def write_certificates(certificates: List[MaterialCertificate], output_json: str | Path) -> None:
    path = Path(output_json)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps([c.to_dict() for c in certificates], indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")

def run_material_certificate_demo(certificates_json: str | Path = "outputs/material_certificates_v8.json", ledger_path: str | Path = "outputs/material_finality_ledger_v8.jsonl") -> Dict[str, Any]:
    audits = run_audit_report()
    factory = MaterialCertificateFactory()
    ledger = MaterialFinalityLedger(ledger_path)
    certificates = [factory.build_certificate(audit) for audit in audits]
    write_certificates(certificates, certificates_json)
    commits = [ledger.commit_certificate(certificate) for certificate in certificates]
    return {"certificates": certificates, "commits": commits, "verification": ledger.verify(),
            "certificates_json": str(certificates_json), "ledger_path": str(ledger_path)}

if __name__ == "__main__":
    result = run_material_certificate_demo()
    print(result["verification"])
