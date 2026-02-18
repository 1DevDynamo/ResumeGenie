import streamlit as st
from datetime import datetime
import json
import os
from json_preview import build_live_payload
from llm import enhance_resume
from doc_gen import generate_docx_from_template


# --- DIRECTORY SETUP ---
DB_DIR = "dB"
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

# --- PAGE CONFIG ---
st.set_page_config(page_title="Resume Genie 🧞", layout="centered")

# --- INITIAL STATE ---
if 'resume' not in st.session_state:
    st.session_state.resume = {
        "education": [],
        "experience": [],
        "projects": [],
        "skills": [],
        "coursework": []
    }

if "generated_resume" not in st.session_state:
    st.session_state.generated_resume = None

if "has_generated" not in st.session_state:
    st.session_state.has_generated = False


# --- VALIDATION ---
def get_missing_fields(contacts, edu_list, exp_list, proj_list):
    missing = []

    def is_empty(val):
        return val is None or str(val).strip() == ""

    # --- CONTACT ---
    if is_empty(contacts.get('f_name')):
        missing.append("First Name")
    if is_empty(contacts.get('l_name')):
        missing.append("Last Name")
    if is_empty(contacts.get('email')):
        missing.append("Email")
    if is_empty(contacts.get('phone')):
        missing.append("Phone")

    # --- EDUCATION ---
    for i, edu in enumerate(edu_list):
        # Only validate if user started typing institute
        if is_empty(edu.get('institute')):
            continue

        # If institute exists, it's valid (required field satisfied)
        # No further action needed

    # --- EXPERIENCE ---
    for i, exp in enumerate(exp_list):
        if is_empty(exp.get('company')) and any([
            not is_empty(exp.get('role')),
            not is_empty(exp.get('desc'))
        ]):
            missing.append(f"Experience #{i+1} Company")

    # --- PROJECTS ---
    for i, proj in enumerate(proj_list):
        if is_empty(proj.get('name')) and any([
            not is_empty(proj.get('url')),
            not is_empty(proj.get('mem')),
            not is_empty(proj.get('desc'))
        ]):
            missing.append(f"Project #{i+1} Name")

    return missing


# --- HEADER ---
col_logo, col_actions = st.columns([3, 2])
with col_logo:
    st.title("Resume Genie 🧞✨")
    st.caption("Transforming your career path into a professional story 📖")

with col_actions:
    st.write("##")
    act1, act2, act3 = st.columns(3)
    show_history = act1.button("📜 History", use_container_width=True)
    save_trigger = act2.button("💾 Save", type="primary", use_container_width=True)
    reset_trigger = act3.button("🆕 New", use_container_width=True)


st.divider()

#Side Bar
st.sidebar.title("About")
# --- LIVE SIDEBAR JSON PREVIEW ---
st.sidebar.subheader("📦 Live JSON Payload")
live_payload = build_live_payload()
st.sidebar.json(live_payload)


# --- HISTORY ---
if show_history:
    with st.expander("📚 Saved Resumes (History)", expanded=True):
        files = [f for f in os.listdir(DB_DIR) if f.endswith('.json')]
        if not files:
            st.info("No saved resumes found in dB folder.")
        else:
            selected_file = st.selectbox("Select a resume to load:", files)
            if st.button("📥 Import Selected Resume"):
                with open(os.path.join(DB_DIR, selected_file), 'r') as f:
                    data = json.load(f)

                # 🔥 FULL RESET (safe version)
                for key in list(st.session_state.keys()):
                    del st.session_state[key]

                # 🔹 Reinitialize base structure
                st.session_state.resume = {
                    "education": data.get("education", []),
                    "experience": data.get("experience", []),
                    "projects": data.get("projects", []),
                    "skills": data.get("skills", []),
                    "coursework": data.get("coursework", [])
                }

                # 🔹 Restore contacts
                contacts = data.get("contacts", {})
                st.session_state["f_name"] = contacts.get("f_name", "")
                st.session_state["m_name"] = contacts.get("m_name", "")
                st.session_state["l_name"] = contacts.get("l_name", "")
                st.session_state["email"] = contacts.get("email", "")
                st.session_state["phone"] = contacts.get("phone", "")
                st.session_state["linked_in"] = contacts.get("linked_in", "")
                st.session_state["github"] = contacts.get("github", "")

                st.rerun()




