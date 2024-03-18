function generateCharts(categories) {
    categories.forEach(category => {
        const ctx = document.getElementById(`chart-${category.name.toLowerCase()}`);
        const labels = category.candidates.map(candidate => candidate.name);
        const data = category.candidates.map(candidate => candidate.votes);

        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: [
                        '#FF6384',
                        '#36A2EB',
                        '#FFCE56',
                        '#4BC0C0',
                        '#9966FF',
                        '#FF9F40',
                        '#7CFC00',
                        '#8B008B'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    });
}