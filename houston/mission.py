"""Mission orchestration: ATTEMPT -> AUDIT -> HEAL -> PROOF.

One Mission = one executor session (kept alive and steerable) + one fresh verifier
session per audit + a hash-chained receipt at the end.
"""
from __future__ import annotations

import time
import uuid
from typing import Callable

from hai_agents import Client

from . import config
from .prompts import (
    ARBITER_PROMPT,
    EXECUTOR_PREAMBLE,
    HEAL_PROMPT,
    VERIFIER_PROMPT,
    format_observations,
)
from .receipts import finalize_receipt
from .schemas import ArbiterVerdict, Attempt, Receipt, Verdict

Emit = Callable[[str, dict], None]


def _noop_emit(kind: str, data: dict) -> None:  # pragma: no cover
    pass


class Mission:
    def __init__(self, task: str, emit: Emit | None = None, max_heals: int | None = None,
                 local_audit: bool = True, mission_id: str | None = None):
        self.task = task
        self.emit: Emit = emit or _noop_emit
        self.max_heals = config.MAX_HEALS if max_heals is None else max_heals
        self.local_audit_enabled = local_audit
        self.client = Client(api_key=config.HAI_API_KEY)
        self.mission_id = mission_id or uuid.uuid4().hex[:12]
        self.receipt = Receipt(
            mission_id=self.mission_id,
            task=task,
            executor_session_id="",
            executor_agent=config.EXECUTOR_AGENT,
            verifier_agent=config.VERIFIER_AGENT,
            started_at=time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        )
        self._executor = None

    # ---------- phases ----------

    def _start_executor(self) -> None:
        self.emit("phase", {"phase": "attempt", "n": 1})
        self._executor = self.client.start_session(
            agent=config.EXECUTOR_AGENT,
            messages=EXECUTOR_PREAMBLE.format(task=self.task),
            idle_timeout_s=config.EXECUTOR_IDLE_TIMEOUT_S,
        )
        sid = str(self._executor.get().id) if hasattr(self._executor, "get") else str(self._executor.id)
        self.receipt.executor_session_id = sid
        self.receipt.agent_view = config.agent_view_url(sid)
        self.emit("executor_started", {"session_id": sid, "agent_view": self.receipt.agent_view})

    def _consume_until_settled(self) -> str:
        """Stream executor events, emit milestones, return the claimed answer text."""
        answer_text = None
        step = 0
        try:
            for event in self._executor.stream():
                kind = type(event).__name__
                data = getattr(event, "data", None)
                if kind == "RequestStartEvent" or kind == "RequestStartDispatchedEvent":
                    step += 1
                    if step % 3 == 1:
                        self.emit("milestone", {"text": f"working... step {step}", "step": step})
                elif kind == "AgentEvent":
                    inner = type(data).__name__ if data is not None else ""
                    payload = getattr(data, "data", None)
                    if "Answer" in inner:
                        ans = getattr(payload, "answer", None) or getattr(data, "answer", None)
                        if ans is not None:
                            answer_text = str(getattr(ans, "content", ans))
                    elif "Message" in inner:
                        content = getattr(payload, "content", None)
                        if content:
                            self.emit("agent_message", {"text": str(content)[:200]})
                elif kind == "AgentCompletionEvent":
                    reason = getattr(data, "reason", None)
                    self.emit("milestone", {"text": f"executor settled ({reason})", "step": step})
                elif kind == "AgentErrorEvent":
                    self.emit("milestone", {"text": "executor error event", "step": step})
        except Exception as e:  # stream ends when session settles; some SDK versions raise StopIteration wrappers
            self.emit("debug", {"stream_end": repr(e)[:200]})

        if answer_text is None:
            # Fallback: read the answer from session changes
            try:
                changes = self._executor.changes()
                ans = getattr(changes, "answer", None)
                if ans is not None:
                    answer_text = str(getattr(ans, "content", ans))
            except Exception as e:
                self.emit("debug", {"changes_error": repr(e)[:200]})
        return answer_text or "(no answer produced)"

    def _verify(self, claimed_answer: str) -> Verdict:
        self.emit("phase", {"phase": "audit"})
        handle = self.client.start_session(
            agent=config.VERIFIER_AGENT,
            messages=VERIFIER_PROMPT.format(task=self.task, claimed_answer=claimed_answer),
            answer_schema=Verdict,
        )
        vid = str(handle.get().id)
        self.receipt.verifier_session_ids.append(vid)
        self.receipt.verifier_views.append(config.agent_view_url(vid))
        self.emit("verifier_started", {"session_id": vid, "agent_view": self.receipt.verifier_views[-1]})

        verdict: Verdict | None = None
        forced = False
        try:
            result = handle.wait_for_completion(timeout_seconds=config.VERIFIER_BUDGET_S)
            verdict = result.answer
        except TimeoutError:
            # Budget exceeded: tell the verifier to commit to a verdict now.
            forced = True
            self.emit("milestone", {"text": "verifier over budget - forcing a verdict now"})
            try:
                handle.force_answer()
                result = handle.wait_for_completion(timeout_seconds=config.VERIFIER_GRACE_S)
                verdict = result.answer
            except Exception as e:
                self.emit("debug", {"force_answer_failed": repr(e)[:200]})
        except Exception as e:
            self.emit("debug", {"verifier_error": repr(e)[:200]})
        finally:
            try:
                if verdict is None:
                    handle.cancel()
            except Exception:
                pass

        if verdict is None:
            verdict = Verdict(
                verified=False,
                confidence=0.0,
                checked_claims=[],
                divergence="verification inconclusive: the audit could not settle within budget",
                diagnosis=None,  # None marks inconclusive - the arc will not heal on this
            )
        if forced and verdict.confidence > 0.85:
            verdict.confidence = 0.85  # a forced verdict is never fully confident
        self.emit("verdict", {
            "verified": verdict.verified,
            "confidence": verdict.confidence,
            "divergence": verdict.divergence,
            "diagnosis": verdict.diagnosis,
            "claims": [c.model_dump() for c in verdict.checked_claims],
            "verifier_view": self.receipt.verifier_views[-1] if self.receipt.verifier_views else "",
        })
        return verdict

    def _heal(self, verdict: Verdict) -> None:
        self.emit("phase", {"phase": "heal"})
        msg = HEAL_PROMPT.format(
            divergence=verdict.divergence or "material claims did not match the live site",
            observations=format_observations(verdict),
            diagnosis=verdict.diagnosis or "redo the task and re-check every constraint",
        )
        self.emit("healing", {"diagnosis": verdict.diagnosis, "message": msg})
        self._executor.send_message({"type": "user_message", "message": msg})

    def _arbitrate(self) -> None:
        """When healing CHANGED the answer, neither result can be trusted blindly:
        a wrong verifier can gaslight a correct executor. Settle the delta by
        close inspection of only the disputed facts."""
        first = self.receipt.attempts[0]
        last = self.receipt.attempts[-1]
        divergence = first.verdict.divergence if first.verdict else "unknown"
        self.emit("phase", {"phase": "arbiter"})
        handle = self.client.start_session(
            agent=config.VERIFIER_AGENT,
            messages=ARBITER_PROMPT.format(
                task=self.task,
                answer_a=first.claimed_answer,
                answer_b=last.claimed_answer,
                divergence=divergence,
            ),
            answer_schema=ArbiterVerdict,
        )
        aid = str(handle.get().id)
        self.receipt.arbiter_view = config.agent_view_url(aid)
        self.emit("arbiter_started", {"session_id": aid, "agent_view": self.receipt.arbiter_view})
        try:
            result = handle.wait_for_completion(timeout_seconds=config.VERIFIER_BUDGET_S)
        except TimeoutError:
            handle.force_answer()
            result = handle.wait_for_completion(timeout_seconds=config.VERIFIER_GRACE_S)
        arb: ArbiterVerdict = result.answer
        self.receipt.arbiter = arb
        self.emit("arbiter_verdict", {
            "winner": arb.winner,
            "resolved_facts": arb.resolved_facts[:400],
            "confidence": arb.confidence,
            "arbiter_view": self.receipt.arbiter_view,
        })
        if arb.winner == "attempt_original":
            self.receipt.final_answer = first.claimed_answer
            self.receipt.final_status = "verified-by-arbiter (original answer restored)"
        elif arb.winner == "attempt_healed":
            self.receipt.final_answer = last.claimed_answer
            self.receipt.final_status = "verified-by-arbiter"
        else:
            self.receipt.final_answer = arb.corrected_answer or last.claimed_answer
            self.receipt.final_status = "corrected-by-arbiter"

    def _local_audit(self, verdict: Verdict) -> None:
        if not self.local_audit_enabled:
            return
        try:
            from .local_audit import audit_verdict
            report = audit_verdict(self, verdict)
            if report:
                self.receipt.local_audit = report
                self.emit("local_audit", report)
        except Exception as e:
            self.emit("debug", {"local_audit_skipped": repr(e)[:200]})

    # ---------- the arc ----------

    def run(self) -> Receipt:
        t0 = time.time()
        self.emit("mission_started", {"mission_id": self.mission_id, "task": self.task})
        verdict: Verdict | None = None
        try:
            self._start_executor()
            healed_with = None
            for n in range(1, self.max_heals + 2):  # attempt 1 + up to max_heals healed attempts
                a0 = time.time()
                claimed = self._consume_until_settled()
                self.emit("claimed", {"n": n, "answer": claimed})
                verdict = self._verify(claimed)
                self.receipt.attempts.append(Attempt(
                    n=n, claimed_answer=claimed, verdict=verdict,
                    healed_with=healed_with, elapsed_s=round(time.time() - a0, 1),
                ))
                if verdict.verified:
                    break
                if verdict.diagnosis is None:
                    break  # inconclusive audit: do not heal on a hunch
                if n <= self.max_heals:
                    healed_with = verdict.diagnosis
                    self._heal(verdict)
                else:
                    break

            if verdict and verdict.verified:
                self.receipt.final_status = "verified"
            elif verdict and verdict.diagnosis is None and not verdict.checked_claims:
                self.receipt.final_status = "inconclusive"
            else:
                self.receipt.final_status = "unverified"
            self.receipt.final_answer = (
                self.receipt.attempts[-1].claimed_answer if self.receipt.attempts else None
            )
            # Dispute rule: healing changed the substance of the answer -> arbiter.
            if (
                self.receipt.final_status == "verified"
                and len(self.receipt.attempts) > 1
                and self.receipt.attempts[0].claimed_answer.strip()
                != self.receipt.attempts[-1].claimed_answer.strip()
            ):
                try:
                    self._arbitrate()
                except Exception as e:
                    self.emit("debug", {"arbiter_failed": repr(e)[:200]})
            if verdict and verdict.verified:
                self._local_audit(verdict)
        except Exception as e:
            self.receipt.final_status = "error"
            self.emit("mission_error", {"error": repr(e)[:300]})
        finally:
            # Never leave an executor idling against the concurrency quota.
            try:
                if self._executor is not None:
                    self._executor.cancel()
            except Exception:
                pass
            # Public replays: anyone (a judge) can scrub these without logging in.
            try:
                from .share import share_receipt_sessions
                links = share_receipt_sessions(self.receipt)
                if links:
                    self.receipt.public_replays = links
            except Exception as e:
                self.emit("debug", {"share_failed": repr(e)[:150]})
            self.receipt.total_elapsed_s = round(time.time() - t0, 1)
            self.receipt.finished_at = time.strftime("%Y-%m-%dT%H:%M:%S%z")
            finalize_receipt(self.receipt)
            self.emit("receipt", self.receipt.model_dump())
        return self.receipt
