"""
Run this script to see which Gemini models your API key can access.
Usage: python check_models.py
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ GEMINI_API_KEY not found in .env file")
    exit(1)

genai.configure(api_key=api_key)

print("✅ API Key found. Fetching available models...\n")
print("=" * 60)

for model in genai.list_models():
    if "generateContent" in model.supported_generation_methods:
        print(f"✅ {model.name}")

print("=" * 60)
print("\n👆 Copy any model name above and update your .env:")
print('GEMINI_MODEL=gemini-1.5-flash   ← example')