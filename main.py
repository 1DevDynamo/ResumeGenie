import streamlit as st
from datetime import datetime

# --- APP SETUP ---
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

# --- VALIDATION & SAVE FUNCTION ---
def handle_save(contacts, edu_list, exp_list, proj_list):
    # 1. Check Mandatory Contact Fields
    contact_reqs = {
        "First Name": contacts['f_name'],
        "Last Name": contacts['l_name'],
        "Email": contacts['email'],
        "Phone": contacts['phone']
    }
    
    missing = [label for label, value in contact_reqs.items() if not value or value.strip() == ""]
    
    # 2. Check Dynamic Sections (Mandatory if a row exists)
    for i, edu in enumerate(edu_list):
        if not edu.get('institute'): missing.append(f"Education #{i+1} Institute")
    
    for i, exp in enumerate(exp_list):
        if not exp.get('company'): missing.append(f"Experience #{i+1} Company")
        
    for i, proj in enumerate(proj_list):
        if not proj.get('name'): missing.append(f"Project #{i+1} Name")
    
    if missing:
        st.error(f"🚫 Cannot save! Missing: {', '.join(missing)}")
    else:
        st.success("💾 Resume saved successfully! Your story is ready. ✨")

# --- HEADER SECTION ---
col_logo, col_actions = st.columns([3, 2])
with col_logo:
    st.title("Resume Genie 🧞")
    st.caption("Transforming your career path into a professional story 📖")

with col_actions:
    st.write("##") 
    act1, act2 = st.columns(2)
    act1.button("📜 History", use_container_width=True)
    save_trigger = act2.button("💾 Save", type="primary", use_container_width=True)

st.divider()

# --- CONTACT INFORMATION ---
with st.container(border=True):
    st.subheader("👤 Contact Information")
    c1, c2 = st.columns(2)
    contact_data = {
        'f_name': c1.text_input("First Name *", placeholder="👤 John"),
        'm_name': c2.text_input("Middle Name", placeholder="💎 Optional"),
        'l_name': c1.text_input("Last Name *", placeholder="Doe"),
        'email': c2.text_input("Email *", placeholder="📧 john@example.com"),
        'phone': c1.text_input("Phone *", placeholder="📞 +1 (555) 000-0000"),
        'linked_in': c2.text_input("LinkedIn", placeholder="🔗 https://linkedin.com/in/..."),
        'github': st.text_input("GitHub", placeholder="🐙 https://github.com/...")
    }

# --- DYNAMIC SECTIONS ---

# EDUCATION
st.write("##")
with st.container(border=True):
    ed_h1, ed_h2 = st.columns([4, 1.2])
    ed_h1.subheader("🎓 Education")
    if ed_h2.button("➕ Add", key="add_edu"):
        st.session_state.resume["education"].append({"degree": "Bachelor's", "institute": ""})

    for i, edu in enumerate(st.session_state.resume["education"]):
        with st.container(border=True):
            e_col1, e_col2 = st.columns(2)
            edu['degree'] = e_col1.selectbox("📜 Degree", ["Bachelor's", "Master's", "PhD", "Certification"], key=f"deg_{i}")
            edu['institute'] = e_col2.text_input("🏫 Institute *", key=f"inst_{i}", placeholder="University Name")
            d_col1, d_col2 = st.columns(2)
            edu['start'] = d_col1.date_input("📅 Start Date", key=f"s_ed_{i}")
            edu['end'] = d_col2.date_input("🏁 End Date", key=f"e_ed_{i}")
            if st.button(f"🗑️ Remove", key=f"rem_ed_{i}"):
                st.session_state.resume["education"].pop(i)
                st.rerun()

# EXPERIENCE (UPDATED WITH DATES)
st.write("##")
with st.container(border=True):
    ex_h1, ex_h2 = st.columns([4, 1.2])
    ex_h1.subheader("💼 Experience")
    if ex_h2.button("➕ Add", key="add_exp"):
        st.session_state.resume["experience"].append({"company": "", "role": ""})

    for i, exp in enumerate(st.session_state.resume["experience"]):
        with st.container(border=True):
            c_col1, c_col2 = st.columns(2)
            exp['company'] = c_col1.text_input("🏢 Company *", key=f"comp_{i}", placeholder="Tech Corp")
            exp['role'] = c_col2.text_input("🛠️ Role", key=f"role_{i}", placeholder="Software Engineer")
            
            # New Date Fields for Experience
            date_col1, date_col2 = st.columns(2)
            exp['start'] = date_col1.date_input("📅 Start Date", key=f"s_ex_{i}")
            exp['end'] = date_col2.date_input("🏁 End Date", key=f"e_ex_{i}")
            
            exp['desc'] = st.text_area("📝 Description", key=f"desc_{i}", placeholder="Describe your achievements...")
            if st.button(f"🗑️ Remove Job", key=f"rem_exp_{i}"):
                st.session_state.resume["experience"].pop(i)
                st.rerun()

# PROJECTS
st.write("##")
with st.container(border=True):
    pj_h1, pj_h2 = st.columns([4, 1.2])
    pj_h1.subheader("🚀 Projects")
    if pj_h2.button("➕ Add", key="add_pj"):
        st.session_state.resume["projects"].append({"name": ""})

    for i, project in enumerate(st.session_state.resume["projects"]):
        with st.container(border=True):
            p_col1, p_col2 = st.columns(2)
            project['name'] = p_col1.text_input("📛 Project Name *", key=f"pj_name_{i}", placeholder="E-commerce App")
            project['url'] = p_col2.text_input("🔗 Project URL", key=f"pj_url_{i}", placeholder="https://github.com/...")
            project['mem'] = st.text_input("👥 Members", key=f"pj_mem_{i}", placeholder="Solo/Team")
            project['desc'] = st.text_area("📄 Description", key=f"pj_desc_{i}")
            if st.button(f"🗑️ Remove", key=f"rem_pj_{i}"):
                st.session_state.resume["projects"].pop(i)
                st.rerun()

# SKILLS & COURSEWORK
st.write("##")
grid_col1, grid_col2 = st.columns(2)
with grid_col1:
    with st.container(border=True):
        st.subheader("⚡ Skills")
        if st.button("➕ Add Skill"): st.session_state.resume["skills"].append("")
        for i in range(len(st.session_state.resume["skills"])):
            st.session_state.resume["skills"][i] = st.text_input(f"S{i}", key=f"sk_{i}", label_visibility="collapsed")

with grid_col2:
    with st.container(border=True):
        st.subheader("📚 Coursework")
        if st.button("➕ Add Course"): st.session_state.resume["coursework"].append("")
        for i in range(len(st.session_state.resume["coursework"])):
            st.session_state.resume["coursework"][i] = st.text_input(f"C{i}", key=f"co_{i}", label_visibility="collapsed")

# --- TRIGGER VALIDATION ---
if save_trigger:
    handle_save(
        contact_data, 
        st.session_state.resume["education"], 
        st.session_state.resume["experience"], 
        st.session_state.resume["projects"]
    )