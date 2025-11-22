"""
Tests for MarginRenderer
"""

from PIL import Image
from visual_margin_system.margin_renderer import MarginRenderer


class TestMarginRenderer:
    """Test suite for MarginRenderer class."""

    def test_initialization(self):
        """Test renderer initializes with correct dimensions."""
        renderer = MarginRenderer(width=300, height=600, theme='dark')
        assert renderer.width == 300
        assert renderer.height == 600
        assert renderer.theme == 'dark'

    def test_render_returns_image(self):
        """Test render returns a PIL Image."""
        renderer = MarginRenderer()
        state = {
            'total_tokens': 10,
            'total_chars': 50,
            'total_words': 10,
            'line_count': 2,
            'paragraph_count': 1,
            'constraints': {},
            'constraint_status': {},
            'generation_complete': False,
        }

        image = renderer.render(state)
        assert isinstance(image, Image.Image)
        assert image.size == (renderer.width, renderer.height)

    def test_render_with_constraints(self):
        """Test rendering with active constraints."""
        renderer = MarginRenderer()
        state = {
            'total_tokens': 10,
            'total_chars': 50,
            'total_words': 10,
            'line_count': 2,
            'paragraph_count': 1,
            'constraints': {
                'lines': {'target': 4, 'tolerance': 0},
                'words': {'max': 100}
            },
            'constraint_status': {
                'lines': False,
                'words': True
            },
            'generation_complete': False,
        }

        image = renderer.render(state)
        assert isinstance(image, Image.Image)

    def test_render_to_base64(self):
        """Test rendering to base64 string."""
        renderer = MarginRenderer()
        state = {
            'total_tokens': 10,
            'total_chars': 50,
            'total_words': 10,
            'line_count': 2,
            'paragraph_count': 1,
            'constraints': {},
            'constraint_status': {},
            'generation_complete': False,
        }

        base64_str = renderer.render_to_base64(state)
        assert isinstance(base64_str, str)
        assert len(base64_str) > 0

    def test_theme_selection(self):
        """Test different theme selections."""
        dark_renderer = MarginRenderer(theme='dark')
        light_renderer = MarginRenderer(theme='light')

        assert dark_renderer.colors != light_renderer.colors
        assert 'background' in dark_renderer.colors
        assert 'background' in light_renderer.colors

    def test_format_constraint_text(self):
        """Test constraint text formatting."""
        renderer = MarginRenderer()

        state = {
            'line_count': 2,
            'paragraph_count': 1,
            'total_words': 50,
            'total_chars': 250,
        }

        # Test line constraint formatting
        text = renderer._format_constraint_text('lines', {'target': 4}, state)
        assert '2/4' in text

        # Test word constraint formatting
        text = renderer._format_constraint_text('words', {'max': 100}, state)
        assert '50' in text
        assert '100' in text

    def test_get_constraint_color(self):
        """Test constraint color selection based on status."""
        renderer = MarginRenderer()


        state_warning = {
            'line_count': 3,
            'paragraph_count': 2,
            'total_words': 95,
        }

        state_unsatisfied = {
            'line_count': 1,
            'paragraph_count': 0,
            'total_words': 20,
        }

        # Test warning state (close to target)
        color = renderer._get_constraint_color(state_warning, 'lines', {'target': 4})
        # Should be warning or unsatisfied

        # Test unsatisfied state (far from target)
        color = renderer._get_constraint_color(state_unsatisfied, 'lines', {'target': 4})
        # Should be unsatisfied
        assert color == renderer.colors['unsatisfied']
