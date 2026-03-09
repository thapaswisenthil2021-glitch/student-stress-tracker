// Chart.js Configuration for Student Stress Tracker

// Student-friendly color scheme
const studentColors = {
    primary: '#4361ee',
    secondary: '#f72585',
    success: '#4cc9f0',
    warning: '#ffd60a',
    danger: '#ef233c',
    info: '#7209b7',
    light: '#caf0f8',
    dark: '#2b2d42'
};

// Initialize all charts when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize trend chart
    initTrendChart();
    
    // Initialize distribution chart
    initDistributionChart();
    
    // Initialize gender chart
    initGenderChart();
    
    // Initialize real-time updates
    initRealTimeUpdates();
    
    // Add chart responsiveness
    window.addEventListener('resize', function() {
        resizeCharts();
    });
});

// Chart 1: Stress Trend Over Time
function initTrendChart() {
    const ctx = document.getElementById('trendChart');
    if (!ctx) return;
    
    // Get data from data attributes or use dummy data
    const chartData = JSON.parse(ctx.getAttribute('data-chart') || '[]');
    
    let labels = [];
    let data = [];
    
    if (chartData.length > 0) {
        labels = chartData.map(item => item.date);
        data = chartData.map(item => item.avg_stress);
    } else {
        // Demo data
        labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
        data = [3.2, 3.5, 2.8, 3.8, 2.5, 3.0];
    }
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Average Stress Level',
                data: data,
                borderColor: studentColors.primary,
                backgroundColor: `rgba(67, 97, 238, 0.15)`,
                borderWidth: 4,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: studentColors.primary,
                pointBorderColor: '#ffffff',
                pointBorderWidth: 3,
                pointRadius: 7,
                pointHoverRadius: 10,
                pointHoverBackgroundColor: studentColors.secondary,
                pointHoverBorderColor: '#ffffff',
                pointHoverBorderWidth: 3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        color: studentColors.dark,
                        font: {
                            size: 14,
                            family: "'Poppins', 'Segoe UI', sans-serif",
                            weight: '600'
                        },
                        padding: 25,
                        usePointStyle: true,
                        pointStyle: 'circle'
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(43, 45, 66, 0.9)',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff',
                    borderColor: studentColors.primary,
                    borderWidth: 2,
                    cornerRadius: 12,
                    displayColors: true,
                    callbacks: {
                        label: function(context) {
                            return `Stress Score: ${context.parsed.y}`;
                        },
                        title: function(context) {
                            return `Date: ${context[0].label}`;
                        }
                    },
                    padding: 15,
                    boxPadding: 10
                },
                title: {
                    display: false,
                    text: 'Stress Level Trend',
                    color: studentColors.dark,
                    font: {
                        size: 18,
                        family: "'Poppins', sans-serif",
                        weight: '700'
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)',
                        drawBorder: false
                    },
                    ticks: {
                        color: studentColors.dark,
                        font: {
                            size: 12,
                            family: "'Poppins', sans-serif"
                        },
                        padding: 10
                    }
                },
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)',
                        drawBorder: false
                    },
                    ticks: {
                        color: studentColors.dark,
                        font: {
                            size: 12,
                            family: "'Poppins', sans-serif"
                        },
                        padding: 10,
                        callback: function(value) {
                            if (value % 20 === 0) {
                                return value;
                            }
                        }
                    },
                    title: {
                        display: true,
                        text: 'Stress Score',
                        color: studentColors.dark,
                        font: {
                            size: 14,
                            family: "'Poppins', sans-serif",
                            weight: '600'
                        }
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            },
            animations: {
                tension: {
                    duration: 2000,
                    easing: 'easeOutQuart',
                    from: 0,
                    to: 0.4
                },
                colors: {
                    duration: 1500,
                    easing: 'easeOutQuart'
                }
            },
            elements: {
                line: {
                    cubicInterpolationMode: 'monotone'
                }
            }
        }
    });
}

