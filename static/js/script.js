// Chart.js initialization for admin dashboard

document.addEventListener('DOMContentLoaded', function () {
    // Fetch data from API
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            // Loans by Category (Pie Chart)
            const categoryCtx = document.getElementById('categoryChart');
            if (categoryCtx) {
                new Chart(categoryCtx, {
                    type: 'pie',
                    data: {
                        labels: data.category.labels,
                        datasets: [{
                            data: data.category.data,
                            backgroundColor: [
                                '#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
                                '#ec4899', '#14b8a6', '#f97316'
                            ]
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                position: 'bottom'
                            },
                            title: {
                                display: true,
                                text: 'Loans by Category'
                            }
                        }
                    }
                });
            }

            // Monthly Loans (Line Chart)
            const monthlyCtx = document.getElementById('monthlyChart');
            if (monthlyCtx) {
                new Chart(monthlyCtx, {
                    type: 'line',
                    data: {
                        labels: data.monthly.labels,
                        datasets: [{
                            label: 'Loans',
                            data: data.monthly.data,
                            borderColor: '#4f46e5',
                            backgroundColor: 'rgba(79, 70, 229, 0.1)',
                            tension: 0.4,
                            fill: true
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            title: {
                                display: true,
                                text: 'Loans per Month (Current Year)'
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: {
                                    stepSize: 1
                                }
                            }
                        }
                    }
                });
            }

            // Loan Status Distribution (Bar Chart)
            const statusCtx = document.getElementById('statusChart');
            if (statusCtx) {
                new Chart(statusCtx, {
                    type: 'bar',
                    data: {
                        labels: data.status.labels,
                        datasets: [{
                            label: 'Count',
                            data: data.status.data,
                            backgroundColor: [
                                '#10b981', '#f59e0b', '#ef4444', '#6b7280'
                            ]
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            title: {
                                display: true,
                                text: 'Loan Status Distribution'
                            },
                            legend: {
                                display: false
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: {
                                    stepSize: 1
                                }
                            }
                        }
                    }
                });
            }
        })
        .catch(error => console.error('Error fetching chart data:', error));
});
