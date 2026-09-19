"""
LLM Workspace Global — Prompt Compression Engine
Hardened against token-amplification DoS via EXPAND: injection [VULN-A2]
"""
import os
import hmac
import hashlib
import json
from llmlingua import PromptCompressor

compressor = PromptCompressor()

EXPAND_SECRET = os.environ.get("LLM_EXPAND_SECRET", "")
MAX_UNCOMPRESSED_CHARS = int(os.environ.get("MAX_UNCOMPRESSED_CHARS", "8000"))

def compress_prompt(text: str, auth_token: str = None) -> str:
    """
    Compress prompt using LLMLingua-2 with strict bounds and expansion gating.
    Mitigates arbitrary token-amplification DoS via EXPAND: injection.
    """
    if text.startswith("EXPAND:"):
        payload = text[7:]
        # If an expand secret is configured in environment, require constant-time match
        if EXPAND_SECRET:
            if auth_token and hmac.compare_digest(auth_token, EXPAND_SECRET):
                if len(payload) <= MAX_UNCOMPRESSED_CHARS:
                    return payload
            # Unauthorized or over-budget expansion request: fall back to compression
        else:
            # When no secret is enforced, restrict expansion to safe length budget
            if len(payload) <= MAX_UNCOMPRESSED_CHARS:
                return payload

    compressed = compressor.compress_prompt(text, rate=0.04)  # 25x
    return compressed['compressed_prompt']

# Wrapper global
class CompressedLLM:
    def __init__(self, provider, auth_token: str = None):
        self.provider = provider
        self.auth_token = auth_token

    def call(self, prompt: str, auth_token: str = None):
        token = auth_token or self.auth_token
        compressed = compress_prompt(prompt, auth_token=token)
        return self.provider.generate(compressed)

if __name__ == "__main__":
    print("✅ LLM Compression System Active (Hardened against Token-Amplification DoS)")