// Chart 2: Stress Level Distribution
function initDistributionChart() {
    const ctx = document.getElementById('distributionChart');
    if (!ctx) return;
    
    // Get data from data attributes or use dummy data
    const distributionData = JSON.parse(ctx.getAttribute('data-distribution') || '[]');
    
    let labels = ['Low', 'Moderate', 'High'];
    let data = [0, 0, 0];
    let backgroundColors = [
        `rgba(76, 201, 240, 0.8)`,
        `rgba(255, 214, 10, 0.8)`,
        `rgba(239, 35, 60, 0.8)`
    ];
    
    if (distributionData.length > 0) {
        distributionData.forEach(item => {
            const level = item.stress_level;
            const count = item.count;
            if (level >= 1 && level <= 3) {
                data[level - 1] = count;
            }
        });
    } else {
        // Demo data
        data = [15, 25, 10];
    }
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: backgroundColors,
                borderColor: [studentColors.success, studentColors.warning, studentColors.danger],
                borderWidth: 3,
                hoverBackgroundColor: [
                    `rgba(76, 201, 240, 1)`,
                    `rgba(255, 214, 10, 1)`,
                    `rgba(239, 35, 60, 1)`
                ],
                hoverBorderColor: '#ffffff',
                hoverBorderWidth: 4,
                hoverOffset: 25,
                borderRadius: 15
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '65%',
            radius: '85%',
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        color: studentColors.dark,
                        padding: 25,
                        font: {
                            size: 13,
                            family: "'Poppins', sans-serif",
                            weight: '600'
                        },
                        generateLabels: function(chart) {
                            const data = chart.data;
                            if (data.labels.length && data.datasets.length) {
                                return data.labels.map(function(label, i) {
                                    const meta = chart.getDatasetMeta(0);
                                    const style = meta.controller.getStyle(i);
                                    const value = data.datasets[0].data[i];
                                    const total = data.datasets[0].data.reduce((a, b) => a + b, 0);
                                    const percentage = Math.round((value / total) * 100);
                                    
                                    return {
                                        text: `${label}: ${value} (${percentage}%)`,
                                        fillStyle: style.backgroundColor,
                                        strokeStyle: style.borderColor,
                                        lineWidth: style.borderWidth,
                                        hidden: isNaN(data.datasets[0].data[i]) || meta.data[i].hidden,
                                        index: i
                                    };
                                });
                            }
                            return [];
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((value / total) * 100);
                            return `${label}: ${value} assessments (${percentage}%)`;
                        },
                        title: function(context) {
                            return 'Stress Distribution';
                        }
                    },
                    backgroundColor: 'rgba(43, 45, 66, 0.9)',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff',
                    borderColor: studentColors.primary,
                    borderWidth: 2,
                    cornerRadius: 12,
                    padding: 15
                },
                title: {
                    display: false,
                    text: 'Stress Level Distribution',
                    color: studentColors.dark,
                    font: {
                        size: 16,
                        family: "'Poppins', sans-serif",
                        weight: '700'
                    }
                }
            },
            animation: {
                animateScale: true,
                animateRotate: true,
                duration: 2500,
                easing: 'easeOutQuart'
            },
            layout: {
                padding: {
                    left: 20,
                    right: 20,
                    top: 20,
                    bottom: 20
                }
            }
        }
    });
}

