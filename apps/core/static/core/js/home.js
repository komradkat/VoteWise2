// VoteWise Home Page JavaScript
// Handles scroll animations and interactive elements

document.addEventListener('DOMContentLoaded', function() {
    // Intersection Observer for scroll animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                // Unobserve after animation to improve performance
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe all elements that should animate on scroll
    const animatedElements = document.querySelectorAll('.section-title, .section-subtitle, .feature-card');
    animatedElements.forEach(el => observer.observe(el));

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href !== '#' && href.length > 1) {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });

    // Urgency banner countdown (if exists)
    const countdownElement = document.getElementById('countdown');
    const urgencyBanner = document.getElementById('urgencyBanner');
    
    if (countdownElement && urgencyBanner) {
        // Example: Set a target date (you can replace this with dynamic data)
        // const targetDate = new Date('2025-12-31T23:59:59').getTime();
        
        // For now, just hide the banner if no active election
        // You can implement actual countdown logic here
        urgencyBanner.style.display = 'none';
    }

    // Add parallax effect to hero background (subtle)
    const hero = document.querySelector('.hero');
    if (hero && window.matchMedia('(prefers-reduced-motion: no-preference)').matches) {
        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;
            const parallax = scrolled * 0.3;
            hero.style.backgroundPositionY = `${parallax}px`;
        });
    }

    // Add hover sound effect preparation (optional)
    const buttons = document.querySelectorAll('.cta-button, .btn-secondary');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
        });
    });
});

// Check for reduced motion preference
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

if (prefersReducedMotion.matches) {
    // Disable animations for users who prefer reduced motion
    document.documentElement.style.setProperty('--animation-duration', '0.01ms');
}