# --- SAVE LOGIC ---
if save_trigger:

    contacts = {
        "f_name": st.session_state.get("f_name", ""),
        "m_name": st.session_state.get("m_name", ""),
        "l_name": st.session_state.get("l_name", ""),
        "email": st.session_state.get("email", ""),
        "phone": st.session_state.get("phone", ""),
        "linked_in": st.session_state.get("linked_in", ""),
        "github": st.session_state.get("github", "")
    }

    education = []
    for i in range(len(st.session_state.resume["education"])):
        education.append({
            "degree": st.session_state.get(f"deg_{i}", ""),
            "institute": st.session_state.get(f"inst_{i}", ""),
            "start": str(st.session_state.get(f"s_ed_{i}", "")),
            "end": str(st.session_state.get(f"e_ed_{i}", ""))
        })

    experience = []
    for i in range(len(st.session_state.resume["experience"])):
        experience.append({
            "company": st.session_state.get(f"comp_{i}", ""),
            "role": st.session_state.get(f"role_{i}", ""),
            "start": str(st.session_state.get(f"s_ex_{i}", "")),
            "end": str(st.session_state.get(f"e_ex_{i}", "")),
            "desc": st.session_state.get(f"desc_{i}", "")
        })

    projects = []
    for i in range(len(st.session_state.resume["projects"])):
        projects.append({
            "name": st.session_state.get(f"pj_name_{i}", ""),
            "url": st.session_state.get(f"pj_url_{i}", ""),
            "mem": st.session_state.get(f"pj_mem_{i}", ""),
            "desc": st.session_state.get(f"pj_desc_{i}", "")
        })

    save_payload = {
        "contacts": contacts,
        "education": education,
        "experience": experience,
        "projects": projects,
        "skills": st.session_state.resume["skills"],
        "coursework": st.session_state.resume["coursework"]
    }

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{contacts.get('f_name','User')}_{timestamp}.json"
    filepath = os.path.join(DB_DIR, filename)

    with open(filepath, "w") as f:
        json.dump(save_payload, f, indent=4)

    st.success(f"✅ Resume saved successfully as {filename}")

# --- RESET LOGIC ---
if reset_trigger:
    # Clear all session state
    for key in list(st.session_state.keys()):
        del st.session_state[key]

    # Reinitialize resume structure
    st.session_state.resume = {
        "education": [],
        "experience": [],
        "projects": [],
        "skills": [],
        "coursework": []
    }

    st.success("✨ Form Reset Successfully!")
    st.rerun()







# --- CONTACT ---
with st.container(border=True):
    st.subheader("👤 Contact Information")
    c1, c2 = st.columns(2)

    c1.text_input("First Name *", key="f_name")
    c2.text_input("Middle Name", key="m_name")
    c1.text_input("Last Name *", key="l_name")
    c2.text_input("Email *", key="email")
    c1.text_input("Phone *", key="phone")
    c2.text_input("LinkedIn", key="linked_in")
    st.text_input("GitHub", key="github")

# --- EDUCATION ---
st.write("##")
with st.container(border=True):
    ed_h1, ed_h2 = st.columns([4, 1.2])
    ed_h1.subheader("🎓 Education")

    if ed_h2.button("➕ Add Edu", key="add_edu"):
        st.session_state.resume["education"].append({})

    for i in range(len(st.session_state.resume["education"])):
        with st.container(border=True):
            e_col1, e_col2 = st.columns(2)
            e_col1.selectbox("📜 Degree", ["Bachelor's", "Master's", "PhD"], key=f"deg_{i}")
            e_col2.text_input("🏫 Institute *", key=f"inst_{i}")
            d_col1, d_col2 = st.columns(2)
            d_col1.date_input("📅 Start Date", key=f"s_ed_{i}")
            d_col2.date_input("🏁 End Date", key=f"e_ed_{i}")

            if st.button(f"🗑️ Remove Item {i+1}", key=f"rem_ed_{i}"):
                st.session_state.resume["education"].pop(i)
                st.rerun()

