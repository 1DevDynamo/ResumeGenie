import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from doc_gen import Document

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if OPENROUTER_API_KEY is None:
    raise RuntimeError("OPENROUTER_API_KEY not found")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

def load_docx_template(template_name="sample_template.docx"):  # ✅ FIXED CASE
    current_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(current_dir, "templates", template_name)

    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template not found at {template_path}")

    doc = Document(template_path)
    full_text = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    return "\n".join(full_text)

def clean_json(data):
    if isinstance(data, dict):
        cleaned = {}
        for k, v in data.items():
            v = clean_json(v)
            if v not in ["", None, [], {}]:
                cleaned[k] = v
        return cleaned
    elif isinstance(data, list):
        cleaned_list = [clean_json(v) for v in data]
        return [v for v in cleaned_list if v not in ["", None, {}, []]]
    return data


def enhance_resume(resume_json, sample_resume_latex):
    cleaned_data = clean_json(resume_json)
    json_string = json.dumps(cleaned_data, indent=2)

    prompt = f"""
You are a senior ATS resume optimization engine specialized in technical roles.

OBJECTIVE:
Generate a recruiter ready, ATS optimized, high impact technical resume.

STRICT OUTPUT RULES:
- Output plain professional text only
- Do NOT output LaTeX
- Do NOT output markdown
- Do NOT include explanations
- Do NOT include decorative symbols
- Do NOT use hyphenated words
- Do NOT invent or assume missing data
- Deterministic output required

STRUCTURE REQUIREMENTS:
You MUST strictly follow this exact section order and formatting:

1. Header
   NAME
   PHONE | EMAIL | LINKEDIN_URL | GITHUB_URL

2. Education
   DEGREE  DURATION
   INSTITUTION  GRADE

3. Experience
   ROLE — COMPANY  DURATION
   • Bullet
   • Bullet

4. Projects
   PROJECT TITLE
   • Bullet
   • Bullet

5. Relevant Coursework
   Bullet list in two rows separated by spaces

6. Technical Skills
   CATEGORY: skills comma separated

CRITICAL RULES:
Generate bullets points and all for projects,exp and all from the descrpition and inputs given.
SECTION ORDER:
Preserve section order exactly as defined above.
If a section has no meaningful content, omit the entire section.

BULLET RULES:
- Start each bullet with a strong technical action verb
- Rewrite weak bullets to be impact driven
- Add measurable metrics ONLY if clearly inferable from the input data
- Keep bullets concise and achievement focused
- Avoid generic phrases such as responsible for, worked on, helped with

ATS OPTIMIZATION:
- Optimize wording for Applicant Tracking Systems
- Use industry standard technical terminology
- Prioritize keywords relevant to software engineering and technical roles
- Maintain consistent formatting
- Avoid fancy characters

FORMATTING RULES:
- Use clean spacing between sections
- No extra commentary
- No placeholder text
- No brackets
- No assumptions

INPUT DATA (JSON):
{json_string}

REFERENCE TEMPLATE STRUCTURE:
{sample_resume_latex}

Return ONLY the final resume content.
"""

    response = client.chat.completions.create(
        model="google/gemini-2.0-flash-001",
        messages=[
            {"role": "system", "content": "You are a deterministic ATS resume generation engine."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    return response.choices[0].message.content
