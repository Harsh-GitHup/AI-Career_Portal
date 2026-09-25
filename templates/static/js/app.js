const API_BASE_URL = 'http://127.0.0.1:8000/api';
let currentUserId = localStorage.getItem('user_id');
let currentPage = 1;

window.onload = () => {
    const savedUsername = localStorage.getItem('username');
    if (currentUserId && savedUsername) {
        document.getElementById('loginBtn').classList.add('hidden');
        const profileControls = document.getElementById('userProfileControls');
        profileControls.classList.remove('hidden');
        profileControls.classList.add('flex');
        document.getElementById('loggedInUser').innerText = savedUsername;
        document.getElementById('tab-saved').classList.remove('hidden');

        // Dynamically fetch profile data
        fetchProfile();
    }

    const savedPdf = localStorage.getItem('saved_resume_pdf');
    if (savedPdf) {
        document.getElementById('resumePreviewFrame').src = savedPdf;
        document.getElementById('resumePreviewFrame').classList.remove('hidden');
        document.getElementById('resumePlaceholder').classList.add('hidden');
    }

    fetchDynamicTypes();
};

async function fetchProfile() {
    try {
        const res = await fetch(`${API_BASE_URL}/profiles/`, {
            credentials: 'include'
        });
        if (res.ok) {
            const data = await res.json();
            if (data.length > 0) {
                populateDashboard(data[0]);
                fetchRecommendations();
            }
        }
    } catch (e) {
        console.error("Error fetching profile", e);
    }
}

function populateDashboard(profile) {
    document.getElementById('page-title').innerText = `Welcome, ${profile.full_name || localStorage.getItem('username')}`;
    document.getElementById('targetRole').innerText = profile.target_role || "Not Set";
    document.getElementById('readinessScore').innerText = `${profile.readiness_score || 0}%`;

    // Skills Table
    const tbody = document.getElementById('skillsTableBody');
    tbody.innerHTML = '';

    (profile.current_skills || []).forEach(skill => {
        tbody.innerHTML += `<tr><td class="py-4 px-6">${skill}</td><td class="py-4 px-6"><span class="px-2.5 py-1 text-xs rounded-full bg-emerald-100 text-emerald-700">Proficient</span></td><td class="py-4 px-6">Ready</td></tr>`;
    });
    (profile.skill_gaps || []).forEach(gap => {
        tbody.innerHTML += `
                    <tr>
                        <td class="py-4 px-6 font-medium text-gray-900">${gap}</td>
                        <td class="py-4 px-6"><span class="px-2.5 py-1 text-xs rounded-full bg-rose-100 text-rose-700">Missing</span></td>
                        <td class="py-4 px-6">
                            <button onclick="searchOpportunity('${gap}')" class="text-indigo-600 hover:text-indigo-800 font-semibold underline text-sm transition-colors">
                                Find ${gap} Courses &rarr;
                            </button>
                        </td>
                    </tr>`;
    });

    // Resume Builder
    const tipsList = document.getElementById('resumeTipsContainer');
    tipsList.innerHTML = '';
    (profile.resume_improvements || []).forEach(tip => {
        tipsList.innerHTML += `<li class="p-4 bg-indigo-50 border-l-4 border-indigo-500 text-sm text-indigo-900 rounded-r-lg font-medium shadow-sm">${tip}</li>`;
    });

    // Mock Interview
    const interviewContainer = document.getElementById('interviewQuestionsContainer');
    interviewContainer.innerHTML = '';
    (profile.interview_questions || []).forEach((q, idx) => {
        interviewContainer.innerHTML += `<div class="p-5 bg-white border border-gray-100 shadow-sm rounded-xl hover:shadow-md transition-shadow"><span class="text-xs font-bold text-indigo-500 uppercase tracking-wider mb-2 block">Question ${idx + 1}</span><p class="text-sm font-semibold text-gray-800">${q}</p></div>`;
    });
}

function searchOpportunity(query) {
    switchTab('opportunities');
    document.getElementById('searchOpp').value = query;
    document.getElementById('typeOpp').value = "Course";
    fetchOpportunities();
}

async function fetchDynamicTypes() {
    try {
        const res = await fetch(`${API_BASE_URL}/opportunities/types/`);
        if (res.ok) {
            const types = await res.json();
            const typeSelect = document.getElementById('typeOpp');
            types.forEach(t => {
                const opt = document.createElement('option');
                opt.value = t;
                opt.textContent = t;
                typeSelect.appendChild(opt);
            });
        }
    } catch (e) {
        console.error("Error fetching opportunity types", e);
    }
}

