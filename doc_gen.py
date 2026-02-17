from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH



def generate_docx(text, filename="resume.docx"):
    doc = Document()

    for line in text.split("\n"):

        line = line.strip()

        if not line:
            doc.add_paragraph("")  # preserve spacing
            continue

        # ✅ Detect section headings
        if line.lower() in [
            "education",
            "experience",
            "projects",
            "relevant coursework",
            "technical skills"
        ]:
            p = doc.add_paragraph()
            run = p.add_run(line.upper())
            run.bold = True
            run.font.size = Pt(14)
            continue

        # ✅ Detect bullet points
        if line.startswith("•"):
            p = doc.add_paragraph(style="List Bullet")
            p.add_run(line.replace("•", "").strip())
            continue

        # ✅ Header formatting (Name line = first non-empty line)
        if text.split("\n").index(line) == 0:
            p = doc.add_paragraph()
            run = p.add_run(line)
            run.bold = True
            run.font.size = Pt(16)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            continue

        # ✅ Normal content
        p = doc.add_paragraph(line)
        p.paragraph_format.space_after = Pt(4)

    doc.save(filename)
    return filename
