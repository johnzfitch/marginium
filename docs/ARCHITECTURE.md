# Visual Margin System Architecture

## Overview

This document provides a detailed technical architecture overview of the Visual Margin System, explaining how each component works and how they integrate together.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Prompt + Constraints                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
            ┌────────────────────────┐
            │   ConstraintParser     │
            │  - Parse constraints   │
            │  - Extract requirements│
            └────────┬───────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │ VisualMarginGenerator      │
        │  - Orchestration          │
        │  - Generation loop        │
        └─┬──────────────────────┬───┘
          │                      │
          ▼                      ▼
┌──────────────────┐   ┌──────────────────────┐
│ GenerationState  │   │   MarginRenderer     │
│ Tracker          │──▶│  - Render state      │
│ - Track metrics  │   │  - Visual encoding   │
│ - Check constraints│  │  - Base64 output     │
└──────────────────┘   └──────────┬───────────┘
          │                       │
          │                       ▼
          │            ┌─────────────────────┐
          │            │  Vision-Language    │
          └───────────▶│       Model         │
                       │  (Claude + margin)  │
                       └──────────┬──────────┘
                                  │
                                  ▼
                          Generated Text
```

## Core Components

### 1. GenerationStateTracker

**Purpose**: Maintains real-time structural metadata during text generation.

**Key Responsibilities**:
- Track token, character, and word counts
- Detect line boundaries (newline characters)
- Detect paragraph boundaries (double newlines)
- Monitor constraint satisfaction
- Provide queryable state snapshots

**Implementation Details**:

```python
class GenerationStateTracker:
    def __init__(self):
        # Counters
        self.total_tokens = 0
        self.total_chars = 0
        self.total_words = 0

        # Structural units
        self.lines = []           # Completed lines
        self.paragraphs = []      # Completed paragraphs
        self.current_line = ""    # In-progress line
        self.current_paragraph = "" # In-progress paragraph

        # Constraint tracking
        self.constraints = {}
        self.constraint_status = {}
        self.generation_complete = False