# --- EXPERIENCE ---
st.write("##")
with st.container(border=True):
    ex_h1, ex_h2 = st.columns([4, 1.2])
    ex_h1.subheader("💼 Experience")

    if ex_h2.button("➕ Add Exp", key="add_exp"):
        st.session_state.resume["experience"].append({})

    for i in range(len(st.session_state.resume["experience"])):
        with st.container(border=True):
            c_col1, c_col2 = st.columns(2)
            c_col1.text_input("🏢 Company *", key=f"comp_{i}")
            c_col2.text_input("🛠️ Role", key=f"role_{i}")
            d_col1, d_col2 = st.columns(2)
            d_col1.date_input("📅 Start Date", key=f"s_ex_{i}")
            d_col2.date_input("🏁 End Date", key=f"e_ex_{i}")
            st.text_area("📝 Description", key=f"desc_{i}")

            if st.button(f"🗑️ Remove Job {i+1}", key=f"rem_exp_{i}"):
                st.session_state.resume["experience"].pop(i)
                st.rerun()

# --- PROJECTS ---
st.write("##")
with st.container(border=True):
    pj_h1, pj_h2 = st.columns([4, 1.2])
    pj_h1.subheader("🚀 Projects")

    if pj_h2.button("➕ Add Project", key="add_pj"):
        st.session_state.resume["projects"].append({})

    for i in range(len(st.session_state.resume["projects"])):
        with st.container(border=True):
            p_col1, p_col2 = st.columns(2)
            p_col1.text_input("📛 Project Name *", key=f"pj_name_{i}")
            p_col2.text_input("🔗 Project URL", key=f"pj_url_{i}")
            st.text_input("👥 Members", key=f"pj_mem_{i}")
            st.text_area("📄 Description", key=f"pj_desc_{i}")

            if st.button(f"🗑️ Remove Project {i+1}", key=f"rem_pj_{i}"):
                st.session_state.resume["projects"].pop(i)
                st.rerun()

# --- Job Description ---
st.write("##")
with st.container(border=True):
    st.subheader("📄 Job Description")

    st.text_input("💼 Job Title", key="jd_title")
    st.text_area("📝 Job Description", key="jd_desc", height=150)
    st.text_area("🛠️ Skills Required (comma separated)", key="jd_skills", height=100)



# --- SKILLS & COURSEWORK ---
st.write("##")
g1, g2 = st.columns(2)

with g1:
    with st.container(border=True):
        st.subheader("⚡ Skills")
        if st.button("➕ Add Skill"):
            st.session_state.resume["skills"].append("")
        for i in range(len(st.session_state.resume["skills"])):
            st.session_state.resume["skills"][i] = st.text_input(f"S{i}", key=f"sk_{i}", label_visibility="collapsed")

with g2:
    with st.container(border=True):
        st.subheader("📚 Coursework")
        if st.button("➕ Add Course"):
            st.session_state.resume["coursework"].append("")
        for i in range(len(st.session_state.resume["coursework"])):
            st.session_state.resume["coursework"][i] = st.text_input(f"C{i}", key=f"co_{i}", label_visibility="collapsed")

