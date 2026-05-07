import os
import json
import re
import secrets
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from utils.resume_parser import extract_resume_text

app = Flask(__name__, static_folder='.')
CORS(app)

# ================== GLOBAL SKILL MASTER DATABASE ==================
SKILL_MASTER = {

    # ================= IT & SOFTWARE =================
    "IT & Software": [
        "Python", "Java", "C++", "C#", "Go", "Rust", "Swift", "Kotlin", "PHP", "Ruby",
        "HTML", "CSS", "JavaScript", "TypeScript", "React", "Angular", "Vue.js", "Next.js",
        "Node.js", "Express.js", "Django", "Flask", "Spring Boot", "ASP.NET",
        "REST API", "GraphQL", "SOAP", "Microservices",
        "Git", "GitHub", "GitLab", "Bitbucket",
        "Linux", "Shell Scripting", "PowerShell",
        "Docker", "Kubernetes", "Jenkins", "Ansible", "Terraform",
        "AWS", "Azure", "Google Cloud", "Heroku",
        "SQL", "NoSQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch",
        "System Design", "Algorithms", "Data Structures"
    ],

    # ================= DATA SCIENCE & AI =================
    "Data Science & AI": [
        "Machine Learning", "Deep Learning", "Neural Networks",
        "Data Analysis", "Data Mining", "Data Visualization",
        "Power BI", "Tableau", "Looker", "Excel",
        "Pandas", "NumPy", "SciPy", "Scikit-learn",
        "TensorFlow", "PyTorch", "Keras", "OpenCV",
        "Natural Language Processing (NLP)", "Large Language Models (LLMs)", "Generative AI",
        "Computer Vision", "Reinforcement Learning",
        "Big Data", "Hadoop", "Spark", "Kafka", "Hive",
        "Statistics", "Probability", "Linear Algebra", "Calculus",
        "Time Series Analysis", "A/B Testing", "Experiment Design",
        "MLOps", "Model Deployment"
    ],

    # ================= CLOUD & DEVOPS =================
    "Cloud & DevOps": [
        "AWS (EC2, S3, Lambda)", "Azure (DevOps, Functions)", "Google Cloud Platform",
        "Docker", "Kubernetes", "Helm", "Istio",
        "Terraform", "CloudFormation", "Ansible", "Chef", "Puppet",
        "CI/CD Pipelines", "Jenkins", "GitHub Actions", "GitLab CI",
        "Prometheus", "Grafana", "ELK Stack", "Splunk", "Datadog",
        "Linux Administration", "Bash Scripting", "Networking",
        "Serverless Architecture", "Microservices"
    ],

    # ================= CYBERSECURITY =================
    "Cybersecurity": [
        "Network Security", "Application Security", "Cloud Security",
        "Ethical Hacking", "Penetration Testing", "Vulnerability Assessment",
        "SOC Operations", "SIEM (Splunk, QRadar)", "Incident Response",
        "Cryptography", "PKI", "Identity & Access Management (IAM)",
        "Risk Assessment", "Compliance (GDPR, HIPAA, SOC2)",
        "Firewall Configuration", "Wireshark", "Metasploit", "Nmap",
        "Malware Analysis", "Forensics"
    ],

    # ================= FINANCE & ACCOUNTING =================
    "Finance & Accounting": [
        "Financial Accounting", "Management Accounting", "Cost Accounting",
        "Taxation", "GST", "Income Tax", "Corporate Tax",
        "Auditing", "Internal Audit", "Forensic Accounting",
        "Financial Analysis", "Financial Modeling", "Valuation",
        "Budgeting", "Forecasting", "Cash Flow Management",
        "Investment Analysis", "Portfolio Management", "Wealth Management",
        "Risk Management", "Compliance", "Anti-Money Laundering (AML)",
        "Excel (Advanced)", "Tally", "SAP FICO", "QuickBooks", "Xero", "Oracle Financials"
    ],

    # ================= MARKETING & ADVERTISING =================
    "Marketing & Advertising": [
        "Digital Marketing", "Traditional Marketing",
        "SEO (Search Engine Optimization)", "SEM (Search Engine Marketing)",
        "Social Media Marketing", "Content Marketing", "Email Marketing",
        "Brand Management", "Public Relations (PR)",
        "Google Ads", "Facebook Ads", "LinkedIn Ads", "Google Analytics",
        "Market Research", "Consumer Behavior", "Competitive Analysis",
        "Copywriting", "Creative Direction", "Campaign Management",
        "CRM Tools (Salesforce, HubSpot)", "Marketing Automation"
    ],

    # ================= SALES & BUSINESS DEVELOPMENT =================
    "Sales & Business Dev": [
        "B2B Sales", "B2C Sales", "Enterprise Sales",
        "Lead Generation", "Cold Calling", "Prospecting",
        "Account Management", "Client Relationship Management",
        "Negotiation", "Closing Skills", "Sales Strategy",
        "Business Development", "Strategic Partnerships",
        "Salesforce", "Zoho CRM", "HubSpot",
        "Pipeline Management", "Forecasting", "Sales Presentation"
    ],

    # ================= HR & OPERATIONS =================
    "HR & Operations": [
        "Talent Acquisition", "Recruitment", "Sourcing",
        "Employee Relations", "Performance Management",
        "Payroll Management", "Compensation & Benefits",
        "HR Compliance", "Labor Laws",
        "Learning & Development", "Training",
        "HRIS (Workday, BambooHR)",
        "Operations Management", "Process Improvement", "Six Sigma", "Lean Management",
        "Supply Chain Management", "Logistics", "Procurement", "Vendor Management",
        "Inventory Management", "Project Management"
    ],

    # ================= ENGINEERING (CORE) =================
    "Engineering (Core)": [
        "AutoCAD", "SolidWorks", "CATIA", "Revit",
        "MATLAB", "Simulink", "ANSYS",
        "PLC Programming", "SCADA",
        "Embedded Systems", "Microcontrollers",
        "Circuit Design", "PCB Design",
        "Structural Analysis", "Thermodynamics", "Fluid Mechanics",
        "Civil Engineering", "Mechanical Engineering", "Electrical Engineering",
        "Quality Control", "Quality Assurance", "ISO Standards",
        "Production Planning", "Manufacturing Processes"
    ],

    # ================= HEALTHCARE & MEDICAL =================
    "Healthcare & Medical": [
        "Clinical Research", "Clinical Trials",
        "Medical Coding", "Medical Billing", "ICD-10",
        "Patient Care", "Nursing", "Vital Signs Monitoring",
        "Healthcare Management", "Hospital Administration",
        "Public Health", "Epidemiology",
        "Pharmacy", "Pharmacovigilance",
        "Radiology", "Lab Technology"
    ],

    # ================= LEGAL =================
    "Legal": [
        "Corporate Law", "Criminal Law", "Civil Law",
        "Contract Law", "Drafting", "Litigation",
        "Intellectual Property (IP)", "Patents", "Trademarks",
        "Compliance", "Regulatory Affairs",
        "Legal Research", "Due Diligence", "Mediation", "Arbitration"
    ],

    # ================= EDUCATION & TRAINING =================
    "Education & Training": [
        "Curriculum Design", "Instructional Design",
        "Classroom Management", "E-Learning",
        "Teaching", "Tutoring", "Mentoring",
        "Educational Technology", "LMS Administration",
        "Special Education", "Student Counseling"
    ],

    # ================= CREATIVE & DESIGN =================
    "Creative & Design": [
        "Graphic Design", "Illustration", "Typography",
        "UI/UX Design", "Wireframing", "Prototyping",
        "Adobe Photoshop", "Adobe Illustrator", "Adobe InDesign",
        "Figma", "Sketch", "Adobe XD",
        "Video Editing", "Premiere Pro", "After Effects",
        "3D Modeling", "Blender", "Maya",
        "Photography", "Videography"
    ],

    # ================= HOSPITALITY & TOURISM =================
    "Hospitality & Tourism": [
        "Hotel Management", "Front Desk Operations",
        "Food & Beverage", "Culinary Arts",
        "Event Management", "Travel Planning",
        "Customer Service", "Guest Relations"
    ],

    # ================= CONSTRUCTION & REAL ESTATE =================
    "Construction & Real Estate": [
        "Project Management", "Site Supervision",
        "Estimation", "Costing",
        "Civil Engineering", "Architecture",
        "Real Estate Sales", "Property Management",
        "Urban Planning", "Safety Management"
    ],

    # ================= SOFT SKILLS =================
    "Soft Skills": [
        "Communication", "Public Speaking", "Storytelling",
        "Leadership", "Teamwork", "Collaboration",
        "Problem Solving", "Critical Thinking", "Analytical Skills",
        "Time Management", "Organization", "Prioritization",
        "Adaptability", "Flexibility", "Resilience",
        "Emotional Intelligence", "Empathy",
        "Conflict Resolution", "Negotiation", "Mediation",
        "Creativity", "Innovation",
        "Decision Making", "Strategic Thinking",
        "Work Ethics", "Integrity", "Accountability",
        "Stress Management",
        "Interpersonal Skills", "Networking"
    ]
}

