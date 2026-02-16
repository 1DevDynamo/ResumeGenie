import streamlit as st
from datetime import datetime
import json
import os

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

# --- VALIDATION LOGIC ---
def get_missing_fields(contacts, edu_list, exp_list, proj_list):
    missing = []
    if not contacts['f_name'].strip(): missing.append("First Name")
    if not contacts['l_name'].strip(): missing.append("Last Name")
    if not contacts['email'].strip(): missing.append("Email")
    if not contacts['phone'].strip(): missing.append("Phone")
    for i, edu in enumerate(edu_list):
        if not edu.get('institute', '').strip(): missing.append(f"Education #{i+1} Institute")
    for i, exp in enumerate(exp_list):
        if not exp.get('company', '').strip(): missing.append(f"Experience #{i+1} Company")
    for i, proj in enumerate(proj_list):
        if not proj.get('name', '').strip(): missing.append(f"Project #{i+1} Name")
    return missing

# --- HEADER SECTION ---
col_logo, col_actions = st.columns([3, 2])
with col_logo:
    st.title("Resume Genie 🧞✨")
    st.caption("Transforming your career path into a professional story 📖")

with col_actions:
    st.write("##") 
    act1, act2 = st.columns(2)
    show_history = act1.button("📜 History", use_container_width=True)
    save_trigger = act2.button("💾 Save", type="primary", use_container_width=True)

st.divider()

# --- HISTORY MODAL (Overlay) ---
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
                    # Update session state
                    st.session_state.resume = data
                    st.success(f"Successfully loaded {selected_file}!")
                    st.rerun()

# --- CONTACT INFORMATION ---
with st.container(border=True):
    st.subheader("👤 Contact Information")
    c1, c2 = st.columns(2)
    contact_data = {
        'f_name': c1.text_input("First Name *", placeholder="👤 John", key="fn_val"),
        'm_name': c2.text_input("Middle Name", placeholder="💎 Optional", key="mn_val"),
        'l_name': c1.text_input("Last Name *", placeholder="Doe", key="ln_val"),
        'email': c2.text_input("Email *", placeholder="📧 john@example.com", key="em_val"),
        'phone': c1.text_input("Phone *", placeholder="📞 +1 (555) 000-0000", key="ph_val"),
        'linked_in': c2.text_input("LinkedIn", placeholder="🔗 https://linkedin.com/in/...", key="li_val"),
        'github': st.text_input("GitHub", placeholder="🐙 https://github.com/...", key="gh_val")
    }

# --- DYNAMIC SECTIONS ---

# EDUCATION
st.write("##")
with st.container(border=True):
    ed_h1, ed_h2 = st.columns([4, 1.2])
    ed_h1.subheader("🎓 Education")
    if ed_h2.button("➕ Add Edu", key="add_edu"):
        st.session_state.resume["education"].append({"degree": "Bachelor's", "institute": ""})
    for i, edu in enumerate(st.session_state.resume["education"]):
        with st.container(border=True):
            e_col1, e_col2 = st.columns(2)
            edu['degree'] = e_col1.selectbox("📜 Degree", ["Bachelor's", "Master's", "PhD"], key=f"deg_{i}", index=0)
            edu['institute'] = e_col2.text_input("🏫 Institute *", key=f"inst_{i}")
            d_col1, d_col2 = st.columns(2)
            edu['start'] = str(d_col1.date_input("📅 Start Date", key=f"s_ed_{i}")) # Save as string for JSON
            edu['end'] = str(d_col2.date_input("🏁 End Date", key=f"e_ed_{i}"))
            if st.button(f"🗑️ Remove Item {i+1}", key=f"rem_ed_{i}"):
                st.session_state.resume["education"].pop(i)
                st.rerun()

