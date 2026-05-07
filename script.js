const API_URL = '/api';
let SKILL_MASTER_DATA = {};
let isLogin = true;
let uploadedResumeText = "";

// Global State & Chart Instances
let currentSection = 'auth';
let isResumeMismatch = false;
let latestAtsScore = 0;
let atsChartInstance = null;
let gapChartInstance = null;
let categoryChartInstance = null;
let dashAtsChartInstance = null;

document.addEventListener('DOMContentLoaded', () => {
    // Check if user is logged in
    const user = sessionStorage.getItem('user');
    if (user) {
        showSection('profile');
        fetchSkills(); // Fetch skills on load
    }
});

async function fetchSkills() {
    try {
        const res = await fetch(API_URL + '/get_skills');
        const data = await res.json();

        // Handle new structure: { skills: {}, domain_roles: {} }
        SKILL_MASTER_DATA = data.skills;
        const DOMAIN_ROLES_DATA = data.domain_roles;

        // Store mapping globally for loadTechSkills
        window.DOMAIN_ROLES = DOMAIN_ROLES_DATA;

        // Populate Domain Dropdown
        const domainSelect = document.getElementById('tech-domain');
        domainSelect.innerHTML = '<option value="">Select Domain</option>';

        Object.keys(SKILL_MASTER_DATA).forEach(domain => {
            if (domain !== 'Soft Skills') {
                const opt = document.createElement('option');
                opt.value = domain;
                opt.textContent = domain;
                domainSelect.appendChild(opt);
            }
        });

        // Load Soft Skills immediately
        loadSoftSkills();

        // click outside close dropdowns
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.multiselect-container')) {
                document.querySelectorAll('.checkboxes').forEach(el => el.classList.remove('show'));
            }
        });

    } catch (err) {
        console.error("Failed to fetch skills", err);
    }
}

function toggleSelect(type) {
    const list = document.getElementById(`${type}-checkboxes`);
    // Close others
    document.querySelectorAll('.checkboxes').forEach(el => {
        if (el !== list) el.classList.remove('show');
    });
    list.classList.toggle('show');
}

function updateSelectedTags(type) {
    const container = document.getElementById(`${type}-selected-tags`);
    const checkboxes = document.querySelectorAll(`#${type}-checkboxes input:checked`);
    const placeholder = document.getElementById(`${type}-placeholder`);

    container.innerHTML = '';

    if (checkboxes.length > 0) {
        placeholder.textContent = `${checkboxes.length} selected`;
        checkboxes.forEach(cb => {
            const tag = document.createElement('span');
            tag.className = 'tag';
            tag.textContent = cb.value;
            container.appendChild(tag);
        });
    } else {
        placeholder.textContent = 'Choose options';
    }
}

function loadTechSkills() {
    const domain = document.getElementById('tech-domain').value;
    const container = document.getElementById('tech-checkboxes');
    const group = document.getElementById('tech-skills-group');
    const placeholder = document.getElementById('tech-placeholder');
    const tagsArea = document.getElementById('tech-selected-tags');
    const roleSelect = document.getElementById('job-role');

    container.innerHTML = '';
    tagsArea.innerHTML = '';
    placeholder.textContent = 'Choose options';

    // Populate Job Roles for this domain
    roleSelect.innerHTML = '<option value="">Select Role</option>';
    if (window.DOMAIN_ROLES && window.DOMAIN_ROLES[domain]) {
        window.DOMAIN_ROLES[domain].forEach(role => {
            const opt = document.createElement('option');
            opt.value = role;
            opt.textContent = role;
            roleSelect.appendChild(opt);
        });
    } else {
        roleSelect.innerHTML = '<option value="">Select Domain First</option>';
    }

    if (!domain || !SKILL_MASTER_DATA[domain]) {
        group.style.display = 'none';
        return;
    }

    group.style.display = 'block'; // Make sure parent follows flex flow if needed, or block

    SKILL_MASTER_DATA[domain].forEach(skill => {
        const label = document.createElement('label');
        label.innerHTML = `
            <input type="checkbox" value="${skill}" onchange="updateSelectedTags('tech')">
            ${skill}
        `;
        container.appendChild(label);
    });
}