ALL_SKILLS = sorted(
    {skill for skills in SKILL_MASTER.values() for skill in skills}
)

# ================== HELPER FUNCTIONS ==================
def load_users():
    if os.path.exists("users.json"):
        try:
            with open("users.json", "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f)

def calculate_ats_score(text):
    score = 0
    text_lower = text.lower()
    word_count = len(text.split())

    # 1. Contact Information (Max 15)
    contact_score = 0
    if re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text):
        contact_score += 5
    if re.search(r'\+?\d[\d -]{8,}\d', text):
        contact_score += 5
    if "linkedin.com/in/" in text_lower or "linkedin.com" in text_lower:
        contact_score += 5
    score += contact_score

    # 2. Section Structure (Max 25)
    section_score = 0
    section_keywords = {
        "Experience": ["experience", "work history", "employment", "professional background"],
        "Education": ["education", "academic", "qualifications"],
        "Skills": ["skills", "technical skills", "core competencies", "expertise"],
        "Projects": ["projects", "personal projects", "portfolio"],
        "Summary": ["summary", "profile", "objective", "about me"]
    }
    for section, keywords in section_keywords.items():
        if any(kw in text_lower for kw in keywords):
            section_score += 5
    score += section_score

    # 3. Measurable Achievements (Max 20)
    # Look for numbers/metrics followed by action words or percentage signs
    achievement_patterns = [
        r'\d+%', # Percentage
        r'\$\d+', # Dollars
        r'\d+\s*\+', # 10+ years, etc.
        r'(increased|improved|reduced|managed|led|saved|achieved)\s+\w*\s*\d+' # managed 10 people, increased 20%
    ]
    achievement_count = sum(len(re.findall(pattern, text_lower)) for pattern in achievement_patterns)
    score += min(achievement_count * 4, 20)

    # 4. Skills Content (Max 30)
    detected_skills = {
        skill
        for skill in ALL_SKILLS
        if skill.lower() in text_lower
    }
    # Score based on number of skills found
    skill_score = min(len(detected_skills) * 1.5, 30)
    score += skill_score

    # 5. Formatting & Length (Max 10)
    formatting_score = 0
    # Length check (Optimized for 300-600 words)
    if 300 <= word_count <= 800:
        formatting_score += 5
    elif 150 <= word_count < 300 or 800 < word_count <= 1200:
        formatting_score += 3
        
    # Bullet point check
    if any(line.strip().startswith(('•', '-', '*')) for line in text.split('\n')):
        formatting_score += 5
    
    score += formatting_score

    return min(round(score), 100), list(detected_skills)

