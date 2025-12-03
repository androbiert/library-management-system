// ===== STATE MANAGEMENT =====
let currentSlide = 1;
const totalSlides = 15;  // Changed from 9 to 15
let charts = {};

// ===== DOM ELEMENTS =====
const slidesContainer = document.getElementById('slidesContainer');
const slides = document.querySelectorAll('.slide');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');
const progressFill = document.getElementById('progressFill');
const slideCounter = document.getElementById('slideCounter');

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', () => {
    initializeSlides();
    updateUI();
    setupEventListeners();

    // Check URL hash for deep linking
    const hash = window.location.hash;
    if (hash) {
        const slideNum = parseInt(hash.replace('#slide-', ''));
        if (slideNum >= 1 && slideNum <= totalSlides) {
            goToSlide(slideNum);
        }
    }
});

// ===== SLIDE NAVIGATION =====
function goToSlide(slideNumber) {
    if (slideNumber < 1 || slideNumber > totalSlides) return;

    // Update classes
    slides.forEach((slide, index) => {
        slide.classList.remove('active', 'prev');
        if (index + 1 === slideNumber) {
            slide.classList.add('active');
        } else if (index + 1 < slideNumber) {
            slide.classList.add('prev');
        }
    });

    currentSlide = slideNumber;

    // Update URL hash
    window.location.hash = `slide-${slideNumber}`;

    // Update UI
    updateUI();

    // Trigger slide-specific actions
    onSlideEnter(slideNumber);
}

function nextSlide() {
    if (currentSlide < totalSlides) {
        goToSlide(currentSlide + 1);
    }
}

function prevSlide() {
    if (currentSlide > 1) {
        goToSlide(currentSlide - 1);
    }
}

// ===== UI UPDATES =====
function updateUI() {
    // Update progress bar
    const progress = (currentSlide / totalSlides) * 100;
    progressFill.style.width = `${progress}%`;

    // Update slide counter
    slideCounter.textContent = `${currentSlide} / ${totalSlides}`;

    // Update navigation buttons
    prevBtn.disabled = currentSlide === 1;
    nextBtn.disabled = currentSlide === totalSlides;
}

// ===== EVENT LISTENERS =====
function setupEventListeners() {
    // Button clicks
    prevBtn.addEventListener('click', prevSlide);
    nextBtn.addEventListener('click', nextSlide);

    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowRight' || e.key === ' ') {
            e.preventDefault();
            nextSlide();
        } else if (e.key === 'ArrowLeft') {
            e.preventDefault();
            prevSlide();
        } else if (e.key === 'Home') {
            e.preventDefault();
            goToSlide(1);
        } else if (e.key === 'End') {
            e.preventDefault();
            goToSlide(totalSlides);
        }
    });

    // Touch gestures for mobile
    let touchStartX = 0;
    let touchEndX = 0;

    slidesContainer.addEventListener('touchstart', (e) => {
        touchStartX = e.changedTouches[0].screenX;
    }, false);

    slidesContainer.addEventListener('touchend', (e) => {
        touchEndX = e.changedTouches[0].screenX;
        handleSwipe();
    }, false);

    function handleSwipe() {
        const swipeThreshold = 50;
        const diff = touchStartX - touchEndX;

        if (Math.abs(diff) > swipeThreshold) {
            if (diff > 0) {
                // Swipe left - next slide
                nextSlide();
            } else {
                // Swipe right - previous slide
                prevSlide();
            }
        }
    }
}

// ===== SLIDE-SPECIFIC ACTIONS =====
function onSlideEnter(slideNumber) {
    // Slide 8: Statistics with charts
    if (slideNumber === 8 && !charts.categoryChart) {
        setTimeout(() => {
            animateStatNumbers();
            initializeCharts();
        }, 300);
    }
}

