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

        # ✅ Detect headings
        if line.lower() in [
            "education",
            "experience",
            "projects",
            "relevant coursework",
            "skills"
        ]:
            p = doc.add_paragraph()
            run = p.add_run(line)
            run.bold = True
            run.font.size = Pt(14)
            continue

        # ✅ Normal content
        p = doc.add_paragraph(line)
        p.paragraph_format.space_after = Pt(4)

    doc.save(filename)
    return filename
