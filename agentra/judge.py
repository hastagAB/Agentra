"""
LLM-as-judge for subjective evaluation.
"""

import os
from typing import Optional
from .types import Score


class Judge:
    """
    Uses an LLM to evaluate subjective criteria.
    
    Supports OpenAI and Anthropic (via environment variables).
    """
    
    def __init__(self, model: str = None):
        """
        Initialize judge.
        
        Args:
            model: Model to use. Defaults to GPT-4 if OpenAI key available,
                   or Claude if Anthropic key available.
        """
        self.model = model or self._get_default_model()
        self.client = None
        self.provider = None
        self._setup_client()
    
    def _get_default_model(self) -> str:
        """Determine default model based on available API keys."""
        if os.getenv("OPENAI_API_KEY"):
            return "gpt-4"
        elif os.getenv("ANTHROPIC_API_KEY"):
            return "claude-3-5-sonnet-20241022"
        else:
            return "gpt-4"  # Fallback
    
    def _setup_client(self):
        """Set up LLM client based on model."""
        if self.model.startswith("gpt"):
            self.provider = "openai"
            try:
                import openai
                self.client = openai.OpenAI()
            except ImportError:
                raise ImportError("openai package required for GPT models. Install: pip install openai")
        elif self.model.startswith("claude"):
            self.provider = "anthropic"
            try:
                import anthropic
                self.client = anthropic.Anthropic()
            except ImportError:
                raise ImportError("anthropic package required for Claude models. Install: pip install anthropic")
        else:
            # Try OpenAI as default
            self.provider = "openai"
            try:
                import openai
                self.client = openai.OpenAI()
            except ImportError:
                raise ImportError("openai or anthropic package required. Install: pip install openai")
    
    def evaluate(
        self,
        criteria: str,
        input: str,
        output: str,
        context: str = "",
    ) -> Score:
        """
        Evaluate using LLM-as-judge.
        
        Args:
            criteria: What to evaluate (e.g., "Is the output correct?")
            input: Input to the agent
            output: Output from the agent
            context: Additional context (system description, etc.)
        
        Returns:
            Score with value 0.0-1.0 and reasoning
        """
        
        prompt = self._build_prompt(criteria, input, output, context)
        
        try:
            response = self._call_llm(prompt)
            return self._parse_response(response)
        except Exception as e:
            # Fallback to neutral score on error
            return Score(
                value=0.5,
                reason=f"Judge evaluation failed: {str(e)}",
                details={"error": str(e)}
            )
    
    def _build_prompt(self, criteria: str, input: str, output: str, context: str) -> str:
        """Build evaluation prompt."""
        return f"""You are an expert evaluator of AI agent systems.

Evaluate the following based on this criteria: {criteria}

{f"System Context: {context}" if context else ""}

Input:
{input}

Output:
{output}

Provide your evaluation in the following format:
SCORE: [0.0 to 1.0]
REASON: [Brief explanation]

Be objective and precise. Consider:
- Does the output address the input?
- Is it correct and appropriate?
- Are there any errors or issues?

Your evaluation:"""
    
    def _call_llm(self, prompt: str) -> str:
        """Call LLM based on provider."""
        if self.provider == "openai":
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert AI agent evaluator. Provide objective, precise evaluations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500,
            )
            return response.choices[0].message.content
        
        elif self.provider == "anthropic":
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                temperature=0.3,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
        
        else:
            raise ValueError(f"Unknown provider: {self.provider}")
    
    def _parse_response(self, response: str) -> Score:
        """Parse LLM response into Score."""
        lines = response.strip().split("\n")
        
        score_value = 0.5
        reason = "Could not parse evaluation"
        
        for line in lines:
            line = line.strip()
            if line.startswith("SCORE:"):
                try:
                    score_str = line.replace("SCORE:", "").strip()
                    score_value = float(score_str)
                    score_value = max(0.0, min(1.0, score_value))  # Clamp to [0, 1]
                except ValueError:
                    pass
            elif line.startswith("REASON:"):
                reason = line.replace("REASON:", "").strip()
        
        # If no REASON: prefix found, use all text after score
        if reason == "Could not parse evaluation":
            # Find text after SCORE line
            score_line_idx = next((i for i, line in enumerate(lines) if "SCORE:" in line), -1)
            if score_line_idx >= 0 and score_line_idx < len(lines) - 1:
                reason = "\n".join(lines[score_line_idx + 1:]).strip()
                # Remove REASON: prefix if present
                if reason.startswith("REASON:"):
                    reason = reason.replace("REASON:", "").strip()
        
        return Score(
            value=score_value,
            reason=reason or "No reason provided",
            details={"raw_response": response}
        )

