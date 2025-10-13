from llmlingua import PromptCompressor
import json

compressor = PromptCompressor()

def compress_prompt(text):
    if text.startswith("EXPAND:"):
        return text[7:]  # linguagem natural
    compressed = compressor.compress_prompt(text, rate=0.04)  # 25x
    return compressed['compressed_prompt']

# Wrapper global
class CompressedLLM:
    def __init__(self, provider):
        self.provider = provider

    def call(self, prompt):
        compressed = compress_prompt(prompt)
        return self.provider.generate(compressed)

print("✅ LLM Compression System Active")
