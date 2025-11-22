# Constraint Syntax Guide

This guide describes all supported constraint patterns and how to use them effectively.

## Overview

The Visual Margin System supports natural language constraint specification. You can describe structural requirements in plain English, and the system will automatically extract and enforce them during generation.

## Constraint Types

### 1. Line Count Constraints

Control the exact number of lines in the generated text.

#### Patterns

| Pattern | Example | Parsed As |
|---------|---------|-----------|
| `N lines` | "4 lines" | Exactly 4 lines |
| `WORD lines` | "four lines" | Exactly 4 lines |
| `exactly N lines` | "exactly 5 lines" | Exactly 5 lines |
| `a N-line NOUN` | "a 4-line poem" | Exactly 4 lines |

#### Examples

```python
# Digit form
"Give me 4 lines of creative text"
→ {'lines': {'target': 4, 'tolerance': 0}}

# Word form
"Write three lines about the ocean"
→ {'lines': {'target': 3, 'tolerance': 0}}

# Explicit exact
"Generate exactly 5 lines"
→ {'lines': {'target': 5, 'tolerance': 0}}

# Adjective form
"Write a 6-line poem"
→ {'lines': {'target': 6, 'tolerance': 0}}
```

#### Supported Word Numbers

- one (1)
- two (2)
- three (3)
- four (4)
- five (5)
- six (6)
- seven (7)
- eight (8)
- nine (9)
- ten (10)
- eleven (11)
- twelve (12)
- ... up to twenty (20)

#### Notes

- Line breaks are detected by `\n` characters
- Empty lines at the start are not counted
- Incomplete final line (no trailing newline) is counted

---

### 2. Paragraph Count Constraints

Control the number of paragraphs in the generated text.

#### Patterns

| Pattern | Example | Parsed As |
|---------|---------|-----------|
| `N paragraphs` | "3 paragraphs" | Exactly 3 paragraphs |
| `WORD paragraphs` | "two paragraphs" | Exactly 2 paragraphs |
| `exactly N paragraphs` | "exactly 4 paragraphs" | Exactly 4 paragraphs |

#### Examples

```python
# Digit form
"Write 3 paragraphs about AI"
→ {'paragraphs': {'target': 3, 'tolerance': 0}}

# Word form
"Create two paragraphs"
→ {'paragraphs': {'target': 2, 'tolerance': 0}}

# Explicit exact
"Generate exactly 5 paragraphs"
→ {'paragraphs': {'target': 5, 'tolerance': 0}}
```

#### Notes

- Paragraphs are separated by double newlines (`\n\n`)
- Single newlines do not create new paragraphs
- Incomplete final paragraph (no trailing `\n\n`) is counted

---

### 3. Word Count Constraints

Control the total number of words in the generated text.

#### Range Constraints

| Pattern | Example | Parsed As |
|---------|---------|-----------|
| `between N and M words` | "between 100 and 200 words" | 100-200 words |
| `N-M words` | "50-75 words" | 50-75 words |
| `N to M words` | "100 to 150 words" | 100-150 words |

```python
# "between...and" form
"Explain quantum computing in between 100 and 200 words"
→ {'words': {'min': 100, 'max': 200}}

# Hyphenated range
"Write 50-75 words"
→ {'words': {'min': 50, 'max': 75}}

# "to" form
"Use 100 to 150 words"
→ {'words': {'min': 100, 'max': 150}}
```

#### Maximum Constraints

| Pattern | Example | Parsed As |
|---------|---------|-----------|
| `under N words` | "under 100 words" | Maximum 100 words |
| `less than N words` | "less than 50 words" | Maximum 50 words |
| `max N words` | "max 75 words" | Maximum 75 words |
| `maximum N words` | "maximum 100 words" | Maximum 100 words |
| `no more than N words` | "no more than 50 words" | Maximum 50 words |
| `at most N words` | "at most 100 words" | Maximum 100 words |

```python
# Various maximum forms
"Write under 100 words"
→ {'words': {'max': 100}}

"Use less than 50 words"
→ {'words': {'max': 50}}

"Keep it to max 75 words"
→ {'words': {'max': 75}}
```

#### Minimum Constraints

| Pattern | Example | Parsed As |
|---------|---------|-----------|
| `at least N words` | "at least 100 words" | Minimum 100 words |
| `more than N words` | "more than 50 words" | Minimum 50 words |
| `min N words` | "min 75 words" | Minimum 75 words |
| `minimum N words` | "minimum 100 words" | Minimum 100 words |
| `over N words` | "over 50 words" | Minimum 50 words |

