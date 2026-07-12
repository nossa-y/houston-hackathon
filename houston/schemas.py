"""Typed contracts: the verifier's verdict and the mission receipt."""
from __future__ import annotations

from pydantic import BaseModel, Field


class Claim(BaseModel):
    """One specific claim from the executor, checked against reality."""
    claim: str = Field(description="A specific factual claim the executor made")
    observed: str = Field(description="What the verifier actually observed on the live site")
    matches: bool = Field(description="Whether the claim matches the observation")


class Verdict(BaseModel):
    """The verifier's independent audit of the executor's claimed answer."""
    verified: bool = Field(description="True only if every material claim checks out against the live site")
    confidence: float = Field(ge=0, le=1, description="Verifier's confidence in this verdict")
    checked_claims: list[Claim] = Field(description="Each specific claim, what was observed, and whether it matches")
    divergence: str | None = Field(default=None, description="If not verified: exactly what the executor got wrong, in one sentence")
    diagnosis: str | None = Field(default=None, description="If not verified: a precise, actionable instruction that would fix the failure")


class ArbiterVerdict(BaseModel):
    """Resolves a dispute between the original attempt and the healed attempt."""
    winner: str = Field(description="One of: attempt_original | attempt_healed | neither")
    corrected_answer: str | None = Field(default=None, description="If neither is right, the correct answer as directly observed")
    resolved_facts: str = Field(description="What was directly observed on close inspection of the disputed items")
    confidence: float = Field(ge=0, le=1)


class Attempt(BaseModel):
    """One executor attempt and its audit."""
    n: int
    claimed_answer: str
    verdict: Verdict | None = None
    healed_with: str | None = None  # the diagnosis that was injected before this attempt
    elapsed_s: float = 0.0


class Receipt(BaseModel):
    """Hash-chained proof of what actually happened."""
    mission_id: str
    task: str
    executor_session_id: str
    executor_agent: str
    verifier_agent: str
    verifier_session_ids: list[str] = []
    attempts: list[Attempt] = []
    final_status: str = "unknown"  # verified | unverified | failed
    final_answer: str | None = None
    agent_view: str = ""
    verifier_views: list[str] = []
    local_audit: dict | None = None  # on-device Holo evidence check
    arbiter: ArbiterVerdict | None = None  # fired only when heal changed the answer
    arbiter_view: str | None = None
    public_replays: dict[str, str] | None = None  # share_session URLs, viewable by anyone
    started_at: str = ""
    finished_at: str = ""
    total_elapsed_s: float = 0.0
    prev_hash: str = ""
    hash: str = ""
