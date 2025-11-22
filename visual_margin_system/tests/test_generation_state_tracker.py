"""
Tests for GenerationStateTracker
"""

from visual_margin_system.generation_state_tracker import GenerationStateTracker


class TestGenerationStateTracker:
    """Test suite for GenerationStateTracker class."""

    def test_initialization(self):
        """Test tracker initializes with empty state."""
        tracker = GenerationStateTracker()
        assert tracker.total_tokens == 0
        assert tracker.total_chars == 0
        assert tracker.total_words == 0
        assert len(tracker.lines) == 0
        assert len(tracker.paragraphs) == 0

    def test_line_counting(self):
        """Test accurate line counting."""
        tracker = GenerationStateTracker()
        tracker.update_with_token("Line one\n")
        tracker.update_with_token("Line two\n")
        tracker.update_with_token("Line three\n")

        state = tracker.get_state_snapshot()
        assert state['line_count'] == 3
        assert len(state['lines']) == 3

    def test_line_counting_with_current_line(self):
        """Test line counting includes current incomplete line."""
        tracker = GenerationStateTracker()
        tracker.update_with_token("Line one\n")
        tracker.update_with_token("Line two")  # No newline

        state = tracker.get_state_snapshot()
        assert state['line_count'] == 2  # Should count incomplete line

    def test_paragraph_counting(self):
        """Test accurate paragraph counting."""
        tracker = GenerationStateTracker()
        tracker.update_with_token("Paragraph one.\n\n")
        tracker.update_with_token("Paragraph two.\n\n")

        state = tracker.get_state_snapshot()
        assert state['paragraph_count'] == 2

    def test_word_counting(self):
        """Test accurate word counting."""
        tracker = GenerationStateTracker()
        tracker.update_with_token("This is a test sentence with seven words.\n")

        state = tracker.get_state_snapshot()
        assert state['total_words'] == 8

    def test_character_counting(self):
        """Test accurate character counting."""
        tracker = GenerationStateTracker()
        text = "Hello, world!"
        tracker.update_with_token(text)

        state = tracker.get_state_snapshot()
        assert state['total_chars'] == len(text)

    def test_line_constraint_exact(self):
        """Test exact line count constraint."""
        tracker = GenerationStateTracker()
        tracker.set_constraints({"lines": {"target": 3, "tolerance": 0}})

        tracker.update_with_token("Line 1\n")
        assert not tracker.is_complete()

        tracker.update_with_token("Line 2\n")
        assert not tracker.is_complete()

        tracker.update_with_token("Line 3\n")
        assert tracker.is_complete()

    def test_word_range_constraint(self):
        """Test word count range constraint."""
        tracker = GenerationStateTracker()
        tracker.set_constraints({"words": {"min": 5, "max": 10}})

        tracker.update_with_token("One two three four")
        assert not tracker.is_complete()  # 4 words, below min

        tracker.update_with_token(" five six")
        assert tracker.is_complete()  # 6 words, within range

        tracker.update_with_token(" seven eight nine ten eleven")
        assert not tracker.is_complete()  # 11 words, above max

    def test_paragraph_constraint(self):
        """Test paragraph count constraint."""
        tracker = GenerationStateTracker()
        tracker.set_constraints({"paragraphs": {"target": 2, "tolerance": 0}})

        tracker.update_with_token("First paragraph.\n\n")
        assert not tracker.is_complete()

        tracker.update_with_token("Second paragraph.\n\n")
        assert tracker.is_complete()

    def test_words_per_line_constraint(self):
        """Test words per line constraint."""
        tracker = GenerationStateTracker()
        tracker.set_constraints({"words_per_line": {"max": 5}})

        tracker.update_with_token("One two three\n")
        assert tracker.is_complete()  # 3 words, under max

        tracker.update_with_token("One two three four five six\n")
        assert not tracker.is_complete()  # Second line has 6 words, over max

    def test_reset(self):
        """Test tracker reset functionality."""
        tracker = GenerationStateTracker()
        tracker.update_with_token("Some text\n")
        tracker.set_constraints({"lines": {"target": 1}})

        tracker.reset()

        assert tracker.total_tokens == 0
        assert tracker.total_words == 0
        assert len(tracker.lines) == 0
        assert len(tracker.constraints) == 0

    def test_state_snapshot(self):
        """Test state snapshot contains all expected fields."""
        tracker = GenerationStateTracker()
        tracker.update_with_token("Test\n")

        state = tracker.get_state_snapshot()

        assert 'total_tokens' in state
        assert 'total_chars' in state
        assert 'total_words' in state
        assert 'line_count' in state
        assert 'paragraph_count' in state
        assert 'lines' in state
        assert 'paragraphs' in state
        assert 'constraints' in state
        assert 'constraint_status' in state
        assert 'generation_complete' in state
