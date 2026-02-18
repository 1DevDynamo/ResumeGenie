import os
import json
import re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if OPENROUTER_API_KEY is None:
    raise RuntimeError("OPENROUTER_API_KEY not found")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

def safe_json_parse(raw):
    raw = raw.strip()

    # Remove markdown fences
    raw = re.sub(r"^```(?:json)?", "", raw)
    raw = re.sub(r"```$", "", raw)

    # Extract first JSON object from text
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        raise ValueError("Model did not return JSON:\n" + raw)

    json_text = match.group(0)
    return json.loads(json_text)



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


def enhance_resume(resume_json, job_description_json, feedback=None):

    cleaned_resume = clean_json(resume_json)
    cleaned_jd = clean_json(job_description_json)

    resume_string = json.dumps(cleaned_resume, indent=2)
    jd_string = json.dumps(cleaned_jd, indent=2)

    prompt = f"""
You are a senior ATS resume optimization engine specialized in technical roles.

OBJECTIVE:
Generate a recruiter ready, ATS optimized, high impact technical resume
tailored specifically to the provided Job Description.

STRICT OUTPUT RULES:
- Return ONLY valid JSON. No surrounding text.
- Do NOT output LaTeX
- Do NOT output markdown
- Do NOT include explanations
- Do NOT include decorative symbols
- No trailing commas
- No comments
- No extra keys
- Must be parseable by json.loads()


STRUCTURE REQUIREMENTS:
You MUST strictly follow this exact key structure:

Structure:
{{
  "header": {{
    "name": "",
    "phone": "",
    "email": "",
    "linkedin": "",
    "github": ""
  }},
  "summary": "",
  "education": [
    {{
      "degree": "",
      "institution": "",
      "grade": "",
      "duration": ""
    }}
  ],
  "experience": [
    {{
      "role": "",
      "company": "",
      "duration": "",
      "bullets": []
    }}
  ],
  "projects": [
    {{
      "title": "",
      "bullets": []
    }}
  ],
  "coursework": [],
  "skills": {{
    "Category": []
  }}
}}


BULLET RULES (CRITICAL):
- Atleast 2 bullets per experience
- Maximum 2 bullets per project
- Each bullet ≤ 12 words
- Force metric driven impact where possible
- Start with strong technical action verbs
- No weak phrases
- No generic wording
- No repetition of verbs

ATS OPTIMIZATION RULES:
- Aggressively align wording with Job Description keywords
- Prioritize skills mentioned in Job Description
- Strengthen impact statements
- Maintain technical professional tone
- Avoid fluff

SMART CONTENT LOGIC:
- If fewer than 2 projects exist → generate relevant project aligned to Job Description
- Generated project MUST be realistic, technical, and JD relevant
- Do NOT fabricate employment experience
- Do NOT invent certifications or degrees

Experience Generation Rules:
- Should align with job description have 2 sentences. least
- Maximum 3 sentences. in accordance to job description if not exp not given
- Do not add experience if not given

PROJECT GENERATION RULES:
- Only trigger if resume lacks sufficient projects
- There should be atleast 3 projects according to the Job Description if enough projects not given.
- Must appear authentic and technically credible
- Must align with candidate skill profile
- Must follow bullet rules strictly

Summary Rules:
- Should Align with Project and Job description
- Should be humanized
- ATS freindly
- No irrelevnant info
- Atleast 3 – 5 sentences.

Skills and Courswork GENERATION RULES:
- Should have 5 bullet skills
- should have 5 bullet coursworks
- relevant to project and job description

FORMATTING RULES:
- Clean spacing between sections
- Strict alignment
- Do not return empty fields; omit keys if data unavailable.
- No commentary

If feedback is provided, revise the resume strictly according to feedback while maintaining ATS optimization.
Do not ignore feedback.

==============================
RESUME DATA (JSON):
{resume_string}

JOB DESCRIPTION (JSON):
{jd_string}


FEEDBACK FROM USER (if any):
{feedback if feedback else "No additional feedback provided."}
==============================

Return ONLY the ATS freindly json file.
"""

    response = client.chat.completions.create(
        model="google/gemini-2.0-flash-001",
        messages=[
            {
                "role": "system",
                "content": "You are a deterministic ATS resume generation engine."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    raw = response.choices[0].message.content

    print("RAW MODEL OUTPUT:\n", raw)   # temporary debug

    return safe_json_parse(raw)