def extract_skills_from_text(text):
    return [skill for skill in ALL_SKILLS if skill.lower() in text]

# ================== ROUTES ==================

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    users = load_users()
    
    if username in users and users[username] == password:
        return jsonify({"success": True, "message": "Login successful"})
    return jsonify({"success": False, "message": "Invalid credentials"}), 401

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    users = load_users()
    if username in users:
        return jsonify({"success": False, "message": "Username exists"}), 400
        
    users[username] = password
    save_users(users)
    return jsonify({"success": True, "message": "Account created"})

@app.route('/api/get_skills', methods=['GET'])
def get_skills():
    return jsonify({
        "skills": SKILL_MASTER,
        "domain_roles": DOMAIN_ROLES
    })

# ================== DOMAIN TO ROLE MAPPING ==================
DOMAIN_ROLES = {
    "IT & Software": ["Frontend Developer", "Backend Developer", "Full Stack Developer", "Software Engineer", "Mobile App Developer", "UI/UX Designer"],
    "Data Science & AI": ["Data Scientist", "Data Analyst", "Machine Learning Engineer", "AI Researcher", "Data Engineer"],
    "Cloud & DevOps": ["DevOps Engineer", "Cloud Architect", "Cloud Engineer", "Site Reliability Engineer (SRE)"],
    "Cybersecurity": ["Security Analyst", "Ethical Hacker", "Security Engineer", "Forensic Analyst"],
    "Finance & Accounting": ["Financial Accountant", "Investment Banker", "Tax Consultant", "Auditor", "Financial Analyst"],
    "Marketing & Advertising": ["Digital Marketing Manager", "SEO Specialist", "Content Strategist", "Brand Manager", "Social Media Manager"],
    "Sales & Business Dev": ["Business Development Manager", "Sales Executive", "Account Manager", "Sales Lead"],
    "HR & Operations": ["HR Manager", "Operations Manager", "Talent Acquisition Specialist", "Public Relations Officer"],
    "Engineering & Manufacturing": ["Mechanical Engineer", "Civil Engineer", "Electrical Engineer", "Quality Assurance Engineer"],
    "Healthcare & Medical": ["Clinical Researcher", "Medical Coder", "Healthcare Administrator", "Lab Technician"],
    "Legal": ["Corporate Lawyer", "Legal Consultant", "Compliance Officer", "IP Attorney"],
    "Education & Training": ["Curriculum Designer", "Instructional Designer", "E-Learning Specialist", "Educational Technology Specialist"],
    "Creative & Design": ["Graphic Designer", "UI/UX Designer", "Motion Graphics Artist", "Brand Designer"],
    "Hospitality & Tourism": ["Hotel Manager", "Event Planner", "Travel Consultant", "Customer Service Manager"],
    "Construction & Real Estate": ["Project Site Manager", "Construction Estimator", "Real Estate Specialist", "Safety Officer"]
}

