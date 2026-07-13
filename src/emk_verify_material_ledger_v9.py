"""EMK Material Ledger Verifier v9."""
from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List
import argparse
import json

try:
    from emk_material_certificate_v8 import sha256_hex
except ImportError:
    import sys
    sys.path.append(str(Path(__file__).resolve().parent))
    from emk_material_certificate_v8 import sha256_hex

DEFAULT_LEDGER = "outputs/material_finality_ledger_v8.jsonl"

def read_ledger(path: str | Path) -> List[Dict[str, Any]]:
    ledger_path = Path(path)
    if not ledger_path.exists():
        raise FileNotFoundError(f"Ledger not found: {ledger_path}")
    commits: List[Dict[str, Any]] = []
    with ledger_path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                commits.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON at line {line_number}: {exc}") from exc
    return commits

def recompute_proposal_hash(commit: Dict[str, Any]) -> str:
    return sha256_hex({
        "source_type": commit["source_type"],
        "certificate_hash": commit["certificate_hash"],
        "payload_hash": commit["payload_hash"],
        "prev_commit_hash": commit["prev_commit_hash"],
        "proposed_state_hash": commit["proposed_state_hash"],
    })

def recompute_commit_hash(commit: Dict[str, Any]) -> str:
    return sha256_hex({
        "ledger_version": commit["ledger_version"],
        "source_type": commit["source_type"],
        "material": commit["material"],
        "certificate_hash": commit["certificate_hash"],
        "payload_hash": commit["payload_hash"],
        "prev_commit_hash": commit["prev_commit_hash"],
        "proposed_state_hash": commit["proposed_state_hash"],
        "proposal_hash": commit["proposal_hash"],
        "entropy_delta": commit["entropy_delta"],
    })

def verify_ledger(path: str | Path = DEFAULT_LEDGER) -> Dict[str, Any]:
    commits = read_ledger(path)
    if not commits:
        return {"ok": True, "count": 0, "head": "GENESIS", "message": "empty ledger"}
    prev = "GENESIS"
    materials = []
    for index, commit in enumerate(commits):
        materials.append(commit.get("material", "UNKNOWN"))
        if commit.get("prev_commit_hash") != prev:
            return {"ok": False, "count": len(commits), "bad_index": index,
                    "material": commit.get("material"), "message": "previous commit hash mismatch"}
        if recompute_proposal_hash(commit) != commit.get("proposal_hash"):
            return {"ok": False, "count": len(commits), "bad_index": index,
                    "material": commit.get("material"), "message": "proposal hash mismatch"}
        if recompute_commit_hash(commit) != commit.get("commit_hash"):
            return {"ok": False, "count": len(commits), "bad_index": index,
                    "material": commit.get("material"), "message": "commit hash mismatch"}
        if not commit.get("proposed_state_hash"):
            return {"ok": False, "count": len(commits), "bad_index": index,
                    "material": commit.get("material"), "message": "missing proposed state hash"}
        if float(commit.get("entropy_delta", 0.0)) <= 0.0:
            return {"ok": False, "count": len(commits), "bad_index": index,
                    "material": commit.get("material"), "message": "entropy delta is not positive"}
        prev = commit["commit_hash"]
    return {"ok": True, "count": len(commits), "head": prev,
            "materials": materials, "message": "ledger verified"}

def main() -> None:
    parser = argparse.ArgumentParser(description="Verify EMK material finality ledger")
    parser.add_argument("--ledger", default=DEFAULT_LEDGER)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = verify_ledger(args.ledger)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("EMK Material Ledger Verifier v9")
        print("Ledger:", args.ledger)
        print("OK:", result.get("ok"))
        print("Count:", result.get("count"))
        print("Head:", result.get("head"))
        print("Message:", result.get("message"))

if __name__ == "__main__":
    main()
