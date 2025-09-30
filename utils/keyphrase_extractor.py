"""
Lightweight keyphrase extraction utility.

Provides simple but effective keyword extraction for maintaining topic fidelity
across research pipeline phases without requiring external NLP libraries.
"""

import re
from typing import List, Set


class KeyphraseExtractor:
    """Lightweight keyphrase extractor for research topics."""

    def __init__(self):
        # Common stop words to filter out
        self.stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'were', 'will', 'with', 'what', 'when', 'where',
            'who', 'why', 'how', 'can', 'could', 'should', 'would', 'may',
            'might', 'must', 'shall', 'do', 'does', 'did', 'have', 'had',
            'this', 'these', 'those', 'they', 'them', 'their', 'there'
        }

        # Terms that are too generic for research topics
        self.generic_terms = {
            'research', 'study', 'studies', 'analysis', 'evidence', 'data',
            'results', 'findings', 'report', 'paper', 'article', 'review',
            'current', 'recent', 'new', 'latest', 'state', 'topic', 'subject',
            'field', 'area', 'domain', 'approach', 'method', 'methodology',
            'implications', 'perspectives', 'viewpoints', 'arguments',
            'limitations', 'gaps', 'knowledge', 'understanding', 'conclusion'
        }

    def extract_keyphrases(self, text: str, max_keyphrases: int = 4) -> List[str]:
        """
        Extract meaningful keyphrases from text.

        Args:
            text: Input text to extract keyphrases from
            max_keyphrases: Maximum number of keyphrases to return

        Returns:
            List of extracted keyphrases, ordered by importance
        """
        if not text:
            return []

        # Normalize text
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)  # Remove punctuation
        text = re.sub(r'\s+', ' ', text).strip()  # Normalize whitespace

        # Extract potential keyphrases (1-3 word phrases)
        candidates = self._extract_candidates(text)

        # Score and rank candidates
        scored_candidates = self._score_candidates(candidates, text)

        # Return top candidates
        return [phrase for phrase, _ in scored_candidates[:max_keyphrases]]

    def _extract_candidates(self, text: str) -> Set[str]:
        """Extract candidate keyphrases from text."""
        candidates = set()
        words = text.split()

        # Single words
        for word in words:
            if self._is_valid_word(word):
                candidates.add(word)

        # Two-word phrases
        for i in range(len(words) - 1):
            phrase = f"{words[i]} {words[i+1]}"
            if self._is_valid_phrase(phrase):
                candidates.add(phrase)

        # Three-word phrases (for compound terms)
        for i in range(len(words) - 2):
            phrase = f"{words[i]} {words[i+1]} {words[i+2]}"
            if self._is_valid_phrase(phrase):
                candidates.add(phrase)

        return candidates

    def _is_valid_word(self, word: str) -> bool:
        """Check if a word is valid for keyphrase extraction."""
        return (
            len(word) >= 3 and
            word not in self.stop_words and
            word not in self.generic_terms and
            word.isalpha()  # Only alphabetic characters
        )

    def _is_valid_phrase(self, phrase: str) -> bool:
        """Check if a phrase is valid for keyphrase extraction."""
        words = phrase.split()

        # Must contain at least one valid word
        if not any(self._is_valid_word(word) for word in words):
            return False

        # Don't include phrases that are all generic terms
        if all(word in self.generic_terms or word in self.stop_words for word in words):
            return False

        return True

    def _score_candidates(self, candidates: Set[str], text: str) -> List[tuple]:
        """Score and rank candidate keyphrases."""
        scored = []
        words = text.split()
        total_words = len(words)

        for candidate in candidates:
            score = self._calculate_score(candidate, words, total_words)
            if score > 0:
                scored.append((candidate, score))

        # Sort by score (descending) and then alphabetically for stability
        return sorted(scored, key=lambda x: (-x[1], x[0]))

    def _calculate_score(self, candidate: str, words: List[str], total_words: int) -> float:
        """Calculate importance score for a candidate keyphrase."""
        candidate_words = candidate.split()

        # Frequency score
        frequency = sum(1 for word in words if word in candidate_words)
        freq_score = frequency / total_words if total_words > 0 else 0

        # Length bonus (prefer 2-word phrases over single words, but not excessively long)
        if len(candidate_words) == 1:
            length_bonus = 0.8  # Good for important single terms
        elif len(candidate_words) == 2:
            length_bonus = 1.0  # Best for specific concepts
        else:
            length_bonus = 0.6  # Slightly lower for longer phrases

        # Position bonus (terms appearing early are often more important)
        position_bonus = 0
        first_occurrence = None
        for i, word in enumerate(words):
            if word in candidate_words:
                first_occurrence = i
                break

        if first_occurrence is not None:
            # Higher score for terms appearing in first third of text
            if first_occurrence < total_words / 3:
                position_bonus = 0.4

        # Meaningful compound term bonus
        meaningful_compounds = [
            'social media', 'mental health', 'artificial intelligence', 'machine learning',
            'climate change', 'data science', 'deep learning', 'natural language',
            'computer vision', 'public health', 'social networking', 'data analysis',
            'renewable energy', 'environmental science', 'cyber security', 'blockchain technology',
            'quantum computing', 'virtual reality', 'augmented reality', 'medical research',
            'educational technology', 'financial technology', 'space exploration'
        ]

        compound_bonus = 0
        if candidate in meaningful_compounds:
            compound_bonus = 1.0  # Strong bonus for recognized compound terms

        # Domain-specific term bonus
        domain_terms = [
            'teenagers', 'adolescents', 'students', 'youth', 'children',
            'depression', 'anxiety', 'wellbeing', 'psychology', 'behavior',
            'research', 'study', 'analysis', 'education', 'health',
            'technology', 'digital', 'online', 'internet', 'mobile'
        ]

        domain_bonus = 0
        for word in candidate_words:
            if word in domain_terms:
                domain_bonus += 0.3

        # Penalty for generic connecting phrases
        generic_patterns = ['of', 'the', 'and', 'to', 'for', 'in', 'on', 'at', 'by', 'with']
        generic_penalty = 0
        if len(candidate_words) >= 2:
            generic_word_count = sum(1 for word in candidate_words if word in generic_patterns)
            generic_penalty = generic_word_count * 0.5  # Penalty for each generic word

        return freq_score + length_bonus + position_bonus + compound_bonus + domain_bonus - generic_penalty

    def extract_topic_keywords(self, objective: str) -> List[str]:
        """
        Extract topic-specific keywords from research objective.

        Optimized for research objectives and queries.

        Args:
            objective: Research objective or query string

        Returns:
            List of 2-4 most relevant topic keywords
        """
        return self.extract_keyphrases(objective, max_keyphrases=4)


# Global instance for convenience
_extractor = KeyphraseExtractor()


def extract_topic_keywords(text: str) -> List[str]:
    """
    Convenience function to extract topic keywords.

    Args:
        text: Text to extract keywords from

    Returns:
        List of relevant topic keywords
    """
    return _extractor.extract_topic_keywords(text)