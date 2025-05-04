const video = document.getElementById('webcam');
const canvas = document.getElementById('captureCanvas');
const registerBtn = document.getElementById('registerBtn');
const attendanceBtn = document.getElementById('attendanceBtn');
const nameInput = document.getElementById('nameInput');
const emailInput = document.getElementById('emailInput');
const rollnoInput = document.getElementById('rollnoInput');
const resultDiv = document.getElementById('result');
const stopAttendanceBtn = document.getElementById('stopAttendanceBtn');
const attendanceDateInput = document.getElementById('attendanceDate');
const presentList = document.getElementById('presentList');
const absentList = document.getElementById('absentList');
let liveAttendanceActive = false;
let liveAttendanceInterval = null;

// Tab navigation
const tabBtns = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');
tabBtns.forEach(btn => {
    btn.onclick = () => {
        tabBtns.forEach(b => b.classList.remove('active'));
        tabContents.forEach(tc => tc.classList.remove('active'));
        btn.classList.add('active');
        document.getElementById(btn.dataset.tab).classList.add('active');
        if (btn.dataset.tab === 'users') loadUsers();
        if (btn.dataset.tab === 'log') loadLog();
    };
});

// Toast notification
function showToast(msg, duration = 2500) {
    const toast = document.getElementById('toast');
    toast.textContent = msg;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), duration);
}

// Add edit functionality to user list
async function editUser(name, email, rollno) {
    const newEmail = prompt(`Edit email for ${name}:`, email);
    const newRollno = prompt(`Edit roll number for ${name}:`, rollno);

    if (!newEmail || !newRollno) {
        showToast('Edit cancelled or invalid input.');
        return;
    }

    try {
        const res = await fetch('/edit_user', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email: newEmail, rollno: newRollno })
        });
        const data = await res.json();
        if (data.success) {
            showToast(data.message);
            loadUsers(); // Refresh the user list
        } else {
            showToast('Edit failed: ' + (data.error || 'Unknown error'));
        }
    } catch (e) {
        showToast('Edit failed: Network error.');
    }
}

// User management
async function loadUsers() {
    const userList = document.getElementById('userList');
    userList.innerHTML = '<div class="spinner"></div>';
    try {
        const res = await fetch('/users');
        const data = await res.json();
        if (data.users && data.users.length > 0) {
            userList.innerHTML = '';
            data.users.forEach(user => {
                const div = document.createElement('div');
                div.className = 'user-item';
                const imgSrc = user.image ? `/registered_faces/${user.image}` : '';
                div.innerHTML = `<img class="user-avatar" src="${imgSrc}" alt="avatar" onerror="this.style.display='none'">
                    <span class="user-name">${user.name}</span>
                    <span class="user-email">${user.email}</span>
                    <span class="user-rollno">${user.rollno}</span>
                    <button class="edit-btn" data-name="${user.name}" data-email="${user.email}" data-rollno="${user.rollno}"><i class="fa fa-edit"></i> Edit</button>
                    <button class="delete-btn" data-name="${user.name}"><i class="fa fa-trash"></i> Delete</button>`;
                userList.appendChild(div);
            });
            // Add edit listeners
            userList.querySelectorAll('.edit-btn').forEach(btn => {
                btn.onclick = () => {
                    const name = btn.dataset.name;
                    const email = btn.dataset.email;
                    const rollno = btn.dataset.rollno;
                    editUser(name, email, rollno);
                };
            });
            // Add delete listeners
            userList.querySelectorAll('.delete-btn').forEach(btn => {
                btn.onclick = async () => {
                    if (confirm(`Delete user ${btn.dataset.name}?`)) {
                        const res = await fetch(`/user/${btn.dataset.name}`, { method: 'DELETE' });
                        const data = await res.json();
                        if (data.success) {
                            showToast(`User ${btn.dataset.name} deleted.`);
                            loadUsers();
                        } else showToast('Delete failed: ' + (data.error || 'Unknown error'));
                    }
                };
            });
        } else {
            userList.innerHTML = 'No users registered.';
        }
    } catch (e) {
        userList.innerHTML = 'Failed to load users.';
    }
}

