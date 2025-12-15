"""
LLM Client Wrapper (OpenAI).

Description:
- Manages communication with Large Language Models (OpenAI GPT-4o-mini).
- Constructs prompts using finding context and parses JSON responses.
- Standardizes output to: { "is_false_positive": bool, "reason": str, "confidence": float }

Connections:
- Called by ml_pipeline.py for high-complexity cases (Layer 3).
- Requires valid OPENAI_API_KEY in config.py.
"""

import json
from app.config import settings

def analyze_with_llm(finding_dict: dict):
    """
    Analyzes a potential secret using an LLM.
    Returns: { "is_false_positive": bool, "reason": str, "confidence": float }
    """
    
    # Check Configuration
    # -------------------
    api_key = settings.OPENAI_API_KEY
    if not api_key:
        return {"is_false_positive": False, "reason": "LLM not configured", "confidence": 0.0}

    from openai import OpenAI
    client = OpenAI(api_key=api_key)

    snippet = finding_dict.get("secret_snippet", "")
    file_path = finding_dict.get("file_path", "")
    rule_id = finding_dict.get("rule_id", "")

    # Construct Prompt
    # ----------------
    # Instructs the LLM to act as a security expert and output strict JSON.
    prompt = f"""
    You are a security expert. Analyze this potential secret finding.
    
    File: {file_path}
    Rule: {rule_id}
    Snippet: "{snippet}"
    
    Is this a False Positive (safe/test data) or a True Positive (actual secret)?
    Reply in JSON format:
    {{
        "is_false_positive": boolean,
        "reason": "Human-readable explanation why (concise)",
        "confidence": float (0.0 to 1.0)
    }}
    """

    try:
        # API Call
        # --------
        # Uses standard chat completion with JSON mode enabled.
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        print(f"LLM Error: {e}")
        return {"is_false_positive": False, "reason": f"LLM Error: {str(e)}", "confidence": 0.0}

