const API_BASE = "EC2_placeholder";

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
    const trendNames = Object.keys(trendsData[0]).filter(key => key !== 'date' && key !== 'extracted_at' && key !== 'id');

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
// Append this function to the bottom of your script.js file

async function fetchGoldInsights() {
    const token = localStorage.getItem('token');
    const response = await fetch(`${API_BASE}/analytics/daily-insights`, {
        headers: { 'Authorization': `Bearer ${token}` }
    });

    const insightsData = await response.json();
    const content = document.getElementById('content-area');
    content.innerHTML = ""; // Wipe area clean

    if (!insightsData || insightsData.length === 0 || insightsData.error) {
        content.innerHTML = `<p class="error">Failed to load analytics: ${insightsData.error || 'No data found'}</p>`;
        return;
    }

    // 1. Map out timelines and establish our target topics
    const labels = insightsData.map(row => row.date);
    const trackedTopics = ['cybersecurity', 'technology', 'geopolitics', 'latvia', 'artificial_intelligence'];

    // 2. Loop through each enterprise topic to render localized cards and dashboards
    trackedTopics.forEach(topic => {
        // Grab the final row to display real-time current momentum status badges
        const latestRow = insightsData[insightsData.length - 1];
        const rawMomentum = latestRow[`${topic}_search_momentum_wow`] || 0;
        const formattedMomentum = rawMomentum.toFixed(1);
        const momentumClass = rawMomentum >= 0 ? 'positive-badge' : 'negative-badge';

        // Extract series arrays for the visualization layer
        const searchVolume = insightsData.map(row => row[topic] || 0);
        const newsVolume = insightsData.map(row => row[`${topic}_news_volume`] || 0);
        const news7dAvg = insightsData.map(row => row[`${topic}_news_7d_avg`] || 0);
        
        // Build card component with embedded metadata metrics
        const card = document.createElement('div');
        card.className = 'card';
        card.innerHTML = `
            <div class="card-header">
                <h3>🥇 Matrix Analysis: ${topic.replace('_', ' ').toUpperCase()}</h3>
                <span class="momentum-badge ${momentumClass}">Search Momentum: ${formattedMomentum}% WoW</span>
            </div>
            <div class="chart-container">
                <canvas id="gold-chart-${topic}"></canvas>
            </div>
        `;
        content.appendChild(card);

        // 3. Mount Dual-Axis Chart.js combination graph
        const ctx = document.getElementById(`gold-chart-${topic}`).getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: '7-Day News Moving Avg',
                        data: news7dAvg,
                        borderColor: '#3b82f6', // Bright blue line
                        backgroundColor: 'transparent',
                        borderWidth: 3,
                        tension: 0.4,
                        yAxisID: 'yNews',
                        pointRadius: 0
                    },
                    {
                        label: 'Raw News Volume',
                        data: newsVolume,
                        type: 'bar',
                        backgroundColor: 'rgba(59, 130, 246, 0.15)', // Light blue bars
                        borderColor: 'rgba(59, 130, 246, 0.4)',
                        borderWidth: 1,
                        yAxisID: 'yNews',
                        barPercentage: 0.6
                    },
                    {
                        label: 'Google Search Index',
                        data: searchVolume,
                        borderColor: '#f59e0b', // Amber/Yellow line
                        backgroundColor: 'transparent',
                        borderWidth: 2,
                        borderDash: [5, 5], // Dashed representation
                        tension: 0.2,
                        yAxisID: 'ySearch',
                        pointRadius: 0
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { mode: 'index', intersect: false },
                scales: {
                    x: {
                        ticks: { color: '#94a3b8', autoSkip: true, maxTicksLimit: 12 },
                        grid: { color: '#334155' }
                    },
                    ySearch: {
                        type: 'linear',
                        position: 'left',
                        beginAtZero: true,
                        ticks: { color: '#f59e0b' },
                        grid: { color: '#334155' },
                        title: { display: true, text: 'Search Interest Index', color: '#f59e0b' }
                    },
                    yNews: {
                        type: 'linear',
                        position: 'right',
                        beginAtZero: true,
                        ticks: { color: '#3b82f6', stepSize: 1 },
                        grid: { drawOnChartArea: false }, // Avoid grid overlap clutter
                        title: { display: true, text: 'Articles Count', color: '#3b82f6' }
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        labels: { color: '#f8fafc', boxWidth: 20 }
                    }
                }
            }
        });
    });
}