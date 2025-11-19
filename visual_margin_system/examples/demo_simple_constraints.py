"""
Demo: Simple Constraints

Demonstrates basic line and paragraph counting with the Visual Margin System.
"""

import os
from visual_margin_system import (
    VisualMarginGenerator,
    GenerationStateTracker,
    MarginRenderer,
    ConstraintParser
)


def demo_exact_line_count():
    """Demo: Generate exactly N lines."""
    print("=" * 60)
    print("Demo: Exact Line Count")
    print("=" * 60)

    # Initialize generator
    generator = VisualMarginGenerator(
        api_key=os.getenv('ANTHROPIC_API_KEY')
    )

    # Generate with constraint
    prompt = "Give me 4 lines of creative text about the ocean"
    print(f"\nPrompt: {prompt}\n")

    result = generator.generate_with_margin(
        prompt=prompt,
        parse_constraints=True,
        chunk_size=30
    )

    print("Generated text:")
    print("-" * 60)
    print(result)
    print("-" * 60)

    # Verify constraint
    lines = result.strip().split('\n')
    print(f"\nLine count: {len(lines)}")
    print(f"Target: 4 lines")
    print(f"Constraint satisfied: {len(lines) == 4}")

    # Save margin visualization
    generator.save_margin_image("demo_line_count_margin.png")
    print("\nMargin visualization saved to: demo_line_count_margin.png")


def demo_paragraph_count():
    """Demo: Generate N paragraphs."""
    print("\n" + "=" * 60)
    print("Demo: Paragraph Count")
    print("=" * 60)

    generator = VisualMarginGenerator(
        api_key=os.getenv('ANTHROPIC_API_KEY')
    )

    prompt = "Write 3 paragraphs about artificial intelligence"
    print(f"\nPrompt: {prompt}\n")

    result = generator.generate_with_margin(
        prompt=prompt,
        parse_constraints=True,
        chunk_size=40
    )

    print("Generated text:")
    print("-" * 60)
    print(result)
    print("-" * 60)

    # Verify constraint
    paragraphs = [p for p in result.strip().split('\n\n') if p.strip()]
    print(f"\nParagraph count: {len(paragraphs)}")
    print(f"Target: 3 paragraphs")
    print(f"Constraint satisfied: {len(paragraphs) == 3}")


def demo_word_count_range():
    """Demo: Generate text within word count range."""
    print("\n" + "=" * 60)
    print("Demo: Word Count Range")
    print("=" * 60)

    generator = VisualMarginGenerator(
        api_key=os.getenv('ANTHROPIC_API_KEY')
    )

    prompt = "Explain quantum computing in 50-75 words"
    print(f"\nPrompt: {prompt}\n")

    result = generator.generate_with_margin(
        prompt=prompt,
        parse_constraints=True,
        chunk_size=30
    )

    print("Generated text:")
    print("-" * 60)
    print(result)
    print("-" * 60)

    # Verify constraint
    word_count = len(result.split())
    print(f"\nWord count: {word_count}")
    print(f"Target range: 50-75 words")
    print(f"Constraint satisfied: {50 <= word_count <= 75}")


def demo_manual_constraints():
    """Demo: Manually specify constraints."""
    print("\n" + "=" * 60)
    print("Demo: Manual Constraint Specification")
    print("=" * 60)

    generator = VisualMarginGenerator(
        api_key=os.getenv('ANTHROPIC_API_KEY')
    )

    prompt = "Write a haiku about technology"

    # Manually specify constraints for a haiku (3 lines)
    constraints = {
        'lines': {'target': 3, 'tolerance': 0}
    }

    print(f"\nPrompt: {prompt}")
    print(f"Constraints: {constraints}\n")

    result = generator.generate_with_margin(
        prompt=prompt,
        constraints=constraints,
        parse_constraints=False,
        chunk_size=20
    )

    print("Generated text:")
    print("-" * 60)
    print(result)
    print("-" * 60)

    lines = result.strip().split('\n')
    print(f"\nLine count: {len(lines)}")
    print(f"Target: 3 lines (haiku format)")
    print(f"Constraint satisfied: {len(lines) == 3}")


if __name__ == "__main__":
    # Check for API key
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        print("Please set it with: export ANTHROPIC_API_KEY='your-key-here'")
        exit(1)

    # Run demos
    demo_exact_line_count()
    demo_paragraph_count()
    demo_word_count_range()
    demo_manual_constraints()

    print("\n" + "=" * 60)
    print("All demos completed!")
    print("=" * 60)
