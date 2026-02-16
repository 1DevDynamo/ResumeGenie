import requests
from openai import OpenAI
import os
import json
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if OPENROUTER_API_KEY is None:
    raise RuntimeError("OPENROUTER_API_KEY not found in environment")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

def load_latex_template(template_name="sample_resume_latex.tex"):
    template_path = os.path.join("templates", template_name)

    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template not found at {template_path}")

    with open(template_path, "r", encoding="utf-8") as file:
        return file.read()


# ✅ CRITICAL FIX → JSON CLEANER
def clean_json(data):
    if isinstance(data, dict):
        return {k: clean_json(v) for k, v in data.items() if v not in ["", [], [""]]}
    elif isinstance(data, list):
        return [clean_json(v) for v in data if v not in ["", None]]
    else:
        return data


def enhance_resume(resume_json, sample_resume_latex):

    cleaned_data = clean_json(resume_json)
    json_string = json.dumps(cleaned_data, indent=2)

    prompt = f"""
You are an expert ATS resume generation engine.

OBJECTIVE:
Generate a ready-to-print ATS-optimized technical resume.

STRICT RULES:
- Do NOT output LaTeX
- Do NOT output markdown
- Output plain professional resume text only
- Preserve section order strictly
- No decorative elements
- No hyphenated words
- Do NOT invent information

EMPTY CONTENT RULE:
If a section has no meaningful content → OMIT the entire section.

INPUT DATA (JSON):
{json_string}

REFERENCE TEMPLATE (STRUCTURE ONLY):
{sample_resume_latex}

OUTPUT REQUIREMENTS:
Return ONLY the resume content.
No explanations.
Deterministic output.
"""

    response = client.chat.completions.create(
        model="google/gemini-2.0-flash-001",
        messages=[
            {
                "role": "system",
                "content": "You are an expert ATS resume generator. You output clean recruiter-ready resumes."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    return response.choices[0].message.content
