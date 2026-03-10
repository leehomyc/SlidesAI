"""
LLM Client Abstraction Layer
Supports Google Gemini, OpenRouter, OpenAI, and Anthropic (Claude) APIs
"""

import os
import json
from typing import Optional

# Try to load configuration
try:
    from project_secrets import GEMINI_API_KEY
except ImportError:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

try:
    from project_secrets import OPENROUTER_API_KEY
except ImportError:
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

try:
    from project_secrets import OPENAI_API_KEY
except ImportError:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

try:
    from project_secrets import ANTHROPIC_API_KEY
except ImportError:
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Default provider: "google", "openrouter", "openai", or "anthropic"
try:
    from project_secrets import LLM_PROVIDER
except ImportError:
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "google")

# Default model per provider (used when model=None is passed to generate())
DEFAULT_MODELS = {
    "google": "gemini-3-pro-preview",
    "openrouter": "gemini-3-pro-preview",
    "openai": "gpt-5.2",
    "anthropic": "claude-opus-4-6",
}


class LLMClient:
    """Unified LLM client interface"""

    def __init__(self, provider: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize LLM client

        Args:
            provider: "google", "openrouter", "openai", or "anthropic"
            api_key: Optional API key; falls back to project_secrets / environment variable
        """
        self.provider = provider or LLM_PROVIDER
        self.api_key = api_key

        if self.provider == "google":
            self._init_google()
        elif self.provider == "openrouter":
            self._init_openrouter()
        elif self.provider == "openai":
            self._init_openai()
        elif self.provider == "anthropic":
            self._init_anthropic()
        else:
            raise ValueError(
                f"Unsupported provider: {self.provider}. "
                "Choose from: 'google', 'openrouter', 'openai', 'anthropic'"
            )

    def _init_google(self):
        """Initialize Google Gemini client"""
        key = self.api_key or GEMINI_API_KEY
        if not key:
            raise ValueError("GEMINI_API_KEY is not set (provide api_key or set environment variable)")

        from google import genai
        self.google_client = genai.Client(api_key=key)
        print("[LLM] Using Google Gemini API")

    def _init_openrouter(self):
        """Initialize OpenRouter client (using OpenAI SDK)"""
        key = self.api_key or OPENROUTER_API_KEY
        if not key:
            raise ValueError("OPENROUTER_API_KEY is not set (provide api_key or set environment variable)")

        from openai import OpenAI
        self.openai_client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=key,
            timeout=300.0,
            default_headers={
                "HTTP-Referer": "https://ai-ppt-generator.app",
                "X-Title": "AI PPT Generator",
            },
        )
        print("[LLM] Using OpenRouter API")

    def _init_openai(self):
        """Initialize direct OpenAI client"""
        key = self.api_key or OPENAI_API_KEY
        if not key:
            raise ValueError("OPENAI_API_KEY is not set (provide api_key or set environment variable)")

        from openai import OpenAI
        self.openai_client = OpenAI(api_key=key, timeout=300.0)
        print("[LLM] Using OpenAI API")

    def _init_anthropic(self):
        """Initialize Anthropic (Claude) client"""
        key = self.api_key or ANTHROPIC_API_KEY
        if not key:
            raise ValueError("ANTHROPIC_API_KEY is not set (provide api_key or set environment variable)")

        import anthropic
        self.anthropic_client = anthropic.Anthropic(api_key=key)
        print("[LLM] Using Anthropic (Claude) API")

    def generate(self, prompt: str, model: Optional[str] = None, json_mode: bool = True) -> str:
        """
        Generate text.

        Args:
            prompt: Prompt text
            model: Model name. If None, uses the default for the current provider.
                   Google format names (e.g. "gemini-3-pro-preview") are auto-converted for OpenRouter.
                   For OpenAI use e.g. "gpt-5.2"; for Anthropic use e.g. "claude-sonnet-4-6".
            json_mode: Whether to request JSON output

        Returns:
            Generated text content
        """
        resolved_model = model or DEFAULT_MODELS.get(self.provider, "")

        if self.provider == "google":
            return self._generate_google(prompt, resolved_model, json_mode)
        elif self.provider == "openrouter":
            return self._generate_openrouter(prompt, resolved_model, json_mode)
        elif self.provider == "openai":
            return self._generate_openai(prompt, resolved_model, json_mode)
        elif self.provider == "anthropic":
            return self._generate_anthropic(prompt, resolved_model, json_mode)

    def _generate_google(self, prompt: str, model: str, json_mode: bool) -> str:
        """Generate via Google Gemini API"""
        from google.genai import types

        config = types.GenerateContentConfig(response_mime_type="application/json") if json_mode else None

        response = self.google_client.models.generate_content(
            model=model,
            contents=prompt,
            config=config,
        )
        return response.text

    def _generate_openrouter(self, prompt: str, model: str, json_mode: bool) -> str:
        """Generate via OpenRouter API"""
        model_mapping = {
            "gemini-3-pro-preview": "google/gemini-3-pro-preview",
            "gemini-3-flash-preview": "google/gemini-3-flash-preview",
            "gemini-2.5-pro": "google/gemini-2.5-pro",
            "gemini-2.5-flash": "google/gemini-2.5-flash",
            "gemini-2.0-flash": "google/gemini-2.0-flash",
            "gemini-1.5-pro": "google/gemini-1.5-pro",
            "gemini-1.5-flash": "google/gemini-1.5-flash",
            "claude-opus-4-6": "anthropic/claude-opus-4-6",
            "claude-sonnet-4-6": "anthropic/claude-sonnet-4-6",
            "gpt-5.2": "openai/gpt-5.2",
            "gpt-4o": "openai/gpt-4o",
        }
        openrouter_model = model_mapping.get(model, model)
        print(f"[LLM] Calling OpenRouter with model: {openrouter_model}")

        kwargs = {
            "model": openrouter_model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 16000,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        try:
            response = self.openai_client.chat.completions.create(**kwargs)
            result = response.choices[0].message.content
            print(f"[LLM] Response received, length: {len(result)} chars")
            return result
        except Exception as e:
            print(f"[LLM] OpenRouter API error: {e}")
            raise

    def _generate_openai(self, prompt: str, model: str, json_mode: bool) -> str:
        """Generate via OpenAI API"""
        print(f"[LLM] Calling OpenAI with model: {model}")

        kwargs = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 16000,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        try:
            response = self.openai_client.chat.completions.create(**kwargs)
            result = response.choices[0].message.content
            print(f"[LLM] Response received, length: {len(result)} chars")
            return result
        except Exception as e:
            print(f"[LLM] OpenAI API error: {e}")
            raise

    def _generate_anthropic(self, prompt: str, model: str, json_mode: bool) -> str:
        """Generate via Anthropic (Claude) API"""
        print(f"[LLM] Calling Anthropic with model: {model}")

        system = "Respond with valid JSON only. Do not include any explanation or markdown fences." if json_mode else None

        try:
            kwargs = {
                "model": model,
                "max_tokens": 16000,
                "messages": [{"role": "user", "content": prompt}],
            }
            if system:
                kwargs["system"] = system

            response = self.anthropic_client.messages.create(**kwargs)
            result = response.content[0].text
            print(f"[LLM] Response received, length: {len(result)} chars")
            return result
        except Exception as e:
            print(f"[LLM] Anthropic API error: {e}")
            raise


# Global singleton
_client: Optional[LLMClient] = None


def get_llm_client(provider: Optional[str] = None, api_key: Optional[str] = None) -> LLMClient:
    """Get (or create) the LLM client singleton."""
    global _client

    if _client is None:
        _client = LLMClient(provider, api_key=api_key)
    elif (provider and _client.provider != provider) or (api_key and _client.api_key != api_key):
        _client = LLMClient(provider or _client.provider, api_key=api_key)

    return _client


def generate_content(
    prompt: str,
    model: Optional[str] = None,
    json_mode: bool = True,
    provider: Optional[str] = None,
    api_key: Optional[str] = None,
) -> str:
    """
    Convenience function: generate content via the configured LLM provider.

    Args:
        prompt: Prompt text
        model: Model name (None = use provider default)
        json_mode: Whether to request JSON output
        provider: Override the default provider ("google", "openrouter", "openai", "anthropic")
        api_key: Optional API key for the provider

    Returns:
        Generated text
    """
    client = get_llm_client(provider, api_key=api_key)
    return client.generate(prompt, model, json_mode)