// ===== STATISTICS ANIMATION =====
function animateStatNumbers() {
    const statValues = document.querySelectorAll('.stat-value');

    statValues.forEach(stat => {
        const target = parseInt(stat.getAttribute('data-count'));
        const duration = 2000; // 2 seconds
        const steps = 60;
        const increment = target / steps;
        const stepDuration = duration / steps;

        let current = 0;
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                stat.textContent = target;
                clearInterval(timer);
            } else {
                stat.textContent = Math.floor(current);
            }
        }, stepDuration);
    });
}

// ===== CHARTS INITIALIZATION =====
function initializeCharts() {
    // Chart.js default font color
    Chart.defaults.color = '#b0b0b0';
    Chart.defaults.font.family = 'Inter';

    // Category Chart (Pie)
    const categoryCtx = document.getElementById('categoryChart');
    if (categoryCtx && !charts.categoryChart) {
        charts.categoryChart = new Chart(categoryCtx, {
            type: 'doughnut',
            data: {
                labels: ['Fantasy', 'Classic', 'Science Fiction', 'Mystery', 'Romance', 'Biography'],
                datasets: [{
                    data: [25, 18, 12, 15, 10, 8],
                    backgroundColor: [
                        'rgba(102, 126, 234, 0.8)',
                        'rgba(118, 75, 162, 0.8)',
                        'rgba(240, 147, 251, 0.8)',
                        'rgba(0, 200, 200, 0.8)',
                        'rgba(255, 107, 107, 0.8)',
                        'rgba(255, 184, 77, 0.8)'
                    ],
                    borderColor: [
                        'rgba(102, 126, 234, 1)',
                        'rgba(118, 75, 162, 1)',
                        'rgba(240, 147, 251, 1)',
                        'rgba(0, 200, 200, 1)',
                        'rgba(255, 107, 107, 1)',
                        'rgba(255, 184, 77, 1)'
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 15,
                            font: {
                                size: 12
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                const label = context.label || '';
                                const value = context.parsed || 0;
                                return `${label}: ${value} emprunts`;
                            }
                        }
                    }
                },
                animation: {
                    animateRotate: true,
                    animateScale: true,
                    duration: 1500
                }
            }
        });
    }

    // Monthly Chart (Line)
    const monthlyCtx = document.getElementById('monthlyChart');
    if (monthlyCtx && !charts.monthlyChart) {
        charts.monthlyChart = new Chart(monthlyCtx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc'],
                datasets: [{
                    label: 'Emprunts',
                    data: [45, 52, 48, 58, 62, 55, 48, 50, 65, 70, 68, 72],
                    borderColor: 'rgba(102, 126, 234, 1)',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4,
                    fill: true,
                    pointBackgroundColor: 'rgba(102, 126, 234, 1)',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 5,
                    pointHoverRadius: 7
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                            label: function (context) {
                                return `Emprunts: ${context.parsed.y}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: '#b0b0b0'
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)'
                        },
                        ticks: {
                            color: '#b0b0b0'
                        }
                    }
                },
                animation: {
                    duration: 2000,
                    easing: 'easeInOutQuart'
                }
            }
        });
    }
}

// ===== HELPER FUNCTIONS =====
function initializeSlides() {
    // Ensure first slide is active
    slides[0].classList.add('active');
}

// ===== ACCESSIBILITY =====
// Add ARIA labels dynamically
slides.forEach((slide, index) => {
    slide.setAttribute('aria-label', `Slide ${index + 1} of ${totalSlides}`);
    slide.setAttribute('role', 'region');
});

// ===== CONSOLE GREETING =====
console.log('%c📚 KTABNA Presentation', 'font-size: 24px; font-weight: bold; color: #667eea;');
console.log('%cKeyboard Shortcuts:', 'font-size: 14px; font-weight: bold; margin-top: 10px;');
console.log('%c→ or Space: Next Slide', 'font-size: 12px;');
console.log('%c←: Previous Slide', 'font-size: 12px;');
console.log('%cHome: First Slide', 'font-size: 12px;');
console.log('%cEnd: Last Slide', 'font-size: 12px;');
