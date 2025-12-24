"""Decision policy enforcing zero-false-positive constraints."""
from typing import Dict


class DecisionPolicy:
    """Apply gating and confidence caps on LLM output and fuzzy features."""

    def apply(self, llm_decision: Dict[str, object], fuzzy_features: Dict[str, object]) -> Dict[str, object]:
        signals = llm_decision.get("signals", {}) if isinstance(llm_decision.get("signals"), dict) else {}
        generic_email = bool(signals.get("generic_email", fuzzy_features.get("generic_email", False)))
        fuzzy_combined = float(signals.get("fuzzy_combined_score", fuzzy_features.get("fuzzy_combined_score", 0)))
        llm_confidence = float(signals.get("llm_raw_confidence", llm_decision.get("confidence", 0)))

        decision = llm_decision.get("decision", "fail")
        reason_parts = [llm_decision.get("reason", "No reason provided")] if llm_decision.get("reason") else []
        forced_fail = False

        if generic_email:
            forced_fail = True
            reason_parts.append("Policy: generic email veto")
        if fuzzy_combined < 70:
            forced_fail = True
            reason_parts.append("Policy: fuzzy score below threshold")
        if llm_confidence < 85:
            forced_fail = True
            reason_parts.append("Policy: LLM confidence below gate")

        capped_confidence = self._cap_confidence(llm_confidence)
        final_confidence = min(llm_confidence, capped_confidence)

        if forced_fail:
            decision = "fail"
            final_confidence = min(final_confidence, 30)

        reason = "; ".join(reason_parts) if reason_parts else "Policy applied"
        return {
            "decision": decision,
            "confidence": int(round(final_confidence)),
            "reason": reason,
            "signals": {
                "fuzzy_combined_score": round(fuzzy_combined, 2),
                "generic_email": generic_email,
                "llm_raw_confidence": round(llm_confidence, 2),
            },
        }

    @staticmethod
    def _cap_confidence(raw_confidence: float) -> float:
        if raw_confidence < 70:
            return raw_confidence
        if 70 <= raw_confidence < 80:
            return 65
        if 80 <= raw_confidence < 85:
            return 80
        return 95