function loadSoftSkills() {
    const container = document.getElementById('soft-checkboxes');
    container.innerHTML = '';

    if (SKILL_MASTER_DATA['Soft Skills']) {
        SKILL_MASTER_DATA['Soft Skills'].forEach(skill => {
            const label = document.createElement('label');
            label.innerHTML = `
                <input type="checkbox" value="${skill}" onchange="updateSelectedTags('soft')">
                ${skill}
            `;
            container.appendChild(label);
        });
    }
}

// DOM Elements
const sections = {
    auth: document.getElementById('auth-section'),
    profile: document.getElementById('profile-section'),
    resume: document.getElementById('resume-section'),
    analysis: document.getElementById('analysis-section'),
    dashboard: document.getElementById('dashboard-section')
};

const sectionOrder = ['profile', 'resume', 'analysis', 'dashboard'];

// Utils
function showSection(name) {
    currentSection = name;
    Object.values(sections).forEach(sec => sec.classList.add('hidden'));
    sections[name].classList.remove('hidden');
    updateNavButtons();
}

function updateNavButtons() {
    const nav = document.getElementById('nav-controls');
    if (currentSection === 'auth') {
        nav.classList.add('hidden');
        return;
    }

    nav.classList.remove('hidden');
    const idx = sectionOrder.indexOf(currentSection);

    // Prev Button
    document.getElementById('prev-btn').style.visibility = (idx <= 0) ? 'hidden' : 'visible';

    // Next Button
    const nextBtn = document.getElementById('next-btn');
    if (idx === sectionOrder.length - 1) {
        nextBtn.style.visibility = 'hidden';
    } else {
        nextBtn.style.visibility = 'visible';
    }
}

function goBack() {
    const idx = sectionOrder.indexOf(currentSection);
    if (idx > 0) {
        showSection(sectionOrder[idx - 1]);
    }
}

function goForward() {
    if (validateCurrentSection()) {
        const idx = sectionOrder.indexOf(currentSection);
        if (idx < sectionOrder.length - 1) {
            // Special Case: Analysis page forward button should actually trigger analysis
            if (currentSection === 'analysis') {
                analyzeGap();
            } else {
                showSection(sectionOrder[idx + 1]);
            }
        }
    }
}

function validateCurrentSection() {
    if (currentSection === 'profile') {
        const fullName = document.getElementById('full-name').value.trim();
        const ageValue = document.getElementById('age').value;
        const age = parseInt(ageValue);
        const jobRole = document.getElementById('job-role').value;
        const qual = document.getElementById('qualification').value;
        const course = document.getElementById('course').value.trim();
        const techDomain = document.getElementById('tech-domain').value;

        const techSkillsCount = document.querySelectorAll('#tech-checkboxes input:checked').length;
        const softSkillsCount = document.querySelectorAll('#soft-checkboxes input:checked').length;

        if (!fullName || !ageValue || !jobRole || !qual || !course || !techDomain) {
            alert("⚠️ Please fill in all mandatory profile details.");
            return false;
        }

        if (techSkillsCount === 0 || softSkillsCount === 0) {
            alert("⚠️ Please select at least one Technical and one Soft Skill.");
            return false;
        }

        if (age < 18) {
            alert("You must be at least 18 years old.");
            return false;
        }

        // Qualification-Age Logic
        if ((qual === 'PhD' && age < 24) || (qual === 'PG' && age < 21) || (qual === 'UG' && age < 17)) {
            alert("Age does not match the minimum requirement for the selected qualification.");
            return false;
        }
        return true;
    }

    if (currentSection === 'resume') {
        // Checking if resume text is extracted
        if (typeof uploadedResumeText === 'undefined' || !uploadedResumeText) {
            alert("⚠️ Please upload your resume and wait for detection to complete.");
            return false;
        }
        if (isResumeMismatch) {
            alert("⚠️ Your resume does not match the target job role. Please upload a relevant resume to proceed.");
            return false;
        }
        return true;
    }

    if (currentSection === 'analysis') {
        const jdText = document.getElementById('jd-text').value.trim();
        if (!jdText) {
            alert("⚠️ Please paste a Job Description to analyze.");
            return false;
        }
        return true;
    }

    return true;
}

