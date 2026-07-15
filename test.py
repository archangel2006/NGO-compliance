from pathlib import Path
from dotenv import load_dotenv
import os
import google.generativeai as genai

backend_dir = Path(__file__).parent / "backend"

loaded = load_dotenv(backend_dir / ".env")

print("Loaded:", loaded)
print("KEY:", os.getenv("GEMINI_API_KEY"))

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

for m in genai.list_models():
    print(m.name)