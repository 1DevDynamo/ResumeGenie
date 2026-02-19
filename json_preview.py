import streamlit as st
# --- LIVE PAYLOAD BUILDER ---
def build_live_payload():
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

    payload = {
        "contacts": contacts,
        "education": education,
        "experience": experience,
        "projects": projects,
        "skills": st.session_state.resume["skills"],
        "coursework": st.session_state.resume["coursework"],
        "job_description": {
            "title": st.session_state.get("jd_title", ""),
            "description": st.session_state.get("jd_desc", ""),
            "skills_required": st.session_state.get("jd_skills", "")
        }
    }

    return payload




# --- LIVE SIDEBAR JSON PREVIEW ---
# st.sidebar.subheader("📦 Live JSON Payload")
# live_payload = build_live_payload()
# st.sidebar.json(live_payload)