# --- GENERATE ---
st.write("##")
with st.container(border=True):
    st.subheader("🧞 Generate Resume")

    if st.button("✨ Generate ATS Resume", use_container_width=True):

        contacts = {
            "f_name": st.session_state.get("f_name", ""),
            "m_name": st.session_state.get("m_name", ""),
            "l_name": st.session_state.get("l_name", ""),
            "email": st.session_state.get("email", ""),
            "phone": st.session_state.get("phone", ""),
            "linked_in": st.session_state.get("linked_in", ""),
            "github": st.session_state.get("github", "")
        }

        education = []
        for i in range(len(st.session_state.resume["education"])):
            education.append({
                "degree": st.session_state.get(f"deg_{i}", ""),
                "institute": st.session_state.get(f"inst_{i}", ""),
                "start": str(st.session_state.get(f"s_ed_{i}", "")),
                "end": str(st.session_state.get(f"e_ed_{i}", ""))
            })

        experience = []
        for i in range(len(st.session_state.resume["experience"])):
            experience.append({
                "company": st.session_state.get(f"comp_{i}", ""),
                "role": st.session_state.get(f"role_{i}", ""),
                "start": str(st.session_state.get(f"s_ex_{i}", "")),
                "end": str(st.session_state.get(f"e_ex_{i}", "")),
                "desc": st.session_state.get(f"desc_{i}", "")
            })

        projects = []
        for i in range(len(st.session_state.resume["projects"])):
            projects.append({
                "name": st.session_state.get(f"pj_name_{i}", ""),
                "url": st.session_state.get(f"pj_url_{i}", ""),
                "mem": st.session_state.get(f"pj_mem_{i}", ""),
                "desc": st.session_state.get(f"pj_desc_{i}", "")
            })

        

        missing = get_missing_fields(contacts, education, experience, projects)

        if missing:
            st.error(f"🚫 Missing: {', '.join(missing)}")
        else:
            
            final_payload = {
                "contacts": contacts,
                "education": education,
                "experience": experience,
                "projects": projects,
                "skills": st.session_state.resume["skills"],
                "coursework": st.session_state.resume["coursework"]
                }
            st.session_state.last_payload = final_payload

            
            # ✅ NEW: Separate JD payload
            jd_payload = {
                "job_title": st.session_state.get("jd_title", ""),
                "description": st.session_state.get("jd_desc", ""),
                "skills_required": st.session_state.get("jd_skills", "")
                }
            
            # ✅ UPDATED: Pass JD separately
            generated_resume = enhance_resume(
                resume_json=final_payload,
                job_description_json=jd_payload
                )
            
            st.session_state.generated_resume = generated_resume
            st.session_state.has_generated = True


            st.success("✅ Resume Generated Successfully!")
            st.json(generated_resume)

            
            # ✅ Generate DOCX file
            docx_file = generate_docx_from_template(generated_resume)

            
            # ✅ Provide DOCX download
            with open(docx_file, "rb") as f:
                st.download_button(
                    label="⬇️ Download Resume.docx",
                    data=f,
                    file_name="Generated_Resume.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                    )





# --- FEEDBACK SECTION ---
if st.session_state.has_generated and "last_payload" in st.session_state:

    with st.container(border=True):
        st.subheader("🔁 Improve Resume with Feedback")

        feedback_text = st.text_area(
            "Provide feedback to improve the resume",
            key="resume_feedback",
            height=120
        )

        if st.button("🚀 Regenerate with Feedback", use_container_width=True):


            jd_payload = {
                "job_title": st.session_state.get("jd_title", ""),
                "description": st.session_state.get("jd_desc", ""),
                "skills_required": st.session_state.get("jd_skills", "")
            }

            improved_resume = enhance_resume(
                resume_json=st.session_state.last_payload,
                job_description_json=jd_payload,
                feedback=feedback_text
            )

            st.session_state.generated_resume = improved_resume

            st.success("✅ Resume Improved Successfully!")

            st.text_area("Updated Resume", improved_resume, height=600)

            # 👇 NEW DOWNLOAD
            docx_file = generate_docx_from_template(improved_resume)

            with open(docx_file, "rb") as file:
                st.download_button(
                    label="📥 Download Improved Resume (.docx)",
                    data=file,
                    file_name="Improved_Resume.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