// Attendance log
async function loadLog() {
    const logList = document.getElementById('logList');
    logList.innerHTML = '<div class="spinner"></div>';
    try {
        const res = await fetch('/attendance_log');
        const data = await res.json();
        if (data.records && data.records.length > 0) {
            let html = '<table class="log-table"><thead><tr><th>Name</th><th>Date & Time</th></tr></thead><tbody>';
            data.records.forEach(r => {
                html += `<tr><td>${r.name}</td><td>${r.date || ''} ${r.time || ''}</td></tr>`;
            });
            html += '</tbody></table>';
            logList.innerHTML = html;
        } else {
            logList.innerHTML = 'No attendance records.';
        }
    } catch (e) {
        logList.innerHTML = 'Failed to load log.';
    }
}

document.getElementById('downloadLogBtn').onclick = () => {
    window.location = '/download_attendance';
};

// Start webcam
async function startWebcam() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;
    } catch (err) {
        resultDiv.textContent = 'Could not access webcam.';
    }
}

function captureImage() {
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL('image/jpeg').split(',')[1]; // base64 without prefix
}

registerBtn.onclick = async () => {
    const name = nameInput.value.trim();
    const email = emailInput.value.trim();
    const rollno = rollnoInput.value.trim();
    if (!name || !email || !rollno) {
        showToast('Please enter your name, email, and roll number.');
        return;
    }
    const imgB64 = captureImage();
    resultDiv.textContent = 'Registering...';
    try {
        const res = await fetch('/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, rollno, image: imgB64 })
        });
        const data = await res.json();
        if (data.success) {
            resultDiv.textContent = 'Registration successful!';
            showToast('Registration successful!');
        } else {
            resultDiv.textContent = 'Registration failed: ' + (data.error || 'Unknown error');
            showToast('Registration failed.');
        }
    } catch (e) {
        resultDiv.textContent = 'Registration failed: Network error.';
        showToast('Registration failed: Network error.');
    }
};

async function captureAndSendAttendance() {
    resultDiv.textContent = 'Capturing for liveness (please blink)...';
    showToast('Capturing for liveness (please blink)...', 1800);
    // Capture a burst of frames (e.g., 20 frames over 2 seconds)
    const frames = [];
    const numFrames = 20;
    const interval = 100; // ms between frames (20 frames in 2 seconds)
    for (let i = 0; i < numFrames; i++) {
        frames.push(captureImage());
        await new Promise(res => setTimeout(res, interval));
    }
    resultDiv.textContent = 'Checking attendance...';
    showToast('Checking attendance...', 1200);
    try {
        const res = await fetch('/attendance', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ images: frames })
        });
        const data = await res.json();
        if (data.success) {
            if (data.names && data.names.length > 0) {
                resultDiv.innerHTML = `Attendance marked for: <b>${data.names.join(', ')}</b>`;
                showToast('Attendance marked!');
                // Refresh attendance status for the selected date
                loadAttendanceStatus(attendanceDateInput.value);
            } else {
                // Check if any faces were detected but not real
                const detected = (data.details || []).filter(d => d.name);
                const fake = (data.details || []).filter(d => d.name && !d.liveness);
                if (detected.length === 0) {
                    resultDiv.textContent = 'No recognized faces detected.';
                    showToast('No recognized faces detected.');
                } else if (fake.length > 0) {
                    resultDiv.textContent = 'Detected faces, but liveness verification failed (please blink, do not use a photo).';
                    showToast('Liveness verification failed.');
                } else {
                    resultDiv.textContent = 'No real (live) recognized faces detected.';
                    showToast('No real (live) recognized faces detected.');
                }
            }
        } else {
            resultDiv.textContent = 'Attendance failed.';
            showToast('Attendance failed.');
        }
    } catch (e) {
        resultDiv.textContent = 'Attendance failed: Network error.';
        showToast('Attendance failed: Network error.');
    }
}

attendanceBtn.onclick = async () => {
    if (!isAdmin) {
        showAdminLogin();
        return;
    }
    // Start live attendance mode
    liveAttendanceActive = true;
    attendanceBtn.disabled = true;
    stopAttendanceBtn.style.display = '';
    showToast('Live attendance started!');
    // Run immediately, then every 3 seconds
    await captureAndSendAttendance();
    liveAttendanceInterval = setInterval(() => {
        if (liveAttendanceActive) captureAndSendAttendance();
    }, 3000);
};

