document.addEventListener('DOMContentLoaded', function() {
    // Helper to safely get data from json_script tags
    const getData = (id) => {
        const element = document.getElementById(id);
        if (!element) return null;
        try {
            return JSON.parse(element.textContent);
        } catch (e) {
            console.error(`Error parsing ${id}:`, e);
            return null;
        }
    };

    // Get all chart data
    const positionLabels = getData('position-labels-data') || [];
    const positionCounts = getData('position-counts-data') || [];
    const turnoutHours = getData('turnout-hours-data') || [];
    const turnoutCounts = getData('turnout-counts-data') || [];
    const courseLabels = getData('course-labels-data') || [];
    const courseCounts = getData('course-counts-data') || [];
    const yearLabels = getData('year-labels-data') || [];
    const yearCounts = getData('year-counts-data') || [];
    const participationCourseLabels = getData('participation-course-labels-data') || [];
    const participationCourseCounts = getData('participation-course-counts-data') || [];
    const participationYearLabels = getData('participation-year-labels-data') || [];
    const participationYearCounts = getData('participation-year-counts-data') || [];

    // Chart.js default configuration
    Chart.defaults.font.family = "'Inter', sans-serif";
    Chart.defaults.color = '#64748b';

    // Common chart options
    const commonOptions = {
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
                cornerRadius: 8
            }
        }
    };

    // Color palettes
    const primaryGradient = (ctx) => {
        const gradient = ctx.createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, 'rgba(37, 99, 235, 0.9)');
        gradient.addColorStop(1, 'rgba(124, 58, 237, 0.7)');
        return gradient;
    };

    const successGradient = (ctx) => {
        const gradient = ctx.createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, 'rgba(16, 185, 129, 0.9)');
        gradient.addColorStop(1, 'rgba(52, 211, 153, 0.7)');
        return gradient;
    };

    const multiColorPalette = [
        'rgba(37, 99, 235, 0.85)',   // Blue
        'rgba(16, 185, 129, 0.85)',  // Green
        'rgba(245, 158, 11, 0.85)',  // Orange
        'rgba(239, 68, 68, 0.85)',   // Red
        'rgba(139, 92, 246, 0.85)',  // Purple
        'rgba(236, 72, 153, 0.85)',  // Pink
        'rgba(6, 182, 212, 0.85)',   // Cyan
        'rgba(251, 191, 36, 0.85)',  // Amber
    ];

    // 1. Turnout Trend Chart (Line Chart)
    const turnoutTrendCanvas = document.getElementById('turnoutTrendChart');
    if (turnoutTrendCanvas && turnoutHours.length > 0) {
        const ctx = turnoutTrendCanvas.getContext('2d');
        const gradient = ctx.createLinearGradient(0, 0, 0, 350);
        gradient.addColorStop(0, 'rgba(37, 99, 235, 0.3)');
        gradient.addColorStop(1, 'rgba(37, 99, 235, 0.05)');

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: turnoutHours,
                datasets: [{
                    label: 'Votes',
                    data: turnoutCounts,
                    borderColor: 'rgba(37, 99, 235, 1)',
                    backgroundColor: gradient,
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 4,
                    pointBackgroundColor: 'rgba(37, 99, 235, 1)',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointHoverRadius: 6,
                    pointHoverBackgroundColor: 'rgba(37, 99, 235, 1)',
                    pointHoverBorderColor: '#fff',
                    pointHoverBorderWidth: 3
                }]
            },
            options: {
                ...commonOptions,
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(226, 232, 240, 0.5)',
                            drawBorder: false
                        },
                        ticks: {
                            color: '#64748b',
                            font: { size: 12 },
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
                            font: { size: 11, weight: '500' },
                            padding: 8,
                            maxRotation: 45,
                            minRotation: 45
                        }
                    }
                },
                plugins: {
                    ...commonOptions.plugins,
                    tooltip: {
                        ...commonOptions.plugins.tooltip,
                        callbacks: {
                            label: function(context) {
                                return 'Votes: ' + context.parsed.y;
                            }
                        }
                    }
                },
                animation: {
                    duration: 1500,
                    easing: 'easeInOutQuart'
                }
            }
        });
    }

    // 2. Position Votes Chart (Horizontal Bar Chart)
    const positionVotesCanvas = document.getElementById('positionVotesChart');
    if (positionVotesCanvas && positionLabels.length > 0) {
        const ctx = positionVotesCanvas.getContext('2d');
        
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: positionLabels,
                datasets: [{
                    label: 'Votes',
                    data: positionCounts,
                    backgroundColor: primaryGradient(ctx),
                    borderRadius: 8,
                    borderSkipped: false,
                    barThickness: 40,
                    hoverBackgroundColor: 'rgba(37, 99, 235, 1)'
                }]
            },
            options: {
                ...commonOptions,
                indexAxis: 'y',
                scales: {
                    x: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(226, 232, 240, 0.5)',
                            drawBorder: false
                        },
                        ticks: {
                            color: '#64748b',
                            font: { size: 12 },
                            padding: 8
                        }
                    },
                    y: {
                        grid: {
                            display: false,
                            drawBorder: false
                        },
                        ticks: {
                            color: '#475569',
                            font: { size: 12, weight: '500' },
                            padding: 8
                        }
                    }
                },
                plugins: {
                    ...commonOptions.plugins,
                    tooltip: {
                        ...commonOptions.plugins.tooltip,
                        callbacks: {
                            label: function(context) {
                                return 'Votes: ' + context.parsed.x;
                            }
                        }
                    }
                },
                animation: {
                    duration: 1000,
                    easing: 'easeInOutQuart'
                }
            }
        });
    }

    // 3. Course Chart (Bar Chart)
    const courseCanvas = document.getElementById('courseChart');
    if (courseCanvas && courseLabels.length > 0) {
        const ctx = courseCanvas.getContext('2d');
        
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: courseLabels,
                datasets: [{
                    label: 'Students',
                    data: courseCounts,
                    backgroundColor: primaryGradient(ctx),
                    borderRadius: 8,
                    borderSkipped: false,
                    barThickness: 40,
                    hoverBackgroundColor: 'rgba(37, 99, 235, 1)'
                }]
            },
            options: {
                ...commonOptions,
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(226, 232, 240, 0.5)',
                            drawBorder: false
                        },
                        ticks: {
                            color: '#64748b',
                            font: { size: 12 },
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
                            font: { size: 12, weight: '500' },
                            padding: 8
                        }
                    }
                },
                plugins: {
                    ...commonOptions.plugins,
                    tooltip: {
                        ...commonOptions.plugins.tooltip,
                        callbacks: {
                            label: function(context) {
                                return 'Students: ' + context.parsed.y;
                            }
                        }
                    }
                },
                animation: {
                    duration: 1000,
                    easing: 'easeInOutQuart'
                }
            }
        });
    }

    // 4. Year Level Chart (Doughnut Chart)
    const yearCanvas = document.getElementById('yearChart');
    if (yearCanvas && yearLabels.length > 0) {
        const ctx = yearCanvas.getContext('2d');
        
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: yearLabels,
                datasets: [{
                    data: yearCounts,
                    backgroundColor: multiColorPalette,
                    borderWidth: 3,
                    borderColor: '#ffffff',
                    hoverBorderWidth: 4,
                    hoverBorderColor: '#ffffff',
                    hoverOffset: 8
                }]
            },
            options: {
                ...commonOptions,
                cutout: '65%',
                plugins: {
                    legend: {
                        display: true,
                        position: 'bottom',
                        labels: {
                            padding: 15,
                            font: { size: 13, weight: '500' },
                            color: '#475569',
                            usePointStyle: true,
                            pointStyle: 'circle'
                        }
                    },
                    tooltip: {
                        ...commonOptions.plugins.tooltip,
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
    }

    // 5. Participation by Course Chart
    const participationCourseCanvas = document.getElementById('participationCourseChart');
    if (participationCourseCanvas && participationCourseLabels.length > 0) {
        const ctx = participationCourseCanvas.getContext('2d');
        
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: participationCourseLabels,
                datasets: [{
                    label: 'Active Voters',
                    data: participationCourseCounts,
                    backgroundColor: successGradient(ctx),
                    borderRadius: 8,
                    borderSkipped: false,
                    barThickness: 40,
                    hoverBackgroundColor: 'rgba(16, 185, 129, 1)'
                }]
            },
            options: {
                ...commonOptions,
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(226, 232, 240, 0.5)',
                            drawBorder: false
                        },
                        ticks: {
                            color: '#64748b',
                            font: { size: 12 },
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
                            font: { size: 12, weight: '500' },
                            padding: 8
                        }
                    }
                },
                plugins: {
                    ...commonOptions.plugins,
                    tooltip: {
                        ...commonOptions.plugins.tooltip,
                        callbacks: {
                            label: function(context) {
                                return 'Voters: ' + context.parsed.y;
                            }
                        }
                    }
                },
                animation: {
                    duration: 1000,
                    easing: 'easeInOutQuart'
                }
            }
        });
    }

    // 6. Participation by Year Chart (Pie Chart)
    const participationYearCanvas = document.getElementById('participationYearChart');
    if (participationYearCanvas && participationYearLabels.length > 0) {
        const ctx = participationYearCanvas.getContext('2d');
        
        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: participationYearLabels,
                datasets: [{
                    data: participationYearCounts,
                    backgroundColor: multiColorPalette,
                    borderWidth: 3,
                    borderColor: '#ffffff',
                    hoverBorderWidth: 4,
                    hoverBorderColor: '#ffffff',
                    hoverOffset: 8
                }]
            },
            options: {
                ...commonOptions,
                plugins: {
                    legend: {
                        display: true,
                        position: 'bottom',
                        labels: {
                            padding: 15,
                            font: { size: 13, weight: '500' },
                            color: '#475569',
                            usePointStyle: true,
                            pointStyle: 'circle'
                        }
                    },
                    tooltip: {
                        ...commonOptions.plugins.tooltip,
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
    }

    // Real-time countdown timers
    const countdownElements = document.querySelectorAll('.countdown');
    
    function updateCountdowns() {
        countdownElements.forEach(element => {
            const endTime = new Date(element.dataset.endTime);
            const now = new Date();
            const diff = endTime - now;
            
            if (diff <= 0) {
                element.textContent = 'Ended';
                element.style.color = '#ef4444';
                return;
            }
            
            const days = Math.floor(diff / (1000 * 60 * 60 * 24));
            const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((diff % (1000 * 60)) / 1000);
            
            if (days > 0) {
                element.textContent = `${days}d ${hours}h ${minutes}m`;
            } else if (hours > 0) {
                element.textContent = `${hours}h ${minutes}m ${seconds}s`;
            } else {
                element.textContent = `${minutes}m ${seconds}s`;
            }
        });
    }
    
    // Update countdowns every second
    if (countdownElements.length > 0) {
        updateCountdowns();
        setInterval(updateCountdowns, 1000);
    }

    // Update "last updated" timestamp
    const lastUpdatedElement = document.getElementById('last-updated');
    if (lastUpdatedElement) {
        function updateLastUpdated() {
            const now = new Date();
            const hours = now.getHours().toString().padStart(2, '0');
            const minutes = now.getMinutes().toString().padStart(2, '0');
            const seconds = now.getSeconds().toString().padStart(2, '0');
            lastUpdatedElement.textContent = `Updated at ${hours}:${minutes}:${seconds}`;
        }
        
        updateLastUpdated();
        setInterval(updateLastUpdated, 1000);
    }

    // Auto-refresh dashboard every 30 seconds (optional - can be enabled)
    // Uncomment the following lines to enable auto-refresh
    /*
    setInterval(() => {
        location.reload();
    }, 30000);
    */
});
