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

    const trendsData = await response.json(); // This is now an array of many rows
    const content = document.getElementById('content-area');
    content.innerHTML = ""; // Clear the "Welcome" or previous cards

    // 1. Get the list of dates for the bottom of the chart
    const labels = trendsData.map(row => row.date);

    // 2. Identify the trend names from the first row
    const trendNames = Object.keys(trendsData[0]).filter(key => key !== 'date');

    // 3. Loop through each trend and create a Chart
    trendNames.forEach(name => {
        // Create a card for each trend
        const card = document.createElement('div');
        card.className = 'card';
        card.innerHTML = `
            <h3>📈 Trend Analysis: ${name}</h3>
            <div class="chart-container">
                <canvas id="chart-${name}"></canvas>
            </div>
        `;
        content.appendChild(card);

        // Extract the specific values for this trend across all dates
        const values = trendsData.map(row => row[name]);

        // Initialize the Chart.js graph
        const ctx = document.getElementById(`chart-${name}`).getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: name,
                    data: values,
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    fill: true,
                    tension: 0.3,
                    pointRadius: 0 // Keep it clean for 1 year of data
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false, // REQUIRED for the 400px height to work
                scales: {
                    x: { ticks: { color: '#94a3b8', autoSkip: true, maxTicksLimit: 12 } },
                    y: { beginAtZero: true, ticks: { color: '#94a3b8' } }
                },
                plugins: { legend: { display: false } }
            }
        });
    });
}