function showToast(message, type = 'success') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast-enter min-w-[300px] px-6 py-3 rounded-lg shadow-xl flex items-center justify-between pointer-events-auto border-l-4`;

    if (type === 'success') {
        toast.classList.add('bg-white', 'border-emerald-500', 'text-gray-800');
        toast.innerHTML = `<div class="flex items-center"><i class="fa-solid fa-circle-check text-emerald-500 mr-3 text-lg"></i><span class="font-medium">${message}</span></div>`;
    } else if (type === 'error') {
        toast.classList.add('bg-white', 'border-red-500', 'text-gray-800');
        toast.innerHTML = `<div class="flex items-center"><i class="fa-solid fa-circle-exclamation text-red-500 mr-3 text-lg"></i><span class="font-medium">${message}</span></div>`;
    } else {
        toast.classList.add('bg-gray-800', 'border-gray-600', 'text-white');
        toast.innerHTML = `<div class="flex items-center"><i class="fa-solid fa-bell text-gray-300 mr-3 text-lg"></i><span class="font-medium">${message}</span></div>`;
    }

    container.appendChild(toast);
    requestAnimationFrame(() => {
        toast.classList.remove('toast-enter');
        toast.classList.add('toast-enter-active');
    });

    setTimeout(() => {
        toast.classList.remove('toast-enter-active');
        toast.classList.add('toast-exit-active');
        setTimeout(() => toast.remove(), 900);
    }, 9000);
}

function switchTab(tabKey) {
    document.querySelectorAll('.content-view').forEach(el => el.classList.add('hidden'));
    document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active-tab'));

    document.getElementById(`section-${tabKey}`).classList.remove('hidden');
    document.getElementById(`tab-${tabKey}`).classList.add('active-tab');

    if (tabKey === 'opportunities') fetchOpportunities();
    if (tabKey === 'saved') fetchSavedOpportunities();
}

function showLogin() {
    document.getElementById('loginModal').classList.remove('hidden');
}
function closeLogin() {
    document.getElementById('loginModal').classList.add('hidden');
}

async function socialLogin() {
    showToast("Google Login requires a valid Client ID. Please use standard login for now.", "info");
}

async function standardLogin() {
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;

    if (!username || !password) {
        showToast("Please enter username and password", "error");
        return;
    }

    try {
        const res = await fetch(`${API_BASE_URL}/login/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ username, password })
        });
        const data = await res.json();
        if (res.ok) {
            currentUserId = data.user_id;
            localStorage.setItem('user_id', data.user_id);
            localStorage.setItem('username', data.username);
            document.getElementById('loginBtn').classList.add('hidden');
            document.getElementById('tab-saved').classList.remove('hidden');
            const profileControls = document.getElementById('userProfileControls');
            profileControls.classList.remove('hidden');
            profileControls.classList.add('flex');
            document.getElementById('loggedInUser').innerText = data.username;
            closeLogin();
            showToast("Successfully logged in!", "success");
            fetchProfile();
        } else {
            showToast(data.error || "Login failed", "error");
        }
    } catch (e) {
        console.error(e);
        showToast("Error connecting to server", "error");
    }
}

function toggleAuth(mode) {
    const loginForm = document.getElementById('loginFormContainer');
    const registerForm = document.getElementById('registerFormContainer');
    const tabLogin = document.getElementById('tabLogin');
    const tabRegister = document.getElementById('tabRegister');

    if (mode === 'login') {
        loginForm.classList.remove('hidden');
        registerForm.classList.add('hidden');
        tabLogin.classList.add('border-indigo-600', 'text-indigo-600');
        tabLogin.classList.remove('border-transparent', 'text-gray-500');
        tabRegister.classList.remove('border-indigo-600', 'text-indigo-600');
        tabRegister.classList.add('border-transparent', 'text-gray-500');
    } else {
        loginForm.classList.add('hidden');
        registerForm.classList.remove('hidden');
        tabRegister.classList.add('border-indigo-600', 'text-indigo-600');
        tabRegister.classList.remove('border-transparent', 'text-gray-500');
        tabLogin.classList.remove('border-indigo-600', 'text-indigo-600');
        tabLogin.classList.add('border-transparent', 'text-gray-500');
    }
}

