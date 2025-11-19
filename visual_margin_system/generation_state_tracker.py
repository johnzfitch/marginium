"""
Generation State Tracker

Maintains real-time structural metadata during generation including
line counts, paragraph counts, word counts, and constraint satisfaction status.
"""

import re
from typing import Dict, List, Optional, Any


class GenerationStateTracker:
    """Tracks generation state and constraint satisfaction in real-time."""

    def __init__(self):
        """Initialize the state tracker with empty state."""
        self.total_tokens = 0
        self.total_chars = 0
        self.total_words = 0
        self.lines: List[str] = []
        self.paragraphs: List[str] = []
        self.current_line = ""
        self.current_paragraph = ""
        self.constraints: Dict[str, Any] = {}
        self.constraint_status: Dict[str, bool] = {}
        self.generation_complete = False
        self._generated_text = ""

    def set_constraints(self, constraints: Dict[str, Any]) -> None:
        """
        Set active constraints to monitor during generation.

        Args:
            constraints: Dictionary of constraint specifications
        """
        self.constraints = constraints
        self.constraint_status = {key: False for key in constraints.keys()}

    def update_with_token(self, token: str) -> None:
        """
        Update all state based on newly generated token.

        Args:
            token: The newly generated token/text chunk
        """
        self._generated_text += token
        self.total_tokens += 1
        self.total_chars += len(token)

        # Process the token character by character to detect line breaks
        for char in token:
            self.current_line += char
            self.current_paragraph += char

            if char == '\n':
                # Line break detected
                line_content = self.current_line.rstrip('\n')
                if line_content or len(self.lines) > 0:  # Don't count leading empty lines
                    self.lines.append(line_content)
                self.current_line = ""

                # Check if this is a paragraph break (double newline)
                if self.current_paragraph.endswith('\n\n'):
                    para_content = self.current_paragraph.rstrip('\n')
                    if para_content.strip():  # Only add non-empty paragraphs
                        self.paragraphs.append(para_content.strip())
                    self.current_paragraph = ""

        # Update word count
        self.total_words = len(self._generated_text.split())

        # Check constraint satisfaction
        self._check_constraints()

    def _check_constraints(self) -> None:
        """Validate all active constraints against current state."""
        for constraint_type, constraint_spec in self.constraints.items():
            if constraint_type == 'lines':
                current_count = len(self.lines)
                if 'target' in constraint_spec:
                    tolerance = constraint_spec.get('tolerance', 0)
                    target = constraint_spec['target']
                    self.constraint_status['lines'] = (
                        target - tolerance <= current_count <= target + tolerance
                    )
                elif 'min' in constraint_spec:
                    self.constraint_status['lines'] = current_count >= constraint_spec['min']
                elif 'max' in constraint_spec:
                    self.constraint_status['lines'] = current_count <= constraint_spec['max']

            elif constraint_type == 'paragraphs':
                current_count = len(self.paragraphs)
                if 'target' in constraint_spec:
                    tolerance = constraint_spec.get('tolerance', 0)
                    target = constraint_spec['target']
                    self.constraint_status['paragraphs'] = (
                        target - tolerance <= current_count <= target + tolerance
                    )
                elif 'min' in constraint_spec:
                    self.constraint_status['paragraphs'] = current_count >= constraint_spec['min']
                elif 'max' in constraint_spec:
                    self.constraint_status['paragraphs'] = current_count <= constraint_spec['max']

            elif constraint_type == 'words':
                if 'target' in constraint_spec:
                    tolerance = constraint_spec.get('tolerance', 0)
                    target = constraint_spec['target']
                    self.constraint_status['words'] = (
                        target - tolerance <= self.total_words <= target + tolerance
                    )
                elif 'min' in constraint_spec and 'max' in constraint_spec:
                    self.constraint_status['words'] = (
                        constraint_spec['min'] <= self.total_words <= constraint_spec['max']
                    )
                elif 'min' in constraint_spec:
                    self.constraint_status['words'] = self.total_words >= constraint_spec['min']
                elif 'max' in constraint_spec:
                    self.constraint_status['words'] = self.total_words <= constraint_spec['max']

            elif constraint_type == 'chars':
                if 'min' in constraint_spec and 'max' in constraint_spec:
                    self.constraint_status['chars'] = (
                        constraint_spec['min'] <= self.total_chars <= constraint_spec['max']
                    )
                elif 'min' in constraint_spec:
                    self.constraint_status['chars'] = self.total_chars >= constraint_spec['min']
                elif 'max' in constraint_spec:
                    self.constraint_status['chars'] = self.total_chars <= constraint_spec['max']

            elif constraint_type == 'words_per_line':
                # Check if all lines satisfy word count constraint
                if self.lines:
                    all_satisfy = True
                    for line in self.lines:
                        word_count = len(line.split())
                        if 'max' in constraint_spec and word_count > constraint_spec['max']:
                            all_satisfy = False
                            break
                        if 'min' in constraint_spec and word_count < constraint_spec['min']:
                            all_satisfy = False
                            break
                    self.constraint_status['words_per_line'] = all_satisfy

            elif constraint_type == 'words_per_paragraph':
                # Check if all paragraphs satisfy word count constraint
                if self.paragraphs:
                    all_satisfy = True
                    for para in self.paragraphs:
                        word_count = len(para.split())
                        if 'max' in constraint_spec and word_count > constraint_spec['max']:
                            all_satisfy = False
                            break
                        if 'min' in constraint_spec and word_count < constraint_spec['min']:
                            all_satisfy = False
                            break
                    self.constraint_status['words_per_paragraph'] = all_satisfy

        # Update completion status
        if self.constraints:
            self.generation_complete = all(self.constraint_status.values())

    def get_state_snapshot(self) -> Dict[str, Any]:
        """
        Return complete current state for rendering.

        Returns:
            Dictionary containing all current state information
        """
        # Count current line if it has content
        current_line_count = len(self.lines)
        if self.current_line.strip():
            current_line_count += 1

        # Count current paragraph if it has content
        current_para_count = len(self.paragraphs)
        if self.current_paragraph.strip() and not self.current_paragraph.endswith('\n\n'):
            current_para_count += 1

        return {
            'total_tokens': self.total_tokens,
            'total_chars': self.total_chars,
            'total_words': self.total_words,
            'line_count': current_line_count,
            'paragraph_count': current_para_count,
            'lines': self.lines + ([self.current_line] if self.current_line.strip() else []),
            'paragraphs': self.paragraphs + ([self.current_paragraph.strip()] if self.current_paragraph.strip() and not self.current_paragraph.endswith('\n\n') else []),
            'constraints': self.constraints,
            'constraint_status': self.constraint_status,
            'generation_complete': self.generation_complete,
            'generated_text': self._generated_text,
        }

    def check_constraints(self) -> Dict[str, bool]:
        """
        Validate all active constraints against current state.

        Returns:
            Dictionary mapping constraint names to satisfaction status
        """
        return self.constraint_status.copy()

    def is_complete(self) -> bool:
        """
        Determine if generation satisfies all constraints.

        Returns:
            True if all constraints are satisfied, False otherwise
        """
        return self.generation_complete

    def reset(self) -> None:
        """Reset the tracker to initial state."""
        self.__init__()
