import requests
import json
import os

BASE_URL = "http://127.0.0.1:8000"
ARTIFACT_PATH = "/Users/sahil_khohari/.gemini/antigravity-ide/brain/1931f5dc-20bb-4b64-a0b5-e74b9a40d0a5/ai_verification.md"

def test_ai_endpoint():
    print("Testing /ai/ask-business-question...")
    payload = {
        "question": "Which product generated the highest total profit, and what was the profit margin?"
    }
    
    try:
        resp = requests.post(f"{BASE_URL}/ai/ask-business-question", json=payload)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        data = {"error": str(e), "details": resp.text if 'resp' in locals() else ""}
    
    print("Writing to artifact...")
    with open(ARTIFACT_PATH, "w") as f:
        f.write("# GenAI Text-to-SQL Response Verification\n\n")
        f.write("## Question\n")
        f.write(f"> {payload['question']}\n\n")
        
        f.write("## Final Response\n")
        f.write("```json\n")
        f.write(json.dumps(data, indent=2))
        f.write("\n```\n")
        
    print("Done!")

if __name__ == "__main__":
    test_ai_endpoint()
