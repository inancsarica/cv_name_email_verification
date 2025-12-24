"""Normalization utilities for names and emails."""
import re
import unicodedata
from typing import List

TURKISH_CHAR_MAP = str.maketrans(
    {
        "ç": "c",
        "ğ": "g",
        "ı": "i",
        "ö": "o",
        "ş": "s",
        "ü": "u",
        "Ç": "c",
        "Ğ": "g",
        "İ": "i",
        "Ö": "o",
        "Ş": "s",
        "Ü": "u",
    }
)

GENERIC_EMAIL_TOKENS = {
    "info",
    "hr",
    "admin",
    "support",
    "help",
    "contact",
    "noreply",
    "no-reply",
    "sales",
    "career",
    "careers",
    "jobs",
    "team",
}


class EmailNameNormalizer:
    """Deterministic normalization of names and emails."""

    @staticmethod
    def normalize_text(text: str) -> str:
        normalized = unicodedata.normalize("NFKD", text).translate(TURKISH_CHAR_MAP)
        normalized = normalized.encode("ascii", "ignore").decode("ascii")
        normalized = normalized.lower()
        normalized = re.sub(r"[^a-z0-9\s]", " ", normalized)
        normalized = re.sub(r"\s+", " ", normalized).strip()
        return normalized

    @staticmethod
    def extract_local_part(email: str) -> str:
        return email.split("@", 1)[0].strip()

    @staticmethod
    def tokenize_local_part(local: str) -> List[str]:
        local = EmailNameNormalizer.normalize_text(local)
        tokens = re.split(r"[\._\-\+]+", local)
        tokens = [tok for tok in tokens if tok]
        return tokens

    @staticmethod
    def tokenize_full_name(full_name: str) -> List[str]:
        normalized = EmailNameNormalizer.normalize_text(full_name)
        tokens = [token for token in normalized.split(" ") if token]
        return tokens

    @staticmethod
    def is_generic_email(local_tokens: List[str]) -> bool:
        return any(tok in GENERIC_EMAIL_TOKENS for tok in local_tokens)