stopAttendanceBtn.onclick = () => {
    liveAttendanceActive = false;
    attendanceBtn.disabled = false;
    stopAttendanceBtn.style.display = 'none';
    resultDiv.textContent = 'Live attendance stopped.';
    showToast('Live attendance stopped.');
    if (liveAttendanceInterval) clearInterval(liveAttendanceInterval);
};

function getTodayDateStr() {
    const d = new Date();
    return d.toISOString().slice(0, 10);
}

// Admin authentication logic
const adminBar = document.getElementById('adminBar');
const adminLoginModal = document.getElementById('adminLoginModal');
const adminLoginBtn = document.getElementById('adminLoginBtn');
const adminLogoutBtn = document.getElementById('adminLogoutBtn');
const closeLoginModal = document.getElementById('closeLoginModal');
const adminPasswordInput = document.getElementById('adminPassword');
const loginError = document.getElementById('loginError');
const showAdminLoginBtn = document.getElementById('showAdminLoginBtn');
let isAdmin = false;

function showAdminLogin() {
    adminLoginModal.style.display = 'flex';
    loginError.textContent = '';
    adminPasswordInput.value = '';
    adminPasswordInput.focus();
}
function hideAdminLogin() {
    adminLoginModal.style.display = 'none';
}
adminLoginBtn.onclick = async () => {
    const password = adminPasswordInput.value;
    const res = await fetch('/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password })
    });
    const data = await res.json();
    if (data.success) {
        isAdmin = true;
        hideAdminLogin();
        showAdminFeatures();
        showToast('Admin login successful!');
    } else {
        loginError.textContent = data.error || 'Login failed.';
    }
};
adminLogoutBtn.onclick = async () => {
    await fetch('/logout', { method: 'POST' });
    isAdmin = false;
    hideAdminFeatures();
    showToast('Logged out.');
};
closeLoginModal.onclick = hideAdminLogin;
window.onclick = (e) => {
    if (e.target === adminLoginModal) hideAdminLogin();
};
function showAdminFeatures() {
    adminBar.style.display = '';
    document.querySelectorAll('.mark-btn').forEach(btn => btn.style.display = '');
    document.getElementById('downloadLogBtn').style.display = '';
    document.getElementById('downloadLogByDateBtn').style.display = '';
    document.getElementById('logExportDate').style.display = '';
    document.getElementById('analyticsCard').style.display = '';
    attendanceBtn.style.display = '';
    stopAttendanceBtn.style.display = stopAttendanceBtn.disabled ? 'none' : '';
}
function hideAdminFeatures() {
    adminBar.style.display = 'none';
    document.querySelectorAll('.mark-btn').forEach(btn => btn.style.display = 'none');
    document.getElementById('downloadLogBtn').style.display = 'none';
    document.getElementById('downloadLogByDateBtn').style.display = 'none';
    document.getElementById('logExportDate').style.display = 'none';
    document.getElementById('analyticsCard').style.display = 'none';
    attendanceBtn.style.display = 'none';
    stopAttendanceBtn.style.display = 'none';
}
async function checkAdmin() {
    const res = await fetch('/is_admin');
    const data = await res.json();
    isAdmin = data.is_admin;
    if (isAdmin) showAdminFeatures();
    else hideAdminFeatures();
}
// Show login button in admin bar if not logged in
adminBar.onclick = () => { if (!isAdmin) showAdminLogin(); };
// Show login modal on page load if not admin
checkAdmin();

// Export by date
const logExportDate = document.getElementById('logExportDate');
const downloadLogByDateBtn = document.getElementById('downloadLogByDateBtn');
logExportDate.value = getTodayDateStr();
downloadLogByDateBtn.onclick = () => {
    if (!isAdmin) { showAdminLogin(); return; }
    const date = logExportDate.value;
    if (!date) { showToast('Select a date to export.'); return; }
    window.location = `/download_attendance?date=${date}`;
};
// Hide admin features by default
hideAdminFeatures();

