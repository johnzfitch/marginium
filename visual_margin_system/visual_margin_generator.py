"""
Visual Margin Generator

Orchestrates the generation loop with margin awareness, combining
state tracking, rendering, and multimodal LLM integration.
"""

from typing import Dict, Any, Optional, List
from anthropic import Anthropic, AsyncAnthropic

from .generation_state_tracker import GenerationStateTracker
from .margin_renderer import MarginRenderer
from .constraint_parser import ConstraintParser

# Token estimation constant for fallback when API doesn't provide usage stats
# Modern tokenizers typically produce 1.3-1.5 tokens per word for English text
TOKENS_PER_WORD_ESTIMATE = 1.33


class VisualMarginGenerator:
    """Orchestrates text generation with visual margin state tracking."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-sonnet-4-20250514",
        renderer: Optional[MarginRenderer] = None,
        tracker: Optional[GenerationStateTracker] = None,
        parser: Optional[ConstraintParser] = None
    ):
        """
        Initialize the visual margin generator.

        Args:
            api_key: Anthropic API key (or set ANTHROPIC_API_KEY env var)
            model: Model to use for generation
            renderer: MarginRenderer instance (creates default if None)
            tracker: GenerationStateTracker instance (creates default if None)
            parser: ConstraintParser instance (creates default if None)
        """
        self.client = Anthropic(api_key=api_key) if api_key else Anthropic()
        self.async_client = AsyncAnthropic(api_key=api_key) if api_key else AsyncAnthropic()
        self.model = model
        self.renderer = renderer or MarginRenderer()
        self.tracker = tracker or GenerationStateTracker()
        self.parser = parser or ConstraintParser()

    def generate_with_margin(
        self,
        prompt: str,
        constraints: Optional[Dict[str, Any]] = None,
        max_tokens: int = 2048,
        chunk_size: int = 50,
        parse_constraints: bool = True
    ) -> str:
        """
        Generate text with visual margin state tracking (synchronous version).

        Args:
            prompt: User prompt
            constraints: Dictionary of constraint specifications (or None to parse from prompt)
            max_tokens: Maximum total tokens to generate
            chunk_size: Number of tokens to generate per API call
            parse_constraints: Whether to parse constraints from prompt if not provided

        Returns:
            Generated text
        """
        # Parse constraints from prompt if not provided
        if constraints is None and parse_constraints:
            constraints = self.parser.parse(prompt)

        # If still no constraints, use empty dict
        if constraints is None:
            constraints = {}

        # Initialize tracker with constraints
        self.tracker.reset()
        self.tracker.set_constraints(constraints)

        generated_text = ""
        remaining_tokens = max_tokens

        while remaining_tokens > 0:
            # Check if we've satisfied all constraints
            if constraints and self.tracker.is_complete():
                break

            # Render current margin state
            state_snapshot = self.tracker.get_state_snapshot()
            margin_b64 = self.renderer.render_to_base64(state_snapshot)

            # Construct multimodal prompt
            messages = self._build_multimodal_messages(
                prompt=prompt,
                generated_so_far=generated_text,
                margin_image_b64=margin_b64,
                constraints=constraints
            )

            try:
                # Determine how many tokens to request (don't exceed remaining budget)
                tokens_to_request = min(chunk_size, remaining_tokens)
                
                # Call vision-language model
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=tokens_to_request,
                    messages=messages
                )

                # Extract generated chunk
                if response.content and len(response.content) > 0:
                    chunk = response.content[0].text
                    generated_text += chunk

                    # Update tracker with new content
                    self.tracker.update_with_token(chunk)
                    
                    # Deduct tokens from remaining budget (prevent negative)
                    tokens_used = self._estimate_token_usage(response, chunk)
                    # Defensive: ensure tokens_used does not exceed tokens_to_request
                    if tokens_used > tokens_to_request:
                        print(f"Warning: tokens_used ({tokens_used}) > tokens_to_request ({tokens_to_request}). Capping to {tokens_to_request}.")
                        tokens_used = tokens_to_request
                    remaining_tokens = max(0, remaining_tokens - tokens_used)
                else:
                    # No more content generated
                    break

            except Exception as e:
                # Handle API errors gracefully
                print(f"Error during generation: {e}")
                break

        return generated_text

    async def generate_with_margin_async(
        self,
        prompt: str,
        constraints: Optional[Dict[str, Any]] = None,
        max_tokens: int = 2048,
        chunk_size: int = 50,
        parse_constraints: bool = True
    ) -> str:
        """
        Generate text with visual margin state tracking (async version).

        This is the core orchestration method that:
        1. Parses constraints from prompt (if not provided)
        2. Initiates generation with margin rendering
        3. Updates state after each token/chunk
        4. Re-renders margin and feeds to next prediction
        5. Terminates when constraints satisfied or max_tokens reached

        Args:
            prompt: User prompt
            constraints: Dictionary of constraint specifications (or None to parse from prompt)
            max_tokens: Maximum total tokens to generate
            chunk_size: Number of tokens to generate per API call
            parse_constraints: Whether to parse constraints from prompt if not provided

        Returns:
            Generated text
        """
        # Parse constraints from prompt if not provided
        if constraints is None and parse_constraints:
            constraints = self.parser.parse(prompt)

        # If still no constraints, use empty dict
        if constraints is None:
            constraints = {}

        # Initialize tracker with constraints
        self.tracker.reset()
        self.tracker.set_constraints(constraints)

        generated_text = ""
        remaining_tokens = max_tokens

        while remaining_tokens > 0:
            # Check if we've satisfied all constraints
            if constraints and self.tracker.is_complete():
                break

            # Render current margin state
            state_snapshot = self.tracker.get_state_snapshot()
            margin_b64 = self.renderer.render_to_base64(state_snapshot)

            # Construct multimodal prompt
            messages = self._build_multimodal_messages(
                prompt=prompt,
                generated_so_far=generated_text,
                margin_image_b64=margin_b64,
                constraints=constraints
            )

            try:
                # Determine how many tokens to request (don't exceed remaining budget)
                tokens_to_request = min(chunk_size, remaining_tokens)
                
                # Call vision-language model
                response = await self.async_client.messages.create(
                    model=self.model,
                    max_tokens=tokens_to_request,
                    messages=messages
                )

                # Extract generated chunk
                if response.content and len(response.content) > 0:
                    chunk = response.content[0].text
                    generated_text += chunk

                    # Update tracker with new content
                    self.tracker.update_with_token(chunk)
                    
                    # Deduct tokens from remaining budget (prevent negative)
                    tokens_used = self._estimate_token_usage(response, chunk)
                    # Defensive check: tokens_used should not exceed tokens_to_request
                    if tokens_used > tokens_to_request:
                        print(f"Warning: tokens_used ({tokens_used}) > tokens_to_request ({tokens_to_request}). Capping tokens_used to tokens_to_request.")
                        tokens_used = tokens_to_request
                    remaining_tokens = max(0, remaining_tokens - tokens_used)
                else:
                    # No more content generated
                    break

            except Exception as e:
                # Handle API errors gracefully
                print(f"Error during generation: {e}")
                break

        return generated_text

    def _build_multimodal_messages(
        self,
        prompt: str,
        generated_so_far: str,
        margin_image_b64: str,
        constraints: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Construct message array with text context and visual margin.

        Args:
            prompt: Original user prompt
            generated_so_far: Text generated so far
            margin_image_b64: Base64-encoded margin image
            constraints: Active constraints

        Returns:
            List of message dictionaries for API
        """
        # Build the instruction text
        if generated_so_far:
            instruction = f"""You are continuing to generate a response to: {prompt}

You have generated so far:
{generated_so_far}

The visual margin image shows your current generation state and constraint satisfaction status.
Pay close attention to the constraint checklist and current counts shown in the margin.
Continue generation while monitoring the margin to ensure you satisfy all constraints.

Important: Only generate the next portion of text. Do not repeat what you've already generated."""
        else:
            constraint_desc = ""
            if constraints:
                constraint_desc = "\n\nConstraints to satisfy:\n"
                for ctype, cspec in constraints.items():
                    constraint_desc += f"- {ctype}: {cspec}\n"

            instruction = f"""You are generating a response to: {prompt}{constraint_desc}

The visual margin image shows your current generation state and constraint satisfaction status.
Pay close attention to the constraint checklist and current counts shown in the margin.
Generate text while monitoring the margin to ensure you satisfy all constraints."""

        return [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": margin_image_b64
                        }
                    },
                    {
                        "type": "text",
                        "text": instruction
                    }
                ]
            }
        ]

    def _estimate_token_usage(self, response, chunk: str) -> int:
        """
        Estimate the number of tokens used in a response.
        
        Args:
            response: API response object
            chunk: Generated text chunk
            
        Returns:
            Estimated token count
        """
        # Try to use actual token count from API response
        if hasattr(response, 'usage') and hasattr(response.usage, 'output_tokens'):
            return response.usage.output_tokens
        
        # Fallback: estimate based on word count using configured constant
        word_count = len(chunk.split())
        return int(word_count * TOKENS_PER_WORD_ESTIMATE)

    def get_state_snapshot(self) -> Dict[str, Any]:
        """
        Get current generation state.

        Returns:
            Current state snapshot
        """
        return self.tracker.get_state_snapshot()

    def save_margin_image(self, filepath: str) -> None:
        """
        Save current margin visualization to file.

        Args:
            filepath: Path to save the image
        """
        state = self.tracker.get_state_snapshot()
        image = self.renderer.render(state)
        image.save(filepath)
