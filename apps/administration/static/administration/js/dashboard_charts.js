document.addEventListener('DOMContentLoaded', function() {
    // Helper to get data from json_script tags
    const getData = (id) => JSON.parse(document.getElementById(id).textContent);

    const courseLabels = getData('course-labels-data');
    const courseCounts = getData('course-counts-data');
    const yearLabels = getData('year-labels-data');
    const yearCounts = getData('year-counts-data');

    // Modern gradient colors
    const gradientBlue = {
        start: 'rgba(37, 99, 235, 0.8)',
        end: 'rgba(59, 130, 246, 0.4)'
    };

    // Course Chart - Enhanced Bar Chart
    const courseCtx = document.getElementById('courseChart').getContext('2d');
    
    // Create gradient for bars
    const courseGradient = courseCtx.createLinearGradient(0, 0, 0, 400);
    courseGradient.addColorStop(0, 'rgba(37, 99, 235, 0.9)');
    courseGradient.addColorStop(1, 'rgba(124, 58, 237, 0.7)');

    new Chart(courseCtx, {
        type: 'bar',
        data: {
            labels: courseLabels,
            datasets: [{
                label: 'Students',
                data: courseCounts,
                backgroundColor: courseGradient,
                borderRadius: 8,
                borderSkipped: false,
                barThickness: 40,
                hoverBackgroundColor: 'rgba(37, 99, 235, 1)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { 
                    display: false 
                },
                tooltip: {
                    backgroundColor: 'rgba(15, 23, 42, 0.95)',
                    padding: 12,
                    titleFont: {
                        size: 14,
                        weight: 'bold'
                    },
                    bodyFont: {
                        size: 13
                    },
                    borderColor: 'rgba(37, 99, 235, 0.5)',
                    borderWidth: 1,
                    displayColors: false,
                    callbacks: {
                        label: function(context) {
                            return 'Students: ' + context.parsed.y;
                        }
                    }
                }
            },
            scales: {
                y: { 
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(226, 232, 240, 0.5)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#64748b',
                        font: {
                            size: 12
                        },
                        padding: 8
                    }
                },
                x: {
                    grid: {
                        display: false,
                        drawBorder: false
                    },
                    ticks: {
                        color: '#475569',
                        font: {
                            size: 12,
                            weight: '500'
                        },
                        padding: 8
                    }
                }
            },
            animation: {
                duration: 1000,
                easing: 'easeInOutQuart'
            }
        }
    });

    // Year Level Chart - Enhanced Doughnut Chart
    const yearCtx = document.getElementById('yearChart').getContext('2d');
    
    new Chart(yearCtx, {
        type: 'doughnut',
        data: {
            labels: yearLabels.map(year => `Year ${year}`),
            datasets: [{
                data: yearCounts,
                backgroundColor: [
                    'rgba(16, 185, 129, 0.85)',  // Green
                    'rgba(245, 158, 11, 0.85)',  // Orange
                    'rgba(239, 68, 68, 0.85)',   // Red
                    'rgba(139, 92, 246, 0.85)',  // Purple
                    'rgba(236, 72, 153, 0.85)'   // Pink
                ],
                borderWidth: 3,
                borderColor: '#ffffff',
                hoverBorderWidth: 4,
                hoverBorderColor: '#ffffff',
                hoverOffset: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '65%',
            plugins: {
                legend: { 
                    position: 'bottom',
                    labels: {
                        padding: 15,
                        font: {
                            size: 13,
                            weight: '500'
                        },
                        color: '#475569',
                        usePointStyle: true,
                        pointStyle: 'circle'
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(15, 23, 42, 0.95)',
                    padding: 12,
                    titleFont: {
                        size: 14,
                        weight: 'bold'
                    },
                    bodyFont: {
                        size: 13
                    },
                    borderColor: 'rgba(37, 99, 235, 0.5)',
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            },
            animation: {
                animateRotate: true,
                animateScale: true,
                duration: 1000,
                easing: 'easeInOutQuart'
            }
        }
    });
});
