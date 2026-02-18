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


def load_docx_template(template_name="Sample_Template.docx"):
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


def enhance_resume(resume_json, job_description_json, Sample_Template, feedback=None):

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
- Output a JSON object only
- Do NOT output LaTeX
- Do NOT output markdown
- Do NOT include explanations
- Do NOT include decorative symbols
- Do NOT use hyphenated words
- Do NOT invent or assume missing data unless explicitly allowed
- Deterministic output required

REFERENCE FORMAT:
Use sample_template.docx strictly as formatting reference.
Maintain professional recruiter friendly layout.

STRUCTURE REQUIREMENTS:
You MUST strictly follow this exact section order and formatting:

1. Header
                                                  NAME
                                PHONE | EMAIL | LINKEDIN_URL | GITHUB_URL
_________________________________________________________________________________________________________

1. {{Profession Ats freindly Job Description Based Summary}}

_________________________________________________________________________________________________________

2. Education
   DEGREE                                                                 DURATION(yy/mm/dd - yy/mm/dd)
   INSTITUTION                                                                         GRADE
_________________________________________________________________________________________________________

3. Experience
   ROLE — COMPANY                                                         DURATION(yy/mm/dd - yy/mm/dd)
   • Bullet
   • Bullet
   • Bullet
_________________________________________________________________________________________________________ 

4. Projects
   PROJECT TITLE
   • Bullet
   • Bullet
_________________________________________________________________________________________________________
5. Relevant Coursework
   Bullet list in two rows separated by spaces
_________________________________________________________________________________________________________

6. Technical Skills
   CATEGORY: skills comma separated


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
- Omit empty sections completely
- If fewer than 2 projects exist → generate relevant project aligned to Job Description
- Generated project MUST be realistic, technical, and JD relevant
- Do NOT fabricate employment experience
- Do NOT invent certifications or degrees

Experience Generation Rules:
- should align with job description have 2 bullet point least
- Maximum 3 bullets in accordance to job description if not exp not given
- Do not add experience if not given

PROJECT GENERATION RULES:
- Only trigger if resume lacks sufficient projects
- There should be atleast 3 projects according to the Job Description.
- Must appear authentic and technically credible
- Must align with candidate skill profile
- Must follow bullet rules strictly

Summary Rules:
- Should Align with Project and Job description
- Should be humanized
- ATS freindly
- No irrelevnant info
- Atleast 3 lines and max 5 lines

Skills and Courswork GENERATION RULES:
- Should have 5 bullet skills
- should have 5 bullet coursworks
- relevant to project and job description

FORMATTING RULES:
- Same as sample_template 
- Date and Grade should be at right most of the row
- Clean spacing between sections
- Strict alignment
- No placeholders
- No commentary
- Insert separator line after each section

If feedback is provided, revise the resume strictly according to feedback while maintaining ATS optimization.
Do not ignore feedback.

==============================
RESUME DATA (JSON):
{resume_string}

JOB DESCRIPTION (JSON):
{jd_string}

REFERENCE TEMPLATE:
{Sample_Template}

FEEDBACK FROM USER (if any):
{feedback if feedback else "No additional feedback provided."}
==============================

Return ONLY the final resume content.
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

    return response.choices[0].message.content