// Auth Handling
function switchAuth(mode) {
    isLogin = mode === 'login';
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');

    document.getElementById('confirm-password').classList.toggle('hidden', isLogin);
    document.getElementById('auth-btn').textContent = isLogin ? 'Login' : 'Sign Up';
}

document.getElementById('auth-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const confirm = document.getElementById('confirm-password').value;
    const msg = document.getElementById('auth-message');

    if (!isLogin && password !== confirm) {
        msg.textContent = "Passwords do not match";
        msg.style.color = "var(--danger)";
        return;
    }

    const endpoint = isLogin ? '/auth/login' : '/auth/signup';

    try {
        const res = await fetch(API_URL + endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        const data = await res.json();

        if (data.success) {
            msg.textContent = "Success!";
            msg.style.color = "var(--success)";
            if (isLogin) {
                // Save session
                sessionStorage.setItem('user', username);
                showSection('profile');
                fetchSkills(); // Fetch skills immediately on login
            } else {
                switchAuth('login');
                msg.textContent = "Account created. Please login.";
            }
        } else {
            msg.textContent = data.message;
            msg.style.color = "var(--danger)";
        }
    } catch (err) {
        msg.textContent = "Server error";
    }
});

// Navigation
function goToResume() {
    goForward();
}

function goToMakeAnalysis() {
    goForward();
}

// Resume Upload
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('resume-file');

dropZone.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', handleUpload);

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.style.borderColor = '#6366f1'; // Indigo 500
});

dropZone.addEventListener('dragleave', (e) => {
    e.preventDefault();
    dropZone.style.borderColor = 'rgba(148, 163, 184, 0.1)'; // Default border
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    fileInput.files = e.dataTransfer.files;
    handleUpload();
});

// Resume Upload

async function handleUpload() {
    const file = fileInput.files[0];
    if (!file) return;

    document.getElementById('file-name').textContent = `Uploaded: ${file.name}`;
    document.getElementById('file-name').classList.remove('hidden');

    const formData = new FormData();
    formData.append('file', file);
    formData.append('job_role', document.getElementById('job-role').value);

    try {
        const res = await fetch(API_URL + '/resume/upload', {
            method: 'POST',
            body: formData
        });
        const data = await res.json();

        if (data.success) {
            uploadedResumeText = data.resume_text;
            isResumeMismatch = data.is_mismatch || false;
            latestAtsScore = data.ats_score;

            document.getElementById('ats-result').classList.remove('hidden');
            document.getElementById('ats-score').textContent = `${data.ats_score}%`;

            const feedbackEl = document.getElementById('ats-feedback');
            feedbackEl.textContent = data.relevance_message || "";
            // Use var(--error-color) if mismatch or warning icons, otherwise success
            feedbackEl.style.color = (data.relevance_message && (data.relevance_message.includes('⚠️') || isResumeMismatch)) ? 'var(--error-color)' : 'var(--success-color)';

            // Hide/Show "Proceed to Analysis" button based on mismatch
            const proceedBtn = document.querySelector('#ats-result button');
            if (isResumeMismatch) {
                proceedBtn.classList.add('hidden');
            } else {
                proceedBtn.classList.remove('hidden');
            }

            // Render ATS Chart
            const atsCtx = document.getElementById('atsChart').getContext('2d');
            if (atsChartInstance) atsChartInstance.destroy();

            const scoreColor = data.ats_score > 75 ? '#10b981' : (data.ats_score > 50 ? '#f59e0b' : '#ef4444');

            atsChartInstance = new Chart(atsCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Score', 'Remaining'],
                    datasets: [{
                        data: [data.ats_score, 100 - data.ats_score],
                        backgroundColor: [scoreColor, 'rgba(255, 255, 255, 0.1)'],
                        borderWidth: 0,
                        cutout: '80%'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false }, tooltip: { enabled: false } }
                }
            });

            const skillsContainer = document.getElementById('detected-skills');
            skillsContainer.innerHTML = data.detected_skills.map(s =>
                `<span class="tag">${s}</span>`
            ).join('');
        }
    } catch (err) {
        alert("Upload failed");
    }
}

