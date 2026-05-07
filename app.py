import streamlit as st
import pandas as pd
import os
import json

from utils.resume_parser import extract_resume_text


# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Skill Gap Analyser",
    page_icon="🎯",
    layout="centered"
)
# ---------------- MODERN UI DESIGN ----------------
st.markdown("""
<style>

/* ===== Main Background ===== */
.stApp {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: white;
    font-family: 'Segoe UI', sans-serif;s
}

/* ===== Headers ===== */
h1, h2, h3 {
    color: #ffffff;
    font-weight: 600;
}

/* ===== Section Cards ===== */
.block-container {
    padding-top: 2rem;
}

div[data-testid="stVerticalBlock"] > div {
    background: rgba(255, 255, 255, 0.05);
    padding: 20px;
    border-radius: 15px;
    backdrop-filter: blur(10px);
    box-shadow: 0px 6px 20px rgba(0,0,0,0.3);
    margin-bottom: 20px;
}

/* ===== Buttons ===== */
.stButton>button {
    background: linear-gradient(90deg, #6C63FF, #3F3D9B);
    color: white;
    border-radius: 10px;
    height: 3em;
    width: 100%;
    font-weight: 600;
    border: none;
    transition: 0.3s ease;
}

.stButton>button:hover {
    transform: scale(1.03);
    background: linear-gradient(90deg, #3F3D9B, #6C63FF);
}

/* ===== Input Fields ===== */
input, textarea, select {
    border-radius: 8px !important;
}

/* ===== Progress Bar ===== */
.stProgress > div > div > div > div {
    background-color: #6C63FF;
}

/* ===== Sidebar ===== */
section[data-testid="stSidebar"] {
    background-color: #111827;
}

/* ===== Success / Warning / Info boxes ===== */
div[data-testid="stAlert"] {
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE INIT ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "page" not in st.session_state:
    st.session_state.page = "details"

if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False


# ================== GLOBAL SKILL MASTER DATABASE ==================
SKILL_MASTER = {

    # ================= IT & SOFTWARE =================
    "IT & Software": [
        "Python", "Java", "C++", "C#", "Go", "Rust",
        "HTML", "CSS", "JavaScript", "TypeScript",
        "React", "Angular", "Vue.js",
        "Node.js", "Express.js",
        "Django", "Flask", "Spring Boot",
        "REST API", "GraphQL",
        "Git", "GitHub", "GitLab",
        "Linux", "Shell Scripting",
        "Docker", "Kubernetes",
        "CI/CD", "DevOps",
        "AWS", "Azure", "Google Cloud",
        "Cybersecurity", "Ethical Hacking"
    ],

    # ================= DATA SCIENCE & AI =================
    "Data Science & AI": [
        "Machine Learning", "Deep Learning",
        "Data Analysis", "Data Mining",
        "Data Visualization",
        "Power BI", "Tableau", "Excel",
        "Pandas", "NumPy", "SciPy",
        "TensorFlow", "PyTorch", "Keras",
        "Natural Language Processing",
        "Computer Vision",
        "Big Data", "Hadoop", "Spark",
        "Statistics", "Probability",
        "Time Series Analysis", "A/B Testing"
    ],

    # ================= CLOUD & DEVOPS =================
    "Cloud & DevOps": [
        "AWS", "Azure", "Google Cloud",
        "Docker", "Kubernetes",
        "Terraform", "Ansible",
        "CI/CD Pipelines",
        "Jenkins", "GitHub Actions",
        "Monitoring", "Prometheus",
        "Cloud Architecture"
    ],

    # ================= CYBERSECURITY =================
    "Cybersecurity": [
        "Network Security",
        "Ethical Hacking",
        "Penetration Testing",
        "SOC Operations",
        "SIEM",
        "Cryptography",
        "Risk Assessment",
        "Incident Response"
    ],

    # ================= ENGINEERING =================
    "Engineering": [
        "AutoCAD", "SolidWorks", "CATIA",
        "MATLAB", "ANSYS",
        "PLC Programming",
        "Embedded Systems",
        "Robotics",
        "Circuit Design",
        "Structural Analysis",
        "Quality Control",
        "Production Planning"
    ],

    # ================= FINANCE & ACCOUNTING =================
    "Finance & Accounting": [
        "Accounting", "Taxation",
        "GST", "Income Tax",
        "Auditing",
        "Tally", "SAP FICO",
        "Financial Analysis",
        "Budgeting",
        "Investment Analysis",
        "Risk Management"
    ],

    # ================= MARKETING =================
    "Marketing & Sales": [
        "Digital Marketing",
        "SEO", "SEM",
        "Social Media Marketing",
        "Brand Management",
        "Email Marketing",
        "Content Marketing",
        "Google Ads",
        "Market Research",
        "Lead Generation",
        "CRM Tools"
    ],

    # ================= HEALTHCARE =================
    "Healthcare": [
        "Clinical Research",
        "Medical Coding",
        "Medical Billing",
        "Patient Care",
        "Healthcare Management",
        "Public Health",
        "Hospital Administration"
    ],

    # ================= HR & OPERATIONS =================
    "HR & Operations": [
        "Recruitment",
        "Payroll Management",
        "Performance Management",
        "Employee Engagement",
        "Operations Management",
        "Supply Chain Management",
        "Vendor Management"
    ],

    # ================= UI/UX & DESIGN =================
    "UI/UX & Design": [
        "UI/UX Design",
        "Figma",
        "Adobe XD",
        "Wireframing",
        "Prototyping",
        "User Research",
        "Interaction Design",
        "Usability Testing"
    ],

    # ================= SOFT SKILLS =================
    "Soft Skills": [
        "Communication",
        "Public Speaking",
        "Leadership",
        "Teamwork",
        "Problem Solving",
        "Critical Thinking",
        "Time Management",
        "Adaptability",
        "Emotional Intelligence",
        "Conflict Resolution",
        "Negotiation",
        "Presentation Skills",
        "Creativity",
        "Decision Making",
        "Work Ethics",
        "Stress Management",
        "Interpersonal Skills"
    ]
}


ALL_SKILLS = sorted(
    {skill for skills in SKILL_MASTER.values() for skill in skills}
)


# ================== MODULE 1: AUTH ==================
if not st.session_state.logged_in:

    st.title("🎯 Skill Gap Analyser")

    def load_users():
        if os.path.exists("users.json"):
            with open("users.json", "r") as f:
                return json.load(f)
        return {}

    def save_users(users):
        with open("users.json", "w") as f:
            json.dump(users, f)

    users = load_users()

    auth_option = st.radio("Select Option", ["Login", "Sign Up"])

    if auth_option == "Login":

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if username in users and users[username] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.page = "details"
                st.rerun()
            else:
                st.error("Invalid credentials")

    else:

        new_username = st.text_input("Create Username")
        new_password = st.text_input("Create Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        if st.button("Sign Up"):
            if new_username in users:
                st.error("Username exists")
            elif new_password != confirm_password:
                st.error("Passwords do not match")
            else:
                users[new_username] = new_password
                save_users(users)
                st.success("Account created! Please login.")


# ================== MODULE 2: PROFILE ==================
elif st.session_state.page == "details":

    st.title("👤 User Profile Setup")
    st.write(f"Welcome **{st.session_state.username}** 👋")

    # ---------- Academic ----------
    st.subheader("🎓 Academic Details")

    full_name = st.text_input("Full Name")
    age = st.number_input("Age", 18, 60)
    qualification = st.selectbox(
        "Highest Qualification",
        ["Select", "Diploma", "UG", "PG", "PhD", "Other"]
    )

    st.divider()

    # ---------- Technical Skills ----------
    st.subheader("💻 Technical Skills (Mandatory)")

    technical_domains = [key for key in SKILL_MASTER.keys() if key != "Soft Skills"]

    selected_domain = st.selectbox(
        "Select Technical Domain",
        technical_domains
    )

    selected_technical_skills = st.multiselect(
        "Choose Technical Skills",
        options=SKILL_MASTER[selected_domain]
    )

    st.divider()

    # ---------- Soft Skills ----------
    st.subheader("🤝 Soft Skills (Mandatory)")

    selected_soft_skills = st.multiselect(
        "Choose Soft Skills",
        options=SKILL_MASTER["Soft Skills"]
    )

    st.divider()

    # ---------- Validation ----------
    if st.button("Proceed to Resume Upload"):

        if not full_name or qualification == "Select":
            st.error("Please fill required details")

        elif not selected_technical_skills:
            st.error("Please select at least one Technical Skill")

        elif not selected_soft_skills:
            st.error("Please select at least one Soft Skill")

        else:
            st.session_state.skills_data = (
                selected_technical_skills + selected_soft_skills
            )
            st.session_state.page = "resume"
            st.rerun()


# ================== MODULE 3: RESUME + ATS ==================
elif st.session_state.page == "resume":

    import matplotlib.pyplot as plt
    import numpy as np

    st.title("📄 Resume Upload & ATS Analysis")

    uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx"])

    if uploaded_file is not None:

        os.makedirs("uploads", exist_ok=True)
        path = os.path.join("uploads", uploaded_file.name)

        with open(path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        resume_text = extract_resume_text(path)

        if resume_text and resume_text.strip() != "":
            st.session_state.resume_text = resume_text
            st.success("✅ Resume uploaded successfully")

            resume_text_lower = resume_text.lower()

            # ------------------ ATS SCORE LOGIC ------------------
            def calculate_ats_score(text):

                score = 0
                word_count = len(text.split())

                # Length check
                if word_count > 300:
                    score += 20

                # Section keywords
                sections = ["experience", "education", "skills", "project"]
                for sec in sections:
                    if sec in text:
                        score += 10

                # Skill presence
                detected_skills = {
                    skill.lower()
                    for skill in ALL_SKILLS
                    if skill.lower() in text
                }

                score += min(len(detected_skills) * 2, 40)

                return min(score, 100), detected_skills

            ats_score, resume_skills = calculate_ats_score(resume_text_lower)

            st.session_state.resume_skills = resume_skills
            st.session_state.ats_score = ats_score

            # ------------------ SEMI DONUT CHART ------------------
            st.subheader("📊 ATS Score")

            fig, ax = plt.subplots()

            ax.pie(
                [ats_score, 100 - ats_score],
                startangle=180,
                wedgeprops=dict(width=0.4)
            )

            ax.text(0, -0.1, f"{ats_score}%", 
                    ha='center', fontsize=20, fontweight='bold')

            ax.set_aspect('equal')
            st.pyplot(fig)
            plt.close(fig)

            # Score Feedback
            if ats_score >= 80:
                st.success("🚀 Excellent ATS Score!")
            elif ats_score >= 60:
                st.info("👍 Good Resume. Minor improvements possible.")
            else:
                st.warning("⚠️ Improve resume structure & keywords.")

            # ------------------ SHOW DETECTED SKILLS ------------------
            st.subheader("🧠 Resume Skills Detected")

            if resume_skills:
                st.write(", ".join(resume_skills))
            else:
                st.warning("No recognizable skills detected.")

        else:
            st.error("❌ Could not extract resume text")

    # Proceed button
    if "resume_text" in st.session_state and st.session_state.resume_text.strip() != "":
        if st.button("Proceed to Analysis"):
            st.session_state.page = "analysis"
            st.rerun()

# ================== MODULE 4: ANALYSIS ==================
elif st.session_state.page == "analysis":

    st.title("🔍 Skill Gap Analysis")

    resume_text = st.session_state.get("resume_text", "").lower()

    if resume_text == "":
        st.warning("No resume found. Please upload again.")
        st.session_state.page = "resume"
        st.rerun()

    def extract_skills(text):
        return {skill.lower() for skill in ALL_SKILLS if skill.lower() in text}

    resume_skills = extract_skills(resume_text)

    st.subheader("📄 Resume Skills Detected")
    st.write(", ".join(resume_skills) if resume_skills else "None detected")

    jd_text = st.text_area("Paste Job Description")

    # ================= ANALYZE BUTTON =================
    if st.button("Analyze"):

        if jd_text.strip() == "":
            st.warning("Please paste Job Description")
        else:
            jd_skills = extract_skills(jd_text.lower())

            matched = resume_skills & jd_skills
            missing = jd_skills - resume_skills

            percent = (
                len(matched) / (len(matched) + len(missing)) * 100
                if jd_skills else 0
            )

            # ✅ Save results to session_state
            st.session_state.matched_skills = matched
            st.session_state.missing_skills = missing
            st.session_state.match_percent = percent
            st.session_state.analysis_done = True

    # ================= SHOW RESULTS AFTER ANALYSIS =================
    if st.session_state.get("analysis_done", False):

        matched = st.session_state.get("matched_skills", set())
        missing = st.session_state.get("missing_skills", set())
        percent = st.session_state.get("match_percent", 0)

        st.subheader("Results")
        st.write("✅ Matched:", ", ".join(matched) if matched else "None")
        st.write("❌ Missing:", ", ".join(missing) if missing else "None")

        st.progress(int(percent))
        st.write(f"Match Percentage: {percent:.2f}%")

        # 🚀 OUTSIDE ANALYZE BUTTON
        if st.button("🚀 Go to Dashboard"):
            st.session_state.page = "dashboard"
            st.rerun()

# ================== MODULE 5: DASHBOARD ==================
elif st.session_state.page == "dashboard":

    import matplotlib.pyplot as plt
    import numpy as np

    st.title("📊 Final Skill Gap Dashboard")

    matched = st.session_state.get("matched_skills", set())
    missing = st.session_state.get("missing_skills", set())
    percent = st.session_state.get("match_percent", 0)

    matched_count = len(matched)
    missing_count = len(missing)

    # ---------- Score Section ----------
    st.subheader("🎯 Overall Match Score")
    st.progress(int(percent))
    st.markdown(f"### ✅ {percent:.2f}% Match")

    st.divider()

    # ================== 📊 MODERN VISUALIZATION SECTION ==================
    st.subheader("📈 Advanced Skill Comparison Analytics")

    # -------- 1️⃣ Horizontal Bar Chart --------
    st.markdown("### 🔹 Matched vs Missing Skills (Horizontal View)")

    fig1, ax1 = plt.subplots()
    ax1.barh(
        ["Matched Skills", "Missing Skills"],
        [matched_count, missing_count]
    )
    ax1.set_xlabel("Number of Skills")
    ax1.set_title("Skill Comparison Overview")

    st.pyplot(fig1)
    plt.close(fig1)

    # -------- 2️⃣ Donut Chart --------
    st.markdown("### 🔹 Skill Match Distribution (Donut Chart)")

    fig2, ax2 = plt.subplots()
    ax2.pie(
        [matched_count, missing_count],
        labels=["Matched", "Missing"],
        autopct="%1.1f%%",
        wedgeprops=dict(width=0.4)
    )
    ax2.set_title("Skill Match Percentage")

    st.pyplot(fig2)
    plt.close(fig2)

    # -------- 3️⃣ Radar Chart --------
    st.markdown("### 🔹 Skill Performance Radar")

    categories = ["Matched", "Missing"]
    values = [matched_count, missing_count]

    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()

    values += values[:1]
    angles += angles[:1]

    fig3, ax3 = plt.subplots(subplot_kw=dict(polar=True))
    ax3.plot(angles, values)
    ax3.fill(angles, values, alpha=0.25)

    ax3.set_xticks(angles[:-1])
    ax3.set_xticklabels(categories)
    ax3.set_title("Skill Gap Radar View")

    st.pyplot(fig3)
    plt.close(fig3)

    st.divider()

    # ---------- Matched Skills ----------
    st.subheader("🟢 Matched Skills")

    if matched:
        for skill in matched:
            st.success(skill)
    else:
        st.info("No matched skills found.")

    st.divider()

    # ---------- Missing Skills ----------
    st.subheader("🔴 Missing Skills (Recommended to Learn)")

    if missing:
        for skill in missing:
            st.warning(skill)
    else:
        st.success("No missing skills 🎉")

    st.divider()

    # ---------- Recommendation Logic ----------
    st.subheader("📌 Recommendation")

    if percent >= 75:
        st.success("🎉 Excellent match! You are highly suitable for this role.")
    elif percent >= 50:
        st.info("👍 Moderate match. Upskill in missing areas to improve chances.")
    else:
        st.error("⚠️ Low match. Consider learning missing skills before applying.")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔄 New Analysis"):
            st.session_state.page = "analysis"
            st.rerun()

    with col2:
        if st.button("🏠 Back to Profile"):
            st.session_state.page = "details"
            st.rerun()