async function standardRegister() {
    const username = document.getElementById('registerUsername').value;
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;

    if (!username || !password) {
        showToast("Please enter username and password", "error");
        return;
    }

    try {
        const res = await fetch(`${API_BASE_URL}/register/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ username, email, password })
        });
        const data = await res.json();
        if (res.ok) {
            currentUserId = data.user_id;
            localStorage.setItem('user_id', data.user_id);
            localStorage.setItem('username', data.username);
            document.getElementById('loginBtn').classList.add('hidden');
            document.getElementById('tab-saved').classList.remove('hidden');
            const profileControls = document.getElementById('userProfileControls');
            profileControls.classList.remove('hidden');
            profileControls.classList.add('flex');
            document.getElementById('loggedInUser').innerText = data.username;
            closeLogin();
            showToast("Account created successfully!", "success");
            fetchProfile();
        } else {
            showToast(data.error || "Registration failed", "error");
        }
    } catch (e) {
        console.error(e);
        showToast("Error connecting to server", "error");
    }
}

async function logout() {
    try {
        const res = await fetch(`${API_BASE_URL}/logout/`, {
            method: 'POST',
            credentials: 'include'
        });
        if (res.ok) {
            currentUserId = null;
            localStorage.removeItem('user_id');
            localStorage.removeItem('username');
            localStorage.removeItem('saved_resume_pdf');
            document.getElementById('loginBtn').classList.remove('hidden');
            document.getElementById('tab-saved').classList.add('hidden');
            const profileControls = document.getElementById('userProfileControls');
            profileControls.classList.add('hidden');
            profileControls.classList.remove('flex');
            document.getElementById('loggedInUser').innerText = "";
            showToast("Successfully logged out!", "success");

            document.getElementById('page-title').innerText = "Welcome, Student";
            document.getElementById('targetRole').innerText = "N/A";
            document.getElementById('readinessScore').innerText = "--";
            document.getElementById('skillsTableBody').innerHTML = `<tr><td colspan="3" class="py-4 px-6 text-center text-gray-500">Upload resume to view analysis</td></tr>`;
            document.getElementById('schemesContainer').innerHTML = ``;
            document.getElementById('resumeTipsContainer').innerHTML = `<li class="p-4 bg-gray-50 rounded-lg text-sm text-gray-700 border-l-4 border-indigo-500">Upload a resume to generate specific formatting and quantitative metric improvements.</li>`;
            document.getElementById('interviewQuestionsContainer').innerHTML = `<p class="text-sm text-gray-400">Upload your resume to formulate custom technical questions.</p>`;
        }
    } catch (e) {
        console.error(e);
        showToast("Error during logout", "error");
    }
}

function toggleChat() {
    const chat = document.getElementById('chatWindow');
    chat.classList.toggle('hidden');
}

async function sendChat() {
    const input = document.getElementById('chatInput');
    const msg = input.value.trim();
    if (!msg) return;

    const history = document.getElementById('chatHistory');
    history.innerHTML += `<div class="bg-indigo-600 text-white p-3 rounded-lg w-3/4 ml-auto text-right shadow-md mb-3">${msg}</div>`;
    input.value = '';
    history.scrollTop = history.scrollHeight;

    try {
        const res = await fetch(`${API_BASE_URL}/chatbot/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ message: msg })
        });
        const data = await res.json();
        history.innerHTML += `<div class="bg-white p-3 rounded-lg border border-gray-100 w-3/4 shadow-md mb-3 text-gray-800 leading-relaxed">${data.response}</div>`;
        history.scrollTop = history.scrollHeight;
    } catch (e) {
        history.innerHTML += `<div class="bg-red-50 text-red-500 p-3 rounded-lg border w-3/4 shadow-sm mb-3">Error fetching response.</div>`;
    }
}

