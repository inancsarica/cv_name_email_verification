"""Azure OpenAI decision client for strict JSON decisions."""
import json
from typing import Dict, Optional

from openai import AzureOpenAI

from .config import get_settings

PROMPT_PATH = "cv_email_verifier_promt.md"


class AzureOpenAIDecisionClient:
    """Call Azure OpenAI with strict JSON schema enforcement."""

    def __init__(self, client: Optional[AzureOpenAI] = None, prompt: Optional[str] = None):
        self.settings = get_settings()
        self.prompt = prompt or self._load_prompt()
        self.client = client or self._build_client()

    def _build_client(self) -> Optional[AzureOpenAI]:
        if not self.settings:
            return None
        return AzureOpenAI(
            api_key=self.settings.azure_openai_api_key,
            api_version=self.settings.azure_openai_api_version,
            azure_endpoint=str(self.settings.azure_openai_endpoint),
        )

    @staticmethod
    def _load_prompt() -> str:
        from pathlib import Path

        prompt_file = Path(__file__).resolve().parent.parent / PROMPT_PATH
        with open(prompt_file, "r", encoding="utf-8") as fh:
            return fh.read()

    def decide(self, full_name: str, email: str, fuzzy_features: Dict[str, object]) -> Dict[str, object]:
        if not self.client:
            return self._fallback_decision(fuzzy_features)

        response = self.client.chat.completions.create(
            model=self.settings.azure_openai_deployment,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": self.prompt},
                {"role": "user", "content": json.dumps({
                    "full_name": full_name,
                    "email": email,
                    "fuzzy_features": fuzzy_features,
                })},
            ],
        )

        raw_content = response.choices[0].message.content
        parsed = self._parse_json(raw_content)
        return self._normalize_decision(parsed, fuzzy_features)

    @staticmethod
    def _parse_json(raw: str) -> Dict[str, object]:
        parsed = json.loads(raw)
        if not isinstance(parsed, dict):
            raise ValueError("Model output must be a JSON object")
        return parsed

    @staticmethod
    def _normalize_decision(model_decision: Dict[str, object], fuzzy_features: Dict[str, object]) -> Dict[str, object]:
        signals = model_decision.get("signals", {}) if isinstance(model_decision.get("signals"), dict) else {}
        return {
            "decision": model_decision.get("decision", "fail"),
            "confidence": int(model_decision.get("confidence", 0)),
            "reason": model_decision.get("reason", "Model decision unavailable"),
            "signals": {
                "fuzzy_combined_score": float(signals.get("fuzzy_combined_score", fuzzy_features.get("fuzzy_combined_score", 0))),
                "generic_email": bool(signals.get("generic_email", fuzzy_features.get("generic_email", False))),
                "llm_raw_confidence": float(signals.get("llm_raw_confidence", model_decision.get("confidence", 0))),
            },
        }

    @staticmethod
    def _fallback_decision(fuzzy_features: Dict[str, object]) -> Dict[str, object]:
        return {
            "decision": "fail",
            "confidence": 0,
            "reason": "Azure OpenAI client not configured",
            "signals": {
                "fuzzy_combined_score": float(fuzzy_features.get("fuzzy_combined_score", 0)),
                "generic_email": bool(fuzzy_features.get("generic_email", False)),
                "llm_raw_confidence": 0,
            },
        }