// Manual Skills & Checkboxes
let userSkills = [];

function addSkill() {
    const input = document.getElementById('skill-input');
    const level = document.getElementById('skill-level');
    const bg = document.getElementById('user-skills-list');

    const skill = input.value.trim();
    if (!skill) return;

    // Add to state
    userSkills.push({ skill: skill, level: level.value });

    // Render
    const tag = document.createElement('span');
    tag.className = 'tag';
    tag.innerHTML = `${skill} <small>(${level.value})</small>`;
    bg.appendChild(tag);

    input.value = '';
}

// Gather all selected skills
function getAllSelectedSkills() {
    let allSkills = [...userSkills]; // Start with manual skills

    // Add checked Tech Skills (NEW SELECTOR)
    const techCbs = document.querySelectorAll('#tech-checkboxes input:checked');
    techCbs.forEach(cb => {
        allSkills.push({ skill: cb.value, level: 'Intermediate' });
    });

    // Add checked Soft Skills (NEW SELECTOR)
    const softCbs = document.querySelectorAll('#soft-checkboxes input:checked');
    softCbs.forEach(cb => {
        allSkills.push({ skill: cb.value, level: 'Intermediate' });
    });

    return allSkills;
}

// Analysis
async function analyzeGap() {
    const jdText = document.getElementById('jd-text').value.trim();
    // In the HTML, the job role select is in the profile section, not the analysis section. 
    // We should either move it or assume checking the profile one.
    // However, the analysis section only has the textarea. 
    // Let's assume we use the one from profile if available, otherwise ask for JD.
    const jobRole = document.getElementById('job-role').value;

    if (!jdText) {
        alert("⚠️ Please paste a Job Description to analyze.");
        return;
    }

    try {
        const finalUserSkills = getAllSelectedSkills();

        const res = await fetch(API_URL + '/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                resume_text: uploadedResumeText,
                jd_text: jdText,
                job_role: jobRole,
                user_skills: finalUserSkills
            })
        });
        const data = await res.json();

        if (data.success) {
            renderDashboard(data);
            showSection('dashboard');
        } else {
            alert(data.message || "Analysis failed");
        }
    } catch (err) {
        console.error("Analysis Error:", err);
        alert("Analysis failed. Please check the console for details.");
    }
}

