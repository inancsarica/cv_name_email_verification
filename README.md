# CV Name ↔ Email Verification Service

FastAPI-based microservice that verifies whether a CV email definitively belongs to the provided full name, following the strict rules in `cv_email_verifier_developer_manuel.md`.

## Components
- `EmailNameNormalizer`: deterministic name/email normalization and tokenization.
- `FuzzyFeatureExtractor`: fuzzy similarity signals using `fuzzywuzzy`.
- `AzureOpenAIDecisionClient`: strict JSON-only Azure OpenAI decision call using the system prompt in `cv_email_verifier_promt.md`.
- `DecisionPolicy`: hard vetoes and confidence caps to enforce zero false positives.
- `EmailVerificationService`: orchestrates the verification flow exposed via FastAPI.

## Running locally
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Environment
Set the Azure OpenAI values before running in a real environment:
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_VERSION` (optional, defaults to `2024-02-15-preview`)
- `AZURE_OPENAI_DEPLOYMENT`

## API
`POST /validate-cv-email`

Request body:
```json
{
  "full_name": "Mustafa İnanç Sarıca",
  "email": "inanc.sarica@company.com",
  "debug": false
}
```

Successful response example:
```json
{
  "email": "inanc.sarica@company.com",
  "decision": "pass",
  "confidence": 90,
  "reason": "LLM: clear direct name match in local-part. Policy: passed strict gates."
}
```
