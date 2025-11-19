"""
Margin Renderer

Converts generation state into visual representations for perception
by vision-language models.
"""

import base64
import io
from typing import Dict, Any, Tuple
from PIL import Image, ImageDraw, ImageFont


class MarginRenderer:
    """Renders generation state as visual margin images."""

    # Color schemes
    THEMES = {
        'dark': {
            'background': (30, 30, 30),
            'text': (220, 220, 220),
            'satisfied': (80, 200, 120),  # Green
            'warning': (255, 200, 50),    # Yellow
            'unsatisfied': (255, 100, 100),  # Red
            'border': (100, 100, 100),
            'section_bg': (45, 45, 45),
        },
        'light': {
            'background': (255, 255, 255),
            'text': (30, 30, 30),
            'satisfied': (34, 139, 34),   # Green
            'warning': (255, 165, 0),     # Orange
            'unsatisfied': (220, 20, 60),  # Red
            'border': (180, 180, 180),
            'section_bg': (240, 240, 240),
        }
    }

    def __init__(self, width: int = 300, height: int = 600, theme: str = "dark"):
        """
        Initialize the margin renderer.

        Args:
            width: Width of the rendered margin in pixels
            height: Height of the rendered margin in pixels
            theme: Color theme ('dark' or 'light')
        """
        self.width = width
        self.height = height
        self.theme = theme
        self.colors = self.THEMES[theme]
        self.font_config = self._load_font_config()

    def _load_font_config(self) -> Dict[str, Any]:
        """
        Load font configuration.

        Returns:
            Dictionary with font settings
        """
        # Try to load a font, fall back to default if not available
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
            header_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
            body_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
            small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
        except OSError:
            # Fallback to default font
            title_font = ImageFont.load_default()
            header_font = ImageFont.load_default()
            body_font = ImageFont.load_default()
            small_font = ImageFont.load_default()

        return {
            'title': title_font,
            'header': header_font,
            'body': body_font,
            'small': small_font,
        }

    def render(self, state: Dict[str, Any]) -> Image.Image:
        """
        Generate visual margin from state snapshot.

        Args:
            state: State snapshot from GenerationStateTracker

        Returns:
            PIL Image object
        """
        # Create canvas
        image = Image.new('RGB', (self.width, self.height), self.colors['background'])
        draw = ImageDraw.Draw(image)

        y_offset = 10

        # Render title
        draw.text((10, y_offset), "Generation State", fill=self.colors['text'], font=self.font_config['title'])
        y_offset += 30

        # Draw separator
        draw.line([(10, y_offset), (self.width - 10, y_offset)], fill=self.colors['border'], width=1)
        y_offset += 15

        # Render constraints section
        if state.get('constraints'):
            y_offset = self._render_constraint_section(draw, state, y_offset)
            y_offset += 10

        # Render metrics section
        y_offset = self._render_metrics_section(draw, state, y_offset)

        return image

    def _render_constraint_section(self, draw: ImageDraw.Draw, state: Dict[str, Any], y_offset: int) -> int:
        """
        Render constraint checklist with visual status indicators.

        Args:
            draw: ImageDraw object
            state: State snapshot
            y_offset: Current vertical position

        Returns:
            Updated y_offset
        """
        draw.text((10, y_offset), "Constraints", fill=self.colors['text'], font=self.font_config['header'])
        y_offset += 25

        constraints = state.get('constraints', {})
        constraint_status = state.get('constraint_status', {})

        for constraint_type, constraint_spec in constraints.items():
            is_satisfied = constraint_status.get(constraint_type, False)

            # Determine status color and indicator
            if is_satisfied:
                color = self.colors['satisfied']
                indicator = "✓"
            else:
                # Check if we're close to the target (warning state)
                color = self._get_constraint_color(state, constraint_type, constraint_spec)
                indicator = "○" if color == self.colors['warning'] else "✗"

            # Draw indicator
            draw.text((15, y_offset), indicator, fill=color, font=self.font_config['body'])

            # Draw constraint description
            constraint_text = self._format_constraint_text(constraint_type, constraint_spec, state)
            draw.text((35, y_offset), constraint_text, fill=self.colors['text'], font=self.font_config['small'])
            y_offset += 20

        return y_offset

    def _get_constraint_color(self, state: Dict[str, Any], constraint_type: str, constraint_spec: Dict[str, Any]) -> Tuple[int, int, int]:
        """
        Determine color for constraint based on how close we are to satisfying it.

        Args:
            state: Current state
            constraint_type: Type of constraint
            constraint_spec: Constraint specification

        Returns:
            RGB color tuple
        """
        # Check if we're within 10% of target (warning state)
        if constraint_type == 'lines':
            current = state['line_count']
            target = constraint_spec.get('target') or constraint_spec.get('max') or constraint_spec.get('min', 0)
            if target > 0 and abs(current - target) / target <= 0.1:
                return self.colors['warning']

        elif constraint_type == 'paragraphs':
            current = state['paragraph_count']
            target = constraint_spec.get('target') or constraint_spec.get('max') or constraint_spec.get('min', 0)
            if target > 0 and abs(current - target) / target <= 0.1:
                return self.colors['warning']

        elif constraint_type == 'words':
            current = state['total_words']
            target = constraint_spec.get('target')
            if target and abs(current - target) / target <= 0.1:
                return self.colors['warning']
            max_words = constraint_spec.get('max')
            if max_words and current / max_words >= 0.9:
                return self.colors['warning']

        return self.colors['unsatisfied']

    def _format_constraint_text(self, constraint_type: str, constraint_spec: Dict[str, Any], state: Dict[str, Any]) -> str:
        """
        Format constraint as readable text with current progress.

        Args:
            constraint_type: Type of constraint
            constraint_spec: Constraint specification
            state: Current state

        Returns:
            Formatted constraint text
        """
        if constraint_type == 'lines':
            current = state['line_count']
            if 'target' in constraint_spec:
                return f"Lines: {current}/{constraint_spec['target']}"
            elif 'max' in constraint_spec:
                return f"Lines: {current} (max {constraint_spec['max']})"
            elif 'min' in constraint_spec:
                return f"Lines: {current} (min {constraint_spec['min']})"

        elif constraint_type == 'paragraphs':
            current = state['paragraph_count']
            if 'target' in constraint_spec:
                return f"Paragraphs: {current}/{constraint_spec['target']}"
            elif 'max' in constraint_spec:
                return f"Paragraphs: {current} (max {constraint_spec['max']})"
            elif 'min' in constraint_spec:
                return f"Paragraphs: {current} (min {constraint_spec['min']})"

        elif constraint_type == 'words':
            current = state['total_words']
            if 'target' in constraint_spec:
                return f"Words: {current}/{constraint_spec['target']}"
            elif 'min' in constraint_spec and 'max' in constraint_spec:
                return f"Words: {current} ({constraint_spec['min']}-{constraint_spec['max']})"
            elif 'max' in constraint_spec:
                return f"Words: {current} (max {constraint_spec['max']})"
            elif 'min' in constraint_spec:
                return f"Words: {current} (min {constraint_spec['min']})"

        elif constraint_type == 'chars':
            current = state['total_chars']
            if 'min' in constraint_spec and 'max' in constraint_spec:
                return f"Chars: {current} ({constraint_spec['min']}-{constraint_spec['max']})"
            elif 'max' in constraint_spec:
                return f"Chars: {current} (max {constraint_spec['max']})"
            elif 'min' in constraint_spec:
                return f"Chars: {current} (min {constraint_spec['min']})"

        elif constraint_type == 'words_per_line':
            if 'max' in constraint_spec:
                return f"Words/line: ≤ {constraint_spec['max']}"
            elif 'min' in constraint_spec:
                return f"Words/line: ≥ {constraint_spec['min']}"

        elif constraint_type == 'words_per_paragraph':
            if 'max' in constraint_spec:
                return f"Words/para: ≤ {constraint_spec['max']}"
            elif 'min' in constraint_spec:
                return f"Words/para: ≥ {constraint_spec['min']}"

        return f"{constraint_type}: {constraint_spec}"

    def _render_metrics_section(self, draw: ImageDraw.Draw, state: Dict[str, Any], y_offset: int) -> int:
        """
        Render current generation metrics.

        Args:
            draw: ImageDraw object
            state: State snapshot
            y_offset: Current vertical position

        Returns:
            Updated y_offset
        """
        # Draw separator
        draw.line([(10, y_offset), (self.width - 10, y_offset)], fill=self.colors['border'], width=1)
        y_offset += 15

        draw.text((10, y_offset), "Current Metrics", fill=self.colors['text'], font=self.font_config['header'])
        y_offset += 25

        # Render metrics
        metrics = [
            f"Lines: {state.get('line_count', 0)}",
            f"Paragraphs: {state.get('paragraph_count', 0)}",
            f"Words: {state.get('total_words', 0)}",
            f"Characters: {state.get('total_chars', 0)}",
            f"Tokens: {state.get('total_tokens', 0)}",
        ]

        for metric in metrics:
            draw.text((15, y_offset), metric, fill=self.colors['text'], font=self.font_config['small'])
            y_offset += 18

        # Completion status
        y_offset += 10
        if state.get('generation_complete'):
            draw.text((15, y_offset), "Status: COMPLETE ✓", fill=self.colors['satisfied'], font=self.font_config['body'])
        else:
            draw.text((15, y_offset), "Status: In Progress...", fill=self.colors['warning'], font=self.font_config['body'])

        return y_offset

    def render_to_base64(self, state: Dict[str, Any]) -> str:
        """
        Render and encode as base64 for API transmission.

        Args:
            state: State snapshot from GenerationStateTracker

        Returns:
            Base64-encoded PNG image string
        """
        image = self.render(state)

        # Convert to base64
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')

        return image_base64
