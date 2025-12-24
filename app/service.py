"""Email verification service orchestrating all components."""
from typing import Dict, Optional

from .azure_client import AzureOpenAIDecisionClient
from .fuzzy import FuzzyFeatureExtractor
from .policy import DecisionPolicy


class EmailVerificationService:
    """High-level email verification orchestrator."""

    def __init__(
        self,
        fuzzy_extractor: Optional[FuzzyFeatureExtractor] = None,
        decision_client: Optional[AzureOpenAIDecisionClient] = None,
        policy: Optional[DecisionPolicy] = None,
    ) -> None:
        self.fuzzy_extractor = fuzzy_extractor or FuzzyFeatureExtractor()
        self.decision_client = decision_client or AzureOpenAIDecisionClient()
        self.policy = policy or DecisionPolicy()

    def verify(self, full_name: str, email: Optional[str], *, debug: bool = False) -> Dict[str, object]:
        if not email or not email.strip():
            return {
                "email": None,
                "decision": "fail",
                "confidence": 0,
                "reason": "Missing email input",
            }

        fuzzy_features = self.fuzzy_extractor.extract(full_name, email)
        llm_decision = self.decision_client.decide(full_name, email, fuzzy_features)
        final_decision = self.policy.apply(llm_decision, fuzzy_features)

        response = {
            "email": email if final_decision["decision"] == "pass" else None,
            "decision": final_decision["decision"],
            "confidence": final_decision["confidence"],
            "reason": final_decision["reason"],
        }

        if debug:
            response["debug"] = {
                "fuzzy_features": fuzzy_features,
                "llm_decision": llm_decision,
                "policy_decision": final_decision,
            }

        return response
