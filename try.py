# app.py
import streamlit as st
import requests
from datetime import date
import uuid

# ---------------- CONFIG ----------------
PROJECT_ID = "YOUR_PROJECT_ID"
PUBLIC_ANON_KEY = "YOUR_PUBLIC_ANON_KEY"

SAVE_URL = f"https://{PROJECT_ID}.supabase.co/functions/v1/make-server-d0519db3/resume"
FETCH_URL = f"https://{PROJECT_ID}.supabase.co/functions/v1/make-server-d0519db3/resumes"

# ---------------- DEFAULT STATE ----------------
def init_state():
    if "contacts" not in st.session_state:
        st.session_state.contacts = {
            "f_name": "",
            "m_name": "",
            "l_name": "",
            "email": "",
            "linked_in": "",
            "github": "",
            "phone": "",
        }
    for key in ["education", "experience", "projects", "skills", "relevant_coursework"]:
        if key not in st.session_state:
            st.session_state[key] = []
    if "drawer_open" not in st.session_state:
        st.session_state.drawer_open = False

init_state()

# ---------------- SIDEBAR (DRAWER) ----------------
def load_history():
    headers = {"Authorization": f"Bearer {PUBLIC_ANON_KEY}"}
    r = requests.get(FETCH_URL, headers=headers)
    if r.ok:
        return r.json()
    return []

if st.sidebar.button("Close History"):
    st.session_state.drawer_open = False

if st.session_state.drawer_open:
    st.sidebar.title("Saved Resumes")
    resumes = load_history()
    for res in resumes:
        label = res.get("name") or f"{res['contacts']['f_name']} {res['contacts']['l_name']}"
        if st.sidebar.button(label):
            st.session_state.contacts = res["contacts"]
            st.session_state.education = res["education"]
            st.session_state.experience = res["experience"]
            st.session_state.projects = res["projects"]
            st.session_state.skills = res["skills"]
            st.session_state.relevant_coursework = res["relevant_coursework"]
            st.session_state.drawer_open = False
            st.success("Resume Loaded")

# ---------------- MAIN FORM ----------------
st.title("Resume Genie")
st.caption("Craft your professional story")

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("History"):
        st.session_state.drawer_open = True
with col2:
    st.button("Export")
with col3:
    submit = st.button("Save")

# CONTACTS
st.subheader("Contact Information")
c1, c2 = st.columns(2)
with c1:
    st.session_state.contacts["f_name"] = st.text_input("First Name", st.session_state.contacts["f_name"])
    st.session_state.contacts["l_name"] = st.text_input("Last Name", st.session_state.contacts["l_name"])
    st.session_state.contacts["phone"] = st.text_input("Phone", st.session_state.contacts["phone"])
with c2:
    st.session_state.contacts["m_name"] = st.text_input("Middle Name", st.session_state.contacts["m_name"])
    st.session_state.contacts["email"] = st.text_input("Email", st.session_state.contacts["email"])
    st.session_state.contacts["linked_in"] = st.text_input("LinkedIn", st.session_state.contacts["linked_in"])
st.session_state.contacts["github"] = st.text_input("GitHub", st.session_state.contacts["github"])

# EDUCATION
st.subheader("Education")
if st.button("Add Education"):
    st.session_state.education.append({"degree":"","institute":"","startDate":date.today(),"endDate":None,"percentage":""})

for i, edu in enumerate(st.session_state.education):
    with st.container():
        st.markdown(f"### Education {i+1}")
        edu["degree"] = st.selectbox("Degree", ["","High School","Associate","Bachelor","Master","PhD","Other"], key=f"deg{i}")
        edu["institute"] = st.text_input("Institute", edu["institute"], key=f"inst{i}")
        d1, d2 = st.columns(2)
        with d1:
            edu["startDate"] = st.date_input("Start Date", edu["startDate"], key=f"sd{i}")
        with d2:
            edu["endDate"] = st.date_input("End Date", edu["endDate"] or date.today(), key=f"ed{i}")
        edu["percentage"] = st.text_input("Percentage/GPA", edu["percentage"], key=f"perc{i}")
        if st.button("Remove", key=f"remedu{i}"):
            st.session_state.education.pop(i)
            st.experimental_rerun()

# EXPERIENCE
st.subheader("Experience")
if st.button("Add Experience"):
    st.session_state.experience.append({"company":"","role":"","startDate":date.today(),"endDate":None,"description":""})

for i, exp in enumerate(st.session_state.experience):
    with st.container():
        st.markdown(f"### Experience {i+1}")
        exp["company"] = st.text_input("Company", exp["company"], key=f"comp{i}")
        exp["role"] = st.text_input("Role", exp["role"], key=f"role{i}")
        d1, d2 = st.columns(2)
        with d1:
            exp["startDate"] = st.date_input("Start Date", exp["startDate"], key=f"esd{i}")
        with d2:
            exp["endDate"] = st.date_input("End Date", exp["endDate"] or date.today(), key=f"eed{i}")
        exp["description"] = st.text_area("Description", exp["description"], key=f"desc{i}")
        if st.button("Remove", key=f"remexp{i}"):
            st.session_state.experience.pop(i)
            st.experimental_rerun()

# PROJECTS
st.subheader("Projects")
if st.button("Add Project"):
    st.session_state.projects.append({"name":"","url":"","members":"","description":""})

for i, proj in enumerate(st.session_state.projects):
    with st.container():
        proj["name"] = st.text_input("Project Name", proj["name"], key=f"pn{i}")
        proj["url"] = st.text_input("URL", proj["url"], key=f"pu{i}")
        proj["members"] = st.text_input("Members", proj["members"], key=f"pm{i}")
        proj["description"] = st.text_area("Description", proj["description"], key=f"pd{i}")
        if st.button("Remove", key=f"remproj{i}"):
            st.session_state.projects.pop(i)
            st.experimental_rerun()

# SKILLS & COURSEWORK
c1, c2 = st.columns(2)

with c1:
    st.subheader("Skills")
    if st.button("Add Skill"):
        st.session_state.skills.append({"skill":""})
    for i, s in enumerate(st.session_state.skills):
        s["skill"] = st.text_input("Skill", s["skill"], key=f"skill{i}")
        if st.button("X", key=f"remskill{i}"):
            st.session_state.skills.pop(i)
            st.experimental_rerun()

with c2:
    st.subheader("Relevant Coursework")
    if st.button("Add Course"):
        st.session_state.relevant_coursework.append({"course":""})
    for i, c in enumerate(st.session_state.relevant_coursework):
        c["course"] = st.text_input("Course", c["course"], key=f"course{i}")
        if st.button("X", key=f"remcourse{i}"):
            st.session_state.relevant_coursework.pop(i)
            st.experimental_rerun()

# ---------------- SAVE ----------------
if submit:
    payload = {
        "id": str(uuid.uuid4()),
        "createdAt": date.today().isoformat(),
        "contacts": st.session_state.contacts,
        "education": st.session_state.education,
        "experience": st.session_state.experience,
        "projects": st.session_state.projects,
        "skills": st.session_state.skills,
        "relevant_coursework": st.session_state.relevant_coursework,
    }
    headers = {
        "Content-Type":"application/json",
        "Authorization": f"Bearer {PUBLIC_ANON_KEY}"
    }
    r = requests.post(SAVE_URL, json=payload, headers=headers)
    if r.ok:
        st.success("Resume saved successfully!")
    else:
        st.error("Failed to save resume")
