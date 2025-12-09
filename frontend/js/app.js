// --- State ---
const state = {
    user: null,
    token: null,
    currentReportId: null,
    findings: [],
    selectedFindingId: null
};

// --- Utils ---
function formatTimestamp(isoString) {
    if (!isoString) return '';
    const date = new Date(isoString);
    // Format: 08 Dec, 2025 • 8:57 PM
    const day = date.getDate().toString().padStart(2, '0');
    const month = date.toLocaleString('default', { month: 'short' });
    const year = date.getFullYear();

    let hours = date.getHours();
    const minutes = date.getMinutes().toString().padStart(2, '0');
    const ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12;
    hours = hours ? hours : 12; // the hour '0' should be '12'

    return `${day} ${month}, ${year} • ${hours}:${minutes} ${ampm}`;
}

function showToast(msg, type = 'success') {
    const t = document.getElementById('toast');
    t.textContent = msg;
    t.className = `toast ${type} show`;
    setTimeout(() => t.classList.remove('show'), 3000);
}

function escapeHtml(text) {
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// --- Router ---
function navigateTo(viewId) {
    // Hide all views
    document.querySelectorAll('.view-section').forEach(el => el.classList.remove('active'));

    // Show target view
    const target = document.getElementById(viewId);
    if (target) {
        target.classList.add('active');

        // Reset scroll position for all scrollable containers within the view
        const scrollables = target.querySelectorAll('div[class*="-container"], .sidebar, .center-panel, .detail-pane');
        scrollables.forEach(el => el.scrollTop = 0);
        // Also reset the view itself just in case
        target.scrollTop = 0;
    }

    // Auth Guard
    if (viewId === 'view-dashboard' && !state.user) {
        navigateTo('view-login');
        return;
    }
}

// --- Smart Navigation ---
// --- Smart Navigation ---
function handleLogoClick() {
    navigateTo('view-hero');
}

// --- Auth Logic ---
function initAuth() {
    const storedUser = localStorage.getItem('sf_user');
    if (storedUser) {
        state.user = JSON.parse(storedUser);
        state.token = localStorage.getItem('sf_token');
        updateHeader();
        // Stay on current page if valid, or default to dashboard? 
        // For simplicity, if we are at root, go to dashboard. 
        // But since this is a SPA, we usually rely on initial load.
        // Let's check if we are already on a view, if not default.
        if (!document.querySelector('.view-section.active')) {
            navigateTo('view-dashboard');
        }
    } else {
        if (!document.querySelector('.view-section.active')) {
            navigateTo('view-hero');
        }
    }
}

function updateHeader() {
    const userMenu = document.getElementById('userMenu');
    const authButtons = document.getElementById('authButtons');
    const usernameDisplay = document.getElementById('usernameDisplay');

    if (state.user) {
        userMenu.classList.remove('hidden');
        authButtons.classList.add('hidden');
        // Show First Name if available, else Username
        usernameDisplay.textContent = state.user.firstname || state.user.username;
    } else {
        userMenu.classList.add('hidden');
        authButtons.classList.remove('hidden');
    }
}

async function handleLogin(e) {
    e.preventDefault();
    const username = e.target.username.value;
    const password = e.target.password.value;
    const errorEl = document.getElementById('loginError');

    errorEl.textContent = '';

    try {
        const res = await window.api.login(username, password);
        state.user = res.user;
        state.token = res.access_token;

        localStorage.setItem('sf_user', JSON.stringify(state.user));
        localStorage.setItem('sf_token', state.token);

        updateHeader();
        showToast(`Welcome, ${state.user.firstname || state.user.username}`);
        navigateTo('view-dashboard');
    } catch (err) {
        errorEl.textContent = err.message || "Login failed";
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const firstname = e.target.firstname.value;
    const lastname = e.target.lastname.value;
    const username = e.target.username.value;
    const email = e.target.email.value;
    const password = e.target.password.value;
    const confirm = e.target.confirm_password.value;
    const errorEl = document.getElementById('registerError');

    errorEl.textContent = '';

    if (password !== confirm) {
        errorEl.textContent = "Passwords do not match";
        return;
    }

    try {
        // Pass first/last name if API supports it. 
        // For this demo, we'll assume the API or mock handles it OR we just persist it locally for the demo effect if the real API doesn't support it yet.
        await window.api.register(username, email, password, firstname, lastname);

        showToast("Registration successful! Please login.");
        navigateTo('view-login');
    } catch (err) {
        // Fallback for demo if API fails on extra args: just pretend
        console.warn("Register API might not support fields, mocking check.");
        errorEl.textContent = err.message || "Registration failed";
    }
}

function handleLogout() {
    window.api.logout();
    state.user = null;
    state.token = null;
    localStorage.removeItem('sf_user');
    localStorage.removeItem('sf_token');
    updateHeader();
    navigateTo('view-hero');
}

// --- Dashboard Logic ---
async function handleFileUpload(file) {
    const statusEl = document.getElementById('uploadStatus');
    const tool = document.getElementById('scannerTool').value;

    statusEl.textContent = "Uploading...";

    try {
        const res = await window.api.analyze(file, tool);
        statusEl.textContent = "Processing...";
        state.currentReportId = res.report_id;
        addReportToSidebar(state.currentReportId);
        pollResults(state.currentReportId);
    } catch (err) {
        statusEl.textContent = "Error uploading file.";
        console.error(err);
    }
}

function addReportToSidebar(id) {
    const list = document.getElementById('reportsList');
    if (list.children[0]?.textContent.includes("No reports")) list.innerHTML = '';

    const div = document.createElement('div');
    div.className = 'report-item glass';
    // Use current time for new report
    const timeStr = formatTimestamp(new Date().toISOString());

    div.innerHTML = `
        <div class="report-id">#${id}</div>
        <div class="report-date">${timeStr}</div>
    `;
    div.onclick = () => loadReport(id);
    list.prepend(div);
}

async function pollResults(id) {
    const statusEl = document.getElementById('uploadStatus');
    let attempts = 0;

    const interval = setInterval(async () => {
        attempts++;
        const data = await window.api.getResults(id);

        if (data.status === 'completed') {
            clearInterval(interval);
            statusEl.textContent = "Analysis Complete";
            renderDashboard(data);
        } else if (attempts > 10) {
            clearInterval(interval);
            statusEl.textContent = "Timeout";
        }
    }, 1000);
}

function renderDashboard(data) {
    // Stats
    document.getElementById('statsGrid').style.display = 'grid';
    document.getElementById('statTotal').textContent = data.stats.total_findings;
    document.getElementById('statFP').textContent = data.stats.filtered_fp;
    document.getElementById('statTP').textContent = data.stats.remaining_tp;

    // Findings
    state.findings = data.findings;
    const list = document.getElementById('findingsList');
    list.innerHTML = '';

    state.findings.forEach(f => {
        const card = document.createElement('div');
        card.className = `finding-card glass ${f.finding_id === state.selectedFindingId ? 'active' : ''}`;
        card.onclick = () => selectFinding(f.finding_id);
        card.innerHTML = `
            <div class="finding-header">
                <span class="rule-id">${f.rule_id}</span>
                <span class="confidence-badge" style="color: ${f.confidence > 0.8 ? 'var(--green-neon)' : 'orange'}">
                    ${Math.round(f.confidence * 100)}% CONF
                </span>
            </div>
            <div class="file-path">${f.file_path}</div>
        `;
        list.appendChild(card);
    });
}

function selectFinding(id) {
    state.selectedFindingId = id;

    // Update active state
    document.querySelectorAll('.finding-card').forEach(c => c.classList.remove('active'));
    // Re-render list logic is simplified here, just find the element
    // In a real app we might re-render or toggle class on specific element
    // For now, let's just re-render the detail

    const finding = state.findings.find(f => f.finding_id === id);
    renderDetail(finding);
}

function renderDetail(f) {
    const pane = document.getElementById('detailContent');
    pane.classList.remove('empty-state');
    pane.innerHTML = `
        <h2 style="color: var(--green-neon); margin-bottom: 8px;">${f.rule_id}</h2>
        <div style="margin-bottom: 20px; color: var(--text-muted);">${f.file_path}</div>
        
        <div class="code-block">${escapeHtml(f.secret_snippet)}</div>
        
        <div style="margin-top: 20px;">
            <div class="meta-row">
                <span class="meta-label">AI Verdict</span>
                <span style="text-align: right; color: white;">${f.ai_verdict}</span>
            </div>
            <div class="meta-row">
                <span class="meta-label">Confidence</span>
                <span>${f.confidence}</span>
            </div>
        </div>

        <div class="actions">
            <button class="btn" onclick="submitFeedback('${f.finding_id}', 'false_positive')">Mark as False Positive</button>
            <button class="btn btn-ghost" onclick="submitFeedback('${f.finding_id}', 'true_positive')">Mark as True Positive</button>
        </div>
    `;
}

async function submitFeedback(findingId, label) {
    await window.api.sendFeedback(state.currentReportId, findingId, label);
    showToast(`Marked as ${label.replace('_', ' ')}`);
}

// --- Event Listeners ---
document.addEventListener('DOMContentLoaded', () => {
    // Auth Forms
    document.getElementById('loginForm').addEventListener('submit', handleLogin);
    document.getElementById('registerForm').addEventListener('submit', handleRegister);

    // File Upload
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        if (e.dataTransfer.files.length) handleFileUpload(e.dataTransfer.files[0]);
    });
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) handleFileUpload(e.target.files[0]);
    });

    // Init
    initAuth();
});

// Expose functions to window for onclick handlers in HTML
window.handleLogout = handleLogout;
window.navigateTo = navigateTo;
window.submitFeedback = submitFeedback;
window.handleLogoClick = handleLogoClick;