// Chart 3: Gender Distribution
function initGenderChart() {
    const ctx = document.getElementById('genderChart');
    if (!ctx) return;
    
    // Get data from data attributes or use dummy data
    const genderData = JSON.parse(ctx.getAttribute('data-gender') || '[]');
    
    let labels = ['Male', 'Female', 'Other'];
    let data = [0, 0, 0];
    let backgroundColors = [
        `rgba(67, 97, 238, 0.8)`,
        `rgba(247, 37, 133, 0.8)`,
        `rgba(114, 9, 183, 0.8)`
    ];
    
    if (genderData.length > 0) {
        genderData.forEach(item => {
            const gender = item.gender.toLowerCase();
            const count = item.count;
            
            if (gender.includes('male')) data[0] = count;
            else if (gender.includes('female')) data[1] = count;
            else data[2] = count;
        });
    } else {
        // Demo data
        data = [30, 35, 5];
    }
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Number of Assessments',
                data: data,
                backgroundColor: backgroundColors,
                borderColor: [studentColors.primary, studentColors.secondary, studentColors.info],
                borderWidth: 2,
                borderRadius: 12,
                barPercentage: 0.7,
                categoryPercentage: 0.8,
                hoverBackgroundColor: [
                    `rgba(67, 97, 238, 1)`,
                    `rgba(247, 37, 133, 1)`,
                    `rgba(114, 9, 183, 1)`
                ],
                hoverBorderColor: '#ffffff',
                hoverBorderWidth: 3,
                hoverRadius: 8
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
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.raw}`;
                        },
                        title: function(context) {
                            return `Gender: ${context[0].label}`;
                        }
                    },
                    backgroundColor: 'rgba(43, 45, 66, 0.9)',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff',
                    borderColor: studentColors.primary,
                    borderWidth: 2,
                    cornerRadius: 12,
                    padding: 15
                },
                title: {
                    display: false,
                    text: 'Gender Distribution',
                    color: studentColors.dark,
                    font: {
                        size: 16,
                        family: "'Poppins', sans-serif",
                        weight: '700'
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false,
                        drawBorder: false
                    },
                    ticks: {
                        color: studentColors.dark,
                        font: {
                            size: 13,
                            family: "'Poppins', sans-serif",
                            weight: '600'
                        },
                        padding: 15
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)',
                        drawBorder: false
                    },
                    ticks: {
                        color: studentColors.dark,
                        font: {
                            size: 12,
                            family: "'Poppins', sans-serif"
                        },
                        padding: 10,
                        stepSize: 10,
                        callback: function(value) {
                            return Number.isInteger(value) ? value : '';
                        }
                    },
                    title: {
                        display: true,
                        text: 'Number of Assessments',
                        color: studentColors.dark,
                        font: {
                            size: 14,
                            family: "'Poppins', sans-serif",
                            weight: '600'
                        },
                        padding: {top: 20, bottom: 10}
                    }
                }
            },
            animation: {
                duration: 2000,
                easing: 'easeOutQuart',
                onComplete: function() {
                    const chart = this;
                    const meta = chart.getDatasetMeta(0);
                    
                    meta.data.forEach((bar, index) => {
                        const ctx = chart.ctx;
                        const x = bar.x;
                        const y = bar.y;
                        const width = bar.width;
                        const height = bar.height;
                        
                        // Draw glow effect
                        ctx.save();
                        ctx.beginPath();
                        ctx.rect(x - width/2, y, width, height);
                        ctx.clip();
                        
                        const gradient = ctx.createLinearGradient(0, y, 0, y + height);
                        gradient.addColorStop(0, 'rgba(255, 255, 255, 0.3)');
                        gradient.addColorStop(1, 'rgba(255, 255, 255, 0)');
                        
                        ctx.fillStyle = gradient;
                        ctx.fillRect(x - width/2, y, width, height);
                        ctx.restore();
                    });
                }
            }
        }
    });
}

// Age Chart (for chart.html template)
function initAgeChart() {
    const ctx = document.getElementById('ageChart');
    if (!ctx) return;
    
    // Get data from template variables
    const ageData = window.ageData || [];
    
    if (ageData && ageData.length > 0) {
        const ageCtx = ctx.getContext('2d');
        new Chart(ageCtx, {
            type: 'bar',
            data: {
                labels: ageData.map(item => item[0]),
                datasets: [{
                    label: 'Number of Assessments',
                    data: ageData.map(item => item[1]),
                    backgroundColor: `rgba(153, 102, 255, 0.8)`,
                    borderColor: studentColors.info,
                    borderWidth: 2,
                    borderRadius: 10,
                    barPercentage: 0.6
                }, {
                    label: 'Average Stress Score',
                    data: ageData.map(item => item[2] || 0),
                    backgroundColor: `rgba(255, 159, 64, 0.8)`,
                    borderColor: studentColors.warning,
                    borderWidth: 2,
                    type: 'line',
                    yAxisID: 'y1',
                    tension: 0.4,
                    fill: false,
                    pointRadius: 6,
                    pointHoverRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Number of Assessments',
                            color: studentColors.dark,
                            font: {
                                size: 14,
                                family: "'Poppins', sans-serif",
                                weight: '600'
                            }
                        }
                    },
                    y1: {
                        position: 'right',
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Average Score',
                            color: studentColors.dark,
                            font: {
                                size: 14,
                                family: "'Poppins', sans-serif",
                                weight: '600'
                            }
                        },
                        grid: {
                            drawOnChartArea: false
                        }
                    }
                }
            }
        });
    }
}

// Real-time chart updates
function initRealTimeUpdates() {
    // Check for new data every 30 seconds
    setInterval(checkForNewData, 30000);
    
    // Add refresh button functionality
    const refreshBtn = document.getElementById('refreshCharts');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            refreshAllCharts();
            showNotification('Charts refreshed successfully!', 'success');
        });
    }
}

// Check for new data and update charts
async function checkForNewData() {
    try {
        const response = await fetch('/api/chart-data');
        if (response.ok) {
            const newData = await response.json();
            updateChartsWithNewData(newData);
        }
    } catch (error) {
        console.log('Error fetching new data:', error);
    }
}

// Update charts with new data
function updateChartsWithNewData(newData) {
    if (newData && newData.updated) {
        // Add pulsing effect to indicate update
        const charts = document.querySelectorAll('.chart-container');
        charts.forEach(chart => {
            chart.style.animation = 'pulse 0.5s ease-in-out';
            setTimeout(() => {
                chart.style.animation = '';
            }, 500);
        });
        
        // Reload page after a short delay to show animation
        setTimeout(() => {
            location.reload();
        }, 1000);
    }
}

// Refresh all charts
function refreshAllCharts() {
    const charts = Chart.instances;
    charts.forEach(chart => {
        chart.destroy();
    });
    
    // Reinitialize charts
    initTrendChart();
    initDistributionChart();
    initGenderChart();
    initAgeChart();
    
    // Add success animation
    const chartContainers = document.querySelectorAll('.chart-container');
    chartContainers.forEach(container => {
        container.style.animation = 'successPulse 1s ease';
        setTimeout(() => {
            container.style.animation = '';
        }, 1000);
    });
}

// Resize charts on window resize
function resizeCharts() {
    const charts = Chart.instances;
    charts.forEach(chart => {
        chart.resize();
    });
}

// Show notification with student theme
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} notification-alert`;
    notification.innerHTML = `
        <div class="d-flex justify-content-between align-items-center">
            <div class="d-flex align-items-center">
                <span class="notification-icon me-3">${
                    type === 'success' ? '✅' : 
                    type === 'error' ? '❌' : 
                    type === 'warning' ? '⚠️' : 'ℹ️'
                }</span>
                <span>${message}</span>
            </div>
            <button type="button" class="btn-close btn-close-white" onclick="this.parentElement.parentElement.remove()"></button>
        </div>
    `;
    
    // Style the notification
    notification.style.cssText = `
        position: fixed;
        top: 30px;
        right: 30px;
        z-index: 9999;
        min-width: 350px;
        max-width: 450px;
        animation: slideInRight 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
        background: ${type === 'success' ? 'linear-gradient(135deg, #38b000 0%, #4cc9f0 100%)' :
                      type === 'error' ? 'linear-gradient(135deg, #ef233c 0%, #d90429 100%)' :
                      type === 'warning' ? 'linear-gradient(135deg, #ffd60a 0%, #f8961e 100%)' :
                      'linear-gradient(135deg, #4361ee 0%, #7209b7 100%)'};
        color: white;
        border: none;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(10px);
    `;
    
    // Add to body
    document.body.appendChild(notification);
    
    // Add animation for icon
    const icon = notification.querySelector('.notification-icon');
    icon.style.animation = 'bounce 0.5s ease infinite alternate';
    
    // Remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.style.animation = 'slideOutRight 0.5s ease';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 500);
        }
    }, 5000);
}

