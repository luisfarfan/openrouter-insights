import re
import logging
from typing import List, Optional, Tuple
from rapidfuzz import fuzz

logger = logging.getLogger(__name__)

class MatchingEngine:
    """
    Domain Service: Reconciles model identifiers between data sources.
    Uses an 85% threshold for relaxed but safe dynamic matching.
    """

    def __init__(self, threshold: float = 85.0):
        self.threshold = threshold

    def normalize(self, text: str) -> str:
        """
        Tier 1: Normalization Rules.
        1. Strip provider (e.g., openai/).
        2. Lowercase.
        3. Replace non-alphanumeric with dashes.
        """
        if not text:
            return ""
            
        # Remove provider (everything before the last /)
        if "/" in text:
            text = text.split("/")[-1]
        
        text = text.lower()
        # Replace complex characters with dashes
        text = re.sub(r'[^a-z0-9]', '-', text)
        # Collapse multiple dashes
        text = re.sub(r'-+', '-', text)
        return text.strip('-')

    def find_match(self, target_id: str, candidates: List[str]) -> Tuple[Optional[str], float]:
        """
        Finds the best match for a target_id in a list of candidates.
        Returns (matched_id, confidence_score).
        """
        if not target_id or not candidates:
            return None, 0.0

        # --- Tier 1: Exact Normalized Match ---
        norm_target = self.normalize(target_id)
        
        # Optimization: cache normalized candidates
        norm_candidates = {self.normalize(c): c for c in candidates}
        
        if norm_target in norm_candidates:
            return norm_candidates[norm_target], 100.0

        # --- Tier 2: Fuzzy Matching (Levenshtein) ---
        best_match = None
        best_score = 0.0

        for candidate in candidates:
            norm_candidate = self.normalize(candidate)
            # Token Set Ratio is ideal for comparing 'gpt-4o' with 'openai-gpt4o'
            score = fuzz.token_set_ratio(norm_target, norm_candidate)
            
            if score > best_score:
                best_score = score
                best_match = candidate

        if best_score >= self.threshold:
            # Prevent false positives for very short names if score is not perfect
            if len(norm_target) < 5 and best_score < 95.0:
                return None, best_score
                
            return best_match, best_score
            
        return None, best_score
