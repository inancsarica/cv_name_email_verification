"""Fuzzy feature extraction utilities."""
from typing import Dict

from fuzzywuzzy import fuzz

from .normalizer import EmailNameNormalizer


class FuzzyFeatureExtractor:
    """Compute fuzzy signals between full name and email local-part tokens."""

    def extract(self, full_name: str, email: str) -> Dict[str, object]:
        local_part = EmailNameNormalizer.extract_local_part(email)
        local_tokens = EmailNameNormalizer.tokenize_local_part(local_part)
        name_tokens = EmailNameNormalizer.tokenize_full_name(full_name)

        token_pairs = [(lt, nt) for lt in local_tokens for nt in name_tokens]
        token_scores = [fuzz.ratio(lt, nt) for lt, nt in token_pairs] if token_pairs else [0]
        top_two = sorted(token_scores, reverse=True)[:2]
        token_score_top2_avg = sum(top_two) / len(top_two)

        string_score = fuzz.ratio(
            EmailNameNormalizer.normalize_text(local_part),
            EmailNameNormalizer.normalize_text(" ".join(name_tokens)),
        )

        generic_email = EmailNameNormalizer.is_generic_email(local_tokens)
        combined_score = 0.6 * token_score_top2_avg + 0.4 * string_score

        return {
            "token_score_top2_avg": round(token_score_top2_avg, 2),
            "string_score": round(string_score, 2),
            "fuzzy_combined_score": round(combined_score, 2),
            "generic_email": generic_email,
            "local_tokens": local_tokens,
            "name_tokens": name_tokens,
        }
