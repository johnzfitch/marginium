"""
Demo: Interactive CLI

Interactive command-line tool for testing the Visual Margin System
with arbitrary constraints.
"""

import os
import sys
from visual_margin_system import VisualMarginGenerator, ConstraintParser


def print_header():
    """Print application header."""
    print("\n" + "=" * 70)
    print(" " * 15 + "Visual Margin System - Interactive Demo")
    print("=" * 70)


def print_menu():
    """Print main menu."""
    print("\nOptions:")
    print("  1. Generate with automatic constraint parsing")
    print("  2. Generate with manual constraint specification")
    print("  3. Test constraint parser only")
    print("  4. View current state")
    print("  5. Save margin visualization")
    print("  q. Quit")


def auto_constraint_mode(generator):
    """Mode 1: Automatic constraint parsing from prompt."""
    print("\n" + "-" * 70)
    print("Mode: Automatic Constraint Parsing")
    print("-" * 70)

    prompt = input("\nEnter your prompt: ").strip()
    if not prompt:
        print("Error: Empty prompt")
        return

    # Parse constraints from prompt
    parser = ConstraintParser()
    constraints = parser.parse(prompt)

    print(f"\nDetected constraints: {constraints}")
    print("\nGenerating...")

    try:
        result = generator.generate_with_margin(
            prompt=prompt,
            parse_constraints=True,
            chunk_size=30
        )

        print("\nGenerated text:")
        print("=" * 70)
        print(result)
        print("=" * 70)

        # Show final state
        state = generator.get_state_snapshot()
        print(f"\nFinal statistics:")
        print(f"  Lines: {state['line_count']}")
        print(f"  Paragraphs: {state['paragraph_count']}")
        print(f"  Words: {state['total_words']}")
        print(f"  Characters: {state['total_chars']}")
        print(f"  Complete: {state['generation_complete']}")

    except Exception as e:
        print(f"\nError during generation: {e}")


def manual_constraint_mode(generator):
    """Mode 2: Manual constraint specification."""
    print("\n" + "-" * 70)
    print("Mode: Manual Constraint Specification")
    print("-" * 70)

    prompt = input("\nEnter your prompt: ").strip()
    if not prompt:
        print("Error: Empty prompt")
        return

    print("\nSpecify constraints (press Enter to skip):")

    constraints = {}

    # Lines
    lines_input = input("  Target line count (e.g., 4): ").strip()
    if lines_input and lines_input.isdigit():
        constraints['lines'] = {'target': int(lines_input), 'tolerance': 0}

    # Paragraphs
    para_input = input("  Target paragraph count (e.g., 3): ").strip()
    if para_input and para_input.isdigit():
        constraints['paragraphs'] = {'target': int(para_input), 'tolerance': 0}

    # Words
    words_input = input("  Word count range (e.g., 50-100 or max:100): ").strip()
    if words_input:
        if '-' in words_input:
            parts = words_input.split('-')
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                constraints['words'] = {'min': int(parts[0]), 'max': int(parts[1])}
        elif words_input.startswith('max:'):
            max_val = words_input.split(':')[1]
            if max_val.isdigit():
                constraints['words'] = {'max': int(max_val)}

    if not constraints:
        print("\nNo constraints specified. Using free-form generation.")

    print(f"\nConstraints: {constraints}")
    print("\nGenerating...")

    try:
        result = generator.generate_with_margin(
            prompt=prompt,
            constraints=constraints,
            parse_constraints=False,
            chunk_size=30
        )

        print("\nGenerated text:")
        print("=" * 70)
        print(result)
        print("=" * 70)

        # Show final state
        state = generator.get_state_snapshot()
        print(f"\nFinal statistics:")
        print(f"  Lines: {state['line_count']}")
        print(f"  Paragraphs: {state['paragraph_count']}")
        print(f"  Words: {state['total_words']}")
        print(f"  Characters: {state['total_chars']}")
        print(f"  Constraints satisfied: {state['generation_complete']}")

    except Exception as e:
        print(f"\nError during generation: {e}")


def test_parser_mode():
    """Mode 3: Test constraint parser."""
    print("\n" + "-" * 70)
    print("Mode: Test Constraint Parser")
    print("-" * 70)

    parser = ConstraintParser()

    while True:
        prompt = input("\nEnter a prompt to parse (or 'back' to return): ").strip()
        if prompt.lower() == 'back':
            break

        if not prompt:
            continue

        constraints = parser.parse(prompt)

        print("\nParsed constraints:")
        if constraints:
            for ctype, cspec in constraints.items():
                print(f"  {ctype}: {cspec}")
        else:
            print("  (no constraints detected)")


def view_state_mode(generator):
    """Mode 4: View current state."""
    print("\n" + "-" * 70)
    print("Current Generation State")
    print("-" * 70)

    state = generator.get_state_snapshot()

    print(f"\nMetrics:")
    print(f"  Lines: {state['line_count']}")
    print(f"  Paragraphs: {state['paragraph_count']}")
    print(f"  Words: {state['total_words']}")
    print(f"  Characters: {state['total_chars']}")
    print(f"  Tokens: {state['total_tokens']}")

    print(f"\nConstraints:")
    if state['constraints']:
        for ctype, cspec in state['constraints'].items():
            status = "✓" if state['constraint_status'].get(ctype, False) else "✗"
            print(f"  {status} {ctype}: {cspec}")
    else:
        print("  (no constraints)")

    print(f"\nGeneration complete: {state['generation_complete']}")


def save_margin_mode(generator):
    """Mode 5: Save margin visualization."""
    print("\n" + "-" * 70)
    print("Save Margin Visualization")
    print("-" * 70)

    filename = input("\nEnter filename (default: margin.png): ").strip()
    if not filename:
        filename = "margin.png"

    if not filename.endswith('.png'):
        filename += '.png'

    try:
        generator.save_margin_image(filename)
        print(f"\nMargin visualization saved to: {filename}")
    except Exception as e:
        print(f"\nError saving margin: {e}")


def main():
    """Main interactive loop."""
    # Check for API key
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        print("Please set it with: export ANTHROPIC_API_KEY='your-key-here'")
        sys.exit(1)

    # Initialize generator
    generator = VisualMarginGenerator(
        api_key=os.getenv('ANTHROPIC_API_KEY')
    )

    print_header()
    print("\nWelcome to the Visual Margin System interactive demo!")

    while True:
        print_menu()
        choice = input("\nSelect an option: ").strip().lower()

        if choice == '1':
            auto_constraint_mode(generator)
        elif choice == '2':
            manual_constraint_mode(generator)
        elif choice == '3':
            test_parser_mode()
        elif choice == '4':
            view_state_mode(generator)
        elif choice == '5':
            save_margin_mode(generator)
        elif choice == 'q':
            print("\nGoodbye!")
            break
        else:
            print("\nInvalid option. Please try again.")


if __name__ == "__main__":
    main()