```python
# Various minimum forms
"Write at least 100 words"
→ {'words': {'min': 100}}

"Use more than 50 words"
→ {'words': {'min': 50}}

"Minimum 75 words please"
→ {'words': {'min': 75}}
```

#### Approximate Constraints

| Pattern | Example | Parsed As |
|---------|---------|-----------|
| `about N words` | "about 100 words" | ~100 words (±10%) |
| `around N words` | "around 200 words" | ~200 words (±10%) |
| `approximately N words` | "approximately 150 words" | ~150 words (±10%) |

```python
# Approximate constraints get 10% tolerance
"Write about 100 words"
→ {'words': {'target': 100, 'tolerance': 10}}

"Use around 200 words"
→ {'words': {'target': 200, 'tolerance': 20}}
```

#### Exact Constraints

| Pattern | Example | Parsed As |
|---------|---------|-----------|
| `exactly N words` | "exactly 100 words" | Exactly 100 words |
| `N words` | "100 words" | Exactly 100 words (implicit) |

```python
# Explicit exact
"Use exactly 100 words"
→ {'words': {'target': 100, 'tolerance': 0}}

# Implicit exact (when standalone)
"Describe it in 50 words"
→ {'words': {'target': 50, 'tolerance': 0}}
```

#### Notes

- Words are counted by splitting on whitespace
- Punctuation attached to words counts as part of the word
- Multiple spaces are treated as single separators

---

### 4. Character Count Constraints

Control the total number of characters in the generated text.

#### Patterns

| Pattern | Example | Parsed As |
|---------|---------|-----------|
| `between N-M characters` | "between 500-1000 characters" | 500-1000 chars |
| `under N characters` | "under 500 characters" | Maximum 500 chars |
| `at least N characters` | "at least 1000 characters" | Minimum 1000 chars |

#### Examples

```python
# Range
"Write between 500-1000 characters"
→ {'chars': {'min': 500, 'max': 1000}}

# Maximum
"Keep it under 500 characters"
→ {'chars': {'max': 500}}

# Minimum
"At least 1000 characters please"
→ {'chars': {'min': 1000}}
```

#### Notes

- All characters counted, including spaces and punctuation
- Newlines count as characters

---

### 5. Words Per Line Constraints

Control the word count for each individual line.

#### Patterns

| Pattern | Example | Parsed As |
|---------|---------|-----------|
| `each line is under N words` | "each line is under 10 words" | Max 10 words/line |
| `each line under N words` | "each line under 8 words" | Max 8 words/line |
| `every line under N words` | "every line under 12 words" | Max 12 words/line |
| `lines under N words each` | "lines under 10 words each" | Max 10 words/line |

#### Examples

```python
# "each line is" form
"Write a poem where each line is under 10 words"
→ {'words_per_line': {'max': 10}}

# Compact form
"Each line under 8 words"
→ {'words_per_line': {'max': 8}}

# "every line" form
"Make sure every line is less than 12 words"
→ {'words_per_line': {'max': 12}}

# Postfix form
"Write with lines under 10 words each"
→ {'words_per_line': {'max': 10}}
```

#### Notes

- Constraint applies to ALL lines independently
- If any line violates the constraint, the entire constraint fails
- Only completed lines are checked (current incomplete line is not)

---

### 6. Words Per Paragraph Constraints

Control the word count for each individual paragraph.

#### Patterns

| Pattern | Example | Parsed As |
|---------|---------|-----------|
| `each paragraph under N words` | "each paragraph under 50 words" | Max 50 words/para |
| `each under N words` | "each under 75 words" | Max 75 words/para |
| `paragraphs under N words each` | "paragraphs under 100 words each" | Max 100 words/para |

#### Examples

```python
# "each paragraph" form
"Write 3 paragraphs, each under 50 words"
→ {
    'paragraphs': {'target': 3, 'tolerance': 0},
    'words_per_paragraph': {'max': 50}
}

# Compact form
"3 paragraphs, each under 75 words"
→ {
    'paragraphs': {'target': 3, 'tolerance': 0},
    'words_per_paragraph': {'max': 75}
}

# Postfix form
"Write paragraphs under 100 words each"
→ {'words_per_paragraph': {'max': 100}}
```

#### Notes

- Constraint applies to ALL paragraphs independently
- If any paragraph violates the constraint, the entire constraint fails
- Only completed paragraphs are checked

---

## Multiple Constraints

You can combine multiple constraints in a single prompt. The parser will extract all detected constraints.

### Examples

#### Lines + Words Per Line
```python
"Write a 4-line poem where each line is under 10 words"
→ {
    'lines': {'target': 4, 'tolerance': 0},
    'words_per_line': {'max': 10}
}
```

