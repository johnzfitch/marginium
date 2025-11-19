"""
Tests for ConstraintParser
"""

import pytest
from visual_margin_system.constraint_parser import ConstraintParser


class TestConstraintParser:
    """Test suite for ConstraintParser class."""

    def test_parse_line_constraint_numeric(self):
        """Test parsing numeric line constraints."""
        parser = ConstraintParser()

        result = parser.parse("Give me 4 lines of text")
        assert 'lines' in result
        assert result['lines']['target'] == 4

        result = parser.parse("Write exactly 5 lines")
        assert result['lines']['target'] == 5

    def test_parse_line_constraint_word_form(self):
        """Test parsing word-form line constraints."""
        parser = ConstraintParser()

        result = parser.parse("Give me three lines of text")
        assert 'lines' in result
        assert result['lines']['target'] == 3

    def test_parse_paragraph_constraint(self):
        """Test parsing paragraph constraints."""
        parser = ConstraintParser()

        result = parser.parse("Create 3 paragraphs")
        assert 'paragraphs' in result
        assert result['paragraphs']['target'] == 3

        result = parser.parse("Write two paragraphs")
        assert result['paragraphs']['target'] == 2

    def test_parse_word_range_constraint(self):
        """Test parsing word range constraints."""
        parser = ConstraintParser()

        result = parser.parse("Write between 100 and 200 words")
        assert 'words' in result
        assert result['words']['min'] == 100
        assert result['words']['max'] == 200

        result = parser.parse("Write 50-75 words")
        assert result['words']['min'] == 50
        assert result['words']['max'] == 75

    def test_parse_word_max_constraint(self):
        """Test parsing maximum word constraints."""
        parser = ConstraintParser()

        result = parser.parse("Write under 100 words")
        assert 'words' in result
        assert result['words']['max'] == 100

        result = parser.parse("Write less than 50 words")
        assert result['words']['max'] == 50

    def test_parse_word_min_constraint(self):
        """Test parsing minimum word constraints."""
        parser = ConstraintParser()

        result = parser.parse("Write at least 100 words")
        assert 'words' in result
        assert result['words']['min'] == 100

        result = parser.parse("Write more than 50 words")
        assert result['words']['min'] == 50

    def test_parse_word_approximate_constraint(self):
        """Test parsing approximate word constraints."""
        parser = ConstraintParser()

        result = parser.parse("Write about 100 words")
        assert 'words' in result
        assert result['words']['target'] == 100
        assert result['words']['tolerance'] > 0

    def test_parse_char_constraint(self):
        """Test parsing character constraints."""
        parser = ConstraintParser()

        result = parser.parse("Write between 500-1000 characters")
        assert 'chars' in result
        assert result['chars']['min'] == 500
        assert result['chars']['max'] == 1000

    def test_parse_words_per_line_constraint(self):
        """Test parsing words per line constraints."""
        parser = ConstraintParser()

        result = parser.parse("Write a 4-line poem where each line is under 10 words")
        assert 'words_per_line' in result
        assert result['words_per_line']['max'] == 10

    def test_parse_words_per_paragraph_constraint(self):
        """Test parsing words per paragraph constraints."""
        parser = ConstraintParser()

        result = parser.parse("Write 3 paragraphs, each under 50 words")
        assert 'words_per_paragraph' in result
        assert result['words_per_paragraph']['max'] == 50

    def test_parse_multiple_constraints(self):
        """Test parsing multiple constraints from single prompt."""
        parser = ConstraintParser()

        result = parser.parse("Write 3 paragraphs, each under 50 words, totaling 100-150 words")
        assert 'paragraphs' in result
        assert 'words_per_paragraph' in result
        assert 'words' in result
        assert result['paragraphs']['target'] == 3
        assert result['words_per_paragraph']['max'] == 50
        assert result['words']['min'] == 100
        assert result['words']['max'] == 150

    def test_parse_no_constraints(self):
        """Test parsing prompt with no constraints."""
        parser = ConstraintParser()

        result = parser.parse("Tell me a story")
        assert len(result) == 0

    def test_number_word_conversion(self):
        """Test word-to-number conversion."""
        parser = ConstraintParser()

        test_cases = [
            ("one line", 1),
            ("two lines", 2),
            ("five paragraphs", 5),
            ("ten words", 10),
        ]

        for prompt, expected in test_cases:
            result = parser.parse(prompt)
            if 'lines' in result:
                assert result['lines']['target'] == expected
            elif 'paragraphs' in result:
                assert result['paragraphs']['target'] == expected