// Add CSS animations for notifications and charts
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    @keyframes bounce {
        0% { transform: translateY(0); }
        100% { transform: translateY(-5px); }
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }
    
    @keyframes successPulse {
        0% { 
            box-shadow: 0 0 0 0 rgba(56, 176, 0, 0.4);
            transform: scale(1);
        }
        70% { 
            box-shadow: 0 0 0 15px rgba(56, 176, 0, 0);
            transform: scale(1.02);
        }
        100% { 
            box-shadow: 0 0 0 0 rgba(56, 176, 0, 0);
            transform: scale(1);
        }
    }
    
    .chart-container {
        position: relative;
        transition: all 0.3s ease;
    }
    
    .chart-container:hover {
        transform: translateY(-5px);
    }
    
    .chart-wrapper {
        background: white;
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 10px 30px rgba(67, 97, 238, 0.1);
        transition: all 0.3s ease;
    }
    
    .chart-wrapper:hover {
        box-shadow: 0 15px 40px rgba(67, 97, 238, 0.2);
    }
    
    .chart-title {
        color: #2b2d42;
        font-family: 'Poppins', sans-serif;
        font-weight: 700;
        font-size: 1.5rem;
        margin-bottom: 20px;
        background: linear-gradient(135deg, #4361ee 0%, #f72585 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .chart-controls {
        display: flex;
        gap: 10px;
        margin-bottom: 20px;
        flex-wrap: wrap;
    }
    
    .chart-control-btn {
        background: rgba(67, 97, 238, 0.1);
        border: 2px solid transparent;
        color: #4361ee;
        padding: 8px 20px;
        border-radius: 25px;
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .chart-control-btn:hover {
        background: #4361ee;
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(67, 97, 238, 0.3);
    }
    
    .chart-control-btn.active {
        background: #4361ee;
        color: white;
        border-color: #4361ee;
    }
    
    .loading-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(255, 255, 255, 0.9);
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 20px;
        z-index: 10;
        opacity: 0;
        visibility: hidden;
        transition: all 0.3s ease;
    }
    
    .loading-overlay.active {
        opacity: 1;
        visibility: visible;
    }
    
    .chart-tooltip {
        background: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.15);
        border-left: 5px solid #4361ee;
        font-family: 'Poppins', sans-serif;
    }