# ================== JOB ROLE SKILL MAPPING ==================
JOB_ROLE_SKILLS = {
    # IT & Software
    "Frontend Developer": ["HTML", "CSS", "JavaScript", "React", "Vue.js", "Angular", "TypeScript", "Git"],
    "Backend Developer": ["Node.js", "Python", "Java", "PHP", "Go", "SQL", "NoSQL", "REST API", "Git"],
    "Full Stack Developer": ["HTML", "CSS", "JavaScript", "React", "Node.js", "SQL", "MongoDB", "Git", "REST API"],
    "Software Engineer": ["Python", "Java", "C++", "SQL", "Git", "Data Structures", "Algorithms", "System Design"],
    "Mobile App Developer": ["Swift", "Kotlin", "React Native", "Flutter", "Android SDK", "iOS Development"],
    
    # Data Science
    "Data Scientist": ["Python", "SQL", "Machine Learning", "Deep Learning", "TensorFlow", "Pandas", "Statistics", "Data Visualization"],
    "Data Analyst": ["Excel", "SQL", "Python", "Tableau", "Power BI", "Data Analysis", "Statistics"],
    "Machine Learning Engineer": ["Python", "PyTorch", "TensorFlow", "Scikit-learn", "MLOps", "NumPy", "Pandas"],
    "Data Engineer": ["Hadoop", "Spark", "Kafka", "SQL", "NoSQL", "Big Data", "Data Pipelines"],
    "AI Researcher": ["Deep Learning", "Neural Networks", "NLP", "Computer Vision", "Statistics", "PyTorch"],
    
    # Cloud & DevOps
    "DevOps Engineer": ["Linux", "Docker", "Kubernetes", "AWS", "CI/CD", "Jenkins", "Python", "Bash"],
    "Cloud Architect": ["AWS", "Azure", "Google Cloud", "Cloud Infrastructure", "Terraform", "CloudFormation"],
    "Cloud Engineer": ["AWS", "Azure", "Docker", "Kubernetes", "Terraform", "Ansible"],
    "Site Reliability Engineer (SRE)": ["Linux", "Python", "Docker", "Kubernetes", "Prometheus", "Grafana", "Networking"],
    
    # Cybersecurity
    "Security Analyst": ["Network Security", "SIEM", "Incident Response", "Vulnerability Assessment", "Firewall"],
    "Ethical Hacker": ["Penetration Testing", "Metasploit", "Nmap", "Linux", "Application Security", "Networking"],
    "Security Engineer": ["Cloud Security", "Cryptography", "Identity & Access Management (IAM)", "Network Security"],
    "Forensic Analyst": ["Malware Analysis", "Forensics", "Legal Research", "Incident Response"],
    
    # Finance
    "Financial Accountant": ["Financial Accounting", "Tally", "GST", "Auditing", "Excel"],
    "Investment Banker": ["Financial Modeling", "Valuation", "Financial Analysis", "Excel", "Corporate Tax"],
    "Tax Consultant": ["Taxation", "Income Tax", "Corporate Tax", "GST", "Compliance"],
    "Auditor": ["Internal Audit", "Compliance", "Financial Accounting", "Risk Assessment"],
    "Financial Analyst": ["Budgeting", "Forecasting", "Financial Modeling", "Excel", "Financial Analysis"],
    
    # Marketing
    "Digital Marketing Manager": ["Digital Marketing", "SEO", "SEM", "Social Media Marketing", "Email Marketing", "Google Ads"],
    "SEO Specialist": ["SEO", "Google Analytics", "Keyword Research", "Content Marketing", "Market Research"],
    "Content Strategist": ["Content Marketing", "Copywriting", "Creative Direction", "Social Media Marketing"],
    "Brand Manager": ["Brand Management", "Market Research", "Public Relations (PR)", "Competitive Analysis"],
    "Social Media Manager": ["Social Media Marketing", "Content Marketing", "Copywriting", "Public Relations (PR)"],
    
    # Sales
    "Business Development Manager": ["B2B Sales", "Lead Generation", "Negotiation", "Closing Skills", "Sales Strategy"],
    "Sales Executive": ["Cold Calling", "Closing Skills", "Sales Presentation", "Account Management"],
    "Account Manager": ["Client Relationship Management", "Account Management", "Negotiation", "CRM Tools"],
    "Sales Lead": ["Pipeline Management", "Forecasting", "Sales Strategy", "Salesforce"],
    
    # HR
    "HR Manager": ["HR Management", "Labor Laws", "Employee Relations", "Payroll Management", "Performance Management"],
    "Operations Manager": ["Operations Management", "Supply Chain Management", "Process Optimization", "Logistics", "Inventory Management"],
    "Talent Acquisition Specialist": ["Recruitment", "Sourcing", "Interviewing", "Applicant Tracking Systems (ATS)", "Social Media Hiring"],
    "Public Relations Officer": ["Public Relations (PR)", "Media Relations", "Crisis Management", "Corporate Communication", "Brand Management"],
    
    # Engineering
    "Mechanical Engineer": ["CAD", "AutoCAD", "SolidWorks", "Thermodynamics", "Fluid Mechanics"],
    "Civil Engineer": ["Civil Engineering", "Structural Analysis", "AutoCAD", "Project Management", "Site Supervision"],
    "Electrical Engineer": ["Electrical Engineering", "Circuit Design", "Power Systems", "Control Systems", "AutoCAD"],
    "Quality Assurance Engineer": ["Quality Assurance", "Quality Control", "ISO Standards", "Six Sigma", "Testing"],
    
    # Healthcare
    "Clinical Researcher": ["Clinical Research", "Clinical Trials", "Epidemiology", "Statistics", "Bioethics"],
    "Medical Coder": ["Medical Coding", "ICD-10", "Medical Billing", "Anatomy", "Medical Terminology"],
    "Healthcare Administrator": ["Healthcare Management", "Hospital Administration", "Public Health", "Regulatory Compliance"],
    "Lab Technician": ["Lab Technology", "Vital Signs Monitoring", "Patient Care", "Medical Equipment Operation"],
    
    # Legal
    "Corporate Lawyer": ["Corporate Law", "Contract Law", "Drafting", "Mergers & Acquisitions", "Governance"],
    "Legal Consultant": ["Civil Law", "Litigation", "Legal Research", "Mediation", "Compliance"],
    "Compliance Officer": ["Compliance", "Regulatory Affairs", "Risk Management", "Anti-Money Laundering (AML)"],
    "IP Attorney": ["Intellectual Property (IP)", "Patents", "Trademarks", "Copyright Law"],
    
    # Education
    "Curriculum Designer": ["Curriculum Design", "Instructional Design", "Teaching", "Educational Technology"],
    "Instructional Designer": ["Instructional Design", "E-Learning", "LMS Administration", "Classroom Management"],
    "E-Learning Specialist": ["E-Learning", "Educational Technology", "Course Creation", "Digital Learning Tools"],
    "Educational Technology Specialist": ["Educational Technology", "SaaS", "LMS Administration", "Instructional Design"],
    
    # Creative
    "Graphic Designer": ["Graphic Design", "Adobe Photoshop", "Adobe Illustrator", "Typography", "Branding"],
    "UI/UX Designer": ["UI/UX Design", "Figma", "Wireframing", "Prototyping", "User Research", "Adobe XD"],
    "Motion Graphics Artist": ["After Effects", "Motion Graphics", "Video Editing", "Animation", "Cinema 4D"],
    "Brand Designer": ["Brand Management", "Logo Design", "Typography", "Visual Identity", "Illustration"],
    
    # Hospitality
    "Hotel Manager": ["Hospitality Management", "Guest Relations", "Operations Management", "Customer Service"],
    "Event Planner": ["Event Management", "Budgeting", "Negotiation", "Public Relations (PR)", "Logistics"],
    "Travel Consultant": ["Travel Planning", "Customer Service", "Geography", "Ticketing Systems"],
    "Customer Service Manager": ["Customer Service", "Conflict Resolution", "Interpersonal Skills", "Team Management"],
    
    # Construction
    "Project Site Manager": ["Site Supervision", "Project Management", "Safety Management", "Estimation", "Civil Engineering"],
    "Construction Estimator": ["Estimation", "Costing", "Budgeting", "Real Estate Planning", "Quantity Surveying"],
    "Real Estate Specialist": ["Real Estate Sales", "Property Management", "Negotiation", "Market Analysis"],
    "Safety Officer": ["Safety Management", "Risk Assessment", "Compliance", "OSHA Standards", "First Aid"]
}

