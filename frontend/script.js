const API_BASE = "http://127.0.0.1:8000";

async function login() {
    const user = document.getElementById('username').value;
    const pass = document.getElementById('password').value;
    const errorEl = document.getElementById('login-error');

    // FastAPI expects "Form Data" for the /token endpoint
    const formData = new FormData();
    formData.append('username', user);
    formData.append('password', pass);

    try {
        const response = await fetch(`${API_BASE}/token`, {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('token', data.access_token);
            
            console.log("Token saved! Switching views..."); // Debug line
            showDashboard();
            fetchNews(); // <--- Add this so the news loads as soon as you log in!
        
        } else {
            errorEl.innerText = "Invalid credentials";
        }
    } catch (err) {
        errorEl.innerText = "Cannot connect to server";
    }
}

function showDashboard() {
    document.getElementById('login-container').classList.add('hidden');
    document.getElementById('dashboard').classList.remove('hidden');
}

async function fetchNews() {
    const token = localStorage.getItem('token');
    const response = await fetch(`${API_BASE}/news`, {
        headers: { 'Authorization': `Bearer ${token}` }
    });

    const news = await response.json();
    const content = document.getElementById('content-area');
    content.innerHTML = news.map(item => `
        <div class="card">
            <h3>${item.title}</h3>
            <p>${item.description || 'No description available.'}</p>
            <small>${item.pubDate}</small>
            <br><a href="${item.link}" target="_blank" style="color:#60a5fa">Read More</a>
        </div>
    `).join('');
}

function logout() {
    localStorage.removeItem('token');
    location.reload();
}

async function fetchTrends() {
    const token = localStorage.getItem('token');
    const response = await fetch(`${API_BASE}/trends`, {
        headers: { 'Authorization': `Bearer ${token}` }
    });

    const trendsData = await response.json();
    const content = document.getElementById('content-area');
    
    // We take the latest row (the most recent date)
    const latestRow = trendsData[0]; 

    // We get all the keys (column names) except for 'date'
    const trendNames = Object.keys(latestRow).filter(key => key !== 'date');

    content.innerHTML = trendNames.map(name => `
        <div class="card" style="border-left: 5px solid #10b981;">
            <h3>🔥 ${name}</h3>
            <p>Trending Index: ${latestRow[name]}</p>
            <small>Data for: ${latestRow.date}</small>
        </div>
    `).join('');
}