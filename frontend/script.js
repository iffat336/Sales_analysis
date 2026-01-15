const API_URL = ""; // Relative URL for deployment

// --- Fetch Functions ---

async function fetchRevenueStats() {
    try {
        const response = await fetch(`${API_URL}/stats/revenue/by-country`);
        const data = await response.json();

        // Calculate Total Revenue
        const total = data.reduce((sum, item) => sum + item.total_revenue, 0);
        document.getElementById('totalRevenue').textContent = `$${(total / 1000000).toFixed(2)}M`;

        // Top Country
        if (data.length > 0) {
            document.getElementById('topCountry').textContent = data[0].country;
        }
    } catch (e) {
        console.error("Error fetching stats:", e);
    }
}

async function fetchMonthlySales() {
    try {
        const response = await fetch(`${API_URL}/analytics/monthly-sales`);
        const data = await response.json();

        const labels = data.map(d => d.month);
        const values = data.map(d => d.revenue);

        const ctx = document.getElementById('monthlyChart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Revenue',
                    data: values,
                    borderColor: '#38bdf8',
                    backgroundColor: 'rgba(56, 189, 248, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: false } },
                scales: {
                    y: { grid: { color: 'rgba(255,255,255,0.05)' } },
                    x: { grid: { display: false } }
                }
            }
        });
    } catch (e) {
        console.error("Error fetching monthly sales:", e);
    }
}

async function fetchTopCustomers() {
    try {
        const response = await fetch(`${API_URL}/analytics/top-customers?limit=10`);
        const data = await response.json();

        document.getElementById('customerCount').textContent = data.length;

        const labels = data.map(d => `ID: ${Math.floor(d.customer_id)}`);
        const values = data.map(d => d.total_spend);

        const ctx = document.getElementById('customerChart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Total Spend',
                    data: values,
                    backgroundColor: '#818cf8',
                    borderRadius: 4
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { color: 'rgba(255,255,255,0.05)' } },
                    y: { grid: { display: false } }
                }
            }
        });
    } catch (e) {
        console.error("Error fetching top customers:", e);
    }
}

async function fetchTransactions() {
    try {
        const response = await fetch(`${API_URL}/transactions?limit=5`);
        const data = await response.json();

        const tbody = document.getElementById('transactionsTable');
        tbody.innerHTML = '';

        data.forEach(tx => {
            const row = `
                <tr>
                    <td>${tx.invoice_id}</td>
                    <td>${new Date(tx.invoice_date).toLocaleDateString()}</td>
                    <td>${tx.country}</td>
                    <td>${tx.items.length} items</td>
                </tr>
            `;
            tbody.innerHTML += row;
        });
    } catch (e) {
        console.error("Error fetching transactions:", e);
    }
}

// --- Admin ---

document.getElementById('rebuildBtn').addEventListener('click', async () => {
    if (!confirm("Are you sure? This will delete the current database and rebuild it from Excel. It may take a minute.")) return;

    const btn = document.getElementById('rebuildBtn');
    const spinner = document.getElementById('spinner');
    const text = document.getElementById('btnText');

    // UI Loading State
    btn.disabled = true;
    text.textContent = "Rebuilding...";
    spinner.classList.remove('hidden');

    try {
        const response = await fetch(`${API_URL}/system/rebuild-database`, { method: 'POST' });
        const res = await response.json();

        if (response.ok) {
            alert("Database rebuilt successfully! Result: " + res.status);
            window.location.reload(); // Refresh data
        } else {
            alert("Error: " + res.detail);
        }
    } catch (e) {
        alert("Network Error: " + e.message);
    } finally {
        // Reset UI
        btn.disabled = false;
        text.textContent = "Rebuild Database";
        spinner.classList.add('hidden');
    }
});

// --- Init ---
(async () => {
    await Promise.all([
        fetchRevenueStats(),
        fetchMonthlySales(),
        fetchTopCustomers(),
        fetchTransactions()
    ]);
})();