@app.route('/api/resume/upload', methods=['POST'])
def upload_resume():
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "No file uploaded"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "message": "No file selected"}), 400

    job_role = request.form.get('job_role')

    os.makedirs("uploads", exist_ok=True)
    file_path = os.path.join("uploads", file.filename)
    file.save(file_path)

    try:
        resume_text = extract_resume_text(file_path)
        if not resume_text:
            return jsonify({"success": False, "message": "Could not extract text"}), 400
            
        ats_score, detected_skills = calculate_ats_score(resume_text)
        
        # Relevance Message Logic
        relevance_message = ""
        is_mismatch = False
        if job_role and job_role in JOB_ROLE_SKILLS:
            required = {s.lower() for s in JOB_ROLE_SKILLS[job_role]}
            detected = {s.lower() for s in detected_skills}
            matches = required.intersection(detected)
            
            match_ratio = len(matches) / len(required) if required else 0
            
            if match_ratio >= 0.7:
                relevance_message = f"Strong match for {job_role}! Your core skills align well."
            elif match_ratio >= 0.3:
                relevance_message = f"Moderate match for {job_role}. Consider highlighting more relevant experience."
            else:
                is_mismatch = True
                relevance_message = f"⚠️ Warning: Your resume shows limited alignment with the {job_role} position. You may need to update your skills."

        return jsonify({
            "success": True,
            "resume_text": resume_text,
            "ats_score": ats_score,
            "detected_skills": detected_skills,
            "relevance_message": relevance_message,
            "is_mismatch": is_mismatch
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        resume_text = data.get('resume_text', '').lower()
        jd_text = data.get('jd_text', '').lower()
        job_role = data.get('job_role', '')
        user_skills_list = data.get('user_skills', []) # List of strings or dicts
        
        # Extract manual skills (just names)
        manual_skills = set()
        for s in user_skills_list:
            if isinstance(s, dict):
                manual_skills.add(s.get('skill', '').lower())
            else:
                manual_skills.add(str(s).lower())

        # 1. Determine Required Skills (Target)
        if not jd_text:
            return jsonify({"success": False, "message": "Please provide a Job Description to analyze."}), 400

        required_skills_list = extract_skills_from_text(jd_text)
        required_skills = {s.lower() for s in required_skills_list}
        
        if not required_skills:
            return jsonify({"success": False, "message": "The Job Description provided does not contain any recognizable skills."}), 400

        # 2. Determine User Skills (Source)
        # Combine resume extracted skills + manually entered skills (from profile)
        resume_skills_list = extract_skills_from_text(resume_text)
        resume_skills = {s.lower() for s in resume_skills_list}
        
        total_user_skills = resume_skills.union(manual_skills)
        
        # 3. Analyze Gap
        matched_lower = total_user_skills & required_skills
        missing_lower = required_skills - total_user_skills
        
        # Map back to original casing from the master list or JD where possible
        match_map = {s.lower(): s for s in required_skills_list}
        matched = [match_map.get(m, m.title()) for m in matched_lower]
        missing = [match_map.get(m, m.title()) for m in missing_lower]
        
        match_percent = 0
        if required_skills:
            match_percent = (len(matched_lower) / len(required_skills)) * 100
            
        parsed_percent = round(match_percent, 2)
        
        # 4. Category-wise Breakdown for Bar Chart
        category_scores = {}
        for category, skills in SKILL_MASTER.items():
            cat_skills_lower = {s.lower() for s in skills}
            
            # Required skills in this category
            cat_required = cat_skills_lower.intersection(required_skills)
            if not cat_required:
                continue
                
            # Matched skills in this category
            cat_matched = cat_skills_lower.intersection(matched_lower)
            
            category_scores[category] = {
                "matched": len(cat_matched),
                "total": len(cat_required),
                "percentage": (len(cat_matched) / len(cat_required)) * 100
            }

        return jsonify({
            "success": True,
            "matched_skills": [m.title() for m in matched],
            "missing_skills": [m.title() for m in missing],
            "match_percent": parsed_percent,
            "job_role": job_role,
            "category_scores": category_scores
        })
    except Exception as e:
        print(f"Analysis Server Error: {str(e)}")
        return jsonify({"success": False, "message": f"Internal Server Error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
