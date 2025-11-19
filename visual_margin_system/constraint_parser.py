"""
Constraint Parser

Extracts structural constraints from natural language prompts.
"""

import re
from typing import Dict, Any, Optional


class ConstraintParser:
    """Parses natural language to extract structural constraints."""

    # Word-to-number mapping
    WORD_TO_NUM = {
        'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
        'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
        'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14, 'fifteen': 15,
        'sixteen': 16, 'seventeen': 17, 'eighteen': 18, 'nineteen': 19, 'twenty': 20,
    }

    def parse(self, prompt: str) -> Dict[str, Any]:
        """
        Extract structural constraints from natural language prompts.

        Args:
            prompt: Natural language prompt

        Returns:
            Dictionary of parsed constraints

        Examples:
            - "4 lines of text" -> {"lines": {"target": 4, "tolerance": 0}}
            - "3 paragraphs" -> {"paragraphs": {"target": 3, "tolerance": 0}}
            - "under 100 words" -> {"words": {"max": 100}}
            - "between 500-1000 characters" -> {"chars": {"min": 500, "max": 1000}}
        """
        prompt_lower = prompt.lower()
        constraints = {}

        # Parse line requirements
        if line_match := self._extract_line_constraint(prompt_lower):
            constraints['lines'] = line_match

        # Parse paragraph requirements
        if para_match := self._extract_paragraph_constraint(prompt_lower):
            constraints['paragraphs'] = para_match

        # Parse word count requirements
        if word_match := self._extract_word_constraint(prompt_lower):
            constraints['words'] = word_match

        # Parse character count requirements
        if char_match := self._extract_char_constraint(prompt_lower):
            constraints['chars'] = char_match

        # Parse words per line requirements
        if wpl_match := self._extract_words_per_line_constraint(prompt_lower):
            constraints['words_per_line'] = wpl_match

        # Parse words per paragraph requirements
        if wpp_match := self._extract_words_per_paragraph_constraint(prompt_lower):
            constraints['words_per_paragraph'] = wpp_match

        return constraints

    def _extract_number(self, text: str) -> Optional[int]:
        """
        Extract a number from text, handling both digits and word forms.

        Args:
            text: Text containing a number

        Returns:
            Integer value or None
        """
        # Try digit form first
        if text.isdigit():
            return int(text)

        # Try word form
        if text in self.WORD_TO_NUM:
            return self.WORD_TO_NUM[text]

        return None

    def _extract_line_constraint(self, prompt: str) -> Optional[Dict[str, Any]]:
        """
        Parse patterns like '4 lines', 'four lines', 'N lines'.

        Args:
            prompt: Lowercase prompt text

        Returns:
            Constraint specification or None
        """
        patterns = [
            # Exact count: "4 lines", "four lines"
            r'(?:exactly\s+)?(\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s+lines?',
            # "a 4-line poem"
            r'a\s+(\d+)-line',
        ]

        for pattern in patterns:
            if match := re.search(pattern, prompt):
                num_text = match.group(1)
                num = self._extract_number(num_text)
                if num:
                    return {"target": num, "tolerance": 0}

        return None

    def _extract_paragraph_constraint(self, prompt: str) -> Optional[Dict[str, Any]]:
        """
        Parse patterns like '3 paragraphs', 'several paragraphs'.

        Args:
            prompt: Lowercase prompt text

        Returns:
            Constraint specification or None
        """
        patterns = [
            # Exact count: "3 paragraphs", "three paragraphs"
            r'(?:exactly\s+)?(\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s+paragraphs?',
        ]

        for pattern in patterns:
            if match := re.search(pattern, prompt):
                num_text = match.group(1)
                num = self._extract_number(num_text)
                if num:
                    return {"target": num, "tolerance": 0}

        return None

    def _extract_word_constraint(self, prompt: str) -> Optional[Dict[str, Any]]:
        """
        Parse patterns like 'under 100 words', '50-75 words', 'about 200 words'.

        Args:
            prompt: Lowercase prompt text

        Returns:
            Constraint specification or None
        """
        # Range: "between 100 and 200 words", "100-200 words"
        if match := re.search(r'(?:between\s+)?(\d+)\s*(?:and|-)\s*(\d+)\s+words?', prompt):
            min_words = int(match.group(1))
            max_words = int(match.group(2))
            return {"min": min_words, "max": max_words}

        # Maximum: "under 100 words", "less than 100 words", "max 100 words"
        if match := re.search(r'(?:under|less than|max|maximum|no more than|at most)\s+(\d+)\s+words?', prompt):
            max_words = int(match.group(1))
            return {"max": max_words}

        # Minimum: "over 100 words", "more than 100 words", "at least 100 words"
        if match := re.search(r'(?:over|more than|min|minimum|at least)\s+(\d+)\s+words?', prompt):
            min_words = int(match.group(1))
            return {"min": min_words}

        # Approximate: "about 100 words", "around 100 words"
        if match := re.search(r'(?:about|around|approximately)\s+(\d+)\s+words?', prompt):
            target = int(match.group(1))
            tolerance = max(5, int(target * 0.1))  # 10% tolerance or 5 words minimum
            return {"target": target, "tolerance": tolerance}

        # Exact: "exactly 100 words", "100 words"
        if match := re.search(r'(?:exactly\s+)?(\d+)\s+words?(?:\s+(?:of|in))?', prompt):
            target = int(match.group(1))
            return {"target": target, "tolerance": 0}

        return None

    def _extract_char_constraint(self, prompt: str) -> Optional[Dict[str, Any]]:
        """
        Parse character count requirements.

        Args:
            prompt: Lowercase prompt text

        Returns:
            Constraint specification or None
        """
        # Range: "between 500-1000 characters"
        if match := re.search(r'(?:between\s+)?(\d+)\s*(?:and|-)\s*(\d+)\s+(?:characters?|chars?)', prompt):
            min_chars = int(match.group(1))
            max_chars = int(match.group(2))
            return {"min": min_chars, "max": max_chars}

        # Maximum: "under 500 characters"
        if match := re.search(r'(?:under|less than|max|maximum)\s+(\d+)\s+(?:characters?|chars?)', prompt):
            max_chars = int(match.group(1))
            return {"max": max_chars}

        # Minimum: "at least 500 characters"
        if match := re.search(r'(?:over|more than|min|minimum|at least)\s+(\d+)\s+(?:characters?|chars?)', prompt):
            min_chars = int(match.group(1))
            return {"min": min_chars}

        return None

    def _extract_words_per_line_constraint(self, prompt: str) -> Optional[Dict[str, Any]]:
        """
        Parse words per line constraints.

        Args:
            prompt: Lowercase prompt text

        Returns:
            Constraint specification or None
        """
        # "each line is under 10 words", "each line under 10 words"
        if match := re.search(r'(?:each|every)\s+line\s+(?:is\s+)?(?:under|less than|max)\s+(\d+)\s+words?', prompt):
            max_words = int(match.group(1))
            return {"max": max_words}

        # "lines under 10 words each"
        if match := re.search(r'lines?\s+(?:under|less than)\s+(\d+)\s+words?\s+each', prompt):
            max_words = int(match.group(1))
            return {"max": max_words}

        return None

    def _extract_words_per_paragraph_constraint(self, prompt: str) -> Optional[Dict[str, Any]]:
        """
        Parse words per paragraph constraints.

        Args:
            prompt: Lowercase prompt text

        Returns:
            Constraint specification or None
        """
        # "each paragraph under 50 words", "each under 50 words"
        if match := re.search(r'(?:each|every)\s+(?:paragraph\s+)?(?:is\s+)?(?:under|less than|max)\s+(\d+)\s+words?', prompt):
            max_words = int(match.group(1))
            return {"max": max_words}

        # "paragraphs under 50 words each"
        if match := re.search(r'paragraphs?\s+(?:under|less than)\s+(\d+)\s+words?\s+each', prompt):
            max_words = int(match.group(1))
            return {"max": max_words}

        return None
