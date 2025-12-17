from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class CallerIdentity:
    actor: str                 # e.g. GitHub login or 'local-test'
    repo: str                  # e.g. 'local/mcp-test'
    pr_number: Optional[int]   # optional
    run_id: Optional[str]      # optional
    change_id: Optional[str]   # optional
    trace_id: Optional[str]    # optional

    @classmethod
    def from_ctx_params(cls, params: Dict[str, Any]) -> "CallerIdentity":
        meta = params.get("_metadata", {})
        return cls(
            actor=meta.get("actor", "local-test"),
            repo=meta.get("repo", "local/mcp-test"),
            pr_number=meta.get("pr_number"),
            run_id=meta.get("run_id"),
            change_id=meta.get("change_id"),
            trace_id=meta.get("trace_id"),
        )