# EXPERIENCE
st.write("##")
with st.container(border=True):
    ex_h1, ex_h2 = st.columns([4, 1.2])
    ex_h1.subheader("💼 Experience")
    if ex_h2.button("➕ Add Exp", key="add_exp"):
        st.session_state.resume["experience"].append({"company": "", "role": ""})
    for i, exp in enumerate(st.session_state.resume["experience"]):
        with st.container(border=True):
            c_col1, c_col2 = st.columns(2)
            exp['company'] = c_col1.text_input("🏢 Company *", key=f"comp_{i}")
            exp['role'] = c_col2.text_input("🛠️ Role", key=f"role_{i}")
            d_col1, d_col2 = st.columns(2)
            exp['start'] = str(d_col1.date_input("📅 Start Date", key=f"s_ex_{i}"))
            exp['end'] = str(d_col2.date_input("🏁 End Date", key=f"e_ex_{i}"))
            exp['desc'] = st.text_area("📝 Description", key=f"desc_{i}")
            if st.button(f"🗑️ Remove Job {i+1}", key=f"rem_exp_{i}"):
                st.session_state.resume["experience"].pop(i)
                st.rerun()

# PROJECTS
st.write("##")
with st.container(border=True):
    pj_h1, pj_h2 = st.columns([4, 1.2])
    pj_h1.subheader("🚀 Projects")
    if pj_h2.button("➕ Add Project", key="add_pj"):
        st.session_state.resume["projects"].append({"name": ""})
    for i, project in enumerate(st.session_state.resume["projects"]):
        with st.container(border=True):
            p_col1, p_col2 = st.columns(2)
            project['name'] = p_col1.text_input("📛 Project Name *", key=f"pj_name_{i}")
            project['url'] = p_col2.text_input("🔗 Project URL", key=f"pj_url_{i}")
            project['mem'] = st.text_input("👥 Members", key=f"pj_mem_{i}")
            project['desc'] = st.text_area("📄 Description", key=f"pj_desc_{i}")
            if st.button(f"🗑️ Remove Project {i+1}", key=f"rem_pj_{i}"):
                st.session_state.resume["projects"].pop(i)
                st.rerun()

# SKILLS & COURSEWORK
st.write("##")
g1, g2 = st.columns(2)
with g1:
    with st.container(border=True):
        st.subheader("⚡ Skills")
        if st.button("➕ Add Skill"): st.session_state.resume["skills"].append("")
        for i in range(len(st.session_state.resume["skills"])):
            st.session_state.resume["skills"][i] = st.text_input(f"S{i}", key=f"sk_{i}", label_visibility="collapsed")
with g2:
    with st.container(border=True):
        st.subheader("📚 Coursework")
        if st.button("➕ Add Course"): st.session_state.resume["coursework"].append("")
        for i in range(len(st.session_state.resume["coursework"])):
            st.session_state.resume["coursework"][i] = st.text_input(f"C{i}", key=f"co_{i}", label_visibility="collapsed")

# --- SAVE DIALOG ---
if save_trigger:
    missing = get_missing_fields(contact_data, st.session_state.resume["education"], st.session_state.resume["experience"], st.session_state.resume["projects"])
    if missing:
        st.error(f"🚫 Missing: {', '.join(missing)}")
    else:
        st.session_state.show_save_dialog = True

if st.session_state.get('show_save_dialog'):
    with st.container(border=True):
        st.write("### 🏷️ Save Resume")
        file_name = st.text_input("Enter a name for this record:", placeholder="e.g. John_Software_Eng")
        if st.button("Confirm Save"):
            full_path = os.path.join(DB_DIR, f"{file_name}.json")
            if os.path.exists(full_path):
                st.warning("⚠️ This name already exists. Please choose another.")
            elif not file_name:
                st.warning("⚠️ Please enter a name.")
            else:
                # Merge contacts into the main resume object for saving
                final_data = {**st.session_state.resume, "contacts": contact_data}
                with open(full_path, "w") as f:
                    json.dump(final_data, f, indent=4)
                st.success(f"✅ Saved to {full_path}!")
                st.session_state.show_save_dialog = False