"""
Demo: Margin Visualization

Demonstrates the visual margin rendering system without API calls.
"""

from visual_margin_system import GenerationStateTracker, MarginRenderer


def demo_margin_rendering():
    """Demonstrate margin rendering with various states."""
    print("=" * 60)
    print("Margin Visualization Demo")
    print("=" * 60)

    # Create tracker and renderer
    tracker = GenerationStateTracker()
    renderer = MarginRenderer(width=300, height=600, theme='dark')

    # Scenario 1: Empty state
    print("\n1. Rendering empty state...")
    state = tracker.get_state_snapshot()
    image = renderer.render(state)
    image.save("margin_empty.png")
    print("   Saved to: margin_empty.png")

    # Scenario 2: Partial progress
    print("\n2. Rendering partial progress...")
    tracker.set_constraints({
        'lines': {'target': 4, 'tolerance': 0},
        'words': {'max': 100}
    })
    tracker.update_with_token("This is line one\n")
    tracker.update_with_token("This is line two\n")

    state = tracker.get_state_snapshot()
    image = renderer.render(state)
    image.save("margin_partial.png")
    print("   Saved to: margin_partial.png")
    print(f"   Lines: {state['line_count']}/4")
    print(f"   Words: {state['total_words']}/100")

    # Scenario 3: Satisfied constraints
    print("\n3. Rendering satisfied constraints...")
    tracker.update_with_token("This is line three\n")
    tracker.update_with_token("This is line four\n")

    state = tracker.get_state_snapshot()
    image = renderer.render(state)
    image.save("margin_satisfied.png")
    print("   Saved to: margin_satisfied.png")
    print(f"   Lines: {state['line_count']}/4 ✓")
    print(f"   Words: {state['total_words']}/100 ✓")
    print(f"   Complete: {state['generation_complete']}")

    # Scenario 4: Multiple constraints
    print("\n4. Rendering multiple constraints...")
    tracker.reset()
    tracker.set_constraints({
        'lines': {'target': 3, 'tolerance': 0},
        'paragraphs': {'target': 2, 'tolerance': 0},
        'words': {'min': 20, 'max': 50},
        'words_per_line': {'max': 10}
    })
    tracker.update_with_token("Short line one with few words.\n")
    tracker.update_with_token("Line two is here.\n\n")
    tracker.update_with_token("And paragraph two starts.\n")

    state = tracker.get_state_snapshot()
    image = renderer.render(state)
    image.save("margin_multiple.png")
    print("   Saved to: margin_multiple.png")
    print(f"   Constraints: {len(state['constraints'])}")
    print(f"   Satisfied: {sum(state['constraint_status'].values())}/{len(state['constraints'])}")

    # Scenario 5: Light theme
    print("\n5. Rendering with light theme...")
    light_renderer = MarginRenderer(width=300, height=600, theme='light')
    image = light_renderer.render(state)
    image.save("margin_light_theme.png")
    print("   Saved to: margin_light_theme.png")

    # Scenario 6: Base64 encoding
    print("\n6. Testing base64 encoding...")
    base64_data = renderer.render_to_base64(state)
    print(f"   Base64 length: {len(base64_data)} characters")
    print(f"   Preview: {base64_data[:50]}...")

    print("\n" + "=" * 60)
    print("Visualization demo completed!")
    print("Generated images:")
    print("  - margin_empty.png")
    print("  - margin_partial.png")
    print("  - margin_satisfied.png")
    print("  - margin_multiple.png")
    print("  - margin_light_theme.png")
    print("=" * 60)


if __name__ == "__main__":
    demo_margin_rendering()
