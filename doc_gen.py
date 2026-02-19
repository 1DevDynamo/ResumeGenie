import os
import re
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from datetime import datetime



BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def set_margins(doc):
    section = doc.sections[0]
    section.top_margin = Inches(0.7)
    section.bottom_margin = Inches(0.7)
    section.left_margin = Inches(0.8)
    section.right_margin = Inches(0.8)


def set_font(run, size=11, bold=False):
    run.font.name = "Calibri"
    run.font.size = Pt(size)
    run.bold = bold


def add_section_title(doc, title):
    add_horizontal_line(doc)
    p = doc.add_paragraph()
    run = p.add_run(title.upper())
    set_font(run, 12, bold=True)
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(6)
    


def add_left_right_line(doc, left_text, right_text, bold_left=False):
    p = doc.add_paragraph()
    tab_stops = p.paragraph_format.tab_stops
    tab_stops.add_tab_stop(Inches(6.5), WD_TAB_ALIGNMENT.RIGHT)

    left_run = p.add_run(left_text)
    set_font(left_run, 11, bold_left)

    p.add_run("\t")

    right_run = p.add_run(right_text)
    set_font(right_run, 11, False)



def add_bullet(doc, text):
    p = doc.add_paragraph(style="List Bullet")

    pattern = r"\*\*(.*?)\*\*"
    last_end = 0

    for match in re.finditer(pattern, text):
        start, end = match.span()

        # Add normal text before bold
        if start > last_end:
            normal_text = text[last_end:start]
            run = p.add_run(normal_text)
            set_font(run)

        # Add bold text (without **)
        bold_text = match.group(1)
        run = p.add_run(bold_text)
        set_font(run, bold=True)

        last_end = end

    # Add remaining normal text
    if last_end < len(text):
        remaining_text = text[last_end:]
        run = p.add_run(remaining_text)
        set_font(run)

def add_horizontal_line(doc):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(6)

    p_pr = p._p.get_or_add_pPr()
    borders = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')

    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '6')      # thickness (increase for thicker line)
    bottom.set(qn('w:space'), '1')
    bottom.set(qn('w:color'), 'auto')

    borders.append(bottom)
    p_pr.append(borders)



def generate_docx_from_template(resume):

    doc = Document()
    set_margins(doc)

    # ================= HEADER =================
    header = resume.get("header", {})

    name_para = doc.add_paragraph()
    name_run = name_para.add_run(header.get("name", ""))
    set_font(name_run, 16, bold=True)
    name_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

    contact_line = " | ".join(
        filter(None, [
            header.get("phone", ""),
            header.get("email", ""),
            header.get("linkedin", ""),
            header.get("github", "")
        ])
    )

    if contact_line:
        contact_para = doc.add_paragraph()
        contact_run = contact_para.add_run(contact_line)
        set_font(contact_run)
        contact_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_horizontal_line(doc)


    # ================= SUMMARY =================
    summary = resume.get("summary", "").strip()
    if summary:
        add_section_title(doc, "Summary")
        p = doc.add_paragraph()
        run = p.add_run(summary)
        set_font(run, 11, bold=False)
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(8)

    # ================= EDUCATION =================
    education = resume.get("education", [])
    if education:
        add_section_title(doc, "Education")

        for edu in education:
            add_left_right_line(
                doc,
                edu.get("degree", ""),
                edu.get("duration", ""),
                bold_left=True
            )

            add_left_right_line(
                doc,
                edu.get("institution", ""),
                edu.get("grade", "")
            )

    # ================= EXPERIENCE =================
    experience = resume.get("experience", [])
    if experience:
        add_section_title(doc, "Experience")

        for exp in experience:
            role_company = f"{exp.get('role','')} — {exp.get('company','')}"
            add_left_right_line(
                doc,
                role_company,
                exp.get("duration", ""),
                bold_left=True
            )

            for bullet in exp.get("bullets", []):
                add_bullet(doc, bullet)

    # ================= PROJECTS =================
    projects = resume.get("projects", [])
    if projects:
        add_section_title(doc, "Projects")

        for proj in projects:
            title_para = doc.add_paragraph()
            title_run = title_para.add_run(proj.get("title", ""))
            set_font(title_run, 11, bold=True)

            for bullet in proj.get("bullets", []):
                add_bullet(doc, bullet)

    # ================= COURSEWORK =================
    coursework = resume.get("coursework", [])
    if coursework:
        add_section_title(doc, "Relevant Coursework")
        course_line = " • ".join(coursework)
        p = doc.add_paragraph(course_line)

    # ================= SKILLS =================
    skills = resume.get("skills", {})
    if skills:
        add_section_title(doc, "Technical Skills")

        for category, items in skills.items():
            line = f"{category}: {', '.join(items)}"
            p = doc.add_paragraph()
            run = p.add_run(line)
            set_font(run)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output = os.path.join(BASE_DIR, f"Generated_Resume_{timestamp}.docx")

    doc.save(output)

    return output