// Analytics
const analyticsCard = document.getElementById('analyticsCard');
const analyticsStats = document.getElementById('analyticsStats');
const analyticsChart = document.getElementById('analyticsChart');
let chartInstance = null;
async function loadAnalytics(date) {
    if (!isAdmin) { analyticsCard.style.display = 'none'; return; }
    analyticsCard.style.display = '';
    analyticsStats.innerHTML = '<div class="spinner"></div>';
    try {
        const res = await fetch(`/attendance_analytics?date=${date}`);
        const data = await res.json();
        analyticsStats.innerHTML = `
            <b>Date:</b> ${data.date}<br>
            <b>Total:</b> ${data.total} &nbsp; <b>Present:</b> ${data.present} &nbsp; <b>Absent:</b> ${data.absent}<br>
            <b>Present %:</b> ${data.percent}%
        `;
        // Draw chart
        if (window.Chart) {
            if (chartInstance) chartInstance.destroy();
            chartInstance = new Chart(analyticsChart.getContext('2d'), {
                type: 'doughnut',
                data: {
                    labels: ['Present', 'Absent'],
                    datasets: [{
                        data: [data.present, data.absent],
                        backgroundColor: ['#10b981', '#ef4444'],
                    }]
                },
                options: { responsive: false, plugins: { legend: { position: 'bottom' } } }
            });
        }
    } catch (e) {
        analyticsStats.innerHTML = 'Failed to load analytics.';
    }
}
attendanceDateInput.onchange = () => {
    loadAttendanceStatus(attendanceDateInput.value);
    loadAnalytics(attendanceDateInput.value);
};
// Load analytics on page load
loadAnalytics(getTodayDateStr());
// Load Chart.js
if (!window.Chart) {
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/chart.js';
    script.onload = () => loadAnalytics(getTodayDateStr());
    document.head.appendChild(script);
}

async function loadAttendanceStatus(date) {
    presentList.innerHTML = '<div class="spinner"></div>';
    absentList.innerHTML = '<div class="spinner"></div>';
    try {
        const res = await fetch(`/attendance_status?date=${date}`);
        const data = await res.json();
        const status = data.status || {};
        presentList.innerHTML = '';
        absentList.innerHTML = '';
        Object.entries(status).forEach(([name, stat]) => {
            if (stat === 'present') {
                const li = document.createElement('li');
                li.textContent = name;
                // Manual mark absent button
                const btn = document.createElement('button');
                btn.className = 'mark-btn absent';
                btn.textContent = 'Mark Absent';
                btn.style.display = isAdmin ? '' : 'none';
                btn.onclick = async () => {
                    await manualMark(name, date, 'absent');
                };
                li.appendChild(btn);
                presentList.appendChild(li);
            } else {
                const li = document.createElement('li');
                li.textContent = name;
                // Manual mark present button
                const btn = document.createElement('button');
                btn.className = 'mark-btn present';
                btn.textContent = 'Mark Present';
                btn.style.display = isAdmin ? '' : 'none';
                btn.onclick = async () => {
                    await manualMark(name, date, 'present');
                };
                li.appendChild(btn);
                absentList.appendChild(li);
            }
        });
    } catch (e) {
        presentList.innerHTML = 'Failed to load.';
        absentList.innerHTML = 'Failed to load.';
    }
}

async function manualMark(name, date, status) {
    try {
        const res = await fetch('/manual_attendance', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, date, status })
        });
        const data = await res.json();
        if (data.success) {
            showToast(data.message);
            loadAttendanceStatus(date);
        } else {
            showToast('Manual mark failed.');
        }
    } catch (e) {
        showToast('Manual mark failed.');
    }
}

attendanceDateInput.value = getTodayDateStr();
attendanceDateInput.onchange = () => {
    loadAttendanceStatus(attendanceDateInput.value);
};

// Load today's attendance status on page load
loadAttendanceStatus(getTodayDateStr());

startWebcam();

// Loading spinner style
const style = document.createElement('style');
style.innerHTML = `.spinner {margin: 24px auto;width: 36px;height: 36px;border: 4px solid #e5e7eb;border-top: 4px solid #3b82f6;border-radius: 50%;animation: spin 1s linear infinite;}@keyframes spin {100% {transform: rotate(360deg);}}`;
document.head.appendChild(style);

showAdminLoginBtn.onclick = showAdminLogin;

const refreshBtn = document.getElementById('refreshBtn');
refreshBtn.onclick = () => {
    location.reload();
};