CV Name ↔ Email Verification Service (Strict, Zero-False-Positive)

Technologies
	•	Python 3.10+
	•	FastAPI (REST endpoint)
	•	Pydantic (request/response validation)
	•	Azure OpenAI (Chat Completions) via openai Python SDK (AzureOpenAI)
	•	fuzzywuzzy (+ optional python-Levenshtein for speed)
	•	Standard logging (logging), optional in-memory/LRU cache

⸻

Class Design

1) EmailNameNormalizer

Responsibility: deterministic normalization of name/email for feature extraction.
	•	Turkish character normalization (ç→c, ı→i, ş→s, etc.)
	•	Lowercasing, punctuation cleanup
	•	Extract email local-part, split tokens
	•	Detect generic/role emails (info/hr/admin/support/noreply/contact/etc.)

Methods
	•	normalize_text(text: str) -> str
	•	extract_local_part(email: str) -> str
	•	tokenize_local_part(local: str) -> list[str]
	•	tokenize_full_name(full_name: str) -> list[str]
	•	is_generic_email(local_tokens: list[str]) -> bool

⸻

2) FuzzyFeatureExtractor

Responsibility: compute fuzzy signals (no final decision).
	•	token_score_top2_avg
	•	string_score
	•	combined_score = 0.6*token_score + 0.4*string_score
	•	generic_email flag

Methods
	•	extract(full_name: str, email: str) -> dict  (returns all features)

⸻

3) AzureOpenAIDecisionClient

Responsibility: call Azure OpenAI and return strict JSON decision.
	•	Uses Azure OpenAI endpoint, deployment, API version.
	•	temperature=0
	•	Strict JSON parsing and basic schema validation.

Configuration (ENV)
	•	AZURE_OPENAI_API_KEY
	•	AZURE_OPENAI_ENDPOINT (e.g., https://<resource-name>.openai.azure.com)
	•	AZURE_OPENAI_API_VERSION (default 2024-02-15-preview unless overridden)
	•	AZURE_OPENAI_DEPLOYMENT (the deployed model name in Azure)

Methods
	•	decide(full_name: str, email: str, fuzzy_features: dict) -> dict
	•	Returns JSON with:
	•	decision: "pass"|"fail"
	•	confidence: int(0..100)
	•	reason: str
	•	signals: { fuzzy_combined_score, generic_email, llm_raw_confidence }

Critical enforcement
	•	Ignore any email-like text in model output; the model must not be allowed to alter/produce email.

⸻

4) DecisionPolicy

Responsibility: enforce “zero false positive” rules + calibrate confidence.

Hard veto
	•	If generic_email == true ⇒ force fail
	•	If fuzzy_combined_score < 70 ⇒ force fail

Confidence gates
	•	If LLM confidence < 85 ⇒ force fail (no email returned)

Confidence caps (after LLM)
	•	70–80 ⇒ cap 65
	•	80–85 ⇒ cap 80
	•	≥85 ⇒ cap 95
	•	Final confidence = min(llm_confidence, cap); if forced fail, confidence can be clamped ≤30.

Methods
	•	apply(llm_decision: dict, fuzzy_features: dict) -> dict
	•	Returns final {decision, confidence, reason, email_should_return}

⸻

5) EmailVerificationService

Responsibility: orchestrate full flow and produce final response.

Flow
	1.	Validate input (full_name, optional email)
	2.	If email is null/empty ⇒ return fail, confidence 0, email null
	3.	Extract fuzzy features
	4.	Call Azure OpenAI decision client with strict prompt
	5.	Apply DecisionPolicy (hard veto + confidence gates/caps)
	6.	Final email output rule
	•	If final decision is pass ⇒ return original input email
	•	Else ⇒ return null

Methods
	•	verify(full_name: str, email: Optional[str]) -> dict

⸻

API Contract (FastAPI)

Request

POST /validate-cv-email

{
  "full_name": "Mustafa İnanç Sarıca",
  "email": "inanc.sarica@company.com",
  "debug": false
}

Response

{
  "email": "inanc.sarica@company.com",
  "decision": "pass",
  "confidence": 90,
  "reason": "LLM: clear direct name match in local-part. Policy: passed strict gates."
}

Mandatory behavior
	•	decision=pass ⇒ email must equal the input email exactly
	•	decision=fail ⇒ email=null
	•	No email string may ever be generated/modified by LLM output.

⸻

Azure OpenAI Prompt (System Prompt)

Use the strict JSON-only prompt already approved (English), with:
	•	“pass means certain”
	•	“fail unless clear, strong, unambiguous”
	•	“do not modify/invent email”
	•	“generic emails almost always fail”
	•	Output only the defined JSON schema.