`;
document.head.appendChild(style);

// Time filter functionality (for chart.html)
function initTimeFilters() {
    const filterBtns = document.querySelectorAll('.time-filter-btn');
    if (filterBtns.length > 0) {
        filterBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                // Remove active class from all buttons
                filterBtns.forEach(b => b.classList.remove('active'));
                // Add active class to clicked button
                this.classList.add('active');
                
                const days = this.getAttribute('data-days');
                filterChartData(parseInt(days));
            });
        });
    }
}

// Filter chart data by time period
async function filterChartData(days) {
    try {
        // Show loading
        const chartContainers = document.querySelectorAll('.chart-container');
        chartContainers.forEach(container => {
            container.style.opacity = '0.7';
        });
        
        // In a real application, this would fetch filtered data from the server
        // For now, we'll just show a notification
        const label = days === 0 ? 'all time' : days + ' days';
        showNotification(`Filtered data for ${label}`, 'info');
        
        // Simulate API call
        setTimeout(() => {
            chartContainers.forEach(container => {
                container.style.opacity = '1';
                container.style.animation = 'pulse 0.5s ease';
                setTimeout(() => {
                    container.style.animation = '';
                }, 500);
            });
        }, 1000);
        
    } catch (error) {
        console.error('Error filtering chart data:', error);
        showNotification('Error filtering data. Please try again.', 'error');
    }
}

// Initialize time filters when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initTimeFilters();
});

// Export Chart functions for global use
window.ChartManager = {
    refreshAllCharts,
    showNotification,
    initTrendChart,
    initDistributionChart,
    initGenderChart,
    initAgeChart,
    filterChartData
};

// Add floating animation to charts
function addChartAnimations() {
    const charts = document.querySelectorAll('.chart-container canvas');
    charts.forEach((chart, index) => {
        chart.style.animationDelay = `${index * 0.2}s`;
        chart.classList.add('float-animation');
    });
}

// Initialize animations when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    addChartAnimations();
});

// Add CSS for float animation
const floatStyle = document.createElement('style');
floatStyle.textContent = `
    .float-animation {
        animation: floatUpDown 3s ease-in-out infinite;
        animation-delay: var(--delay, 0s);
    }
    
    @keyframes floatUpDown {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
`;
document.head.appendChild(floatStyle);