function renderDashboard(data) {
    document.getElementById('match-percent').textContent = `${data.match_percent}%`;
    document.getElementById('gap-percent-overlay').textContent = `${data.match_percent}%`;
    document.getElementById('dashboard-ats-percent-overlay').textContent = `${latestAtsScore}%`;

    const roleText = data.job_role ? ` for ${data.job_role}` : '';
    document.getElementById('final-verdict').textContent =
        (data.match_percent > 70 ? "Great Match! 🚀" :
            data.match_percent > 40 ? "Good Potential 👍" : "Needs Improvement ⚠️") + roleText;

    // Lists
    document.getElementById('matched-list').innerHTML = data.matched_skills.map(s => `<li>${s}</li>`).join('');
    document.getElementById('missing-list').innerHTML = data.missing_skills.map(s => `<li>${s}</li>`).join('');

    // Chart
    const ctx = document.getElementById('gapChart').getContext('2d');

    if (gapChartInstance) gapChartInstance.destroy();

    gapChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Matched', 'Missing'],
            datasets: [{
                data: [data.matched_skills.length, data.missing_skills.length],
                backgroundColor: ['#10b981', '#ef4444'], // Emerald / Red
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { position: 'bottom', labels: { color: 'white' } }
            }
        }
    });

    // Category Bar Chart
    const categoryCtx = document.getElementById('categoryChart').getContext('2d');
    if (categoryChartInstance) categoryChartInstance.destroy();

    // Calculate Consolidated Scores
    const catScores = data.category_scores || {};
    const categories = Object.keys(catScores);

    // 1. Resume Match
    const resumeScore = latestAtsScore || 0;

    // 2. Technical Match (Average of all except Soft Skills)
    const techCategories = categories.filter(c => c !== 'Soft Skills');
    let techAvg = 0;
    if (techCategories.length > 0) {
        const sum = techCategories.reduce((acc, cat) => acc + catScores[cat].percentage, 0);
        techAvg = sum / techCategories.length;
    }

    // 3. Soft Skills Match
    const softScore = catScores['Soft Skills'] ? catScores['Soft Skills'].percentage : 0;

    const displayLabels = ["Resume Match", "Technical Match", "Soft Skills Match"];
    const displayData = [resumeScore, techAvg, softScore];

    categoryChartInstance = new Chart(categoryCtx, {
        type: 'line',
        data: {
            labels: displayLabels,
            datasets: [{
                label: 'Score Percentage',
                data: displayData,
                backgroundColor: 'rgba(37, 99, 235, 0.15)',
                borderColor: '#2563eb',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#2563eb',
                pointBorderColor: '#fff',
                pointHoverRadius: 6,
                pointRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            aspectRatio: 3,
            scales: {
                x: {
                    grid: { color: 'rgba(0, 0, 0, 0.05)' },
                    ticks: { color: '#64748b', font: { weight: '500' } }
                },
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: { color: 'rgba(0, 0, 0, 0.05)' },
                    ticks: {
                        color: '#64748b',
                        callback: value => value + '%'
                    }
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: context => ` ${context.dataset.label}: ${context.raw.toFixed(1)}%`
                    }
                }
            }
        }
    });

    // Dashboard ATS Chart
    const dashAtsCtx = document.getElementById('dashboardAtsChart').getContext('2d');
    if (dashAtsChartInstance) dashAtsChartInstance.destroy();

    const scoreColor = latestAtsScore > 75 ? '#10b981' : (latestAtsScore > 50 ? '#f59e0b' : '#ef4444');

    dashAtsChartInstance = new Chart(dashAtsCtx, {
        type: 'doughnut',
        data: {
            labels: ['Score', 'Remaining'],
            datasets: [{
                data: [latestAtsScore, 100 - latestAtsScore],
                backgroundColor: [scoreColor, 'rgba(255, 255, 255, 0.1)'],
                borderWidth: 0,
                cutout: '80%'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: { legend: { display: false }, tooltip: { enabled: false } }
        }
    });

    // Recommendations
    const recList = document.getElementById('recommendation-list');
    recList.innerHTML = '';
    if (data.missing_skills.length > 0) {
        data.missing_skills.slice(0, 5).forEach(skill => {
            const li = document.createElement('li');
            li.innerHTML = `Consider taking a course on <b>${skill}</b> to boost your profile.`;
            li.style.color = '#cbd5e1';
            li.style.marginBottom = '5px';
            recList.appendChild(li);
        });
        if (data.missing_skills.length > 5) {
            const li = document.createElement('li');
            li.textContent = `And ${data.missing_skills.length - 5} more skills...`;
            li.style.color = '#94a3b8';
            recList.appendChild(li);
        }
    } else {
        recList.innerHTML = '<li style="color: var(--success)">Great job! You have a strong profile for this role.</li>';
    }
}

function restart() {
    showSection('profile'); // Better to go back to profile or analysis? Restart usually means start over.
    // Clear JD
    document.getElementById('jd-text').value = '';
}
