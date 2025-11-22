# API Reference

Complete API documentation for the Visual Margin System.

## Table of Contents

- [GenerationStateTracker](#generationstatetracker)
- [MarginRenderer](#marginrenderer)
- [ConstraintParser](#constraintparser)
- [VisualMarginGenerator](#visualmargingenerator)

---

## GenerationStateTracker

Tracks generation state and constraint satisfaction in real-time.

### Constructor

```python
GenerationStateTracker()
```

Initializes tracker with empty state.

**Returns**: `GenerationStateTracker` instance

### Methods

#### `set_constraints(constraints)`

Set active constraints to monitor during generation.

**Parameters**:
- `constraints` (dict): Dictionary of constraint specifications

**Example**:
```python
tracker.set_constraints({
    'lines': {'target': 4, 'tolerance': 0},
    'words': {'max': 100}
})
```

#### `update_with_token(token)`

Update all state based on newly generated token.

**Parameters**:
- `token` (str): The newly generated token/text chunk

**Example**:
```python
tracker.update_with_token("This is a line\n")
```

#### `get_state_snapshot()`

Return complete current state for rendering.

**Returns**: `dict` containing:
- `total_tokens` (int): Total tokens generated
- `total_chars` (int): Total characters
- `total_words` (int): Total words
- `line_count` (int): Number of lines (including incomplete)
- `paragraph_count` (int): Number of paragraphs (including incomplete)
- `lines` (list): List of completed line strings
- `paragraphs` (list): List of completed paragraph strings
- `constraints` (dict): Active constraints
- `constraint_status` (dict): Constraint satisfaction status
- `generation_complete` (bool): Whether all constraints satisfied
- `generated_text` (str): Full generated text

**Example**:
```python
state = tracker.get_state_snapshot()
print(f"Lines: {state['line_count']}")
print(f"Complete: {state['generation_complete']}")
```

#### `check_constraints()`

Validate all active constraints against current state.

**Returns**: `dict` mapping constraint names to satisfaction status (bool)

**Example**:
```python
status = tracker.check_constraints()
print(f"Lines satisfied: {status['lines']}")
```

#### `is_complete()`

Determine if generation satisfies all constraints.

**Returns**: `bool` - True if all constraints satisfied

**Example**:
```python
if tracker.is_complete():
    print("All constraints satisfied!")
```

#### `reset()`

Reset the tracker to initial state.

**Example**:
```python
tracker.reset()
```

### Attributes

- `total_tokens` (int): Total tokens generated
- `total_chars` (int): Total characters
- `total_words` (int): Total words
- `lines` (list): Completed lines
- `paragraphs` (list): Completed paragraphs
- `current_line` (str): Current incomplete line
- `current_paragraph` (str): Current incomplete paragraph
- `constraints` (dict): Active constraints
- `constraint_status` (dict): Constraint satisfaction status
- `generation_complete` (bool): Completion flag

---

## MarginRenderer

Renders generation state as visual margin images.

### Constructor

```python
MarginRenderer(width=300, height=600, theme="dark")
```

**Parameters**:
- `width` (int, optional): Width of rendered margin in pixels. Default: 300
- `height` (int, optional): Height of rendered margin in pixels. Default: 600
- `theme` (str, optional): Color theme ('dark' or 'light'). Default: "dark"

**Example**:
```python
renderer = MarginRenderer(width=400, height=800, theme='light')
```

### Methods

#### `render(state)`

Generate visual margin from state snapshot.

**Parameters**:
- `state` (dict): State snapshot from GenerationStateTracker

**Returns**: `PIL.Image.Image` object

**Example**:
```python
state = tracker.get_state_snapshot()
image = renderer.render(state)
image.save("margin.png")
```

#### `render_to_base64(state)`

Render and encode as base64 for API transmission.

**Parameters**:
- `state` (dict): State snapshot from GenerationStateTracker

**Returns**: `str` - Base64-encoded PNG image string

**Example**:
```python
base64_str = renderer.render_to_base64(state)
# Use in API call
```

### Attributes

- `width` (int): Margin width in pixels
- `height` (int): Margin height in pixels
- `theme` (str): Current color theme
- `colors` (dict): Color scheme for current theme
- `font_config` (dict): Font configuration

### Color Themes

#### Dark Theme
```python
{
    'background': (30, 30, 30),
    'text': (220, 220, 220),
    'satisfied': (80, 200, 120),
    'warning': (255, 200, 50),
    'unsatisfied': (255, 100, 100),
    'border': (100, 100, 100),
    'section_bg': (45, 45, 45),
}
```

#### Light Theme
```python
{
    'background': (255, 255, 255),
    'text': (30, 30, 30),
    'satisfied': (34, 139, 34),
    'warning': (255, 165, 0),
    'unsatisfied': (220, 20, 60),
    'border': (180, 180, 180),
    'section_bg': (240, 240, 240),
}
```

---

## ConstraintParser

Parses natural language to extract structural constraints.

### Constructor

```python
ConstraintParser()
```

Initializes parser with default patterns.

### Methods

#### `parse(prompt)`

Extract structural constraints from natural language prompts.

**Parameters**:
- `prompt` (str): Natural language prompt

**Returns**: `dict` of parsed constraints

**Examples**:
```python
parser = ConstraintParser()

# Line constraint
result = parser.parse("Give me 4 lines of text")
# Returns: {'lines': {'target': 4, 'tolerance': 0}}

# Word range
result = parser.parse("Write between 100-200 words")
# Returns: {'words': {'min': 100, 'max': 200}}

# Multiple constraints
result = parser.parse("Write 3 paragraphs, each under 50 words")
# Returns: {
#     'paragraphs': {'target': 3, 'tolerance': 0},
#     'words_per_paragraph': {'max': 50}
# }
```

### Supported Patterns

#### Line Constraints
- `"4 lines"` → `{'target': 4, 'tolerance': 0}`
- `"four lines"` → `{'target': 4, 'tolerance': 0}`
- `"exactly 5 lines"` → `{'target': 5, 'tolerance': 0}`

#### Paragraph Constraints
- `"3 paragraphs"` → `{'target': 3, 'tolerance': 0}`
- `"two paragraphs"` → `{'target': 2, 'tolerance': 0}`

#### Word Constraints
- `"100 words"` → `{'target': 100, 'tolerance': 0}`
- `"between 50-100 words"` → `{'min': 50, 'max': 100}`
- `"under 100 words"` → `{'max': 100}`
- `"at least 50 words"` → `{'min': 50}`
- `"about 100 words"` → `{'target': 100, 'tolerance': 10}`

#### Character Constraints
- `"between 500-1000 characters"` → `{'min': 500, 'max': 1000}`
- `"under 500 characters"` → `{'max': 500}`

#### Composite Constraints
- `"each line is under 10 words"` → `{'max': 10}`
- `"each paragraph under 50 words"` → `{'max': 50}`

### Constraint Format

All constraint specifications follow this format:

```python
{
    'constraint_type': {
        'target': int,      # Exact target value (optional)
        'tolerance': int,   # Acceptable deviation (optional)
        'min': int,         # Minimum value (optional)
        'max': int,         # Maximum value (optional)
    }
}
```

---

## VisualMarginGenerator

Orchestrates text generation with visual margin state tracking.

### Constructor

```python
VisualMarginGenerator(
    api_key=None,
    model="claude-sonnet-4-20250514",
    renderer=None,
    tracker=None,
    parser=None
)
```

**Parameters**:
- `api_key` (str, optional): Anthropic API key. If None, reads from `ANTHROPIC_API_KEY` env var
- `model` (str, optional): Model to use for generation. Default: "claude-sonnet-4-20250514"
- `renderer` (MarginRenderer, optional): Custom renderer. Creates default if None
- `tracker` (GenerationStateTracker, optional): Custom tracker. Creates default if None
- `parser` (ConstraintParser, optional): Custom parser. Creates default if None

**Example**:
```python
# Basic usage
generator = VisualMarginGenerator()

# Custom configuration
generator = VisualMarginGenerator(
    api_key="your-key",
    model="claude-sonnet-4-20250514",
    renderer=MarginRenderer(theme='light')
)
```

### Methods

#### `generate_with_margin(prompt, constraints=None, max_tokens=2048, chunk_size=50, parse_constraints=True)`

Generate text with visual margin state tracking (synchronous).

**Parameters**:
- `prompt` (str): User prompt
- `constraints` (dict, optional): Dictionary of constraint specifications. If None, parses from prompt
- `max_tokens` (int, optional): Maximum total tokens to generate. Default: 2048
- `chunk_size` (int, optional): Number of tokens per API call. Default: 50
- `parse_constraints` (bool, optional): Whether to parse constraints from prompt. Default: True

**Returns**: `str` - Generated text

**Example**:
```python
# Automatic constraint parsing
result = generator.generate_with_margin(
    prompt="Give me 4 lines about the ocean"
)

# Manual constraints
result = generator.generate_with_margin(
    prompt="Write a haiku",
    constraints={'lines': {'target': 3, 'tolerance': 0}},
    parse_constraints=False
)

# Custom parameters
result = generator.generate_with_margin(
    prompt="Write 3 paragraphs about AI",
    max_tokens=1000,
    chunk_size=30
)
```

#### `generate_with_margin_async(prompt, constraints=None, max_tokens=2048, chunk_size=50, parse_constraints=True)`

Generate text with visual margin state tracking (asynchronous).

**Parameters**: Same as `generate_with_margin`

**Returns**: `str` - Generated text (awaitable)

**Example**:
```python
import asyncio

async def main():
    result = await generator.generate_with_margin_async(
        prompt="Give me 4 lines about space"
    )
    print(result)

asyncio.run(main())
```

#### `get_state_snapshot()`

Get current generation state.

**Returns**: `dict` - Current state snapshot

**Example**:
```python
state = generator.get_state_snapshot()
print(f"Words generated: {state['total_words']}")
```

#### `save_margin_image(filepath)`

Save current margin visualization to file.

**Parameters**:
- `filepath` (str): Path to save the image

**Example**:
```python
generator.save_margin_image("current_margin.png")
```

### Attributes

- `client` (Anthropic): Synchronous API client
- `async_client` (AsyncAnthropic): Asynchronous API client
- `model` (str): Current model name
- `renderer` (MarginRenderer): Margin renderer instance
- `tracker` (GenerationStateTracker): State tracker instance
- `parser` (ConstraintParser): Constraint parser instance

---

## Constraint Specification Format

Constraints are specified as dictionaries with the following structure:

### Exact Target

```python
{
    'constraint_type': {
        'target': 4,        # Exact target value
        'tolerance': 0      # Acceptable deviation
    }
}
```

**Example**: Exactly 4 lines (3-5 acceptable with tolerance=1)

### Range

```python
{
    'constraint_type': {
        'min': 50,          # Minimum value
        'max': 100          # Maximum value
    }
}
```

**Example**: Between 50-100 words

### Minimum Only

```python
{
    'constraint_type': {
        'min': 50           # Minimum value
    }
}
```

**Example**: At least 50 words

### Maximum Only

```python
{
    'constraint_type': {
        'max': 100          # Maximum value
    }
}
```

**Example**: Under 100 words

## Supported Constraint Types

| Type | Description | Specification |
|------|-------------|---------------|
| `lines` | Number of lines | `{'target': N}` or `{'min': N, 'max': M}` |
| `paragraphs` | Number of paragraphs | `{'target': N}` or `{'min': N, 'max': M}` |
| `words` | Total word count | `{'target': N}`, `{'min': N, 'max': M}`, etc. |
| `chars` | Total character count | `{'min': N, 'max': M}` |
| `words_per_line` | Words per line | `{'max': N}` or `{'min': N}` |
| `words_per_paragraph` | Words per paragraph | `{'max': N}` or `{'min': N}` |

## Error Handling

All methods handle errors gracefully:

- **API Errors**: Logged, partial results returned
- **Rendering Errors**: Fall back to text-only generation
- **Invalid Constraints**: Ignored, empty constraint set used
- **Network Errors**: Propagated to caller

**Example**:
```python
try:
    result = generator.generate_with_margin(prompt="...")
except Exception as e:
    print(f"Generation failed: {e}")
```

## Type Hints

All classes and methods include comprehensive type hints:

```python
from typing import Dict, Any, Optional, List

def generate_with_margin(
    self,
    prompt: str,
    constraints: Optional[Dict[str, Any]] = None,
    max_tokens: int = 2048,
    chunk_size: int = 50,
    parse_constraints: bool = True
) -> str:
    ...
```

---

## Examples

### Complete Example

```python
from visual_margin_system import (
    VisualMarginGenerator,
    MarginRenderer,
    ConstraintParser
)

# Initialize components
parser = ConstraintParser()
renderer = MarginRenderer(theme='dark')
generator = VisualMarginGenerator(
    renderer=renderer
)

# Parse constraints
prompt = "Write 3 paragraphs about AI, each under 50 words"
constraints = parser.parse(prompt)
print(f"Constraints: {constraints}")

# Generate with margin awareness
result = generator.generate_with_margin(
    prompt=prompt,
    constraints=constraints,
    chunk_size=30
)

print("Generated text:")
print(result)

# Check final state
state = generator.get_state_snapshot()
print(f"\nParagraphs: {state['paragraph_count']}")
print(f"Words: {state['total_words']}")
print(f"Satisfied: {state['generation_complete']}")

# Save margin visualization
generator.save_margin_image("final_margin.png")
```

---

For more examples, see the `visual_margin_system/examples/` directory.
