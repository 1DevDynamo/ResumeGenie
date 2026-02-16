import streamlit as st
import json
from llm import enhance_resume, load_latex_template
from doc_gen import generate_docx

st.set_page_config(page_title="Resume Genie", layout="centered")

st.title("Resume Genie")

resume = {}

# Contacts
with st.expander("Contacts"):
    resume["contacts"] = {
        "f_name": st.text_input("First Name"),
        "m_name": st.text_input("Middle Name"),
        "l_name": st.text_input("Last Name"),
        "email": st.text_input("Email"),
        "linked_in": st.text_input("Linked In"),
        "github": st.text_input("Github"),
        "phone": st.text_input("Phone"),
    }

# Education
with st.expander("Education"):
    resume["education"] = {
        "degree": st.text_input("Degree"),
        "institute": st.text_input("Institute"),
        "year": st.text_input("Year"),
        "Percent_CGPA": st.text_input("Percent / CGPA"),
    }

# Experience
with st.expander("Experience"):
    resume["experience"] = {
        "company": st.text_input("Company"),
        "role": st.text_input("Role"),
        "years": st.text_input("Years"),
    }

# Projects
with st.expander("Projects"):
    resume["projects"] = {
        "P_name": st.text_input("Project Name"),
        "P_description": st.text_input("Project Description"),
        "members": st.text_input("Members"),
        "url": st.text_input("URL"),
    }

# Relevant CourseWork
with st.expander("Relevant CourseWork"):
    coursework = st.text_input("Relevant Coursework (comma separated)")
    resume["Relevant CourseWork"] = [s.strip() for s in coursework.split(",") if s.strip()]

# Skills
with st.expander("Technical Skills"):
    skills = st.text_input("Skills (comma separated)")
    resume["skills"] = [s.strip() for s in skills.split(",") if s.strip()]

with st.sidebar.expander("Live Json Preview"):
    st.json(resume)

if st.button("Generate AI Resume"):

    try:
        s_resume = load_latex_template()
        enhanced = enhance_resume(resume, s_resume)
        file = generate_docx(enhanced)

        st.success("Resume generated!")

        with open(file, "rb") as f:
            st.download_button("Download Resume", f, file_name="resume.docx")

    except Exception as e:
        st.error(f"Error generating resume: {e}")