async function uploadResume() {
    const input = document.getElementById('resumeInput');
    if (!input.files || input.files.length === 0) return;

    const btn = document.getElementById('uploadBtn');
    const originalText = btn.innerHTML;
    btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i><span class="hidden md:inline">Analyzing...</span>`;
    btn.disabled = true;

    const formData = new FormData();
    formData.append('resume', input.files[0]);

    const reader = new FileReader();
    reader.onload = function (e) {
        const base64PDF = e.target.result;
        try {
            localStorage.setItem('saved_resume_pdf', base64PDF);
        } catch (e) {
            console.warn("PDF too large for localStorage.");
        }
        document.getElementById('resumePreviewFrame').src = base64PDF;
        document.getElementById('resumePreviewFrame').classList.remove('hidden');
        document.getElementById('resumePlaceholder').classList.add('hidden');
    };
    reader.readAsDataURL(input.files[0]);

    try {
        const response = await fetch(`${API_BASE_URL}/upload-resume/`, {
            method: 'POST',
            credentials: 'include',
            body: formData
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "Failed to process resume.");

        showToast("Resume analyzed successfully!", "success");
        populateDashboard(data);
        fetchRecommendations();

    } catch (err) {
        console.error("Upload error:", err);
        showToast("Upload Exception: " + err.message, "error");
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

async function fetchOpportunities(page = 1) {
    currentPage = page;
    const search = document.getElementById('searchOpp').value;
    const type = document.getElementById('typeOpp').value;
    const sort = document.getElementById('sortOpp').value;

    let url = `${API_BASE_URL}/opportunities/?page=${page}&ordering=${sort}`;
    if (search) url += `&search=${search}`;
    if (type) url += `&type=${type}`;

    try {
        const res = await fetch(url, { credentials: 'include' });
        const data = await res.json();

        const container = document.getElementById('schemesContainer');
        container.innerHTML = '';

        let results = data.results || data;

        if (results.length === 0) {
            container.innerHTML = `<p class="text-sm text-gray-500 col-span-2 text-center py-8">No opportunities found for this query.</p>`;
            return;
        }

        results.forEach(opp => {
            container.innerHTML += `
                        <div class="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm hover:shadow-lg flex flex-col justify-between transition-all duration-300">
                            <div>
                                <div class="flex justify-between items-start mb-3">
                                    <span class="px-3 py-1 text-xs font-bold rounded-full ${opp.is_free ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'}">${opp.stipend_or_cost}</span>
                                    <span class="text-xs font-bold text-gray-400 uppercase tracking-wider">${opp.opportunity_type}</span>
                                </div>
                                <h4 class="text-lg font-bold text-gray-900 mb-1">${opp.title}</h4>
                                <p class="text-xs text-indigo-500 font-semibold mb-3">${opp.provider} &bull; ${opp.mode} &bull; ${opp.location}</p>
                                <p class="text-sm text-gray-600 mb-4 leading-relaxed">${opp.description.substring(0, 120)}...</p>
                            </div>
                            <div class="pt-4 border-t border-gray-50 flex justify-between items-center">
                                <a href="${opp.url}" target="_blank" class="w-full text-center bg-gray-900 hover:bg-indigo-600 text-white text-sm font-semibold px-4 py-2.5 rounded-xl transition-colors shadow-md">Apply Now &rarr;</a>
                            </div>
                        </div>
                    `;
        });

        const pag = document.getElementById('paginationControls');
        pag.innerHTML = '';
        if (data.previous) {
            pag.innerHTML += `<button onclick="fetchOpportunities(${page - 1})" class="px-4 py-2 bg-white border border-gray-200 rounded-lg shadow-sm hover:bg-gray-50 font-medium text-sm transition-colors">Previous</button>`;
        }
        if (data.next) {
            pag.innerHTML += `<button onclick="fetchOpportunities(${page + 1})" class="px-4 py-2 bg-white border border-gray-200 rounded-lg shadow-sm hover:bg-gray-50 font-medium text-sm transition-colors ml-2">Next</button>`;
        }
    } catch (e) {
        console.error(e);
    }
}

async function fetchRecommendations() {
    try {
        const res = await fetch(`${API_BASE_URL}/recommendations/`, {
            credentials: 'include'
        });
        if(!res.ok) return;
        const data = await res.json();

        const allMatches = [...(data.schemes || []), ...(data.opportunities || [])];
        if (allMatches.length === 0) return;

        const container = document.getElementById('schemesContainer');
        let html = `<div class="col-span-full mb-2 flex items-center space-x-2"><i class="fa-solid fa-sparkles text-amber-500"></i><h4 class="text-sm font-bold text-indigo-700 uppercase tracking-wider">AI-Curated For Your Profile</h4></div>`;

        allMatches.slice(0, 6).forEach(match => {
            const opp = match.opportunity;
            const score = match.relevance_score;
            const scoreColor = score >= 70 ? 'emerald' : score >= 40 ? 'amber' : 'gray';
            html += `
                <div class="bg-gradient-to-br from-indigo-50 to-white p-6 rounded-2xl border-2 border-indigo-100 shadow-sm flex flex-col justify-between hover:shadow-lg hover:border-indigo-300 transition-all duration-300 relative overflow-hidden">
                    <div class="absolute -right-4 -top-4 w-16 h-16 bg-indigo-100 rounded-full opacity-50 blur-xl"></div>
                    <div class="relative z-10">
                        <div class="flex justify-between items-start mb-3">
                            <span class="px-3 py-1 text-xs font-bold rounded-full bg-${scoreColor}-100 text-${scoreColor}-800 shadow-sm"><i class="fa-solid fa-bolt mr-1"></i> Match: ${score}%</span>
                            <span class="text-xs font-bold text-gray-400 uppercase tracking-wider">${opp.opportunity_type}</span>
                        </div>
                        <h4 class="text-lg font-bold text-gray-900 mb-1">${opp.title}</h4>
                        <p class="text-xs text-indigo-500 font-semibold mb-3">${opp.provider} &bull; ${opp.mode}</p>
                        <p class="text-sm text-gray-600 mb-3 leading-relaxed">${(opp.description || '').substring(0, 100)}...</p>
                        <div class="bg-white/80 p-3 rounded-lg border border-indigo-50 mb-4">
                            <p class="text-xs text-indigo-700 italic font-medium">💡 ${match.reasoning}</p>
                        </div>
                    </div>
                    <div class="pt-4 border-t border-indigo-50 flex justify-between items-center relative z-10">
                        <button onclick="toggleBookmark(${match.id}, this)" class="w-10 h-10 rounded-full flex items-center justify-center transition-colors ${match.is_bookmarked ? 'text-rose-500 bg-rose-50 hover:bg-rose-100' : 'text-gray-400 bg-gray-50 hover:text-rose-500 hover:bg-rose-50'}">
                            <i class="${match.is_bookmarked ? 'fa-solid' : 'fa-regular'} fa-heart text-lg"></i>
                        </button>
                        ${opp.opportunity_type.toLowerCase() === 'job' || opp.opportunity_type.toLowerCase() === 'internship' ? `<button onclick="generateCoverLetter(${match.id})" class="ml-2 bg-indigo-100 hover:bg-indigo-200 text-indigo-700 text-sm font-semibold px-3 py-2 rounded-xl transition-colors"><i class="fa-solid fa-pen-nib mr-1"></i> Cover Letter</button>` : ''}
                        <a href="${opp.url}" target="_blank" class="flex-1 text-center bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold px-4 py-2.5 rounded-xl transition-colors shadow-md shadow-indigo-200 ml-2">View &rarr;</a>
                    </div>
                </div>`;
        });

        container.innerHTML = html + container.innerHTML;
        showToast(`Found ${allMatches.length} AI-matched opportunities tailored for you!`, 'success');
    } catch(e) {
        console.error('fetchRecommendations error:', e);
    }
}

async function fetchSavedOpportunities() {
    try {
        const res = await fetch(`${API_BASE_URL}/recommendations/`, {
            credentials: 'include'
        });
        if(!res.ok) return;
        const data = await res.json();
        const allMatches = [...(data.schemes || []), ...(data.opportunities || [])].filter(m => m.is_bookmarked);

        const container = document.getElementById('savedContainer');
        container.innerHTML = '';
        
        if (allMatches.length === 0) {
            container.innerHTML = `<p class="text-sm text-gray-500 col-span-2 text-center py-8">No saved matches yet. Bookmark opportunities from the Dashboard to see them here.</p>`;
            return;
        }

        allMatches.forEach(match => {
            const opp = match.opportunity;
            container.innerHTML += `
                <div class="bg-white p-6 rounded-xl border border-rose-100 shadow-sm hover:shadow-md flex flex-col justify-between transition-all duration-300">
                    <div>
                        <div class="flex justify-between items-start mb-3">
                            <span class="px-3 py-1 text-xs font-bold rounded-full bg-emerald-100 text-emerald-800">${opp.stipend_or_cost}</span>
                            <span class="text-xs font-bold text-gray-400 uppercase tracking-wider">${opp.opportunity_type}</span>
                        </div>
                        <h4 class="text-lg font-bold text-gray-900 mb-1">${opp.title}</h4>
                        <p class="text-xs text-indigo-500 font-semibold mb-3">${opp.provider}</p>
                        <p class="text-sm text-gray-600 mb-4 leading-relaxed">${opp.description.substring(0, 120)}...</p>
                    </div>
                    <div class="pt-4 border-t border-gray-50 flex justify-between items-center">
                        <button onclick="toggleBookmark(${match.id}, this)" class="text-rose-500 hover:text-gray-400 text-sm font-semibold px-3 py-2 transition-colors"><i class="fa-solid fa-heart mr-1"></i> Unsave</button>
                        <a href="${opp.url}" target="_blank" class="text-center bg-gray-900 hover:bg-indigo-600 text-white text-sm font-semibold px-4 py-2.5 rounded-xl transition-colors shadow-md">Apply Now &rarr;</a>
                    </div>
                </div>
            `;
        });
    } catch(e) {
        console.error('fetchSavedOpportunities error:', e);
    }
}

async function toggleBookmark(matchId, btnElement) {
    if(!currentUserId) {
        showToast('Please login to save opportunities', 'error');
        return;
    }
    
    // Optimistic UI update
    const icon = btnElement.querySelector('i');
    const isCurrentlySaved = icon.classList.contains('fa-solid');
    
    if (isCurrentlySaved) {
        icon.classList.remove('fa-solid');
        icon.classList.add('fa-regular');
        btnElement.classList.replace('text-rose-500', 'text-gray-400');
        btnElement.classList.replace('bg-rose-50', 'bg-gray-50');
        btnElement.classList.replace('hover:bg-rose-100', 'hover:bg-rose-50');
        btnElement.classList.replace('hover:text-rose-500', 'hover:text-rose-500');
    } else {
        icon.classList.remove('fa-regular');
        icon.classList.add('fa-solid');
        btnElement.classList.replace('text-gray-400', 'text-rose-500');
        btnElement.classList.replace('bg-gray-50', 'bg-rose-50');
        btnElement.classList.replace('hover:bg-rose-50', 'hover:bg-rose-100');
    }

    try {
        const res = await fetch(`${API_BASE_URL}/bookmark/${matchId}/`, {
            method: 'POST',
            credentials: 'include'
        });
        if(!res.ok) throw new Error('Failed to toggle bookmark');
        
        // If we are on the saved tab, re-fetch to update list
        if(document.getElementById('section-saved').classList.contains('hidden') === false) {
            fetchSavedOpportunities();
        }
    } catch (e) {
        console.error(e);
        showToast('Failed to sync bookmark. Please try again.', 'error');
        // Revert on failure... (omitted for brevity)
    }
}

async function generateCoverLetter(matchId) {
    if(!currentUserId) {
        showToast('Please login to generate cover letters', 'error');
        return;
    }

    const modal = document.getElementById('coverLetterModal');
    const content = document.getElementById('coverLetterContent');
    modal.classList.remove('hidden');
    content.innerHTML = `<div class="flex flex-col items-center justify-center h-full text-indigo-500"><i class="fa-solid fa-spinner fa-spin text-3xl mb-3"></i><p>CareerAI is writing your personalized cover letter...</p></div>`;
    
    try {
        const res = await fetch(`${API_BASE_URL}/cover-letter/${matchId}/`, {
            method: 'POST',
            credentials: 'include'
        });
        const data = await res.json();
        
        if (res.ok) {
            content.innerText = data.cover_letter;
        } else {
            content.innerHTML = `<div class="text-rose-500 text-center"><i class="fa-solid fa-triangle-exclamation mb-2 text-2xl"></i><p>${data.error || 'Failed to generate cover letter.'}</p></div>`;
        }
    } catch (e) {
        console.error(e);
        content.innerHTML = `<div class="text-rose-500 text-center"><i class="fa-solid fa-wifi mb-2 text-2xl"></i><p>Network error connecting to AI service.</p></div>`;
    }
}

function closeCoverLetterModal() {
    document.getElementById('coverLetterModal').classList.add('hidden');
}

function copyCoverLetter() {
    const text = document.getElementById('coverLetterContent').innerText;
    if (text) {
        navigator.clipboard.writeText(text).then(() => {
            showToast('Cover letter copied to clipboard!', 'success');
        });
    }
}