```

**State Update Algorithm**:

1. Receive new token/chunk
2. Iterate through each character
3. Accumulate to current_line and current_paragraph
4. On '\n': Finalize line, check for paragraph break
5. On '\n\n': Finalize paragraph
6. Recompute word count from full text
7. Check all constraints
8. Update completion status

**Constraint Checking**:

For each constraint type:
- **Lines**: Compare `len(lines) + (1 if current_line else 0)` to target/range
- **Paragraphs**: Compare `len(paragraphs) + (1 if current_paragraph else 0)` to target/range
- **Words**: Compare `len(text.split())` to target/range
- **Words per line**: Check each completed line individually
- **Words per paragraph**: Check each completed paragraph individually

**Edge Cases**:
- Empty lines: Only counted if not at the start
- Trailing newlines: Don't create extra empty lines
- Incomplete lines: Counted in current state snapshot
- Single-line paragraphs: Handled by checking '\n\n' explicitly

### 2. MarginRenderer

**Purpose**: Convert generation state into visual representations.

**Key Responsibilities**:
- Render constraint checklists with status indicators
- Display current metrics (counts, progress)
- Apply visual hierarchy and color coding
- Encode as base64 for API transmission

**Visual Design**:

```
┌──────────────────────────┐
│   Generation State       │  <- Title
├──────────────────────────┤
│   Constraints            │  <- Section header
│   ✓ Lines: 4/4           │  <- Satisfied (green)
│   ○ Words: 95/100        │  <- Warning (yellow)
│   ✗ Paragraphs: 1/3      │  <- Unsatisfied (red)
├──────────────────────────┤
│   Current Metrics        │
│   Lines: 4               │
│   Paragraphs: 1          │
│   Words: 95              │
│   Characters: 487        │
│   Tokens: 23             │
│   Status: In Progress... │
└──────────────────────────┘
```

**Color Scheme**:

- **Dark Theme**:
  - Background: (30, 30, 30)
  - Text: (220, 220, 220)
  - Satisfied: (80, 200, 120) - Green
  - Warning: (255, 200, 50) - Yellow
  - Unsatisfied: (255, 100, 100) - Red

- **Light Theme**:
  - Background: (255, 255, 255)
  - Text: (30, 30, 30)
  - Satisfied: (34, 139, 34) - Green
  - Warning: (255, 165, 0) - Orange
  - Unsatisfied: (220, 20, 60) - Red

**Status Indicators**:
- ✓ (checkmark): Constraint satisfied
- ○ (circle): Close to target, warning state (within 10%)
- ✗ (cross): Constraint not satisfied

**Rendering Pipeline**:

1. Create blank canvas (PIL Image)
2. Get ImageDraw context
3. Render title section
4. Render constraints section:
   - For each constraint:
     - Determine status color
     - Draw indicator symbol
     - Format constraint text with current/target values
5. Render metrics section:
   - Display all current counts
   - Show completion status
6. Return PIL Image
7. For base64: Convert to PNG bytes, encode

**Font Handling**:
- Attempts to load DejaVu Sans fonts (common on Linux)
- Falls back to PIL default font if not available
- Uses multiple font sizes for hierarchy:
  - Title: 16pt bold
  - Headers: 14pt bold
  - Body: 12pt regular
  - Small: 10pt regular

### 3. ConstraintParser

**Purpose**: Extract structural constraints from natural language.

**Key Responsibilities**:
- Parse line count requirements
- Parse paragraph count requirements
- Parse word count requirements (ranges, bounds, approximations)
- Parse character count requirements
- Parse composite constraints (per-line, per-paragraph)

**Parsing Strategy**:

Uses regex patterns to match common constraint expressions:

1. **Line Constraints**:
   - Pattern: `(\d+|word_number)\s+lines?`
   - Examples: "4 lines", "four lines", "exactly 5 lines"
   - Output: `{"target": N, "tolerance": 0}`

2. **Paragraph Constraints**:
   - Pattern: `(\d+|word_number)\s+paragraphs?`
   - Examples: "3 paragraphs", "two paragraphs"
   - Output: `{"target": N, "tolerance": 0}`

3. **Word Constraints**:
   - **Range**: `(\d+)\s*(?:and|-)\s*(\d+)\s+words?`
     - "between 100 and 200 words", "50-75 words"
     - Output: `{"min": X, "max": Y}`

   - **Maximum**: `(?:under|less than|max)\s+(\d+)\s+words?`
     - "under 100 words"
     - Output: `{"max": X}`

   - **Minimum**: `(?:at least|more than|min)\s+(\d+)\s+words?`
     - "at least 50 words"
     - Output: `{"min": X}`

   - **Approximate**: `(?:about|around)\s+(\d+)\s+words?`
     - "about 100 words"
     - Output: `{"target": X, "tolerance": X*0.1}`

4. **Composite Constraints**:
   - **Per-line**: `each line (?:is\s+)?(?:under|max)\s+(\d+)\s+words?`
     - "each line is under 10 words"
     - Output: `{"max": X}`

   - **Per-paragraph**: `each (?:paragraph\s+)?(?:under|max)\s+(\d+)\s+words?`
     - "each paragraph under 50 words"
     - Output: `{"max": X}`

**Word-to-Number Conversion**:
- Maintains mapping: `{"one": 1, "two": 2, ..., "twenty": 20}`
- Supports both digit and word forms
- Case-insensitive matching

**Parser Output Format**:

```python
{
    "lines": {"target": 4, "tolerance": 0},
    "paragraphs": {"target": 3, "tolerance": 0},
    "words": {"min": 50, "max": 100},
    "words_per_line": {"max": 10}
}
```

### 4. VisualMarginGenerator

**Purpose**: Orchestrate the generation loop with margin awareness.

**Key Responsibilities**:
- Initialize state tracker with constraints
- Manage generation loop
- Render margins before each generation step
- Construct multimodal messages
- Update state after each chunk
- Determine termination conditions

**Generation Loop Algorithm**:

```python
def generate_with_margin(prompt, constraints, max_tokens, chunk_size):
    # 1. Initialize
    tracker.reset()
    tracker.set_constraints(constraints)
    generated_text = ""

    # 2. Generation loop
    while not tracker.is_complete() and len(tokens) < max_tokens:
        # 3. Render current state
        state = tracker.get_state_snapshot()
        margin_image = renderer.render_to_base64(state)

        # 4. Build multimodal message
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "data": margin_image}},
                    {"type": "text", "text": prompt_with_context}
                ]
            }
        ]

        # 5. Call API
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=chunk_size,
            messages=messages
        )

        # 6. Extract chunk
        chunk = response.content[0].text
        generated_text += chunk

        # 7. Update state
        tracker.update_with_token(chunk)

        # 8. Check termination
        if tracker.is_complete():
            break

    return generated_text
```

**Termination Conditions**:

Generation stops when:
1. All constraints are satisfied (`tracker.is_complete()` returns True)
2. Maximum token budget is reached
3. Model naturally ends generation (empty response)
4. API error occurs

**Chunk Size Optimization**:

- **Small chunks (20-30 tokens)**:
  - Pros: Frequent margin updates, fine-grained control
  - Cons: Higher API overhead, increased latency

- **Medium chunks (40-60 tokens)**:
  - Pros: Balance between updates and efficiency
  - Cons: May overshoot constraints slightly

- **Large chunks (100+ tokens)**:
  - Pros: Lower API overhead
  - Cons: Infrequent updates, higher overshoot risk

**Default**: 50 tokens (good balance for most use cases)

**Multimodal Message Construction**:

The message includes:
1. **Visual Context**: Base64-encoded margin image
2. **Text Context**:
   - Original prompt
   - Previously generated text
   - Explicit instruction to attend to margin
   - Constraint summary

**Error Handling**:
- API failures: Log error, return partial result
- Rendering failures: Fall back to text-only generation
- Invalid constraints: Use empty constraint set

## Data Flow

### Single Generation Iteration

```
1. Get current state snapshot
   ├─ Total tokens, chars, words
   ├─ Line count (including current incomplete line)
   ├─ Paragraph count (including current incomplete paragraph)
   ├─ Constraint satisfaction status
   └─ Completion flag