#### Paragraphs + Words Per Paragraph + Total Words
```python
"Write 3 paragraphs, each under 50 words, totaling 100-150 words"
→ {
    'paragraphs': {'target': 3, 'tolerance': 0},
    'words_per_paragraph': {'max': 50},
    'words': {'min': 100, 'max': 150}
}
```

#### Lines + Word Range
```python
"Give me 5 lines about technology, using 50-75 words total"
→ {
    'lines': {'target': 5, 'tolerance': 0},
    'words': {'min': 50, 'max': 75}
}
```

---

## Manual Constraint Specification

If automatic parsing doesn't work for your use case, you can specify constraints manually:

### Format

```python
constraints = {
    'constraint_type': {
        'target': int,      # Optional: exact target value
        'tolerance': int,   # Optional: acceptable deviation
        'min': int,         # Optional: minimum value
        'max': int,         # Optional: maximum value
    }
}
```

### Examples

```python
# Exact line count
constraints = {
    'lines': {'target': 4, 'tolerance': 0}
}

# Word range
constraints = {
    'words': {'min': 50, 'max': 100}
}

# Multiple constraints
constraints = {
    'lines': {'target': 3, 'tolerance': 0},
    'paragraphs': {'target': 2, 'tolerance': 0},
    'words': {'max': 150},
    'words_per_line': {'max': 15}
}

# Use in generation
result = generator.generate_with_margin(
    prompt="Write about AI",
    constraints=constraints,
    parse_constraints=False  # Don't parse from prompt
)
```

---

## Constraint Satisfaction Logic

### Exact Targets

```python
{'target': N, 'tolerance': T}
```

**Satisfied when**: `N - T ≤ current_value ≤ N + T`

**Example**: `{'target': 4, 'tolerance': 0}` requires exactly 4

### Ranges

```python
{'min': N, 'max': M}
```

**Satisfied when**: `N ≤ current_value ≤ M`

**Example**: `{'min': 50, 'max': 100}` requires 50-100

### Minimum Only

```python
{'min': N}
```

**Satisfied when**: `current_value ≥ N`

**Example**: `{'min': 50}` requires at least 50

### Maximum Only

```python
{'max': M}
```

**Satisfied when**: `current_value ≤ M`

**Example**: `{'max': 100}` requires at most 100

### Composite Constraints (Per-Line, Per-Paragraph)

**Satisfied when**: ALL units satisfy the constraint

**Example**: `{'max': 10}` for words_per_line requires EVERY line to have ≤10 words

---

## Visual Indicators

In the rendered margin, constraints are shown with status indicators:

- **✓ Green**: Constraint is satisfied
- **○ Yellow**: Close to satisfaction (within 10% for numeric constraints)
- **✗ Red**: Constraint not satisfied

---

## Tips for Effective Constraints

### 1. Be Specific

**Good**: "Write exactly 4 lines"
**Poor**: "Write a few lines"

### 2. Use Ranges for Flexibility

**Good**: "Write between 100-150 words"
**Poor**: "Write exactly 127 words"

### 3. Combine Complementary Constraints

**Good**: "Write 3 paragraphs, each under 50 words"
**Poor**: "Write some paragraphs with some words"

### 4. Consider Content Requirements

**Good**: "Write 4 lines about the ocean, each under 10 words"
**Poor**: "Write 50 lines about complex philosophical concepts"

### 5. Test Parsing First

Use the parser test mode to verify your constraints are parsed correctly:

```python
from visual_margin_system import ConstraintParser

parser = ConstraintParser()
result = parser.parse("Write 3 paragraphs, each under 50 words")
print(result)
# {'paragraphs': {'target': 3, 'tolerance': 0},
#  'words_per_paragraph': {'max': 50}}
```

---

## Limitations

### Current Limitations

1. **No Sentence Constraints**: Sentence counting not yet supported
2. **No Semantic Constraints**: Can't constrain content, only structure
3. **No Format Constraints**: Can't enforce markdown, bullet points, etc.
4. **No Nested Constraints**: Can't specify sections with subsections

### Workarounds

- **Sentences**: Use lines as approximation (one sentence per line)
- **Content**: Include requirements in prompt text, not constraints
- **Format**: Specify in prompt, not as constraint
- **Nesting**: Flatten to single level (total paragraphs, words per paragraph)

---

## Testing Constraints

Use the visualization demo to see how constraints are tracked:

```bash
python visual_margin_system/examples/demo_visualization.py
```

Or use the interactive demo to test parsing:

```bash
python visual_margin_system/examples/demo_interactive.py
# Select option 3: Test constraint parser
```

---

For complete API documentation, see [API_REFERENCE.md](API_REFERENCE.md).
