import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Current working Groq models (as of 2026)
models_to_test = [
    "llama-3.3-70b-versatile",
    "llama-3.1-70b-versatile",
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768",
    "gemma2-9b-it"
]

print("Testing Groq models...\n")
working_models = []

for model in models_to_test:
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Say 'ok'"}],
            max_tokens=5
        )
        print(f"✅ {model} - WORKING")
        working_models.append(model)
    except Exception as e:
        error = str(e)
        if "decommissioned" in error:
            print(f"❌ {model} - DECOMMISSIONED")
        elif "api_key" in error.lower():
            print(f"❌ API KEY ERROR - Fix your .env file first!")
            break
        else:
            print(f"❌ {model} - {error[:80]}")

print(f"\n✅ Working models: {working_models}")