2. Render margin image
   ├─ Create canvas
   ├─ Render constraints with status colors
   ├─ Render metrics
   └─ Encode as base64

3. Construct API message
   ├─ Add margin image
   └─ Add text instruction with context

4. Call API (chunk_size tokens)
   └─ Receive generated text chunk

5. Update state
   ├─ Append chunk to generated text
   ├─ Process each character
   │  ├─ Detect line breaks
   │  ├─ Detect paragraph breaks
   │  └─ Update counters
   ├─ Recompute word count
   ├─ Check all constraints
   └─ Update completion flag

6. Check termination
   ├─ All constraints satisfied? → DONE
   ├─ Max tokens reached? → DONE
   └─ Otherwise → CONTINUE to step 1
```

## Performance Characteristics

### Time Complexity

- **State Update**: O(n) where n = length of new chunk
  - Character iteration: O(n)
  - Word count: O(N) where N = total generated text length
  - Constraint checking: O(c) where c = number of constraints

- **Margin Rendering**: O(1) - fixed size canvas
  - Drawing operations: O(c) for constraints
  - Image encoding: O(w * h) where w, h are dimensions

- **Total per iteration**: O(N + c)

### Space Complexity

- **State Storage**: O(N) for generated text and line/paragraph lists
- **Margin Image**: O(w * h) ≈ 300 * 600 = 180KB per render
- **Base64 Encoding**: O(w * h) ≈ 240KB (4/3 overhead)

### API Overhead

For a 500-token generation with chunk_size=50:
- Iterations: 10
- API calls: 10
- Margin renders: 10
- Total latency: ~10-15 seconds (vs ~2-3s baseline)
- Overhead: ~300-400%

Optimization strategies:
1. Increase chunk_size (reduces iterations)
2. Cache identical margin states (reduces encoding)
3. Use streaming APIs when available
4. Batch constraint checks

## Integration Points

### Anthropic API Integration

Uses the official `anthropic` Python library:

```python
from anthropic import Anthropic

client = Anthropic(api_key=api_key)

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=50,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": margin_base64
                    }
                },
                {
                    "type": "text",
                    "text": instruction
                }
            ]
        }
    ]
)
```

### Model Requirements

- Must support vision inputs (image + text)
- Recommended: `claude-sonnet-4-20250514` or later
- Alternative: Any multimodal LLM with similar API

## Extensibility

### Adding New Constraint Types

1. **Update ConstraintParser**:
   ```python
   def _extract_sentence_constraint(self, prompt: str) -> Optional[Dict]:
       # Add regex patterns for sentence constraints
       if match := re.search(r'(\d+)\s+sentences?', prompt):
           return {"target": int(match.group(1)), "tolerance": 0}
   ```

2. **Update GenerationStateTracker**:
   ```python
   def _check_constraints(self):
       # Add sentence constraint checking
       if 'sentences' in self.constraints:
           sentence_count = len(re.split(r'[.!?]+', self._generated_text))
           # Check against constraint spec
   ```

3. **Update MarginRenderer**:
   ```python
   def _format_constraint_text(self, constraint_type, constraint_spec, state):
       if constraint_type == 'sentences':
           return f"Sentences: {state['sentence_count']}/{constraint_spec['target']}"
   ```

### Custom Renderers

Subclass `MarginRenderer` to customize visual design:

```python
class CustomRenderer(MarginRenderer):
    def _render_constraint_section(self, draw, state, y_offset):
        # Custom rendering logic
        pass
```

### Alternative Model Backends

Implement custom client wrappers:

```python
class OpenAIClient:
    def generate_with_vision(self, text, image):
        # OpenAI API call
        pass

generator = VisualMarginGenerator(client=OpenAIClient())
```

## Testing Strategy

### Unit Tests

- **GenerationStateTracker**:
  - Test each counter (lines, paragraphs, words, chars)
  - Test constraint checking logic
  - Test edge cases (empty lines, trailing newlines)

- **ConstraintParser**:
  - Test each regex pattern
  - Test word-to-number conversion
  - Test multiple constraints in one prompt

- **MarginRenderer**:
  - Test image creation
  - Test base64 encoding
  - Test color selection logic

### Integration Tests

- End-to-end generation with constraints
- Multi-constraint scenarios
- Error handling and recovery

### Performance Tests

- Measure latency overhead
- Benchmark rendering performance
- Test with long generations (1000+ tokens)

## Future Optimizations

### 1. Differential Rendering
Only re-render changed portions of the margin:
```python
if state_hash == previous_state_hash:
    return cached_margin
```

### 2. Constraint Prediction
Predict when constraints will be satisfied and adjust chunk size:
```python
remaining_lines = target_lines - current_lines
estimated_tokens = remaining_lines * avg_tokens_per_line
chunk_size = min(chunk_size, estimated_tokens + buffer)
```

### 3. Streaming Integration
Use streaming APIs to get partial responses and update state in real-time.

### 4. Model Fine-Tuning
Fine-tune models specifically on margin-aware generation tasks to improve natural attention to visual state.

---

This architecture provides a solid foundation for visual margin-based generation state tracking while remaining flexible and extensible for future enhancements.
